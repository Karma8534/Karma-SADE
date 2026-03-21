---
name: karma-pitfall-vesper-falkordb-unverified
description: Use before declaring the Vesper→Karma growth pipeline working. Promotion count alone is insufficient evidence — must verify FalkorDB write succeeded AND pattern types are non-cascade_performance.
type: feedback
---

## Rule

Never declare "Vesper is working" based only on `total_promotions` count or `self_improving=true`. Verify TWO things: (1) a non-`cascade_performance` pattern exists in vesper_identity_spine.json, and (2) that pattern is visible in a live `/v1/chat` karmaCtx response.

**Why:** B4 (all 20 spine patterns were `cascade_performance` latency stats — not behavioral identity) and B5 (governor's FalkorDB write silently 404'd) meant the entire growth pipeline produced nothing useful for Karma. CC declared "growth working" based on promotion count. Karma received timing data, not learned persona. The pipeline ran but the pipe was leaking. Documented in CCSession032026A (2026-03-20, obs #8655).

**How to apply:** Verification sequence: `ssh vault-neo "ssh -p 2223 -l karma localhost 'python3 -c \"import json; d=json.load(open(\\\"/mnt/c/dev/Karma/k2/cache/vesper_identity_spine.json\\\")); types=set(p[\\\"type\\\"] for p in d.get(\\\"evolution\\\",{}).get(\\\"stable_identity\\\",[])); print(types)\\\""'` — if only `cascade_performance` returned, B4 is not fixed. Then check `/v1/chat` karmaCtx response for pattern text.

## Evidence

- CCSession032026A (2026-03-20): All 20 promoted patterns were `cascade_performance`. Karma had never received a single behavioral pattern from Vesper.
- Obs #8655 in claude-mem
