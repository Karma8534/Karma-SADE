"""
karma_critic_agent.py — Advisory-only K2 Critic Agent.
Proposes plan/tests/risks per cycle. Cannot close issues,
write canonical artifacts, or commit. Output: critic_plan.json (advice only).
"""

import json
import urllib.request

CRITIC_SYSTEM = """You are an advisory critic agent for Karma's autonomous loop.
You receive ONE issue and produce a structured plan. You are ADVISORY ONLY.
You cannot close issues, commit code, or write canonical artifacts.

Respond in valid JSON only. No markdown fences. No extra keys:
{
  "plan": "step-by-step approach",
  "tests": ["specific test commands to verify the fix"],
  "risks": ["potential risks or side effects"],
  "confidence": 0.0
}
"""

DRY_RUN_PLAN = {
    "plan": "Dry run — no Ollama call made",
    "tests": ["echo 'dry run test'"],
    "risks": ["none in dry run"],
    "confidence": 0.0,
}


class CriticAgent:
    def __init__(
        self,
        ollama_url: str = "http://172.22.240.1:11434",
        model: str = "devstral:latest",
        dry_run: bool = False,
    ):
        self.ollama_url = ollama_url
        self.model = model
        self.dry_run = dry_run

    def get_plan(self, issue: dict, context: str) -> dict | None:
        """
        Returns critic plan dict, or None if Critic is unavailable.
        None = degraded mode. Kiki continues without critic plan.
        """
        if self.dry_run:
            return DRY_RUN_PLAN.copy()

        user_msg = (
            f"ISSUE: {issue.get('issue', '')}\n"
            f"DETAILS: {issue.get('details', '')}\n"
            f"CONTEXT: {context[:500]}"
        )

        try:
            raw = self._call_ollama(user_msg)
            return self._parse(raw)
        except Exception:
            return None  # Caller handles None as degraded mode

    def _call_ollama(self, user_msg: str) -> str:
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": CRITIC_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 1024},
        }).encode()
        req = urllib.request.Request(
            f"{self.ollama_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read())
        return body.get("message", {}).get("content", "")

    def _parse(self, raw: str) -> dict | None:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        if "<think>" in raw:
            parts = raw.split("</think>")
            raw = parts[-1].strip() if len(parts) > 1 else raw
        try:
            return json.loads(raw)
        except Exception:
            return None
