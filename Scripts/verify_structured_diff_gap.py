#!/usr/bin/env python3
"""Smoke verification for the structured diff display gap closure."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _require(path: Path, needles: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise AssertionError(f"{path.name} missing: {missing}")
    return missing


def main() -> int:
    code_panel = ROOT / "frontend" / "src" / "components" / "CodePanel.tsx"
    context_panel = ROOT / "frontend" / "src" / "components" / "ContextPanel.tsx"
    app_page = ROOT / "frontend" / "src" / "app" / "page.tsx"

    _require(
        code_panel,
        [
            "function buildDiff",
            "fetch(`/v1/file?path=${encodeURIComponent(filePath)}`",
            "fetch('/v1/file', {",
            "<CodeBlock code={dirty ? diffText : draft}",
            "Diff Preview",
            "karma-open-code",
        ],
    )
    _require(
        context_panel,
        [
            "karma-open-code",
            "CustomEvent('karma-open-code'",
        ],
    )
    _require(
        app_page,
        [
            "CodePanel",
            "CoworkPanel",
            "<CodePanel />",
            "<CoworkPanel />",
        ],
    )

    print("VERIFY_OK=structured_diff_display")
    print(f"CODE_PANEL={code_panel}")
    print(f"CONTEXT_PANEL={context_panel}")
    print(f"APP_PAGE={app_page}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
