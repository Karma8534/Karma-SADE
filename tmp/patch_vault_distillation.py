#!/usr/bin/env python3
"""
Patch /opt/seed-vault/memory_v1/compose/api/server.js to add distillation_brief
to the /v1/checkpoint/latest endpoint response.

Two changes:
1. After the karma_brief scan block (closing `}` at line 788), add a
   distillationFact scan that finds the most recent ledger entry tagged
   "karma_distillation" (no checkpoint_id filter).
2. Add `distillation_brief` field to the res.json() call.
"""

import sys

SERVER_PATH = '/opt/seed-vault/memory_v1/compose/api/server.js'

# === Exact strings to find and replace ===

# Old: closing brace of the karma_brief if-block + blank line before res.json
OLD_AFTER_BRIEF = """    }

    return res.status(200).json({
      ok: true,
      latest_checkpoint_fact: latest || null,
      artifacts,
      resume_prompt,
      karma_brief,
      meta: { generated_at: isoNow() }
    });"""

# New: same closing brace, then distillationFact scan, then res.json with new field
NEW_AFTER_BRIEF = """    }

    // Distillation brief: most recent karma_distillation entry in the ledger.
    // No checkpoint_id filter — always the latest synthesis Karma wrote.
    let distillation_brief = null;
    if (fs.existsSync(LEDGER_PATH)) {
      distillation_brief = await new Promise((resolve) => {
        let found = null;
        const rs3 = fs.createReadStream(LEDGER_PATH, { encoding: 'utf8' });
        const rl3 = readline.createInterface({ input: rs3, crlfDelay: Infinity });
        rl3.on('line', (ln) => {
          const t = (ln || '').trim();
          if (!t) return;
          let obj;
          try { obj = JSON.parse(t); } catch (_) { return; }
          if (!obj || !Array.isArray(obj.tags)) return;
          if (!obj.tags.includes('karma_distillation')) return;
          if (obj.content && obj.content.distillation_brief) {
            found = obj.content.distillation_brief;
          }
        });
        rl3.on('close', () => resolve(found));
        rl3.on('error', () => resolve(null));
        rs3.on('error', () => resolve(null));
      });
    }

    return res.status(200).json({
      ok: true,
      latest_checkpoint_fact: latest || null,
      artifacts,
      resume_prompt,
      karma_brief,
      distillation_brief,
      meta: { generated_at: isoNow() }
    });"""

def main():
    with open(SERVER_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    if OLD_AFTER_BRIEF not in content:
        print("ERROR: target string not found in server.js — patch aborted.")
        print("Looking for:")
        print(repr(OLD_AFTER_BRIEF[:120]))
        sys.exit(1)

    count = content.count(OLD_AFTER_BRIEF)
    if count > 1:
        print(f"ERROR: target string found {count} times — ambiguous, patch aborted.")
        sys.exit(1)

    new_content = content.replace(OLD_AFTER_BRIEF, NEW_AFTER_BRIEF, 1)

    # Sanity check: distillation_brief must now appear
    if 'distillation_brief' not in new_content:
        print("ERROR: patch did not insert distillation_brief — something went wrong.")
        sys.exit(1)

    with open(SERVER_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("Patch applied successfully.")
    print(f"  distillation_brief occurrences in patched file: {new_content.count('distillation_brief')}")

if __name__ == '__main__':
    main()
