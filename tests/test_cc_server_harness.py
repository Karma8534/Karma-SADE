import importlib
import json
import urllib.error
import urllib.parse


def _load_module():
    return importlib.import_module("Scripts.cc_server_p1")


def test_harness_tool_loop_emits_tool_events(monkeypatch):
    mod = _load_module()
    responses = [
        {
            "text": '{"tool_use":{"name":"read_file","input":{"path":"MEMORY.md","limit":80}}}',
            "lines": [],
            "stderr": "",
        },
        {
            "text": "Final answer: memory read succeeded.",
            "lines": [],
            "stderr": "",
        },
    ]
    monkeypatch.setattr(mod, "_run_cc_attempt", lambda *args, **kwargs: responses.pop(0))

    seen = []
    text, _lines = mod._run_cc_harness(
        "read the first line of MEMORY.md",
        event_sink=lambda evt: seen.append(evt),
    )

    assert isinstance(text, str) and text.strip()
    assert seen and seen[-1]["type"] == "result"
    assert any(evt["type"] == "tool_result" for evt in seen)
    tool_result = next(evt for evt in seen if evt["type"] == "tool_result")
    assert '"ok": true' in tool_result["content"][0]["text"].lower()
    assert "MEMORY.md" in tool_result["content"][0]["text"]


def test_shell_tool_respects_permission_engine():
    mod = _load_module()

    blocked = mod._execute_tool_locally("shell", {"command": "rm -rf /"})
    allowed = mod._execute_tool_locally("read_file", {"path": "MEMORY.md", "limit": 40})

    assert blocked["ok"] is False
    assert "permission engine" in blocked["error"].lower()
    assert allowed["ok"] is True
    assert allowed["content"]


def test_execute_tool_locally_normalizes_namespaced_tool_names():
    mod = _load_module()

    result = mod._execute_tool_locally("nexus:read_file", {"path": "MEMORY.md", "limit": 1})

    assert result["ok"] is True
    assert result["content"]


def test_read_file_limit_is_line_based():
    mod = _load_module()

    result = mod._execute_tool_locally("read_file", {"path": "tmp/forensic-tool-read.txt", "limit": 1})

    assert result["ok"] is True
    assert result["content"].startswith("ZXQ-FORENSIC-LINE-")
    assert "\n" not in result["content"]


def test_write_file_creates_checkpointed_write():
    mod = _load_module()
    target = "tmp/test-write-file.txt"

    first = mod._execute_tool_locally("write_file", {"path": target, "content": "alpha"})
    second = mod._execute_tool_locally("write_file", {"path": target, "content": "beta"})
    reread = mod._execute_tool_locally("read_file", {"path": target, "limit": 1})

    assert first["ok"] is True
    assert second["ok"] is True
    assert second["checkpoint"]
    assert reread["content"] == "beta"


def test_groq_tool_loop_executes_grounded_read(monkeypatch):
    mod = _load_module()
    responses = [
        {
            "model": "llama-3.3-70b-versatile",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "call-1",
                                "type": "function",
                                "function": {
                                    "name": "read_file",
                                    "arguments": '{"path":"MEMORY.md","limit":1}',
                                },
                            }
                        ],
                    }
                }
            ],
        },
        {
            "model": "llama-3.3-70b-versatile",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Final grounded answer",
                    }
                }
            ],
        },
    ]
    monkeypatch.setattr(mod, "_groq_chat", lambda *args, **kwargs: responses.pop(0))

    seen = []
    text, model = mod._groq_fallback(
        "read the first line of MEMORY.md",
        event_sink=lambda evt: seen.append(evt),
    )

    assert text == "Final grounded answer"
    assert model == "llama-3.3-70b-versatile"
    assert [evt["type"] for evt in seen] == ["assistant", "tool_result", "assistant", "result"]


def test_groq_grounded_requests_ignore_recovered_transcript(monkeypatch):
    mod = _load_module()
    captured = {}

    def fake_groq_chat(messages, **kwargs):
        captured["messages"] = messages
        return {
            "model": "llama-3.3-70b-versatile",
            "choices": [{"message": {"role": "assistant", "content": "grounded"}}],
        }

    monkeypatch.setattr(mod, "_groq_chat", fake_groq_chat)

    text, _model = mod._groq_fallback(
        "Read the first line of tmp/forensic-tool-read.txt using a tool.",
        transcript_context="[RECOVERED TRANSCRIPT]\n[ASSISTANT] bogus prior answer",
    )

    assert text == "grounded"
    assert captured["messages"][1]["content"] == "Read the first line of tmp/forensic-tool-read.txt using a tool."


def test_sanitized_subprocess_env_removes_anthropic_keys(monkeypatch):
    mod = _load_module()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "bad-key")
    monkeypatch.setenv("CLAUDE_API_KEY", "bad-key-2")

    env = mod._sanitized_subprocess_env()

    assert "ANTHROPIC_API_KEY" not in env
    assert "CLAUDE_API_KEY" not in env


def test_normalize_memory_save_payload_maps_content_to_text():
    mod = _load_module()

    out = mod._normalize_memory_save_payload({"content": "abc", "title": "t"})

    assert out["text"] == "abc"
    assert out["content"] == "abc"
    assert out["title"] == "t"


def test_normalize_memory_save_payload_preserves_text():
    mod = _load_module()

    out = mod._normalize_memory_save_payload({"content": "abc", "text": "xyz"})

    assert out["text"] == "xyz"


def test_claudemem_status_payload_falls_back_from_api_health(monkeypatch):
    mod = _load_module()
    calls = []

    def fake_proxy(path, method="GET", body=None, timeout=5):
        calls.append(path)
        if path == "/api/health":
            return 404, {"error": "missing"}
        if path == "/health":
            return 200, {"status": "ok"}
        return 500, {"error": "unexpected"}

    monkeypatch.setattr(mod, "claudemem_proxy", fake_proxy)
    code, payload = mod._claudemem_status_payload(timeout=5)

    assert code == 200
    assert payload["status"] == "ok"
    assert calls == ["/api/health", "/health"]


def test_claudemem_status_payload_stops_on_non_404(monkeypatch):
    mod = _load_module()
    calls = []

    def fake_proxy(path, method="GET", body=None, timeout=5):
        calls.append(path)
        return 503, {"error": "down"}

    monkeypatch.setattr(mod, "claudemem_proxy", fake_proxy)
    code, payload = mod._claudemem_status_payload(timeout=5)

    assert code == 503
    assert payload["error"] == "down"
    assert calls == ["/api/health"]


def test_normalize_local_route_maps_memory_save_alias():
    mod = _load_module()

    out = mod._normalize_local_route("/v1/memory/save")

    assert out == "/memory/save"


def test_groq_fallback_skips_tool_schema_for_simple_prompts(monkeypatch):
    mod = _load_module()
    captured = {}

    def fake_groq_chat(messages, tools=None, tool_choice="auto", temperature=0.0, max_tokens=1024):
        captured["tools"] = tools
        return {
            "model": "llama-3.3-70b-versatile",
            "choices": [{"message": {"role": "assistant", "content": "OK"}}],
        }

    monkeypatch.setattr(mod, "_groq_chat", fake_groq_chat)

    text, model = mod._groq_fallback("Answer with only OK.")

    assert text == "OK"
    assert model == "llama-3.3-70b-versatile"
    assert captured["tools"] is None


def test_run_cc_prefers_openrouter_before_groq(monkeypatch):
    mod = _load_module()

    monkeypatch.setattr(mod, "_run_cc_harness", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("claude down")))
    monkeypatch.setattr(mod, "_openrouter_fallback", lambda *args, **kwargs: ("OPENROUTER_OK", "anthropic/claude-sonnet-4.6"))
    monkeypatch.setattr(mod, "_groq_fallback", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("groq should not run")))
    monkeypatch.setattr(mod, "_local_ollama_fallback", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("ollama should not run")))
    monkeypatch.setattr(mod, "_k2_fallback", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("k2 should not run")))

    text = mod.run_cc("Answer with only OK.")

    assert text == "OPENROUTER_OK"


def test_run_cc_falls_back_to_local_ollama_before_k2_when_openrouter_and_groq_fail(monkeypatch):
    mod = _load_module()

    monkeypatch.setattr(mod, "_run_cc_harness", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("claude down")))
    monkeypatch.setattr(mod, "_openrouter_fallback", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("openrouter down")))
    monkeypatch.setattr(mod, "_groq_fallback", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("groq down")))
    monkeypatch.setattr(mod, "_local_ollama_fallback", lambda *args, **kwargs: ("OLLAMA_OK", "sam860/LFM2:350m"))

    text = mod.run_cc("Answer with only OK.")

    assert text == "OLLAMA_OK"


def test_message_needs_grounding_detects_direct_file_targets():
    mod = _load_module()

    assert mod._message_needs_grounding("Create tmp/example.txt with exactly the content alive.")
    assert mod._message_needs_grounding("Write docs/output.md with the final summary.")


def test_select_p1_ollama_model_prefers_stronger_available_model(monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "P1_OLLAMA_MODEL", "")
    monkeypatch.setattr(mod, "_p1_ollama_model_cache", None)
    monkeypatch.setattr(mod, "_list_ollama_models", lambda _url: ["sam860/LFM2:350m", "gemma4:31b-cloud"])

    out = mod._select_p1_ollama_model()

    assert out == "gemma4:31b-cloud"


def test_local_ollama_fallback_executes_tool_loop(monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "_select_p1_ollama_model", lambda: "gemma4:31b-cloud")
    responses = [
        {
            "model": "gemma4:31b",
            "message": {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call-1",
                        "function": {
                            "name": "read_file",
                            "arguments": {"path": "MEMORY.md", "limit": 1},
                        },
                    }
                ],
            },
        },
        {
            "model": "gemma4:31b",
            "message": {"role": "assistant", "content": "# MEMORY"},
        },
    ]
    monkeypatch.setattr(mod, "_ollama_chat", lambda *args, **kwargs: responses.pop(0))

    seen = []
    text, model = mod._local_ollama_fallback(
        "Read the first line of MEMORY.md using a tool and answer with only that line.",
        event_sink=lambda evt: seen.append(evt),
    )

    assert text == "# MEMORY"
    assert model == "gemma4:31b"
    assert [evt["type"] for evt in seen] == ["assistant", "tool_result", "assistant", "result"]


def test_local_ollama_fallback_retries_empty_grounded_turn(monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "_select_p1_ollama_model", lambda: "gemma4:31b-cloud")
    responses = [
        {"model": "gemma4:31b", "message": {"role": "assistant", "content": ""}},
        {"model": "gemma4:31b", "message": {"role": "assistant", "content": "DONE"}},
    ]
    monkeypatch.setattr(mod, "_ollama_chat", lambda *args, **kwargs: responses.pop(0))

    text, model = mod._local_ollama_fallback(
        "Create tmp/example.txt with exactly the content alive and then answer with only DONE."
    )

    assert text == "DONE"
    assert model == "gemma4:31b"


def test_k2_fallback_uses_direct_query_payload_without_global_context(monkeypatch):
    mod = _load_module()
    captured = {}

    class _Resp:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def read(self):
            return json.dumps({"answer": "K2_OK"}).encode()

    def fake_urlopen(req, timeout=0):
        captured["url"] = req.full_url
        captured["timeout"] = timeout
        captured["payload"] = json.loads(req.data.decode())
        return _Resp()

    monkeypatch.setattr(mod, "_compose_harness_message", lambda message, transcript_context="": f"{transcript_context}::{message}")
    monkeypatch.setattr(mod.urllib.request, "urlopen", fake_urlopen)

    text, model = mod._k2_fallback("Answer with only OK.", transcript_context="RECOVERED")

    assert text == "K2_OK"
    assert model == "k2-cortex"
    assert captured["url"].endswith("/query")
    assert captured["timeout"] == mod.K2_QUERY_TIMEOUT
    assert captured["payload"] == {"query": "RECOVERED::Answer with only OK.", "temperature": 0.0}


def test_k2_fallback_retries_once_before_success(monkeypatch):
    mod = _load_module()
    calls = {"count": 0}

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({"answer": "K2_OK"}).encode()

    def fake_urlopen(req, timeout=0):
        calls["count"] += 1
        if calls["count"] == 1:
            raise urllib.error.URLError("temporary timeout")
        return _Resp()

    monkeypatch.setattr(mod.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(mod.time, "sleep", lambda _secs: None)
    monkeypatch.setattr(mod, "K2_QUERY_RETRIES", 2)

    text, model = mod._k2_fallback("Answer with only OK.")

    assert calls["count"] == 2
    assert text == "K2_OK"
    assert model == "k2-cortex"


def test_aaak_encode_truncates_oversized_first_chunk():
    aaak = importlib.import_module("Scripts.aaak")
    giant = "X" * 5000

    out = aaak.aaak_encode([giant], max_chars=1200)

    assert out.startswith("* ")
    assert len(out) <= 1200


def test_recall_queries_skip_global_context_prefix():
    mod = _load_module()
    transcript_context = "[RECOVERED TRANSCRIPT]\n[USER] Remember this exact token: TEST-123.\n[ASSISTANT] Logged."

    combined = mod._contextualize_message(
        "What exact token did I ask you to remember earlier?",
        transcript_context=transcript_context,
    )

    assert combined == transcript_context + "\n\n[USER]\nWhat exact token did I ask you to remember earlier?"


def test_deterministic_transcript_recall_token_and_phrase():
    mod = _load_module()
    transcript = [
        {"role": "user", "content": "Remember this exact token: TOKEN-12345."},
        {"role": "assistant", "content": "stored"},
        {"role": "user", "content": "Remember this exact phrase for restart recovery: sovereign-restart-signal."},
    ]

    token = mod._deterministic_transcript_recall("What exact token did I ask you to remember earlier?", transcript)
    phrase = mod._deterministic_transcript_recall("What exact phrase did I ask you to remember earlier?", transcript)

    assert token == "TOKEN-12345"
    assert phrase == "sovereign-restart-signal"


def test_deterministic_transcript_recall_supports_live_browser_wording():
    mod = _load_module()
    transcript = [
        {"role": "user", "content": "Remember exactly HUBTOK_d44d885a"},
        {"role": "assistant", "content": "Locked. **HUBTOK_d44d885a** — stored in memory."},
    ]

    token = mod._deterministic_transcript_recall(
        "What exact token did I tell you earlier in this conversation? Answer with only the token.",
        transcript,
    )

    assert token == "HUBTOK_d44d885a"


def test_recall_query_without_transcript_stays_inside_conversation_boundary():
    mod = _load_module()

    answer = mod._deterministic_transcript_boundary_answer(
        "What exact token did I ask you to remember earlier?",
        [],
    )

    assert answer == "I do not have anything earlier in this conversation to recall yet."


def test_deterministic_workspace_answer_heading_and_first_line():
    mod = _load_module()

    heading = mod._deterministic_workspace_answer("What exact heading is at the top of MEMORY.md? Answer with only the heading.")
    first_line = mod._deterministic_workspace_answer("Read the first line of tmp/forensic-tool-read.txt using a tool.")

    assert heading == "# Karma SADE — Active Memory"
    assert first_line.startswith("ZXQ-FORENSIC-LINE-")


def test_recovered_transcript_context_stays_out_of_literal_user_message():
    mod = _load_module()
    transcript = [
        {"role": "user", "content": "Remember this exact phrase for restart recovery: sovereign-restart-signal."},
        {"role": "assistant", "content": "Logged. sovereign-restart-signal."},
    ]

    transcript_context = mod._build_recovered_transcript_context(transcript)
    combined = mod._contextualize_message(
        "After restart, what exact phrase did I ask you to remember earlier, and what is the main heading at the top of MEMORY.md?",
        transcript_context=transcript_context,
    )

    assert "[RECOVERED TRANSCRIPT]" in combined
    assert combined.rstrip().endswith(
        "[USER]\nAfter restart, what exact phrase did I ask you to remember earlier, and what is the main heading at the top of MEMORY.md?"
    )


def test_session_registry_keeps_default_and_new_thread_isolated(tmp_path, monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "SESSION_FILE", tmp_path / ".cc_nexus_session_id")
    monkeypatch.setattr(mod, "SESSION_REGISTRY_FILE", tmp_path / ".cc_nexus_session_registry.json")

    mod.save_session_id("sid-default")
    mod.save_session_id("sid-thread-1", "thread-1")

    assert mod.load_session_id() == "sid-default"
    assert mod.load_session_id("thread-1") == "sid-thread-1"
    assert mod.load_session_id("thread-2") is None
    assert json.loads((tmp_path / ".cc_nexus_session_registry.json").read_text()) == {"thread-1": "sid-thread-1"}


def test_build_cc_cmd_uses_conversation_specific_resume_session(tmp_path, monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "SESSION_FILE", tmp_path / ".cc_nexus_session_id")
    monkeypatch.setattr(mod, "SESSION_REGISTRY_FILE", tmp_path / ".cc_nexus_session_registry.json")
    monkeypatch.setattr(mod, "build_context_prefix", lambda message: "")

    mod.save_session_id("sid-default")
    mod.save_session_id("sid-thread-1", "thread-1")

    default_cmd = mod._build_cc_cmd("hello default")
    thread_cmd = mod._build_cc_cmd("hello thread", conversation_id="thread-1")
    fresh_cmd = mod._build_cc_cmd("hello fresh", conversation_id="thread-2")

    assert "--resume" in default_cmd
    assert default_cmd[default_cmd.index("--resume") + 1] == "sid-default"
    assert "--resume" in thread_cmd
    assert thread_cmd[thread_cmd.index("--resume") + 1] == "sid-thread-1"
    assert "--resume" not in fresh_cmd


def test_run_cc_harness_passes_conversation_id_to_cc_attempt(monkeypatch):
    mod = _load_module()
    seen = []

    def fake_run_cc_attempt(*args, **kwargs):
        seen.append(kwargs.get("conversation_id"))
        return {"text": "isolated thread answer", "lines": [], "stderr": ""}

    monkeypatch.setattr(mod, "_run_cc_attempt", fake_run_cc_attempt)

    text, _lines = mod._run_cc_harness("hello", conversation_id="thread-9")

    assert text == "isolated thread answer"
    assert seen == ["thread-9"]


def test_cc_routes_do_not_allow_ollama_preemption():
    mod = _load_module()

    assert mod._should_allow_smartrouter_precheck("/cc") is False
    assert mod._should_allow_smartrouter_precheck("/cc/stream") is False


def test_browser_route_aliases_map_to_local_cc_contract():
    mod = _load_module()

    assert mod._normalize_local_route("/v1/chat") == "/cc"
    assert mod._normalize_local_route("/v1/chat/stream") == "/cc/stream"
    assert mod._normalize_local_route("/v1/file?path=MEMORY.md") == "/file?path=MEMORY.md"
    assert mod._normalize_local_route("/v1/files") == "/files"
    assert mod._normalize_local_route("/v1/agents-status") == "/agents-status"
    assert mod._normalize_local_route("/v1/memory/search") == "/memory/search"
    assert mod._normalize_local_route("/health") == "/health"


def test_release_cc_lock_can_clear_stale_lock_without_active_process():
    mod = _load_module()
    acquired = mod._proc_lock.acquire(blocking=False)
    assert acquired is True
    mod._current_proc = None
    mod._lock_acquired_at = 123

    try:
        assert mod._release_cc_lock(force=True) is True
        assert mod._proc_lock.acquire(blocking=False) is True
        mod._proc_lock.release()
        assert mod._lock_acquired_at == 0
    finally:
        if mod._proc_lock.locked():
            mod._release_cc_lock(force=True)
