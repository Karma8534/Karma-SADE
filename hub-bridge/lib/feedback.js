// lib/feedback.js — pure logic for /v1/feedback endpoint (no I/O)

/**
 * Remove pending_writes entries older than max_age_ms. Mutates `map` in place.
 */
export function prunePendingWrites(map, max_age_ms = 30 * 60 * 1000) {
  const cutoff = Date.now() - max_age_ms;
  for (const [key, entry] of map.entries()) {
    if (entry.ts < cutoff) map.delete(key);
  }
}

/**
 * Process a feedback signal for a pending write.
 * Returns { write_content, dpo_pair, delete_key } — all I/O is caller's responsibility.
 */
export function processFeedback(pending_writes, write_id, signal, note, turn_id = null) {
  const entry = pending_writes.get(write_id) || null;
  const proposed = entry?.content || null;
  const preferred = note || (signal === "up" ? proposed : null);
  // down always suppresses the write; note (if any) is captured in dpo_pair.preferred only
  // write_content is non-null only when a real pending write entry exists and signal is up
  const write_content = (signal === "up" && entry) ? (note || proposed) : null;

  const dpo_pair = {
    type: "dpo-pair",
    tags: ["dpo-pair"],
    write_id,
    turn_id,
    signal,
    proposed,
    preferred,
    ts: new Date().toISOString(),
  };

  return {
    write_content,
    dpo_pair,
    delete_key: entry ? write_id : null,
  };
}
