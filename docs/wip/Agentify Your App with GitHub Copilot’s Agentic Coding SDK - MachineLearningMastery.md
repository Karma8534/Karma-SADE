# Agentify Your App with GitHub Copilot’s Agentic Coding SDK - MachineLearningMastery

*Converted from: Agentify Your App with GitHub Copilot’s Agentic Coding SDK - MachineLearningMastery.PDF*



---
*Page 1*


GET STARTED BLOG TOPICS  EBOOKS FAQ ABOUT
CONTACT Searc
Learn more
Agentify Your App with GitHub Copilot’s Agentic
Coding SDK
by Shittu Olumide on February 18, 2026 in Artificial Intelligence  0
Share Share Post
In this article, you will learn how to build and embed an agentic Python assistant using the GitHub
Copilot Agentic Coding SDK, including custom tools and multi-turn context.
Topics we will cover include:
How agentic assistants differ from traditional automation and chat-style tools.
How to set up the GitHub Copilot SDK in Python and run a basic tool-using agent.
How to add file-access tools, permission handling, and multi-turn memory.
Let’s not waste any more time.



---
*Page 2*


Agentify Your App with GitHub Copilot’s Agentic Coding SDK (click to enlarge)
Image by Editor
Introduction
For years, GitHub Copilot has served as a powerful pair programming tool for programmers,
suggesting the next line of code. The new GitHub Copilot Agentic Coding SDK changes the game,
transforming Copilot from a reactive helper into an autonomous assistant you can integrate into
your applications. Imagine assigning a complex task to a junior developer who can plan, execute,
and report back — that’s the power of an agent.
In this article, I will guide you through building your first agentic Python application using this SDK.
Think of a traditional coding tool as a very smart keyboard that predicts the next word. An AI agent
is more like a dedicated assistant that you set a goal for, and it figures out the steps, uses the right
tools, and gets the job done without needing your help for every single decision. For a data
scientist, this could mean creating an agent that, when given a raw dataset, can autonomously
clean it, run an analysis, and generate a report.
This new approach allows you to move beyond simple automation to creating systems that
understand context and make decisions. Here’s a comparison of the two paradigms:


---
*Page 3*


TRADITIONAL
ASPECT AGENTIC ASSISTANT (VIA SDK)
AUTOMATION/CHAT
Interaction Single-turn query and Multi-turn, goal-oriented conversation
response
Capability Answers questions, suggests Plans, executes commands, edits files, runs tests
code
Integration External tool or IDE plugin Programmatically embedded into your own Python,
Node.js, Go, or .NET apps
Complexity Manages simple prompts Handles context, tool orchestration, and permissions
for you
How To Get Started With Your First Agent Using
Python
We are going to demo how to integrate the GitHub Copilot SDK into a Python application.
The SDK exposes the same agentic engine behind Copilot CLI as a programmable SDK.
Prerequisites
1. GitHub Copilot Subscription
A GitHub Copilot plan with a Free tier available with limited usage (Installation
guide)
Sign up at github.com/features/copilot
2. On Windows
Navigate to your project directory using the command
cd
1 cd path\to\your\project
Create your virtual environment.
1 python -m venv myenv
Activate it.
1 myenv\Scripts\activate.bat


---
*Page 4*


On Linux/macOS
Navigate to your project directory using the command
cd
1 cd path\to\your\project
Create a virtual environment.
1 python3 -m venv .venv
Activate it.
1 source .venv/bin/activate
3. GitHub Copilot CLI
Install via npm:
1 npm install -g @github/copilot
Verify installation:
1 copilot --version
4. Python 3.10+: The SDK requires Python 3.10 or higher
5. Python Packages
1 pip install github-copilot-sdk pydantic
Output:


---
*Page 5*


Authentication: The Copilot CLI uses your VS Code/GitHub authentication automatically.
Make sure you’re logged into GitHub in VS Code with Copilot enabled. You can also run this
command:
1 copilot -p "Hello" --allow-all-tools
Note: If the CLI is installed via VS Code’s Copilot extension, you may need to specify the CLI path
explicitly like this:
1 client = CopilotClient({
2 "cli_path": "path/to/copilot.cmd", # if you’re on Windows
3 # or "copilot" if it's in your PATH
4 })
Then you can create a Python file and give it a name like basic_agent_demo.py. Then paste the
following code in the file:
1 import asyncio
2 import sys
3 from copilot import CopilotClient
4 from copilot.tools import define_tool
5 from copilot.generated.session_events import SessionEventType


---
*Page 6*


6 from pydantic import BaseModel, Field
7
8 # Step 1: Define custom tools using the @define_tool decorator.
9 class GetDataVisualizationParams(BaseModel):
10 library_name: str = Field(description="The name of the Python library to get info abo
11
12
13 @define_tool(description="Get information about a Python data visualization library")
14 async def get_library_info(params: GetDataVisualizationParams) -> dict:
15 """Custom tool that provides information about data visualization libraries."""
16 libraries = {
17 "matplotlib": {
18 "name": "Matplotlib",
19 "use_case": "Foundational plotting library for static, animated, and interact
20 "install": "pip install matplotlib",
21 "popularity": "Most widely used, basis for many other libraries",
22 },
23 "seaborn": {
24 "name": "Seaborn",
25 "use_case": "Statistical data visualization with attractive default styles",
26 "install": "pip install seaborn",
27 "popularity": "Great for exploratory data analysis",
28 },
29 "plotly": {
30 "name": "Plotly",
31 "use_case": "Interactive, publication-quality graphs for dashboards",
32 "install": "pip install plotly",
33 "popularity": "Best for web-based interactive visualizations",
34 },
35 }
36
37 library = params.library_name.lower()
38 if library in libraries:
39 return libraries[library]
40 return {"error": f"Library '{library}' not found. Try: matplotlib, seaborn, or plotly
41
42
43 async def main():
44 # Step 2: Create and start the Copilot client with an explicit CLI path.
45 # The SDK needs to find the Copilot CLI, so specify the path explicitly.
46 client = CopilotClient({
47 "cli_path": "C:\nvm4w\nodejs\copilot.cmd", # Path to Copilot CLI
48 "log_level": "debug", # Enable debug logging for troubleshooting
49 })
50
51 print(" GitHub Copilot SDK Demo - Agentic Coding in Action")
52 print(" Starting Copilot client (this may take a moment)...\n")
53
54 await client.start()
55
56 print("=" * 60)
57
58 # Step 3: Create a session with custom configuration.
59 session = await client.create_session({
60 "model": "gpt-4.1", # Choose a model
61 "streaming": True, # Enable streaming responses
62 "tools": [get_library_info], # Register custom tools
63 "system_message": (
64 "You are a helpful technical assistant for data scientists. "
65 "When asked about visualization libraries, use the get_library_info tool "
66 "to provide accurate information."
67 ),
68 })
69
70 print(f"Session created: {session.session_id}\n")


---
*Page 7*


71
72 # Step 4: Set up event handlers for streaming.
73 def handle_event(event):
74 if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
75 # Stream the response as it arrives.
76 sys.stdout.write(event.data.delta_content)
77 sys.stdout.flush()
78 elif event.type == SessionEventType.TOOL_EXECUTION_START:
79 print(f"\n Tool called: {event.data.tool_name}")
80
81 session.on(handle_event)
82
83 # Step 5: Send a prompt and let the agent work.
84 print(" User: List three common Python libraries for data visualization and their m
85 print(" Assistant: ", end="")
86
87 await session.send_and_wait({
88 "prompt": (
89 "List three common Python libraries for data visualization and their main use
90 "Use the get_library_info tool to get accurate information about each one."
91 )
92 })
93
94 print("\n\n" + "=" * 60)
95
96 # Step 6: Clean up.
97 await session.destroy()
98 await client.stop()
99
100 print(" Session ended successfully!")
101
102
103 if __name__ == "__main__":
104 asyncio.run(main())
Code Explanation
First, we import everything we need, then define a custom tool with a Pydantic model for its
parameters. The agent can call this tool to retrieve library information from local data. Next, we
initialize and start the SDK client, which connects to the Copilot CLI.
We then create an agentic session with:
Model selection ( )
gpt-4.1
Streaming enabled
Custom tools registered
System instructions
From there, we subscribe to real-time events to display streamed responses and tool calls. We send
a prompt, and the agent autonomously decides to call our custom tool three times to gather
information before responding.
Finally, we clean up by destroying the session and stopping the client gracefully.
Output:


---
*Page 8*


This simple example shows the core pattern of defining tools, starting a session, and running
prompts. The SDK manages the complex orchestration, including autonomous tool selection and
execution, letting you focus on building your application’s logic.
Building a More Capable Agent That Adds Tools and
Memory
An agent’s true power comes from using tools (like reading files or executing code) and maintaining
context across multiple interactions. Let’s build a more advanced agent that can analyze a directory
and remember our conversation.
Creating an Agent with File Access
The example below demonstrates a more complex setup where the agent can use tools to interact
with the file system, and we maintain a conversation thread for context.
1 import asyncio
2 import sys
3 from copilot import CopilotClient
4 from copilot.tools import define_tool
5 from copilot.generated.session_events import SessionEventType
6 from pydantic import BaseModel, Field
7
8
9 # Permission request handler - uses the correct SDK types
10 def on_permission_request(request, invocation):
11 """Handle requests to use tools like reading files."""
12 print(f"\n Agent wants to perform: {request.get('tool_name', 'unknown action')}")
13 # Auto-approve for this demo, or add logic for user input.
14 return {"decision": "allow"}
15
16
17 async def main():


---
*Page 9*


18 # 1. Create the Copilot client.
19 client = CopilotClient({
20 "cli_path": "C:\nvm4w\nodejs\copilot.cmd",
21 "log_level": "info",
22 })
23
24 print("GitHub Copilot SDK Demo - Multi-Turn Conversation")
25 print("Starting Copilot client...\n")
26
27 await client.start()
28 print("=" * 60)
29
30 # 2. Create a session with permission handling enabled.
31 session = await client.create_session({
32 "model": "gpt-4.1",
33 "streaming": True,
34 "on_permission_request": on_permission_request, # Enable tool approval
35 "system_message": "You help analyze code and data projects.",
36 })
37
38 print(f"Session created: {session.session_id}\n")
39
40 # Event handler for streaming.
41 def handle_event(event):
42 if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
43 sys.stdout.write(event.data.delta_content)
44 sys.stdout.flush()
45 elif event.type == SessionEventType.TOOL_EXECUTION_START:
46 print(f"\n Tool: {event.data.tool_name}")
47
48 session.on(handle_event)
49
50 # 3. First task: Summarize files in the current directory.
51 print("User: List all Python files and summarize what this project does.\n")
52 print("Assistant: ", end="")
53
54 await session.send_and_wait({
55 "prompt": "List all Python files in the current directory and summarize what a typ
56 })
57
58 print("\n")
59
60 # 4. Follow-up: The session remembers context (multi-turn conversation).
61 print("User: For the first file, suggest how to add error handling.\n")
62 print("Assistant: ", end="")
63
64 await session.send_and_wait({
65 "prompt": "For the first file you mentioned, suggest how to add error handling."
66 })
67
68 print("\n\n" + "=" * 60)
69
70 # 5. Clean up.
71 await session.destroy()
72 await client.stop()
73
74 print("Session ended successfully!")
75
76 if __name__ == "__main__":
77 asyncio.run(main())
In this code, the on_permission_request function allows the agent to safely request access to
perform actions like reading your file system. The session is important because it keeps the


---
*Page 10*


conversation history, so your second question can refer to “the first file you mentioned” without
confusion.
Output:
Key Concepts and Best Practices
The following are key concepts and best practices you must have in mind. Building a demo is the
first step. To create robust applications, keep these principles in mind:
You must define clear instructions. Your agent’s instructions parameter is its job
description. Be specific about its role, limitations, and output format.
Use tools strategically: Start by enabling the SDK’s built-in tools (file, shell, Git) for powerful
prototypes. Later, build custom tools (like querying a database) for specialized tasks.
Manage permissions: Always implement a permission handler (as shown above). Never run
agents with unrestricted access in production.
Handle errors gracefully: AI agents can make mistakes. Build validation steps to check their
work, especially for file operations or code generation.
Conclusion
The GitHub Copilot SDK democratizes agentic AI, allowing you to integrate sophisticated, goal-
oriented assistants into your Python applications without building complex orchestration logic from
scratch.
You’ve seen how a few lines of code can create an assistant that understands context, uses tools,
and completes multi-step tasks. The potential applications are vast: automated data pipelines,
intelligent code reviewers, personalized CLI tools, or interactive documentation bots.


---
*Page 11*


To move forward:
Visit the official repository for the latest documentation, detailed
github/copilot-sdk
guides, and more examples in Python and other languages.
Experiment by giving your agent a real, small task from your workflow.
Explore integrating custom tools and MCP servers to connect your agent to external data
and APIs.
Begin your journey into agentic development today. Install the SDK, build a small project, and
discover how to offload complex, reasoning-based tasks to your new AI-powered assistant.
Learn More
Authentication Guide GitHub OAuth, environment variables, and BYOK
BYOK (Bring Your Own Key) use your own API keys from Azure AI Foundry, OpenAI, etc.
Node.js SDK Reference
Python SDK Reference
Go SDK Reference
.NET SDK Reference
Using MCP Servers Integrate external tools via Model Context Protocol
GitHub MCP Server Documentation
MCP Servers Directory
Share Share Post
More On This Topic
5 Agentic Coding Tips & Practical Agentic Coding The 3 Invisible Risks Every
Tricks with Google Jules LLM App Faces (And
How…


---
*Page 12*


Stop Coding Machine 3 Ways Vibe Coding and The Roadmap for
Learning Algorithms From AI-Assisted Development Mastering AI-Assisted
Scratch Are 2… Coding in 2025
About Shittu Olumide
Shittu Olumide is a software engineer and technical writer passionate about leveraging cutting-edge technologies
to craft compelling narratives, with a keen eye for detail and a knack for simplifying complex concepts. You can
also find Shittu on Twitter.
View all posts by Shittu Olumide →
 LLM Embeddings vs TF-IDF vs Bag-of-Words: Which Works Better in Scikit-learn?
Building a Simple MCP Server in Python 
No comments yet.
Leave a Reply


---
*Page 13*


Name (required)
Email (will not be published) (required)
SUBMIT COMMENT
Welcome!
I'm Jason Brownlee PhD
and I help developers get results with machine learning.
Read more
Never miss a tutorial:
Picked for you:
Your First Deep Learning Project in Python with Keras Step-by-Step
Your First Machine Learning Project in Python Step-By-Step
How to Develop LSTM Models for Time Series Forecasting


---
*Page 14*


How to Create an ARIMA Model for Time Series Forecasting in Python
Machine Learning for Developers
Loving the Tutorials?
The EBook Catalog is where
you'll find the Really Good stuff.
>> SEE WHAT'S INSIDE
Machine Learning Mastery is part of Guiding Tech Media, a leading digital media publisher focused
on helping people figure out technology. Visit our corporate website to learn more about our
mission and team.
PRIVACY | DISCLAIMER | TERMS | CONTACT | SITEMAP | ADVERTISE WITH US
© 2026 Guiding Tech Media All Rights Reserved