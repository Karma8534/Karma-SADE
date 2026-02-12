"""Enable the browser tool for Karma model"""
import sqlite3
import json

DB_PATH = r"C:\openwebui\venv\Lib\site-packages\open_webui\data\webui.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get Karma's current meta
cursor.execute("SELECT meta FROM model WHERE id = 'karma-sade-architect'")
row = cursor.fetchone()

if row:
    meta = json.loads(row[0]) if row[0] else {}
    tools = meta.get('toolIds', [])
    
    if 'karma-browser-control' not in tools:
        tools.append('karma-browser-control')
        meta['toolIds'] = tools
        cursor.execute("UPDATE model SET meta = ? WHERE id = 'karma-sade-architect'", (json.dumps(meta),))
        conn.commit()
        print("[OK] Enabled browser tool for Karma")
    else:
        print("[INFO] Browser tool already enabled for Karma")
    
    print(f"Current tools: {tools}")
else:
    print("[ERROR] Karma model not found")

conn.close()
