/**
 * deferred_intent.js — Pure logic for Karma Deferred Intent Engine
 * No I/O, no external dependencies. Phase 4 Task 1.
 */

/**
 * Generate a unique intent ID.
 * @returns {string} e.g. "int_1741600000000_abc123"
 */
export function generateIntentId() {
  return "int_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8);
}

/**
 * Evaluate whether a trigger condition matches.
 * @param {object|null|undefined} trigger
 * @param {string} userMessage
 * @param {string} sessionPhase
 * @returns {boolean}
 */
export function triggerMatches(trigger, userMessage, sessionPhase = "active") {
  if (trigger == null) return false;

  switch (trigger.type) {
    case "always":
      return true;
    case "topic":
      return typeof trigger.value === "string" &&
        (userMessage || "").toLowerCase().includes(trigger.value.toLowerCase());
    case "phase":
      return trigger.value === sessionPhase;
    default:
      return false;
  }
}

/**
 * Build formatted text block for active intents to inject into context.
 * @param {Array} matchedIntents
 * @returns {string}
 */
export function buildActiveIntentsText(matchedIntents) {
  if (!matchedIntents || matchedIntents.length === 0) return "";

  const lines = matchedIntents.map(intent =>
    `- [${intent.action || "surface_before_responding"}] ${intent.intent} (fire_mode: ${intent.fire_mode}, id: ${intent.intent_id || "?"})`
  );

  return [
    "--- ACTIVE INTENTS ---",
    ...lines,
    "--- END ACTIVE INTENTS ---",
  ].join("\n");
}

/**
 * Get intents that should surface for the current message.
 * @param {Map} activeIntentsMap - Map of intent_id → intent object
 * @param {Set} firedThisSession - Set of intent_ids already fired this session
 * @param {string} userMessage
 * @param {string} sessionPhase
 * @returns {Array} matched intent objects
 */
export function getSurfaceIntents(activeIntentsMap, firedThisSession, userMessage, sessionPhase = "active") {
  const matched = [];

  for (const [id, intent] of activeIntentsMap) {
    if (intent.status !== "active") continue;
    if (intent.fire_mode === "once_per_conversation" && firedThisSession.has(id)) continue;
    if (triggerMatches(intent.trigger, userMessage, sessionPhase)) {
      matched.push(intent);
    }
  }

  return matched;
}
