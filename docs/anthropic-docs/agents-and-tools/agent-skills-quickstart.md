---
source: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart
scraped: 2026-03-23
section: agents-and-tools
---

# Get started with Agent Skills in the API

Learn how to use Agent Skills to create documents with the Claude API in under 10 minutes.

This tutorial shows you how to use Agent Skills to create a PowerPoint presentation. You'll learn how to enable Skills, make a simple request, and access the generated file.

## Prerequisites

- Claude API key
- Python 3.7+ or curl installed
- Basic familiarity with making API requests

## Agent Skills overview

Pre-built Agent Skills extend Claude's capabilities with specialized expertise for tasks like creating documents, analyzing data, and processing files. Anthropic provides the following pre-built Agent Skills in the API:

- **PowerPoint (pptx):** Create and edit presentations
- **Excel (xlsx):** Create and analyze spreadsheets
- **Word (docx):** Create and edit documents
- **PDF (pdf):** Generate PDF documents

## Step 1: List available Skills

First, check what Skills are available. Use the Skills API to list all Anthropic-managed Skills:

```python Python
import anthropic

client = anthropic.Anthropic()

# List Anthropic-managed Skills
skills = client.beta.skills.list(source="anthropic", betas=["skills-2025-10-02"])

for skill in skills.data:
    print(f"{skill.id}: {skill.display_title}")
```

```bash Shell
curl "https://api.anthropic.com/v1/skills?source=anthropic" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: skills-2025-10-02"
```

You see the following Skills: `pptx`, `xlsx`, `docx`, and `pdf`.

## Step 2: Create a presentation

Now use the PowerPoint Skill to create a presentation about renewable energy. Specify Skills using the `container` parameter in the Messages API:

```python Python
import anthropic

client = anthropic.Anthropic()

# Create a message with the PowerPoint Skill
response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [{"type": "anthropic", "skill_id": "pptx", "version": "latest"}]
    },
    messages=[
        {
            "role": "user",
            "content": "Create a presentation about renewable energy with 5 slides",
        }
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)

print(response.content)
```

```bash Shell
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: code-execution-2025-08-25,skills-2025-10-02" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 4096,
    "container": {
      "skills": [
        {
          "type": "anthropic",
          "skill_id": "pptx",
          "version": "latest"
        }
      ]
    },
    "messages": [{"role": "user", "content": "Create a presentation about renewable energy with 5 slides"}],
    "tools": [{"type": "code_execution_20250825", "name": "code_execution"}]
  }'
```

Let's break down what each part does:

- **`container.skills`:** Specifies which Skills Claude can use
- **`type: "anthropic"`:** Indicates this is an Anthropic-managed Skill
- **`skill_id: "pptx"`:** The PowerPoint Skill identifier
- **`version: "latest"`:** The Skill version set to the most recently published
- **`tools`:** Enables code execution (required for Skills)
- **Beta headers:** `code-execution-2025-08-25` and `skills-2025-10-02`

## Step 3: Download the created file

The presentation was created in the code execution container and saved as a file. The response includes a file reference with a file ID. Extract the file ID and download it using the Files API:

```python Python
from typing import Any

response: Any = None
# Extract file ID from response
file_id = None
for block in response.content:
    if block.type == "tool_use" and block.name == "code_execution":
        # File ID is in the tool result
        for result_block in block.content:
            if hasattr(result_block, "file_id"):
                file_id = result_block.file_id
                break

if file_id:
    # Download the file
    file_content = client.beta.files.download(
        file_id=file_id, betas=["files-api-2025-04-14"]
    )

    # Save to disk
    with open("renewable_energy.pptx", "wb") as f:
        file_content.write_to_file(f.name)

    print(f"Presentation saved to renewable_energy.pptx")
```

## Try more examples

### Create a spreadsheet

```python Python
response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [{"type": "anthropic", "skill_id": "xlsx", "version": "latest"}]
    },
    messages=[
        {
            "role": "user",
            "content": "Create a quarterly sales tracking spreadsheet with sample data",
        }
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)
```

### Create a Word document

```python Python
response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [{"type": "anthropic", "skill_id": "docx", "version": "latest"}]
    },
    messages=[
        {
            "role": "user",
            "content": "Write a 2-page report on the benefits of renewable energy",
        }
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)
```

### Generate a PDF

```python Python
response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [{"type": "anthropic", "skill_id": "pdf", "version": "latest"}]
    },
    messages=[{"role": "user", "content": "Generate a PDF invoice template"}],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)
```
