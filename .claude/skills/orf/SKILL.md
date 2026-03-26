# ORF — Organic Reasoning Flow

## When to invoke

After brainstorming and debugging produce a plan, BEFORE executing. Every architectural or build decision. No exceptions.

ORF is the final gate between "plan" and "build." It catches overengineering, blind plan-following, missing blockers, and complexity that a simpler solution eliminates.

## The flow

Run through these 9 steps. Write the answers out loud. Do not skip any.

### 1. Who has the problem?
Name the entity (Julian, Karma, CC, Colby, hub-bridge, etc.) and what they experience.

### 2. What is currently happening?
Describe the actual current behavior — verified, not assumed. If you haven't checked, check now.

### 3. Why is this a problem?
One sentence. If you can't say it in one sentence, you don't understand the problem.

### 4. What does a successful outcome look like?
Concrete, testable. "I can run X and see Y." Not "the system is improved."

### 5. Input → Processing → Output
- **Input:** What enters the system? Where from? What format?
- **Processing:** What transformation happens? By whom?
- **Output:** What does the user/system receive?

### 6. Rules
- The system MUST: [list hard requirements]
- The system MUST NEVER: [list constraints]
- If something fails, it SHOULD: [describe graceful degradation]

### 7. Simplest working architecture
Propose the minimum viable version. If it's more than one script or one service, justify why. Default assumption: simpler is better. 350 lines when 30 will do is a failure.

### 8. Failure points
List every way this can break. For each: how likely? How do we detect it? How do we recover?

### 9. Smallest testable version
One command that proves it works. If you can't test it in one command, the architecture is too complex for v1.

## After running ORF

- Compare ORF output against the original plan
- Every gap between them is a potential pitfall
- Save gaps as PITFALL observations immediately
- Revise the plan to match ORF output
- Only then execute

## Why this exists

Session 144: brainstorming + debugging produced a 350-line Python synthesis_worker with 6 moving parts (watermark, vault writes, keyword filtering, separate Ollama call, cron, session-end hook wiring). ORF reduced it to a 30-line bash script with one SSH hop. 12 prompt iterations and 60% of session context burned before ORF was applied. Never again.
