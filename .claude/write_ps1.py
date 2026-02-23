
import sys

ps1_content = r"""# Get-KarmaContext.ps1
# Fetches Karma's live CC session brief at CC session start.
# Primary: SSH to vault-neo, run gen-cc-brief.py, read cc-session-brief.md.
# Writes to cc-session-brief.md and karma-context.md (both gitignored) for CC to read.
# Fallback: K2 FalkorDB at 192.168.0.226:6379.

param(
    [string]      = "\..\..\karma-context.md",
    [string]         = "\..\..\karma-context.md.tmp",
    [string] = "\..\..\cc-session-brief.md",
    [string]   = "vault-neo",
    [string]          = "192.168.0.226",
    [int]             = 6379,
    [string]       = "neo_workspace",
    [int]    = 15,
    [int]        = 2000
)
PLACEHOLDER
"""

print(ps1_content[:200])
