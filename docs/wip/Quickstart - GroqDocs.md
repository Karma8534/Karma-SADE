# Quickstart - GroqDocs

*Converted from: Quickstart - GroqDocs.PDF*



---
*Page 1*


Docs Login
Documentation
Docs API Reference
Search
Quickstart
Quickstart
Copy page
Get up and running with the Groq API in a few minutes, with the steps below.
For additional support, catch our onboarding video.
Create an API Key
Please visit here to create an API Key.
Set up your API Key (recommended)
Configure your API key as an environment variable. This approach streamlines your API usage by
eliminating the need to include your API key in each request. Moreover, it enhances security by
minimizing the risk of inadvertently including your API key in your codebase.
In your terminal of choice:
shell
export GROQ_API_KEY=<your-api-key-here>
Requesting your first chat completion
curl JavaScript Python JSON


---
*Page 2*


Install the Groq Python library:
Docs
shell
GETTING STARTED
pip install groq
Overview
Quickstart
Performing a Chat Completion:
Models
Python
OpenAI Compatibility
1 import os
2Responses API
3 from groq import Groq
4
Rate Limits
5 client = Groq(
6 api_key=os.environ.get("GROQ_API_KEY"),
Templates
7 )
8
API Reference
9 chat_completion = client.chat.completions.create(
10 messages=[
11 {
CORE FEATURES
12 "role": "user",
Text Generation
13 "content": "Explain the importance of fast language models",
14 }
S1p5ee c h t o] T,ext
16 model="llama-3.3-70b-versatile",
T1e7xt t)o Speech
18
19Orpphreiunst(chat_completion.choices[0].message.content)
OCR and Image Recognition
Using third-party libraries and SDKs
Reasoning
Vercel AI SDK LiteLLM LangChain
Content Moderation
Structured Outputs
Using AI SDK:
Prompt Caching
AI SDK is a Javascript-based open-source library that simplifies building large language model (LLM)
applications. Documentation for how to use Groq on the AI SDK can be found here.
TOOLS & INTEGRATIONS
Tool Use
First, install the ai package and the Groq provider @ai-sdk/groq :
Overview


---
*Page 3*


DocGsroq Built-In Tools
shell
Web Search
GETTING STARTED
pnpm add ai @ai-sdk/groq
Visit Website
Overview
Browser Automation
Quickstart
Then, you can use the Groq provider to generate text. By default, the provider will look for
Code Execution
GMROoQd_eAlsPI_KEY as the API key.
Wolfram Alpha
OpenAI Compatibility
Browser Search (GPT OSS Models)
JavaScript
Responses API
Remote Tools and MCP
R1ate iLimmpiotsrt { groq } from '@ai-sdk/groq';
2 import { generateText } from 'ai';
Connectors
Te3mplates
4 const { text } = await generateText({
Local Tool Calling
A5PI Re f emroednecle: groq('llama-3.3-70b-versatile'),
6 prompt: 'Write a vegetarian lasagna recipe for 4 people.',
Integrations Catalog
7 });
CORE FEATURES
Coding with Groq
Text Generation
Now that you have successfully received a chat completion, you can try out the other endpoints in the
API.Factory Droid
Speech to Text
OpenCode
Text to Speech
NextK iSlot eCpodse
Orpheus
Check out the Playground to try out the Groq API in your browser
Roo Code
OCJoRi na nodu rIm GargoqeC Rleocuodg dneitvieolnoper community
ACdldin ea how-to on your project to the Groq API Cookbook
Reasoning
CCOoMntPeOnUtN DM (oAdGEeNraTtICio AnI)
Was this page helpful? Yes No Suggest Edits
Overview
Structured Outputs
Built-In Tools
Prompt Caching
Systems
TOOLS & INTEGRATIONS
Use Cases
Tool Use
GUIODvEeSrview