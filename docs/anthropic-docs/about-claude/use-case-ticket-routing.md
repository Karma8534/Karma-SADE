---
source: https://platform.claude.com/docs/en/about-claude/use-case-guides/ticket-routing
scraped: 2026-03-23
---

# Ticket routing

This guide walks through how to harness Claude's advanced natural language understanding capabilities to classify customer support tickets at scale based on customer intent, urgency, prioritization, customer profile, and more.

---

## Define whether to use Claude for ticket routing

Key indicators that you should use an LLM like Claude instead of traditional ML approaches:

- **Limited labeled training data available**: Claude's pre-trained model can effectively classify tickets with just a few dozen labeled examples.
- **Classification categories are likely to change or evolve over time**: Claude can easily adapt to changes in class definitions or new classes without extensive relabeling.
- **You need to handle complex, unstructured text inputs**: Claude's advanced language understanding allows for accurate classification based on content and context.
- **Classification rules are based on semantic understanding**: Claude excels at understanding and applying underlying rules when classes are defined by conditions rather than examples.
- **You require interpretable reasoning for classification decisions**: Claude can provide human-readable explanations for its classification decisions.
- **You want to handle edge cases and ambiguous tickets more effectively**: Claude's NLP capabilities allow it to better interpret context and nuance.
- **You need multilingual support without maintaining separate models**: Claude's multilingual capabilities allow it to classify tickets in various languages.

---

## Build and deploy your LLM support workflow

### Understand your current support approach

Before diving into automation, investigate your existing ticketing system:
- What criteria determine SLA/service offering applied?
- Is ticket routing used to determine which tier of support a ticket goes to?
- Are there automated rules or workflows already in place? Where do they fail?
- How are edge cases or ambiguous tickets handled?
- How does the team prioritize tickets?

### Define user intent categories

A well-defined list of user intent categories is crucial for accurate classification. Example categories:

- Technical issue (hardware, software, compatibility, performance)
- Account management (password reset, account access, billing, subscription)
- Product information (feature inquiries, compatibility, pricing, availability)
- User guidance (how-to, feature usage, best practices, troubleshooting)
- Feedback (bug reports, feature requests, complaints)
- Order-related (order status, shipping, returns, modifications)
- Service request (installation, upgrades, maintenance, cancellation)
- Security concerns (data privacy, suspicious activity)
- Emergency support (critical system failures, urgent security issues)

### Establish success criteria

Standard criteria and benchmarks for ticket routing:

- **Classification consistency**: Periodically test with standardized inputs; aim for 95%+ consistency rate
- **Routing accuracy**: Correctly assign tickets on first try; aim for 90-95% accuracy
- **Time-to-assignment**: Faster assignment = quicker resolutions; aim for under 5 minutes
- **Rerouting rate**: Lower = better initial routing; aim below 10%
- **First-contact resolution rate**: Industry benchmarks 70-75%, top performers 80%+
- **Customer satisfaction scores**: Aim for CSAT 90%+, top performers 95%+

### Choose the right Claude model

Many customers have found `claude-haiku-4-5-20251001` ideal for ticket routing — fastest and most cost-effective. For deep subject matter expertise or large volume of intent categories, consider Sonnet.

### Build a strong prompt

Ticket routing is a classification task. Here's an example prompt:

```python
def classify_support_request(ticket_contents):
    classification_prompt = f"""You will be acting as a customer support ticket classification system. Your task is to analyze customer support requests and output the appropriate classification intent for each request, along with your reasoning.

        Here is the customer support request you need to classify:

        <request>{ticket_contents}</request>

        Please carefully analyze the above request to determine the customer's core intent and needs. Consider what the customer is asking for or has concerns about.

        First, write out your reasoning and analysis of how to classify this request inside <reasoning> tags.

        Then, output the appropriate classification label for the request inside a <intent> tag. The valid intents are:
        <intents>
        <intent>Support, Feedback, Complaint</intent>
        <intent>Order Tracking</intent>
        <intent>Refund/Exchange</intent>
        </intents>

        A request may have ONLY ONE applicable intent. Only include the intent that is most applicable to the request.
        """
```

Key components:
- Use f-strings to insert `ticket_contents` into `<request>` tags
- Give Claude a clearly defined role as a classification system
- Instruct Claude on proper output formatting with `<reasoning>` and `<intent>` XML tags
- Specify valid intent categories
- Include few-shot examples to improve accuracy

### Deploy your prompt

```python
import anthropic
import re

client = anthropic.Anthropic()
DEFAULT_MODEL = "claude-haiku-4-5-20251001"

def classify_support_request(ticket_contents):
    # ... classification_prompt as above ...
    message = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=500,
        temperature=0,
        messages=[{"role": "user", "content": classification_prompt}],
        stream=False,
    )
    reasoning_and_intent = message.content[0].text

    reasoning_match = re.search(r"<reasoning>(.*?)</reasoning>", reasoning_and_intent, re.DOTALL)
    reasoning = reasoning_match.group(1).strip() if reasoning_match else ""

    intent_match = re.search(r"<intent>(.*?)</intent>", reasoning_and_intent, re.DOTALL)
    intent = intent_match.group(1).strip() if intent_match else ""

    return reasoning, intent
```

Set `stream=False` since we need complete reasoning and intent text before parsing.

---

## Evaluate your prompt

### Build an evaluation function

Measure performance on three key metrics:
- Accuracy
- Cost per classification

```python
def classify_support_request(request, actual_intent):
    # ... (classification prompt) ...
    message = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=500,
        temperature=0,
        messages=[{"role": "user", "content": classification_prompt}],
    )
    usage = message.usage
    # ... extract reasoning, intent ...
    correct = actual_intent.strip() == intent.strip()
    return reasoning, intent, correct, usage
```

### Run your evaluation

Establish thresholds before running. Examples:
- **Accuracy:** 95% (out of 100 tests)
- **Cost per classification:** 50% reduction on average from current method

---

## Improve performance

### Use a taxonomic hierarchy for 20+ intent categories

1. Organize intents in a taxonomic tree structure
2. Create cascading classifiers at every level of the tree

- **Pros**: Greater nuance and accuracy with targeted context-specific prompts
- **Cons**: Multiple classifiers increase latency; use Haiku for speed

### Use vector databases and similarity search

Employ a vector database to do similarity searches from a dataset of examples and retrieve the most relevant examples for a given query. This approach has been shown to improve performance from 71% accuracy to 93% accuracy.

### Account specifically for expected edge cases

- **Customers make implicit requests**: Provide examples with underlying intent labeled
- **Claude prioritizes emotion over intent**: Instruct Claude to "Ignore all customer emotions. Focus only on analyzing the intent."
- **Multiple issues cause prioritization confusion**: Clarify how to rank and prioritize intents

---

## Integrate Claude into your greater support workflow

Two integration approaches:
- **Push-based**: Support ticket system triggers code via webhook event → routes to classifier
  - More web-scalable, but needs a public endpoint
- **Pull-based**: Code polls for latest tickets on a schedule
  - Easier to implement, but may have latency or unnecessary polling
