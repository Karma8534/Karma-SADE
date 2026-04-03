// Karma Nexus VS Code Extension
// Connects editor to hub.arknexus.net for context capture and AI assistance

const vscode = require('vscode');
const https = require('https');
const http = require('http');

let statusBarItem;
let hubHealthy = false;

function activate(context) {
    console.log('[karma-nexus] Activating...');

    // Status bar item — shows Karma connection status
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'karma.showStatus';
    statusBarItem.text = '$(pulse) KARMA';
    statusBarItem.tooltip = 'Karma Nexus — click for status';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('karma.askKarma', askKarma),
        vscode.commands.registerCommand('karma.captureContext', captureContext),
        vscode.commands.registerCommand('karma.showStatus', showStatus),
        vscode.commands.registerCommand('karma.openHub', openHub),
    );

    // Auto-connect on startup
    const config = vscode.workspace.getConfiguration('karma');
    if (config.get('autoConnect')) {
        checkHubHealth();
        // Refresh every 30 seconds
        const interval = setInterval(checkHubHealth, 30000);
        context.subscriptions.push({ dispose: () => clearInterval(interval) });
    }
}

function getConfig() {
    const config = vscode.workspace.getConfiguration('karma');
    return {
        hubUrl: config.get('hubUrl') || 'https://hub.arknexus.net',
        token: config.get('token') || '',
    };
}

async function hubFetch(path, options = {}) {
    const { hubUrl, token } = getConfig();
    const url = new URL(path, hubUrl);
    const mod = url.protocol === 'https:' ? https : http;

    return new Promise((resolve, reject) => {
        const headers = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const req = mod.request(url, {
            method: options.method || 'GET',
            headers,
            timeout: 10000,
        }, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(data)); }
                catch { resolve({ ok: false, raw: data }); }
            });
        });
        req.on('error', reject);
        req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
        if (options.body) req.write(JSON.stringify(options.body));
        req.end();
    });
}

async function checkHubHealth() {
    try {
        const res = await hubFetch('/health');
        hubHealthy = res.ok === true;
        statusBarItem.text = hubHealthy ? '$(check) KARMA' : '$(warning) KARMA';
        statusBarItem.backgroundColor = hubHealthy ? undefined : new vscode.ThemeColor('statusBarItem.warningBackground');
    } catch {
        hubHealthy = false;
        statusBarItem.text = '$(error) KARMA';
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    }
}

async function askKarma() {
    const query = await vscode.window.showInputBox({
        prompt: 'Ask Karma anything',
        placeHolder: 'What should I work on next?',
    });
    if (!query) return;

    const editor = vscode.window.activeTextEditor;
    let context = query;
    if (editor) {
        const selection = editor.document.getText(editor.selection);
        if (selection) {
            context = `[Selected code from ${editor.document.fileName}]\n${selection}\n\n${query}`;
        }
    }

    try {
        vscode.window.withProgress({ location: vscode.ProgressLocation.Notification, title: 'Asking Karma...' }, async () => {
            const res = await hubFetch('/v1/chat', {
                method: 'POST',
                body: { message: context, stream: false },
            });
            const answer = res.assistant_text || res.response || JSON.stringify(res);
            const doc = await vscode.workspace.openTextDocument({ content: `# Karma Response\n\n${answer}`, language: 'markdown' });
            vscode.window.showTextDocument(doc, { preview: true });
        });
    } catch (e) {
        vscode.window.showErrorMessage(`Karma error: ${e.message}`);
    }
}

async function captureContext() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('No active editor');
        return;
    }

    const selection = editor.document.getText(editor.selection);
    const fileName = editor.document.fileName;
    const content = selection || editor.document.getText().slice(0, 2000);

    try {
        await hubFetch('/v1/ambient', {
            method: 'POST',
            body: {
                type: 'log',
                content: `[IDE Capture] ${fileName}\n${content}`,
                tags: ['ide-capture', 'vscode'],
                source: 'karma-nexus-vscode',
            },
        });
        vscode.window.showInformationMessage(`Captured to Karma: ${fileName.split(/[/\\]/).pop()}`);
    } catch (e) {
        vscode.window.showErrorMessage(`Capture failed: ${e.message}`);
    }
}

async function showStatus() {
    try {
        const health = await hubFetch('/health');
        const status = await hubFetch('/v1/status');
        const msg = [
            `Hub: ${health.ok ? 'Online' : 'Offline'}`,
            `P1: ${status.harness?.p1?.healthy ? 'Up' : 'Down'}`,
            `K2: ${status.harness?.k2?.healthy ? 'Up' : 'Down'}`,
        ].join(' | ');
        vscode.window.showInformationMessage(`Karma Nexus — ${msg}`);
    } catch (e) {
        vscode.window.showErrorMessage(`Status check failed: ${e.message}`);
    }
}

function openHub() {
    const { hubUrl } = getConfig();
    vscode.env.openExternal(vscode.Uri.parse(hubUrl));
}

function deactivate() {
    console.log('[karma-nexus] Deactivated');
}

module.exports = { activate, deactivate };
