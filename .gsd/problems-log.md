## 2026-03-19 BOM IN karma_regent.py
**Symptom:** vesper_patch_regent.py returned "syntax error: invalid non-printable character U+FEFF" on all karma_regent.py patches.
**Root cause:** karma_regent.py on K2 had a UTF-8 BOM (0xEF 0xBB 0xBF) prepended. ast.parse() fails on BOM even though Python runtime tolerates it.
**Fix:** `data = open(path,'rb').read(); if data.startswith(b'\xef\xbb\xbf'): open(path,'wb').write(data[3:])` before patching.
**Status:** RESOLVED

## 2026-03-19 /regent ENDPOINT SPECULATION
**Symptom:** Told Colby there was no direct Vesper chat UI; described curl workarounds for coordination bus.
**Root cause:** Answered from memory/inference without reading server.js. GET /regent exists at line 2450, serves public/regent.html.
**Fix:** Always grep server.js routes before answering questions about what endpoints exist.
**Status:** RESOLVED — /anchor invoked
