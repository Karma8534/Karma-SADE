#!/usr/bin/env python3
"""batch_pdf_to_md.py — Convert all PDFs in Karma_PDFs/ to markdown files.

Extracts text from each PDF using pdfplumber, writes clean .md files.
Skips already-converted files. No manual work needed.

Usage:
    python Scripts/batch_pdf_to_md.py                    # dry run (show what would be converted)
    python Scripts/batch_pdf_to_md.py --execute          # actually convert
    python Scripts/batch_pdf_to_md.py --execute --wip    # convert + copy to docs/wip/ for auto-ingestion
"""
import os
import sys
import argparse
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber not installed. Run: pip install pdfplumber")
    sys.exit(1)

KARMA_PDFS = Path(r"C:\Users\raest\Documents\Karma_SADE\Karma_PDFs")
OUTPUT_DIR = KARMA_PDFS / "Converted"
WIP_DIR = Path(r"C:\Users\raest\Documents\Karma_SADE\docs\wip")


def extract_pdf_to_md(pdf_path: Path) -> str:
    """Extract text from PDF and format as markdown."""
    lines = []
    lines.append(f"# {pdf_path.stem}")
    lines.append(f"*Converted from: {pdf_path.name}*\n")

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    if len(pdf.pages) > 1:
                        lines.append(f"\n---\n*Page {i+1}*\n")
                    lines.append(text.strip())
    except Exception as e:
        lines.append(f"\n**ERROR extracting: {e}**")

    return "\n\n".join(lines)


def find_pdfs(source_dir: Path) -> list:
    """Find all PDFs recursively, excluding Converted/ and Done/."""
    pdfs = []
    for root, dirs, files in os.walk(source_dir):
        # Skip output directories
        dirs[:] = [d for d in dirs if d not in ("Converted", "Done", "Processing", "Gated")]
        for f in files:
            if f.lower().endswith(".pdf"):
                pdfs.append(Path(root) / f)
    return sorted(pdfs)


def main():
    parser = argparse.ArgumentParser(description="Batch convert PDFs to markdown")
    parser.add_argument("--execute", action="store_true", help="Actually convert (default is dry run)")
    parser.add_argument("--wip", action="store_true", help="Also copy to docs/wip/ for auto-ingestion")
    parser.add_argument("--limit", type=int, default=0, help="Max files to convert (0 = all)")
    args = parser.parse_args()

    pdfs = find_pdfs(KARMA_PDFS)
    print(f"Found {len(pdfs)} PDFs in {KARMA_PDFS}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    converted = 0
    skipped = 0
    errors = 0

    for pdf in pdfs:
        md_name = pdf.stem + ".md"
        out_path = OUTPUT_DIR / md_name

        if out_path.exists():
            skipped += 1
            continue

        if not args.execute:
            print(f"  [DRY RUN] Would convert: {pdf.name} ({pdf.stat().st_size / 1024:.0f}KB)")
            converted += 1
            if args.limit and converted >= args.limit:
                break
            continue

        print(f"  Converting: {pdf.name}...", end=" ", flush=True)
        try:
            md_content = extract_pdf_to_md(pdf)
            out_path.write_text(md_content, encoding="utf-8")
            print(f"OK ({len(md_content)} chars)")

            if args.wip:
                wip_path = WIP_DIR / md_name
                if not wip_path.exists():
                    wip_path.write_text(md_content, encoding="utf-8")

            converted += 1
            if args.limit and converted >= args.limit:
                print(f"  Reached limit of {args.limit}")
                break
        except Exception as e:
            print(f"ERROR: {e}")
            errors += 1

    print(f"\nDone: {converted} converted, {skipped} skipped (already exist), {errors} errors")
    if not args.execute:
        print("This was a DRY RUN. Add --execute to actually convert.")


if __name__ == "__main__":
    main()
