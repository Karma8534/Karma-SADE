---
source: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-latency
scraped: 2026-03-23
---

# Reducing latency

---

Latency refers to the time it takes for the model to process a prompt and generate an output. Latency can be influenced by various factors, such as the size of the model, the complexity of the prompt, and the underlying infrastructure supporting the model and point of interaction.

> It's always better to first engineer a prompt that works well without model or prompt constraints, and then try latency reduction strategies afterward. Trying to reduce latency prematurely might prevent you from discovering what top performance looks like.

---

## How to measure latency

When discussing latency, you may come across several terms and measurements:

- **Baseline latency**: The time taken by the model to process the prompt and generate the response, without considering the input and output tokens per second. Provides a general idea of the model's speed.
- **Time to first token (TTFT)**: The time it takes for the model to generate the first token of the response, from when the prompt was sent. Particularly relevant when using streaming to provide a responsive experience to users.

---

## How to reduce latency

### 1. Choose the right model

One of the most straightforward ways to reduce latency is to select the appropriate model for your use case. For speed-critical applications, **Claude Haiku 4.5** offers the fastest response times while maintaining high intelligence:

```python
import anthropic

client = anthropic.Anthropic()

# For time-sensitive applications, use Claude Haiku 4.5
message = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Summarize this customer feedback in 2 sentences: [feedback text]",
        }
    ],
)
```

For more details about model metrics, see the [models overview](/docs/en/about-claude/models/overview) page.

### 2. Optimize prompt and output length

Minimize the number of tokens in both your input prompt and the expected output, while still maintaining high performance.

Tips to optimize prompts and outputs:

- **Be clear but concise**: Avoid unnecessary details or redundant information while keeping instructions clear.
- **Ask for shorter responses**: Ask Claude directly to be concise. Claude models have improved steerability.
  - Due to how LLMs count tokens instead of words, asking for an exact word count or a word count limit is not as effective a strategy as asking for paragraph or sentence count limits.
- **Set appropriate output limits**: Use the `max_tokens` parameter to set a hard limit on the maximum length of the generated response.
  - Note: When the response reaches `max_tokens` tokens, the response will be cut off, perhaps midsentence or mid-word. This is a blunt technique that may require post-processing and is usually most appropriate for multiple choice or short answer responses.
- **Experiment with temperature**: Lower values (e.g., 0.2) can sometimes lead to more focused and shorter responses, while higher values (e.g., 0.8) may result in more diverse but potentially longer outputs.

Finding the right balance between prompt clarity, output quality, and token count may require experimentation.

### 3. Leverage streaming

Streaming is a feature that allows the model to start sending back its response before the full output is complete. This can significantly improve the perceived responsiveness of your application, as users can see the model's output in real-time.

With streaming enabled, you can process the model's output as it arrives, updating your user interface or performing other tasks in parallel.

Visit [streaming Messages](/docs/en/build-with-claude/streaming) to learn about how you can implement streaming for your use case.
