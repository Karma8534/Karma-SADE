import argparse
import json
import statistics
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable


BASE_URL = "http://100.75.109.92:11434"
CHAT_URL = f"{BASE_URL}/api/chat"
TAGS_URL = f"{BASE_URL}/api/tags"
PS_URL = f"{BASE_URL}/api/ps"
GENERATE_URL = f"{BASE_URL}/api/generate"
CALL_TIMEOUT = 120


def post_json(url: str, payload: dict[str, Any], timeout: int = CALL_TIMEOUT) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(url: str, timeout: int = 30) -> dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def exact_match(expected: str) -> Callable[[str], tuple[float, str]]:
    def score_fn(text: str) -> tuple[float, str]:
        actual = text.strip()
        return (1.0, "exact") if actual == expected else (0.0, f"expected={expected!r} actual={actual!r}")

    return score_fn


def json_match(expected: Any) -> Callable[[str], tuple[float, str]]:
    def score_fn(text: str) -> tuple[float, str]:
        try:
            actual = json.loads(text.strip())
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


TASKS = [
    ("exact_token", "Reply with EXACTLY NEXUS_OK and nothing else.", exact_match("NEXUS_OK")),
    (
        "tool_call_json",
        'Return only minified JSON with this exact object and nothing else: {"tool":"read_file","path":"MEMORY.md","limit":1}',
        json_match({"tool": "read_file", "path": "MEMORY.md", "limit": 1}),
    ),
    (
        "permission_matrix",
        'Return only minified JSON array classifying whether each command should be allowed. Use exact keys id and allow. 1: "Get-Content MEMORY.md" -> true. 2: "rm -rf /" -> false. 3: "git status" -> true.',
        json_match([{"id": 1, "allow": True}, {"id": 2, "allow": False}, {"id": 3, "allow": True}]),
    ),
    (
        "transcript_summary",
        "Read this session excerpt and return only minified JSON with keys user_goal,file,blocker,next_step. Excerpt: User: Fix memory autosave in Electron. Assistant: Investigating electron/main.js and preload.js. Assistant: Desktop turns are not written to claude-mem automatically. Assistant: Next step is to call memorySave after assistant response.",
        json_match(
            {
                "user_goal": "Fix memory autosave in Electron",
                "file": "electron/main.js",
                "blocker": "Desktop turns are not written to claude-mem automatically",
                "next_step": "call memorySave after assistant response",
            }
        ),
    ),
    (
        "context_recall",
        "Facts: P1 host is PAYBACK. K2 host is K2. vault host is vault-neo. claude-mem runs on localhost:37778. qwen3.5:4b is on K2. sam860/LFM2:350m is on P1. CC CLI Max is primary. OpenRouter is escape plan. Groq is fallback. Browser and Electron are one product. Return only minified JSON with keys mem_port,p1_model,escape_plan.",
        json_match({"mem_port": 37778, "p1_model": "sam860/LFM2:350m", "escape_plan": "OpenRouter"}),
    ),
    (
        "route_selection",
        'Return only minified JSON array with exact routing choices using keys id and route. Routes must be one of "cc","k2","groq". 1: read the first line of MEMORY.md with local tool use -> "cc". 2: summarize recent transcript rows on K2 local floor -> "k2". 3: CC locked and K2 unavailable, answer a generic writing request -> "groq".',
        json_match([{"id": 1, "route": "cc"}, {"id": 2, "route": "k2"}, {"id": 3, "route": "groq"}]),
    ),
    (
        "powershell_command",
        "Return only one PowerShell command that counts files recursively under Scripts and prints only the count.",
        contains_all(["Get-ChildItem", "Scripts", "-Recurse", "-File", "Measure-Object"]),
    ),
    (
        "structured_diff",
        'A diff adds a feature to display structured artifacts in a side panel instead of inline chat. Return only minified JSON with keys gap_id and verdict using exact values {"gap_id":"structured_diff_display","verdict":"HAVE"}.',
        json_match({"gap_id": "structured_diff_display", "verdict": "HAVE"}),
    ),
    (
        "concise_reasoning",
        "A task takes 3 minutes and runs every 15 minutes starting at 09:52. How many runs complete by 10:52 inclusive? Reply with only the integer.",
        exact_match("5"),
    ),
    (
        "format_discipline",
        "Return exactly one lowercase word naming the canonical claude-mem escape provider in Nexus. No punctuation.",
        exact_match("openrouter"),
    ),
    (
        "host_boundary",
        'Return only minified JSON with keys p1,k2,vault using the exact values {"p1":"windows","k2":"ubuntu","vault":"remote"}.',
        json_match({"p1": "windows", "k2": "ubuntu", "vault": "remote"}),
    ),
    ("brevity_control", "Reply with exactly two words: merged workspace", exact_match("merged workspace")),
]


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def run_chat(model: str, prompt: str, keep_alive: str = "10m") -> dict[str, Any]:
    payload = {
        "model": model,
        "stream": False,
        "keep_alive": keep_alive,
        "options": {"temperature": 0},
        "messages": [
            {"role": "system", "content": "Follow the user's formatting instructions exactly. Do not add explanation."},
            {"role": "user", "content": prompt},
        ],
    }
    started = time.perf_counter()
    response = post_json(CHAT_URL, payload)
    response["_elapsed_s"] = time.perf_counter() - started
    return response


def unload_model(model: str) -> dict[str, Any]:
    return post_json(GENERATE_URL, {"model": model, "prompt": "", "stream": False, "keep_alive": 0}, timeout=60)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_task: dict[str, dict[str, Any]] = {}
    for task_id, _, _ in TASKS:
        task_rows = [r for r in rows if r["task_id"] == task_id]
        by_task[task_id] = {
            "score": statistics.mean([r["score"] for r in task_rows]) if task_rows else 0.0,
            "elapsed_s": statistics.mean([r["elapsed_s"] for r in task_rows]) if task_rows else 0.0,
            "output": task_rows[-1]["output"] if task_rows else "",
            "reason": task_rows[-1]["reason"] if task_rows else "",
        }
    return {
        "overall_score": statistics.mean([r["score"] for r in rows]) if rows else 0.0,
        "overall_elapsed_s": statistics.mean([r["elapsed_s"] for r in rows]) if rows else 0.0,
        "by_task": by_task,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    out = Path(args.output)
    state = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": args.model,
        "endpoint": BASE_URL,
        "timeout_s": CALL_TIMEOUT,
        "available_models_before": [m["name"] for m in get_json(TAGS_URL).get("models", [])],
        "ps_before": get_json(PS_URL),
        "rows": [],
        "summary": {},
    }
    write_state(out, state)

    warm = run_chat(args.model, "Reply with READY and nothing else.", keep_alive="15m")
    state["warmup"] = {
        "output": warm.get("message", {}).get("content", ""),
        "elapsed_s": warm["_elapsed_s"],
        "load_duration_ns": warm.get("load_duration"),
    }
    write_state(out, state)
    print(f"[warmup] {args.model} {warm['_elapsed_s']:.2f}s", flush=True)

    for index, (task_id, prompt, scorer) in enumerate(TASKS, start=1):
        started = time.perf_counter()
        try:
            response = run_chat(args.model, prompt, keep_alive="15m")
            text = response.get("message", {}).get("content", "")
            score, reason = scorer(text)
            row = {
                "task_id": task_id,
                "score": score,
                "reason": reason,
                "output": text,
                "elapsed_s": response["_elapsed_s"],
                "eval_count": response.get("eval_count"),
                "eval_duration_ns": response.get("eval_duration"),
                "prompt_eval_count": response.get("prompt_eval_count"),
                "prompt_eval_duration_ns": response.get("prompt_eval_duration"),
            }
        except Exception as exc:
            row = {
                "task_id": task_id,
                "score": 0.0,
                "reason": f"exception:{exc.__class__.__name__}",
                "output": "",
                "elapsed_s": time.perf_counter() - started,
                "error": str(exc),
            }
        state["rows"].append(row)
        state["summary"] = summarize(state["rows"])
        write_state(out, state)
        print(f"[{index}/{len(TASKS)}] {args.model} {task_id} score={row['score']:.2f} elapsed={row['elapsed_s']:.2f}s reason={row['reason']}", flush=True)

    state["unload"] = unload_model(args.model)
    state["ps_after_unload"] = get_json(PS_URL)
    state["summary"] = summarize(state["rows"])
    write_state(out, state)
    print(f"[done] {args.model} overall={state['summary']['overall_score']:.3f}", flush=True)


if __name__ == "__main__":
    main()
