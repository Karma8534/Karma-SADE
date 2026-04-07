# medium(2)

*Converted from: medium(2).PDF*



---
*Page 1*


Open in app
Search Write
Pub Crawl is coming back, March 11–12! Register Now!
Data Science Col…
8 Python Libraries That
Made My AI Agents
Actually Work
The Stack I Wish I Found Sooner
Paolo Perrone Follow 6 min read · Feb 3, 2026
1.2K 17
Let me be blunt: I used to be that guy. The one who
built every agent component from scratch.
Need memory? “I’ll just implement a vector store
wrapper.” Want retries? “Give me an hour and
some try-except blocks.”


---
*Page 2*


Three weeks and 400 lines later, I had a memory
system with a bug where duplicate entries
corrupted my entire index. The actual agent logic?
Maybe 50 lines.
So today, I’m breaking down 8 libraries that made
my custom code obsolete. These aren’t just
popular. They’re practical, cleanly designed, and
solve real agent pain with elegance.


---
*Page 3*


1. LiteLLM — Because Provider Lock-In Is
for Suckers
Your agent works with GPT-4. Now you want to test
Claude. Congrats, you’re rewriting your API layer.
from litellm import completion
response = completion(model="gpt-4", messages=[{"role
response = completion(model="claude-3-opus-20240229",
response = completion(model="ollama/llama2", messages
One interface. 100+ models. Switch providers by
changing a string.
I ran a cost comparison last quarter: same
workload, GPT-4 vs Claude Sonnet vs Llama 3 70B.
Difference was $847/month. Without LiteLLM,
testing that would’ve taken a week of refactoring.
✔
Use it for: Multi-model testing, provider
fallbacks, cost optimization


---
*Page 4*


󰡇
Pro tip: Set up automatic fallbacks. When
OpenAI goes down (and it will), your agent
switches to Anthropic without you waking up.
2. Instructor — Because LLMs Lie About
JSON
You ask for JSON. You get JSON with markdown
backticks. Or extra fields. Or a string that looks like
JSON but isn’t.
import instructor
from pydantic import BaseModel
from openai import OpenAI
client = instructor.from_openai(OpenAI())
class UserInfo(BaseModel):
name: str
age: int
user = client.chat.completions.create(
model="gpt-4",
messages=[{"role": "user", "content": "Extract: J
response_model=UserInfo
)


---
*Page 5*


Guaranteed valid output. If extraction fails,
Instructor shows the model what went wrong and
retries automatically.
Before Instructor, I had a 150-line parse_llm_json()
function with twelve edge cases. It still failed on
production data about once a week. Now? Zero
parsing errors in four months.
✔
Use it for: Any structured extraction, tool call
parsing, data pipelines
💡
Insight: Pairs perfectly with Pydantic AI. Same
philosophy, different layers.
3. Tenacity — Because APIs Will Betray
You at 3am
APIs fail. Networks timeout. Rate limits hit. Your
agent crashes and you wake up to angry Slack
messages.
from tenacity import retry, stop_after_attempt, wait_


---
*Page 6*


@retry(stop=stop_after_attempt(3), wait=wait_exponent
def call_flaky_api():
return external_service.get_data()
Exponential backoff, jitter, custom retry
conditions. Wrap any function and forget about
transient failures.
I once had nested try-except blocks four levels
deep. Still missed edge cases. One Sunday morning
I got 47 Slack alerts because a third-party API
returned 503s for 20 minutes and my “robust”
error handling just logged and moved on.
✔
Use it for: Every external API call. Every single
one.
⚠
Warning: Don’t retry on 4xx errors. You’ll just
get rate limited faster.
4. Logfire — Because “Processing
Complete” Is Not Debugging


---
*Page 7*


Your agent did something weird. The logs say
“Processing complete.” You have no idea what
happened between input and output.
import logfire
logfire.configure()
@logfire.instrument("process_user_request")
def handle_request(user_input: str):
logfire.info("Received input", input=user_input)
result = agent.run(user_input)
logfire.info("Agent complete", result=result, tok
return result
Structured, searchable observability. See exactly
what your agent did, what the LLM returned, and
where things went wrong.
Last month I spent 3 hours debugging why an
agent kept recommending the wrong product.
Turns out the retrieval step was returning stale
data. With proper observability, I would’ve seen it
in 5 minutes. Logfire fixed that.


---
*Page 8*


✔
Use it for: Production debugging, token
tracking, latency monitoring
󰡇
Pro tip: Integrates with Pydantic. Your
structured data gets logged with full type
information automatically.
Quick pause: If you’re building agents and want
more breakdowns like this, this, follow me. No
😉
hype, no affiliate links.
5. Diskcache — Because You Don’t Need
Redis for Everything
Your agent calls the same API with the same inputs
constantly. You’re burning money and adding
latency for no reason.
from diskcache import Cache
cache = Cache('./agent_cache')


---
*Page 9*


@cache.memoize(expire=3600)
def expensive_embedding(text: str):
return openai.embeddings.create(input=text, model
Persistent, file-based cache. Survives restarts.
Handles concurrent access. No Redis server to
maintain.
I added Diskcache to an embedding pipeline that
was making 10K+ calls per day. Many were
duplicates. API costs dropped 34% the first week.
Should’ve done it months earlier.
✔
Use it for: Embedding caches, API response
caching, expensive computation memoization
💡
Insight: Multiple agent processes can share the
same cache without corruption. Tested this the
hard way.
6. Tiktoken — Because Guessing Token
Counts Is How Production Incidents Start


---
*Page 10*


Your agent stuffs context until it hits the limit, then
crashes with a cryptic API error. Or worse, silently
truncates important information.
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4")
def fits_in_context(messages: list, max_tokens: int =
total = sum(len(enc.encode(m["content"])) for m i
return total < max_tokens
Counts tokens exactly how OpenAI counts them.
Know before you send.
I used to estimate tokens by dividing character
count by 4. Worked fine until a customer uploaded
a document heavy on code and special characters.
My estimate said 6K tokens. Actual count was 11K.
Agent crashed mid-conversation. Customer was
not impressed.
✔
Use it for: Context window management, cost
estimation, smart truncation


---
*Page 11*


⚠
Warning: Character-based estimates are wrong
30% of the time on real data. Don’t learn this the
way I did.
7. Rich — Because Print Debugging
Shouldn’t Hurt Your Eyes
Your agent prints a 500-line JSON blob. You scroll.
You squint. You give up and add more print
statements.
from rich.console import Console
from rich.table import Table
from rich import print_json
console = Console()
print_json(data=agent_response)
table = Table(title="Agent Actions")
table.add_column("Step")
table.add_column("Tool")
table.add_column("Result")
for step in agent.history:
table.add_row(str(step.num), step.tool, step.resu
console.print(table)
Tables, syntax highlighting, progress bars, tree
views. Debug output you can actually read.


---
*Page 12*


✔
Use it for: Development debugging, demo
outputs, CLI interfaces
😏
Real talk: from rich import print replaces built-
in print. One import, instant upgrade. I demo'd an
agent to a client last month and the Rich-formatted
output got more compliments than the agent itself.
8. Watchfiles — Because Your Iteration
Loop Is Killing Your Productivity
You change a prompt, restart the agent, wait for it
to initialize, test, realize you made a typo, restart
again…
from watchfiles import run_process
def main():
from my_agent import Agent
agent = Agent()
agent.run_interactive()
if __name__ == "__main__":
run_process("./", target=main)


---
*Page 13*


Detects changes, triggers reloads. Your agent
restarts automatically when you save.
I tracked my workflow for a day before using this. I
was restarting my agent 40+ times. Each restart
took 8 seconds. That’s over 5 minutes of waiting.
Per day. For weeks.
✔
Use it for: Local development, prompt
iteration, rapid prototyping
󰡇
Pro tip: Smart about which changes matter.
Modify a prompt file, instant reload. Save a log file,
no reload.
The Meta-Lesson
Each library does one thing well. That’s not an
accident.
When I started building agents, I reached for
frameworks that promised to handle everything.
They were complex, opinionated, and brittle.
When something broke, I was debugging the


---
*Page 14*


framework instead of my agent. (I wrote about why
most AI agents fail in production and this is one of
the reasons.)
Now I compose small libraries. LiteLLM for model
calls. Instructor for structured outputs. Tenacity
for retries. Each piece is replaceable. Each piece is
understandable.
The best agent architecture isn’t the most
sophisticated. It’s the one where you can trace any
bug in five minutes.
If this helped, give it 50 claps. It
tells Medium to show it to more
people. Follow me for more no-BS
breakdowns.


---
*Page 15*


Building your first agent? Start with the complete
LangGraph guide. 110K readers found it useful.
Artificial Intelligence Machine Learning Programming
Software Development Software Engineering
Published in Data Science Collective
Follow
896K followers · Last published 18 hours ago
Advice, insights, and ideas from the Medium data
science community
Written by Paolo Perrone
Follow
9.6K followers · 165 following
✍
Founding Editor Data Science Collective | 110k+
🤖
followers on LinkedIn | Join The Tech Audience
👉
Accelerator https://shorturl.at/rBsrt
Responses (17)


---
*Page 16*


To respond to this story,
get the free Medium app.
Suresh Alokam
Feb 4
Very useful. Thanks for sharing.
5
Asma Taamallah
Feb 4
✨
Thank you for this insightful content
2
Brit Tadesse they/them
Feb 5
I love how cleanly you broke this down, it’s such a relief to see someone
admit how much time gets wasted reinventing pieces that already exist.
The way you framed each library as a single, composable building block.
It’s the kind of architecture… more
1
See all responses


---
*Page 17*


More from Paolo Perrone and Data Science
Collective
In by In by
Data Science Co… Paolo Pe… Data Science Co… Shengga…
RAG Systems in 5 Why Building AI Agents
L l f Diffi lt I M tl W t f
From “it should work” to “it The Structural, Mathematical,
t ll k i d ti ” d E i Li it f RAG
Jan 19 Jan 12
In by In by
Data Science Col… Marina … Data Science Co… Paolo Pe…
AI Agents: Complete You’re Using AI to Write
C C d Y ’ N t U i
From beginner to intermediate 7 prompts for the security,
t d ti hit t d


---
*Page 18*


Dec 6, 2025 Jan 13
See all from Paolo Perrone See all from Data Science Collective
Recommended from Medium
In by Reza Rezvani
Product Not… Mohit Aggar…
I Tested Every Major
The 2026 AI Agent
Cl d O 4 6
R l ti 7 T l
After 24 hours of real testing
Forget chatbots. The real
d il kfl
l ti i AI t th t
Feb 3 Feb 6


---
*Page 19*


Joe Njenga In by
Data Science Co… Paolo Pe…
I Tested (New) Claude
RAG Systems in 5
C d /I i ht (It
L l f Diffi lt
Claude Code Insights is a new
From “it should work” to “it
d th t l
t ll k i d ti ”
Feb 5 Jan 19
In by In by
Level Up Cod… Teja Kusire… Activated Thin… Shane Coll…
I Stopped Using Sam Altman Just
Ch tGPT f 30 D D d 8 H d T th
91% of you will abandon 2026 In a candid, unscripted Q&A,
l ti b J 10th th O AI CEO di tl d
Dec 28, 2025 Jan 27
See more recommendations