#!/usr/bin/env python3
"""auto_convert_pdfs.py — Auto-converts new PDFs in Karma_PDFs/Inbox/ to markdown.

Runs as a background watcher. When a new PDF appears in Inbox:
1. Convert to .md using pdfplumber
2. Move .md to docs/wip/ (auto-ingestion by wip-watcher)
3. Move PDF to Karma_PDFs/Done/

No manual work. Drop PDFs anywhere — they become knowledge.

Usage:
    python Scripts/auto_convert_pdfs.py          # run once (scan + convert)
    python Scripts/auto_convert_pdfs.py --watch   # continuous watcher mode
"""
import io
import os
import sys
import time
import shutil
import argparse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber not installed. Run: pip install pdfplumber")
    sys.exit(1)

INBOX = Path(r"C:\Users\raest\Documents\Karma_SADE\Karma_PDFs\Inbox")
DONE = Path(r"C:\Users\raest\Documents\Karma_SADE\Karma_PDFs\Done")
WIP = Path(r"C:\Users\raest\Documents\Karma_SADE\docs\wip")
SCAN_INTERVAL = 60  # seconds between scans in watch mode


def convert_pdf(pdf_path: Path) -> str:
    lines = [f"# {pdf_path.stem}", f"*Source: {pdf_path.name}*\n"]
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                if len(pdf.pages) > 1:
                    lines.append(f"\n---\n*Page {i+1}*\n")
                lines.append(text.strip())
    return "\n\n".join(lines)


def process_inbox():
    DONE.mkdir(parents=True, exist_ok=True)
    WIP.mkdir(parents=True, exist_ok=True)

    pdfs = [f for f in INBOX.iterdir() if f.suffix.lower() == '.pdf']
    if not pdfs:
        return 0

    converted = 0
    for pdf in pdfs:
        md_name = pdf.stem + ".md"
        wip_path = WIP / md_name

        if wip_path.exists():
            # Already converted — just move PDF to Done
            shutil.move(str(pdf), str(DONE / pdf.name))
            print(f"  [skip] {pdf.name} (already in wip)")
            continue

        try:
            md_content = convert_pdf(pdf)
            wip_path.write_text(md_content, encoding='utf-8')
            shutil.move(str(pdf), str(DONE / pdf.name))
            print(f"  [ok] {pdf.name} -> {md_name} ({len(md_content)} chars)")
            converted += 1
        except Exception as e:
            print(f"  [err] {pdf.name}: {e}")

    # Clean up any leftover error/verdict files
    for f in INBOX.iterdir():
        if f.suffix in ('.txt',) and ('.error.' in f.name or '.verdict.' in f.name):
            f.unlink()

    return converted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true", help="Continuous watcher mode")
    args = parser.parse_args()

    print(f"[auto-convert] Inbox: {INBOX}")
    print(f"[auto-convert] Output: {WIP}")

    if args.watch:
        print(f"[auto-convert] Watch mode: scanning every {SCAN_INTERVAL}s")
        while True:
            n = process_inbox()
            if n:
                print(f"[auto-convert] Converted {n} PDFs")
            time.sleep(SCAN_INTERVAL)
    else:
        n = process_inbox()
        print(f"[auto-convert] Done: {n} converted")


if __name__ == "__main__":
    main()
