    // ─── POST /v1/shell ──────────────────────────────────────────────
    if (req.method === "POST" && req.url === "/v1/shell") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }

      const raw = await parseBody(req, 10000);
      let body;
      try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }

      const { command } = body;
      if (!command || typeof command !== 'string') {
        return json(res, 400, { ok: false, error: "command required (string)" });
      }

      // TODO: Validate against whitelist
      // TODO: Execute command via child_process
      // TODO: Capture stdout/stderr
      // TODO: Log to audit trail
      // TODO: Return { ok: true, stdout: '...', stderr: '...', exitCode: N }

      return json(res, 200, { ok: true, message: 'Endpoint ready', todo: 'implement execution' });
    }

