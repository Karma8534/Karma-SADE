---
source: https://platform.claude.com/docs/en/build-with-claude/pdf-support
scraped: 2026-03-23
section: build-with-claude
---

# PDF support

Process PDFs with Claude. Extract text, analyze charts, and understand visual content from your documents.

---

You can ask Claude about any text, pictures, charts, and tables in PDFs you provide. Some sample use cases:
- Analyzing financial reports and understanding charts/tables
- Extracting key information from legal documents
- Translation assistance for documents
- Converting document information into structured formats

## Before you begin

### Check PDF requirements

| Requirement | Limit |
|------------|--------|
| Maximum request size | 32 MB |
| Maximum pages per request | 600 (100 for models with a 200k-token context window) |
| Format | Standard PDF (no passwords/encryption) |

> **Tip**: Dense PDFs (many small-font pages, complex tables, or heavy graphics) can fill the context window before reaching the page limit. Try splitting the document into sections; for large files, since each page is processed as an image, downsampling embedded images can also help.

### Supported platforms and models

PDF support is currently supported via direct API access and Google Vertex AI. All active models support PDF processing.

### Amazon Bedrock PDF Support

When using PDF support through Amazon Bedrock's Converse API, there are two distinct document processing modes:

> **Important**: To access Claude's full visual PDF understanding capabilities in the Converse API, you must enable citations. Without citations enabled, the API falls back to basic text extraction only.

1. **Converse Document Chat** (Text extraction only): Provides basic text extraction from PDFs. Cannot analyze images, charts, or visual layouts within PDFs. Automatically used when citations are not enabled.

2. **Claude PDF Chat** (Full visual understanding): Provides complete visual analysis of PDFs. Can understand and analyze charts, graphs, images, and visual layouts. **Requires citations to be enabled** in the Converse API.

## Process PDFs with Claude

### Send your first PDF request

You can provide PDFs to Claude in three ways:

1. As a URL reference to a PDF hosted online
2. As a base64-encoded PDF in `document` content blocks
3. By a `file_id` from the Files API

#### Option 1: URL-based PDF document

```python Python
import anthropic

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "url",
                        "url": "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf",
                    },
                },
                {"type": "text", "text": "What are the key findings in this document?"},
            ],
        }
    ],
)

print(message.content)
```

#### Option 2: Base64-encoded PDF document

```python Python
import anthropic
import base64
import httpx

# Load and encode the PDF
pdf_url = "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
pdf_data = base64.standard_b64encode(httpx.get(pdf_url).content).decode("utf-8")

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                },
                {"type": "text", "text": "What are the key findings in this document?"},
            ],
        }
    ],
)

print(message.content)
```

#### Option 3: Files API

For PDFs you'll use repeatedly, or when you want to avoid encoding overhead, use the Files API:

```python Python
import anthropic

client = anthropic.Anthropic()

# Upload the PDF file
with open("document.pdf", "rb") as f:
    file_upload = client.beta.files.upload(file=("document.pdf", f, "application/pdf"))

# Use the uploaded file in a message
message = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    betas=["files-api-2025-04-14"],
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {"type": "file", "file_id": file_upload.id},
                },
                {"type": "text", "text": "What are the key findings in this document?"},
            ],
        }
    ],
)

print(message.content)
```

### How PDF support works

1. **The system extracts the contents of the document.** The system converts each page of the document into an image. The text from each page is extracted and provided alongside each page's image.
2. **Claude analyzes both the text and images** to better understand the document. Documents are provided as a combination of text and images for analysis.
3. **Claude responds, referencing the PDF's contents** if relevant. Claude can reference both textual and visual content when it responds.

### Estimate your costs
The token count of a PDF file depends on the total text extracted from the document as well as the number of pages:
- Text token costs: Each page typically uses 1,500-3,000 tokens per page depending on content density.
- Image token costs: Since each page is converted into an image, the same image-based cost calculations are applied.

## Optimize PDF processing

### Improve performance
Follow these best practices for optimal results:
- Place PDFs before text in your requests
- Use standard fonts
- Ensure text is clear and legible
- Rotate pages to proper upright orientation
- Use logical page numbers (from PDF viewer) in prompts
- Split large PDFs into chunks when needed
- Enable prompt caching for repeated analysis

### Use prompt caching

Cache PDFs to improve performance on repeated queries:

```python Python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                    "cache_control": {"type": "ephemeral"},
                },
                {"type": "text", "text": "Analyze this document."},
            ],
        }
    ],
)
```

### Process document batches

Use the Message Batches API for high-volume workflows:

```python Python
import anthropic

client = anthropic.Anthropic()

message_batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": "doc1",
            "params": {
                "model": "claude-opus-4-6",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_data,
                                },
                            },
                            {"type": "text", "text": "Summarize this document."},
                        ],
                    }
                ],
            },
        }
    ]
)
```
