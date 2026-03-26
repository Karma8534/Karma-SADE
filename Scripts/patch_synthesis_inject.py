#!/usr/bin/env python3
"""Patch hub-bridge server.js to inject synthesis cache into Karma's context."""

path = "/opt/seed-vault/memory_v1/hub_bridge/app/server.js"

with open(path, "r") as f:
    code = f.read()

changes = 0

# STEP 1: Add synthesis cache variable + loader after loadDirectionMd
if "_synthesisCacheText" not in code:
    old = '  } catch (_) {}\n}\n\n// cc_scratchpad'
    new = '''  } catch (_) {}
}

// Synthesis cache - most recent [SYNTHESIS] entry from vault via FAISS.
// Refreshed every 5min. Injected into buildSystemText for session continuity.
let _synthesisCacheText = "";
async function loadSynthesisCache() {
  try {
    const r = await fetch("http://localhost:8081/v1/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: "synthesis session decisions insights pitfalls", limit: 1 }),
    });
    if (r.ok) {
      const d = await r.json();
      const top = (d.results || [])[0];
      if (top && top.content_preview) {
        _synthesisCacheText = top.content_preview;
        console.log("[SYNTHESIS] cache refreshed:", _synthesisCacheText.length, "chars");
      }
    }
  } catch (e) {
    console.error("[SYNTHESIS] cache refresh failed:", e.message);
  }
}

// cc_scratchpad'''
    if old in code:
        code = code.replace(old, new)
        changes += 1
        print("STEP 1: synthesis cache variable + loader ADDED")
    else:
        print("STEP 1: marker not found - checking alt pattern")
        # Try alternate marker
        if "loadDirectionMd" in code and "_synthesisCacheText" not in code:
            # Insert after the loadDirectionMd function closing brace
            idx = code.find("function loadDirectionMd()")
            if idx > 0:
                # Find the closing brace of this function
                brace_start = code.find("{", idx)
                depth = 0
                pos = brace_start
                while pos < len(code):
                    if code[pos] == "{":
                        depth += 1
                    elif code[pos] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    pos += 1
                insert_point = pos + 1
                synthesis_code = '''

// Synthesis cache - most recent [SYNTHESIS] entry from vault via FAISS.
// Refreshed every 5min. Injected into buildSystemText for session continuity.
let _synthesisCacheText = "";
async function loadSynthesisCache() {
  try {
    const r = await fetch("http://localhost:8081/v1/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: "synthesis session decisions insights pitfalls", limit: 1 }),
    });
    if (r.ok) {
      const d = await r.json();
      const top = (d.results || [])[0];
      if (top && top.content_preview) {
        _synthesisCacheText = top.content_preview;
        console.log("[SYNTHESIS] cache refreshed:", _synthesisCacheText.length, "chars");
      }
    }
  } catch (e) {
    console.error("[SYNTHESIS] cache refresh failed:", e.message);
  }
}
'''
                code = code[:insert_point] + synthesis_code + code[insert_point:]
                changes += 1
                print("STEP 1: synthesis cache ADDED (alt pattern)")
else:
    print("STEP 1: already present, skipping")

# STEP 2: Add synthesis injection in buildSystemText after MEMORY SPINE
if "RECENT SESSION SYNTHESIS" not in code:
    # Find the KARMA MEMORY SPINE injection line
    marker = 'KARMA MEMORY SPINE (recent)'
    idx = code.find(marker)
    if idx > 0:
        # Find the end of that block (the closing line with ---)
        line_end = code.find("\n", code.find("---", idx + len(marker)))
        if line_end > 0:
            insert = '''

  // Recent session synthesis - always injected for continuity
  if (_synthesisCacheText) {
    text += "\\n\\n--- RECENT SESSION SYNTHESIS ---\\n" + _synthesisCacheText + "\\n---";
  }'''
            code = code[:line_end] + insert + code[line_end:]
            changes += 1
            print("STEP 2: synthesis injection in buildSystemText ADDED")
    else:
        print("STEP 2: MEMORY SPINE marker not found")
else:
    print("STEP 2: already present, skipping")

# STEP 3: Add startup call and interval
if "loadSynthesisCache" in code and "setInterval(loadSynthesisCache" not in code:
    # Find where loadMemoryMd interval is set
    interval_marker = "setInterval(loadMemoryMd,"
    idx = code.find(interval_marker)
    if idx > 0:
        code = code[:idx] + "loadSynthesisCache(); setInterval(loadSynthesisCache, 5 * 60 * 1000);\n" + code[idx:]
        changes += 1
        print("STEP 3: synthesis startup + interval ADDED")
    else:
        print("STEP 3: loadMemoryMd interval not found")
else:
    if "setInterval(loadSynthesisCache" in code:
        print("STEP 3: already present, skipping")
    else:
        print("STEP 3: loadSynthesisCache not in code yet")

if changes > 0:
    with open(path, "w") as f:
        f.write(code)
    print(f"PATCH COMPLETE: {changes} changes applied")
else:
    print("NO CHANGES NEEDED")
