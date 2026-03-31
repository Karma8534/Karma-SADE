---
source: https://platform.claude.com/docs/en/test-and-evaluate/eval-tool
scraped: 2026-03-23
---

# Using the Evaluation Tool

The [Claude Console](/dashboard) features an **Evaluation tool** that allows you to test your prompts under various scenarios.

---

## Accessing the Evaluate Feature

To get started with the Evaluation tool:

1. Open the Claude Console and navigate to the prompt editor.
2. After composing your prompt, look for the 'Evaluate' tab at the top of the screen.

> Ensure your prompt includes at least 1-2 dynamic variables using the double brace syntax: `{{variable}}`. This is required for creating eval test sets.

## Generating Prompts

The Console offers a built-in prompt generator powered by Claude Opus 4.1:

1. **Click 'Generate Prompt'** — This opens a modal that allows you to enter your task information.
2. **Describe your task** — Describe your desired task (e.g., "Triage inbound customer support requests") with as much or as little detail as you desire.
3. **Generate your prompt** — Click the orange 'Generate Prompt' button to have Claude generate a high quality prompt for you.

This feature makes it easier to create prompts with the appropriate variable syntax for evaluation.

## Creating Test Cases

When you access the Evaluation screen, you have several options to create test cases:

1. Click the '+ Add Row' button at the bottom left to manually add a case.
2. Use the 'Generate Test Case' feature to have Claude automatically generate test cases.
3. Import test cases from a CSV file.

To use the 'Generate Test Case' feature:

1. **Click on 'Generate Test Case'** — Claude will generate test cases one row at a time.
2. **Edit generation logic (optional)** — Click the arrow dropdown to the right of the 'Generate Test Case' button, then 'Show generation logic'. Editing this allows you to customize and fine-tune the test cases Claude generates.

> If you update your original prompt text, you can re-run the entire eval suite against the new prompt to see how changes affect performance across all test cases.

## Tips for Effective Evaluation

### Prompt Structure for Evaluation

To make the most of the Evaluation tool, structure your prompts with clear input and output formats. For example:

```text
In this task, you will generate a cute one sentence story that incorporates two elements: a color and a sound.
The color to include in the story is:
<color>
{{COLOR}}
</color>
The sound to include in the story is:
<sound>
{{SOUND}}
</sound>
Here are the steps to generate the story:
1. Think of an object, animal, or scene that is commonly associated with the color provided.
2. Imagine a simple action, event or scene involving the colored object/animal/scene and the sound provided.
3. Describe the action, event or scene in a single, concise sentence.
Please keep your story to one sentence only.
Write your completed one sentence story inside <story> tags.
```

This structure makes it easy to vary inputs (`{{COLOR}}` and `{{SOUND}}`) and evaluate outputs consistently.

> Use the 'Generate a prompt' helper tool in the Console to quickly create prompts with the appropriate variable syntax for evaluation.

## Understanding and comparing results

The Evaluation tool offers several features to help you refine your prompts:

1. **Side-by-side comparison**: Compare the outputs of two or more prompts to quickly see the impact of your changes.
2. **Quality grading**: Grade response quality on a 5-point scale to track improvements in response quality per prompt.
3. **Prompt versioning**: Create new versions of your prompt and re-run the test suite to quickly iterate and improve results.

By reviewing results across test cases and comparing different prompt versions, you can spot patterns and make informed adjustments to your prompt more efficiently.

Start evaluating your prompts today to build more robust AI applications with Claude!
