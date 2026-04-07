from pathlib import Path


def test_electron_renderer_autosaves_memory():
    source = Path("frontend/src/hooks/useKarmaStream.ts").read_text(encoding="utf-8")
    assert "memorySave?: (text: string, title?: string)" in source
    assert "if (assistantText && window.karma?.memorySave)" in source
    assert "Electron Nexus chat:" in source


def test_message_input_listens_for_external_send_event():
    source = Path("frontend/src/components/MessageInput.tsx").read_text(encoding="utf-8")
    assert "window.addEventListener('karma-send-message'" in source
    assert "void sendMessage(detail);" in source


def test_external_send_event_has_readiness_contract():
    message_input = Path("frontend/src/components/MessageInput.tsx").read_text(encoding="utf-8")
    electron_main = Path("electron/main.js").read_text(encoding="utf-8")
    assert "__karmaSendMessageReady" in message_input
    assert "__karmaSendMessageReady" in electron_main
    assert "listenerReady" in electron_main


def test_electron_loads_repo_frontend_export_before_remote_hub():
    source = Path("electron/main.js").read_text(encoding="utf-8")
    assert 'const FRONTEND_DIR = path.join(WORK_DIR, "frontend", "out");' in source


def test_electron_frontend_rewrites_relative_api_calls_under_file_protocol():
    page = Path("frontend/src/app/page.tsx").read_text(encoding="utf-8")
    assert "karma?.isElectron" in page
    assert "window.location.protocol !== 'file:'" in page or "window.location.protocol === 'file:'" in page
    assert "http://127.0.0.1:7891" in page


def test_electron_preload_exposes_hub_token_reader():
    preload = Path("electron/preload.js").read_text(encoding="utf-8")
    main = Path("electron/main.js").read_text(encoding="utf-8")
    assert 'hubToken: () => ipcRenderer.invoke("hub-token")' in preload
    assert 'ipcMain.handle("hub-token"' in main


def test_gate_auto_authenticates_in_electron():
    gate = Path("frontend/src/components/Gate.tsx").read_text(encoding="utf-8")
    assert "karma?.isElectron" in gate
    assert "karma?.hubToken" in gate
    assert "setToken(token.trim())" in gate


def test_next_export_uses_relative_assets_for_electron_file_protocol():
    config = Path("frontend/next.config.js").read_text(encoding="utf-8")
    assert "assetPrefix: './'" in config or 'assetPrefix: "./"' in config


def test_electron_memory_search_normalizes_worker_content_to_results():
    source = Path("electron/main.js").read_text(encoding="utf-8")
    assert "function normalizeMemorySearchPayload" in source
    assert 'payload?.content' in source
    assert 'results: text ? [{ text }] : []' in source


def test_electron_uses_shared_transcript_dir_and_helpers():
    source = Path("electron/main.js").read_text(encoding="utf-8")
    assert 'const TRANSCRIPT_DIR = path.join(WORK_DIR, "tmp", "transcripts");' in source
    assert "function transcriptPath(conversationId)" in source
    assert "function appendTranscriptEntry(conversationId, entry)" in source
    assert "function loadTranscript(conversationId, limit = 100)" in source


def test_electron_cc_chat_loads_prior_transcript_and_persists_turns():
    source = Path("electron/main.js").read_text(encoding="utf-8")
    assert "const priorTranscript = loadTranscript(conversationId, 100);" in source
    assert 'appendTranscriptEntry(conversationId, { role: "user", content: message });' in source
    assert 'appendTranscriptEntry(conversationId, { role: "assistant", content: String(result.result || "").slice(0, 2000) });' in source
    assert "return await runChatCascade(message, { ...opts, priorTranscript }, runId);" in source or "const result = await runChatCascade(message, { ...opts, priorTranscript }, runId);" in source


def test_electron_hardens_windows_crash_path_and_logs_failures():
    source = Path("electron/main.js").read_text(encoding="utf-8")
    assert 'app.disableHardwareAcceleration();' in source
    assert 'const RUNTIME_LOG_FILE = path.join(app.getPath("userData"), "karma_runtime.log");' in source
    assert 'mainWindow.webContents.on("render-process-gone"' in source
    assert 'app.on("child-process-gone"' in source
    assert 'process.on("uncaughtException"' in source
    assert 'process.on("unhandledRejection"' in source
