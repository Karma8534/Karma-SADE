# I switched everything to local AI and stopped sending my documents to the cloud

*Converted from: I switched everything to local AI and stopped sending my documents to the cloud.PDF*



---
*Page 1*


     
1
I switched everything to local AI and stopped
sending my documents to the cloud
CCrreeddiitt:: OOlluuwwaaddeemmiillaaddee AAffoollaabbii // MMaakkeeUUsseeOOff
  
Follow Like 1 Add us on
–
By Oluwademilade Afolabi Feb 21, 2026, 2:30 PM EST
For a long time, I didn’t think twice about pasting a contract into ChatGPT, uploading
a confidential report to ask for a summary, or feeding a client proposal into a cloud
AI tool. Then one day I actually stopped and read a terms of service document
(something I’d been lazily skimming for years) and the realization hit me: these files
were leaving my machine and living, at least temporarily, on someone else’s servers.
And interestingly, I realized that a former colleague had once covered why you
shouldn't trust ChatGPT with confidential information. That discomfort sent me
looking for a better way.
✕
✕


---
*Page 2*


   Ad  
Link copied to clipboard
1 Ad
What I found was AnythingLLM, a free, open-source desktop app that lets you build
a fully private AI assistant from your own documents — and does it entirely on your
device. It has become one of the open-source AI apps I use every day. Here’s what
switching over actually looked like.
AnythingLLM
OS
Windows, Android, Mac, Linux
Price model
Free (open-source)
Run and chat with large language models locally using AnythingLLM. It lets you connect documents,
control your data, and keep AI fully under your ownership.
See at AnythingLLM
See at GitHub
Getting AnythingLLM installed and configured
takes only a few minutes
And it tells you exactly where your data goes before you even begin


---
*Page 3*


   Ad  
Link copied to clipboard
1 Ad
  
✕ Remove Ads
Ad
After you've grabbed the setup file, double-click it, and the wizard takes over. During
install, it automatically downloads supporting components: Ollama’s CUDA libraries
if you have a compatible NVIDIA GPU — a process you'll appreciate if you
understand what CUDA cores are and how they improve general computational
power — FFProbe for media handling, and Meeting Assistant assets for voice


---
*Page 4*


features. None of that requires any input from you. The whole thing, from double-
   Ad  
Link copied to clipboard
clicking the installer to see1ing the main dAasdhboard, took me under five minutes.
✕ Remove Ads
Ad
Once AnythingLLM opens, one of the first things it shows you is a Data Handling &
Privacy screen — and it’s worth reading. It states plainly that your model and chats
are only accessible on your device, that document text is embedded privately on this
instance using its built-in AnythingLLM Embedder, and that your vectors are stored
locally via LanceDB. If you've ever looked into what a vector database is and how
they boost AI, you'll recognize that keeping this component completely offline is a
massive privacy win. There are no toggles, and opt-outs buried in settings.
Everything stays local by default.
Right after the privacy overview, AnythingLLM walks you through its LLM Preference
screen. The list of supported providers is long: on the cloud side there’s OpenAI,
Anthropic, Azure OpenAI, Gemini, Groq, and others. On the fully local side, there’s
Ollama, LM Studio, LocalAI, KoboldCPP, Dell Pro AI Studio, Microsoft Foundry Local,
and Docker Model Runner, among others. The default “AnythingLLM” option bundles
a local model runner powered by Ollama, meaning you can download models like
Microsoft’s Phi-4 (9.1 GB) or Alibaba’s Qwen3 0.6B (a lean 600 MB) directly from
inside the app, without any additional setup.


---
*Page 5*


✕ Remove Ads
   Ad  
Link copied to clipboard
1 Ad
Ad
RELATED
Dec 13, 2024
The 9 Best Local/Offline LLMs You Can Try
Right Now
Looking for LLMs you can locally run on your computer? We've got
you covered!
By Jayric Maning |  4
If your machine doesn’t have a dedicated GPU, that’s not a dealbreaker. Connecting
to Groq’s API gives you access to fast-inference models like Llama 3 70B at near-
zero cost, and you only need an API key to make it work. You can switch your
provider at any time from settings, so you’re never locked into whichever option you
chose at setup. I started on the local provider for testing — Phi-3 3.8B surprised me
with how capable it felt for document Q&A on a mid-range laptop—then moved to
Groq for heavier tasks where speed mattered more.


---
*Page 6*


✕ Remove Ads
   Ad  
Link copied to clipboard
1 Ad
Ad
Once you’re set up, AnythingLLM turns your own
documents into a focused AI assistant
Your files get to talk back in a much clearer way
  


---
*Page 7*


The dashboard greets you with a getting-started checklist and a sidebar that already
   Ad  
Link copied to clipboard
contains a default worksp1ace called “MyA Wdorkspace.” Workspaces are the core
organizing concept in AnythingLLM: each one is a self-contained environment
where your documents and conversations live together. Think of each workspace as
a separate room: one for client contracts, another for internal research, a third for
personal notes. Documents can be shared between workspaces if needed, but they
don’t bleed into each other, which keeps the AI’s context focused and its answers
accurate.
✕ Remove Ads
Ad
Mountain fun for everyone.
Sponsored by: Roundtop
Getting documents into a workspace is a simple drag-and-drop. AnythingLLM
handles Word documents, plain text files, CSVs, spreadsheets, audio files and even
PDFs, similar to how NotebookLM turns any PDF into an interactive conversation.
There’s also a “Fetch website” field in the upload panel, so if you want to pull in a
webpage or online resource, you paste the URL, and it scrapes the content
automatically. Once uploaded, AnythingLLM processes each file through its
embedded, chunking the text and storing the vectors locally. A typical ten-page PDF
takes just a few seconds.


---
*Page 8*


✕ Remove Ads
   Ad  
Link copied to clipboard
1 Ad
Ad
From there, chatting with your documents works the way you’d hope. I uploaded five
of my university lecture notes and asked it to summarize some key topics, flag any
mentioned risks, and compare two sections I’d been struggling to reconcile
manually. It handled all three cleanly. Responses include citations that point back to
the specific document sections the answer drew from, so you’re never left
wondering whether the AI made something up or actually found it in your files. That
traceability alone makes it far more trustworthy than a generic chatbot for real work.
Agents and slash commands push AnythingLLM
beyond a smart search box
This is the part where it gets really interesting


---
*Page 9*


   Ad  
Link copied to clipboard
1 Ad
✕ Remove Ads
Ad
Mountain fun for everyone.
Sponsored by: Roundtop
AnythingLLM ships with agentic capabilities that go well beyond simple document
Q&A. Typing @agent in the chat activates an AI agent that can perform tool-calling
tasks: web search, deeper research, and cross-app actions. Custom agent skills are
available through the AnythingLLM Community Hub, where the library is growing
steadily. The slash command feature lets you build and save prompt templates for
repetitive tasks — things like summarizing meeting notes in a consistent format,


---
*Page 10*


drafting email replies in a particular tone, or extracting specific fields from uploaded
   Ad  
Link copied to clipboard
documents every time. 1 Ad
RELATED
Feb 28, 2025
What Are AI Agents and How Do They Work?
AI Agents can help you solve complex problems, but how do they
actually work?
By Jayric Maning | 
✕ Remove Ads
Ad
If you want to go further, there’s a browser extension that lets you interact with your
AnythingLLM instance from any webpage, and a GPTLocalhost integration that
brings the assistant into Microsoft Word directly. Teams that need shared access
can opt for the Docker version, which adds multi-user support, role-based controls,
and white-labeling. The desktop app is more than enough for personal use, but it’s
good to know the path to a team setup exists.
Welcome to the private AI revolution (population: you)
By switching to AnythingLLM, I’ve stopped viewing AI as a service I rent and started
viewing it as a utility I own. My documents stay on my drive, my queries stay private,


---
*Page 11*


and I now have a digital assistant that actually knows my context, not just the
   Ad  
Link copied to clipboard
general internet. 1 Ad
✕ Remove Ads
Ad
Productivity Artificial… Privacy Tips
  
Follow Like Share

THREAD
1
We want to hear from you! Share your opinions in the thread below and remember to keep it respectful.

Reply / Post
Sort by: Popular


---
*Page 12*


 Lissa   Ad  
Link copied to clipboard
1 Ad
2026-02-22 05:39:08
Hope to have a brand new start this week sometime. Possiblely today so stay tuned in and please keep
updated. As well as for the me too. And for as Donnie , he dead. He and I... Love to see some action soon or I
may as well leave too then ok Sir!
   Copy
Terms |Privacy |Feedback
✕ Remove Ads
Ad
Mountain fun for everyone.
Sponsored by: Roundtop

RECOMMENDED
6 days ago Feb 15, 2026 Feb 4, 2026
OpenClaw's creator has This brilliant new Android I changed how I search on
joined OpenAI — here's keyboard makes typing Google, and it actually
why that's a big deal effortless works better now


---
*Page 13*


   Ad  
Link copied to clipboard
1 Ad
Ad
Join Our Team
Our Audience
About Us
Press & Events
Media Coverage
Contact Us
Follow Us
     
Advertising
Careers
Terms
Privacy
Policies
MUO is part of the Valnet Publishing Group


---
*Page 14*


   Ad  
Link copied to clipboard
1 Copyright ©A 20d26 Valnet Inc.