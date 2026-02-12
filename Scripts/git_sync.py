"""Git Sync — Stage, commit, and push memory changes to GitHub.

Step 4 of the Karma memory sync pipeline.
Only commits when there are actual changes. Skips silently otherwise.
"""
import subprocess
import os
from datetime import datetime

REPO_DIR = r"C:\Users\raest\Documents\Karma_SADE"
LOG_DIR = os.path.join(REPO_DIR, "Logs")
LOG_FILE = os.path.join(LOG_DIR, "karma-sade.log")


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [git_sync] {message}"
    print(line)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def git(*args, check=True):
    """Run a git command in the repo directory."""
    cmd = ["git", "-C", REPO_DIR] + list(args)
    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result


def main():
    log("Starting git sync")

    # Stage all changes (respects .gitignore)
    git("add", "-A")

    # Check if there's anything to commit
    result = git("diff", "--cached", "--quiet", check=False)
    if result.returncode == 0:
        log("No changes to commit — skipping")
        return

    # Count what changed
    stat = git("diff", "--cached", "--stat")
    changed_summary = stat.stdout.strip().split("\n")[-1] if stat.stdout.strip() else "changes"
    log(f"Changes detected: {changed_summary}")

    # Commit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    git("commit", "-m", f"auto: memory sync {timestamp}\n\nCo-Authored-By: Warp <agent@warp.dev>")
    log("Committed")

    # Push
    result = git("push", "origin", "main", check=False)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "rejected" in stderr or "conflict" in stderr:
            log(f"[WARN] Push rejected (remote has newer commits): {stderr[:200]}")
            log("Attempting pull --rebase then push...")
            git("pull", "--rebase", "origin", "main")
            git("push", "origin", "main")
            log("Push succeeded after rebase")
        else:
            log(f"[ERROR] Push failed: {stderr[:300]}")
            return
    else:
        log("Pushed to origin/main")

    log("Git sync complete")


if __name__ == "__main__":
    main()
