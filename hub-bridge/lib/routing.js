// STUB — implementation added in Phase C (drift-fix C2, C3)
// Tests in hub-bridge/tests/test_routing.js should FAIL against this stub.

export const ALLOWED_DEEP_MODELS = ["gpt-4o-mini"];

export function chooseModel(_deepMode, _env) {
  throw new Error("NOT IMPLEMENTED: chooseModel stub — Phase C C2/C3 required");
}

export function validateModelEnv(_env) {
  throw new Error("NOT IMPLEMENTED: validateModelEnv stub — Phase C C2 required");
}
