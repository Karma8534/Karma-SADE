import sys, json, urllib.request

BASE = "http://127.0.0.1:9400"

def req(method, endpoint, data=None, timeout=120):
    url = f"{BASE}{endpoint}"
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        r = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method=method)
    else:
        r = urllib.request.Request(url, method=method)
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
