import sys, json, urllib.request, urllib.error

BASE = "http://127.0.0.1:9400"

def req(endpoint, payload, timeout=30):
    url = f"{BASE}{endpoint}"
    body = json.dumps(payload).encode("utf-8")
    r = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            b = json.loads(e.read().decode("utf-8"))
        except Exception:
            b = {"error": e.reason}
        return e.code, b

if __name__ == "__main__":
    js = sys.argv[1] if len(sys.argv) > 1 else "document.title"
    desc = sys.argv[2] if len(sys.argv) > 2 else "debug"
    code1, body1 = req("/cockpit/exec", {"js": js, "description": desc})
    if "code" in body1:
        code = body1["code"]
        code2, body2 = req("/cockpit/exec", {"js": js, "description": desc, "confirm_code": code})
        print(json.dumps(body2, indent=2))
    else:
        print(json.dumps(body1, indent=2))
