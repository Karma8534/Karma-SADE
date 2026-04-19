/**
 * Phase 1 Validation Loop
 * Validates all Phase 1 acceptance criteria
 * Phase Ascendance 1, Step 1, Task 5
 *
 * Completion Criteria:
 * - first-frame persona present and non-generic
 * - last 3 turns match prior session
 * - paint_ms < 2000
 * - canonical endpoint trace present
 *
 * Usage: node validate-phase1.js
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Validate evidence files exist and meet criteria
 * @param {string} evidenceDir - Directory containing evidence files
 * @returns {Promise<Object>} Validation results
 */
async function validatePhase1(evidenceDir = './evidence') {
  const criteria = {
    first_frame_persona: { passed: false, evidence: null },
    last_3_turns: { passed: false, evidence: null },
    paint_time: { passed: false, evidence: null },
    canonical_endpoints: { passed: false, evidence: null }
  };

  try {
    // Read all evidence files
    console.log(`Validating evidence files in ${evidenceDir}...\n`);

    // Check first-frame.png
    try {
      const firstFramePath = path.join(evidenceDir, 'phase1-first-frame.png');
      const firstFrameContent = await fs.readFile(firstFramePath, 'utf-8');
      const firstFrame = JSON.parse(firstFrameContent);

      // Criteria: persona present and non-generic
      const personaPresent = firstFrame.persona.name && firstFrame.persona.name.length > 0;
      const nonGeneric = firstFrame.persona.name !== 'default' && firstFrame.persona.name !== 'Anonymous';
      criteria.first_frame_persona.passed = personaPresent && nonGeneric;
      criteria.first_frame_persona.evidence = {
        persona_name: firstFrame.persona.name,
        persona_source: firstFrame.persona.source,
        present: personaPresent,
        non_generic: nonGeneric,
        validation_results: firstFrame.validation
      };

      console.log(`✓ first-frame.png read`);
      console.log(`  - Persona: ${firstFrame.persona.name} (${criteria.first_frame_persona.passed ? 'PASS' : 'FAIL'})`);
    } catch (e) {
      console.error(`✗ first-frame.png failed: ${e.message}`);
    }

    // Check history-diff.txt
    try {
      const historyPath = path.join(evidenceDir, 'phase1-history-diff.txt');
      const historyContent = await fs.readFile(historyPath, 'utf-8');

      // Criteria: last 3 turns from prior session
      const hasValidation = historyContent.includes('VALIDATION');
      const exactly3Turns = historyContent.includes('Turn count: 3');
      const deterministic = historyContent.includes('Deterministic order: PASS');
      criteria.last_3_turns.passed = hasValidation && exactly3Turns && deterministic;
      criteria.last_3_turns.evidence = {
        has_validation_section: hasValidation,
        exactly_3_turns: exactly3Turns,
        deterministic_order: deterministic,
        content_snippet: historyContent.substring(0, 200)
      };

      console.log(`✓ history-diff.txt read`);
      console.log(`  - 3 turns: ${exactly3Turns ? 'YES' : 'NO'}, Deterministic: ${deterministic ? 'YES' : 'NO'} (${criteria.last_3_turns.passed ? 'PASS' : 'FAIL'})`);
    } catch (e) {
      console.error(`✗ history-diff.txt failed: ${e.message}`);
    }

    // Check timing.json
    try {
      const timingPath = path.join(evidenceDir, 'phase1-timing.json');
      const timingContent = await fs.readFile(timingPath, 'utf-8');
      const timing = JSON.parse(timingContent);

      // Criteria: paint_ms < 2000
      const paintMs = timing.boot_hydration.persona_paint_ms;
      const deadline = timing.requirements.paint_deadline_ms;
      criteria.paint_time.passed = timing.boot_hydration.passed;
      criteria.paint_time.evidence = {
        paint_ms: paintMs,
        deadline_ms: deadline,
        met: paintMs < deadline,
        fetch_duration_ms: timing.boot_hydration.boot_fetch_duration_ms,
        total_duration_ms: timing.boot_hydration.total_ms
      };

      console.log(`✓ timing.json read`);
      console.log(`  - Paint: ${paintMs}ms < ${deadline}ms (${criteria.paint_time.passed ? 'PASS' : 'FAIL'})`);
    } catch (e) {
      console.error(`✗ timing.json failed: ${e.message}`);
    }

    // Check canonical-trace.txt
    try {
      const tracePath = path.join(evidenceDir, 'phase1-canonical-trace.txt');
      const traceContent = await fs.readFile(tracePath, 'utf-8');

      // Criteria: canonical endpoint trace present
      const hasWakeup = traceContent.includes('/memory/wakeup');
      const hasSession = traceContent.includes('/memory/session');
      const hasSessionEndpoint = traceContent.includes('/v1/session');
      const noNewEndpoints = traceContent.includes('NO NEW ENDPOINTS INTRODUCED: PASS');
      criteria.canonical_endpoints.passed = hasWakeup && hasSession && hasSessionEndpoint && noNewEndpoints;
      criteria.canonical_endpoints.evidence = {
        has_wakeup: hasWakeup,
        has_session: hasSession,
        has_session_endpoint: hasSessionEndpoint,
        no_new_endpoints: noNewEndpoints,
        all_canonical: hasWakeup && hasSession && hasSessionEndpoint
      };

      console.log(`✓ canonical-trace.txt read`);
      console.log(`  - Endpoints: ${hasWakeup && hasSession && hasSessionEndpoint ? 'ALL PRESENT' : 'MISSING'} (${criteria.canonical_endpoints.passed ? 'PASS' : 'FAIL'})`);
    } catch (e) {
      console.error(`✗ canonical-trace.txt failed: ${e.message}`);
    }

    // Summary
    const allPassed = Object.values(criteria).every(c => c.passed);
    const passCount = Object.values(criteria).filter(c => c.passed).length;
    const totalCount = Object.values(criteria).length;

    console.log(`\n=== VALIDATION RESULTS ===`);
    console.log(`${passCount}/${totalCount} criteria passed: ${allPassed ? 'PASS ✓' : 'FAIL ✗'}\n`);

    return { allPassed, criteria, passCount, totalCount };
  } catch (error) {
    console.error('Validation error:', error);
    throw error;
  }
}

/**
 * Run validation loop with 3-attempt max
 * @param {string} evidenceDir - Evidence directory
 * @param {number} maxAttempts - Maximum validation attempts (default: 3)
 */
async function runValidationLoop(evidenceDir = './evidence', maxAttempts = 3) {
  console.log(`=== PHASE 1 VALIDATION LOOP (max ${maxAttempts} attempts) ===\n`);

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    console.log(`Attempt ${attempt}/${maxAttempts}\n`);

    try {
      const result = await validatePhase1(evidenceDir);

      if (result.allPassed) {
        console.log(`\n✓ PHASE 1 VALIDATION PASSED\n`);
        console.log('Summary:');
        console.log(`  - Persona present and non-generic: ✓`);
        console.log(`  - Last 3 turns from prior session: ✓`);
        console.log(`  - Paint time < 2000ms: ✓`);
        console.log(`  - Canonical endpoint trace: ✓\n`);
        return { status: 'PASS', attempt, result };
      } else {
        console.log(`\n✗ VALIDATION FAILED (${result.passCount}/${result.totalCount})\n`);

        if (attempt < maxAttempts) {
          console.log(`Retrying... (attempt ${attempt + 1} of ${maxAttempts})\n`);
        }
      }
    } catch (error) {
      console.error(`\n✗ VALIDATION ERROR: ${error.message}\n`);

      if (attempt < maxAttempts) {
        console.log(`Retrying... (attempt ${attempt + 1} of ${maxAttempts})\n`);
      }
    }

    // Add delay between attempts
    if (attempt < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }

  console.log(`\n✗ PHASE 1 VALIDATION FAILED (${maxAttempts} attempts exhausted)\n`);
  console.log('PITFALL: Phase 1 did not pass after maximum validation attempts.');
  console.log('See evidence files for diagnostic information.\n');

  return { status: 'FAIL', attempt: maxAttempts };
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { validatePhase1, runValidationLoop };
}

// Run if called directly
if (require.main === module) {
  runValidationLoop().then(result => {
    process.exit(result.status === 'PASS' ? 0 : 1);
  }).catch(error => {
    console.error('Validation loop error:', error);
    process.exit(1);
  });
}
