"""
Groq-powered full audit of the Karma Cockpit project.
Sends key file sections to Groq for security, reliability, and architecture review.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

# ---------- Config ----------
VBS_PATH = os.path.join(
    os.environ.get("APPDATA", ""),
    r"Microsoft\Windows\Start Menu\Programs\Startup\start_openwebui.vbs",
)
MODEL = "llama-3.3-70b-versatile"
SCRIPTS = r"C:\Users\raest\Documents\Karma_SADE\Scripts"
MEMORY = r"C:\Users\raest\Documents\Karma_SADE\Memory"

# ---------- Helpers ----------

def get_groq_key():
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key
    try:
        vbs = open(VBS_PATH, encoding="utf-8").read()
        key = vbs.split('OPENAI_API_KEYS") = "')[1].split('"')[0]
        return key
    except Exception as e:
        print(f"[ERROR] Cannot extract Groq key: {e}")
        sys.exit(1)


def call_groq(api_key, prompt, max_tokens=3000):
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "KarmaSADE-Audit/1.0",
        },
        method="POST",
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                usage = data.get("usage", {})
                content = data["choices"][0]["message"]["content"]
                return content, usage
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8")
            if e.code == 429 and attempt < 3:
                # Parse retry-after from error message
                wait = 30 + attempt * 15
                try:
                    msg = json.loads(err).get("error", {}).get("message", "")
                    if "try again in" in msg:
                        secs = float(msg.split("try again in ")[1].split("s")[0])
                        wait = max(int(secs) + 5, wait)
                except Exception:
                    pass
                print(f"  [Rate limited — waiting {wait}s before retry {attempt+2}/4]")
                time.sleep(wait)
                # Re-create request (urlopen consumes it)
                req = urllib.request.Request(
                    url, data=body,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                        "User-Agent": "KarmaSADE-Audit/1.0",
                    },
                    method="POST",
                )
                continue
            return f"HTTP {e.code}: {err[:400]}", {}
        except Exception as e:
            return f"Error: {e}", {}
    return "Max retries exceeded", {}


def read_file(path):
    try:
        return open(path, encoding="utf-8").read()
    except Exception as e:
        return f"(cannot read: {e})"


def truncate(text, max_chars=28000):
    """Truncate to stay within ~7K tokens input."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n... [TRUNCATED] ..."


# ---------- Audit Passes ----------

AUDIT_SYSTEM = """You are a senior security and reliability auditor. 
Analyze the provided code and report issues using this format:
- CRITICAL: <issue> — <location> — <fix>
- HIGH: <issue> — <location> — <fix>
- MEDIUM: <issue> — <location> — <fix>
- LOW: <issue> — <location> — <fix>
- OK: <what's good>
Be specific with line references. Only report real issues, not style preferences.
Do NOT suggest switching to production WSGI servers (this is a local-only service).
Do NOT flag the Groq API key in the VBS launcher (user is aware, will rotate)."""


def audit_pass(api_key, label, code_text, focus):
    prompt = f"""{AUDIT_SYSTEM}

## Focus: {focus}

## Code:
```
{truncate(code_text)}
```

Provide your audit findings. Be concise but thorough."""
    print(f"\n{'='*60}")
    print(f"AUDIT PASS: {label}")
    print(f"{'='*60}")
    result, usage = call_groq(api_key, prompt)
    tokens = usage.get("total_tokens", "?")
    print(f"[Groq: {tokens} tokens]\n")
    print(result)
    return result


# ---------- Main ----------

def main():
    api_key = get_groq_key()
    print(f"Groq key: {api_key[:8]}...{api_key[-4:]}")
    print(f"Model: {MODEL}\n")

    # Read files
    cockpit = read_file(os.path.join(SCRIPTS, "karma_cockpit_service.py"))
    tool = read_file(os.path.join(SCRIPTS, "openwebui_browser_tool_v2.py"))
    prompt_gen = read_file(os.path.join(SCRIPTS, "generate_karma_prompt.py"))
    installer = read_file(os.path.join(SCRIPTS, "install_cockpit_tool.py"))
    facts = read_file(os.path.join(MEMORY, "05-user-facts.json"))

    results = []

    # Pass 1: Cockpit Security (first half)
    cockpit_lines = cockpit.split("\n")
    half = len(cockpit_lines) // 2
    cockpit_p1 = "\n".join(cockpit_lines[:half])
    cockpit_p2 = "\n".join(cockpit_lines[half:])

    r = audit_pass(api_key, "Cockpit Service — Security & Config (Part 1)",
                   cockpit_p1,
                   "Security: CORS, input validation, injection risks, auth, subprocess safety, secrets handling. "
                   "Also check: thread safety, error handling, resource leaks.")
    results.append(r)
    time.sleep(35)  # Rate limit buffer (12K TPM)

    # Pass 2: Cockpit (second half — Flask routes, Gemini, main)
    r = audit_pass(api_key, "Cockpit Service — Routes & Gemini (Part 2)",
                   cockpit_p2,
                   "Security: route input validation, command injection via Gemini CLI, error handling. "
                   "Reliability: timeout handling, subprocess cleanup, Flask config. "
                   "Check all POST routes accept proper JSON validation.")
    results.append(r)
    time.sleep(35)

    # Pass 3: Browser tool
    r = audit_pass(api_key, "Browser Tool v2 (Open WebUI Tool)",
                   tool,
                   "Security: HTTP request safety, error handling, timeout config. "
                   "Reliability: failure modes, missing error paths. "
                   "Architecture: tool interface design, docstrings, parameter handling.")
    results.append(r)
    time.sleep(35)

    # Pass 4: Prompt generator + installer + facts
    combined = (
        "=== generate_karma_prompt.py ===\n" + prompt_gen +
        "\n\n=== install_cockpit_tool.py ===\n" + installer +
        "\n\n=== 05-user-facts.json ===\n" + facts
    )
    r = audit_pass(api_key, "Prompt Generator + Installer + Facts",
                   combined,
                   "Security: SQL injection in DB writes, file path handling. "
                   "Data quality: duplicate facts, stale data, PII exposure in prompts. "
                   "Reliability: DB error handling, file encoding, fact filtering logic.")
    results.append(r)
    time.sleep(35)

    # Pass 5: Architecture synthesis
    summary_prompt = f"""{AUDIT_SYSTEM}

You previously audited 4 parts of the Karma Cockpit system. Here are the findings:

{chr(10).join(f'--- Pass {i+1} ---{chr(10)}{r[:1500]}' for i, r in enumerate(results))}

Now provide a FINAL AUDIT SUMMARY:
1. Overall risk rating (PASS / PASS WITH NOTES / FAIL)
2. Top 3 most important findings across all passes
3. Any systemic patterns you noticed
4. Final verdict and recommended next steps

Be concise. This is a local-only development tool, not production software."""

    print(f"\n{'='*60}")
    print("FINAL SYNTHESIS")
    print(f"{'='*60}")
    result, usage = call_groq(api_key, summary_prompt, max_tokens=2000)
    tokens = usage.get("total_tokens", "?")
    print(f"[Groq: {tokens} tokens]\n")
    print(result)


if __name__ == "__main__":
    main()
