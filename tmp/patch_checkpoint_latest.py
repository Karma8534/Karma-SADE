"""
Patch /v1/checkpoint/latest in vault api/server.js to include karma_brief.
Scans ledger for latest karma_brief fact matching the checkpoint_id.
"""

path = '/opt/seed-vault/memory_v1/compose/api/server.js'

with open(path, 'r') as f:
    content = f.read()

OLD_RETURN = '''    const resume_prompt = buildResumePrompt(latest, artifacts, resStatus);
    return res.status(200).json({
      ok: true,
      latest_checkpoint_fact: latest || null,
      artifacts,
      resume_prompt,
      meta: { generated_at: isoNow() }
    });'''

NEW_RETURN = '''    const resume_prompt = buildResumePrompt(latest, artifacts, resStatus);

    // Autonomous continuity: find karma_brief stored during last PROMOTE.
    // hub-bridge injects this into Karma\'s system prompt on every chat turn.
    const ckId = ck && ck.checkpoint_id ? ck.checkpoint_id : null;
    let karma_brief = null;
    if (ckId && fs.existsSync(LEDGER_PATH)) {
      karma_brief = await new Promise((resolve) => {
        let found = null;
        const rs2 = fs.createReadStream(LEDGER_PATH, { encoding: \'utf8\' });
        const rl2 = readline.createInterface({ input: rs2, crlfDelay: Infinity });
        rl2.on(\'line\', (ln) => {
          const t = (ln || \'\').trim();
          if (!t) return;
          let obj;
          try { obj = JSON.parse(t); } catch (_) { return; }
          if (!obj || !Array.isArray(obj.tags)) return;
          if (!obj.tags.includes(\'karma_brief\')) return;
          if (obj.content && obj.content.checkpoint_id === ckId) {
            found = obj.content.karma_brief || null;
          }
        });
        rl2.on(\'close\', () => resolve(found));
        rl2.on(\'error\', () => resolve(null));
        rs2.on(\'error\', () => resolve(null));
      });
    }

    return res.status(200).json({
      ok: true,
      latest_checkpoint_fact: latest || null,
      artifacts,
      resume_prompt,
      karma_brief,
      meta: { generated_at: isoNow() }
    });'''

if OLD_RETURN not in content:
    print('ERROR: target block not found')
    idx = content.find('buildResumePrompt')
    if idx >= 0:
        print('Context:')
        print(content[idx:idx+500])
    exit(1)

content = content.replace(OLD_RETURN, NEW_RETURN, 1)

with open(path, 'w') as f:
    f.write(content)

print('OK: /v1/checkpoint/latest now returns karma_brief')
print(f'New file size: {len(content)} chars')
