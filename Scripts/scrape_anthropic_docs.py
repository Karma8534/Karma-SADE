#!/usr/bin/env python3
"""
K-2: Anthropic Docs Scraper (Playwright version)
Scrapes all English docs from platform.claude.com/docs/en/ using headless browser.
Output: docs/knowledge/anthropic-docs/
"""

import time
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "knowledge" / "anthropic-docs"
DELAY = 1.0  # seconds between pages

ENGLISH_URLS = [
    "https://platform.claude.com/docs/en/intro",
    "https://platform.claude.com/docs/en/get-started",
    "https://platform.claude.com/docs/en/about-claude/models/overview",
    "https://platform.claude.com/docs/en/about-claude/models/choosing-a-model",
    "https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-6",
    "https://platform.claude.com/docs/en/about-claude/models/migration-guide",
    "https://platform.claude.com/docs/en/about-claude/model-deprecations",
    "https://platform.claude.com/docs/en/about-claude/pricing",
    "https://platform.claude.com/docs/en/build-with-claude/overview",
    "https://platform.claude.com/docs/en/build-with-claude/working-with-messages",
    "https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons",
    "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices",
    "https://platform.claude.com/docs/en/build-with-claude/extended-thinking",
    "https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking",
    "https://platform.claude.com/docs/en/build-with-claude/effort",
    "https://platform.claude.com/docs/en/build-with-claude/fast-mode",
    "https://platform.claude.com/docs/en/build-with-claude/structured-outputs",
    "https://platform.claude.com/docs/en/build-with-claude/citations",
    "https://platform.claude.com/docs/en/build-with-claude/streaming",
    "https://platform.claude.com/docs/en/build-with-claude/batch-processing",
    "https://platform.claude.com/docs/en/build-with-claude/pdf-support",
    "https://platform.claude.com/docs/en/build-with-claude/search-results",
    "https://platform.claude.com/docs/en/build-with-claude/multilingual-support",
    "https://platform.claude.com/docs/en/build-with-claude/embeddings",
    "https://platform.claude.com/docs/en/build-with-claude/vision",
    "https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview",
    "https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use",
    "https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool",
    "https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool",
    "https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool",
    "https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool",
    "https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool",
    "https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool",
    "https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool",
    "https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool",
    "https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling",
    "https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming",
    "https://platform.claude.com/docs/en/build-with-claude/context-windows",
    "https://platform.claude.com/docs/en/build-with-claude/compaction",
    "https://platform.claude.com/docs/en/build-with-claude/context-editing",
    "https://platform.claude.com/docs/en/build-with-claude/prompt-caching",
    "https://platform.claude.com/docs/en/build-with-claude/token-counting",
    "https://platform.claude.com/docs/en/build-with-claude/files",
    "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview",
    "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart",
    "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices",
    "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise",
    "https://platform.claude.com/docs/en/build-with-claude/skills-guide",
    "https://platform.claude.com/docs/en/agent-sdk/overview",
    "https://platform.claude.com/docs/en/agent-sdk/quickstart",
    "https://platform.claude.com/docs/en/agent-sdk/agent-loop",
    "https://platform.claude.com/docs/en/agent-sdk/claude-code-features",
    "https://platform.claude.com/docs/en/agent-sdk/sessions",
    "https://platform.claude.com/docs/en/agent-sdk/streaming-vs-single-mode",
    "https://platform.claude.com/docs/en/agent-sdk/streaming-output",
    "https://platform.claude.com/docs/en/agent-sdk/permissions",
    "https://platform.claude.com/docs/en/agent-sdk/user-input",
    "https://platform.claude.com/docs/en/agent-sdk/hooks",
    "https://platform.claude.com/docs/en/agent-sdk/file-checkpointing",
    "https://platform.claude.com/docs/en/agent-sdk/structured-outputs",
    "https://platform.claude.com/docs/en/agent-sdk/hosting",
    "https://platform.claude.com/docs/en/agent-sdk/secure-deployment",
    "https://platform.claude.com/docs/en/agent-sdk/modifying-system-prompts",
    "https://platform.claude.com/docs/en/agent-sdk/mcp",
    "https://platform.claude.com/docs/en/agent-sdk/custom-tools",
    "https://platform.claude.com/docs/en/agent-sdk/subagents",
    "https://platform.claude.com/docs/en/agent-sdk/slash-commands",
    "https://platform.claude.com/docs/en/agent-sdk/skills",
    "https://platform.claude.com/docs/en/agent-sdk/cost-tracking",
    "https://platform.claude.com/docs/en/agent-sdk/todo-tracking",
    "https://platform.claude.com/docs/en/agent-sdk/plugins",
    "https://platform.claude.com/docs/en/agent-sdk/typescript",
    "https://platform.claude.com/docs/en/agent-sdk/typescript-v2-preview",
    "https://platform.claude.com/docs/en/agent-sdk/python",
    "https://platform.claude.com/docs/en/agent-sdk/migration-guide",
    "https://platform.claude.com/docs/en/agents-and-tools/mcp-connector",
    "https://platform.claude.com/docs/en/agents-and-tools/remote-mcp-servers",
    "https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock",
    "https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry",
    "https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai",
    "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview",
    "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-tools",
    "https://platform.claude.com/docs/en/test-and-evaluate/develop-tests",
    "https://platform.claude.com/docs/en/test-and-evaluate/eval-tool",
    "https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-latency",
    "https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations",
    "https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/increase-consistency",
    "https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks",
    "https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/handle-streaming-refusals",
    "https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-prompt-leak",
    "https://platform.claude.com/docs/en/build-with-claude/administration-api",
    "https://platform.claude.com/docs/en/build-with-claude/data-residency",
    "https://platform.claude.com/docs/en/build-with-claude/workspaces",
    "https://platform.claude.com/docs/en/build-with-claude/usage-cost-api",
    "https://platform.claude.com/docs/en/build-with-claude/claude-code-analytics-api",
    "https://platform.claude.com/docs/en/build-with-claude/zero-data-retention",
    "https://platform.claude.com/docs/en/api/overview",
    "https://platform.claude.com/docs/en/api/beta-headers",
    "https://platform.claude.com/docs/en/api/errors",
    "https://platform.claude.com/docs/en/api/client-sdks",
    "https://platform.claude.com/docs/en/api/sdks/python",
    "https://platform.claude.com/docs/en/api/sdks/typescript",
    "https://platform.claude.com/docs/en/api/sdks/java",
    "https://platform.claude.com/docs/en/api/sdks/go",
    "https://platform.claude.com/docs/en/api/sdks/ruby",
    "https://platform.claude.com/docs/en/api/sdks/csharp",
    "https://platform.claude.com/docs/en/api/sdks/php",
    "https://platform.claude.com/docs/en/api/rate-limits",
    "https://platform.claude.com/docs/en/api/service-tiers",
    "https://platform.claude.com/docs/en/api/versioning",
    "https://platform.claude.com/docs/en/api/ip-addresses",
    "https://platform.claude.com/docs/en/api/supported-regions",
    "https://platform.claude.com/docs/en/api/openai-sdk",
    "https://platform.claude.com/docs/en/resources/overview",
    "https://platform.claude.com/docs/en/about-claude/glossary",
    "https://platform.claude.com/docs/en/release-notes/system-prompts",
    "https://platform.claude.com/docs/en/about-claude/use-case-guides/overview",
    "https://platform.claude.com/docs/en/about-claude/use-case-guides/ticket-routing",
    "https://platform.claude.com/docs/en/about-claude/use-case-guides/customer-support-chat",
    "https://platform.claude.com/docs/en/about-claude/use-case-guides/content-moderation",
    "https://platform.claude.com/docs/en/about-claude/use-case-guides/legal-summarization",
    "https://platform.claude.com/docs/en/release-notes/overview",
]


def url_to_filename(url: str) -> str:
    path = urlparse(url).path
    path = re.sub(r'^/docs/en/', '', path.lstrip('/'))
    path = path.replace('/', '__')
    path = re.sub(r'[^a-zA-Z0-9_\-]', '_', path)
    return path + '.md'


def extract_markdown(page) -> str:
    """Extract clean content from a rendered page using JavaScript."""
    # Try to get the main article/content area text
    content = page.evaluate("""() => {
        // Try different selectors for main content
        const selectors = [
            'article',
            'main article',
            '.prose',
            'main',
            '[class*="content"]',
            '[class*="article"]',
        ];
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el && el.innerText && el.innerText.trim().length > 200) {
                return el.innerText;
            }
        }
        // Fallback: get body text minus nav/header/footer
        const remove = document.querySelectorAll('nav, header, footer, script, style, [class*="nav"], [class*="sidebar"], [class*="toc"]');
        remove.forEach(el => el.remove());
        return document.body.innerText;
    }""")
    return content or ""


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    total = len(ENGLISH_URLS)
    success = 0
    failed = []

    # Check which are already done
    skip = sum(1 for u in ENGLISH_URLS if (OUTPUT_DIR / url_to_filename(u)).exists())
    # Remove bad "Loading..." files
    for u in ENGLISH_URLS:
        fp = OUTPUT_DIR / url_to_filename(u)
        if fp.exists() and fp.stat().st_size < 500:
            fp.unlink()

    print(f"Scraping {total} pages to {OUTPUT_DIR}")
    print("-" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        for i, url in enumerate(ENGLISH_URLS, 1):
            filename = url_to_filename(url)
            filepath = OUTPUT_DIR / filename

            if filepath.exists():
                print(f"[{i:3d}/{total}] SKIP: {filename}")
                success += 1
                continue

            try:
                page.goto(url, wait_until="networkidle", timeout=20000)
                # Wait for content to render
                page.wait_for_timeout(1500)

                content = extract_markdown(page)
                title = page.title()

                if not content or len(content.strip()) < 100:
                    print(f"[{i:3d}/{total}] EMPTY: {filename}")
                    failed.append(url)
                    continue

                # Clean up
                content = re.sub(r'\n{3,}', '\n\n', content.strip())

                output = f"# {title}\nSource: {url}\n\n---\n\n{content}\n"
                filepath.write_text(output, encoding='utf-8')
                print(f"[{i:3d}/{total}] OK   ({len(content):6d} chars): {filename}")
                success += 1

            except Exception as e:
                print(f"[{i:3d}/{total}] ERR  {e}: {filename}")
                failed.append(url)

            time.sleep(DELAY)

        browser.close()

    print("-" * 60)
    print(f"Done: {success}/{total} pages")
    if failed:
        print(f"Failed ({len(failed)}):")
        for u in failed:
            print(f"  {u}")

    # Write index
    index_path = OUTPUT_DIR / "_index.md"
    lines = [f"# Anthropic Docs Index\nTotal: {total} | Success: {success}\n\n"]
    for url in ENGLISH_URLS:
        fn = url_to_filename(url)
        lines.append(f"- [{fn}](./{fn}) — {url}\n")
    index_path.write_text(''.join(lines), encoding='utf-8')
    print(f"Index: {index_path}")
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
