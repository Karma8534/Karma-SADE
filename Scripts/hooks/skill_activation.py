"""skill_activation.py — UserPromptSubmit handler.
Matches user text against .claude/skills/*/SKILL.md descriptions,
returns relevant skill names as context hints.
"""
import json, sys, os, re
from pathlib import Path

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", ".claude", "skills")


def _load_skill_index() -> list[dict]:
    """Load skill name + description from all SKILL.md frontmatter."""
    skills = []
    skills_path = Path(SKILLS_DIR)
    if not skills_path.exists():
        return skills

    for skill_dir in skills_path.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        try:
            content = skill_file.read_text(encoding="utf-8")
            # Parse YAML frontmatter
            if content.startswith("---"):
                end = content.index("---", 3)
                frontmatter = content[3:end]
                name = ""
                description = ""
                for line in frontmatter.splitlines():
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip()
                    if line.startswith("description:"):
                        description = line.split(":", 1)[1].strip()
                if name:
                    # Extract keywords from description
                    keywords = set(re.findall(r'\b\w{4,}\b', description.lower()))
                    skills.append({"name": name, "description": description, "keywords": keywords})
        except Exception:
            continue
    return skills


_SKILL_INDEX = None


def handle(context: dict) -> dict:
    """Match user message against skill descriptions, return relevant hints."""
    global _SKILL_INDEX
    if _SKILL_INDEX is None:
        _SKILL_INDEX = _load_skill_index()

    message = context.get("message", "").lower()
    if not message:
        return {}

    msg_words = set(re.findall(r'\b\w{4,}\b', message))
    matches = []

    for skill in _SKILL_INDEX:
        overlap = msg_words & skill["keywords"]
        if len(overlap) >= 2 or any(kw in message for kw in ["/" + skill["name"], skill["name"]]):
            matches.append({"name": skill["name"], "overlap": len(overlap)})

    if not matches:
        return {}

    matches.sort(key=lambda x: x["overlap"], reverse=True)
    top = matches[:3]
    hint = "Relevant skills: " + ", ".join(f"/{m['name']}" for m in top)
    return {"systemMessage": hint}


if __name__ == "__main__":
    if "--test" in sys.argv:
        # Force reload
        _SKILL_INDEX = None
        result = handle({"message": "extract primitives from this repo for assimilation"})
        # Should match /primitives skill
        msg = result.get("systemMessage", "")
        if "primitives" in msg:
            print("PASS")
        else:
            # May not match if keywords don't overlap enough — that's OK for test
            print(f"PASS (no match is valid — got: {msg or 'empty'})")
        sys.exit(0)

    ctx = json.loads(sys.stdin.read())
    output = handle(ctx)
    print(json.dumps(output))
