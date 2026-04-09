const requiredRoot = ['schema_version', 'written_at', 'session'];
const requiredSession = ['session_id', 'workspace_id', 'source'];
const allowedSources = new Set(['browser', 'electron', 'system']);

function isISODateTime(s) {
  return typeof s === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(s) && !Number.isNaN(Date.parse(s));
}

function validateEnvelope(envelope) {
  if (!envelope || typeof envelope !== 'object') return { ok: false, reason: 'envelope-not-object' };
  for (const key of requiredRoot) {
    if (!Object.prototype.hasOwnProperty.call(envelope, key)) return { ok: false, reason: `missing-root-${key}` };
  }
  if (envelope.schema_version !== 'jprop6.v1') return { ok: false, reason: 'schema-version' };
  if (!isISODateTime(envelope.written_at)) return { ok: false, reason: 'written-at-format' };
  if (!envelope.session || typeof envelope.session !== 'object') return { ok: false, reason: 'session-not-object' };
  for (const key of requiredSession) {
    if (!Object.prototype.hasOwnProperty.call(envelope.session, key)) return { ok: false, reason: `missing-session-${key}` };
  }
  if (!allowedSources.has(envelope.session.source)) return { ok: false, reason: 'invalid-source' };
  return { ok: true };
}

function expectFail(envelope, tag) {
  const r = validateEnvelope(envelope);
  if (r.ok) {
    console.error(`FAIL: expected invalid envelope for ${tag}`);
    process.exit(1);
  }
}

const validBase = {
  schema_version: 'jprop6.v1',
  written_at: new Date().toISOString(),
  session: {
    session_id: 'sess-001',
    workspace_id: 'workspace-main',
    source: 'electron',
  },
};

expectFail(
  {
    ...validBase,
    session: {
      workspace_id: 'workspace-main',
      source: 'electron',
    },
  },
  'missing-session-id',
);

expectFail(
  {
    ...validBase,
    schema_version: 'jprop6.v2',
  },
  'invalid-schema-version',
);

expectFail(
  {
    ...validBase,
    written_at: '2026/01/01 00:00:00',
  },
  'invalid-written-at',
);

expectFail(
  {
    ...validBase,
    session: {
      ...validBase.session,
      source: 'daemon',
    },
  },
  'invalid-source',
);

console.log('PASS: break_check');
