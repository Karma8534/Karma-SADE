---
source: https://platform.claude.com/docs/en/about-claude/use-case-guides/content-moderation
scraped: 2026-03-23
---

# Content moderation

Content moderation is a critical aspect of maintaining a safe, respectful, and productive environment in digital applications. This guide discusses how Claude can be used to moderate content within your digital application.

---

> Visit the [content moderation cookbook](https://platform.claude.com/cookbook/misc-building-moderation-filter) to see an example content moderation implementation using Claude.

> This guide is focused on moderating user-generated content within your application. If you're looking for guidance on moderating interactions with Claude, refer to the [guardrails guide](/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations).

## Before building with Claude

### Decide whether to use Claude for content moderation

Key indicators for using Claude instead of traditional ML or rules-based approaches:
- **Cost-effective and rapid implementation**: Claude can have a sophisticated moderation system up and running in a fraction of the time and cost of traditional ML or human moderation
- **Semantic understanding and quick decisions**: Bridges the gap between traditional ML (struggles with context) and human moderation (requires time)
- **Consistent policy decisions**: Claude applies complex moderation guidelines uniformly
- **Moderation policies are likely to change or evolve**: Claude adapts easily without extensive relabeling
- **Interpretable reasoning**: Claude can generate detailed justifications for moderation decisions
- **Multilingual support**: No need for separate models per language
- **Multimodal support**: Claude can analyze both text and images

> **Note:** Anthropic has trained all Claude models to be honest, helpful and harmless. This may result in Claude moderating content deemed particularly dangerous (in line with the Acceptable Use Policy), regardless of the prompt used. Review the AUP before building a moderation solution.

### Generate examples of content to moderate

Create examples of content that should and should not be flagged, including edge cases:

```python
allowed_user_comments = [
    "This movie was great, I really enjoyed it. The main actor really killed it!",
    "I hate Mondays.",
    "It is a great time to invest in gold!",
]

disallowed_user_comments = [
    "Delete this post now or you better hide. I am coming after you and your family.",
    "Stay away from the 5G cellphones!! They are using 5G to control you.",
    "Congratulations! You have won a $1,000 gift card. Click here to claim your prize!",
]

unsafe_categories = [
    "Child Exploitation",
    "Conspiracy Theories",
    "Hate",
    "Indiscriminate Weapons",
    "Intellectual Property",
    "Non-Violent Crimes",
    "Privacy",
    "Self-Harm",
    "Sex Crimes",
    "Sexual Content",
    "Specialized Advice",
    "Violent Crimes",
]
```

The example `"The main actor really killed it!"` requires recognizing "killed it" as a metaphor. The comment `"I am coming after you and your family."` should be flagged despite no explicit violence words.

---

## How to moderate content using Claude

### Select the right Claude model

Cost estimate for 1 billion posts per month moderation:
- **Claude Haiku 3 estimated cost**: ~$2,590/month
- **Claude Opus 4.6 estimated cost**: ~$51,800/month

For large-scale moderation, Claude Haiku 3 is an excellent cost-effective choice.

### Build a strong prompt

```python
import anthropic
import json

client = anthropic.Anthropic()

def moderate_message(message, unsafe_categories):
    unsafe_category_str = "\n".join(unsafe_categories)
    assessment_prompt = f"""
    Determine whether the following message warrants moderation,
    based on the unsafe categories outlined below.

    Message:
    <message>{message}</message>

    Unsafe Categories:
    <categories>
    {unsafe_category_str}
    </categories>

    Respond with ONLY a JSON object, using the format below:
    {{
    "violation": <Boolean field denoting whether the message should be moderated>,
    "categories": [Comma-separated list of violated categories],
    "explanation": [Optional. Only include if there is a violation.]
    }}"""

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=200,
        temperature=0,
        messages=[{"role": "user", "content": assessment_prompt}],
    )
    assessment = json.loads(response.content[0].text)
    contains_violation = assessment["violation"]
    violated_categories = assessment.get("categories", []) if contains_violation else []
    explanation = assessment.get("explanation") if contains_violation else None
    return contains_violation, violated_categories, explanation
```

### Evaluate your prompt

Consider multiple risk levels instead of binary classification:

```python
def assess_risk_level(message, unsafe_categories):
    # ... prompt includes risk level 0-3 ...
    # 0 - No risk, 1 - Low risk, 2 - Medium risk, 3 - High risk
    # Returns: risk_level, violated_categories, explanation
```

This enables flexible content moderation: automatically block high risk, flag medium risk for human review.

### Deploy your prompt

Best practices for production:
1. **Provide clear feedback to users**: Explain why their message was flagged and how to rephrase
2. **Analyze moderated content**: Track types of content being flagged to identify trends
3. **Continuously evaluate and improve**: Regularly assess precision and recall metrics

---

## Improve performance

### Define topics and provide examples

In addition to listing unsafe categories, provide definitions and phrases related to each category:

```python
unsafe_category_definitions = {
    "Child Exploitation": "Content that depicts child nudity or that enables, encourages, excuses, or depicts the sexual abuse of children.",
    "Conspiracy Theories": "Content that promotes or endorses unfounded, false, or misleading theories about events...",
    "Hate": "Content that is hateful toward people on the basis of their protected characteristics...",
    "Specialized Advice": "Content that contains financial, medical, or legal advice. Financial advice includes guidance on investments, stocks, bonds, or any financial planning.",
    # ... etc
}
```

With definitions, comments like `"It's a great time to invest in gold!"` trigger a violation under Specialized Advice.

### Consider batch processing

For scenarios where real-time moderation isn't necessary, moderate messages in batches:

```python
def batch_moderate_messages(messages, unsafe_categories):
    messages_str = "\n".join(
        [f"<message id={idx}>{msg}</message>" for idx, msg in enumerate(messages)]
    )
    # Ask Claude to assess all messages at once
    # Returns: {"violations": [{"id": N, "categories": [...], "explanation": "..."}]}
```

Keep in mind larger batch sizes lower costs but may decrease quality. Experiment to find optimal batch size.
