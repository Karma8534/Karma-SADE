#!/usr/bin/env python3
"""
Apply core 5 KCC integrity fixes to server.py:
1. Add imports (aiofiles, httpx)
2. Add constants (PROMOTIONS_JSONL, VAULT_API_URL, _promote_lock)
3. Add helper function (_read_promoted_ids)
4. Replace log_to_ledger() with async loopback version
5. Replace /promote-candidates with append-only journal + WHERE clause
"""
import sys

def apply_fixes():
    server_file = '/opt/seed-vault/memory_v1/karma-core/server.py'

    with open(server_file, 'r', encoding='utf-8') as f:
        content = f.read()

    original_len = len(content)

    # ========== FIX 1: Add imports ==========
    print("[1/5] Adding imports...", end=' ')
    if 'import aiofiles' not in content:
        # Find 'import config' and add before it
        import_config_idx = content.find('import config')
        if import_config_idx > 0:
            imports_to_add = 'import aiofiles  # FIX [2.3]: Non-blocking file I/O\nimport httpx  # FIX [1.3]: Async HTTP loopback\n'
            content = content[:import_config_idx] + imports_to_add + content[import_config_idx:]
            print("✓")
        else:
            print("SKIP (no import config found)")
    else:
        print("SKIP (already present)")

    # ========== FIX 2: Add constants ==========
    print("[2/5] Adding constants...", end=' ')
    if 'PROMOTIONS_JSONL' not in content:
        candidates_idx = content.find('CANDIDATES_JSONL = ')
        if candidates_idx > 0:
            line_end = content.find('\n', candidates_idx)
            constants_to_add = '\n\nPROMOTIONS_JSONL = os.getenv("PROMOTIONS_JSONL", "/ledger/promotions.jsonl")  # FIX [3.1]\nVAULT_API_URL = "http://127.0.0.1:8080/v1/memory"  # FIX [1.3]\n_promote_lock = asyncio.Lock() if asyncio else None  # FIX [3.1]\n'
            content = content[:line_end] + constants_to_add + content[line_end:]
            print("✓")
        else:
            print("SKIP (no CANDIDATES_JSONL)")
    else:
        print("SKIP (already present)")

    # ========== FIX 3: Add helper function ==========
    print("[3/5] Adding helper function...", end=' ')
    if '_read_promoted_ids' not in content:
        helper_func = '''
# ─── Memory Integrity Gate - KCC Fixes [3.1, 2.3, 3.2, 3.4, 3.7] ────

async def _read_promoted_ids():
    """Read promoted IDs using non-blocking I/O. FIX [3.1]"""
    promoted = set()
    if os.path.exists(PROMOTIONS_JSONL):
        try:
            async with aiofiles.open(PROMOTIONS_JSONL, mode='r') as f:
                async for line in f:
                    try:
                        record = json.loads(line)
                        if record.get('status') == 'promoted':
                            promoted.add(record['id'])
                    except Exception:
                        continue
        except Exception as e:
            print(f'[WARN] Failed to read promoted IDs: {e}')
    return promoted

'''
        app_idx = content.find('app = FastAPI(')
        if app_idx > 0:
            content = content[:app_idx] + helper_func + content[app_idx:]
            print("✓")
        else:
            print("SKIP (no FastAPI)")
    else:
        print("SKIP (already present)")

    # ========== FIX 4: Replace log_to_ledger() ==========
    print("[4/5] Replacing log_to_ledger()...", end=' ')
    if 'def log_to_ledger(user_msg' in content:
        # Find the function
        start_idx = content.find('def log_to_ledger(user_msg')
        if start_idx > 0:
            # Find end of function (next line starting with 'def ' or 'async def ')
            # Go back to start of line
            start_idx = content.rfind('\n', 0, start_idx) + 1

            # Find end
            end_idx = content.find('\ndef ', start_idx + 1)
            if end_idx < 0:
                end_idx = content.find('\nasync def ', start_idx + 1)
            if end_idx < 0:
                end_idx = len(content)

            new_func = '''async def log_to_ledger(user_msg: str, assistant_msg: str, model_used: str = "unknown"):
    """Append to ledger via async loopback (non-blocking I/O). FIX [2.3]"""
    try:
        entry = {
            "id": f"karma_chat_{int(time.time())}_{hash(user_msg) % 10000:04d}",
            "type": "log",
            "tags": ["capture", "karma-terminal", "conversation"],
            "content": {
                "provider": "karma-terminal",
                "url": "terminal://karma-chat",
                "thread_id": "karma-terminal-session",
                "user_message": user_msg,
                "assistant_message": assistant_msg,
                "metadata": {"interface": "terminal", "model": model_used},
                "captured_at": datetime.now(timezone.utc).isoformat(),
            },
            "source": {"kind": "tool", "ref": "karma-terminal-chat"},
            "confidence": 1.0,
            "verification": {"verifier": "karma-chat-server", "status": "verified"},
        }
        # Use async loopback to vault API (FIX [1.3])
        async with httpx.AsyncClient() as client:
            response = await client.post(
                VAULT_API_URL,
                json=entry,
                timeout=10.0,
            )
            if response.status_code not in [200, 201]:
                print(f"[WARN] Ledger write failed: {response.status_code}")
    except Exception as e:
        print(f"[WARN] Failed to log to ledger: {e}")

'''
            content = content[:start_idx] + new_func + content[end_idx:]
            print("✓")
        else:
            print("SKIP")
    else:
        print("SKIP (not found)")

    # ========== FIX 5: Replace /promote-candidates endpoint ==========
    print("[5/5] Replacing /promote-candidates endpoint...", end=' ')
    if '@app.post("/promote-candidates")' in content:
        start_idx = content.find('@app.post("/promote-candidates")')
        if start_idx > 0:
            # Find end of endpoint
            end_idx = content.find('\n@app.', start_idx + 1)
            if end_idx < 0:
                end_idx = content.find('\nif __name__', start_idx + 1)

            new_endpoint = '''@app.post("/promote-candidates")
async def promote_candidates_endpoint(request: Request):
    """Promote candidates to canonical with append-only journal audit. FIX [3.4/3.7]"""
    global _promote_lock
    import falkordb as fdb
    try:
        async with _promote_lock:  # Non-blocking lock (FIX [3.1])
            body = {}
            try:
                body = await request.json()
            except Exception:
                pass

            approved_uuids = set(body.get("approved_uuids", []))
            authorized_by = body.get("authorized_by", "Colby")
            reason = body.get("reason", "manual_review")
            promoted_at = datetime.now(timezone.utc).isoformat()

            if not approved_uuids:
                return JSONResponse({"ok": True, "promoted_count": 0, "promoted_facts": []})

            fdb_r = fdb.FalkorDB(host=config.FALKORDB_HOST, port=config.FALKORDB_PORT)
            g = fdb_r.select_graph(config.GRAPHITI_GROUP_ID)

            promoted_count = 0
            promoted_facts = []

            for uuid_val in approved_uuids:
                try:
                    # WHERE lane != 'canonical' prevents bypass (FIX [3.2])
                    result = g.query(
                        "MATCH (e:Episodic {uuid: $uuid}) WHERE e.lane != 'canonical' "
                        "SET e.lane = 'canonical', e.promoted_by = $by, e.promoted_at = $at, e.promotion_reason = $reason",
                        {"uuid": uuid_val, "by": authorized_by, "at": promoted_at, "reason": reason}
                    )
                    if result:
                        promoted_count += 1
                        promoted_facts.append({"uuid": uuid_val[:8], "promoted_by": authorized_by})

                        # Append audit fact to promotions journal (append-only, non-blocking) - FIX [3.4]
                        audit_entry = {
                            "id": f"promotion_{uuid_val}_{int(time.time())}",
                            "uuid": uuid_val,
                            "promoted_by": authorized_by,
                            "promoted_at": promoted_at,
                            "promotion_reason": reason,
                            "status": "promoted"
                        }
                        async with aiofiles.open(PROMOTIONS_JSONL, "a") as f:
                            await f.write(json.dumps(audit_entry) + "\\n")
                except Exception as pe:
                    print(f"[GATE] promote failed for {uuid_val[:8]}: {pe}")

            print(f"[GATE] Promoted {promoted_count} candidates via {authorized_by}")
            return JSONResponse({
                "ok": True,
                "promoted_count": promoted_count,
                "authorized_by": authorized_by,
                "promoted_at": promoted_at,
                "promoted_facts": promoted_facts,
            })
    except Exception as e:
        print(f"[ERROR] /promote-candidates failed: {e}")
        traceback.print_exc()
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

'''
            content = content[:start_idx] + new_endpoint + content[end_idx:]
            print("✓")
        else:
            print("SKIP")
    else:
        print("SKIP (not found)")

    # Write file
    with open(server_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ File updated: {len(content)} bytes (was {original_len})")

    # Verify syntax
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', server_file], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Syntax check: PASS")
        return True
    else:
        print(f"✗ Syntax check: FAIL\n{result.stderr}")
        return False

if __name__ == '__main__':
    try:
        if apply_fixes():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
