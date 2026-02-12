import sys, json, urllib.request, urllib.error

BASE = "http://127.0.0.1:9400"

def req(method, endpoint, data=None, timeout=120):
    url = f"{BASE}{endpoint}"
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        r = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method=method)
    else:
        r = urllib.request.Request(url, method=method)
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
