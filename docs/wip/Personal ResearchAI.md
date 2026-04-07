# Personal ResearchAI

*Converted from: Personal ResearchAI.pdf*



---
*Page 1*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
Open in app
2
Search Write
Towards AI
How I Built a Personal AI Research
Assistant Using LLMs to Organize
My Daily Academic Work
Amar Chetri, PhD Follow 9 min read · Feb 24, 2026
58
https://medium.com/p/e9c1176814dc 1/20


---
*Page 2*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
The journey from information overload to streamlined research.
As a graduate student, my daily life is a constant battle against information
overload. Between reading papers, drafting proposals, managing citations,
and keeping up with the latest preprints, my browser tabs multiply like
rabbits. For years, I felt like I was spending more time organizing my
research than actually doing it. I needed a solution — something that could
understand the context of my work, help me filter the noise, and act as a true
cognitive partner.
This is the story of how I built a Personal AI Research Assistant using Large
Language Models (LLMs). It wasn’t about replacing my thinking, but
augmenting it. This system, which I call “Hermes” (after the messenger of
the gods), now handles the grunt work of academic processing, allowing me
to focus on creativity and analysis.
https://medium.com/p/e9c1176814dc 2/20


---
*Page 3*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
In this article, I’ll walk you through the architecture, the tools, the code, and
the thought process behind building your own AI research assistant.
Table of Contents
1. The Problem: The Firehose of Academia
2. The Vision: What I Wanted Hermes to Do
3. The Tech Stack: Choosing the Right Tools
4. Phase 1: The Knowledge Base — My Digital Brain
5. Phase 2: The Ingestion Pipeline — Feeding the Brain
6. Phase 3: The RAG System — How Hermes “Thinks”
7. Phase 4: The Interface — Talking to Hermes
8. Overcoming Challenges & Future Work
9. Conclusion: The New Way I Work
1. The Problem: The Firehose of Academia
To understand why I needed this, you have to understand a typical Tuesday.
I’d start my day with a specific goal: “Read papers on Transformer
efficiency.” Within an hour, I’d have:
5 PDFs open from arXiv.
10 browser tabs with blog posts and related papers.
https://medium.com/p/e9c1176814dc 3/20


---
*Page 4*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
A scattered set of notes in a Markdown file.
A Zotero library with 20 new, unread items.
Finding a specific quote I read last week was a nightmare. Connecting ideas
across different papers was purely a function of my flawed memory. I was
losing the thread of my own research.
The academic status quo: information chaos.
2. The Vision: What I Wanted Hermes to Do
I envisioned an assistant that lived alongside my workflow. It didn’t need to
write my papers for me, but it needed to:
https://medium.com/p/e9c1176814dc 4/20


---
*Page 5*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
1. Ingest Everything: Automatically read and understand every PDF,
website, and note I threw at it.
2. Answer Questions: Allow me to ask natural language questions like,
“What were the key limitations of the Attention is All You Need paper?” or
“Summarize the latest papers on multimodal learning.”
3. Connect Ideas: Proactively suggest connections between papers I’d read
and new ones I was discovering.
4. Draft Content: Help me draft literature review paragraphs, abstracts, and
email responses to advisors based on my existing knowledge base.
5. Be Private: My research is my intellectual property. The core processing
needed to happen locally or on my own infrastructure, not on a public
server.
3. The Tech Stack: Choosing the Right Tools
The landscape of AI tools is vast, but I chose a stack that prioritized
flexibility, privacy, and cost-effectiveness.
LLM Provider:
Primary: Ollama (for running models locally). I primarily use llama3:8b
for quick tasks and mixtral:8x7b for complex reasoning. This ensures
privacy for my notes and ongoing drafts.
Secondary: OpenAI API (GPT-4). For tasks that require extreme nuance or
when I need a second opinion, I use GPT-4, but I send only anonymized
paper abstracts, not my personal notes.
Framework: LangChain. This is the glue that holds everything together. It
provides the tools for building chains, managing prompts, and
connecting to vector databases.
https://medium.com/p/e9c1176814dc 5/20


---
*Page 6*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
Vector Database: ChromaDB. It’s lightweight, runs locally, and is perfect
for a personal project.
Embeddings Model: BAAI/bge-small-en. This model runs locally via
Ollama/transformers and converts my documents into numerical
representations (vectors) that capture their meaning.
Frontend: Streamlit. It’s Python-based and allows me to build a simple,
interactive web UI in minutes.
PDF Processing: PyPDF2 and pdfplumber for extracting text.
4. Phase 1: The Knowledge Base — My Digital Brain
The first step was to build the memory. I needed a central repository for all
my research artifacts. I created a folder structure on my local machine:
text
~/research_knowledge_base/
├── papers/ # All PDFs, named as Author_Year_Title.pdf
├── notes/ # My personal .md notes, tagged with topics
├── websites/ # Saved webpages as .html or .txt
└── metadata/ # A simple CSV to track what's been processed
This folder is the source of truth. The AI assistant’s job is to index this folder
and make it searchable.
5. Phase 2: The Ingestion Pipeline — Feeding the Brain
This is the automated process that monitors my folder and converts
documents into a format the AI can understand.
https://medium.com/p/e9c1176814dc 6/20


---
*Page 7*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
The ingestion pipeline: Turning raw files into searchable vectors.
Here’s the Python code (simplified) that powers this pipeline using
LangChain:
# ingest.py
import os
from langchain.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdown
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
import hashlib
 
# Configuration
PERSIST_DIRECTORY = "chroma_db"
SOURCE_DIRECTORY = "~/research_knowledge_base"
EMBEDDING_MODEL = "BAAI/bge-small-en"
https://medium.com/p/e9c1176814dc 7/20


---
*Page 8*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
def hash_file_content(content):
"""Generate a hash for a document to avoid re-processing."""
return hashlib.md5(content.encode()).hexdigest()
def load_documents():
"""Loads documents from the source directory."""
documents = []
for root, _, files in os.walk(SOURCE_DIRECTORY):
for file in files:
file_path = os.path.join(root, file)
try:
if file.endswith(".pdf"):
loader = PyPDFLoader(file_path)
elif file.endswith(".md"):
loader = UnstructuredMarkdownLoader(file_path)
elif file.endswith(".txt"):
loader = TextLoader(file_path, encoding="utf-
8")
else:
continue
docs = loader.load()
# Add metadata like source file path
for doc in docs:
doc.metadata["source"] = file_path
doc.metadata["file_hash"] =
hash_file_content(doc.page_content)
documents.extend(docs)
print(f"Loaded: {file_path}")
except Exception as e:
print(f"Error loading {file_path}: {e}")
return documents
def split_documents(documents):
"""Splits documents into smaller chunks."""
text_splitter = RecursiveCharacterTextSplitter(
chunk_size=1000,
chunk_overlap=200,
length_function=len,
)
return text_splitter.split_documents(documents)
def create_or_update_vectorstore():
"""Main function to run ingestion."""
print("Loading documents...")
raw_docs = load_documents()
print("Splitting documents...")
chunks = split_documents(raw_docs)
print(f"Created {len(chunks)} chunks.")
print("Initializing embeddings model...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
https://medium.com/p/e9c1176814dc 8/20


---
*Page 9*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
print("Creating/updating vector store...")
# Check if DB exists and update, otherwise create
if os.path.exists(PERSIST_DIRECTORY):
# For simplicity, we're recreating. In a real app, you'd
check hashes.
import shutil
shutil.rmtree(PERSIST_DIRECTORY)
vectorstore = Chroma.from_documents(
documents=chunks,
embedding=embeddings,
persist_directory=PERSIST_DIRECTORY
)
vectorstore.persist()
print("Ingestion complete!")
if __name__ == "__main__":
create_or_update_vectorstore()
I run this script every night via a cron job. It scans my knowledge base, splits
every document into 1000-character chunks (with overlap), generates an
embedding for each chunk, and stores it in ChromaDB.
6. Phase 3: The RAG System — How Hermes “Thinks”
Now for the magic: Retrieval-Augmented Generation (RAG). This is the core
of Hermes. When I ask a question, the system doesn’t just guess an answer. It
follows a precise process:
1. Retrieve: It takes my question, converts it into an embedding, and
searches the vector database for the 5–10 most semantically similar text
chunks.
2. Augment: It stuffs these retrieved chunks into a carefully crafted prompt,
instructing the LLM to answer the question only based on the provided
context.
3. Generate: It sends this augmented prompt to the LLM (Llama 3 locally, or
GPT-4 via API) and streams the response back to me.
https://medium.com/p/e9c1176814dc 9/20


---
*Page 10*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
The RAG workflow: Grounding the AI’s answers in my own documents.
Here’s the code for the Q&A chain:
# qa_engine.py
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
PERSIST_DIRECTORY = "chroma_db"
EMBEDDING_MODEL = "BAAI/bge-small-en"
# Custom prompt to enforce grounded answers
PROMPT_TEMPLATE = """You are an AI research assistant. Use the
following pieces of context to answer the question at the end. If
you don't know the answer based *only* on the context, just say
that you don't know. Don't try to make up an answer.
https://medium.com/p/e9c1176814dc 10/20


---
*Page 11*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
Context:
{context}
Question: {question}
Helpful Answer:"""
def get_qa_chain(model_name="llama3:8b"):
# Load vector store
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY,
embedding_function=embeddings)
# Setup LLM (local via Ollama)
llm = Ollama(model=model_name, temperature=0.3) # Low temp for
factual answers
# Create prompt
prompt = PromptTemplate(template=PROMPT_TEMPLATE,
input_variables=["context", "question"])
# Create retrieval chain
qa_chain = RetrievalQA.from_chain_type(
llm=llm,
chain_type="stuff", # "stuff" puts all retrieved docs into
one prompt
retriever=vectorstore.as_retriever(search_kwargs={"k":
5}),
return_source_documents=True, # Tells us which docs were
used
chain_type_kwargs={"prompt": prompt}
)
return qa_chain
def ask_question(question):
chain = get_qa_chain()
result = chain({"query": question})
return result
7. Phase 4: The Interface — Talking to Hermes
A command line is fine, but a visual interface makes the assistant feel like a
real tool. I used Streamlit to build a simple chat interface.
python
https://medium.com/p/e9c1176814dc 11/20


---
*Page 12*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
# app.py
import streamlit as st
from qa_engine import ask_question
import time
st.set_page_config(page_title="Hermes - AI Research Assistant",
layout="wide")
🧑‍🔬
st.title(" Hermes: Your Personal Research Assistant")
# Sidebar for controls
with st.sidebar:
st.header("Settings")
st.info("Connected to local knowledge base.")
🔄
if st.button(" Re-index Knowledge Base"):
with st.spinner("Re-indexing... This may take a few
minutes."):
# In a real app, you'd call the ingest function here
# import ingest
# ingest.create_or_update_vectorstore()
time.sleep(2) # Simulate work
st.success("Knowledge base re-indexed!")
st.header("Session Info")
st.write(f"**Documents in scope:** All files in
`~/research_knowledge_base`")
st.write(f"**Current LLM:** Llama 3 (Local)")
# Main chat area
if "messages" not in st.session_state:
st.session_state.messages = [
{"role": "assistant", "content": "Hello! I'm Hermes. Ask
me anything about your research library."}
]
# Display chat messages
for message in st.session_state.messages:
with st.chat_message(message["role"]):
st.markdown(message["content"])
# Chat input
if prompt := st.chat_input("Ask a question about your
research..."):
# Add user message
st.session_state.messages.append({"role": "user", "content":
prompt})
with st.chat_message("user"):
st.markdown(prompt)
https://medium.com/p/e9c1176814dc 12/20


---
*Page 13*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
# Generate assistant response
with st.chat_message("assistant"):
message_placeholder = st.empty()
full_response = ""
try:
# Call the QA engine
result = ask_question(prompt)
answer = result['result']
source_docs = result['source_documents']
# Simulate streaming effect
for chunk in answer.split():
full_response += chunk + " "
time.sleep(0.05)
message_placeholder.markdown(full_response + "▌")
message_placeholder.markdown(full_response)
# Show sources in an expander
with st.expander("View Sources"):
for i, doc in enumerate(source_docs):
st.caption(f"**Source {i+1}:**
`{doc.metadata['source']}`")
st.text(doc.page_content[:300] + "...")
st.divider()
except Exception as e:
st.error(f"An error occurred: {e}")
full_response = "Sorry, I encountered an error. Please
check the logs."
st.session_state.messages.append({"role": "assistant",
"content": full_response})
https://medium.com/p/e9c1176814dc 13/20


---
*Page 14*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
The Hermes chat interface, displaying a question, an answer, and the sources used.
8. Overcoming Challenges & Future Work
Building this wasn’t all smooth sailing. Here are a few hurdles I hit:
Challenge 1: PDF Parsing Hell. Academic PDFs often have complex
layouts (two columns, math, tables). PyPDF2 often extracted text in the
wrong order. Solution: I switched to using pdfplumber for better layout
detection and am now experimenting with Nougat (Neural Optical
Understanding for Academic Documents) by Meta, which converts PDFs
to Markdown, preserving structure.
Challenge 2: The “Lost in the Middle” Problem. LLMs tend to ignore
information in the middle of a long context. Solution: I’m working on
implementing a Reranking step. After retrieving the top 10 chunks, I use
https://medium.com/p/e9c1176814dc 14/20


---
*Page 15*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
a cross-encoder model to re-evaluate their relevance and only pass the
top 3 to the LLM.
Challenge 3: Multi-hop Reasoning. A question like “How does the
architecture of Model X influence the training stability issues found in
Dataset Y?” requires connecting information from multiple papers.
Solution: This requires more advanced RAG techniques, like query
transformation or iterative retrieval, which is my next major focus.
Future Features on My Roadmap:
1. Automated Literature Gap Analysis: Have Hermes analyze a set of papers
on a topic and suggest what’s missing.
2. Research Idea Generation: Provide Hermes with a list of my recent notes
and papers and ask it to propose three novel research hypotheses.
3. Integration with Zotero: Automatically ingest new papers added to my
reference manager.
9. Conclusion: The New Way I Work
Building Hermes has fundamentally changed my academic workflow. I no
longer fear the “Monday morning inbox.” I have a tool that knows everything
I’ve read and can recall it in an instant. The time I used to spend searching
for that one quote is now spent thinking about its implications.
This project proves that you don’t need a massive corporate infrastructure to
benefit from AI. With open-source models, a bit of Python, and a clear
vision, you can build a tool that not only organizes your work but actively
participates in it.
https://medium.com/p/e9c1176814dc 15/20


---
*Page 16*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
My research is no longer a chaotic pile of papers. It’s a connected,
searchable, and interactive garden of ideas — and Hermes is my guide.
Programming Life Python Marketing Productivity
Published in Towards AI
Following
112K followers · Last published 1 hour ago
We build Enterprise AI. We teach what we learn. Join 100K+ AI practitioners on
Towards AI Academy. Free: 6-day Agentic AI Engineering Email Guide:
https://email-course.towardsai.net/
Written by Amar Chetri, PhD
Follow
67 followers · 143 following
I write to think clearly and explore ideas. Expect simple insights, honest
reflections, and curiosity-driven notes.
No responses yet
Rae Steele
What are your thoughts?
https://medium.com/p/e9c1176814dc 16/20


---
*Page 17*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
More from Amar Chetri, PhD and Towards AI
InWrite A Catalystby Amar Chetri, PhD InTowards AIby Soultntoure
Running Your Own AI is Easier The NotebookLM Workflow That
Than You Think: A Beginner’s… Changed How I Learn Any…
Remember the first time you heard about A practical system for conquering dense
ChatGPT? It felt like magic. But then came th… documentation, complex tools, and heavy…
Feb 16 94 1 Dec 23, 2025 1.5K 20
https://medium.com/p/e9c1176814dc 17/20


---
*Page 18*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
InTowards AIby Khushbu Shah InTowards AIby Amar Chetri, PhD
9 Agentic AI Projects I’d Build in The Magic of Prompting: How to
2026 to Learn What Agents Reall… Talk to AI to Get What You Actuall…
Most “ AI agent demos” online are just
chatbots with a loop. I’ve seen enough agent…
Jan 27 306 10 5d ago 14
See all from Amar Chetri, PhD See all from Towards AI
Recommended from Medium
https://medium.com/p/e9c1176814dc 18/20


---
*Page 19*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
Will Lockett InLevel Up Coding by Gaurav Shrivastav
OpenAI Is Totally Cooked Build Multi Agent AI Deep Research
Planning App End to End
What a s**tshow.
How I designed a planning-first, multi-agent
research pipeline with LangGraph, Tavily, an…
Feb 23 2.6K 38 Feb 20 274 3
InEntrepreneurship Handbook by Joe Procopio InAI Advancesby Delanoe Pirard
Databricks CEO Just Dropped The A Discord Community Beat Meta’s
Most Honest Advice About The… LLaMA. The Secret? An…
Data company leaders aren’t interested in RWKV-7 scores 72.8% vs LLaMA’s 69.7% with
histrionics and hand-waving 3x fewer tokens. It runs in constant memory.…
Feb 23 1.7K 55 Feb 22 546 6
InData Science Colle… by Han HELOIR YAN, Ph.… Ignacio de Gregorio
The February Reset: Three Labs, Anthropic Reveals China’s Dirty
Four Models, and the End of “One… Little AI Secret.
How Gemini 3.1 Pro, Claude Opus 4.6, and …While ousting themselves as huge
GPT-5.3-Codex split the frontier into three… hypocrites
https://medium.com/p/e9c1176814dc 19/20


---
*Page 20*


3/4/26, 9:39 AM How I Built a Personal AI Research Assistant Using LLMs to Organize My Daily Academic Work | by Amar Chetri, PhD | Feb, 2026 | …
Feb 21 1.3K 9 Feb 24 1.8K 42
See more recommendations
https://medium.com/p/e9c1176814dc 20/20