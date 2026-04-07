import argparse
import json
import statistics
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable


BASE_URL = "http://100.75.109.92:11434"
CHAT_URL = f"{BASE_URL}/api/chat"
TAGS_URL = f"{BASE_URL}/api/tags"
PS_URL = f"{BASE_URL}/api/ps"
GENERATE_URL = f"{BASE_URL}/api/generate"


def post_json(url: str, payload: dict[str, Any], timeout: int = 300) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(url: str, timeout: int = 60) -> dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_json(text: str) -> Any:
    return json.loads(text.strip())


def exact_match(expected: str) -> Callable[[str], tuple[float, str]]:
    def score_fn(text: str) -> tuple[float, str]:
        actual = text.strip()
        return (1.0, "exact") if actual == expected else (0.0, f"expected={expected!r} actual={actual!r}")

    return score_fn


def json_dict_match(expected: dict[str, Any]) -> Callable[[str], tuple[float, str]]:
    def score_fn(text: str) -> tuple[float, str]:
        try:
            actual = parse_json(text)
        except Exception as exc:
            return 0.0, f"json_error={exc}"
        if actual == expected:
            return 1.0, "json_exact"
        return 0.0, f"expected={expected!r} actual={actual!r}"

    return score_fn


def json_array_match(expected: list[dict[str, Any]]) -> Callable[[str], tuple[float, str]]:
    def score_fn(text: str) -> tuple[float, str]:
        try:
            actual = parse_json(text)
        except Exception as exc:
            return 0.0, f"json_error={exc}"
        if actual == expected:
            return 1.0, "json_exact"
        return 0.0, f"expected={expected!r} actual={actual!r}"

    return score_fn


def contains_all(parts: list[str]) -> Callable[[str], tuple[float, str]]:
    def score_fn(text: str) -> tuple[float, str]:
        actual = text.strip()
        missing = [p for p in parts if p not in actual]
        if not missing:
            return 1.0, "contains_all"
        return 0.0, f"missing={missing!r} actual={actual!r}"

    return score_fn


TASKS: list[dict[str, Any]] = [
    {
        "id": "exact_token",
        "prompt": "Reply with EXACTLY NEXUS_OK and nothing else.",
        "score": exact_match("NEXUS_OK"),
    },
    {
        "id": "tool_call_json",
        "prompt": (
            "Return only minified JSON with this exact object and nothing else: "
            '{"tool":"read_file","path":"MEMORY.md","limit":1}'
        ),
        "score": json_dict_match({"tool": "read_file", "path": "MEMORY.md", "limit": 1}),
    },
    {
        "id": "permission_matrix",
        "prompt": (
            "Return only minified JSON array classifying whether each command should be allowed. "
            'Use exact keys id and allow. '
            '1: "Get-Content MEMORY.md" -> true. '
            '2: "rm -rf /" -> false. '
            '3: "git status" -> true.'
        ),
        "score": json_array_match(
            [{"id": 1, "allow": True}, {"id": 2, "allow": False}, {"id": 3, "allow": True}]
        ),
    },
    {
        "id": "transcript_summary",
        "prompt": (
            "Read this session excerpt and return only minified JSON with keys "
            'user_goal,file,blocker,next_step.\n'
            "Excerpt:\n"
            "User: Fix memory autosave in Electron.\n"
            "Assistant: Investigating electron/main.js and preload.js.\n"
            "Assistant: Desktop turns are not written to claude-mem automatically.\n"
            "Assistant: Next step is to call memorySave after assistant response.\n"
        ),
        "score": json_dict_match(
            {
                "user_goal": "Fix memory autosave in Electron",
                "file": "electron/main.js",
                "blocker": "Desktop turns are not written to claude-mem automatically",
                "next_step": "call memorySave after assistant response",
            }
        ),
    },
    {
        "id": "context_recall",
        "prompt": (
            "Facts:\n"
            "1. P1 host is PAYBACK.\n"
            "2. K2 host is K2.\n"
            "3. vault host is vault-neo.\n"
            "4. claude-mem runs on localhost:37778.\n"
            "5. qwen3.5:4b is on K2.\n"
            "6. sam860/LFM2:350m is on P1.\n"
            "7. CC CLI Max is primary.\n"
            "8. OpenRouter is escape plan.\n"
            "9. Groq is fallback.\n"
            "10. Browser and Electron are one product.\n"
            "Return only minified JSON with keys mem_port,p1_model,escape_plan."
        ),
        "score": json_dict_match(
            {"mem_port": 37778, "p1_model": "sam860/LFM2:350m", "escape_plan": "OpenRouter"}
        ),
    },
    {
        "id": "route_selection",
        "prompt": (
            "Return only minified JSON array with exact routing choices using keys id and route. "
            'Routes must be one of "cc","k2","groq". '
            '1: read the first line of MEMORY.md with local tool use -> "cc". '
            '2: summarize recent transcript rows on K2 local floor -> "k2". '
            '3: CC locked and K2 unavailable, answer a generic writing request -> "groq".'
        ),
        "score": json_array_match(
            [{"id": 1, "route": "cc"}, {"id": 2, "route": "k2"}, {"id": 3, "route": "groq"}]
        ),
    },
    {
        "id": "powershell_command",
        "prompt": "Return only one PowerShell command that counts files recursively under Scripts and prints only the count.",
        "score": contains_all(["Get-ChildItem", "Scripts", "-Recurse", "-File", "Measure-Object"]),
    },
    {
        "id": "structured_diff",
        "prompt": (
            "A diff adds a feature to display structured artifacts in a side panel instead of inline chat. "
            "Return only minified JSON with keys gap_id and verdict using exact values "
            '{"gap_id":"structured_diff_display","verdict":"HAVE"}.'
        ),
        "score": json_dict_match({"gap_id": "structured_diff_display", "verdict": "HAVE"}),
    },
    {
        "id": "concise_reasoning",
        "prompt": (
            "A task takes 3 minutes and runs every 15 minutes starting at 09:52. "
            "How many runs complete by 10:52 inclusive? Reply with only the integer."
        ),
        "score": exact_match("5"),
    },
    {
        "id": "format_discipline",
        "prompt": (
            "Return exactly one lowercase word naming the canonical claude-mem escape provider in Nexus. "
            "No punctuation."
        ),
        "score": exact_match("openrouter"),
    },
    {
        "id": "host_boundary",
        "prompt": (
            "Return only minified JSON with keys p1,k2,vault using the exact values "
            '{"p1":"windows","k2":"ubuntu","vault":"remote"}.'
        ),
        "score": json_dict_match({"p1": "windows", "k2": "ubuntu", "vault": "remote"}),
    },
    {
        "id": "brevity_control",
        "prompt": "Reply with exactly two words: merged workspace",
        "score": exact_match("merged workspace"),
    },
]


def run_chat(model: str, prompt: str, keep_alive: str = "10m") -> dict[str, Any]:
    payload = {
        "model": model,
        "stream": False,
        "keep_alive": keep_alive,
        "options": {"temperature": 0},
        "messages": [
            {
                "role": "system",
                "content": "Follow the user's formatting instructions exactly. Do not add explanation unless asked.",
            },
            {"role": "user", "content": prompt},
        ],
    }
    started = time.perf_counter()
    response = post_json(CHAT_URL, payload, timeout=600)
    response["_elapsed_s"] = time.perf_counter() - started
    return response


def unload_model(model: str) -> dict[str, Any]:
    payload = {"model": model, "prompt": "", "stream": False, "keep_alive": 0}
    return post_json(GENERATE_URL, payload, timeout=120)


def safe_mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    task_scores: dict[str, Any] = {}
    for task in TASKS:
        task_rows = [r for r in rows if r["task_id"] == task["id"]]
        task_scores[task["id"]] = {
            "avg_score": safe_mean([r["score"] for r in task_rows]),
            "avg_elapsed_s": safe_mean([r["elapsed_s"] for r in task_rows]),
            "avg_tokens_per_s": safe_mean([r["tokens_per_s"] for r in task_rows if r["tokens_per_s"] is not None]),
            "outputs": [r["output"] for r in task_rows],
            "reasons": [r["reason"] for r in task_rows],
        }
    return {
        "task_scores": task_scores,
        "overall_avg_score": safe_mean([r["score"] for r in rows]),
        "overall_avg_elapsed_s": safe_mean([r["elapsed_s"] for r in rows]),
        "overall_median_elapsed_s": statistics.median([r["elapsed_s"] for r in rows]) if rows else 0.0,
        "overall_avg_tokens_per_s": safe_mean([r["tokens_per_s"] for r in rows if r["tokens_per_s"] is not None]),
    }


def write_state(output_path: Path, state: dict[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def load_state(output_path: Path) -> dict[str, Any] | None:
    if not output_path.exists() or output_path.stat().st_size == 0:
        return None
    return json.loads(output_path.read_text(encoding="utf-8"))


def completed_pairs(rows: list[dict[str, Any]]) -> set[tuple[str, int]]:
    return {(row["task_id"], int(row["rep"])) for row in rows}


def benchmark_model(model: str, reps: int, output_path: Path) -> None:
    state = load_state(output_path)
    if state is None:
        state = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "endpoint": BASE_URL,
            "model": model,
            "reps": reps,
            "available_models_before": [m["name"] for m in get_json(TAGS_URL).get("models", [])],
            "ps_before": get_json(PS_URL),
            "warmup": None,
            "rows": [],
            "summary": {},
        }
        write_state(output_path, state)

    if state.get("warmup") is None:
        warm = run_chat(model, "Reply with READY and nothing else.", keep_alive="15m")
        state["warmup"] = {
            "elapsed_s": warm["_elapsed_s"],
            "output": warm.get("message", {}).get("content", ""),
            "load_duration_ns": warm.get("load_duration"),
            "eval_count": warm.get("eval_count"),
        }
        write_state(output_path, state)
        print(f"[warmup] {model} elapsed={warm['_elapsed_s']:.2f}s output={state['warmup']['output']!r}", flush=True)
    else:
        print(f"[resume] {model} warmup already recorded", flush=True)

    total = len(TASKS) * reps
    done_pairs = completed_pairs(state["rows"])
    completed = len(done_pairs)
    for task in TASKS:
        for rep in range(1, reps + 1):
            if (task["id"], rep) in done_pairs:
                continue
            started = time.perf_counter()
            try:
                response = run_chat(model, task["prompt"], keep_alive="15m")
                text = response.get("message", {}).get("content", "")
                score, reason = task["score"](text)
                eval_count = response.get("eval_count")
                eval_duration_ns = response.get("eval_duration")
                tokens_per_s = None
                if eval_count and eval_duration_ns and eval_duration_ns > 0:
                    tokens_per_s = eval_count / (eval_duration_ns / 1_000_000_000)
                row = {
                    "task_id": task["id"],
                    "rep": rep,
                    "score": score,
                    "reason": reason,
                    "output": text,
                    "elapsed_s": response["_elapsed_s"],
                    "load_duration_ns": response.get("load_duration"),
                    "eval_count": eval_count,
                    "eval_duration_ns": eval_duration_ns,
                    "prompt_eval_count": response.get("prompt_eval_count"),
                    "prompt_eval_duration_ns": response.get("prompt_eval_duration"),
                    "tokens_per_s": tokens_per_s,
                }
            except Exception as exc:
                row = {
                    "task_id": task["id"],
                    "rep": rep,
                    "score": 0.0,
                    "reason": f"exception:{exc.__class__.__name__}",
                    "output": "",
                    "elapsed_s": time.perf_counter() - started,
                    "load_duration_ns": None,
                    "eval_count": None,
                    "eval_duration_ns": None,
                    "prompt_eval_count": None,
                    "prompt_eval_duration_ns": None,
                    "tokens_per_s": None,
                    "error": str(exc),
                }
            state["rows"].append(row)
            done_pairs.add((task["id"], rep))
            state["summary"] = summarize_rows(state["rows"])
            write_state(output_path, state)
            completed += 1
            print(
                f"[{completed}/{total}] {model} {task['id']} rep={rep} "
                f"score={row['score']:.2f} elapsed={row['elapsed_s']:.2f}s reason={row['reason']}",
                flush=True,
            )

    state["unload"] = unload_model(model)
    state["ps_after_unload"] = get_json(PS_URL)
    state["summary"] = summarize_rows(state["rows"])
    write_state(output_path, state)
    print(f"[done] {model} overall_score={state['summary']['overall_avg_score']:.3f}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--reps", type=int, default=2)
    args = parser.parse_args()
    benchmark_model(args.model, args.reps, Path(args.output))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[aborted] benchmark interrupted", file=sys.stderr)
        raise
