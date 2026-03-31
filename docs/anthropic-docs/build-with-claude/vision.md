---
source: https://platform.claude.com/docs/en/build-with-claude/vision
scraped: 2026-03-23
section: build-with-claude
---

# Vision

Claude's vision capabilities allow it to understand and analyze images, opening up exciting possibilities for multimodal interaction.

---

This guide describes how to work with images in Claude, including best practices, code examples, and limitations to keep in mind.

## How to use vision

Use Claude's vision capabilities through:

- [claude.ai](https://claude.ai/). Upload an image like you would a file, or drag and drop an image directly into the chat window.
- The Console Workbench. A button to add images appears at the top right of every User message block.
- **API request**. See the examples in this guide.

## Before you upload

### Basics and limits

You can include multiple images in a single request: up to 20 for claude.ai, and up to 600 for API requests (100 for models with a 200k-token context window). Claude analyzes all provided images when formulating its response.

If you submit an image larger than 8000x8000 px, it is rejected. If you submit more than 20 images in one API request, this limit is 2000x2000 px.

### Evaluate image size

For optimal performance, resize images before uploading if they are too large. If your image's long edge is more than 1568 pixels, or your image is more than ~1,600 tokens, it is first scaled down, preserving aspect ratio, until it's within the size limits.

> **Tip**: To improve time-to-first-token, consider resizing images to no more than 1.15 megapixels (and within 1568 pixels in both dimensions).

Here is a table of maximum image sizes accepted by the API that will not be resized for common aspect ratios. With Claude Sonnet 4.6, these images use approximately 1,600 tokens and around $4.80/1k images.

| Aspect ratio | Image size |
| ------------ | ------------ |
| 1:1 | 1092x1092 px |
| 3:4 | 951x1268 px |
| 2:3 | 896x1344 px |
| 9:16 | 819x1456 px |
| 1:2 | 784x1568 px |

### Calculate image costs

Each image you include in a request to Claude counts towards your token usage. To calculate the approximate cost, multiply the approximate number of image tokens by the per-token price of the model you're using.

If your image does not need to be resized, you can estimate the number of tokens used through this algorithm: `tokens = (width px * height px)/750`

| Image size | # of Tokens | Cost / image | Cost / 1k images |
| ----------------------------- | ------------ | ------------ | ---------------- |
| 200x200 px (0.04 megapixels) | ~54 | ~$0.00016 | ~$0.16 |
| 1000x1000 px (1 megapixel) | ~1334 | ~$0.004 | ~$4.00 |
| 1092x1092 px (1.19 megapixels) | ~1590 | ~$0.0048 | ~$4.80 |

### Ensuring image quality

When providing images to Claude, keep the following in mind for best results:

- **Image format**: Use a supported image format: JPEG, PNG, GIF, or WebP.
- **Image clarity**: Ensure images are clear and not too blurry or pixelated.
- **Text**: If the image contains important text, make sure it's legible and not too small.

## Prompt examples

> **Tip**: Just as placing long documents before your query improves results in text prompts, Claude works best when images come before text.

### Base64-encoded image example

```python Python
import anthropic

image1_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
image1_media_type = "image/png"

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image1_media_type,
                        "data": image1_data,
                    },
                },
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ],
)
print(message)
```

### URL-based image example

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
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg",
                    },
                },
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ],
)
print(message)
```

### Files API image example

For images you'll use repeatedly or when you want to avoid encoding overhead, use the Files API. Upload the image once, then reference the returned `file_id` in subsequent messages.

> **Tip**: In multi-turn conversations and agentic workflows, each request resends the full conversation history. If images are base64-encoded, the full image bytes are included in the payload on every turn. Uploading images to the Files API and referencing them by `file_id` keeps request payloads small regardless of how many images accumulate in the conversation history.

```python Python
import anthropic

client = anthropic.Anthropic()

# Upload the image file
with open("image.jpg", "rb") as f:
    file_upload = client.beta.files.upload(file=("image.jpg", f, "image/jpeg"))

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
                    "type": "image",
                    "source": {"type": "file", "file_id": file_upload.id},
                },
                {"type": "text", "text": "Describe this image."},
            ],
        }
    ],
)

print(message.content)
```

### Multiple images

In situations where there are multiple images, introduce each image with `Image 1:` and `Image 2:` and so on.

```python Python
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Image 1:"},
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg",
                    },
                },
                {"type": "text", "text": "Image 2:"},
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Iridescent.green.sweat.bee1.jpg",
                    },
                },
                {"type": "text", "text": "How are these images different?"},
            ],
        }
    ],
)
```

---

## Limitations

While Claude's image understanding capabilities are cutting-edge, there are some limitations to be aware of:

- **People identification**: Claude cannot be used to name people in images and refuses to do so.
- **Accuracy**: Claude may hallucinate or make mistakes when interpreting low-quality, rotated, or very small images under 200 pixels.
- **Spatial reasoning**: Claude's spatial reasoning abilities are limited. It may struggle with tasks requiring precise localization or layouts, like reading an analog clock face or describing exact positions of chess pieces.
- **Counting**: Claude can give approximate counts of objects in an image but may not always be precisely accurate, especially with large numbers of small objects.
- **AI generated images**: Claude does not know if an image is AI-generated and may be incorrect if asked.
- **Inappropriate content**: Claude does not process inappropriate or explicit images that violate the Acceptable Use Policy.
- **Healthcare applications**: Claude's outputs should not be considered a substitute for professional medical advice or diagnosis.

---

## FAQ

**What image file types does Claude support?**

Claude currently supports JPEG, PNG, GIF, and WebP image formats.

**Can Claude read image URLs?**

Yes, Claude can process images from URLs with URL image source blocks in the API.

**Is there a limit to the image file size I can upload?**

Yes:
- API: Maximum 5 MB per image
- claude.ai: Maximum 10 MB per image

**How many images can I include in one request?**

- Messages API: Up to 600 images per request (100 for models with a 200k-token context window)
- claude.ai: Up to 20 images per turn

**Can Claude generate or edit images?**

No, Claude is an image understanding model only. It can interpret and analyze images, but it cannot generate, produce, edit, manipulate, or create images.
