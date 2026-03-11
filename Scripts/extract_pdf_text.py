import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def try_extract(path):
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            print(f"Pages: {len(pdf.pages)}", file=sys.stderr)
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if text.strip():
                    print(f"\n--- PAGE {i+1} ---")
                    print(text[:3000])
        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    path = sys.argv[1]
    try_extract(path)
