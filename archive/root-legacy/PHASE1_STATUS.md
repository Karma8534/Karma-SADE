# Phase 1: Capture MVP - Current Status

**Date:** February 12, 2026
**Session:** Continuation from context limit

---

## ✅ COMPLETED

### 1. Infrastructure
- [x] Droplet resized from 2GB → 4GB RAM
- [x] All services running (Hub, Vault API, PostgreSQL, Caddy)
- [x] Backup created and verified
- [x] Hub endpoint `/v1/chatlog` deployed and responding

### 2. Chrome Extension
- [x] `manifest.json` - Manifest V3 configuration
- [x] `background.js` - Service worker with API communication
- [x] `content-claude.js` - Claude.ai scraper
- [x] `content-openai.js` - ChatGPT scraper
- [x] `content-gemini.js` - Gemini scraper
- [x] `popup.html` - Configuration UI
- [x] `popup.js` - UI logic and storage management
- [x] Placeholder icons created (16px, 48px, 128px)
- [x] README.md with installation and usage docs

### 3. Documentation
- [x] Project context saved in `.claude/project.json`
- [x] Extension README with complete instructions
- [x] Vault schema fix documented in `/tmp/CHATLOG_ENDPOINT_FIX.md`
- [x] Deployment script created in `/tmp/deploy_chatlog_fix.sh`

---

## ⏳ PENDING

### 1. Hub Endpoint Fix (BLOCKING)

**Issue:** Vault schema validation failing

**Current error:**
```json
{
  "ok": false,
  "error": "schema_validation_failed",
  "details": [
    "missing: content, source, confidence, verification",
    "type must be: fact|preference|project|artifact|log|contact",
    "data field not allowed"
  ]
}
```

**Fix Required:**
Update `/opt/seed-vault/memory_v1/hub_bridge/app/server.js` chatlog endpoint:

```javascript
// OLD (BROKEN)
const vaultRecord = {
  id: turn_id,
  type: "chatlog",  // ❌ Invalid
  data: { ... },    // ❌ Wrong field
  verifier: HUB_VERIFIER  // ❌ Wrong name
};

// NEW (CORRECT)
const conversationData = { provider, url, user_message, assistant_message, ... };
const vaultRecord = {
  id: turn_id,
  type: "log",  // ✅ Valid type
  content: JSON.stringify(conversationData),  // ✅ Correct field
  source: HUB_SOURCE,
  verification: HUB_VERIFIER,  // ✅ Correct name
  confidence: 1.0  // ✅ Required field
};
```

**Deployment Steps:**
```bash
# 1. SSH to droplet
ssh neo@arknexus.net

# 2. Backup and edit server.js
cp /opt/seed-vault/memory_v1/hub_bridge/app/server.js{,.backup}
nano /opt/seed-vault/memory_v1/hub_bridge/app/server.js
# (Make changes per /tmp/CHATLOG_ENDPOINT_FIX.md)

# 3. Rebuild and restart
cd /opt/seed-vault/memory_v1
docker compose -f compose.hub.yml build hub-bridge
docker restart anr-hub-bridge

# 4. Verify
docker logs anr-hub-bridge --tail 10
```

**Files:**
- Fix documented: `/tmp/CHATLOG_ENDPOINT_FIX.md`
- Fixed code: `/tmp/chatlog_endpoint_fixed.js`
- Deployment script: `/tmp/deploy_chatlog_fix.sh`

### 2. Extension Testing

Once Hub endpoint is fixed:

**Install Extension:**
1. Chrome → `chrome://extensions/`
2. Enable Developer mode
3. Load unpacked → `C:\Users\raest\Documents\Karma_SADE\chrome-extension`
4. Configure vault token (get from droplet `.env`)
5. Enable memory capture

**Test Each Platform:**
1. Claude.ai - Start conversation, verify capture
2. ChatGPT - Start conversation, verify capture
3. Gemini - Start conversation, verify capture

**Verify in Vault:**
```bash
ssh neo@arknexus.net
docker exec anr-vault-db psql -U memory -d memoryvault -c \
  "SELECT id, type, tags, timestamp FROM memories WHERE tags @> ARRAY['capture'] ORDER BY timestamp DESC LIMIT 10;"
```

### 3. Phase 1 Success Criteria

- [ ] 100 conversation turns captured
- [ ] 0% data loss (all turns successfully stored)
- [ ] All 3 platforms working reliably
- [ ] Average capture latency < 1 second
- [ ] No user-visible errors

---

## 🚧 CURRENT BLOCKER

**SSH Connection Timeout**

The droplet is responding to HTTPS (Hub endpoint returns 401 unauthorized, which is correct behavior), but SSH connections are timing out.

**Possible causes:**
1. Cloudflare proxy blocking SSH
2. Firewall configuration
3. Temporary network issue

**Workaround:**
- Hub endpoint fix is documented and ready to deploy
- Extension is complete and ready to test
- Can proceed with deployment when SSH access returns

**Test endpoint is alive:**
```bash
curl -X POST https://hub.arknexus.net/v1/chatlog \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test" \
  -d '{"provider":"claude","url":"test","timestamp":"2026-02-12T00:00:00Z","user_message":"test","assistant_message":"test"}'

# Response: {"ok":false,"error":"unauthorized"}  ✅ Endpoint is responding!
```

---

## 📊 ARCHITECTURE

```
Chrome Extension                  Hub API                     Vault API
┌──────────────┐                 ┌──────────┐                ┌──────────┐
│ content-*.js │───┐              │          │                │          │
│ (3 scrapers) │   │              │  Node.js │                │ FastAPI  │
└──────────────┘   │   POST       │  server  │   POST         │ Python   │
                   ├──────────────►  .js     ├───────────────►│          │
┌──────────────┐   │   /v1/       │          │   /v1/memory  │          │
│ background.js│───┘   chatlog    │  Port    │                │  Port    │
│ (API client) │                  │  18090   │                │  8080    │
└──────────────┘                  └──────────┘                └────┬─────┘
       ▲                                                            │
       │                                                            ▼
┌──────┴───────┐                                            ┌──────────────┐
│  popup.html  │                                            │ PostgreSQL   │
│  (Config UI) │                                            │ memoryvault  │
└──────────────┘                                            └──────────────┘

HTTPS: hub.arknexus.net (Caddy reverse proxy)
Internal: localhost (Docker network)
```

---

## 💰 COST BREAKDOWN

| Component | Cost | Notes |
|-----------|------|-------|
| Droplet (4GB) | $24/mo | DigitalOcean NYC3 |
| Embeddings API | $0/mo | Phase 2 only ($5-10/mo) |
| Domain | $0/mo | Already owned |
| **Total Phase 1** | **$24/mo** | Capture-only MVP |
| **Total Phase 2** | **$29-34/mo** | With embeddings |

Annual: $288/year (Phase 1) or $348-408/year (Phase 2)

---

## 📁 FILE LOCATIONS

### Extension Files (Local)
```
C:\Users\raest\Documents\Karma_SADE\chrome-extension\
├── manifest.json
├── background.js
├── content-claude.js
├── content-openai.js
├── content-gemini.js
├── popup.html
├── popup.js
├── icons/
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md
```

### Hub Code (Droplet)
```
/opt/seed-vault/memory_v1/hub_bridge/app/
├── server.js          ← Needs schema fix
├── Dockerfile
└── package.json

/opt/seed-vault/memory_v1/
└── compose.hub.yml    ← For rebuilding
```

### Fix Documentation (Local Temp)
```
\tmp\
├── CHATLOG_ENDPOINT_FIX.md      ← Detailed fix instructions
├── chatlog_endpoint_fixed.js     ← Corrected code
├── deploy_chatlog_fix.sh         ← Deployment script
└── chatlog_endpoint_addition.js  ← Original broken code
```

---

## 🎯 NEXT ACTIONS

### Immediate (When SSH Available)
1. SSH to droplet: `ssh neo@arknexus.net`
2. Apply Hub endpoint fix per `/tmp/CHATLOG_ENDPOINT_FIX.md`
3. Test endpoint with curl (includes full request in doc)
4. Verify successful storage in Vault

### Then
5. Install extension in Chrome
6. Configure with vault token
7. Test on Claude.ai
8. Test on ChatGPT
9. Test on Gemini
10. Verify 100 captures with 0% loss

### Success = Phase 1 Complete!

---

## 📞 SUPPORT INFO

- Droplet: arknexus-vault-01 (arknexus.net)
- Hub endpoint: https://hub.arknexus.net/v1/chatlog
- SSH user: neo
- Docker containers: anr-hub-bridge, anr-vault-api, anr-vault-db, anr-vault-caddy

---

**Status:** Ready to deploy endpoint fix and begin testing.
**Blocker:** SSH timeout (endpoint is alive, just need shell access)
**Time to completion:** ~2-4 hours once SSH is available
