# Phase 1 MVP - Deployment Checklist

**Print this and check off each item as you complete it!**

---

## ☐ PART 1: Fix Hub Endpoint (5 minutes)

### ☐ 1.1 Connect to Droplet
```bash
ssh neo@arknexus.net
```
- **Status:** ☐ Connected

### ☐ 1.2 Backup Current File
```bash
cd /opt/seed-vault/memory_v1/hub_bridge/app
cp server.js server.js.backup-$(date +%Y%m%d-%H%M%S)
ls -lh server.js*
```
- **Status:** ☐ Backed up
- **Backup filename:** ________________

### ☐ 1.3 Edit server.js
```bash
nano server.js
```

Find line with `// NEW: /v1/chatlog endpoint` (around line 411)

Scroll down to the `vaultRecord` section (around line 434)

**REPLACE THIS:**
```javascript
      // Prepare Vault record
      const vaultRecord = {
        id: turn_id,
        type: "chatlog",
        tags: ["capture", provider, "extension"],
        timestamp: timestamp,
        data: {
          provider,
          url,
          thread_id: payload.thread_id || null,
          user_message,
          assistant_message,
          metadata: payload.metadata || {},
          captured_at: nowIso()
        },
        source: HUB_SOURCE,
        verifier: HUB_VERIFIER
      };
```

**WITH THIS:**
```javascript
      // Prepare conversation content as JSON string
      const conversationData = {
        provider,
        url,
        thread_id: payload.thread_id || null,
        user_message,
        assistant_message,
        metadata: payload.metadata || {},
        captured_at: nowIso()
      };

      // Prepare Vault record matching required schema
      const vaultRecord = {
        id: turn_id,
        type: "log",
        tags: ["capture", provider, "extension", "conversation"],
        timestamp: timestamp,
        content: JSON.stringify(conversationData),
        source: HUB_SOURCE,
        verification: HUB_VERIFIER,
        confidence: 1.0
      };
```

Save (Ctrl+O, Enter) and exit (Ctrl+X)

- **Status:** ☐ Edited

### ☐ 1.4 Rebuild Docker Image
```bash
cd /opt/seed-vault/memory_v1
docker compose -f compose.hub.yml build hub-bridge
```
- **Status:** ☐ Built
- **Build time:** ______ seconds

### ☐ 1.5 Restart Container
```bash
docker restart anr-hub-bridge
sleep 3
docker logs anr-hub-bridge --tail 10
```
- **Status:** ☐ Restarted
- **Expected output:** `hub-bridge v2.0.0 listening on :18090`

### ☐ 1.6 Test Endpoint
```bash
# Get token
TOKEN=$(grep VAULT_BEARER /opt/seed-vault/memory_v1/.env | cut -d= -f2)
echo "Token: $TOKEN"

# Test
curl -X POST https://hub.arknexus.net/v1/chatlog \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "provider": "claude",
    "url": "https://claude.ai/chat/test",
    "timestamp": "2026-02-12T23:00:00Z",
    "user_message": "Test question",
    "assistant_message": "Test response"
  }'
```

- **Status:** ☐ Tested
- **Expected response:** `{"id":"chatlog_...","stored":true,"timestamp":"..."}`
- **Actual response:** ___________________________________

### ☐ 1.7 Verify in Vault
```bash
docker exec anr-vault-db psql -U memory -d memoryvault -c \
  "SELECT id, type, tags, timestamp FROM memories WHERE tags @> ARRAY['capture'] ORDER BY timestamp DESC LIMIT 1;"
```
- **Status:** ☐ Verified in database
- **Record ID:** ___________________________________

---

## ☐ PART 2: Install Extension (5 minutes)

### ☐ 2.1 Open Extensions Page
1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top right)

- **Status:** ☐ Extensions page open

### ☐ 2.2 Load Extension
1. Click "Load unpacked"
2. Navigate to: `C:\Users\raest\Documents\Karma_SADE\chrome-extension`
3. Click "Select Folder"

- **Status:** ☐ Extension loaded
- **Extension ID:** ___________________________________

### ☐ 2.3 Get Vault Token
From droplet (already did this in 1.6):
```bash
ssh neo@arknexus.net "grep VAULT_BEARER /opt/seed-vault/memory_v1/.env | cut -d= -f2"
```
- **Status:** ☐ Token copied
- **Token (last 4 chars):** ____

### ☐ 2.4 Configure Extension
1. Click extension icon in Chrome toolbar
2. Paste token in "Vault Token" field
3. Toggle "Memory Capture" to ON
4. Click "Save Configuration"

- **Status:** ☐ Configured
- **Expected message:** "Configuration saved successfully!"

---

## ☐ PART 3: Test Captures (15 minutes)

### ☐ 3.1 Test Claude.ai
1. Go to `https://claude.ai/`
2. Start new conversation
3. Send: "Hello, this is test message 1 for my memory system"
4. Wait for response
5. Check extension popup - "Captured" count should be 1
6. Press F12 → Console
7. Look for: `[UAI Memory] Turn captured successfully`

- **Status:** ☐ Claude working
- **Captured count:** ___
- **Thread ID:** ___________________________________

### ☐ 3.2 Test ChatGPT
1. Go to `https://chatgpt.com/`
2. Start new conversation
3. Send: "Hello, this is test message 2 for my memory system"
4. Wait for response
5. Check extension popup - "Captured" count should be 2
6. Check console for success message

- **Status:** ☐ ChatGPT working
- **Captured count:** ___
- **Thread ID:** ___________________________________

### ☐ 3.3 Test Gemini
1. Go to `https://gemini.google.com/`
2. Start new conversation
3. Send: "Hello, this is test message 3 for my memory system"
4. Wait for response
5. Check extension popup - "Captured" count should be 3
6. Check console for success message

- **Status:** ☐ Gemini working
- **Captured count:** ___
- **Thread ID:** ___________________________________

### ☐ 3.4 Verify All 3 in Vault
```bash
ssh neo@arknexus.net
docker exec anr-vault-db psql -U memory -d memoryvault -c \
  "SELECT
    content::json->>'provider' as provider,
    content::json->>'url' as url,
    length(content::json->>'user_message') as user_msg_len,
    timestamp
   FROM memories
   WHERE tags @> ARRAY['capture']
   ORDER BY timestamp DESC
   LIMIT 10;"
```

- **Status:** ☐ All 3 verified in database
- **Claude record:** ☐ Found
- **ChatGPT record:** ☐ Found
- **Gemini record:** ☐ Found

---

## ☐ PART 4: Extended Testing (2 hours casual)

### ☐ 4.1 Claude.ai - 30 Captures
Have natural conversations, check popup periodically

- **Status:** ☐ 30 captures
- **Failed count:** ___ (should be 0)

### ☐ 4.2 ChatGPT - 30 Captures
Have natural conversations, check popup periodically

- **Status:** ☐ 30 captures
- **Failed count:** ___ (should be 0)

### ☐ 4.3 Gemini - 30 Captures
Have natural conversations, check popup periodically

- **Status:** ☐ 30 captures
- **Failed count:** ___ (should be 0)

### ☐ 4.4 Final Verification
```bash
ssh neo@arknexus.net
docker exec anr-vault-db psql -U memory -d memoryvault -c \
  "SELECT
    content::json->>'provider' as provider,
    COUNT(*) as count
   FROM memories
   WHERE tags @> ARRAY['capture']
   GROUP BY content::json->>'provider'
   ORDER BY provider;"
```

- **Status:** ☐ Verified
- **Claude count:** ___ (target: 31)
- **ChatGPT count:** ___ (target: 31)
- **Gemini count:** ___ (target: 31)
- **Total:** ___ (target: 93+)

---

## ☐ PART 5: Success Criteria Check

### ☐ 5.1 100+ Conversations Captured
- **Status:** ☐ Complete
- **Total captured:** ___

### ☐ 5.2 0% Data Loss
- **Status:** ☐ Verified
- **Failed captures:** ___ (target: 0)
- **Success rate:** ___% (target: 100%)

### ☐ 5.3 All 3 Platforms Working
- **Claude:** ☐ Working
- **ChatGPT:** ☐ Working
- **Gemini:** ☐ Working

### ☐ 5.4 No User-Visible Errors
- **Status:** ☐ No errors
- **Issues found:** ___________________________

### ☐ 5.5 Performance Check
- **Average capture time:** ___ ms (target: < 1000ms)
- **Extension overhead:** ☐ Negligible

---

## 🎉 COMPLETION

### ☐ Phase 1 MVP Complete!

**Final Stats:**
- Total captures: ___
- Success rate: ___%
- Platforms working: ___/3
- Time to complete: ___ hours
- Cost: $24/month

**Sign-off:**
- Date completed: _______________
- Your signature: _______________

---

## 📝 Notes & Issues

Use this space to note any problems or observations:

_______________________________________________

_______________________________________________

_______________________________________________

_______________________________________________

---

## 🚀 Next Steps (Phase 2)

☐ Add embeddings generation
☐ Implement semantic search
☐ Build retrieval API
☐ Create memory visualization dashboard

**Phase 2 Start Date:** _______________

---

**Good luck! You've got this! 🚀**
