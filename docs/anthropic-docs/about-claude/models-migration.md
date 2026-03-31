---
source: https://platform.claude.com/docs/en/about-claude/models/migration-guide
scraped: 2026-03-23
---

# Migration guide

Guide for migrating to Claude 4.6 models from previous Claude versions

---

## Migrating to Claude 4.6

Claude Opus 4.6 is a near drop-in replacement for Claude 4.5, with a few breaking changes to be aware of. For a full list of new features, see [What's new in Claude 4.6](/docs/en/about-claude/models/whats-new-claude-4-6).

### Update your model name

```python
# Opus migration
model = "claude-opus-4-5"  # Before
model = "claude-opus-4-6"  # After
```

### Breaking changes

1. **Prefill removal:** Prefilling assistant messages returns a 400 error on Claude 4.6 models. Use structured outputs, system prompt instructions, or `output_config.format` instead.

2. **Tool parameter quoting:** Claude 4.6 models may produce slightly different JSON string escaping in tool call arguments. If you parse tool call `input` as a raw string rather than using a JSON parser, verify your parsing logic. Standard JSON parsers (like `json.loads()` or `JSON.parse()`) handle these differences automatically.

### Recommended changes

1. **Migrate to adaptive thinking:** `thinking: {type: "enabled", budget_tokens: N}` is deprecated on Claude 4.6 models and will be removed in a future model release. Switch to `thinking: {type: "adaptive"}` and use the effort parameter to control thinking depth.

   ```python
   # Before
   response = client.beta.messages.create(
       model="claude-opus-4-5",
       max_tokens=16000,
       thinking={"type": "enabled", "budget_tokens": 32000},
       betas=["interleaved-thinking-2025-05-14"],
       messages=[...],
   )

   # After
   response = client.messages.create(
       model="claude-opus-4-6",
       max_tokens=16000,
       thinking={"type": "adaptive"},
       output_config={"effort": "high"},
       messages=[{"role": "user", "content": "Your prompt here"}],
   )
   ```

   Note that the migration also moves from `client.beta.messages.create` to `client.messages.create`. Adaptive thinking and effort are GA features and do not require the beta SDK namespace or any beta headers.

2. **Remove effort beta header:** The effort parameter is now GA. Remove `betas=["effort-2025-11-24"]` from your requests.

3. **Remove fine-grained tool streaming beta header:** Fine-grained tool streaming is now GA. Remove `betas=["fine-grained-tool-streaming-2025-05-14"]` from your requests.

4. **Remove interleaved thinking beta header (Opus 4.6 only):** Adaptive thinking automatically enables interleaved thinking on Opus 4.6. Remove `betas=["interleaved-thinking-2025-05-14"]` from your Opus 4.6 requests. Note: Sonnet 4.6 continues to support this beta header with manual extended thinking.

5. **Migrate to output_config.format:** If using structured outputs, update `output_format={...}` to `output_config={"format": {...}}`. The old parameter remains functional but is deprecated and will be removed in a future model release.

### Migrating from Claude 4.1 or earlier to Claude 4.6

If you're migrating from Opus 4.1, Sonnet 4, or earlier models directly to Claude 4.6, apply the Claude 4.6 breaking changes above plus the additional changes in this section.

```python
# From Opus 4.1
model = "claude-opus-4-1-20250805"  # Before
model = "claude-opus-4-6"  # After

# From Sonnet 4
model = "claude-sonnet-4-20250514"  # Before
model = "claude-opus-4-6"  # After

# From Sonnet 3.7
model = "claude-3-7-sonnet-20250219"  # Before
model = "claude-opus-4-6"  # After
```

#### Additional breaking changes

1. **Update sampling parameters** — Use only `temperature` OR `top_p`, not both:

   ```python
   # Before - This will error in Claude 4+ models
   response = client.messages.create(
       model="claude-3-7-sonnet-20250219",
       temperature=0.7,
       top_p=0.9,  # Cannot use both
       # ...
   )

   # After
   response = client.messages.create(
       model="claude-opus-4-6",
       temperature=0.7,  # Use temperature OR top_p, not both
       # ...
   )
   ```

2. **Update tool versions** — Update to the latest tool versions. Remove any code using the `undo_edit` command:

   ```python
   # Before
   tools = [{"type": "text_editor_20250124", "name": "str_replace_editor"}]

   # After
   tools = [{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"}]
   ```

3. **Handle the `refusal` stop reason:**

   ```python
   response = client.messages.create(...)

   if response.stop_reason == "refusal":
       # Handle refusal appropriately
       pass
   ```

4. **Handle the `model_context_window_exceeded` stop reason:**

   ```python
   response = client.messages.create(...)

   if response.stop_reason == "model_context_window_exceeded":
       # Handle context window limit appropriately
       pass
   ```

5. **Verify tool parameter handling (trailing newlines):** Claude 4.5+ models preserve trailing newlines in tool call string parameters that were previously stripped.

6. **Update your prompts for behavioral changes:** Claude 4+ models have a more concise, direct communication style and require explicit direction.

#### Additional recommended changes

- **Remove legacy beta headers:** Remove `token-efficient-tools-2025-02-19` and `output-128k-2025-02-19`. All Claude 4+ models have built-in token-efficient tool use and these headers have no effect.

### Claude 4.6 migration checklist

- [ ] Update model ID to `claude-opus-4-6`
- [ ] **BREAKING:** Remove assistant message prefills (returns 400 error); use structured outputs or `output_config.format` instead
- [ ] **Recommended:** Migrate from `thinking: {type: "enabled", budget_tokens: N}` to `thinking: {type: "adaptive"}` with the effort parameter (`budget_tokens` is deprecated and will be removed in a future release)
- [ ] Verify tool call JSON parsing uses a standard JSON parser
- [ ] Remove `effort-2025-11-24` beta header (effort is now GA)
- [ ] Remove `fine-grained-tool-streaming-2025-05-14` beta header
- [ ] Remove `interleaved-thinking-2025-05-14` beta header (Opus 4.6 only; Sonnet 4.6 still supports it)
- [ ] Migrate `output_format` to `output_config.format` (if applicable)
- [ ] If migrating from Claude 4.1 or earlier: update sampling parameters to use only `temperature` OR `top_p`
- [ ] If migrating from Claude 4.1 or earlier: update tool versions (`text_editor_20250728`, `code_execution_20250825`)
- [ ] If migrating from Claude 4.1 or earlier: handle `refusal` stop reason
- [ ] If migrating from Claude 4.1 or earlier: handle `model_context_window_exceeded` stop reason
- [ ] If migrating from Claude 4.1 or earlier: verify tool string parameter handling for trailing newlines
- [ ] If migrating from Claude 4.1 or earlier: remove legacy beta headers (`token-efficient-tools-2025-02-19`, `output-128k-2025-02-19`)
- [ ] Review and update prompts following prompting best practices
- [ ] Test in development environment before production deployment

---

## Migrating to Claude Sonnet 4.6

Claude Sonnet 4.6 combines strong intelligence with fast performance, featuring improved agentic search capabilities and free code execution when used with web search or web fetch.

> Sonnet 4.6 pricing is $3 per million input tokens, $15 per million output tokens.

**Update your model name:**

```python
# From Sonnet 4.5
model = "claude-sonnet-4-5"  # Before
model = "claude-sonnet-4-6"  # After

# From Sonnet 4
model = "claude-sonnet-4-20250514"  # Before
model = "claude-sonnet-4-6"  # After
```

### Breaking changes (Sonnet 4.6)

1. **Prefilling assistant messages is no longer supported** — Returns a `400` error on Sonnet 4.6. Use structured outputs, system prompt instructions, or `output_config.format` instead.

2. **Tool parameter JSON escaping may differ** — JSON string escaping in tool parameters may differ from previous models. Standard JSON parsers handle this automatically.

3. **Update sampling parameters** (from 3.x) — Use only `temperature` OR `top_p`, not both.

4. **Update tool versions** (from 3.x) — Update to `text_editor_20250728`, `code_execution_20250825`. Remove `undo_edit` command usage.

5. **Handle the `refusal` stop reason** — Update your application to handle refusal stop reasons.

> **Warning:** Sonnet 4.6 defaults to an effort level of `high`, in contrast to Sonnet 4.5 which had no effort parameter. Consider adjusting the effort parameter as you migrate from Sonnet 4.5 to Sonnet 4.6.

### Sonnet 4.6 migration checklist

- [ ] Update model ID to `claude-sonnet-4-6`
- [ ] **BREAKING:** Remove assistant message prefilling; use structured outputs or `output_config.format` instead
- [ ] **BREAKING:** Verify tool parameter JSON parsing handles escaping differences
- [ ] Handle new `refusal` stop reason in your application
- [ ] Remove `fine-grained-tool-streaming-2025-05-14` beta header (now GA)
- [ ] Migrate `output_format` to `output_config.format`
- [ ] Review and update prompts following prompting best practices
- [ ] Consider enabling extended thinking or adaptive thinking for complex reasoning tasks
- [ ] Test in development environment before production deployment

---

## Migrating to Claude Sonnet 4.5

> Sonnet 4.5 pricing is $3 per million input tokens, $15 per million output tokens.

**Update your model name:**

```python
# From Sonnet 4
model = "claude-sonnet-4-20250514"  # Before
model = "claude-sonnet-4-5-20250929"  # After

# From Sonnet 3.7
model = "claude-3-7-sonnet-20250219"  # Before
model = "claude-sonnet-4-5-20250929"  # After
```

### Sonnet 4.5 migration checklist

- [ ] Update model ID to `claude-sonnet-4-5-20250929`
- [ ] **BREAKING:** Update tool versions to latest (if migrating from 3.x)
- [ ] **BREAKING:** Update sampling parameters to use only `temperature` OR `top_p`, not both (if migrating from 3.x)
- [ ] Handle new `refusal` stop reason in your application
- [ ] Consider enabling extended thinking for complex reasoning tasks
- [ ] Test in development environment before production deployment

---

## Migrating to Claude Haiku 4.5

> Haiku 4.5 pricing is $1 per million input tokens, $5 per million output tokens.

**Update your model name:**

```python
# From Haiku 3.5
model = "claude-3-5-haiku-20241022"  # Before
model = "claude-haiku-4-5-20251001"  # After

# From Haiku 3
model = "claude-3-haiku-20240307"  # Before
model = "claude-haiku-4-5-20251001"  # After
```

### Haiku 4.5 migration checklist

- [ ] Update model ID to `claude-haiku-4-5-20251001`
- [ ] **BREAKING:** Update tool versions to latest (`text_editor_20250728`, `code_execution_20250825`)
- [ ] **BREAKING:** Update sampling parameters to use only `temperature` OR `top_p`, not both
- [ ] Handle new `refusal` stop reason in your application
- [ ] Review and adjust for new rate limits (separate from Haiku 3.5)
- [ ] Consider enabling extended thinking for complex reasoning tasks
- [ ] Test in development environment before production deployment

---

## Get help

- Check the [API documentation](/docs/en/api/overview) for detailed specifications
- Review [model capabilities](/docs/en/about-claude/models/overview) for performance comparisons
- Review [API release notes](/docs/en/release-notes/api) for API updates
- Contact support if you encounter any issues during migration
