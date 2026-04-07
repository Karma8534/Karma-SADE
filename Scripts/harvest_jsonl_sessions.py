#!/usr/bin/env python3
"""
harvest_jsonl_sessions.py — Plan-A Task 3/4
Extracts DECISION/PROOF/PITFALL/DIRECTION events from Claude Code JSONL session files.
Outputs extracted observations to a staging JSON file for CC to save via claude-mem MCP.
Tracks processed files via .harvest_watermark_jsonl.json to enable resume.

Usage:
    python3 Scripts/harvest_jsonl_sessions.py [--test] [--limit N]
    --test   : process 1 file only, print results
    --limit N: process at most N files
"""

import json
import os
import sys
import hashlib
import re
import urllib.request
from pathlib import Path
from datetime import datetime

# Config
PROJECTS_DIR = Path(os.environ['USERPROFILE']) / '.claude' / 'projects' / 'C--Users-raest-Documents-Karma-SADE'
WATERMARK_FILE = PROJECTS_DIR / '.harvest_watermark_jsonl.json'
OUTPUT_FILE = Path(__file__).parent.parent / 'Scripts' / 'harvest_jsonl_output.json'
CLAUDE_MEM_URL = os.environ.get('CLAUDE_MEM_URL', 'http://127.0.0.1:37778')

# Keywords that signal a extractable event
EVENT_KEYWORDS = [
    'DECISION', 'PROOF', 'PITFALL', 'DIRECTION', 'INSIGHT',
    'root cause', 'verified', 'confirmed working', 'fixed by',
    'DRIFT DETECTED', 'BLOCKED', 'RESOLVED', 'architectural',
]

# Minimum substantive length for non-keyword text
MIN_SUBSTANTIVE_LEN = 600

def load_watermark():
    if WATERMARK_FILE.exists():
        with open(WATERMARK_FILE, 'r') as f:
            return json.load(f)
    return {'processed': [], 'version': 1}

def save_watermark(watermark):
    with open(WATERMARK_FILE, 'w') as f:
        json.dump(watermark, f, indent=2)

def extract_assistant_text(entry):
    """Extract text from an assistant JSONL entry."""
    msg = entry.get('message', {})
    if not msg:
        return ''
    content = msg.get('content', [])
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'text':
                parts.append(item.get('text', ''))
        return '\n'.join(parts)
    return ''

def extract_user_text(entry):
    """Extract text from a user JSONL entry."""
    msg = entry.get('message', {})
    if not msg:
        return ''
    content = msg.get('content', '')
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'text':
                parts.append(item.get('text', ''))
        return '\n'.join(parts)
    return ''

def is_extractable(text):
    """Return True if this text contains an extractable observation."""
    if len(text) < 100:
        return False
    text_upper = text.upper()
    for kw in EVENT_KEYWORDS:
        if kw.upper() in text_upper:
            return True
    # Substantive assistant response
    if len(text) >= MIN_SUBSTANTIVE_LEN:
        return True
    return False

def classify_event(text):
    """Return event type based on content."""
    text_upper = text.upper()
    if 'PITFALL' in text_upper:
        return 'pitfall'
    if 'PROOF' in text_upper or 'VERIFIED' in text_upper or 'CONFIRMED WORKING' in text_upper:
        return 'proof'
    if 'DECISION' in text_upper:
        return 'decision'
    if 'DIRECTION' in text_upper:
        return 'direction'
    if 'INSIGHT' in text_upper:
        return 'insight'
    return 'discovery'

def make_title(text, session_id):
    """Create a brief title from text content."""
    # First sentence or first 100 chars
    lines = text.strip().split('\n')
    first_line = lines[0].strip()[:120]
    if not first_line:
        first_line = text.strip()[:120]
    # Remove markdown
    first_line = re.sub(r'[#*`_]', '', first_line).strip()
    return first_line or f'Observation from session {session_id[:8]}'

def content_hash(text):
    return hashlib.md5(text.encode()).hexdigest()[:16]


def save_observation(observation):
    payload = json.dumps({
        'title': observation.get('title', ''),
        'text': observation.get('text', ''),
        'project': observation.get('project', 'Karma_SADE'),
    }).encode('utf-8')
    req = urllib.request.Request(
        f'{CLAUDE_MEM_URL}/api/memory/save',
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return 200 <= resp.status < 300


def ingest_observations(observations):
    ingested = 0
    for observation in observations:
        try:
            if save_observation(observation):
                ingested += 1
        except Exception as e:
            print(f'WARN: failed to ingest observation "{observation.get("title", "")[:80]}": {e}', file=sys.stderr)
    return ingested

def process_file(jsonl_path, seen_hashes):
    """Process a single JSONL file, return list of observations."""
    observations = []
    session_id = jsonl_path.stem

    try:
        with open(jsonl_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    except Exception as e:
        print(f'  ERROR reading {jsonl_path.name}: {e}', file=sys.stderr)
        return observations

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        entry_type = entry.get('type', '')
        timestamp = entry.get('timestamp', '')

        if entry_type == 'assistant':
            text = extract_assistant_text(entry)
            if text and is_extractable(text):
                h = content_hash(text)
                if h not in seen_hashes:
                    seen_hashes.add(h)
                    event_type = classify_event(text)
                    title = make_title(text, session_id)
                    observations.append({
                        'title': title,
                        'text': text[:4000],  # cap at 4000 chars for claude-mem
                        'type': event_type,
                        'project': 'Karma_SADE',
                        'source_session': session_id,
                        'source_timestamp': timestamp,
                        'content_hash': h,
                    })

    return observations

def main():
    test_mode = '--test' in sys.argv
    limit = None
    if '--limit' in sys.argv:
        idx = sys.argv.index('--limit')
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])

    # Load watermark
    watermark = load_watermark()
    processed_set = set(watermark.get('processed', []))

    # Get all JSONL files not yet processed
    all_files = sorted(PROJECTS_DIR.glob('*.jsonl'), key=lambda f: f.stat().st_mtime)
    pending = [f for f in all_files if str(f) not in processed_set]

    if limit:
        pending = pending[:limit]
    if test_mode:
        pending = pending[:1]

    print(f'Total files: {len(all_files)}')
    print(f'Already processed: {len(processed_set)}')
    print(f'Pending: {len(pending)}')
    if test_mode:
        print('TEST MODE: processing 1 file only')

    # Load existing output to append
    existing_output = []
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            existing_output = json.load(f)

    seen_hashes = set(obs.get('content_hash', '') for obs in existing_output)

    all_observations = list(existing_output)
    new_obs_count = 0
    new_observations = []

    for i, fpath in enumerate(pending):
        if i % 10 == 0 and i > 0:
            print(f'Progress: {i}/{len(pending)} files, {new_obs_count} new observations extracted...')

        obs = process_file(fpath, seen_hashes)
        all_observations.extend(obs)
        new_observations.extend(obs)
        new_obs_count += len(obs)

        if not test_mode:
            processed_set.add(str(fpath))
        else:
            print(f'Test file: {fpath.name}')
            print(f'Extracted {len(obs)} observations:')
            for o in obs[:3]:
                print(f'  [{o["type"]}] {o["title"][:80]}')
            if len(obs) > 3:
                print(f'  ... and {len(obs)-3} more')

    # Save output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_observations, f, indent=2, ensure_ascii=False)

    ingested_count = ingest_observations(new_observations)

    # Save watermark (not in test mode)
    if not test_mode:
        watermark['processed'] = sorted(processed_set)
        watermark['last_run'] = datetime.utcnow().isoformat() + 'Z'
        watermark['total_observations'] = len(all_observations)
        save_watermark(watermark)

    print(f'\nDone. New observations extracted: {new_obs_count}')
    print(f'Ingested to claude-mem: {ingested_count}')
    print(f'Total in output file: {len(all_observations)}')
    print(f'Output: {OUTPUT_FILE}')

if __name__ == '__main__':
    main()
