---
source: https://platform.claude.com/docs/en/build-with-claude/citations
scraped: 2026-03-23
section: build-with-claude
---

# Citations

---

Claude is capable of providing detailed citations when answering questions about documents, helping you track and verify information sources in responses.

All active models support citations, with the exception of Haiku 3.

Here's an example of how to use citations with the Messages API:

```python Python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "text",
                        "media_type": "text/plain",
                        "data": "The grass is green. The sky is blue.",
                    },
                    "title": "My Document",
                    "context": "This is a trustworthy document.",
                    "citations": {"enabled": True},
                },
                {"type": "text", "text": "What color is the grass and sky?"},
            ],
        }
    ],
)
print(response)
```

> **Comparison with prompt-based approaches**: The citations feature has these advantages over prompt-based citations:
> - **Cost savings:** `cited_text` does not count towards your output tokens.
> - **Better citation reliability:** Citations are parsed into the respective response formats and `cited_text` is extracted, guaranteeing valid pointers to the provided documents.
> - **Improved citation quality:** In evaluations, the citations feature was found to be significantly more likely to cite the most relevant quotes from documents.

---

## How citations work

### Step 1: Provide document(s) and enable citations

- Include documents in any of the supported formats: PDFs, plain text, or custom content documents
- Set `citations.enabled=true` on each of your documents. Currently, citations must be enabled on all or none of the documents within a request.
- Note that only text citations are currently supported and image citations are not yet possible.

### Step 2: Documents get processed

- Document contents are "chunked" in order to define the minimum granularity of possible citations.
  - **For PDFs:** Text is extracted and content is chunked into sentences. Citing images from PDFs is not currently supported.
  - **For plain text documents:** Content is chunked into sentences that can be cited from.
  - **For custom content documents:** Your provided content blocks are used as-is and no further chunking is done.

### Step 3: Claude provides cited response

- Responses may now include multiple text blocks where each text block can contain a claim that Claude is making and a list of citations that support the claim.
- Citations reference specific locations in source documents. The format of these citations are dependent on the type of document being cited from.
  - **For PDFs:** Citations include the page number range (1-indexed).
  - **For plain text documents:** Citations include the character index range (0-indexed).
  - **For custom content documents:** Citations include the content block index range (0-indexed) corresponding to the original content list provided.
- Document indices are provided to indicate the reference source and are 0-indexed according to the list of all documents in your original request.

### Citable vs non-citable content

- Text found within a document's `source` content can be cited from.
- `title` and `context` are optional fields that will be passed to the model but not used towards cited content.
- `title` is limited in length so you may find the `context` field to be useful in storing any document metadata as text or stringified json.

### Citation indices
- Document indices are 0-indexed from the list of all document content blocks in the request (spanning across all messages).
- Character indices are 0-indexed with exclusive end indices.
- Page numbers are 1-indexed with exclusive end page numbers.
- Content block indices are 0-indexed with exclusive end indices from the `content` list provided in the custom content document.

### Token costs
- Enabling citations incurs a slight increase in input tokens due to system prompt additions and document chunking.
- The citations feature is very efficient with output tokens. The `cited_text` field is provided for convenience and does not count towards output tokens.
- When passed back in subsequent conversation turns, `cited_text` is also not counted towards input tokens.

### Feature compatibility
Citations works in conjunction with other API features including prompt caching, token counting and batch processing.

> **Warning**: **Citations and Structured Outputs are incompatible**. Citations cannot be used together with Structured Outputs. If you enable citations on any user-provided document and also include the `output_config.format` parameter, the API will return a 400 error.

## Document Types

### Choosing a document type

Three document types are supported for citations. Documents can be provided directly in the message (base64, text, or URL) or uploaded via the Files API and referenced by `file_id`:

| Type | Best for | Chunking | Citation format |
| :--- | :--- | :--- | :--- |
| Plain text | Simple text documents, prose | Sentence | Character indices (0-indexed) |
| PDF | PDF files with text content | Sentence | Page numbers (1-indexed) |
| Custom content | Lists, transcripts, special formatting, more granular citations | No additional chunking | Block indices (0-indexed) |

### Plain text documents

Plain text documents are automatically chunked into sentences. Example:

```python
{
    "type": "document",
    "source": {
        "type": "text",
        "media_type": "text/plain",
        "data": "Plain text content...",
    },
    "title": "Document Title",  # optional
    "context": "Context about the document that will not be cited from",  # optional
    "citations": {"enabled": True},
}
```

Example plain text citation:
```python
{
    "type": "char_location",
    "cited_text": "The exact text being cited",  # not counted towards output tokens
    "document_index": 0,
    "document_title": "Document Title",
    "start_char_index": 0,  # 0-indexed
    "end_char_index": 50,  # exclusive
}
```

### PDF documents

PDF documents can be provided as base64-encoded data or by `file_id`. Example PDF citation:

```python
{
    "type": "page_location",
    "cited_text": "The exact text being cited",  # not counted towards output tokens
    "document_index": 0,
    "document_title": "Document Title",
    "start_page_number": 1,  # 1-indexed
    "end_page_number": 2,  # exclusive
}
```

### Custom content documents

Custom content documents give you control over citation granularity:

```python
{
    "type": "document",
    "source": {
        "type": "content",
        "content": [
            {"type": "text", "text": "First chunk"},
            {"type": "text", "text": "Second chunk"},
        ],
    },
    "title": "Document Title",  # optional
    "context": "Context about the document that will not be cited from",  # optional
    "citations": {"enabled": True},
}
```

## Response Structure

When citations are enabled, responses include multiple text blocks with citations:

```python
{
    "content": [
        {"type": "text", "text": "According to the document, "},
        {
            "type": "text",
            "text": "the grass is green",
            "citations": [
                {
                    "type": "char_location",
                    "cited_text": "The grass is green.",
                    "document_index": 0,
                    "document_title": "Example Document",
                    "start_char_index": 0,
                    "end_char_index": 20,
                }
            ],
        },
        {"type": "text", "text": " and "},
        {
            "type": "text",
            "text": "the sky is blue",
            "citations": [
                {
                    "type": "char_location",
                    "cited_text": "The sky is blue.",
                    "document_index": 0,
                    "document_title": "Example Document",
                    "start_char_index": 20,
                    "end_char_index": 36,
                }
            ],
        },
    ]
}
```

### Streaming Support

For streaming responses, a `citations_delta` type is included that contains a single citation to be added to the `citations` list on the current `text` content block.

### Using Prompt Caching with Citations

Citations and prompt caching can be used together effectively. Apply `cache_control` to your top-level document content blocks:

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "text",
                        "media_type": "text/plain",
                        "data": long_document,
                    },
                    "citations": {"enabled": True},
                    "cache_control": {
                        "type": "ephemeral"
                    },  # Cache the document content
                },
                {
                    "type": "text",
                    "text": "What does this document say about API features?",
                },
            ],
        }
    ],
)
print(response)
```
