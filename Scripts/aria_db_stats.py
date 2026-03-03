import sqlite3
db = sqlite3.connect('/mnt/c/dev/Karma/k2/aria/aria.db')
c = db.cursor()
for t in ['facts','graph_nodes','graph_edges','experience_log','patterns','sessions','behavioral_rules','tool_usage']:
    count = c.execute('SELECT COUNT(*) FROM ' + t).fetchone()[0]
    print(t + ': ' + str(count))
db.close()
