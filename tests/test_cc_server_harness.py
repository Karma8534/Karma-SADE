import importlib


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
