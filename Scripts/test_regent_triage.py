#!/usr/bin/env python3
import sys
sys.path.insert(0, '/mnt/c/dev/Karma/k2/aria')
import regent_triage

r = regent_triage.classify({"from": "colby", "content": "hello"})
assert r == "sovereign", f"expected sovereign, got {r}"

r1 = regent_triage.classify({"from": "karma", "content": "Thanks got it"})
r2 = regent_triage.classify({"from": "kcc", "content": "Please restart aria service"})
print("sovereign OK")
print("ack test:", r1)
print("action test:", r2)
print("triage OK")
