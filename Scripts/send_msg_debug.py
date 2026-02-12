import sys, json, urllib.request, urllib.error
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

    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            b = json.loads(e.read().decode("utf-8"))
        except Exception:
            b = {"error": e.reason}
        print(f"HTTPError {e.code}: {b}")
        return e.code, b


def send_msg(text, wait=90):
    code1, body1 = req("POST", "/cockpit/send", {"text": text, "wait": wait})
    print("Step1:", code1, body1)
    code = body1.get("code")
    if not code:
        return body1
    code2, body2 = req("POST", "/cockpit/send", {"text": text, "wait": wait, "confirm_code": code}, timeout=wait+30)
    print("Step2:", code2, body2)
    return body2

if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) or "Say hello"
    result = send_msg(msg, wait=90)
    print(json.dumps(result, indent=2))
