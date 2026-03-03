"""Replace /v1/feedback endpoint in karma-server to use turn_id + FalkorDB confidence."""
import sys

path = sys.argv[1] if len(sys.argv) > 1 else '/opt/seed-vault/memory_v1/karma-core/server.py'
with open(path, 'r') as f:
    content = f.read()

old_endpoint = '''@app.post("/v1/feedback")
async def api_feedback(request: Request):
    """
    When Colby praises a response or task outcome is positive,
    increment usage on retrieved memory nodes. Useful memories bubble up.
    """
    if not _MEMORY_TOOLS_AVAILABLE:
        return JSONResponse({"ok": False, "error": "memory_tools not loaded"}, status_code=503)
    try:
        import sqlite3 as _sq
        body = await request.json()
        memory_ids = body.get("memory_ids", [])
        boost = int(body.get("boost", 1))
        signal = body.get("signal", "positive")  # positive or negative

        db_path = os.getenv("MEMORY_DB_PATH", "/opt/seed-vault/memory_v1/memory.db")
        db = _sq.connect(db_path)
        updated = 0
        for mid in memory_ids:
            if signal == "positive":
                db.execute("UPDATE mem_cells SET usage = usage + ? WHERE id = ?", (boost, mid))
            elif signal == "negative":
                db.execute("UPDATE mem_cells SET usage = MAX(0, usage - ?) WHERE id = ?", (boost, mid))
            updated += db.total_changes
        db.commit()
        db.close()
        return JSONResponse({"ok": True, "updated": updated, "signal": signal})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)'''

new_endpoint = '''@app.post("/v1/feedback")
async def api_feedback(request: Request):
    """
    Thumbs up/down on a chat response. Adjusts confidence on the
    corresponding FalkorDB Episodic node and logs to feedback.jsonl.
    """
    try:
        body = await request.json()
        turn_id = body.get("turn_id", "").strip()
        signal = body.get("signal", "").strip()  # "up" or "down"

        if not turn_id:
            return JSONResponse({"ok": False, "error": "turn_id required"}, status_code=400)
        if signal not in ("up", "down"):
            return JSONResponse({"ok": False, "error": "signal must be 'up' or 'down'"}, status_code=400)

        # Confidence adjustment
        boost = 0.05 if signal == "up" else -0.10
        graph_name = config.GRAPHITI_GROUP_ID

        r = get_falkor()
        old_confidence = None
        new_confidence = None

        if r:
            # Find Episodic node whose name contains the turn_id
            safe_id = turn_id.replace('"', '\\\\"')
            query = f'MATCH (e:Episodic) WHERE e.name CONTAINS "{safe_id}" RETURN e.uuid, COALESCE(e.confidence, 1.0) LIMIT 1'
            try:
                result = r.execute_command("GRAPH.QUERY", graph_name, query)
                if isinstance(result, list) and len(result) > 1 and isinstance(result[1], list) and len(result[1]) > 0:
                    row = result[1][0]
                    ep_uuid = str(row[0])
                    old_confidence = float(row[1])
                    new_confidence = max(0.1, min(1.0, old_confidence + boost))
                    update_q = f'MATCH (e:Episodic {{uuid: "{ep_uuid}"}}) SET e.confidence = {round(new_confidence, 4)} RETURN e.uuid'
                    r.execute_command("GRAPH.QUERY", graph_name, update_q)
            except Exception as graph_err:
                print(f"[FEEDBACK] FalkorDB error (non-fatal): {graph_err}")

        # Log to feedback.jsonl
        feedback_path = os.getenv("FEEDBACK_JSONL", "/ledger/feedback.jsonl")
        try:
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "turn_id": turn_id,
                "signal": signal,
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
            }
            with open(feedback_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\\n")
        except Exception as log_err:
            print(f"[FEEDBACK] Log write error (non-fatal): {log_err}")

        return JSONResponse({
            "ok": True,
            "turn_id": turn_id,
            "signal": signal,
            "old_confidence": old_confidence,
            "new_confidence": new_confidence,
        })
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)'''

if old_endpoint not in content:
    print('ERROR: old feedback endpoint not found')
    sys.exit(1)

content = content.replace(old_endpoint, new_endpoint)

with open(path, 'w') as f:
    f.write(content)
print('OK - feedback endpoint replaced')
