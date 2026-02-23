"""
Patch karma-server/server.py for v2.13.0 — Epistemic Gate (Colby sign-off).

Changes:
1. /promote-candidates: accept approved_uuids list + audit fields
   - No auto-promotion: only Colby-approved UUIDs get promoted
   - Audit fields written to FalkorDB: promoted_by, promoted_at, promotion_reason
2. /candidates/list: return full UUID (not truncated) so UI can use it
"""

INFILE = '/opt/seed-vault/memory_v1/karma-core/server.py'

with open(INFILE, 'r') as f:
    lines = f.readlines()

print(f'Read {len(lines)} lines')

# ── 1. Replace promote_candidates_endpoint (lines 892-961, 1-indexed = 891-960, 0-indexed) ──

# Verify we're replacing the right block
assert lines[891].strip() == '@app.post("/promote-candidates")', f'Unexpected line 892: {lines[891]!r}'
assert lines[961].strip() == '@app.get("/candidates/count")', f'Unexpected line 962: {lines[961]!r}'

NEW_FN = '''\
@app.post("/promote-candidates")
async def promote_candidates_endpoint(request: Request):
    """Promote explicitly Colby-approved candidates to canonical in FalkorDB.

    Requires approved_uuids list — only those UUIDs get promoted.
    No auto-promotion: Colby\'s explicit sign-off is the gate.
    Audit fields (promoted_by, promoted_at, promotion_reason) written to FalkorDB + ledger."""
    import json as _json
    import falkordb as fdb
    try:
        body = {}
        try:
            body = await request.json()
        except Exception:
            pass

        approved_uuids = set(body.get("approved_uuids", []))
        authorized_by = body.get("authorized_by", "Colby")
        reason = body.get("reason", "manual_review")
        promoted_at = datetime.now(timezone.utc).isoformat()

        fdb_r = fdb.FalkorDB(host=config.FALKORDB_HOST, port=config.FALKORDB_PORT)
        g = fdb_r.select_graph(config.GRAPHITI_GROUP_ID)

        if not os.path.exists(CANDIDATES_JSONL):
            return JSONResponse({"ok": True, "promoted_count": 0, "skipped_count": 0,
                                 "authorized_by": authorized_by})

        entries = []
        with open(CANDIDATES_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(_json.loads(line))
                    except Exception:
                        pass

        promoted_count = 0
        skipped_count = 0
        promoted_facts = []

        for entry in entries:
            uuid_val = entry.get("uuid")
            if not uuid_val or entry.get("promoted"):
                continue
            if uuid_val in approved_uuids:
                try:
                    g.query(
                        "MATCH (e:Episodic {uuid: $uuid}) SET e.lane = \'canonical\', "
                        "e.promoted_by = $by, e.promoted_at = $at, e.promotion_reason = $reason",
                        {"uuid": uuid_val, "by": authorized_by, "at": promoted_at, "reason": reason}
                    )
                    entry["promoted"] = True
                    entry["promoted_by"] = authorized_by
                    entry["promoted_at"] = promoted_at
                    entry["promotion_reason"] = reason
                    promoted_count += 1
                    promoted_facts.append({"uuid": uuid_val[:8], "name": entry.get("name", "")})
                except Exception as pe:
                    print(f"[GATE] promote failed for {uuid_val[:8]}: {pe}")
            else:
                skipped_count += 1

        with open(CANDIDATES_JSONL, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(_json.dumps(entry) + "\\n")

        print(f"[GATE] Colby approved {promoted_count} candidates (authorized_by={authorized_by}), {skipped_count} remain pending")
        return JSONResponse({
            "ok": True,
            "promoted_count": promoted_count,
            "skipped_count": skipped_count,
            "authorized_by": authorized_by,
            "promoted_at": promoted_at,
            "promoted_facts": promoted_facts,
        })
    except Exception as e:
        print(f"[ERROR] /promote-candidates failed: {e}")
        traceback.print_exc()
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


'''

new_fn_lines = [line + '\n' for line in NEW_FN.split('\n')]
# Remove the extra final '\n' added by the last split element
if new_fn_lines and new_fn_lines[-1] == '\n':
    new_fn_lines.pop()

# Replace lines 891-960 (0-indexed) with new function
lines[891:961] = new_fn_lines

print(f'After fn replacement: {len(lines)} lines')
print('New line 892:', repr(lines[891]))

# ── 2. Fix UUID truncation in candidates_list ──
fixed_uuid = False
for i, line in enumerate(lines):
    if '"uuid": e.get("uuid", "")[:8],' in line:
        lines[i] = line.replace('"uuid": e.get("uuid", "")[:8],', '"uuid": e.get("uuid", ""),')
        print(f'UUID fix applied at line {i+1}')
        fixed_uuid = True
        break

if not fixed_uuid:
    print('WARNING: UUID truncation line not found!')

# ── 3. Write back ──
with open(INFILE, 'w') as f:
    f.writelines(lines)

print(f'Written {len(lines)} lines to {INFILE}')
print('Verifying...')

# Verify
with open(INFILE, 'r') as f:
    content = f.read()

assert 'approved_uuids' in content, 'approved_uuids not found!'
assert 'authorized_by' in content, 'authorized_by not found!'
assert 'promoted_by' in content, 'promoted_by not found!'
assert '"uuid": e.get("uuid", ""),' in content, 'UUID fix not found!'
assert '"uuid": e.get("uuid", "")[:8],' not in content, 'Old UUID truncation still present!'
print('All assertions passed!')
