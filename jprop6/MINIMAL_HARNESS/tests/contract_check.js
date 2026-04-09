const fs = require('fs');
const path = require('path');

const schemaPath = path.resolve(__dirname, '..', 'session_contract.schema.json');
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));

const sample = {
  schema_version: 'jprop6.v1',
  written_at: new Date().toISOString(),
  session: {
    session_id: 'sess-001',
    workspace_id: 'workspace-main',
    source: 'electron',
    thread_id: 'thread-001',
  },
};

function assert(cond, msg) {
  if (!cond) {
    console.error(`FAIL: ${msg}`);
    process.exit(1);
  }
}

assert(schema.type === 'object', 'schema root must be object');
assert(Array.isArray(schema.required), 'schema required must be array');
for (const key of schema.required) {
  assert(Object.prototype.hasOwnProperty.call(sample, key), `sample missing root key ${key}`);
}
for (const key of schema.properties.session.required) {
  assert(Object.prototype.hasOwnProperty.call(sample.session, key), `sample missing session key ${key}`);
}

console.log('PASS: contract_check');
