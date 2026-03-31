---
source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool
scraped: 2026-03-23
section: agents-and-tools
---

# Computer use tool

Claude can interact with computer environments through the computer use tool, which provides screenshot capabilities and mouse/keyboard control for autonomous desktop interaction.

> Computer use is in beta and requires a beta header:
> - `"computer-use-2025-11-24"` for Claude Opus 4.6, Claude Sonnet 4.6, Claude Opus 4.5
> - `"computer-use-2025-01-24"` for Sonnet 4.5, Haiku 4.5, Opus 4.1, Sonnet 4, Opus 4, and Sonnet 3.7 (deprecated)
>
> This feature is in beta and is **not** eligible for Zero Data Retention (ZDR).

## Overview

Computer use is a beta feature that enables Claude to interact with desktop environments. This tool provides:

- **Screenshot capture**: See what's currently displayed on screen
- **Mouse control**: Click, drag, and move the cursor
- **Keyboard input**: Type text and use keyboard shortcuts
- **Desktop automation**: Interact with any application or interface

## Model compatibility

| Model | Tool Version | Beta Flag |
|-------|--------------|-----------|
| Claude Opus 4.6, Claude Sonnet 4.6, Claude Opus 4.5 | `computer_20251124` | `computer-use-2025-11-24` |
| All other supported models | `computer_20250124` | `computer-use-2025-01-24` |

> Claude Opus 4.6, Claude Sonnet 4.6, and Claude Opus 4.5 introduce the `computer_20251124` tool version with new capabilities including the zoom action for detailed screen region inspection.

> Older tool versions are not guaranteed to be backwards-compatible with newer models.

## Security considerations

> To minimize risks, consider taking precautions such as:
>
> 1. Using a dedicated virtual machine or container with minimal privileges
> 2. Avoiding giving the model access to sensitive data
> 3. Limiting internet access to an allowlist of domains
> 4. Asking a human to confirm decisions that may result in meaningful real-world consequences

In some circumstances, Claude will follow commands found in content even if it conflicts with the user's instructions. The model has been trained to resist prompt injections, and an extra layer of defense has been added with classifiers that automatically run on prompts to flag potential instances of prompt injections.

Inform end users of relevant risks and obtain their consent prior to enabling computer use in your own products.

## Quick start

```bash Shell
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: computer-use-2025-11-24" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "tools": [
      {
        "type": "computer_20251124",
        "name": "computer",
        "display_width_px": 1024,
        "display_height_px": 768,
        "display_number": 1
      },
      {
        "type": "text_editor_20250728",
        "name": "str_replace_based_edit_tool"
      },
      {
        "type": "bash_20250124",
        "name": "bash"
      }
    ],
    "messages": [
      {
        "role": "user",
        "content": "Save a picture of a cat to my desktop."
      }
    ]
  }'
```

```python Python
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[
        {
            "type": "computer_20251124",
            "name": "computer",
            "display_width_px": 1024,
            "display_height_px": 768,
            "display_number": 1,
        },
        {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool"},
        {"type": "bash_20250124", "name": "bash"},
    ],
    messages=[{"role": "user", "content": "Save a picture of a cat to my desktop."}],
    betas=["computer-use-2025-11-24"],
)
print(response)
```

```typescript TypeScript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const response = await client.beta.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  tools: [
    {
      type: "computer_20251124",
      name: "computer",
      display_width_px: 1024,
      display_height_px: 768,
      display_number: 1
    },
    {
      type: "text_editor_20250728",
      name: "str_replace_based_edit_tool"
    },
    {
      type: "bash_20250124",
      name: "bash"
    }
  ],
  messages: [{ role: "user", content: "Save a picture of a cat to my desktop." }],
  betas: ["computer-use-2025-11-24"]
});

console.log(response);
```

> A beta header is only required for the computer use tool. The example above shows all three tools being used together, which requires the beta header because it includes the computer use tool.

---

## How computer use works

1. **Provide Claude with the computer use tool and a user prompt** — Add the computer use tool (and optionally other tools) to your API request.
2. **Claude decides to use the computer use tool** — Claude assesses if the computer use tool can help with the user's query. The API response has a `stop_reason` of `tool_use`.
3. **Extract tool input, evaluate the tool on a computer, and return results** — On your end, extract the tool name and input from Claude's request, use the tool on a container or Virtual Machine, and continue the conversation with a new `user` message containing a `tool_result` content block.
4. **Continue in an agentic loop** — Claude may use more tool calls as it works through the task.

## Computer use tool parameters

| Parameter | Description |
|-----------|-------------|
| `type` | Tool version (e.g., `computer_20251124`) |
| `name` | Must be `"computer"` |
| `display_width_px` | Width of the display in pixels |
| `display_height_px` | Height of the display in pixels |
| `display_number` | The X display number (for X11 environments) |

## Computer use actions

The computer tool supports these action types:

### `screenshot`
Takes a screenshot of the current display state.

### `left_click`, `right_click`, `double_click`
Mouse click actions at specified coordinates (`coordinate: [x, y]`).

### `left_click_drag`
Drag from one coordinate to another (`start_coordinate`, `coordinate`).

### `type`
Type text at the current cursor position (`text: "string"`).

### `key`
Press keyboard key(s) (`key: "Return"`, `key: "ctrl+c"`).

### `mouse_move`
Move the mouse to a coordinate (`coordinate: [x, y]`).

### `scroll`
Scroll at a coordinate (`coordinate`, `direction: "up"|"down"|"left"|"right"`, `amount`).

### `zoom` (computer_20251124 only)
Zoom in on a specific region for detailed inspection (`coordinate: [x, y]`, `zoom_factor`).

### `cursor_position`
Get the current cursor position.

## Implementing the computer use tool

When implementing computer use, you need to:

1. **Set up a display environment** — Provide a VNC, X11, or similar display environment
2. **Handle screenshot requests** — Capture and return screen images as base64-encoded PNG
3. **Handle action requests** — Execute mouse and keyboard actions
4. **Return results** — Send tool results back in the conversation

Example tool result for a screenshot:
```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": [
        {
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": "image/png",
            "data": "base64_encoded_screenshot_data..."
          }
        }
      ]
    }
  ]
}
```

## Reference implementation

A [reference implementation](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo) is available that includes a web interface, Docker container, example tool implementations, and an agent loop.

## Pricing

The computer use tool adds **683 input tokens** to your API calls, regardless of tool version. Additional tokens are consumed by screenshot images included in the conversation.
