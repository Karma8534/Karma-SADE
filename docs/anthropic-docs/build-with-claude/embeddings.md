---
source: https://platform.claude.com/docs/en/build-with-claude/embeddings
scraped: 2026-03-23
section: build-with-claude
---

# Embeddings

Text embeddings are numerical representations of text that enable measuring semantic similarity. This guide introduces embeddings, their applications, and how to use embedding models for tasks like search, recommendations, and anomaly detection.

---

## Before implementing embeddings

When selecting an embeddings provider, there are several factors you can consider depending on your needs and preferences:

- Dataset size & domain specificity: size of the model training dataset and its relevance to the domain you want to embed. Larger or more domain-specific data generally produces better in-domain embeddings
- Inference performance: embedding lookup speed and end-to-end latency. This is a particularly important consideration for large scale production deployments
- Customization: options for continued training on private data, or specialization of models for very specific domains.

## How to get embeddings with Anthropic

Anthropic does not offer its own embedding model. One embeddings provider that has a wide variety of options and capabilities encompassing all of the above considerations is Voyage AI.

Voyage AI makes state-of-the-art embedding models and offers customized models for specific industry domains such as finance and healthcare, or bespoke fine-tuned models for individual customers.

The rest of this guide is for Voyage AI, but you should assess a variety of embeddings vendors to find the best fit for your specific use case.

## Available Models

Voyage recommends using the following text embedding models:

| Model | Context Length | Embedding Dimension | Description |
| --- | --- | --- | --- |
| `voyage-3-large` | 32,000 | 1024 (default), 256, 512, 2048 | The best general-purpose and multilingual retrieval quality. |
| `voyage-3.5` | 32,000 | 1024 (default), 256, 512, 2048 | Optimized for general-purpose and multilingual retrieval quality. |
| `voyage-3.5-lite` | 32,000 | 1024 (default), 256, 512, 2048 | Optimized for latency and cost. |
| `voyage-code-3` | 32,000 | 1024 (default), 256, 512, 2048 | Optimized for **code** retrieval. |
| `voyage-finance-2` | 32,000 | 1024 | Optimized for **finance** retrieval and RAG. |
| `voyage-law-2` | 16,000 | 1024 | Optimized for **legal** and **long-context** retrieval and RAG. |

Additionally, the following multimodal embedding models are recommended:

| Model | Context Length | Embedding Dimension | Description |
| --- | --- | --- | --- |
| `voyage-multimodal-3` | 32000 | 1024 | Rich multimodal embedding model that can vectorize interleaved text and content-rich images. |

## Getting started with Voyage AI

To access Voyage embeddings:

1. Sign up on Voyage AI's website
2. Obtain an API key
3. Set the API key as an environment variable for convenience:

```bash
export VOYAGE_API_KEY="<your secret key>"
```

### Voyage Python library

```bash
pip install -U voyageai
```

```python
import voyageai

vo = voyageai.Client()
# This will automatically use the environment variable VOYAGE_API_KEY.

texts = ["Sample text 1", "Sample text 2"]

result = vo.embed(texts, model="voyage-3.5", input_type="document")
print(result.embeddings[0])
print(result.embeddings[1])
```

`result.embeddings` will be a list of two embedding vectors, each containing 1024 floating-point numbers.

### Voyage HTTP API

```bash
curl https://api.voyageai.com/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $VOYAGE_API_KEY" \
  -d '{
    "input": ["Sample text 1", "Sample text 2"],
    "model": "voyage-3.5"
  }'
```

The response is a JSON object containing the embeddings and the token usage.

## Quickstart example

The following brief example shows how to use embeddings.

```python
import voyageai
import numpy as np

documents = [
    "The Mediterranean diet emphasizes fish, olive oil, and vegetables, believed to reduce chronic diseases.",
    "Photosynthesis in plants converts light energy into glucose and produces essential oxygen.",
    "20th-century innovations, from radios to smartphones, centered on electronic advancements.",
    "Rivers provide water, irrigation, and habitat for aquatic species, vital for ecosystems.",
    "Apple's conference call to discuss fourth fiscal quarter results and business updates is scheduled for Thursday, November 2, 2023 at 2:00 p.m. PT / 5:00 p.m. ET.",
    "Shakespeare's works, like 'Hamlet' and 'A Midsummer Night's Dream,' endure in literature.",
]

vo = voyageai.Client()

# Embed the documents
doc_embds = vo.embed(documents, model="voyage-3.5", input_type="document").embeddings

query = "When is Apple's conference call scheduled?"

# Embed the query
query_embd = vo.embed([query], model="voyage-3.5", input_type="query").embeddings[0]

# Compute the similarity
# Voyage embeddings are normalized to length 1, therefore dot-product
# and cosine similarity are the same.
similarities = np.dot(doc_embds, query_embd)

retrieved_id = np.argmax(similarities)
print(documents[retrieved_id])
```

Note that `input_type="document"` and `input_type="query"` are used for embedding the document and query, respectively.

The output would be the 5th document, which is indeed the most relevant to the query:

```
Apple's conference call to discuss fourth fiscal quarter results and business updates is scheduled for Thursday, November 2, 2023 at 2:00 p.m. PT / 5:00 p.m. ET.
```

## FAQ

**Why do Voyage embeddings have superior quality?**

Embedding models rely on powerful neural networks to capture and compress semantic context, similar to generative models. Voyage's team of experienced AI researchers optimizes every component of the embedding process, including model architecture, data collection, loss functions, and optimizer selection.

**What embedding models are available and which should I use?**

For general-purpose embedding, the recommended models are:
- `voyage-3-large`: Best quality
- `voyage-3.5-lite`: Lowest latency and cost
- `voyage-3.5`: Balanced performance with superior retrieval quality at a competitive price point

Domain-specific models:
- Legal tasks: `voyage-law-2`
- Code and programming documentation: `voyage-code-3`
- Finance-related tasks: `voyage-finance-2`

**Which similarity function should I use?**

Voyage AI embeddings are normalized to length 1, which means that:
- Cosine similarity is equivalent to dot-product similarity, while the latter can be computed more quickly.
- Cosine similarity and Euclidean distance will result in the identical rankings.

**When and how should I use the input_type parameter?**

For all retrieval tasks and use cases (for example, RAG), use the `input_type` parameter to specify whether the input text is a query or document. Specifying whether input text is a query or document can create better dense vector representations for retrieval, which can lead to better retrieval quality.

## Pricing

Visit Voyage's pricing page for the most up to date pricing details.
