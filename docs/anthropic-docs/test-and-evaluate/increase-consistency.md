---
source: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/increase-consistency
scraped: 2026-03-23
---

# Increase output consistency

---

> **For guaranteed JSON schema conformance**
>
> If you need Claude to always output valid JSON that conforms to a specific schema, use [Structured Outputs](/docs/en/build-with-claude/structured-outputs) instead of the prompt engineering techniques below. Structured outputs provide guaranteed schema compliance and are specifically designed for this use case.
>
> The techniques below are useful for general output consistency or when you need flexibility beyond strict JSON schemas.

Here's how to make Claude's responses more consistent:

## Specify the desired output format

Precisely define your desired output format using JSON, XML, or custom templates so that Claude understands every output formatting element you require.

Example — standardizing customer feedback:

```
You're a Customer Insights AI. Analyze this feedback and output in JSON format with keys:
"sentiment" (positive/negative/neutral), "key_issues" (list), and "action_items" (list of dicts with "team" and "task").

"I've been a loyal user for 3 years, but the recent UI update is a disaster. Finding basic features
is now a scavenger hunt. Plus, the new 'premium' pricing is outrageous. I'm considering switching
unless this is fixed ASAP."
```

## Prefill Claude's response

> **Note:** Prefilling is deprecated and not supported on Claude Opus 4.6, Claude Sonnet 4.6, and Claude Sonnet 4.5. Use [structured outputs](/docs/en/build-with-claude/structured-outputs) or system prompt instructions instead.

Prefill the `Assistant` turn with your desired format. This trick bypasses Claude's friendly preamble and enforces your structure.

Example — daily sales report with XML template:

```
You're an insightful Sales Intelligence AI. Generate today's sales report.

Structure the report like this:

<report>
    <summary>
        <metric name="total_revenue">$0.00</metric>
        <metric name="units_sold">0</metric>
        <metric name="avg_order_value">$0.00</metric>
    </summary>
    <top_products>
        <product>
            <name>Product Name</name>
            <revenue>$0.00</revenue>
            <units>0</units>
        </product>
        ...
    </top_products>
    ...
</report>
```

Then prefill the assistant turn with `<report>` to bypass the preamble.

## Constrain with examples

Provide examples of your desired output. This trains Claude's understanding better than abstract instructions.

Example — generating consistent market intelligence:

```
As a Market Intelligence AI, analyze our competitors. Output following this example format:

<competitor>
  <name>Rival Inc</name>
  <overview>A 50-word summary.</overview>
  <swot>
    <strengths>- Bullet points</strengths>
    <weaknesses>- Bullet points</weaknesses>
    <opportunities>- Bullet points</opportunities>
    <threats>- Bullet points</threats>
  </swot>
  <strategy>A 30-word strategic response.</strategy>
</competitor>

Now, analyze AcmeGiant and AcmeDataCo using this format.
```

## Use retrieval for contextual consistency

For tasks requiring consistent context (e.g., chatbots, knowledge bases), use retrieval to ground Claude's responses in a fixed information set.

Example — IT support knowledge base:

```
You're our IT Support AI that draws on knowledge base data. Here are entries from your knowledge base:

<kb>
  <entry>
    <id>1</id>
    <title>Reset Active Directory password</title>
    <content>1. Go to password.ourcompany.com
2. Enter your username
3. Click "Forgot Password"
4. Follow email instructions</content>
  </entry>
  ...
</kb>

When helping users, always check the knowledge base first. Respond in this format:

<response>
  <kb_entry>Knowledge base entry used</kb_entry>
  <answer>Your response</answer>
</response>
```

## Chain prompts for complex tasks

Break down complex tasks into smaller, consistent subtasks. Each subtask gets Claude's full attention, reducing inconsistency errors across scaled workflows.

## Keep Claude in character

For role-based applications, maintaining consistent character requires deliberate prompting:

- **Use system prompts to set the role**: Define Claude's role and personality clearly. Provide detailed information about the personality, background, and any specific traits or quirks.
- **Prepare Claude for possible scenarios**: Provide a list of common scenarios and expected responses in your prompts.

Example — enterprise chatbot role prompting:

```
System: You are AcmeBot, the enterprise-grade AI assistant for AcmeTechCo. Your role:
    - Analyze technical documents (TDDs, PRDs, RFCs)
    - Provide actionable insights for engineering, product, and ops teams
    - Maintain a professional, concise tone

Your rules for interaction are:
    - Always reference AcmeTechCo standards or industry best practices
    - If unsure, ask for clarification before proceeding
    - Never disclose confidential AcmeTechCo information.

As AcmeBot, you should handle situations along these guidelines:
    - If asked about AcmeTechCo IP: "I cannot disclose TechCo's proprietary information."
    - If questioned on best practices: "Per ISO/IEC 25010, we prioritize..."
    - If unclear on a doc: "To ensure accuracy, please clarify section 3.2..."
```
