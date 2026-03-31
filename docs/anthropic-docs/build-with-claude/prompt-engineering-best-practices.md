---
source: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
scraped: 2026-03-23
section: build-with-claude
---

# Prompting best practices

Comprehensive guide to prompt engineering techniques for Claude's latest models, covering clarity, examples, XML structuring, thinking, and agentic systems.

---

This is the single reference for prompt engineering with Claude's latest models, including Claude Opus 4.6, Claude Sonnet 4.6, and Claude Haiku 4.5. It covers foundational techniques, output control, tool use, thinking, and agentic systems.

## General principles

### Be clear and direct

Claude responds well to clear, explicit instructions. Being specific about your desired output can help enhance results. If you want "above and beyond" behavior, explicitly request it rather than relying on the model to infer this from vague prompts.

Think of Claude as a brilliant but new employee who lacks context on your norms and workflows. The more precisely you explain what you want, the better the result.

**Golden rule:** Show your prompt to a colleague with minimal context on the task and ask them to follow it. If they'd be confused, Claude will be too.

- Be specific about the desired output format and constraints.
- Provide instructions as sequential steps using numbered lists or bullet points when the order or completeness of steps matters.

**Less effective:**
```text
Create an analytics dashboard
```

**More effective:**
```text
Create an analytics dashboard. Include as many relevant features and interactions as possible. Go beyond the basics to create a fully-featured implementation.
```

### Add context to improve performance

Providing context or motivation behind your instructions helps Claude better understand your goals and deliver more targeted responses.

**Less effective:**
```text
NEVER use ellipses
```

**More effective:**
```text
Your response will be read aloud by a text-to-speech engine, so never use ellipses since the text-to-speech engine will not know how to pronounce them.
```

### Use examples effectively

Examples are one of the most reliable ways to steer Claude's output format, tone, and structure. A few well-crafted examples (few-shot or multishot prompting) can dramatically improve accuracy and consistency.

When adding examples, make them:
- **Relevant:** Mirror your actual use case closely.
- **Diverse:** Cover edge cases and vary enough that Claude doesn't pick up unintended patterns.
- **Structured:** Wrap examples in `<example>` tags (multiple examples in `<examples>` tags) so Claude can distinguish them from instructions.

Include 3-5 examples for best results.

### Structure prompts with XML tags

XML tags help Claude parse complex prompts unambiguously, especially when your prompt mixes instructions, context, examples, and variable inputs. Wrapping each type of content in its own tag (e.g. `<instructions>`, `<context>`, `<input>`) reduces misinterpretation.

Best practices:
- Use consistent, descriptive tag names across your prompts.
- Nest tags when content has a natural hierarchy (documents inside `<documents>`, each inside `<document index="n">`).

### Give Claude a role

Setting a role in the system prompt focuses Claude's behavior and tone for your use case:

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    system="You are a helpful coding assistant specializing in Python.",
    messages=[
        {"role": "user", "content": "How do I sort a list of dictionaries by key?"}
    ],
)
print(message.content)
```

### Long context prompting

When working with large documents or data-rich inputs (20k+ tokens):

- **Put longform data at the top**: Place your long documents and inputs near the top of your prompt, above your query, instructions, and examples. This can significantly improve performance across all models. Queries at the end can improve response quality by up to 30% in tests, especially with complex, multi-document inputs.

- **Structure document content and metadata with XML tags**: When using multiple documents, wrap each document in `<document>` tags with `<document_content>` and `<source>` subtags for clarity.

```xml
<documents>
  <document index="1">
    <source>annual_report_2023.pdf</source>
    <document_content>
      {{ANNUAL_REPORT}}
    </document_content>
  </document>
  <document index="2">
    <source>competitor_analysis_q2.xlsx</source>
    <document_content>
      {{COMPETITOR_ANALYSIS}}
    </document_content>
  </document>
</documents>

Analyze the annual report and competitor analysis. Identify strategic advantages and recommend Q3 focus areas.
```

- **Ground responses in quotes**: For long document tasks, ask Claude to quote relevant parts of the documents first before carrying out its task.

## Output and formatting

### Communication style and verbosity

Claude's latest models have a more concise and natural communication style compared to previous models:

- **More direct and grounded:** Provides fact-based progress reports rather than self-celebratory updates
- **More conversational:** Slightly more fluent and colloquial, less machine-like
- **Less verbose:** May skip detailed summaries for efficiency unless prompted otherwise

If you prefer more visibility into its reasoning:

```text
After completing a task that involves tool use, provide a quick summary of the work you've done.
```

### Control the format of responses

Effective ways to steer output formatting:

1. **Tell Claude what to do instead of what not to do**
   - Instead of: "Do not use markdown in your response"
   - Try: "Your response should be composed of smoothly flowing prose paragraphs."

2. **Use XML format indicators**
   - Try: "Write the prose sections of your response in `<smoothly_flowing_prose_paragraphs>` tags."

3. **Match your prompt style to the desired output**
   The formatting style used in your prompt may influence Claude's response style.

4. **Use detailed prompts for specific formatting preferences**

```text
<avoid_excessive_markdown_and_bullet_points>
When writing reports, documents, technical explanations, analyses, or any long-form content, write in clear, flowing prose using complete paragraphs and sentences. Use standard paragraph breaks for organization and reserve markdown primarily for `inline code`, code blocks, and simple headings (###). Avoid using **bold** and *italics*.

DO NOT use ordered lists (1. ...) or unordered lists (*) unless you're presenting truly discrete items or the user explicitly requests a list.

Instead of listing items with bullets or numbers, incorporate them naturally into sentences.
</avoid_excessive_markdown_and_bullet_points>
```

### LaTeX output

Claude Opus 4.6 defaults to LaTeX for mathematical expressions. If you prefer plain text:

```text
Format your response in plain text only. Do not use LaTeX, MathJax, or any markup notation such as \( \), $, or \frac{}{}. Write all math expressions using standard text characters (e.g., "/" for division, "*" for multiplication, and "^" for exponents).
```

### Migrating away from prefilled responses

Starting with Claude 4.6 models, prefilled responses on the last assistant turn are no longer supported. Common prefill scenarios and how to migrate:

- **Controlling output formatting**: Use Structured Outputs or simply ask the model to conform to your output structure.
- **Eliminating preambles**: Use direct instructions: "Respond directly without preamble. Do not start with phrases like 'Here is...', 'Based on...', etc."
- **Avoiding bad refusals**: Claude is much better at appropriate refusals now. Clear prompting within the `user` message should be sufficient.
- **Continuations**: Move the continuation to the user message: "Your previous response was interrupted and ended with `[previous_response]`. Continue from where you left off."

## Tool use

### Tool usage

Claude's latest models benefit from explicit direction to use specific tools. For Claude to take action, be more explicit:

**Less effective (Claude will only suggest):**
```text
Can you suggest some changes to improve this function?
```

**More effective (Claude will make the changes):**
```text
Change this function to improve its performance.
```

To make Claude more proactive about taking action by default:

```text
<default_to_action>
By default, implement changes rather than only suggesting them. If the user's intent is unclear, infer the most useful likely action and proceed, using tools to discover any missing details instead of guessing.
</default_to_action>
```

To make Claude more conservative:

```text
<do_not_act_before_instructions>
Do not jump into implementation or change files unless clearly instructed to make changes. When the user's intent is ambiguous, default to providing information, doing research, and providing recommendations rather than taking action.
</do_not_act_before_instructions>
```

### Optimize parallel tool calling

Claude's latest models excel at parallel tool execution. To maximize parallel efficiency:

```text
<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between the tool calls, make all of the independent tool calls in parallel. Prioritize calling tools simultaneously whenever the actions can be done in parallel rather than sequentially.
</use_parallel_tool_calls>
```

## Thinking and reasoning

### Overthinking and excessive thoroughness

Claude Opus 4.6 does significantly more upfront exploration than previous models. If your prompts previously encouraged the model to be more thorough, tune that guidance:

- **Replace blanket defaults with more targeted instructions.**
- **Remove over-prompting.** Tools that undertriggered in previous models are likely to trigger appropriately now.
- **Use effort as a fallback.** If Claude continues to be overly aggressive, use a lower setting for `effort`.

### Leverage thinking & interleaved thinking capabilities

Claude Opus 4.6 uses adaptive thinking (`thinking: {type: "adaptive"}`), where Claude dynamically decides when and how much to think. Claude Sonnet 4.6 supports both adaptive thinking and manual extended thinking with interleaved mode.

You can guide Claude's thinking behavior:

```text
After receiving tool results, carefully reflect on their quality and determine optimal next steps before proceeding. Use your thinking to plan and iterate based on this new information, and then take the best next action.
```

If you are migrating from extended thinking with `budget_tokens`, replace your thinking configuration:

```python
# Before (extended thinking, older models)
client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=64000,
    thinking={"type": "enabled", "budget_tokens": 32000},
    messages=[{"role": "user", "content": "..."}],
)

# After (adaptive thinking)
client.messages.create(
    model="claude-opus-4-6",
    max_tokens=64000,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},  # or max, medium, low
    messages=[{"role": "user", "content": "..."}],
)
```

Tips:
- **Prefer general instructions over prescriptive steps.**
- **Multishot examples work with thinking.** Use `<thinking>` tags inside your few-shot examples to show Claude the reasoning pattern.
- **Ask Claude to self-check.** Append something like "Before you finish, verify your answer against [test criteria]."

## Agentic systems

### Long-horizon reasoning and state tracking

Claude's latest models excel at long-horizon reasoning tasks with exceptional state tracking capabilities. Claude maintains orientation across extended sessions by focusing on incremental progress.

#### Context awareness and multi-window workflows

Claude 4.6 and Claude 4.5 models feature context awareness, enabling the model to track its remaining context window throughout a conversation. If you are using Claude in an agent harness that compacts context or allows saving context to external files:

```text
Your context window will be automatically compacted as it approaches its limit, allowing you to continue working indefinitely from where you left off. Therefore, do not stop tasks early due to token budget concerns. As you approach your token budget limit, save your current progress and state to memory before the context window refreshes. Always be as persistent and autonomous as possible and complete tasks fully.
```

#### Multi-context window workflows

For tasks spanning multiple context windows:

1. **Use a different prompt for the very first context window**: Use the first context window to set up a framework (write tests, create setup scripts), then use future context windows to iterate on a todo-list.
2. **Have the model write tests in a structured format**: Ask Claude to create tests before starting work and keep track of them in a structured format (e.g., `tests.json`).
3. **Set up quality of life tools**: Encourage Claude to create setup scripts to gracefully start servers, run test suites, and linters.
4. **Use git for state tracking**: Git provides a log of what's been done and checkpoints that can be restored.

#### State management best practices

- **Use structured formats for state data**: When tracking structured information (like test results or task status), use JSON or other structured formats
- **Use unstructured text for progress notes**: Freeform progress notes work well for tracking general progress
- **Emphasize incremental progress**: Explicitly ask Claude to keep track of its progress and focus on incremental work

### Balancing autonomy and safety

Without guidance, Claude Opus 4.6 may take actions that are difficult to reverse or affect shared systems. If you want Claude to confirm before taking potentially risky actions:

```text
Consider the reversibility and potential impact of your actions. You are encouraged to take local, reversible actions like editing files or running tests, but for actions that are hard to reverse, affect shared systems, or could be destructive, ask the user before proceeding.

Examples of actions that warrant confirmation:
- Destructive operations: deleting files or branches, dropping database tables, rm -rf
- Hard to reverse operations: git push --force, git reset --hard, amending published commits
- Operations visible to others: pushing code, commenting on PRs/issues, sending messages, modifying shared infrastructure
```

### Research and information gathering

For optimal research results:

```text
Search for this information in a structured way. As you gather data, develop several competing hypotheses. Track your confidence levels in your progress notes to improve calibration. Regularly self-critique your approach and plan. Break down this complex research task systematically.
```

### Subagent orchestration

Claude's latest models demonstrate significantly improved native subagent orchestration capabilities. If you're seeing excessive subagent use:

```text
Use subagents when tasks can run in parallel, require isolated context, or involve independent workstreams that don't need to share state. For simple tasks, sequential operations, single-file edits, or tasks where you need to maintain context across steps, work directly rather than delegating.
```

### Reduce file creation in agentic coding

If you'd prefer to minimize net new file creation:

```text
If you create any temporary new files, scripts, or helper files for iteration, clean up these files by removing them at the end of the task.
```

### Overeagerness

Claude Opus 4.5 and Claude Opus 4.6 have a tendency to overengineer by creating extra files, adding unnecessary abstractions, or building in flexibility that wasn't requested:

```text
Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused. Don't add features, refactor code, or make "improvements" beyond what was asked. Don't create helpers, utilities, or abstractions for one-time operations.
```

### Avoid focusing on passing tests and hard-coding

```text
Please write a high-quality, general-purpose solution using the standard tools available. Do not create helper scripts or workarounds to accomplish the task more efficiently. Implement a solution that works correctly for all valid inputs, not just the test cases. Do not hard-code values or create solutions that only work for specific test inputs.
```

### Minimizing hallucinations in agentic coding

```text
<investigate_before_answering>
Never speculate about code you have not opened. If the user references a specific file, you MUST read the file before answering. Make sure to investigate and read relevant files BEFORE answering questions about the codebase. Never make any claims about code before investigating unless you are certain of the correct answer.
</investigate_before_answering>
```

## Capability-specific tips

### Improved vision capabilities

Claude Opus 4.5 and Claude Opus 4.6 have improved vision capabilities compared to previous models. One technique that has proven effective is to give Claude a crop tool, enabling it to "zoom" in on relevant regions of an image.

### Frontend design

Claude Opus 4.5 and Claude Opus 4.6 excel at building complex, real-world web applications. To create distinctive, creative frontends:

```text
<frontend_aesthetics>
You tend to converge toward generic, "on distribution" outputs. In frontend design, this creates what users call the "AI slop" aesthetic. Avoid this: make creative, distinctive frontends that surprise and delight.

Focus on:
- Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter.
- Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency.
- Motion: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML.
- Backgrounds: Create atmosphere and depth rather than defaulting to solid colors.

Avoid generic AI-generated aesthetics: overused font families (Inter, Roboto, Arial), clichéd color schemes (particularly purple gradients on white backgrounds), predictable layouts.
</frontend_aesthetics>
```

## Migration considerations

When migrating to Claude 4.6 models from earlier generations:

1. **Be specific about desired behavior**: Describe exactly what you'd like to see in the output.
2. **Frame your instructions with modifiers**: Adding modifiers that encourage Claude to increase the quality and detail of its output can help better shape Claude's performance.
3. **Request specific features explicitly**: Animations and interactive elements should be requested explicitly when desired.
4. **Update thinking configuration**: Claude 4.6 models use adaptive thinking (`thinking: {type: "adaptive"}`) instead of manual thinking with `budget_tokens`. Use the effort parameter to control thinking depth.
5. **Migrate away from prefilled responses**: Prefilled responses on the last assistant turn are deprecated starting with Claude 4.6 models.
6. **Tune anti-laziness prompting**: If your prompts previously encouraged the model to be more thorough or use tools more aggressively, dial back that guidance.

### Migrating from Claude Sonnet 4.5 to Claude Sonnet 4.6

Claude Sonnet 4.6 defaults to an effort level of `high`, in contrast to Claude Sonnet 4.5 which had no effort parameter.

**Recommended effort settings:**
- **Medium** for most applications
- **Low** for high-volume or latency-sensitive workloads
- Set a large max output token budget (64k tokens recommended) at medium or high effort

#### If you're not using extended thinking

```python
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=8192,
    thinking={"type": "disabled"},
    output_config={"effort": "low"},
    messages=[{"role": "user", "content": "..."}],
)
```

#### If you're using extended thinking

```python
# For coding use cases (agentic coding, tool-heavy workflows, code generation)
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16384,
    thinking={"type": "enabled", "budget_tokens": 16384},
    output_config={"effort": "medium"},
    messages=[{"role": "user", "content": "..."}],
)

# For chat and non-coding use cases
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 16384},
    output_config={"effort": "low"},
    messages=[{"role": "user", "content": "..."}],
)
```

#### When to try adaptive thinking

Consider adaptive thinking for:
- **Autonomous multi-step agents:** coding agents, data analysis pipelines, bug finding where the model runs independently across many steps.
- **Computer use agents:** Claude Sonnet 4.6 achieved best-in-class accuracy on computer use evaluations using adaptive mode.
- **Bimodal workloads:** a mix of easy and hard tasks where adaptive skips thinking on simple queries and reasons deeply on complex ones.

```python
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=64000,
    thinking={"type": "adaptive"},
    output_config={"effort": "high"},
    messages=[{"role": "user", "content": "..."}],
)
```
