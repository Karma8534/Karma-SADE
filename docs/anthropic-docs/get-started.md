---
source: https://platform.claude.com/docs/en/get-started
scraped: 2026-03-23
---

# Get started with Claude

Make your first API call to Claude and build a simple web search assistant.

---

## Prerequisites

- An Anthropic [Console account](/)
- An [API key](/settings/keys)

## Call the API

### Using cURL

**Step 1: Set your API key**

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

**Step 2: Make your first API call**

```bash
curl https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1000,
    "messages": [
      {
        "role": "user",
        "content": "What should I search for to find the latest developments in renewable energy?"
      }
    ]
  }'
```

### Using Python

**Step 1: Set your API key**

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

**Step 2: Install the SDK**

```bash
pip install anthropic
```

**Step 3: Create your code**

Save as `quickstart.py`:

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "What should I search for to find the latest developments in renewable energy?",
        }
    ],
)
print(message.content)
```

**Step 4: Run your code**

```bash
python quickstart.py
```

### Using TypeScript

**Step 1: Set your API key**

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

**Step 2: Install the SDK**

```bash
npm install @anthropic-ai/sdk
```

**Step 3: Create your code**

Save as `quickstart.ts`:

```typescript
import Anthropic from "@anthropic-ai/sdk";

async function main() {
  const anthropic = new Anthropic();

  const msg = await anthropic.messages.create({
    model: "claude-opus-4-6",
    max_tokens: 1000,
    messages: [
      {
        role: "user",
        content: "What should I search for to find the latest developments in renewable energy?"
      }
    ]
  });
  console.log(msg);
}

main().catch(console.error);
```

**Step 4: Run your code**

```bash
npx tsx quickstart.ts
```

### Using Java

Add the Anthropic Java SDK to your project. Find the current version on [Maven Central](https://central.sonatype.com/artifact/com.anthropic/anthropic-java).

**Gradle:**
```groovy
implementation("com.anthropic:anthropic-java:2.18.0")
```

**Maven:**
```xml
<dependency>
  <groupId>com.anthropic</groupId>
  <artifactId>anthropic-java</artifactId>
  <version>2.18.0</version>
</dependency>
```

**QuickStart.java:**

```java
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.Message;
import com.anthropic.models.messages.MessageCreateParams;

public class QuickStart {

  public static void main(String[] args) {
    AnthropicClient client = AnthropicOkHttpClient.fromEnv();

    MessageCreateParams params = MessageCreateParams.builder()
      .model("claude-opus-4-6")
      .maxTokens(1000)
      .addUserMessage(
        "What should I search for to find the latest developments in renewable energy?"
      )
      .build();

    Message message = client.messages().create(params);
    System.out.println(message.content());
  }
}
```

## Next steps

You made your first API call. Next, learn the Messages API patterns you'll use in every Claude integration.

- **Working with the Messages API**: Learn multi-turn conversations, system prompts, stop reasons, and other core patterns. See [/docs/en/build-with-claude/working-with-messages](/docs/en/build-with-claude/working-with-messages)
- **Models overview**: Compare Claude models by capability and cost. See [/docs/en/about-claude/models/overview](/docs/en/about-claude/models/overview)
- **Features overview**: Browse all Claude capabilities: tools, context management, structured outputs, and more. See [/docs/en/build-with-claude/overview](/docs/en/build-with-claude/overview)
- **Client SDKs**: Reference documentation for Python, TypeScript, Java, and other client libraries. See [/docs/en/api/client-sdks](/docs/en/api/client-sdks)
