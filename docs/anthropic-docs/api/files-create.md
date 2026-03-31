---
source: https://platform.claude.com/docs/en/api/files-create
scraped: 2026-03-23
section: api
---

# Upload File

**post** `/v1/files`

Upload a file for use with the Files API.

## Header Parameters

- `"anthropic-beta": optional array of AnthropicBeta`

  The Files API requires `files-api-2025-04-14`. Other supported beta values include:
  - `"message-batches-2024-09-24"`
  - `"prompt-caching-2024-07-31"`
  - `"computer-use-2024-10-22"`
  - `"computer-use-2025-01-24"`
  - `"pdfs-2024-09-25"`
  - `"token-counting-2024-11-01"`
  - `"token-efficient-tools-2025-02-19"`
  - `"output-128k-2025-02-19"`
  - `"files-api-2025-04-14"`
  - `"mcp-client-2025-04-04"`
  - `"mcp-client-2025-11-20"`
  - `"dev-full-thinking-2025-05-14"`
  - `"interleaved-thinking-2025-05-14"`
  - `"code-execution-2025-05-22"`
  - `"extended-cache-ttl-2025-04-11"`
  - `"context-1m-2025-08-07"`
  - `"context-management-2025-06-27"`
  - `"model-context-window-exceeded-2025-08-26"`
  - `"skills-2025-10-02"`
  - `"fast-mode-2026-02-01"`

## Returns

- `FileMetadata = object { id, created_at, filename, mime_type, size_bytes, type, downloadable }`

  - `id: string` — Unique object identifier.
  - `created_at: string` — RFC 3339 datetime string representing when the file was created.
  - `filename: string` — Original filename of the uploaded file.
  - `mime_type: string` — MIME type of the file.
  - `size_bytes: number` — Size of the file in bytes.
  - `type: "file"` — Object type. For files, this is always `"file"`.
  - `downloadable: optional boolean` — Whether the file can be downloaded.

## Example

```bash
curl https://api.anthropic.com/v1/files?beta=true \
    -H 'Content-Type: multipart/form-data' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: files-api-2025-04-14' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -F 'file=@/path/to/file'
```
