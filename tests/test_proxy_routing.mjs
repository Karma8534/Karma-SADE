import test from "node:test";
import assert from "node:assert/strict";

import { shouldBypassHarnessForV1Chat } from "../hub-bridge/app/proxy.js";

test("browser workspace chat never bypasses the harness for short questions", () => {
  assert.equal(
    shouldBypassHarnessForV1Chat({
      message: "What exact token did I ask you to remember earlier?",
      session_id: "thread-1",
      stream: false,
    }),
    false,
  );

  assert.equal(
    shouldBypassHarnessForV1Chat({
      message: "What is 2+2?",
      session_id: "",
      stream: false,
    }),
    false,
  );
});
