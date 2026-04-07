# AltIngestPipeline

*Converted from: AltIngestPipeline.PDF*



---
*Page 1*


Open in app
11
Search Write
Towards AI
Member-only story
PaddleOCR + hybrid
retrieval + Rerank
techniques Just
Revolutionized Agent
OCR Forever
⾼達烈
Gao Dalie ( ) Follow 12 min read · Jan 4, 2026
140


---
*Page 2*


In 2026, Generative AI will have passed its “magic”
stage and will enter the “Year of Utility.”
With the rapid development of large models and
RAG technology, structured data is becoming more
important for intelligent systems. Converting
unstructured data, such as document images and
PDFs, into structured formats like Markdown and
JSON is now a key challenge in the industry.
Many current open-source solutions still struggle
with complex documents. They often have poor
text recognition, fail to restore the correct reading


---
*Page 3*


order, recognise tables incorrectly, and cannot
parse long or complex formulas.
These problems not only compromise data quality
for training and fine-tuning large models but also
hinder the development and deployment of AI
applications.
Good News, Paddle OCR introduces PP-
StructureV3, designed to solve these problems and
provide faster and more accurate document
parsing for the industry.
It supports high-precision parsing of document
images and PDFs, and can convert them into
Markdown and JSON across many layouts and
scenarios, performing very well on the
OmniDocBench benchmark.
The system also supports advanced features,
including stamp recognition, chart parsing, tables
with formulas or images, vertical text, and
mathematical formulas and chemical equations.


---
*Page 4*


PP-StructureV3 utilises a well-optimised
combination of models, offering simple APIs and
deployment tools that make it easy for developers
to use locally or as a service.
Do not forget to mention that RAG uses vector
search to find relevant documents by converting
text into vectors and comparing their similarity to
a query.
Because vectors compress meaning, important
information may exist in lower-ranked documents,
so increasing the number of retrieved documents
can improve recall.
However, passing too many documents to a large
language model hurts performance due to context
window limits and reduced instruction-following
ability.
To solve this, we retrieve many documents to
maximise recall, then reorder and keep only the


---
*Page 5*


most relevant ones before sending them to the
model
So, let me give you a quick demo of a live chatbot
to show you what I mean.
I’ve been locking myself in for a while, building my
first product. As many of you know, I’m a student,
a content creator, and a research assistant — and
balancing school, work, and life has been harder
than I expected.


---
*Page 6*


Some days, I lose focus easily. I tried countless
Chrome extensions and productivity apps, hoping
one of them would truly help — but none of them
felt right.
That’s when I decided to build TiimoAi. A tool that
understands my tasks, organizes my tabs,
highlights what matters, sets reminders, and keeps
me on track — all in one beautiful place.
I built TiimoAi for people like me — and yes, it’s
completely free to use.
You can organise your tabs manually or let AI
group them based on your tasks. You can create
tasks, assign them to projects, set custom time
blocks, and plan your day your way.
Once a focus session starts, TiimoAi blocks
distracting apps so you can work deeply without
distractions. Every task, project, and minute is
tracked and shown in a clean, beautiful dashboard
that helps you see where your time really goes.


---
*Page 7*


You’ll know how much time you spend on each
project, which days you’re most productive, and
what habits are holding you back — giving you real
control over your life.
As they say, “Time is money.” And when you truly
understand your time, you start owning it.
So guys, I encourage you to try TiimoAi and see the
difference for yourself! Don’t forget to leave a
comment and give us 5 stars if you love it — every
star means a lot to me and keeps me motivated to
keep building and sharing with you all.
Check out the chrome: https://tiimoai.dev/
Alright, without further delay, let’s dive into the
demo!
I will upload a resume profile and ask the chatbot
the question, “Give a summary about this resume “


---
*Page 8*


If you look at how the chatbot generates the
output, you’ll see that the agent sends this PDF to
PP-Structure. OCR is a powerful document parser.
It not only reads text.
It also understands the layout of the page, like
titles, paragraphs, columns, and images. The result
is clean Markdown text and saved images instead
of broken lines.
Next, the agent takes the Markdown text and
chunks it into small pieces. It uses a sliding
window, so each chunk overlaps with the next one.
This overlap helps keep the meaning when a
sentence is split. Each text piece is now small
enough for the model to understand.
Then, the agent turns each text piece into a vector
number using an embedding model. Each vector
has 384 values. The agent stores the vector, the
original text, and extra info (file name, page


---
*Page 9*


number, chunk ID) together in Milvus, which is
the vector database.
When the user asks a question, the agent starts the
search flow. First, it translates the question into
two languages (Chinese and English). This avoids
missing answers when the question language and
document language are different.
After that, the agent runs two searches at the same
time:
Vector search to find text that is similar in
meaning
Keyword search to find exact words, numbers,
or variable names
The agent then merges the two result lists using
Reciprocal Rank Fusion, which keeps both
accuracy and diversity.
Next, the agent sends all retrieved chunks to
Reranker V2. This step gives each chunk a final


---
*Page 10*


score. The score is not from one model only. It is a
mix of rules and semantics between
Semantic similarity from Milvus (35%)
Fuzzy text match (25%)
Keyword coverage (25%)
Text length (15%)
Bonus for a good position and proper nouns
This makes the decision easy to explain and not a
black box.
If the question talks about a figure or chart, the
agent activates the vision flow. It sends the image
and the OCR text from the same page to a
multimodal model, so the model understands both
the picture and its context. If this fails, the agent
automatically falls back to normal text search.
Finally, the agent inserts the top-scored text
chunks into a prompt and sends them to the LLM.


---
*Page 11*


The LLM reads only this trusted context and
generates the final answer.
󰬾
Before we start!
If you like this topic and you want to support me:
1. Clap my article 50 times; that will really help me
👏
out.
2. Follow me on Medium and subscribe to get my
🫶
latest article for Free
3. Join the family — Subscribe to the YouTube
channel
What makes PP-StructureV3 Unique?
Traditional plain text extraction tools such as
PyPDF2 often fall short in dealing with common
issues in scientific research papers, such as two-
column layout, mixed formulas, and embedded
figures (easily leading to paragraph disorder and
table corruption).


---
*Page 12*


To this end, this project encapsulates the
OnlinePDFParser class in backend.py, which
directly integrates the PP-StructureV3 online API
for high-precision document layout analysis
(Layout Parsing).
This solution has three core advantages:
Structured output: Directly returns Markdown
format (automatically recognizes heading levels
and paragraph boundaries).
Chart Extraction: While parsing the text,
automatically extract and save the images from
the document to provide materials for
subsequent “multimodal question answering”.
Context preservation: Segmentation is based on
a sliding window to prevent the loss of key
information at slice boundaries.
Why choose to use a reorderer?
We still use reorderers despite their slower speed
because their accuracy far surpasses that of


---
*Page 13*


embedding (bi-encoder) models. Bi-encoders
compress all possible meanings of a document
into a single vector, losing information and
ignoring the query’s context.
Reorderers, in contrast, process the raw query and
document together in a Transformer, reducing
information loss and generating more precise
similarity scores.
The trade-off is time: while vector search with bi-
encoders is extremely fast, reordering is much
slower but much more accurate.
Reorderers excel in understanding nuanced
queries, handling context-specific meanings, and
capturing subtle relationships between query and
document content that embeddings often miss.
They are particularly valuable when precision is
critical, such as in legal search, scientific research,
or high-stakes recommendation systems.


---
*Page 14*


While slower, their ability to evaluate each
document against the query in full detail makes
them indispensable for tasks where accuracy
outweighs speed.
Let’s start coding:
While exploring new technology, I came across the
Baidu Team. I want to thank them for making the
code open-source — full credit goes to them.
Please note, I didn’t write a single line of the code;
I’m here only to explain it and share my learning
journey with you.
They construct an API request to send the PDF file
stream to the server and parse the returned
layoutParsingResults to extract the cleaned
Markdown text and image resources.
def predict(self, file_path):
# 1. Convert file to Base64
with open(file_path, "rb") as file:
file_data = base64.b64encode(file.read()).dec
# 2. Construct request payload


---
*Page 15*


payload = {
"file": file_data,
"fileType": 1, # PDF type
"useChartRecognition": False, # Configure as
"useDocOrientationClassify": False
}
# 3. Send request to get Layout Parsing results
# Assuming headers are defined elsewhere or passe
headers = {"Contement-Type": "application/json"}
response = requests.post(self.api_url, json=paylo
response.raise_for_status() # Raise exception fo
res_json = response.json()
# 4. Extract Markdown text and images
parsing_results = res_json.get("result", {}).get(
mock_outputs = []
for item in parsing_results:
md_text = item.get("markdown", {}).get("text"
images = item.get("markdown", {}).get("images
# (Add image downloading and text cleaning lo
# For example: clean text, download images to
# Assuming MockResult is a class or namedtupl
# Example: MockResult = namedtuple('MockResul
mock_outputs.append(MockResult(md_text, image
return mock_outputs, "Success"
2.1.2 Sliding Window Text Blocking


---
*Page 16*


After obtaining the structured Markdown text, in
order to avoid the semantics being abruptly cut off
(e.g., a sentence spanning two chunks), we
implemented a sliding window chunking strategy
with overlap.
def split_text_into_chunks(text: str, chunk_size: int
"""Split text into chunks with sliding window app
if not text:
return []
lines = [line.strip() for line in text.split("\n"
chunks = []
current_chunk = []
current_length = 0
for line in lines:
# Handle lines that are longer than chunk_siz
while len(line) > chunk_size:
# Extract a part of the line that fits wi
part = line[:chunk_size]
line = line[chunk_size:]
# Add the part to current chunk
current_chunk.append(part)
current_length += len(part)
# If current length exceeds threshold, cr
if current_length >= chunk_size:
chunks.append("\n".join(current_chunk


---
*Page 17*


# For overlap: take the last part fro
# but only if it's long enough for ov
overlap_text = ""
if current_chunk and len(current_chun
overlap_text = current_chunk[-1][
elif current_chunk:
overlap_text = current_chunk[-1]
# Reset for next chunk with overlap t
current_chunk = [overlap_text] if ove
current_length = len(overlap_text)
# Add the remaining part of the line (or the
if line:
current_chunk.append(line)
current_length += len(line)
# Check if we've reached the chunk size thres
if current_length >= chunk_size:
chunks.append("\n".join(current_chunk))
# For overlap: take the last line from cu
overlap_text = ""
if current_chunk and len(current_chunk[-1
overlap_text = current_chunk[-1][-ove
elif current_chunk:
overlap_text = current_chunk[-1]
# Reset for next chunk with overlap text
current_chunk = [overlap_text] if overlap
current_length = len(overlap_text)
# Add any remaining text as the final chunk
if current_chunk:
chunks.append("\n".join(current_chunk).strip(


---
*Page 18*


return chunks
Milvus Vector Library and Hybrid
Retrieval Strategy
Engineering Processing of Knowledge Base
Naming
In practical deployments, vector databases such as
Milvus typically have strict naming restrictions on
collection names. To address this issue, we
implemented a transparent encoding/decoding
mechanism in the backend code.
1. Encoding: When a user creates a library such as
“physics paper”, the system converts its UTF-8
bytes to a Hex string and adds kb_a prefix.
2. Decode: When displayed on the front end,
automatically decode the Hex string into the
original Chinese characters.
import binascii
import re


---
*Page 19*


def encode_name(ui_name):
"""Convert Chinese name to a hex string valid for
if not ui_name:
return ""
# If it's pure English letters/numbers/underscore
if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', ui_name)
return ui_name
# Hex encoding with kb_ prefix
hex_str = binascii.hexlify(ui_name.encode('utf-8'
return f"kb_{hex_str}"
def decode_name(real_name):
"""Convert hex string back to Chinese"""
if real_name.startswith("kb_"):
try:
hex_str = real_name[3:]
return binascii.unhexlify(hex_str).decode
except:
return real_name
return real_name
Hybrid Search Strategy
Before the search, the system first uses a bilingual
translation of the question generated by LLM to
avoid Chinese questions querying English
documents, which would lead to keyword


---
*Page 20*


mismatch and maximise semantic coverage. Then,
two-way searches are executed in parallel:
1. Dense (vector retrieval): Captures semantic
similarity (e.g., the semantic association
between “simple harmonic oscillator” and
“spring oscillator”).
2. Sparse (keyword retrieval): compensates for the
shortcomings of vector models in matching
proper nouns or exact numbers (such as
matching variable names in formulas).
Vector retrieval is prone to recalling incorrect
concepts due to semantic generalization (such as
“spring oscillator” and “simple harmonic
oscillator”), while high-weight keyword retrieval
can ensure accurate hits of proper nouns, thereby
significantly improving accuracy.
Then execute:


---
*Page 21*


RRF (Reciprocal Rank Fusion): The system
internally uses the Reciprocal Rank Fusion
algorithm to merge the two results, ensuring
diversity.
def search(self, query: str, top_k: int = 10, **kwarg
'''Vector retrieval (Dense+Keyword) + RRF fusion'
# 1. Vector retrieval (Dense)
dense_results = []
query_vector = self.embedding_client.get_embeddin
# ... (Milvus search code) ...
# 2. Keyword retrieval (Keyword)
# Construct like "%keyword%" query after jieba wo
keyword_results = self._keyword_search(query, top
# 3. RRF fusion
rank_dict = {}
def apply_rrf(results_list, k=60, weight=1.0):
for rank, item in enumerate(results_list):
doc_id = item.get('id') or item.get('chun
if doc_id not in rank_dict:
rank_dict[doc_id] = {"data": item, "s
# RRF core formula
rank_dict[doc_id]["score"] += weight * (1
apply_rrf(dense_results, weight=1.0)
apply_rrf(keyword_results, weight=3.0) # Higher
# 4. Sort and output


---
*Page 22*


sorted_docs = sorted(rank_dict.values(), key=lamb
return [item['data'] for item in sorted_docs[:top
Comprehensive Reordering Algorithm
The retrieved chunks require further refinement.
reranker_v2.pyA comprehensive scoring algorithm
was designed in [the document/platform name -
implied]. The scoring dimensions include:
1. Fuzzy Score : fuzzywuzzyCalculates the literal
overlap between the Query and the Content.
2. Keyword Coverage: Calculates the proportion of
core words in a query that appear in a document
fragment.
3. Semantic similarity: the original vector distance
from Milvus.
4. Length penalty and position bias: Penalise
excessively short segments and reward high-
ranking segments recalled by Milvus with
position bias.
5. Proper nouns :


---
*Page 23*


For English (look at the “case-sensitive” feature):
Use regular expressions \b[A-Z][a-z]+\b|[A-Z]
{2,}to specifically match words that start with a
capital letter (such as "Milvus") or abbreviations
that are all capitalized (such as "RAG"), because
these usually represent proper nouns in English.
This reordering strategy, which combines rules
and semantics, is more interpretable than a pure
black-box model when no training data is
available.
def _calculate_composite_score(self, query: str, chun
content = chunk.get('content', '')
# 1. Literal overlap score (FuzzyWuzzy)
fuzzy_score = fuzz.partial_ratio(query, content)
# 2. Keyword coverage rate
query_keywords = self._extract_keywords(query)
content_keywords = self._extract_keywords(content
keyword_coverage = (len(query_keywords & content_
# 3. Vector semantic score (normalized)
milvus_distance = chunk.get('semantic_score', 0)
milvus_similarity = 100 / (1 + milvus_distance *


---
*Page 24*


# 4. Length penalty (prefer paragraphs with 200-6
content_len = len(content)
if 200 <= content_len <= 600:
length_score = 100
else:
# Penalty logic: reduced score for too short
length_score = 100 - min(50, abs(content_len
# Weighted sum
base_score = (
fuzzy_score * 0.25 +
keyword_coverage * 0.25 +
milvus_similarity * 0.35 +
length_score * 0.15
)
# Position weighting
position_bonus = 0
if 'milvus_rank' in chunk:
rank = chunk['milvus_rank']
position_bonus = max(0, 20 - rank)
# Proper noun bonus
proper_noun_bonus = 30 if self._check_proper_noun
return base_score + position_bonus + proper_noun_
Multimodal Question Answering
To address the characteristic of research
documents containing numerous key charts and
graphs (such as experimental data and model


---
*Page 25*


architectures), this system implements a “chart
locking” question-and-answer function. The core
technology implementation encompasses the
following three dimensions:
1. When constructing a request, the context-
enhanced Prompt backend not only sends the
image itself but also retrieves the OCR text of the
page containing the image as background
information (Context). The Prompt structure
dynamically assembles “image metadata +
background text + user question,” effectively
improving the model’s ability to understand
chart details and contextual relationships.
# 1. Retrieve OCR text of current page as background
# System fetches complete page text from Milvus based
# page_num is parsed from frontend image filename (e.
page_text_context = milvus_store.get_page_content(doc
# 2. Dynamically assemble Context-Enhanced Prompt
# Key point: Force alignment between "visual informat
# to prevent model hallucinations when describing ima
final_prompt = f"""
[Task] Answer the question by combining the image and


---
*Page 26*


[Image Metadata] Source: {doc_name} (P{page_num})
[Background Text] {page_text_context} ... (long text
[User Question] {user_question}
"""
# 3. Send multimodal request (Vision API)
# The underlying system will convert image to Base64
answer = ernie_client.chat_with_image(query=final_pro
Conclusion :
The transition from PP-StructureV3 to hybrid
research and reranking is not just a simple library
replacement. We can expect architectural
improvements, such as simplified image
preprocessing and the ability to obtain results
with confidence scores.
󰩃
I am an AI Generative expert! If you want to
collaborate on a project, drop an inquiry here or
book a 1-on-1 Consulting Call With Me.
DSPy 3 + GEPA: The Most Advanced RAG
F k Y t A t R i &
Last week, OpenAI experienced a sudden
i th iddl f th i ht d t i t
pub.towardsai.net


---
*Page 27*


DeepSeek-V3.2 + DocLing + Agentic RAG:
P A D t ith E
If you’ve been following open-source logical
d lli k it' b hi hl
medium.com
Gemini 3.0 Flash + MistralOCR 3 + RAG Just
R l ti i d A t OCR F
Not long ago, I shared a video about
D S k OCR d P ddl OCR d
pub.towardsai.net
Data Science Artificial Intelligence Machine Learning
Technology Programming
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


---
*Page 28*


NC State Uni (Research Assistant), Learn AI Agent,
LLMs, RAG & Generative AI. See everything I have to
offer at the link below: https://linktr.ee/GaoDalie_AI
No responses yet
To respond to this story,
get the free Medium app.
⾼達烈
More from Gao Dalie ( ) and Towards
AI
In by ⾼達 In by
Towards … Gao Dalie ( … Towards AI Shreyas Naphad
RLM: The Ultimate If You Understand
E l ti f AI? Th 5 AI T
During the weekend, I scrolled Master the core ideas behind
th h T itt t h t AI ith t tti l t


---
*Page 29*


Jan 10 5d ago
In by In by ⾼達
Towards AI Alpha Iterations Towards … Gao Dalie ( …
Agentic AI Project: DSPy 3 + GEPA: The
B ild C t M t Ad d RAG
End to end implementation of Last week, OpenAI
A ti AI b d t i d dd
Mar 26 Dec 21, 2025
⾼達烈
See all from Gao Dalie ( ) See all from Towards AI
Recommended from Medium


---
*Page 30*


In by In by
Towards AI Alpha Iterations AI Exploration Jo… Florian J…
Agentic AI Project: dots.ocr: Turning
B ild C t D t P i i t
End to end implementation of At first glance, document
A ti AI b d t i i ht l k lik OCR
Mar 26 Mar 25
Mandar Karhade, MD. PhD. Ewan Mak
Which Small vLLM OCR Mac Mini M4 vs AMD
M d l I th B t F Mi i PC f L l AI
A weekend experiment that The single most important
t t d ith “j t t th b h b i l l
4d ago 4d ago
In by In by
Generativ… Gaurav Shriva… Graph P… Alexander Shere…
I Threw Out My Vector Building Knowledge
D t b RAG G t G h ith L l
Here’s what happens when For the production GraphRAG
l t LLM i t i li th t ti t i


---
*Page 31*


Mar 24 Mar 23
See more recommendations