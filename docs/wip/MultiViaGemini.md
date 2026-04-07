# MultiViaGemini

*Converted from: MultiViaGemini.PDF*



---
*Page 1*


Open in app
11
Search Write
Towards AI
Member-only story
Multimodal RAG +
Gemini Embedding 2 +
GPT-5.4 Just
Revolutionized AI
Forever
⾼達烈
Gao Dalie ( ) Follow 13 min read · Mar 19, 2026
166 1


---
*Page 2*


During the weekend, I scrolled through Twitter to
see what was happening in the AI community.
Google has announced its first native multimodal
embedding model, Gemini Embedding 2, as a
public preview. It is Google’s first native
multimodal embedding model that can integrate
text, images, videos, audio, and PDFs into a single
vector space.
Traditional multimodal search systems typically
use a two-step pipeline: first converting images to
text, and then passing them to a text embedding
model.


---
*Page 3*


What does this mean? Simply put, in the past, if a
company wanted to build a system that supported
“text + image” retrieval, it had to use multiple
models to generate vectors separately and then
spend a lot of effort on integration and alignment.
Now, with Gemini Embedding 2, only one model is
needed to handle semantic understanding and
retrieval for all modalities. Whether it’s RAG,
semantic search, recommendation systems, or
data clustering, it can all be done under a unified
framework, greatly simplifying the architecture of
multimodal AI systems.
OpenAI has just announced its long-awaited new
flagship model, the ” GPT-5.4" series!
This update goes beyond mere “performance
improvements” and represents a decisive evolution
in the ” agent function”, where AI thinks for itself,
uses tools effectively, and completes complex
tasks.


---
*Page 4*


According to OpenAI’s documentation, the
previous frontier model for APIs was GPT-5.2, and
the main daily-use version for ChatGPT is GPT-5.3
Instant. GPT-5.4 is presented as a higher-end
model that enhances coding, document
comprehension, tool usage, long-running tasks,
and multi-source searches.
Therefore, the essence of GPT-5.4 is not that “it
dramatically changes for every question,” but
rather that the difference is more likely to appear
in “tasks with many intermediate steps,” such as
research, document creation, coding, and
organizing long texts.
So, let me give you a quick demo of the live chatbot
to show you how everything works.


---
*Page 5*


I will upload a PDF that contains a table, image,
text, and charts, and I will ask the question “How
many visitors export to Morocco?”
If you see how the chatbot generates output, you’ll
see that the agent iterates through every page,
extracting the raw text and rendering a high-
resolution PNG image of that page simultaneously
— this dual extraction is critical because PDFs
often contain tables, diagrams, and visual layouts
where meaning lives in structure rather than text
alone.


---
*Page 6*


Both the text and the image are then passed
together as a multimodal input to Gemini
Embedding 2, which is Google’s latest multimodal
embedding model capable of ingesting mixed text-
and-image content and compressing it into a single
dense vector of 1536 floating-point numbers —
This vector is essentially a semantic fingerprint of
the entire page, capturing not just what words
appear but how the page looks visually, making it
far more powerful than text-only embeddings for
document understanding.
Each page vector is stored in ChromaDB on disk
under a unique ID, organized using an HNSW
graph index for fast approximate nearest-
neighbour search.
When you ask a question, that question text is also
passed to Gemini Embedding 2, but this time with
the task type RETRIEVAL_QUERY instead of
RETRIEVAL_DOCUMENT


---
*Page 7*


As Gemini trains query and document embeddings
in slightly different spaces to maximise retrieval
precision, the resulting query vector is compared
against all stored page vectors using cosine
distance, returning the 5 most semantically similar
pages.
The text content of those 5 pages is then assembled
into a structured context block and sent to GPT-5.4,
along with a system prompt instructing it to
answer strictly from the provided manual content
and cite page numbers
What makes Gemini Embedding 2
Unique?
Gemini Embedding 2 is based on the Gemini
architecture and converts text, image, video,
audio, and PDF modalities into a unified vector
representation in a semantic space by passing
them through a common encoder.


---
*Page 8*


In other words, “an image of a cat” and “text about
a cat” are mapped to nearby locations in the same
space, enabling cross-modality searching and
classification.
Furthermore, it natively supports interleaved input
from multiple modalities (for example, passing
images and text simultaneously), allowing it to
capture complex relationships between modalities.
For PDFs, it performs OCR (Optical Character
Recognition) internally, and audio tracks included
in videos are automatically extracted and
embedded.
The output dimension is controlled using a
technique called Matryoshka Representation
Learning, which is a method that learns to
aggregate the most important semantic
information into the first dimension of a 3,072-
dimensional vector. It’s like a Russian Matryoshka


---
*Page 9*


doll, where lower-dimensional vectors are nested
inside higher-dimensional vectors.
By utilising this characteristic, a two-stage search
architecture can be realised that screens large
amounts of data using coarse, low-dimensional
vectors, and then re-ranks the top candidates
using precise, high-dimensional vectors.
What makes GPT-5.4 unique?
The GPT-5 series employs a Sparse Mixture-of-
Experts (Sparse MoE) architecture. This
mechanism maintains a vast number of
parameters across the entire model, while
selectively activating only the most relevant
“expert” submodels for each query.
For coding questions, experts specializing in code
generation are dynamically routed, and for image-
related questions, visual inference experts are
dynamically routed, eliminating the need to


---
*Page 10*


activate all parameters every time, thus achieving
both high accuracy and efficiency.
The attention mechanism utilises both Group
Query Attention (GQA) and sliding window
attention, enabling efficient processing of
inference for extremely long contexts of up to 1.05
million tokens.
Furthermore, GPT-5.4 introduces a new
mechanism called Tool Search. Previously, all tool
definitions had to be preloaded when an API call
was made, but with Tool Search, only a lightweight
list of tools is accepted, and the full definitions are
referenced on demand as needed. In tests with 250
tasks using 36 MCP servers, token consumption
was reduced by 47% while maintaining accuracy.
Let’s start coding :
Ingest file :
I created this script to build the ingestion pipeline
for my RAG system, where I process a PDF manual


---
*Page 11*


once and store embeddings in Chroma so the
agent can search it later.
Then I set up a persistent Chroma database and
created a collection that uses cosine similarity,
because I want vector search to compare
embeddings efficiently. After that, I open the PDF
using PyMuPDF and loop through every page,
since my strategy is to generate one embedding
per page instead of splitting the text into chunks.
For each page, I extract the text and also render
the page as an image, because I want the
embedding to understand both the written content
and the visual layout. I save the rendered image to
a cache folder, read it as bytes, and then I combine
the text and the image into a single multimodal
request using the Gemini embedding model,
which produces a 1536-dimensional vector that
represents the full page.


---
*Page 12*


As I generate each embedding, I store the page ID,
metadata, text snippet, and vector in lists, so I can
insert everything into Chroma later. Once all pages
are processed, I upsert the vectors into the
database in small batches to avoid memory issues
and keep the ingestion stable.
"""
ingest.py — One-time script to process the PDF manual
Strategy: For each page, we combine the extracted tex
into a single multimodal embedding using gemini-embed
This produces one rich 1536-dim vector per page that
Usage: python ingest.py
"""
import os
from pathlib import Path
import chromadb
import fitz # PyMuPDF
from dotenv import load_dotenv
from google import genai
from google.genai import types
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PDF_PATH = os.getenv("PDF_PATH", "manual/Documents/do


---
*Page 13*


CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "man
PAGES_CACHE_DIR = Path("pages_cache")
EMBED_MODEL = "gemini-embedding-2-preview"
EMBED_DIM = 1536
def embed_page(client: genai.Client, page_text: str,
"""
Create a multimodal embedding for a single PDF pa
Combines text + image into one aggregated vector
"""
parts = []
if page_text.strip():
parts.append(types.Part(text=page_text))
parts.append(types.Part.from_bytes(data=image_byt
result = client.models.embed_content(
model=EMBED_MODEL,
contents=[types.Content(parts=parts)],
config=types.EmbedContentConfig(
task_type="RETRIEVAL_DOCUMENT",
output_dimensionality=EMBED_DIM,
),
)
return result.embeddings[0].values
def main():
PAGES_CACHE_DIR.mkdir(exist_ok=True)
google_client = genai.Client(api_key=GOOGLE_API_K
chroma_client = chromadb.PersistentClient(path=CH


---
*Page 14*


collection = setup_chroma_collection(chroma_clien
pdf_path = Path(PDF_PATH)
if not pdf_path.exists():
raise FileNotFoundError(f"PDF not found at: {
doc = fitz.open(str(pdf_path))
total_pages = len(doc)
print(f"\nProcessing '{pdf_path.name}' — {total_p
ids = []
embeddings = []
metadatas = []
documents = []
for i, page in enumerate(doc):
page_num = i + 1
print(f" Page {page_num}/{total_pages}...",
page_text = page.get_text()
mat = fitz.Matrix(2.0, 2.0)
pix = page.get_pixmap(matrix=mat)
image_path = PAGES_CACHE_DIR / f"page_{page_n
pix.save(str(image_path))
with open(image_path, "rb") as f:
image_bytes = f.read()
embedding = embed_page(google_client, page_te
ids.append(f"page-{page_num}")
embeddings.append(embedding)
metadatas.append({
"page_number": page_num,


---
*Page 15*


"image_path": str(image_path),
"pdf_name": pdf_path.name,
})
documents.append(page_text[:800]) # Chroma's
print(f"✓ embedded ({len(embedding)} dims)")
doc.close()
# Upsert to Chroma in batches of 10
print(f"\nUpserting {len(ids)} vectors to Chroma.
batch_size = 10
for start in range(0, len(ids), batch_size):
end = start + batch_size
collection.upsert(
ids=ids[start:end],
embeddings=embeddings[start:end],
metadatas=metadatas[start:end],
documents=documents[start:end],
)
print("Done! All pages ingested into Chroma.")
print(f"Chroma DB path: {Path(CHROMA_PATH).resolv
print(f"Page images saved in: {PAGES_CACHE_DIR.re
if __name__ == "__main__":
main()
Rag file :
I developed this file to handle the full RAG query
pipeline, which means this is the part that runs


---
*Page 16*


every time the user asks a question.
Then I created a helper function to initialize the
Google client, the OpenAI client, and the Chroma
collection only once, because I don’t want to
reconnect to the database or APIs every time a
query runs.
After that, I built the main function that takes the
user’s question and runs the full retrieval-
augmented generation flow. I start by embedding
the question using the Gemini embedding model,
but this time I use the retrieval query mode, since
the vector needs to match the document
embeddings that I created earlier during ingestion.
Once I get the query vector, I search the Chroma
collection to find the most similar pages, and I
request the metadata, distances, and stored text
snippets so I can build context for the model. If
nothing is found, I return a safe message saying
the manual does not contain relevant information.


---
*Page 17*


When results exist, I combine the matched pages
into one context string, and I include the page
numbers so the model knows where the
information came from. Then I send that context
to the generation model, which I configured to act
like a manual assistant, forcing it to answer only
from the provided pages, keep the response clear,
and include page references.
"""
rag.py — RAG query functions: embed question → searc
"""
import os
from typing import Dict, List, Optional, Tuple
import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "man
EMBED_MODEL = "gemini-embedding-2-preview"


---
*Page 18*


GEN_MODEL = "gpt-5.4"
EMBED_DIM = 1536
_google_client: Optional[genai.Client] = None
_openai_client: Optional[OpenAI] = None
_chroma_collection = None
def query_rag(question: str, top_k: int = 5) -> Tuple
"""
Full RAG pipeline:
1. Embed the user question with gemini-embedding-
2. Search Chroma for top_k similar page vectors
3. Build context from matched pages
4. Generate answer with GPT-4o
5. Return (answer_text, sources_list)
"""
google_client, openai_client, collection = _get_c
# 1. Embed question
embed_result = google_client.models.embed_content
model=EMBED_MODEL,
contents=question,
config=types.EmbedContentConfig(
task_type="RETRIEVAL_QUERY",
output_dimensionality=EMBED_DIM,
),
)
query_vector = embed_result.embeddings[0].values
# 2. Search Chroma
results = collection.query(
query_embeddings=[query_vector],
n_results=top_k,
include=["metadatas", "distances", "documents


---
*Page 19*


)
metadatas = results["metadatas"][0]
distances = results["distances"][0]
if not metadatas:
return "I couldn't find relevant information
# 3. Build context
context_parts = []
for meta, doc in zip(metadatas, results["document
context_parts.append(f"[Page {meta.get('page_
context = "\n\n---\n\n".join(context_parts)
# 4. Generate answer
response = openai_client.chat.completions.create(
model=GEN_MODEL,
messages=[
{
"role": "system",
"content": (
"You are a helpful Manual Assista
"based ONLY on the provided manua
"Use numbered steps when explaini
"Mention relevant page numbers in
),
},
{
"role": "user",
"content": f"Manual content:\n{contex
},
],
)
answer = response.choices[0].message.content


---
*Page 20*


# 5. Build sources — convert cosine distance to s
sources = []
for meta, dist, doc in zip(metadatas, distances,
sources.append({
"page_number": int(meta.get("page_number"
"score": round((1 - dist) * 100, 1),
"text_snippet": doc[:350],
"image_path": meta.get("image_path", ""),
})
return answer, sources
app.py
I built this file to create the full user interface for
the manual RAG assistant using Streamlit, because
I wanted a clean web app where I can upload a
PDF, index it, and ask questions in a chat. First, I
set up environment variables so the app can read
the API keys, the Chroma database path, and the
collection name without hard-coding them.
Then I configured the Streamlit layout and added
custom CSS to give the app a cleaner design with
styled chat bubbles and fonts so it feels like a real
product.


---
*Page 21*


After that, I created a helper function to run the
ingestion process inside the app, so when I upload
a PDF, the code reads it from memory, extracts the
text, renders each page as an image, and generates
one multimodal embedding per page while
showing a progress bar. Once the embeddings are
ready, I store them in Chroma in batches to keep
the indexing stable.
Next, I built the sidebar to upload the PDF, start
indexing, and clear the chat, so the workflow is
simple: upload, index, then ask questions. In the
main area, I made a chat interface that keeps the
conversation in session state, and every time I ask
a question, the app calls the RAG function to
search Chroma and generate an answer from the
manual.
"""
app.py — Streamlit UI for manual RAG assistant with P
"""
import os
from pathlib import Path


---
*Page 22*


import chromadb
import fitz
import streamlit as st
from dotenv import load_dotenv
from google import genai
from ingest import embed_page, setup_chroma_collectio
from rag import query_rag
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "man
PAGES_CACHE_DIR = Path("pages_cache")
# ── Page config ──────────────────────────────
st.set_page_config(page_title="Manual AI", page_icon=
# ── Custom CSS ───────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family
html, body, [class*="css"] {
font-family: 'DM Sans', sans-serif;
background-color: #faf9f7;
color: #1a1a1a;
}
header[data-testid="stHeader"] { background: transpar
#MainMenu, footer { visibility: hidden; }
.block-container {


---
*Page 23*


padding: 2rem 3rem 4rem 3rem;
max-width: 1100px;
}
h1 {
font-family: 'DM Serif Display', serif !important
font-size: 2.6rem !important;
color: #1a1a1a !important;
letter-spacing: -0.02em;
margin-bottom: 0 !important;
}
section[data-testid="stSidebar"] {
background-color: #f2f0ec !important;
border-right: 1px solid #e0ddd8 !important;
}
[data-testid="stFileUploader"] {
background: #ffffff;
border: 1.5px dashed #c8b89a;
border-radius: 12px;
padding: 1rem;
transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover { border-color:
.stButton > button {
background: #2e2e2e !important;
color: #faf9f7 !important;
border: none !important;
border-radius: 8px !important;
font-family: 'DM Mono', monospace !important;
font-size: 0.85rem !important;
font-weight: 500 !important;
padding: 0.5rem 1.4rem !important;


---
*Page 24*


transition: background 0.2s, transform 0.1s !impo
}
.stButton > button:hover {
background: #111 !important;
transform: translateY(-1px);
}
[data-testid="stChatMessage"] {
background: #ffffff !important;
border: 1px solid #e8e5e0 !important;
border-radius: 12px !important;
margin-bottom: 0.75rem !important;
padding: 1rem 1.25rem !important;
}
[data-testid="stChatInput"] textarea {
background: #ffffff !important;
border: 1.5px solid #d8d4ce !important;
border-radius: 10px !important;
color: #1a1a1a !important;
font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
border-color: #9a7a52 !important;
box-shadow: 0 0 0 2px rgba(154,122,82,0.15) !impo
}
[data-testid="stExpander"] {
background: #ffffff !important;
border: 1px solid #e8e5e0 !important;
border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
font-family: 'DM Mono', monospace;
font-size: 0.8rem;


---
*Page 25*


color: #666 !important;
}
.score-badge {
display: inline-block;
background: #eaf4ea;
color: #2e7d32;
font-family: 'DM Mono', monospace;
font-size: 0.75rem;
padding: 2px 8px;
border-radius: 4px;
margin-left: 8px;
}
hr { border-color: #e8e5e0 !important; }
.stCaption, small { color: #888 !important; }
</style>
""", unsafe_allow_html=True)
# ── Ingest helper ─────────────────────────────
def ingest_pdf(pdf_bytes: bytes, pdf_name: str, progr
PAGES_CACHE_DIR.mkdir(exist_ok=True)
google_client = genai.Client(api_key=GOOGLE_API_K
chroma_client = chromadb.PersistentClient(path=CH
collection = setup_chroma_collection(chroma_clien
doc = fitz.open(stream=pdf_bytes, filetype="pdf")
total = len(doc)
ids, embeddings, metadatas, documents = [], [], [
for i, page in enumerate(doc):
page_num = i + 1
progress_bar.progress(page_num / total, text=


---
*Page 26*


page_text = page.get_text()
mat = fitz.Matrix(2.0, 2.0)
pix = page.get_pixmap(matrix=mat)
image_path = PAGES_CACHE_DIR / f"page_{page_n
pix.save(str(image_path))
with open(image_path, "rb") as f:
image_bytes = f.read()
embedding = embed_page(google_client, page_te
ids.append(f"page-{page_num}")
embeddings.append(embedding)
metadatas.append({
"page_number": page_num,
"image_path": str(image_path),
"pdf_name": pdf_name,
})
documents.append(page_text[:800])
doc.close()
batch_size = 10
for start in range(0, len(ids), batch_size):
end = start + batch_size
collection.upsert(
ids=ids[start:end],
embeddings=embeddings[start:end],
metadatas=metadatas[start:end],
documents=documents[start:end],
)
return total


---
*Page 27*


# ── Sidebar ──────────────────────────────────
with st.sidebar:
📄
st.markdown("## Load Manual")
st.caption("Upload a PDF to index it, then ask qu
uploaded = st.file_uploader("Drop a PDF here", ty
if uploaded:
st.markdown(f"**{uploaded.name}** \n`{round(
⚡
if st.button(" Index PDF"):
try:
uploaded.seek(0)
bar = st.progress(0, text="Starting…"
bar.empty()
st.success(f"✓ Indexed {total_pages}
st.session_state.pdf_loaded = True
st.session_state.pdf_name = uploaded.
except Exception as e:
st.error(f"Ingest failed: {e}")
raise e
st.divider()
🗑
if st.button(" Clear chat"):
st.session_state.messages = []
st.markdown("<br>", unsafe_allow_html=True)
st.caption("Embeddings: Gemini multimodal \nGene
# ── Main ────────────────────────────────────
st.markdown("# Manual AI")
if "pdf_name" in st.session_state:


---
*Page 28*


st.caption(f"Loaded: `{st.session_state.pdf_name}
else:
st.caption("Upload a PDF in the sidebar to get st
st.divider()
if "messages" not in st.session_state:
st.session_state.messages = []
for msg in st.session_state.messages:
with st.chat_message(msg["role"]):
st.markdown(msg["content"])
if prompt := st.chat_input("Ask anything about the ma
if "pdf_loaded" not in st.session_state:
st.warning("Please upload and index a PDF fir
else:
st.session_state.messages.append({"role": "us
with st.chat_message("user"):
st.markdown(prompt)
with st.chat_message("assistant"):
with st.spinner("Searching…"):
answer, sources = query_rag(prompt)
st.markdown(answer)
if sources:
📎
with st.expander(f" {len(sources)}
for s in sources:
st.markdown(
f"**Page {s['page_number'
f'<span class="score-badg
unsafe_allow_html=True,
)


---
*Page 29*


st.caption(s["text_snippet"])
st.divider()
st.session_state.messages.append({"role": "as
Conclusion :
This is not just another “AI drawing” gimmick. The
value of Gemini Embedding 2 and GPT-4.5 lies in
the way they allow AI to truly “see the world,” just
like humans — not by breaking it down into parts,
but by understanding it as a whole.
In the future, we are moving from an era where we
ask questions to chatbots to an era where AI
actually reads documents, creates tables, runs
browsers, and works across multiple applications.
If you deal with large amounts of unstructured
data every day — images, videos, audio, and
documents all mixed together — then this tool is
not a “bonus,” but a “must-have.”


---
*Page 30*


󰩃
I am an AI Generative expert! If you want to
collaborate on a project, drop an inquiry here or
book a 1-on-1 Consulting Call With Me.
The New Nano Banana 2 + OCR + Claude
C d P f l AI OCR PDF Edit
Yesterday, when I was trying to draw an
ill t ti th t I ll i t i t t
pub.towardsai.net
I Studied OpenClaw Memory System —
H ’ Wh t I F d
Over the past year, almost all AI products
h b t lki b t d
generativeai.pub
RLM + Graph: The Ultimate Evolution of AI?
R i L M d l G h
Not long ago, I shared a video about
R i L M d l d f
pub.towardsai.net
Data Science Artificial Intelligence Machine Learning
Technology Programming


---
*Page 31*


Published in Towards AI
Following
119K followers · Last published 4 hours ago
We build Enterprise AI. We teach what we learn. Join
100K+ AI practitioners on Towards AI Academy. Free:
6-day Agentic AI Engineering Email Guide:
https://email-course.towardsai.net/
⾼達烈
Written by Gao Dalie ( )
Follow
9.3K followers · 1 following
NC State Uni (Research Assistant), Learn AI Agent,
LLMs, RAG & Generative AI. See everything I have to
offer at the link below: https://linktr.ee/GaoDalie_AI
Responses (1)
To respond to this story,
get the free Medium app.
Tiffany Meyers
Mar 19
Nice overview!
3 1 reply


---
*Page 32*


⾼達烈
More from Gao Dalie ( ) and Towards
AI
In by ⾼ In by
Generativ… Gao Dalie ( … Towards AI Shreyas Naphad
I Studied OpenClaw If You Understand
M S t Th 5 AI T
Over the past year, almost all Master the core ideas behind
AI d t h b t lki AI ith t tti l t
Mar 16 5d ago
In by In by ⾼達
Towards AI Alpha Iterations Towards … Gao Dalie ( …
Agentic AI Project: PaddleOCR + hybrid
B ild C t t i l + R k
End to end implementation of In 2026, Generative AI will
A ti AI b d t h d it “ i ” t


---
*Page 33*


Mar 26 Jan 3
⾼達烈
See all from Gao Dalie ( ) See all from Towards AI
Recommended from Medium
In by In by
Towards AI Alpha Iterations Data Science C… Santosh S…
Agentic AI Project: Building a Production
B ild C t AI V i A t
End to end implementation of A deep-dive into real-time
A ti AI b d t di i i t l h
Mar 26 Mar 18


---
*Page 34*


In by In by
AI Exploration Jo… Florian J… Graph P… Alexander Shere…
dots.ocr: Turning Building Knowledge
D t P i i t G h ith L l
At first glance, document For the production GraphRAG
i i ht l k lik OCR i li th t ti t i
Mar 25 Mar 23
In by Steve Hedden
Generativ… Gaurav Shriva…
Open Knowledge
I Threw Out My Vector
G h A S h
D t b RAG G t
A daily-refreshed catalog of
Here’s what happens when
k l d h
l t LLM i t
Mar 24 Mar 16
See more recommendations