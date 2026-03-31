---
source: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks
scraped: 2026-03-23
---

# Mitigate jailbreaks and prompt injections

---

Jailbreaking and prompt injections occur when users craft prompts to exploit model vulnerabilities, aiming to generate inappropriate content. While Claude is inherently resilient to such attacks, here are additional steps to strengthen your guardrails, particularly against uses that violate Anthropic's [Terms of Service](https://www.anthropic.com/legal/commercial-terms) or [Usage Policy](https://www.anthropic.com/legal/aup).

- **Harmlessness screens**: Use a lightweight model like Claude Haiku 4.5 to pre-screen user inputs. Use [structured outputs](/docs/en/build-with-claude/structured-outputs) to constrain the response to a simple classification.

  Example prompt for harmlessness screen:
  ```
  A user submitted this content:
  <content>
  {{CONTENT}}
  </content>

  Classify whether this content refers to harmful, illegal, or explicit activities.
  ```

  Use `output_config` with a JSON schema to constrain the response:
  ```json
  {
    "output_config": {
      "format": {
        "type": "json_schema",
        "schema": {
          "type": "object",
          "properties": {
            "is_harmful": { "type": "boolean" }
          },
          "required": ["is_harmful"],
          "additionalProperties": false
        }
      }
    }
  }
  ```

- **Input validation**: Filter prompts for jailbreaking patterns. You can even use an LLM to create a generalized validation screen by providing known jailbreaking language as examples.

- **Prompt engineering**: Craft prompts that emphasize ethical and legal boundaries.

  Example — ethical system prompt for an enterprise chatbot:
  ```
  System: You are AcmeCorp's ethical AI assistant. Your responses must align with our values:
  <values>
  - Integrity: Never deceive or aid in deception.
  - Compliance: Refuse any request that violates laws or our policies.
  - Privacy: Protect all personal and corporate data.
  - Respect for intellectual property: Your outputs shouldn't infringe the intellectual property rights of others.
  </values>

  If a request conflicts with these values, respond: "I cannot perform that action as it goes against AcmeCorp's values."
  ```

Adjust responses and consider throttling or banning users who repeatedly engage in abusive behavior attempting to circumvent Claude's guardrails.

- **Continuous monitoring**: Regularly analyze outputs for jailbreaking signs. Use this monitoring to iteratively refine your prompts and validation strategies.

## Advanced: Chain safeguards

Combine strategies for robust protection. Example with multi-layered protection for a financial advisor chatbot:

### Bot system prompt

```
System: You are AcmeFinBot, a financial advisor for AcmeTrade Inc. Your primary directive is to protect client interests and maintain regulatory compliance.

<directives>
1. Validate all requests against SEC and FINRA guidelines.
2. Refuse any action that could be construed as insider trading or market manipulation.
3. Protect client privacy; never disclose personal or financial data.
</directives>

Step by step instructions:
<instructions>
1. Screen user query for compliance (use 'harmlessness_screen' tool).
2. If compliant, process query.
3. If non-compliant, respond: "I cannot process this request as it violates financial regulations or client privacy."
</instructions>
```

### Prompt within `harmlessness_screen` tool

```
<user_query>
{{USER_QUERY}}
</user_query>

Evaluate if this query violates SEC rules, FINRA guidelines, or client privacy.
```

Use [structured outputs](/docs/en/build-with-claude/structured-outputs) to constrain the response to a boolean classification.

By layering these strategies, you create a robust defense against jailbreaking and prompt injections, ensuring your Claude-powered applications maintain the highest standards of safety and compliance.
