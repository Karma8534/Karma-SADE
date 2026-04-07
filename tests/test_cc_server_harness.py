import importlib
import json


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

    assert text == "Final answer: memory read succeeded."
    assert [evt["type"] for evt in seen] == ["assistant", "tool_result", "result"]
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
    assert mod._normalize_local_route("/health") == "/health"
