const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const required = [
  'package.json',
  'main.js',
  'preload.js',
  'renderer/fallback.html',
  'session_contract.schema.json',
  'tests/contract_check.js',
];

function fail(msg) {
  console.error(`FAIL: ${msg}`);
  process.exit(1);
}

for (const rel of required) {
  const abs = path.join(root, rel);
  if (!fs.existsSync(abs)) fail(`missing required file ${rel}`);
}

const main = fs.readFileSync(path.join(root, 'main.js'), 'utf8');
if (!main.includes('loadURL(HUB_URL)')) fail('main.js does not load HUB_URL');
if (main.includes('nodeIntegration: true')) fail('nodeIntegration must remain false');
if (main.includes('ipcMain.handle(\'shell')) fail('shell capabilities are forbidden in minimal scaffold');

const preload = fs.readFileSync(path.join(root, 'preload.js'), 'utf8');
if (!preload.includes('contextBridge.exposeInMainWorld')) fail('preload bridge missing');

const schema = JSON.parse(fs.readFileSync(path.join(root, 'session_contract.schema.json'), 'utf8'));
if (!schema.required || !schema.required.includes('session')) fail('session schema missing required fields');

console.log('PASS: proof_check');
