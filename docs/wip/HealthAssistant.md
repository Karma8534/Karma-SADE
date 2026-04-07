# HealthAssistant

*Converted from: HealthAssistant.PDF*



---
*Page 1*


Open in app
Search Write
Level Up Coding
Member-only story
Build an Agentic
Personal Health
Companion with Mem0
and CrewAI
Learn to build a multi-agentic personal health
companion with long-term memory using
Mem0 and CrewAI.
Dr. Ashish Bamania Following 9 min read · 1 hour ago
41


---
*Page 2*


AI agents are becoming hugely popular, and
building them is an essential skill for an AI
engineer.
In this lesson, we will learn to build a multi-agent
system that can monitor personal health
issues/comorbidities and act as a long-term health
companion.
The tools that we will use are:
CrewAI: Framework for building multi-agent
systems
Mem0: Persistent memory layer for LLMs


---
*Page 3*


If you’re completely new to building agents with
CrewAI, the following lesson will help you get
started.
Building Your First AI Agent (That Will
A t ll I Y A A AI E i )
A guide to building a helpful Multi-agent AI
t th t h l fi d th b t AI
www.intoai.pub
Let’s begin!
Overview of the Multi-Agent System
We intend to build a health companion that
manages chronic health conditions/ comorbidities
using three specialized AI agents that work
together sequentially.
These agents are:
1. Comorbidity Analyst: Determines how different
medical conditions affect each other and flags


---
*Page 4*


dangerous medication interactions.
2. Lifestyle Optimizer: Helps find the best lifestyle
changes that improve these medical conditions
3. Care Coordinator: Turns all the advice from the
other two agents into an action plan that
includes targets, timelines to achieve them, and
questions the user must ask their doctor at the
next visit
Alongside these capabilities, the health companion
uses long-term memory to remember one’s
medical history, medications, lab results, advice
from past consultations, and changes in clinical
conditions since those consultations.
The architectural pipeline of this multi-agent
system is shown below.


---
*Page 5*


Architectural pipeline of the multi-agentic health companion
Building the Multi-Agent System
To simplify the build, I have used Google Colab to
write and run all the code.
We start by installing the required packages for
CrewAI and Mem0 using uv.
!uv pip install crewai crewai-tools mem0ai -q


---
*Page 6*


Next, we import the necessary packages as follows.
import os
from mem0 import MemoryClient
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
Then, we set the required API keys for:
Mem0: for persistent memory (You can obtain
this API key here)
OpenAI: for its models to be used as agents
Serper: To search Google for free (You can obtain
this API key free of cost and without using a
credit card by using this link.)
(Note that a more secure way to use API keys on
Google Colab can be found here.)
os.environ["MEM0_API_KEY"] = "your_mem0_api_key"
os.environ["OPENAI_API_KEY"] = "your_openai_api_key"
os.environ["SERPER_API_KEY"] = "your_serper_api_key"


---
*Page 7*


Following this, we initialize Mem0, Serper as a
search tool, and create an ID for the user
# Initialize Mem0 memory
memory = MemoryClient()
# Initialize Serper Google search tool
search_tool = SerperDevTool()
# User ID to be used in Mem0 records
USER_ID = "health_user_1"
Next, we create a dummy past conversation with
the user. This is used to onboard them and fetch
relevant memories. This conversation could come
from an automated form or their conversation
with an AI agent, if you’re building an application
for production.
def onboard_user(user_id):
conversation = [
{
"role": "user",
"content": (
"I'm 58 years old, male, 5'10, 100 kg
"I was diagnosed with Type 2 diabetes


---
*Page 8*


),
},
{
"role": "assistant",
"content": "What medications are you curr
{
"role": "user",
"content": (
"Metformin 1g twice daily for diabete
"for blood pressure. I also take a st
),
},
{
"role": "assistant",
"content": "Any other medical conditions
{
"role": "user",
"content": (
"I have stage 2 chronic kidney diseas
"Last HbA1C was 6.8%. Blood pressure
"My total cholesterol is 210, LDL is
),
},
{
"role": "assistant",
"content": "How active is your lifestyle,
{
"role": "user",
"content": (
"I've a sedentary, desk job. I try to
"Diet is not great tbh, its lots of p
"I quit smoking 5 years ago. I drink
),
},
]


---
*Page 9*


memory.add(conversation, user_id = user_id)
print(f"Onboarded {user_id}!")
onboard_user(USER_ID)
# Output: Onboarded health_user_1!
These memories can be retrieved as follows.
results = memory.get_all(user_id = USER_ID)
for result in results:
print(f"- {result['memory']}\n")
The returned memories are shown below.
- User has a sedentary desk job, walks about 20 minut
- User has stage 2 chronic kidney disease with estima
- User is taking Metformin 1g twice daily for diabete
- User was diagnosed with Type 2 diabetes three years
- User is a 58-year-old male, 5'10" tall, weighing 10


---
*Page 10*


Pretty good extraction, right?
You can also navigate to your Mem0 dashboard to
view the newly created entity health_user_1 and
the memories extracted from the onboarding
conversation.
Look at how Mem0 automatically categorizes these
memories into:
health
food
professional_details, and
person_details


---
*Page 11*


To ensure our agents can use these memories in
their context, we write a helper function as
follows.
def get_health_context(user_id, query):
memories = memory.search(query, user_id=user_id)
if not memories:
return "User's health profile not found."
lines = [f"- {m['memory']}" for m in memories]
return "User Health Profile:\n" + "\n".join(lines


---
*Page 12*


Note the use of the search method that helps
retrieve the most relevant stored memories for a
user with a natural language query, so that an
agent can use them as context.
It’s now time to build our agents. The following
helper function creates three agents, each with a
role, goal, and backstory.
None of the agents is allowed to delegate their
assigned tasks to other agents (allow_delegation =
False), and they always output detailed logs about
their functioning (verbose = True).
Alongside this, the ‘Lifestyle Optimizer’ agent has
access to the search_tool to search Google to help
it find the best advice.
def create_agents(context):
# Comorbidity Analyst agent
comorbidity_analyst = Agent(
role = "Comorbidity Analyst",
goal = (
"Analyze how the user's conditions intera


---
*Page 13*


"the highest-risk comorbidity combination
),
backstory = (
f"You are an internal medicine specialist
f"with multiple chronic conditions. Your
f"each other's risks. \n{context}\n\n"
),
allow_delegation = False,
verbose = True,
)
# Lifestyle Optimizer agent
lifestyle_optimizer = Agent(
role = "Lifestyle & Prevention Optimizer",
goal = (
"Create specific and achievable lifestyle
"multiple conditions simultaneously. Prio
"highest cross-condition impact."
),
backstory = (
f"You are a certified health coach specia
f"management through lifestyle change. Yo
f"with multiple conditions need unified p
f"\n{context}\n\n"
),
allow_delegation = False,
tools = [search_tool],
verbose = True,
)
# Care Coordinator agent
care_coordinator = Agent(
role = "Care Plan Coordinator",
goal = (
"Convert the comorbidity analysis and lif


---
*Page 14*


"into a single prioritized care plan with
"timelines, and monitoring checkpoints."
),
backstory = (
f"You are a care coordinator who creates
f"for complex patients. You turn speciali
f"action items. \n{context}\n\n"
f"IMPORTANT: Always include a disclaimer
f"guidance and not a substitute for profe
),
allow_delegation = False,
verbose = True,
)
return comorbidity_analyst, lifestyle_optimizer,
Next, we create tasks for these AI agents using
another helper function. Note how the
care_coordination_task depends on the outputs of
comorbidity_analysis_task and
lifestyle_optimization_task.
def create_tasks(agents, user_question):
comorbidity_analyst, lifestyle_optimizer, care_co
# Task for Comorbidity Analyst agent
comorbidity_analysis_task = Task(
description = (
f"User asks: '{user_question}'\n\n"


---
*Page 15*


f"Analyze how their medical conditions in
f"Identify the most dangerous feedback lo
f"Check for any medication interactions o
f"Highlight which lab values are most cri
),
expected_output = (
"A comorbidity interaction map that shows
"medication interactions, and a ranked li
),
agent = comorbidity_analyst,
)
# Task for Lifestyle Optimizer agent
lifestyle_optimization_task = Task(
description = (
f"User asks: '{user_question}'\n\n"
f"Research and recommend specific lifesty
f"Be specific with exact dietary targets,
),
expected_output = (
"A set of 4-6 lifestyle modifications wit
f"which conditions each one helps, and a
),
agent = lifestyle_optimizer,
)
# Task for Care Coordinator agent
care_coordination_task = Task(
description = (
f"User asks: '{user_question}'\n\n"
f"Using the comorbidity analysis and life
f"create a unified action plan. Include s
f"a monitoring schedule (what to check an
f"questions the patient should ask their
),


---
*Page 16*


expected_output = (
"A prioritized care plan with weekly acti
"monitoring schedule, and a list of quest
"in simpler language avoiding medical jar
"Must include a medical disclaimer."
),
agent = care_coordinator,
context = [comorbidity_analysis_task, lifesty
)
return [comorbidity_analysis_task, lifestyle_opti
Our final helper function creates a crew from
these agents and runs them sequentially. It stores
the crew output in Mem0 memory and returns it
for us to visualise.
def run_health_advisor(user_id, user_question):
# Create health context
health_context = get_health_context(user_id, user
# Create agents
agents = create_agents(health_context)
# Create tasks for agents
tasks = create_tasks(agents, user_question)
# Initialize the multi-agent crew
crew = Crew(
agents = list(agents),


---
*Page 17*


tasks = tasks,
process = Process.sequential,
verbose = True,
)
# Run the crew
result = crew.kickoff()
# Update Mem0 memory with crew result
memory.add(
[
{"role": "user", "content": user_question
{"role": "assistant", "content": str(resu
],
user_id = user_id,
)
print("\n\nConversation stored in memory.")
return str(result)
Time to run the crew and see what it comes up
with.
advice = run_health_advisor(
user_id = USER_ID,
user_question = "My HbA1C today is 8%. What shoul
)


---
*Page 18*


I created a simple frontend to show how these
agents work together and return the final advice.
Here is how it looks.
The memories are updated after this crew runs.
We can check this as follows:
new_memories = memory.search("What is user's latest H
print(new_memories[0]["memory"])
# User has stage 2 chronic kidney disease with estima
# HbA1c on 2026-02-18 is 8% (up from 6.8%), blood pre
# a month ago, total cholesterol 210 mg/dL, LDL 130 m
# apnea using a CPAP machine intermittently.


---
*Page 19*


The Mem0 dashboard now looks as follows. Note
the updated memory at the top.
Important Note
The official Mem0 documentation advises on
creating the crew:
Without manually retrieving the health context
from the Mem0 memory
Without manually adding to the Mem0 memory
after the crew run


---
*Page 20*


# Initialize the multi-agent crew
crew = Crew(
agents = list(agents),
tasks = tasks,
process = Process.sequential,
verbose = True,
memory = True,
memory_config={
"provider": "mem0",
"config": {"user_id": user_id},
}
)
Following this advice still seemed to use CrewAI’s
internal memory mechanisms rather than Mem0.
This is why I have added custom functions to fetch
context and store results in memory after each
crew run.
Source of Images
All images have been created or obtained by the
author unless stated otherwise.


---
*Page 21*


Artificial Intelligence AI Agent Programming Technology
Machine Learning
Published in Level Up Coding
Follow
303K followers · Last published 1 hour ago
Coding tutorials and news. The developer homepage
gitconnected.com && skilled.dev && levelup.dev
Written by Dr. Ashish Bamania
Following
43K followers · 415 following
🍰
I simplify the latest advances in AI & Quantum
📩
Computing for you | Subscribe to my
newsletter: https://www.intoai.pub
No responses yet
To respond to this story,
get the free Medium app.


---
*Page 22*


More from Dr. Ashish Bamania and Level
Up Coding
In by In by
Level Up C… Dr. Ashish B… Level Up C… Dr. Ashish B…
Learn About The Entire All The Basics That You
C t S i N d T K Ab t
A visual tour through the We’re living in an amazing time
ti C t S i h d t di AI
Jan 29 Aug 24, 2025
In by In by
AI Advan… Dr. Ashish Ba… AI Advan… Dr. Ashish Ba…
Universal Reasoning Build and Train an LLM
M d l A D Di f S t h
Learn about what Universal An end-to-end guide to
R i M d l (URM ) t i i LLM f t h


---
*Page 23*


Feb 1 Jan 2
See all from Dr. Ashish Bamania See all from Level Up Coding
Recommended from Medium
In by In by
Activated Thin… Shane Coll… Towards Deep L… Sumit Pa…
Why the Smartest Andrej Karpathy Just
P l i T h A B ilt E ti GPT i
The water is rising fast, and No PyTorch. No TensorFlow.
f i f Ch tGPT J t P th d b i
Feb 13 Feb 15


---
*Page 24*


In by Steve Yegge
Towards AI Florian June
The Anthropic Hive
Cog-RAG: Giving RAG a
Mi d
B i Th t Thi k
As you’ve probably noticed,
Retrieval-Augmented
thi i h i
G ti (RAG) i
Feb 17 Feb 6
In by In by
AI Advanc… Jose Crespo, P… CodeX MayhemCode
Anthropic is Killing Why Thousands Are
Bit i B i M Mi i t
The AI-native currency Something strange happened
l d i t hidi i i l 2026 A l t
Feb 17 Feb 15
See more recommendations