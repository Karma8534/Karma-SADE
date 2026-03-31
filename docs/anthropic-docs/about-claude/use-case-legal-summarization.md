---
source: https://platform.claude.com/docs/en/about-claude/use-case-guides/legal-summarization
scraped: 2026-03-23
---

# Legal summarization

This guide walks through how to leverage Claude's advanced natural language processing capabilities to efficiently summarize legal documents, extracting key information and expediting legal research.

---

> Visit the [summarization cookbook](https://platform.claude.com/cookbook/capabilities-summarization-guide) to see an example legal summarization implementation using Claude.

## Before building with Claude

### Decide whether to use Claude for legal summarization

Key indicators:
- **High volume of documents to review efficiently**: Claude processes and summarizes vast amounts of legal documents rapidly, reducing time and cost of document review
- **Automated extraction of key metadata**: Extract and categorize parties involved, dates, contract terms, or specific clauses
- **Generate clear, concise, standardized summaries**: Follow predetermined formats for consistency
- **Precise citations required**: Claude includes accurate citations for all referenced legal points
- **Expedite legal research**: Quickly analyze large volumes of case law, statutes, and legal commentary

### Determine the details you want to extract

Without clear direction, it's difficult for Claude to determine which details to include. Example for a sublease agreement:

```python
details_to_extract = [
    "Parties involved (sublessor, sublessee, and original lessor)",
    "Property details (address, description, and permitted use)",
    "Term and rent (start date, end date, monthly rent, and security deposit)",
    "Responsibilities (utilities, maintenance, and repairs)",
    "Consent and notices (landlord's consent, and notice requirements)",
    "Special provisions (furniture, parking, and subletting restrictions)",
]
```

### Establish success criteria

Metrics for evaluating legal summarization quality:
- **Factual correctness**: Accurately represent facts, legal concepts, and key points
- **Legal precision**: Correct terminology and references to statutes, case law, or regulations
- **Conciseness**: Condense to essential points without losing important details
- **Consistency**: Maintain consistent structure and approach across multiple documents
- **Readability**: Clear and easy to understand for the intended audience
- **Bias and fairness**: Unbiased depiction of legal arguments and positions

---

## How to summarize legal documents using Claude

### Select the right Claude model

Model accuracy is extremely important for legal summarization. Claude Opus 4.6 is excellent for high-accuracy use cases. For large document volumes where cost is a concern, Claude Haiku 4.5 is a viable alternative.

Cost estimate for summarizing 1,000 sublease agreements:
- **Claude Opus 4.6**: ~$438.75 total
- **Claude Haiku 3**: ~$21.96 total

### Transform documents into a format Claude can process

```python
from io import BytesIO
import re
import pypdf
import requests

def get_llm_text(pdf_file):
    reader = pypdf.PdfReader(pdf_file)
    text = "\n".join([page.extract_text() for page in reader.pages])
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove page numbers
    text = re.sub(r"\n\s*\d+\s*\n", "\n", text)
    return text
```

### Build a strong prompt

```python
import anthropic

client = anthropic.Anthropic()

def summarize_document(text, details_to_extract, model="claude-opus-4-6", max_tokens=1000):
    details_to_extract_str = "\n".join(details_to_extract)

    prompt = f"""Summarize the following sublease agreement. Focus on these key aspects:

    {details_to_extract_str}

    Provide the summary in bullet points nested within the XML header for each section. For example:

    <parties involved>
    - Sublessor: [Name]
    // Add more details as needed
    </parties involved>

    If any information is not explicitly stated in the document, note it as "Not specified". Do not preamble.

    Sublease agreement text:
    {text}
    """

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system="You are a legal analyst specializing in real estate law, known for highly accurate and detailed summaries of sublease agreements.",
        messages=[
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "Here is the summary of the sublease agreement: <summary>"},
        ],
        stop_sequences=["</summary>"],
    )

    return response.content[0].text
```

The XML tag structure allows parsing each section individually as a post-processing step.

### Evaluate your prompt

Metrics for evaluating summary quality:
- **ROUGE scores**: Overlap between generated and reference summary (recall-focused)
- **BLEU scores**: Precision of n-gram matches between generated and reference summaries
- **Contextual embedding similarity**: Cosine similarity between vector representations
- **LLM-based grading**: Use Claude to evaluate against a scoring rubric
- **Human evaluation**: Legal experts review sample summaries as a sanity check

### Deploy your prompt

Key considerations for production:
1. **Ensure no liability**: Provide disclaimers that summaries are AI-generated and should be reviewed by legal professionals
2. **Handle diverse document types**: Ensure your pipeline can handle PDFs, Word documents, text files, etc.
3. **Parallelize API calls**: Send API calls in parallel for large document collections; respect rate limits

---

## Improve performance

### Perform meta-summarization to handle long documents

For documents exceeding Claude's context window:

```python
def chunk_text(text, chunk_size=20000):
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

def summarize_long_document(text, details_to_extract, model="claude-opus-4-6", max_tokens=1000):
    # Summarize each chunk individually
    chunk_summaries = [
        summarize_document(chunk, details_to_extract, model=model, max_tokens=max_tokens)
        for chunk in chunk_text(text)
    ]

    # Combine chunk summaries into a final meta-summary
    final_summary_prompt = f"""
    You are looking at the chunked summaries of multiple documents that are all related.
    Combine the following summaries into a coherent overall summary:

    <chunked_summaries>
    {"".join(chunk_summaries)}
    </chunked_summaries>

    Focus on these key aspects:
    {"\n".join(details_to_extract)}
    ...
    """
    # Send to Claude for final summarization
```

### Use summary indexed documents for large document collections

Summary indexed documents is an advanced RAG approach:
1. Use Claude to generate a concise summary for each document in your corpus
2. Use Claude to rank the relevance of each summary to the query being asked
3. Retrieve and use the most relevant documents for response generation

This provides more efficient ranking than traditional RAG, using less context.

### Fine-tune Claude to learn from your dataset

Fine-tuning process:
1. **Identify errors**: Collect instances where Claude's summaries fall short
2. **Curate a dataset**: Compile problematic examples with corrected summaries
3. **Perform fine-tuning**: Retrain the model on your curated dataset
4. **Iterative improvement**: Continuously add new examples where the model underperforms

> **Tip:** Fine-tuning is currently only available via Amazon Bedrock.
