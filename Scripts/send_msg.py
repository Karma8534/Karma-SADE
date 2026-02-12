import sys, json, urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:9400"
TOKEN_FILE = Path.home() / "karma" / "cockpit-token.txt"


def _load_token() -> str:
    try:
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def req(method, endpoint, data=None, timeout=120):
    url = f"{BASE}{endpoint}"
    headers = {}
    token = _load_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
        r = urllib.request.Request(url, data=body, headers=headers, method=method)
    else:
        r = urllib.request.Request(url, headers=headers, method=method)

    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))

def send_msg(text, wait=90):
    code1, body1 = req("POST", "/cockpit/send", {"text": text, "wait": wait})
    code = body1.get("code")
    if not code:
        return body1
    code2, body2 = req("POST", "/cockpit/send", {"text": text, "wait": wait, "confirm_code": code}, timeout=wait+30)
    return body2

if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) or "Say hello"
    result = send_msg(msg, wait=90)
    print(json.dumps(result, indent=2))
