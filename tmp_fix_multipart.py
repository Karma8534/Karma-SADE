import sys

path = "/opt/seed-vault/memory_v1/hub_bridge/app/server.js"

with open(path, "r") as f:
    content = f.read()

# Backup
with open(path + ".bak.multipart", "w") as f:
    f.write(content)

# 1. Add parseMultipart helper function after parseBody
old_parsebody = '''function parseBody(req, maxSize = 2000000) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (chunk) => {
      data += chunk;
      if (data.length > maxSize) { reject(new Error("body_too_large")); req.destroy(); }
    });
    req.on("end", () => resolve(data));
    req.on("error", reject);
  });
}'''

new_parsebody = '''function parseBody(req, maxSize = 2000000) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (chunk) => {
      data += chunk;
      if (data.length > maxSize) { reject(new Error("body_too_large")); req.destroy(); }
    });
    req.on("end", () => resolve(data));
    req.on("error", reject);
  });
}

function parseBodyRaw(req, maxSize = 20000000) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    req.on("data", (chunk) => {
      size += chunk.length;
      if (size > maxSize) { reject(new Error("body_too_large")); req.destroy(); return; }
      chunks.push(chunk);
    });
    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", reject);
  });
}

/**
 * Parse multipart/form-data from raw Buffer.
 * Returns { fields: {name: string}, files: [{name, filename, contentType, data: Buffer}] }
 */
function parseMultipart(rawBuffer, boundary) {
  const fields = {};
  const files = [];
  const sep = Buffer.from('--' + boundary);
  const parts = [];

  // Split by boundary
  let start = 0;
  while (true) {
    const idx = rawBuffer.indexOf(sep, start);
    if (idx === -1) break;
    if (start > 0) {
      // Strip leading CRLF and trailing CRLF from part
      let partStart = start;
      let partEnd = idx;
      if (rawBuffer[partStart] === 0x0d && rawBuffer[partStart + 1] === 0x0a) partStart += 2;
      if (partEnd >= 2 && rawBuffer[partEnd - 2] === 0x0d && rawBuffer[partEnd - 1] === 0x0a) partEnd -= 2;
      if (partEnd > partStart) parts.push(rawBuffer.subarray(partStart, partEnd));
    }
    start = idx + sep.length;
  }

  for (const part of parts) {
    // Find header/body separator (double CRLF)
    const headerEnd = part.indexOf('\\r\\n\\r\\n');
    if (headerEnd === -1) continue;
    const headerStr = part.subarray(0, headerEnd).toString('utf8');
    const body = part.subarray(headerEnd + 4);

    const cdMatch = headerStr.match(/Content-Disposition:[^\\r\\n]*name="([^"]+)"(?:;\\s*filename="([^"]*)")?/i);
    if (!cdMatch) continue;
    const [, name, filename] = cdMatch;

    if (filename !== undefined) {
      const ctMatch = headerStr.match(/Content-Type:\\s*([^\\r\\n]+)/i);
      files.push({ name, filename, contentType: ctMatch ? ctMatch[1].trim() : 'application/octet-stream', data: body });
    } else {
      fields[name] = body.toString('utf8');
    }
  }
  return { fields, files };
}'''

if old_parsebody not in content:
    print("ERROR: parseBody function not found")
    sys.exit(1)

content = content.replace(old_parsebody, new_parsebody)
print("1. Added parseBodyRaw and parseMultipart helpers")

# 2. Replace the /v1/chat body parsing to handle both JSON and multipart
old_chat_parse = '''      const raw = await parseBody(req);
      if (req.headers['content-type'] && !req.headers['content-type'].includes('application/json')) { console.log(`[CHAT-DEBUG] non-JSON content-type: ${req.headers['content-type']}, body length: ${(raw||'').length}`); }
      let body; try { body = JSON.parse(raw || "{}"); } catch (e) { console.error(`[CHAT-DEBUG] JSON parse error: ${e.message}, content-type: ${req.headers['content-type']}, body first 200: ${(raw||'').slice(0,200)}`); return json(res, 400, { ok: false, error: "invalid_json" }); }'''

new_chat_parse = '''      const contentType = req.headers['content-type'] || '';
      let body, attachedFiles = [];

      if (contentType.includes('multipart/form-data')) {
        const boundaryMatch = contentType.match(/boundary=([^;\\s]+)/);
        if (!boundaryMatch) return json(res, 400, { ok: false, error: "missing_boundary" });
        const rawBuf = await parseBodyRaw(req, 20000000);
        const { fields, files } = parseMultipart(rawBuf, boundaryMatch[1]);
        body = { message: fields.message || '', conversation_id: fields.conversation_id || '' };
        attachedFiles = files;
        console.log(`[CHAT] multipart: message=${(body.message||'').length} chars, ${files.length} file(s): ${files.map(f => f.filename + ' (' + f.data.length + 'B)').join(', ')}`);
      } else {
        const raw = await parseBody(req);
        try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }
      }'''

if old_chat_parse not in content:
    print("ERROR: /v1/chat parse block not found")
    sys.exit(1)

content = content.replace(old_chat_parse, new_chat_parse)
print("2. Updated /v1/chat to handle multipart/form-data")

# 3. Find where userMessage is used and inject file content into the prompt
# After the userMessage extraction, add file processing
old_usermsg = '''      const userMessage = (body?.message || "").toString().trim();
      if (!userMessage) return json(res, 400, { ok: false, error: "missing_message" });'''

new_usermsg = '''      let userMessage = (body?.message || "").toString().trim();

      // Process attached files (from multipart upload)
      if (attachedFiles.length > 0) {
        const fileTexts = [];
        for (const af of attachedFiles) {
          const ext = (af.filename || '').split('.').pop().toLowerCase();
          if (ext === 'txt' || ext === 'md' || ext === 'csv' || ext === 'json' || ext === 'js' || ext === 'py' || ext === 'html' || ext === 'css' || ext === 'xml' || ext === 'yaml' || ext === 'yml' || ext === 'log' || ext === 'sh') {
            fileTexts.push(`--- FILE: ${af.filename} ---\\n${af.data.toString('utf8').slice(0, 30000)}\\n--- END ---`);
          } else if (ext === 'pdf') {
            try {
              const pdfText = pdfParse ? (await pdfParse(af.data)).text : null;
              if (pdfText && pdfText.trim()) {
                fileTexts.push(`--- FILE: ${af.filename} ---\\n${pdfText.slice(0, 30000)}\\n--- END ---`);
              } else {
                fileTexts.push(`--- FILE: ${af.filename} ---\\n[PDF extraction failed or empty]\\n--- END ---`);
              }
            } catch (e) {
              console.error(`[CHAT] PDF extraction failed for ${af.filename}:`, e.message);
              fileTexts.push(`--- FILE: ${af.filename} ---\\n[PDF extraction error: ${e.message}]\\n--- END ---`);
            }
          } else {
            fileTexts.push(`--- FILE: ${af.filename} ---\\n[Binary file, ${af.data.length} bytes, type: ${af.contentType}]\\n--- END ---`);
          }
        }
        if (fileTexts.length > 0) {
          const fileContext = fileTexts.join('\\n\\n');
          userMessage = userMessage
            ? userMessage + '\\n\\n' + fileContext
            : 'Please review the attached file(s):\\n\\n' + fileContext;
        }
      }

      if (!userMessage) return json(res, 400, { ok: false, error: "missing_message" });'''

if old_usermsg not in content:
    print("ERROR: userMessage block not found")
    sys.exit(1)

content = content.replace(old_usermsg, new_usermsg)
print("3. Added file content extraction and injection into chat prompt")

with open(path, "w") as f:
    f.write(content)

print("DONE - multipart file upload support added to /v1/chat")
