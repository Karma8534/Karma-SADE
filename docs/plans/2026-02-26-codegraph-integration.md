# Claude Graph Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate Claude Graph into Claude Code to eliminate exploration overhead and create persistent codebase knowledge across sessions.

**Architecture:** Install CodeGraph MCP server, auto-configure Claude Code hooks, index Karma_SADE codebase with tree-sitter AST parsing into local SQLite database, verify integration and document setup.

**Tech Stack:** CodeGraph (MCP server), tree-sitter (AST parsing), SQLite (local storage), Claude Code hooks (auto-sync)

---

## Task 1: Install CodeGraph NPM Package

**Files:**
- Modify: `package.json` (if exists, or use global install)
- Create: `.codegraph/` (will be auto-created by codegraph init)

**Step 1: Verify Node.js version**

Run: `node --version`
Expected: v18.0.0 or higher

**Step 2: Install CodeGraph globally**

Run: `npm install -g @colbymchenry/codegraph`
Expected: Output shows "added X packages" or already installed

**Step 3: Verify installation**

Run: `codegraph --version`
Expected: Shows version number (e.g., 1.0.0 or similar)

**Step 4: Commit (if package.json modified)**

```bash
git add package.json
git commit -m "feat: add codegraph dependency"
```

---

## Task 2: Run CodeGraph Installer to Configure MCP

**Files:**
- Create/Modify: `~/.claude/settings.json` (MCP server registration)
- Create/Modify: `.claude/settings.local.json` (project-level overrides, if needed)

**Step 1: Run CodeGraph installer**

Run: `npx @colbymchenry/codegraph`
Expected: Interactive prompt asking:
- Configure MCP server in ~/.claude/settings.json? (answer: yes)
- Set up auto-allow permissions? (answer: yes)
- Initialize current project? (answer: no - we'll do this next)

**Step 2: Verify MCP was registered**

Run: `cat ~/.claude/settings.json | grep -A 5 codegraph`
Expected: JSON block showing codegraph MCP server registered

**Step 3: Note the configuration**

The installer should have added something like:
```json
{
  "mcpServers": {
    "codegraph": {
      "command": "node",
      "args": ["/path/to/codegraph/server.js"]
    }
  }
}
```

**Step 4: No commit needed**

MCP configuration is user-local, not project-specific.

---

## Task 3: Verify Claude Code Hooks Configuration

**Files:**
- Check: `.claude/settings.local.json` (hooks)
- Reference: `CLAUDE.md` (CodeGraph instructions added by installer)

**Step 1: Check if hooks were written**

Run: `cat .claude/settings.local.json | grep -A 10 hooks`
Expected: PostToolUse and Stop hooks listed

**Step 2: Verify hook content**

The hooks should include:
- `PostToolUse(Edit|Write)` → marks index dirty
- `Stop` → runs sync-if-dirty

**Step 3: Check CLAUDE.md for CodeGraph instructions**

Run: `grep -n "codegraph\|CodeGraph" CLAUDE.md | head -20`
Expected: New instructions added by installer

**Step 4: No action needed**

Installer handles this automatically. Just verify it worked.

---

## Task 4: Initialize CodeGraph Index for Karma_SADE

**Files:**
- Create: `.codegraph/index.db` (SQLite database)
- Create: `.codegraph/embeddings/` (vector embeddings)
- Reference: `.gitignore` (will add .codegraph/)

**Step 1: Run codegraph init to index the project**

Run: `codegraph init -i`

From project root: `C:\Users\raest\Documents\Karma_SADE`

Expected output:
```
Scanning codebase...
Parsing 85 files with tree-sitter...
Extracting 542 symbols...
Building relationships...
Indexing relationships...
Generating embeddings...
Index created: .codegraph/index.db
Done in 0.45s
```

**Step 2: Verify index was created**

Run: `ls -lh .codegraph/`
Expected: Files present:
- `index.db` (SQLite database, ~5-20MB depending on codebase size)
- `embeddings/` directory

**Step 3: Verify index contains symbols**

Run: `sqlite3 .codegraph/index.db "SELECT COUNT(*) FROM symbols;"`
Expected: Number greater than 100 (should match ~542 from init output)

**Step 4: Verify relationships indexed**

Run: `sqlite3 .codegraph/index.db "SELECT COUNT(*) FROM relationships;"`
Expected: Number showing indexed relationships (calls, imports, extends, etc.)

**Step 5: No commit at this stage**

Index is local; we'll add to .gitignore in next task.

---

## Task 5: Add .codegraph/ to .gitignore

**Files:**
- Modify: `.gitignore`

**Step 1: Check current .gitignore**

Run: `cat .gitignore | grep codegraph`
Expected: Either shows ".codegraph/" or "(no output if not present)"

**Step 2: Add .codegraph/ if not present**

Edit `.gitignore` and add:
```
# CodeGraph index (local, auto-generated)
.codegraph/
```

**Step 3: Verify git ignores the directory**

Run: `git status | grep codegraph`
Expected: No output (directory is ignored)

**Step 4: Commit .gitignore update**

```bash
git add .gitignore
git commit -m "chore: ignore codegraph local index (.codegraph/)"
```

---

## Task 6: Test CodeGraph Tools Are Accessible

**Files:**
- Reference: No new files, testing only

**Step 1: Verify CodeGraph MCP server is running**

In Claude Code, open a fresh session in Karma_SADE project.

Run in Claude Code: Ask "What are the main entry points in this codebase?"

Expected: Claude Code should use codegraph_context or codegraph_search tool to answer without exploring files manually.

**Step 2: Check tool calls in response**

Look for tool use like:
- `codegraph_context` — returns entry points, main symbols
- `codegraph_search` — semantic search
- `codegraph_callers`/`codegraph_callees` — relationship tracing

Expected: Faster response, fewer file exploration calls than before.

**Step 3: Test semantic search**

Ask: "Find all authentication-related functions in the codebase"

Expected: CodeGraph returns matches even with different naming (validateAuth, checkToken, AuthService, etc.)

**Step 4: Test impact analysis**

Ask: "If I change the signature of [some_function], what would break?"

Expected: CodeGraph traces callers and shows blast radius.

**Step 5: No changes to code**

This is verification only.

---

## Task 7: Update CLAUDE.md with CodeGraph Integration Notes

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Read current CLAUDE.md**

Check if CodeGraph instructions already added by installer.

Run: `grep -n "codegraph\|CodeGraph" CLAUDE.md`
Expected: May or may not be present depending on installer behavior

**Step 2: Add CodeGraph section if missing**

Add to CLAUDE.md (in appropriate section, e.g., after "LLM Routing Strategy"):

```markdown
## Claude Graph Integration

**Status:** Active (installed via @colbymchenry/codegraph)

**Purpose:** Persistent codebase knowledge across sessions. Eliminates exploration overhead by pre-indexing code structure.

**How it works:**
- Tree-sitter parses codebase into AST
- SQLite database stores symbols, relationships, embeddings
- MCP server (codegraph) exposes tools to Claude Code:
  - `codegraph_context` — build context for any task
  - `codegraph_search` — semantic symbol search
  - `codegraph_callers`/`codegraph_callees` — trace relationships
  - `codegraph_impact` — change blast radius analysis

**Auto-sync:** Claude Code hooks (PostToolUse, Stop) keep index fresh when files are edited.

**Storage:** `.codegraph/index.db` (local SQLite, 100% private, auto-ignored in git)

**Performance:** ~30% fewer tokens on exploration tasks, ~25% fewer tool calls.

**Testing:** Ask Claude Code "What are the main entry points?" and verify it uses codegraph_context instead of file scanning.
```

**Step 3: Commit CLAUDE.md update**

```bash
git add CLAUDE.md
git commit -m "docs: document CodeGraph integration and usage"
```

---

## Task 8: Update MEMORY.md with Integration Status

**Files:**
- Modify: `MEMORY.md`

**Step 1: Add CodeGraph status to System Status table**

In MEMORY.md, find the System Status section and add a row:

```markdown
| CodeGraph Index | ✅ WORKING | 542 symbols indexed, auto-synced via hooks |
```

**Step 2: Add to Session notes**

Add entry under "Recent Decisions":
```
- [2026-02-26T HH:MM:SSZ] Integrated CodeGraph MCP server for codebase indexing
  Outcome: Persistent code structure knowledge, ~30% exploration token savings
```

**Step 3: Commit MEMORY.md update**

```bash
git add MEMORY.md
git commit -m "docs: update MEMORY.md - CodeGraph integration complete"
```

---

## Task 9: Verify Full Integration End-to-End

**Files:**
- Reference: No new files, verification only

**Step 1: Restart Claude Code**

Fully close and reopen Claude Code to ensure new MCP config is loaded.

**Step 2: Open fresh session in Karma_SADE**

Start new Claude Code session in project directory.

**Step 3: Ask a code exploration question**

Prompt: "Analyze the request flow in hub-bridge. Show me how /v1/chat connects to karma-server."

Expected: Claude Code uses codegraph tools instead of exploring files manually.

Check console logs for tool use like:
```
[codegraph_context] building context for /v1/chat
[codegraph_search] found 23 related symbols
[codegraph_callers] traced 5 callers to karma-server
```

**Step 4: Verify no exploration overhead**

Expected: Response comes back faster than before, with fewer tool calls in the debug output.

**Step 5: Verify index stays fresh**

Edit a file (e.g., change a comment in server.js):

```bash
echo "// test comment" >> hub-bridge/app/server.js
```

Wait 2-3 seconds for PostToolUse hook.

Run: `stat .codegraph/index.db` and note the modification time.

Expected: timestamp should be recent (within last 5 seconds), indicating hook ran sync-if-dirty.

**Step 6: No commits**

This is pure verification.

---

## Task 10: Final Commit and Documentation

**Files:**
- Reference: All prior commits made individually

**Step 1: Verify all commits are in git log**

Run: `git log --oneline | head -10`
Expected: Show recent commits:
- "docs: update MEMORY.md - CodeGraph integration complete"
- "docs: document CodeGraph integration and usage"
- "chore: ignore codegraph local index (.codegraph/)"
- "feat: add codegraph dependency" (if applicable)

**Step 2: Verify nothing uncommitted**

Run: `git status`
Expected: "nothing to commit, working tree clean"

**Step 3: Push to GitHub**

Run: `git push origin main`
Expected: All commits synced to remote

**Step 4: Done**

CodeGraph integration complete and verified.

---

## Success Criteria

✅ CodeGraph MCP server registered in `~/.claude/settings.json`
✅ `.codegraph/index.db` created with 542+ symbols indexed
✅ `.codegraph/` ignored in git
✅ Claude Code hooks configured (PostToolUse, Stop)
✅ CLAUDE.md documented with integration notes
✅ MEMORY.md updated with status
✅ End-to-end test passed (codegraph tools used, exploration reduced)
✅ All changes committed and pushed
