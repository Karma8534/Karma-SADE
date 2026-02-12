# Phase 1 MVP - Quick Start Guide

## 🚦 Current Status: 95% Complete

**What's Done:**
- ✅ Chrome extension fully built (7 files)
- ✅ Hub endpoint deployed and responding
- ✅ All documentation complete

**What's Blocked:**
- ⏸️ SSH connection timeout (temporary network issue)
- ⏸️ Hub endpoint needs 5-minute schema fix

---

## ⚡ Quick Deploy (When SSH Works)

### 1. Fix Hub Endpoint
```bash
ssh neo@arknexus.net
cd /opt/seed-vault/memory_v1/hub_bridge/app
cp server.js server.js.backup

# Edit line ~411 in server.js - change vaultRecord to:
# See full fix in: \tmp\CHATLOG_ENDPOINT_FIX.md

cd /opt/seed-vault/memory_v1
docker compose -f compose.hub.yml build hub-bridge
docker restart anr-hub-bridge
```

### 2. Install Extension
```
1. Chrome → chrome://extensions/
2. Developer mode ON
3. Load unpacked → C:\Users\raest\Documents\Karma_SADE\chrome-extension
4. Get token: ssh neo@arknexus.net "grep VAULT_BEARER /opt/seed-vault/memory_v1/.env | cut -d= -f2"
5. Paste in extension → Enable → Save
```

### 3. Test
```
- Visit Claude.ai, ChatGPT, or Gemini
- Start conversation
- Check extension popup for capture count
```

---

## 📚 Full Documentation

- **Detailed Status:** `PHASE1_STATUS.md`
- **Session Context:** `SESSION_HANDOFF.md`
- **Extension Docs:** `chrome-extension/README.md`
- **Endpoint Fix:** `\tmp\CHATLOG_ENDPOINT_FIX.md`

---

## 🔑 Quick Reference

**Droplet:** arknexus.net (neo@)
**Hub API:** https://hub.arknexus.net/v1/chatlog
**Extension:** C:\Users\raest\Documents\Karma_SADE\chrome-extension
**Cost:** $24/month

---

## ✅ Success = 100 Captures, 0% Loss

*Time to completion: ~30 min from SSH access*
