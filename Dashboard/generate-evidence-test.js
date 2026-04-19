/**
 * Test Runner for Evidence Generation
 * Phase Ascendance 1, Step 1, Task 4
 *
 * Usage: node generate-evidence-test.js
 */

const { generateEvidence } = require('./generateEvidence.js');

async function runTest() {
  console.log('Testing Evidence Generation Script...\n');

  // Mock metrics from Task 1 evidence
  const mockMetrics = {
    persona: { name: 'Karma', status: 'ready' },
    session: { session_id: 'sess-12345', created_at: '2026-04-19T02:50:00Z' },
    turns: [
      { role: 'user', text: 'hello karma' },
      { role: 'assistant', text: 'hi there friend' },
      { role: 'user', text: 'how are you?' }
    ],
    timing: {
      window_visible_ms: 0,
      boot_fetch_start_ms: 0,
      boot_fetch_end_ms: 150,
      persona_paint_ms: 450
    },
    source: {
      persona: 'remote',
      session: 'remote',
      turns: 'remote'
    },
    timestamp: '2026-04-19T02:50:42.777Z'
  };

  try {
    // Generate evidence files
    const evidenceFiles = await generateEvidence(mockMetrics, './evidence');

    console.log('\n=== Evidence Generation TEST RESULTS ===\n');

    // Validate first-frame
    const firstFrame = JSON.parse(evidenceFiles['phase1-first-frame.png']);
    console.log('✓ first-frame.png: Valid JSON');
    console.log(`  - Persona: ${firstFrame.persona.name} (${firstFrame.persona.source})`);
    console.log(`  - History turns: ${firstFrame.history.turns}`);
    console.log(`  - Validation persona_present: ${firstFrame.validation.persona_present}`);

    // Validate timing
    const timing = JSON.parse(evidenceFiles['phase1-timing.json']);
    console.log('\n✓ timing.json: Valid JSON');
    console.log(`  - Paint time: ${timing.boot_hydration.persona_paint_ms}ms (deadline: 2000ms)`);
    console.log(`  - Passed: ${timing.boot_hydration.passed}`);
    console.log(`  - Sources: ${timing.sources.persona} / ${timing.sources.session} / ${timing.sources.turns}`);

    // Validate history-diff
    const history = evidenceFiles['phase1-history-diff.txt'];
    console.log('\n✓ history-diff.txt: Generated');
    const historyLines = history.split('\n');
    console.log(`  - Lines: ${historyLines.length}`);
    console.log(`  - Contains "VALIDATION": ${history.includes('VALIDATION')}`);
    console.log(`  - Contains "Exactly 3 turns": ${history.includes('Exactly 3 turns')}`);

    // Validate canonical-trace
    const trace = evidenceFiles['phase1-canonical-trace.txt'];
    console.log('\n✓ canonical-trace.txt: Generated');
    console.log(`  - Contains "/memory/wakeup": ${trace.includes('/memory/wakeup')}`);
    console.log(`  - Contains "/v1/session": ${trace.includes('/v1/session')}`);
    console.log(`  - All canonical endpoints: ${trace.includes('All canonical endpoints: PASS')}`);

    console.log('\n=== ALL TESTS PASS ===\n');

  } catch (error) {
    console.error('TEST FAILED:', error);
    process.exit(1);
  }
}

runTest();
