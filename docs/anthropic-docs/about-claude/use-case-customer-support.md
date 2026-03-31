---
source: https://platform.claude.com/docs/en/about-claude/use-case-guides/customer-support-chat
scraped: 2026-03-23
---

# Customer support agent

This guide walks through how to leverage Claude's advanced conversational capabilities to handle customer inquiries in real time, providing 24/7 support, reducing wait times, and managing high support volumes with accurate responses and positive interactions.

---

## Before building with Claude

### Decide whether to use Claude for support chat

Key indicators for using Claude:
- **High volume of repetitive queries**: Claude handles large numbers of similar questions efficiently
- **Need for quick information synthesis**: Claude quickly retrieves and combines information from vast knowledge bases
- **24/7 availability requirement**: Claude provides round-the-clock support without fatigue
- **Rapid scaling during peak periods**: Claude handles sudden increases in query volume
- **Consistent brand voice**: Claude consistently represents your brand's tone and values

Advantages over other LLMs:
- Natural, nuanced conversation with human-like quality
- Handles complex and open-ended queries without canned responses
- Scalable multilingual support in 200+ languages

### Define your ideal chat interaction

Outline an ideal customer interaction to define technical requirements. Example for car insurance:

1. Customer initiates support chat
2. Claude warmly greets customer
3. Customer asks about electric vehicle insurance
4. Claude provides relevant information and answers questions
5. Customer asks off-topic questions → Claude redirects back to car insurance
6. Customer expresses interest in a quote → Claude collects information, calls quote API, presents quote
7. Claude answers follow-up questions and guides customer to next steps

### Break the interaction into unique tasks

Break down the ideal interaction into every task Claude needs to perform:

1. **Greeting and general guidance**: Warm greeting, provide general company information
2. **Product information**: Provide EV coverage info, answer questions, offer source links
3. **Conversation management**: Stay on topic, redirect off-topic questions
4. **Quote generation**: Ask eligibility questions, adapt to responses, submit to quote API, present result

### Establish success criteria

Key metrics:
- **Query comprehension accuracy**: Correct interpretation of customer intent; aim 95%+
- **Response relevance**: Addresses specific question or issue; aim 90%+
- **Topic adherence**: 95% of responses directly related to relevant topic
- **Escalation efficiency**: Recognize when human intervention needed; aim 95%+
- **Deflection rate**: Handle without human intervention; typically aim 70-80%
- **Customer satisfaction score**: Aim 4/5 or higher via post-interaction surveys
- **Average handle time**: Lower than human agents

---

## How to implement Claude as a customer service agent

### Choose the right Claude model

For customer support chat, Claude Opus 4.6 balances intelligence, latency, and cost. For complex flows with multiple prompts including RAG, tool use, and/or long-context prompts, Claude Haiku 4.5 may optimize latency better.

### Build a strong prompt

Start with a system prompt:

```python
IDENTITY = """You are Eva, a friendly and knowledgeable AI assistant for Acme Insurance
Company. Your role is to warmly welcome customers and provide information on
Acme's insurance offerings, which include car insurance and electric car
insurance. You can also help customers get quotes for their insurance needs."""
```

Build piecemeal sections for each task — static context, examples, guardrails:

```python
STATIC_GREETINGS_AND_GENERAL = """
<static_context>
Acme Auto Insurance: Your Trusted Companion on the Road
...
Business hours: Monday-Friday, 9 AM - 5 PM EST
Customer service number: 1-800-123-4567
</static_context>
"""

EXAMPLES = """
Here are a few examples of how you can interact with customers:

<example 1>
H: Hi, do you offer commercial insurance for small businesses?
A: Unfortunately, we don't offer commercial insurance at this time. However, we do provide personal insurance including car and electric car insurance. Would you like to know more?
</example 1>
...
"""

ADDITIONAL_GUARDRAILS = """Please adhere to the following guardrails:
1. Only provide information about insurance types listed in our offerings.
2. If asked about insurance we don't offer, politely state that we don't provide that service.
3. Do not speculate about future product offerings or company plans.
4. Don't make promises or enter into agreements it's not authorized to make.
5. Do not mention any competitor's products or services.
"""
```

### Add dynamic and agentic capabilities with tool use

Define tools for external APIs:

```python
TOOLS = [
    {
        "name": "get_quote",
        "description": "Calculate the insurance quote based on user input. Returned value is per month premium.",
        "input_schema": {
            "type": "object",
            "properties": {
                "make": {"type": "string", "description": "The make of the vehicle."},
                "model": {"type": "string", "description": "The model of the vehicle."},
                "year": {"type": "integer", "description": "The year the vehicle was manufactured."},
                "mileage": {"type": "integer", "description": "The mileage on the vehicle."},
                "driver_age": {"type": "integer", "description": "The age of the primary driver."},
            },
            "required": ["make", "model", "year", "mileage", "driver_age"],
        },
    }
]
```

### Deploy your prompts

Build a ChatBot class with `generate_message` and `process_user_input` methods:

```python
from anthropic import Anthropic

class ChatBot:
    def __init__(self, session_state):
        self.anthropic = Anthropic()
        self.session_state = session_state

    def generate_message(self, messages, max_tokens):
        response = self.anthropic.messages.create(
            model=MODEL,
            system=IDENTITY,
            max_tokens=max_tokens,
            messages=messages,
            tools=TOOLS,
        )
        return response

    def process_user_input(self, user_input):
        self.session_state.messages.append({"role": "user", "content": user_input})
        response_message = self.generate_message(
            messages=self.session_state.messages,
            max_tokens=2048,
        )
        # Handle tool_use or text response
        if response_message.content[-1].type == "tool_use":
            # ... handle tool call, get result, follow up ...
            pass
        elif response_message.content[0].type == "text":
            response_text = response_message.content[0].text
            self.session_state.messages.append({"role": "assistant", "content": response_text})
            return response_text
```

---

## Improve performance

### Reduce long context latency with RAG

When dealing with large amounts of static and dynamic context, use Retrieval Augmented Generation (RAG) techniques. Using embedding models to convert information into vector representations allows dynamic retrieval of relevant information, reducing costs, improving accuracy, and handling large knowledge bases.

### Integrate real-time data with tool use

For queries requiring real-time information (account balances, policy details), use tool use to look up customer information, retrieve order details, and take actions on behalf of the customer.

### Strengthen input and output guardrails

- **Reduce hallucination**: Implement fact-checking and citations
- **Mitigate jailbreaks**: Use harmlessness screens and input validation
- **Increase output consistency**: Prevent Claude from changing style or going out of character
- **Remove PII**: Unless explicitly required, strip PII from responses

### Reduce perceived response time with streaming

Use the Anthropic Streaming API to display responses progressively, mitigating the impact of longer processing times on user experience.

### Scale your chatbot

As complexity grows:
- Optimize prompts first using prompt engineering guides
- Add additional tools to the prompt
- For highly varied tasks, consider a separate intent classifier to route queries to specialized conversations
