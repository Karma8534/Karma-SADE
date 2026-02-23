# K2 Consciousness Worker

K2 is the local persistence layer for Karma. It runs every 60 seconds to:
1. Read Karma's state from droplet (vault-neo)
2. Process locally with available LLM
3. Log results to shared drive
4. (Later: write decisions back to droplet)

## Setup

### Prerequisites
- Python 3.8+ on K2
- `requests` library: `pip install requests`
- Tailscale running on K2 (connects to vault-neo)
- Shared drive: `\\PAYBACK\Users\raest\OneDrive\Karma`

### Installation

1. Copy `karma-k2-sync.py` and `karma-k2-sync.bat` to:
   ```
   \\PAYBACK\Users\raest\OneDrive\Karma\
   ```

2. Create logs directory:
   ```cmd
   mkdir "\\PAYBACK\Users\raest\OneDrive\Karma\logs"
   mkdir "\\PAYBACK\Users\raest\OneDrive\Karma\Processing"
   ```

3. Test manually:
   ```powershell
   cd "\\PAYBACK\Users\raest\OneDrive\Karma"
   python karma-k2-sync.py
   ```
   Watch for log files in `Processing/` directory.

### Scheduled Execution

1. Open Task Scheduler: `taskschd.msc`
2. Create new task:
   - Name: "Karma K2 Sync"
   - Trigger: Repeat every 60 seconds
   - Action: Run `\\PAYBACK\Users\raest\OneDrive\Karma\karma-k2-sync.bat`

## Status

- [x] Initial script written
- [ ] Test connection to droplet via Tailscale
- [ ] Verify logging to shared drive
- [ ] Task Scheduler setup
- [ ] Add write-back to droplet endpoints

## Next Steps

Once this is working:
1. Build droplet endpoints: `/v1/decisions`, `/v1/graph/state`
2. Implement write-back to droplet
3. Add error handling and retry logic
4. Monitor logs for performance

---
Session: 2026-02-23 | K2 Persistence Layer v0.1
