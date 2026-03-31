---
source: https://platform.claude.com/docs/en/agent-sdk/user-input
scraped: 2026-03-23
section: agent-sdk
---

# Handle approvals and user input

Surface Claude's approval requests and clarifying questions to users, then return their decisions to the SDK.

---

While working on a task, Claude sometimes needs to check in with users. It might need permission before deleting files, or need to ask which database to use for a new project. Your application needs to surface these requests to users so Claude can continue with their input.

Claude requests user input in two situations: when it needs **permission to use a tool** (like deleting files or running commands), and when it has **clarifying questions** (via the `AskUserQuestion` tool). Both trigger your `canUseTool` callback, which pauses execution until you return a response.

## Detect when Claude needs input

Pass a `canUseTool` callback in your query options:

```python Python
async def handle_tool_request(tool_name, input_data, context):
    ...

options = ClaudeAgentOptions(can_use_tool=handle_tool_request)
```

```typescript TypeScript
async function handleToolRequest(toolName, input) {
  ...
}

const options = { canUseTool: handleToolRequest };
```

The callback fires in two cases:

1. **Tool needs approval**: Claude wants to use a tool that isn't auto-approved. Check `tool_name` for the tool (e.g., `"Bash"`, `"Write"`).
2. **Claude asks a question**: Claude calls the `AskUserQuestion` tool. Check if `tool_name == "AskUserQuestion"`.

> **Note:** In Python, `can_use_tool` requires streaming mode and a `PreToolUse` hook that returns `{"continue_": True}` to keep the stream open.

## Handle tool approval requests

Your callback receives:

| Argument | Description |
|----------|-------------|
| `toolName` | The name of the tool Claude wants to use |
| `input` | The parameters Claude is passing to the tool |

### Respond to tool requests

Your callback returns one of two response types:

| Response | Python | TypeScript |
|----------|--------|------------|
| **Allow** | `PermissionResultAllow(updated_input=...)` | `{ behavior: "allow", updatedInput }` |
| **Deny** | `PermissionResultDeny(message=...)` | `{ behavior: "deny", message }` |

```python Python
from claude_agent_sdk.types import PermissionResultAllow, PermissionResultDeny

# Allow the tool to execute
return PermissionResultAllow(updated_input=input_data)

# Block the tool
return PermissionResultDeny(message="User rejected this action")
```

```typescript TypeScript
// Allow the tool to execute
return { behavior: "allow", updatedInput: input };

// Block the tool
return { behavior: "deny", message: "User rejected this action" };
```

## Handle clarifying questions

When Claude needs more direction on a task, it calls the `AskUserQuestion` tool. This triggers your `canUseTool` callback with `toolName` set to `AskUserQuestion`.

### Steps to handle clarifying questions

1. **Pass a `canUseTool` callback** and include `AskUserQuestion` in your tools array if you use an explicit tools list
2. **Detect `AskUserQuestion`** in your callback by checking `toolName === "AskUserQuestion"`
3. **Parse the question input** - the input contains a `questions` array
4. **Collect answers from the user** - present the questions
5. **Return answers to Claude** - build the `answers` object

### Question format

```json
{
  "questions": [
    {
      "question": "How should I format the output?",
      "header": "Format",
      "options": [
        { "label": "Summary", "description": "Brief overview" },
        { "label": "Detailed", "description": "Full explanation" }
      ],
      "multiSelect": false
    }
  ]
}
```

### Response format

```python Python
return PermissionResultAllow(
    updated_input={
        "questions": input_data.get("questions", []),
        "answers": {
            "How should I format the output?": "Summary",
        },
    }
)
```

```typescript TypeScript
return {
  behavior: "allow",
  updatedInput: {
    questions: input.questions,
    answers: {
      "How should I format the output?": "Summary"
    }
  }
};
```

### Complete example

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";
import * as readline from "readline/promises";

async function prompt(question: string): Promise<string> {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const answer = await rl.question(question);
  rl.close();
  return answer;
}

function parseResponse(response: string, options: any[]): string {
  const indices = response.split(",").map((s) => parseInt(s.trim()) - 1);
  const labels = indices
    .filter((i) => !isNaN(i) && i >= 0 && i < options.length)
    .map((i) => options[i].label);
  return labels.length > 0 ? labels.join(", ") : response;
}

async function handleAskUserQuestion(input: any) {
  const answers: Record<string, string> = {};

  for (const q of input.questions) {
    console.log(`\n${q.header}: ${q.question}`);
    q.options.forEach((opt: any, i: number) => {
      console.log(`  ${i + 1}. ${opt.label} - ${opt.description}`);
    });

    const response = (await prompt("Your choice: ")).trim();
    answers[q.question] = parseResponse(response, q.options);
  }

  return {
    behavior: "allow",
    updatedInput: { questions: input.questions, answers }
  };
}

for await (const message of query({
  prompt: "Help me decide on the tech stack for a new mobile app",
  options: {
    canUseTool: async (toolName, input) => {
      if (toolName === "AskUserQuestion") {
        return handleAskUserQuestion(input);
      }
      return { behavior: "allow", updatedInput: input };
    }
  }
})) {
  if ("result" in message) console.log(message.result);
}
```

## Limitations

- **Subagents**: `AskUserQuestion` is not currently available in subagents spawned via the Agent tool
- **Question limits**: each `AskUserQuestion` call supports 1-4 questions with 2-4 options each

## Related resources

- [Configure permissions](/docs/en/agent-sdk/permissions): set up permission modes and rules
- [Control execution with hooks](/docs/en/agent-sdk/hooks): run custom code at key points in the agent lifecycle
