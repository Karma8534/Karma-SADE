# Karma SADE Session Startup Instructions

**Purpose**: Automatically sync documentation to the vault-neo droplet at the start of each new conversation.

---

## Quick Start

At the beginning of each new conversation session, run:

```powershell
C:\Users\raest\Documents\Karma_SADE\Scripts\session-startup.ps1
```

Or from any directory:

```powershell
& "C:\Users\raest\Documents\Karma_SADE\Scripts\session-startup.ps1"
```

This will:
1. ✅ Sync all documentation to vault-neo droplet
2. ✅ Update README with current memory stats
3. ✅ Update timestamp on the droplet

---

## What Gets Synced

The following files are automatically copied to `vault-neo:~/karma-sade-docs/`:

1. **09-rebuild-complete.md** - Complete rebuild documentation
2. **08-session-handoff.md** - Planning document
3. **05-user-facts.json** - Current memory state
4. **README.md** - Auto-generated directory overview
5. **Latest session notes** - If any `*-session-notes.md` files exist

---

## Manual Sync (Python)

If you prefer to run the Python script directly:

```powershell
python C:\Users\raest\Documents\Karma_SADE\Scripts\sync_docs_to_droplet.py
```

This provides more detailed logging.

---

## Verification

Check that files were synced:

```powershell
ssh vault-neo "ls -lh ~/karma-sade-docs/"
```

View the README on the droplet:

```powershell
ssh vault-neo "cat ~/karma-sade-docs/README.md"
```

Check last sync time:

```powershell
ssh vault-neo "cat ~/karma-sade-docs/.last_sync"
```

---

## Automated Sync (Optional)

### Option 1: Schedule at Login

Create a scheduled task that runs at user login:

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\session-startup.ps1" -WorkingDirectory "C:\Users\raest\Documents\Karma_SADE\Scripts"
$trigger = New-ScheduledTaskTrigger -AtLogon -User "raest"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "KarmaSADE-SessionStartup" -Action $action -Trigger $trigger -Settings $settings -Description "Sync Karma SADE documentation at session start" -Force
```

### Option 2: Schedule Daily

Run once per day at a specific time (e.g., 9 AM):

```powershell
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "C:\Users\raest\Documents\Karma_SADE\Scripts\sync_docs_to_droplet.py" -WorkingDirectory "C:\Users\raest\Documents\Karma_SADE\Scripts"
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "KarmaSADE-DailyDocSync" -Action $action -Trigger $trigger -Settings $settings -Description "Daily documentation sync to droplet" -Force
```

### Option 3: Manual Only

Just run the script manually at the start of each session. This gives you the most control.

---

## Troubleshooting

### SSH Connection Failed

**Problem**: Cannot connect to vault-neo

**Solution**:
1. Verify SSH config: `cat ~/.ssh/config`
2. Test connection: `ssh vault-neo "echo OK"`
3. Check droplet is running (DigitalOcean dashboard)

### Files Not Syncing

**Problem**: Files exist locally but don't appear on droplet

**Solution**:
1. Check file exists: `Test-Path C:\Users\raest\Documents\Karma_SADE\Memory\09-rebuild-complete.md`
2. Check permissions on droplet: `ssh vault-neo "ls -la ~/karma-sade-docs/"`
3. Review logs: `Get-Content C:\Users\raest\Documents\Karma_SADE\Logs\droplet-sync.log -Tail 50`

### Slow Performance

**Problem**: Sync takes too long

**Solution**:
- Normal sync time: 5-10 seconds
- If slower, check network connection
- Large session notes files may take longer

---

## Log Files

All sync activity is logged to:

```
C:\Users\raest\Documents\Karma_SADE\Logs\droplet-sync.log
```

View recent activity:

```powershell
Get-Content C:\Users\raest\Documents\Karma_SADE\Logs\droplet-sync.log -Tail 50
```

---

## Benefits

✅ **Automatic backup**: Documentation is always on the droplet  
✅ **Session continuity**: New sessions can reference previous work  
✅ **Disaster recovery**: Files safe even if PAYBACK has issues  
✅ **Remote access**: View documentation from anywhere via SSH  
✅ **Version tracking**: Timestamp shows when last synced  

---

## Related Scripts

- **sync_docs_to_droplet.py** - Main sync script (Python)
- **session-startup.ps1** - Convenient PowerShell wrapper
- **karma_memory_sync.py** - Memory system sync (runs every 30 min)
- **upload_rebuild_docs.py** - One-time Vault API upload

---

**Created**: 2026-02-10  
**Last Updated**: 2026-02-10 03:42 UTC  
**Status**: Production Ready



