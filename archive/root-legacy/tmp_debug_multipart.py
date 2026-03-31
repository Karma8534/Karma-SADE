import sys

path = "/opt/seed-vault/memory_v1/hub_bridge/app/server.js"

with open(path, "r") as f:
    content = f.read()

# Add deeper debug logging to multipart path
old = """        const rawBuf = await parseBodyRaw(req, 20000000);
        const { fields, files } = parseMultipart(rawBuf, boundaryMatch[1]);
        body = { message: fields.message || '', conversation_id: fields.conversation_id || '' };
        attachedFiles = files;
        console.log(`[CHAT] multipart: message=${(body.message||'').length} chars, ${files.length} file(s): ${files.map(f => f.filename + ' (' + f.data.length + 'B)').join(', ')}`);"""

new = """        const rawBuf = await parseBodyRaw(req, 20000000);
        console.log(`[CHAT-MP] raw buffer: ${rawBuf.length} bytes, boundary: ${boundaryMatch[1]}`);
        const { fields, files } = parseMultipart(rawBuf, boundaryMatch[1]);
        console.log(`[CHAT-MP] parsed fields: ${JSON.stringify(Object.keys(fields))}, files: ${files.length}`);
        // Debug: show what parts were found
        const sep = Buffer.from('--' + boundaryMatch[1]);
        let count = 0, idx = 0;
        while ((idx = rawBuf.indexOf(sep, idx)) !== -1) { count++; idx += sep.length; }
        console.log(`[CHAT-MP] boundary occurrences: ${count}`);
        // Show first 500 bytes as hex-safe string
        const preview = rawBuf.subarray(0, 500).toString('latin1').replace(/[\\x00-\\x1f]/g, c => '\\\\x' + c.charCodeAt(0).toString(16).padStart(2,'0'));
        console.log(`[CHAT-MP] preview: ${preview}`);
        body = { message: fields.message || '', conversation_id: fields.conversation_id || '' };
        attachedFiles = files;
        console.log(`[CHAT] multipart: message=${(body.message||'').length} chars, ${files.length} file(s): ${files.map(f => f.filename + ' (' + f.data.length + 'B)').join(', ')}`);"""

if old not in content:
    print("ERROR: target not found")
    sys.exit(1)

content = content.replace(old, new)

with open(path, "w") as f:
    f.write(content)

print("OK - deep multipart debug logging added")
