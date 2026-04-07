# MasteringGoogleStuff

*Converted from: MasteringGoogleStuff.pdf*



---
*Page 1*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Open in app
Search Write
Member-only story
Mastering ADK Tools: Function
Tools, MCP Tools, OpenAPI Tools &
When to Use Each | Part-3
Simranjeet Singh Following 48 min read · 4 days ago
56
You’ve built an agent. Now what?
You followed the quickstart. You set up your environment, wrote your first
Agent(...), ran adk run it, and watched Gemini respond to your prompt. It
was satisfying. It felt like the future.
Then you asked it to do something real — check a stock price, query your
database, send a Slack message — and realised the hard truth:
Your agent can think. It can reason. But it can’t do anything yet.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 1/71


---
*Page 2*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Mastering ADK Tools
It’s sitting in a room with no hands. Smart, articulate, completely helpless.
This is the moment that separates a chatbot from an actual agent. And the
gap between the two is closed by exactly one thing: tools.
Tools are what let an agent reach outside its context window and interact
with the world — call APIs, execute code, query databases, read files, send
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 2/71


---
*Page 3*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
messages. Without tools, your agent is giving advice. With tools, it’s taking
action.
But here’s where it gets interesting: ADK doesn’t have one way to give your
agent tools. It has four completely different tool types, each designed for a
different situation. Pick the wrong one and you’ll either write unnecessary
boilerplate or create a production agent that misuses its capabilities.
By the end of this post, you’ll know exactly which tool type to reach for in
any situation — and why.
We’ll cover every tool type with real, runnable code. We’ll look at how ADK
actually works under the hood (the schema generation magic most
developers miss). And we’ll give you a decision tree you can screenshot and
use on every project.
Let’s build agents that actually do things.
Google ADK In-Depth Series of Learning Agentic AI
1. Google ADK in 2026: The Complete Beginner’s Guide to Building AI
Agents | Part-1
2. Your First Google ADK Agent with Skills: Build a Weather and News Agent
in 30 Minutes | Part-2
3. Mastering ADK Tools: Function Tools, MCP Tools, OpenAPI Tools &
When to Use Each | Part-3
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 3/71


---
*Page 4*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
4. ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with
Google ADK | Part-4
5. Google Agent Skills Explained: The Open Standard Changing How AI
Agents Work | Part-5
6. ADK Memory, Sessions & State: Building Agents That Remember | Part-6
7. Multi-Agent Systems with ADK: Build Your Own AI Research Team | Part-7
8. Gemini CLI + Agent Skills: Supercharge Your Developer Workflow | Part-8
9. Firebase + Agent Skills: Add AI Superpowers to Your Firebase App | Part-9
10. Grounding ADK Agents: Google Search, Vertex AI Search & RAG Patterns |
Part-10
11. ADK + MCP: Connecting Your Agent to Any Tool in the World | Part-11
12. Build a Full-Stack AI SaaS App with Google ADK: From Idea to Live
Product | Part-12
Table of Contents
What is a tool in ADK, really? (The mental model)
Function Tools: your go-to workhorse
MCP Tools: connect to the whole world
OpenAPI Tools: REST APIs without the boilerplate
SkillToolset: context-efficient modular knowledge
The production decision tree
Action confirmations & human-in-the-loop
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 4/71


---
*Page 5*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Tool performance tips
Note: ADK supports 5 tool types in total. This post covers 4 of the custom
types — Function, MCP, OpenAPI, and SkillToolset. Built-in tools (Google
Search grounding, code execution) were covered in Blog 1. If you haven’t set
up ADK yet, start there.
What Is a Tool in ADK, Really?
Before a single line of code, let’s lock in the mental model. Misunderstanding
how tools work in ADK is the #1 cause of bugs, weird agent behaviour, and
tools that never get called.
The Tool Call Lifecycle
When you add a tool to an ADK agent, three things happen on every turn, in
sequence, in a precise order:
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 5/71


---
*Page 6*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Working of Tool in ADK
Step 1: Tool Selection. The LLM receives your message, the agent’s
instructions, and the schemas of every available tool. It reasons about which
tool (if any) to call, and why.
Step 2: Function Calling. The LLM prepares the request — it generates a
structured JSON payload with the tool name and arguments. Critically, the
model is not calling the tool itself. It’s filling out a form that ADK will use to call
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 6/71


---
*Page 7*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
the tool on its behalf. This is called function calling, and it’s the foundational
mechanism behind every ADK tool.
Step 3: Response Interpretation. ADK executes the tool using the payload the
model prepared, captures the result, and feeds it back into the model’s
context. The model reads the result and decides whether to call another tool,
ask for clarification, or respond to the user.
# This is what gets fed BACK to the LLM after ADK executes your tool.
# The model reads this and decides what to do next.
# Notice: the model prepared the call, ADK ran it, now the model interprets the resu
{
"tool_name": "get_weather",
"result": {
"temperature": "28°C",
"condition": "Partly cloudy",
"city": "Bengaluru"
}
}
 
This three-step loop is the heartbeat of every ADK agent. It repeats until the
model decides it has enough information to respond to the user.
The magic ADK beginners Miss: Schema Auto-Generation
Here’s something that trips up nearly every new ADK developer. You write a
Python function and add it to your agent’s tools list. ADK doesn't just store a
reference to that function — it reads it. It inspects:
Your type annotations ( str, int, list[str], Optional[str]) to generate
the JSON schema for each parameter
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 7/71


---
*Page 8*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Your docstring to generate the tool’s description — the text the LLM reads
to decide when to call this tool
Both of these are fed to the LLM on every single turn. Your docstring is your
tool’s prompt. A vague docstring leads to wrong tool selections. A precise
docstring with clear “when to use this” guidance is the difference between a
tool that gets called correctly and one that never fires.
# ADK reads this function and auto-generates a JSON schema like:
# {
# "name": "search_products",
# "description": "Search the product catalog...",
# "parameters": {
# "query": {"type": "string", "description": "The search term..."},
# "category": {"type": "string", "description": "Product category..."},
# "max_results": {"type": "integer", "description": "Maximum number..."}
# }
# }
def search_products(
query: str,
category: str,
max_results: int = 5
) -> dict:
"""
Search the product catalog for items matching the query.
Use this tool when the user asks about available products, inventory,
or wants to find items in a specific category.
Args:
query: The search term to look for in product names and descriptions.
category: Product category filter. Use 'all' for no filter.
max_results: Maximum number of results to return. Defaults to 5.
"""
...
This auto-generation is why missing a type annotation or leaving a vague
docstring silently breaks your agent — the LLM gets an incomplete or
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 8/71


---
*Page 9*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
confusing schema and either misuses the tool or ignores it entirely.
BaseTool and BaseToolset: The two abstractions
Everything in ADK’s tools system descends from one of two abstract base
classes:
BaseTool — a single capability. A function tool, an MCP-exposed
function, or a single REST endpoint from an OpenAPI spec. The LLM
sees it as one callable function.
BaseToolset — a collection of tools resolved at runtime. McpToolset,
OpenAPIToolset, and SkillToolset are all toolsets. When you add a toolset
to your agent, ADK calls get_tools() on it during agent startup to expand
it into individual BaseTool instances.
You don’t need to subclass either of these in day-to-day development. But
knowing this architecture helps you reason about tool initialisation,
filtering, and lazy loading, all of which matter at production scale.
ToolContext: The power feature most developers skip
Some tools need more than just their input arguments. They need to read
session state, write back to it, or know things about the current user or
conversation. That’s where ToolContext comes in.
ToolContext is an object that ADK automatically injects into any function tool
that declares it as a parameter. You never construct it yourself — ADK
handles that. But when it's there, it gives your tool access to:
tool_context.state — the current session's key-value state store. Read
from it (e.g., get the logged-in user's ID) or write to it (e.g., cache an API
result for later turns).
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 9/71


---
*Page 10*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Auth credentials — for tools that need OAuth tokens or API keys resolved
at runtime.
Artifact service — for reading and writing files or binary data within a
session.
Event emitting — for sending intermediate output to the user while a
long-running tool is still executing.
from google.adk.tools import ToolContext
async def get_user_orders(tool_context: ToolContext) -> dict:
"""Retrieve the current user's recent orders."""
# Read from session state - set by auth/login logic earlier in the session
user_id = tool_context.state.get("authenticated_user_id")
if not user_id:
return {"status": "error", "message": "No authenticated user in session."}
orders = await orders_db.get_by_user(user_id)
# Cache the result so other tools can reference it this session
tool_context.state["last_fetched_orders"] = [o.id for o in orders]
return {"status": "success", "orders": [o.to_dict() for o in orders]}
 
You don’t need ToolContext for simple tools. But any production tool that
touches user identity, session memory, or needs to share state between tools
across a multi-turn conversation will need it.
📦
ADK’s 5 Tool Types at a Glance
Tool TypeWhat it isFunction ToolA Python function you write. Full
control.Built-in ToolGoogle-native features: Search grounding, Code
Execution (covered in Blog 1)OpenAPI ToolAuto-generated from a REST API
specMCP ToolA tool exposed by any MCP-compatible serverSkillToolsetA
modular SKILL.md knowledge package
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 10/71


---
*Page 11*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
The remaining sections cover all four custom types — with production-grade
code for each.
Function Tools (Your Go-To Workhorse)
If you only master one tool type in ADK, make it this one. Function tools are
the foundation of almost every real-world agent — they’re the bridge between
the LLM’s reasoning and your actual code. A function tool is simply a regular
Python function that your agent can call. That’s it. No special class to extend,
no config file to maintain. Just a function.
But there’s a lot of depth hiding underneath that simplicity. Let’s peel it back
layer by layer.
The Anatomy of a Perfect Function Tool
Here’s something most tutorials skip: ADK never directly shows the model
your Python code. Instead, it reads your function’s signature and docstring
and converts them into a JSON schema — a structured description of what
the tool does, what arguments it expects, and what it returns. That JSON
schema is what the LLM actually sees when deciding whether and how to
call your tool.
This means your docstring is not documentation for humans. It is a prompt
for the model. Every word matters.
Let’s look at what ADK extracts from a well-written function:
from typing import Optional
def search_products(
query: str,
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 11/71


---
*Page 12*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
category: str,
max_results: int = 5,
in_stock_only: Optional[bool] = None
) -> dict:
"""
Search the product catalog for items matching the query.
Use this tool when the user wants to find, browse, or look up products.
Do NOT use this for checking order status or tracking shipments.
Args:
query: The search term to look for in product names and descriptions.
Be specific — 'red running shoes size 10' works better than 'shoes'.
category: Product category to filter by (e.g., 'footwear', 'electronics').
Use 'all' to search across all categories.
max_results: Maximum number of results to return. Defaults to 5.
Increase to 10 or 20 only if the user explicitly wants more opt
in_stock_only: If True, only return products currently in stock.
If None (default), return all products regardless of availabi
Returns:
dict with 'products' list (each with id, name, price, category, in_stock),
'total_count' integer, and 'status' string ('success' or 'error').
"""
results = product_db.search(
query=query,
category=category,
limit=max_results,
stock_filter=in_stock_only
)
return {
"products": [p.to_dict() for p in results],
"total_count": len(results),
"status": "success"
}
Look at what ADK does with this function — and why each part matters:
 
The function name becomes the tool name the model calls. Use clear, verb-
noun names like, search_products, get_order_status, send_notification.
Avoid abbreviations — the model reads these names literally.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 12/71


---
*Page 13*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Type annotations are not optional. ADK uses them to generate the JSON
schema for each parameter. Here’s the mapping you need to know:
str: string | int: integer | float: number | bool:boolean | list[str]:
array of string | dict: object(Avoid, too vague for the model) |
Optional[str]: string with nullable: true(For truly optional params) | No
⚠
annotation: Omitted from schema ( The model won't know this param exists.)
The docstring body becomes the tool description the model reads on every
agent turn. Notice how the example docstring tells the model when to use
this tool AND explicitly when not to; that negative guidance prevents wrong
tool selections and is one of the most impactful things you can add.
The Args section gives the model per-parameter instructions. This is where
you describe the meaning of each value, not just its type. The difference
between category: str them category: Product category to filter by (e.g.,
'footwear', 'electronics'). Use 'all' to search across all categories. is
enormous at runtime.
The Returns section tells the model what to expect back, so it can reason
correctly about the response.
What should you return?
Always return a dict. Here's why, illustrated with what the model sees for
each return type:
# ❌ Returning a string
return "Found 3 products: Nike Air Max, Adidas Ultraboost, Puma RS-X"
# Model sees: an opaque blob of text. It can't programmatically check
# product count, access individual items, or handle errors gracefully.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 13/71


---
*Page 14*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
# ❌ Returning None (implicitly, by forgetting a return statement)
return
# Model sees: null. It has no idea if the operation succeeded,
# failed, or found zero results. This causes hallucination.
# ✅ Returning a dict
return {
"products": [...],
"total_count": 3,
"status": "success"
}
# Model sees: structured data it can reason about. It knows
# the count, can iterate the list, and can check the status.
The status field deserves special attention. Always include it. When an error
occurs, a structured error response lets the model decide how to recover —
retry with different parameters, tell the user what went wrong, or escalate to
a different tool. Without it, the model guesses:
# ✅ Error handling done right
def get_order_status(order_id: str) -> dict:
"""..."""
try:
order = orders_db.get(order_id)
if not order:
return {
"status": "error",
"error_code": "ORDER_NOT_FOUND",
"message": f"No order found with ID '{order_id}'. Check the ID and t
}
return {
"status": "success",
"order": order.to_dict()
}
except Exception as e:
return {
"status": "error",
"error_code": "DATABASE_ERROR",
"message": "Could not retrieve order. Please try again shortly."
}
 
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 14/71


---
*Page 15*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Pro Tip — Your docstring IS your tool’s prompt. A vague docstring like "Gets
products" produces wrong tool selections, hallucinated parameters, and
agents that call the search tool when they should be checking inventory. Be
explicit: say when to use it, when not to use it, what each argument means,
and what the response structure looks like. Treat it like you're writing
instructions for a brilliant but literal intern who has never seen your
codebase.
Using ToolContext for Power Features
Most function tools don’t need anything beyond their parameters. But when
you need to — read the user’s session data, remember something across
turns, control what the agent does next — ADK gives you the ToolContext.
By including tool_context: ToolContext in your function signature, ADK
automatically provides an instance of the ToolContext class when your tool
is called during agent execution. Google You don't register it, configure it, or
pass it yourself — ADK sees the parameter name and type and handles
injection entirely.
Here’s what ToolContext gives you:
from google.adk.tools import ToolContext
async def process_order(
order_id: str,
tool_context: ToolContext # ← ADK injects this. Don't pass it manually.
) -> dict:
"""
Process and confirm a customer order.
Args:
order_id: The unique identifier of the order to process.
Returns:
dict with 'status', 'order_id', and 'confirmation_number'.
"""
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 15/71


---
*Page 16*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
# ── READ from session state ──────────────────────────────────────────
user_id = tool_context.state.get("user_id")
user_tier = tool_context.state.get("user:membership_tier", "standard")
# Note: "user:" prefix = persists across ALL sessions for this user
if not user_id:
return {"status": "error", "message": "No active user session found."}
# ── WRITE to session state ───────────────────────────────────────────
tool_context.state["last_order_id"] = order_id
# Note: no prefix = persists only within the current session
tool_context.state["temp:processing_flag"] = True
# Note: "temp:" prefix = only lives for the current agent turn
# ── CONTROL agent behaviour after this tool runs ─────────────────────
# tool_context.actions.skip_summarization = True # skip LLM response summary
# tool_context.actions.transfer_to_agent = "payment_agent" # hand off
result = orders_service.process(order_id, user_id, tier=user_tier)
return {
"status": "success",
"order_id": order_id,
"confirmation_number": result.confirmation_id
}
The State Prefix System: One of ADK’s Best-Kept Secrets
ADK has magic state key prefixes like user: and app:, which allow you to
persist state key values either across all user sessions, or across all sessions
with all users.
In the Google Agent Development Kit (ADK), Scope Prefixes determine how
and where your agent stores data. Use no prefix for session-level data like
temporary cart items, or user: for persistent traits like language preferences
 
that survive across multiple interactions. For broader control, app: manages
global settings like feature flags across all users, while temp: is restricted to
a single turn, making it ideal for passing intermediate values or debug flags
without cluttering the agent’s long-term memory.
When you modify context.state, the ADK framework ensures that these
changes are automatically captured and correctly routed into the
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 16/71


---
*Page 17*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
EventActions.state_delta for the event being generated, ensuring proper
persistence and tracking. This means you get audit history and persistence
for free — you just write to the dict.
Reading State Inside Agent Instructions
Here’s a bonus that compounds the power of state writes in tools, ADK lets
your agent’s instruction prompt read state values directly using a {key}
template syntax:
from google.adk.agents import Agent
agent = Agent(
model="gemini-2.5-flash",
name="personal_shopping_agent",
instruction="""
You are a personal shopping assistant for {user:name}.
Their membership tier is: {user:membership_tier}.
Their preferred currency is: {user:preferred_currency}.
Last viewed product: {last_viewed_product_id}.
Greet them by name and tailor all recommendations to their tier.
""",
tools=[search_products, get_order_status, process_order]
)
Once a tool writes tool_context.state["user:name"] = "Priya", every
subsequent agent turn automatically receives a personalised instruction
prompt. No prompt-engineering gymnastics needed.
When Do You Actually Need ToolContext?
A simple decision: if your tool only needs its explicit arguments and returns
a result, skip it. If you need any of the following, reach for it:
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 17/71


---
*Page 18*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Accessing user identity or preferences set earlier in the session
Remembering something across multiple turns (e.g., shopping cart,
multi-step form)
Using actions to control what the agent does after your tool (skip
summarization, transfer to another agent, request credentials for auth)
Accessing artifacts (files, images) stored in the session
Async vs. Sync: Choosing the Right Tool Shape
ADK supports both regular ( def) and async ( async def) function tools
without any extra configuration. Choosing correctly has a real impact on
your agent's responsiveness:
import asyncio
import httpx
from datetime import datetime
# ✅ Use regular def for CPU-bound work (fast, no I/O waiting)
def calculate_discount(
original_price: float,
discount_percentage: float,
member_tier: str
) -> dict:
"""
Calculate the final price after applying a discount.
Use this for price calculations before showing the user a final quote.
Args:
original_price: The original product price in INR.
discount_percentage: Discount to apply as a percentage (0–100).
member_tier: Customer tier ('standard', 'silver', 'gold').
Gold members receive an additional 5% loyalty discount.
Returns:
dict with 'original_price', 'final_price', 'total_savings', 'status'.
"""
bonus = 5.0 if member_tier == "gold" else 0.0
effective_discount = min(discount_percentage + bonus, 100.0)
final_price = original_price * (1 - effective_discount / 100)
savings = original_price - final_price
return {
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 18/71


---
*Page 19*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
"original_price": original_price,
"final_price": round(final_price, 2),
"total_savings": round(savings, 2),
"applied_discount_pct": effective_discount,
"status": "success"
}
# ✅ Use async def for I/O-bound work (API calls, DB queries, file reads)
async def get_live_inventory(
product_id: str,
warehouse_region: str = "IN-South"
) -> dict:
"""
Fetch real-time inventory count for a product from the warehouse API.
Use this when the user asks about stock availability or shipping times.
Do NOT use this for price information - use get_product_details instead.
Args:
product_id: The unique product SKU (e.g., 'NK-AIR-MAX-10-RED').
warehouse_region: The warehouse region to check. Defaults to 'IN-South'
(Bengaluru hub). Use 'IN-North' for Delhi/NCR customers.
Returns:
dict with 'product_id', 'stock_count', 'warehouse_region',
'estimated_dispatch_days', and 'status'.
"""
async with httpx.AsyncClient(timeout=5.0) as client:
try:
response = await client.get(
f"https://warehouse-api.internal/inventory/{product_id}",
params={"region": warehouse_region}
)
response.raise_for_status()
data = response.json()
return {
"product_id": product_id,
"stock_count": data["available_units"],
"warehouse_region": warehouse_region,
"estimated_dispatch_days": data["dispatch_sla_days"],
"status": "success"
}
except httpx.TimeoutException:
return {
"status": "error",
"error_code": "INVENTORY_TIMEOUT",
"message": "Inventory service is slow. Please try again in a moment.
}
except httpx.HTTPStatusError as e:
return {
"status": "error",
"error_code": "INVENTORY_API_ERROR",
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 19/71


---
*Page 20*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
"message": f"Could not fetch inventory (HTTP {e.response.status_code
}
The rule of thumb: if your tool calls await on anything (an HTTP request, a
database query, a file read), make it async def. If it's pure computation,
maths, string processing, data transformation, keep it def. ADK runs both in
the same event loop without any special handling on your part.
One extra note for async tools: always set explicit timeouts (as shown with
httpx.AsyncClient(timeout=5.0)). A hanging tool call blocks the entire agent
turn. In production, a 5–10 second timeout with a clean error response is far
better than leaving the agent, and your user, waiting indefinitely.
The 6 Most Common Function Tool Mistakes
These are the errors that don’t throw exceptions, they just make your agent
quietly worse. Each one is a real production failure pattern:
❌
Mistake 1: Missing type annotations
# Bad — ADK omits un-annotated params from the schema entirely
def get_weather(city, units): # model doesn't know 'units' exists
...
# Good
def get_weather(city: str, units: str = "metric") -> dict:
...
Without type annotations, ADK cannot include that parameter in the JSON
schema it sends to the model. The model literally cannot see the parameter
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 20/71


---
*Page 21*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
exists, so it never passes a value for it.
❌
Mistake 2: Returning raw strings instead of dicts
# Bad
def get_stock_price(symbol: str) -> str:
return f"AAPL is currently trading at $227.50"
# Good
def get_stock_price(symbol: str) -> dict:
return {"symbol": "AAPL", "price": 227.50, "currency": "USD", "status": "success
 
String returns force the model to parse natural language, which it does
inconsistently, especially for downstream tool calls that need specific values
from the response.
❌
Mistake 3: Overly broad or vague docstrings
# Bad — model calls this for EVERYTHING
def get_data(query: str) -> dict:
"""Get data based on a query."""
...
# Good - model knows exactly when to use it
def get_product_reviews(
product_id: str,
min_rating: Optional[int] = None
) -> dict:
"""
Retrieve customer reviews for a specific product.
Use this ONLY when the user asks about reviews, ratings, or customer feedback.
Do NOT use for product specifications, pricing, or inventory.
...
"""
 
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 21/71


---
*Page 22*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
❌
Mistake 4: Too many parameters
The model’s ability to correctly fill in parameters degrades as the count
grows. Beyond 5–7 parameters, wrong values appear with increasing
frequency. The fix is to split into multiple focused tools, or use a single
options: dict parameter for rarely-used configuration — though this
sacrifices schema clarity.
❌
Mistake 5: Silent failures from missing error handling
# Bad — exception propagates up, agent crashes mid-turn
def get_customer_profile(customer_id: str) -> dict:
customer = db.get(customer_id) # throws if customer doesn't exist
return customer.to_dict()
# Good - structured error lets the agent recover gracefully
def get_customer_profile(customer_id: str) -> dict:
"""..."""
try:
customer = db.get(customer_id)
if not customer:
return {"status": "error", "error_code": "NOT_FOUND",
"message": f"Customer '{customer_id}' does not exist."}
return {"status": "success", "customer": customer.to_dict()}
except DatabaseError:
return {"status": "error", "error_code": "DB_UNAVAILABLE",
"message": "Customer database is temporarily unavailable."}
❌
Mistake 6: Registering tools the agent doesn’t need in that context
Every tool in your agent’s tools=[] list is sent to the model on every single
turn — even if the current task has nothing to do with 90% of them. This
inflates your token bill, slows latency, and confuses the model. The
solutions: use SkillToolset for context-aware tool loading (Blog 2), split
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 22/71


---
*Page 23*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
capabilities across specialised sub-agents (Blog 6), or at minimum, curate
tools per agent tightly.
Quick Reference — The Function Tool Checklist
Before registering any function tool, run through this list:
1. Every parameter has a type annotation
2. The docstring says when to use and when NOT to use the tool
3. The Args section explains the meaning — not just the type — of each parameter
4. Returns a dict with a status field
5. Error cases return structured dicts, not exceptions
6. Async for I/O, sync for computation
7. Parameter count is 7 or fewer
8. The tool name is a clear verb-noun pair
That’s the full depth of Function Tools. In the next section, we level up:
connecting your ADK agent to GitHub, Slack, databases, and any other
service in the world; without writing a single wrapper, using MCP Tools.
MCP Tools (Connect to the Whole World)
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 23/71


---
*Page 24*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Function Tools showed you how to build tools that run your own code. This
section shows you how to skip writing the code entirely — and instead
connect your agent to tools that already exist, built by other teams, for
dozens of services you use every day.
That’s what MCP makes possible. And once you understand it, you’ll never
go back to writing API wrappers by hand.
MCP Tools
What MCP Is (and Why It Changes Everything)
The Model Context Protocol (MCP) is an open standard designed to
standardize how Large Language Models communicate with external
applications, data sources, and tools — a universal connection mechanism
that simplifies how LLMs obtain context, execute actions, and interact with
various systems.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 24/71


---
*Page 25*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Before MCP, every agent framework invented its own way of talking to
external services. The result was a fragmented ecosystem: GitHub
integration for LangChain looked nothing like GitHub integration for
AutoGen, and a tool built for one framework couldn’t be reused in another.
MCP was introduced by Anthropic in 2024, and provides an abstraction layer
between your AI agent and tool “backends” — APIs, databases, and more. But
what started as one company’s solution quickly became an industry
standard. Today GitHub, Slack, Notion, PostgreSQL, Google Drive, Hugging
Face, and hundreds of other services all publish official MCP servers. Any
agent that speaks MCP — including ADK agents — gets all of them for free.
The architecture is a clean client-server split. MCP servers expose tools. ADK
acts as the client. When you include an McpToolset instance in your agent's
tools list, it automatically handles connection management, tool discovery,
schema adaptation, and proxying of all tool calls to the MCP server and back
to the agent. From the model’s perspective, MCP tools are indistinguishable
from native ADK function tools — it sees the same clean JSON schema and
calls them the same way.
There are three transport options you need to know, each suited to a
different context: StdioConnectionParams for local servers,
StreamableHTTPConnectionParams for remote production servers, and
SseConnectionParams for legacy SSE-based servers. Let's build with each one.
Local MCP Servers: StdioConnectionParams
Local MCP servers run as subprocesses on the same machine as your agent.
They communicate over standard input/output (stdin/stdout). This is the
pattern you’ll use during development, for internal tooling, or any time the
MCP server should live alongside your agent process.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 25/71


---
*Page 26*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
When using StdioConnectionParams, ADK launches and manages the MCP
server process itself, it starts when your agent initialises and shuts down
gracefully when the agent terminates. You don't run a separate terminal, you
don't manage a process, ADK does it all.
Local MCP Servers Architecture
Here’s a complete filesystem agent that lets users read, list, and manage files
via natural language:
import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
# The folder your agent is allowed to access
WORKSPACE_PATH = os.path.abspath("./agent_workspace")
filesystem_agent = Agent(
model="gemini-2.5-flash",
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 26/71


---
*Page 27*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
name="filesystem_assistant",
instruction="""
You help users manage files in their workspace.
You can list directories, read file contents, create files, and search.
Always confirm with the user before writing or deleting anything.
Current workspace: ./agent_workspace
""",
tools=[
McpToolset(
connection_params=StdioConnectionParams(
server_params=StdioServerParameters(
command="npx",
args=[
"-y", # auto-confirm
"@modelcontextprotocol/server-filesystem", # the MCP serve
WORKSPACE_PATH, # MUST be an ab
],
),
timeout=30, # seconds to wait for the subprocess to start
),
# Only expose the tools we actually need
tool_filter=["list_directory", "read_file", "search_files", "get_file_in
)
]
)
⚠
Common gotcha — paths must be absolute. The filesystem MCP server
runs as a separate subprocess with its own working directory. Relative paths
like "./workspace" will silently resolve to the wrong location. Always use
os.path.abspath() or construct an absolute path explicitly.
The timeout parameter is worth highlighting. If npx needs to download the
 
MCP server package for the first time (on a cold start), it can take 10–30
seconds. A timeout that's too low causes the agent to fail on first boot. Set it
generously for development; pre-install packages in your container for
production to eliminate cold start entirely.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 27/71


---
*Page 28*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Want to connect a local Python MCP server instead of an npm package? Just
swap the command:
StdioConnectionParams(
server_params=StdioServerParameters(
command="python3",
args=["./tools/my_custom_mcp_server.py"],
# Pass environment variables to the subprocess
env={
"DATABASE_URL": os.environ["DATABASE_URL"],
"API_KEY": os.environ["MY_SERVICE_KEY"],
}
)
)
This pattern is powerful for building internal company tools: write your
MCP server in Python using FastMCP, and any ADK agent in your
organisation can consume it without knowing anything about your internal
implementation.
Remote MCP Servers: StreamableHTTPConnectionParams
For production deployments, you want your MCP server decoupled from
your agent. Running as a separate Cloud Run service, it can scale
independently, be shared across multiple agents, and be updated without
redeploying the agent. StreamableHTTPConnectionParams connects your ADK
agent to a remote MCP server over HTTP, enabling this architecture.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 28/71


---
*Page 29*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Remote MCP with Local MCP
Here’s the complete setup for a production GitHub agent, exactly the pattern
you’d use to give your agent access to issues, PRs, and repository search:
import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionPa
GITHUB_TOKEN = os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"]
github_agent = Agent(
model="gemini-2.5-flash",
name="github_triage_agent",
instruction="""
You are a GitHub triage assistant for the engineering team.
Help users search for issues, review pull requests, and investigate open bugs.
You have READ-ONLY access. You cannot create, modify, or close anything.
Always include links to the relevant GitHub URLs in your responses.
""",
tools=[
McpToolset(
connection_params=StreamableHTTPConnectionParams(
url="https://api.githubcopilot.com/mcp/",
headers={
"Authorization": f"Bearer {GITHUB_TOKEN}",
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 29/71


---
*Page 30*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
},
),
# CRITICAL: see Section 3d for why this filter is non-negotiable
tool_filter=[
"search_repositories",
"search_issues",
"list_issues",
"get_issue",
"list_pull_requests",
"get_pull_request",
]
)
]
)
The same pattern applies to any remote MCP server, swap the URL and
headers for your service:
# Slack agent — read channels, post messages
McpToolset(
connection_params=StreamableHTTPConnectionParams(
url="https://mcp.slack.com/api/mcp",
headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
),
tool_filter=["send_message", "list_channels", "search_messages"]
)
# Your own internal MCP server deployed on Cloud Run
McpToolset(
connection_params=StreamableHTTPConnectionParams(
url="https://my-mcp-server-abc123-uc.a.run.app/mcp",
headers={"X-Internal-Token": os.environ["INTERNAL_MCP_SECRET"]}
 ), 
tool_filter=["get_customer_data", "search_orders"]
)
A note on transport evolution. The original MCP transport was SSE (Server-
Sent Events), using SseConnectionParams. In March 2025, MCP released
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 30/71


---
*Page 31*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Streamable HTTP as a new transport that allows a server to function as an
independent process managing multiple client connections via HTTP POST
and GET requests, with optional SSE for streaming. Streamable HTTP is now
the recommended approach for all new production MCP servers. If you
encounter an older MCP server that only speaks SSE, swap
StreamableHTTPConnectionParams for SseConnectionParams — the rest of the
McpToolset API is identical.
The Parameter: Non-Negotiable in Production
tool_filter
This is the single most important McpToolset parameter and the one most
beginners skip. Here's what happens without it.
The GitHub MCP server exposes different parts of GitHub’s functionality,
from issues and pull requests to notifications and code security. Google
That’s not 3 tools — it’s over 50. When you drop 50+ tool definitions into the
model’s context on every single turn, three bad things happen
simultaneously:
1. The model picks wrong tools. With 50 similar-sounding options, the LLM
makes wrong selections — choosing create_issue when the user asked to
find an issue, or calling a write operation when only reads are intended.
Every wrong tool selection costs at minimum one full agent turn to recover.
2. Token costs spike. Every tool definition sent to the model on every turn
adds tokens. 50 detailed GitHub tool schemas can add thousands of tokens to
every request. At scale — say, 10,000 agent requests per day — this cost is
substantial and entirely avoidable.
3. Latency increases. More tokens in the context = longer time to first token.
For interactive agents, this is directly felt by users.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 31/71


---
*Page 32*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
The fix is three lines of code:
# ❌ Without filter — the model sees 50+ tools every turn
McpToolset(
connection_params=StreamableHTTPConnectionParams(url=GITHUB_MCP_URL, headers=hea
)
# ✅ With filter — the model sees only what it needs
McpToolset(
connection_params=StreamableHTTPConnectionParams(url=GITHUB_MCP_URL, headers=hea
tool_filter=[
"search_issues",
"get_issue",
"list_pull_requests",
]
)
 
tool_filter also serves as a security boundary. If your agent only needs to
read data, never include write tools ( create_issue, push_files,
delete_branch) in the filter — even if the token has write permissions. An
agent that can't see a tool can't accidentally call it. This is defence-in-depth
for agentic systems, and it costs you nothing.
Production rule of thumb: Start with the minimum set of tools that covers
your use case, usually 3 to 5. Add more only when you have a specific,
tested reason to.
Production-Ready MCP Servers: Your Starter Toolkit
This table covers the MCP servers you’ll reach for most often. All are either
officially published by the service provider or maintained by the MCP
community with production stability:
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 32/71


---
*Page 33*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
The Model Context Protocol (MCP) acts as a universal adapter, allowing your
agent to interact with diverse ecosystems via two primary connection types: Local
stdio and Remote HTTP.
Local servers, such as those for PostgreSQL, SQLite, or Filesystem access,
typically run via npx and allow the agent to manage local infrastructure directly.
Remote servers, like those for GitHub, Slack, or Brave Search, connect via secure
HTTP endpoints, enabling the agent to perform complex external tasks like
managing PRs, searching the live web, or triggering n8n automation workflows
without requiring you to write custom API wrappers for every service.
Bonus
Flip It: Expose Your ADK Tools as an MCP Server
Everything so far treats ADK as the MCP client. But the protocol works in
both directions. ADK also supports exposing your own tools via an MCP
server, using FastMCP to handle all the complex protocol details and server
management, so you can focus on building great tools.
Why would you do this? Two scenarios come up constantly in team settings:
you’ve built a set of ADK function tools that other teams want to use in their
own agents (regardless of which framework they’re using), or you want to
make your agent’s capabilities accessible to Gemini CLI, Claude, Cursor, or
any other MCP-compatible client.
Here’s the minimal pattern, an MCP server that exposes two ADK function
tools:
# mcp_server.py — run this as a separate service
from fastmcp import FastMCP
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 33/71


---
*Page 34*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type
# Your existing ADK function tools
from my_agent.tools import search_products, get_order_status
mcp = FastMCP("my-company-tools")
# Register each ADK tool with the MCP server
# FastMCP uses the same docstring + type annotation schema that ADK does
@mcp.tool()
async def search_products_tool(query: str, category: str = "all") -> dict:
"""
Search the product catalog.
Args:
query: The search term.
category: Product category filter. Use 'all' for no filter.
Returns:
dict with 'products' list and 'total_count'.
"""
return await search_products(query=query, category=category)
@mcp.tool()
async def get_order_status_tool(order_id: str) -> dict:
"""
Get the current status of an order.
Args:
order_id: The unique order identifier.
Returns:
dict with 'status', 'order_id', and 'estimated_delivery'.
"""
return await get_order_status(order_id=order_id)
if __name__ == "__main__":
# Run as stdio server (for local consumption)
mcp.run()
# Or run as HTTP server (for remote consumption):
# mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)
Once deployed (locally or on Cloud Run), any MCP client, another ADK
agent, a Gemini CLI user, a Cursor IDE plugin, can discover and call your
tools without knowing anything about your internal Python implementation.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 34/71


---
*Page 35*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Running an MCP server on Cloud Run provides scalability, a centralised
endpoint your team can share via IAM privileges, and the ability for team
members to connect from their local machines rather than each running
their own server.
This pattern is the foundation of the multi-agent architectures we’ll cover in
Blog 6: where specialised agents expose their capabilities as MCP servers
and a coordinator agent orchestrates them all.
You now have the full MCP toolkit: local servers for development and
internal tools, remote servers for production third-party integrations,
aggressive tool_filter usage for cost and accuracy control, and the ability to
expose your own tools back to the ecosystem.
OpenAPI Tools (REST APIs Without the Boilerplate)
You’ve built tools from scratch in Section 2. You’ve connected to third-party
services via MCP in Section 3. But there’s a third scenario that comes up
constantly in backend development: you have an API — your own, or a third-
party one — with a perfectly good OpenAPI spec. You don’t want to write 30
function tools, one per endpoint. And you shouldn’t have to.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 35/71


---
*Page 36*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
OpenAPI Tools
That’s exactly the gap OpenAPIToolset fills.
What OpenAPIToolset Does For You Automatically
ADK simplifies interacting with external REST APIs by automatically
generating callable tools directly from an OpenAPI Specification. This
eliminates the need to manually define individual function tools for each
API endpoint.
Here’s the mechanical process that happens the moment you pass a spec to
OpenAPIToolset:
ADK parses the spec and resolves internal references like $ref to
understand all API endpoints. It then scans the spec to find all valid API
operations, GET, POST, PUT, DELETE, and for each one, automatically
creates a RestApiTool. The tool name comes from the operationId in the
spec (converted to snake_case). The description is taken from the operation's
summary or description. The tool includes all HTTP details: method, path,
parameters, and request body.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 36/71


---
*Page 37*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
The result: the LLM sees a clean function signature for every endpoint. It
doesn’t know or care that it’s calling a REST API. From the model’s
perspective, calling get_current_weather looks exactly the same whether it's
a Python function you wrote or an auto-generated wrapper around a weather
API endpoint. The underlying HTTP request, headers, auth, URL
construction, parameter injection, response parsing, is handled entirely by
ADK.
This approach is particularly valuable for integrating third-party APIs where
OpenAPI specifications are already available, or for exposing large APIs with
many endpoints without writing boilerplate code.
One important thing to understand about RestApiTool naming: the tool name
comes from the operationId in the spec, converted to snake_case. This
means the quality of your operationId values directly affects how accurately
the model picks the right tool. getUserProfile becomes get_user_profile —
clear. op123 becomes op123 — useless to the model. If you control the spec,
use descriptive verb-noun operationId values. If you don't, we'll look at how
to handle that shortly.
Loading an OpenAPI Spec: Three Ways
OpenAPIToolset supports three loading strategies, each useful in a different
context:
import json
import yaml
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAP
# ── Way 1: From a JSON or YAML string ────────────────────────────────────────
# Best for: loading a spec from disk, environment variable, or Secret Manager
with open("./specs/my_api_spec.yaml", "r") as f:
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 37/71


---
*Page 38*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
spec_content = f.read()
toolset = OpenAPIToolset(
spec_str=spec_content,
spec_str_type="yaml" # or "json" — required when using spec_str
)
# ── Way 2: From a Python dict ────────────────────────────────────────────────
# Best for: specs already fetched and parsed, or programmatically assembled specs
import httpx
response = httpx.get("https://api.example.com/openapi.json")
spec_dict = response.json()
toolset = OpenAPIToolset(spec_dict=spec_dict)
# Note: no spec_str_type needed — dict format is unambiguous
# ── Way 3: Inline JSON string ────────────────────────────────────────────────
# Best for: quick prototyping with a spec you've pasted in
openapi_spec_json = """
{
"openapi": "3.0.0",
"info": { "title": "My API", "version": "1.0" },
"paths": { ... }
}
"""
toolset = OpenAPIToolset(
spec_str=openapi_spec_json,
spec_str_type="json"
)
⚠
Gotcha — spec_str_type is required with spec_str. Passing a string
without the type raises a validation error at initialization. The toolset can't
reliably distinguish JSON from YAML from a raw string. Always specify
"json" or "yaml" explicitly.
 
Once you have a toolset, you can inspect what tools it generated before
attaching it to an agent — a useful debugging step when working with large
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 38/71


---
*Page 39*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
specs:
# Inspect generated tools before wiring up the agent
tools = toolset.get_tools()
print(f"Generated {len(tools)} tools from spec:")
for tool in tools:
print(f" {tool.name}: {tool.description[:80]}")
This is invaluable when working with large API specs. The GitHub OpenAPI
spec, for example, exposes over 1,000 endpoints. Printing the generated
tools lets you identify exactly which tool names you want to keep.
Full Working Example: GitHub Issues Agent
Let’s build a real, runnable agent. Rather than a contrived example, we’ll use
the GitHub REST API, something you might genuinely deploy, to create an
agent that answers questions about repositories and issues in natural
language.
The GitHub API publishes an official OpenAPI spec. We’ll load it,
authenticate with a personal access token, wire up the agent, and show the
full execution flow.
import os
import asyncio
import httpx
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAP
from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credenti
from google.genai import types
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 39/71


---
*Page 40*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
GITHUB_TOKEN = os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"]
GITHUB_SPEC_URL = "https://raw.githubusercontent.com/github/rest-api-description/mai
# ── Step 1: Load the OpenAPI spec ────────────────────────────────────────────
print("Fetching GitHub OpenAPI spec...")
response = httpx.get(GITHUB_SPEC_URL, timeout=30)
github_spec = response.json()
# ── Step 2: Configure authentication ────────────────────────────────────────
# GitHub uses a Bearer token in the Authorization header
# token_to_scheme_credential is ADK's helper that formats this correctly
auth_scheme, auth_credential = token_to_scheme_credential(
"apikey", # auth type
"header", # where the key goes: "header" or "query"
"Authorization", # the header name
f"Bearer {GITHUB_TOKEN}" # the value — note the "Bearer " prefix
)
# ── Step 3: Create the toolset ────────────────────────────────────────────────
github_toolset = OpenAPIToolset(
spec_dict=github_spec,
auth_scheme=auth_scheme,
auth_credential=auth_credential,
)
# Inspect what was generated (run this once to understand the spec)
# for tool in github_toolset.get_tools():
# print(f"{tool.name}: {tool.description[:60]}")
# ── Step 4: Create the agent ─────────────────────────────────────────────────
github_agent = Agent(
model="gemini-2.5-flash",
name="github_issues_agent",
instruction="""
You are a GitHub assistant for engineering teams.
Help users find repositories, search issues, and review pull requests.
When showing results:
- Always include the URL to the GitHub resource
- Format issue titles as: #<number>: <title>
- Show the issue state (open/closed) and creation date
- Summarise any code or technical details clearly
You have READ-ONLY access. Do NOT attempt to create, edit, or close anything.
""",
tools=[github_toolset]
)
# ── Step 5: Run the agent ────────────────────────────────────────────────────
async def ask_github_agent(question: str):
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 40/71


---
*Page 41*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
session_service = InMemorySessionService()
session = await session_service.create_session(
app_name="github-demo",
user_id="user-001"
)
runner = Runner(
agent=github_agent,
app_name="github-demo",
session_service=session_service
)
response_text = ""
async for event in runner.run_async(
user_id="user-001",
session_id=session.id,
new_message=types.Content(
role="user",
parts=[types.Part(text=question)]
)
):
if event.is_final_response() and event.content:
for part in event.content.parts:
response_text += part.text or ""
return response_text
# Example usage
if __name__ == "__main__":
answer = asyncio.run(
ask_github_agent(
"List the 5 most recent open issues in the google/adk-python repository"
)
)
print(answer)
Notice what we did not write: no requests calls, no URL construction, no
Authorization header management, no response parsing, no per-endpoint
function definitions. The agent handles natural language input, picks the
right GitHub API operation ( issues_list_for_repo or similar), constructs and
sends the HTTP request, and formats the JSON response, all automatically.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 41/71


---
*Page 42*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
What the model actually sees at runtime: When the user asks about issues,
Gemini sees a tool called issues_list_for_repo with a description pulled
straight from GitHub's spec: "List issues assigned to the authenticated user
across all visible repositories". It fills in owner="google", repo="adk-python",
state="open", per_page=5 and calls it, no hardcoded logic anywhere.
Authentication: The Three Patterns You’ll Actually Use
When using OpenAPIToolset, you pass auth_scheme and auth_credential
during toolset initialization. The toolset applies them to all generated tools
automatically. You configure authentication once, not per-tool, not per-
request.
Pattern 1: API Key (most common)
from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credenti
# API key in a header (e.g., OpenWeatherMap, SendGrid, Stripe)
auth_scheme, auth_credential = token_to_scheme_credential(
"apikey",
"header",
"X-API-Key", # the header name your API uses
os.environ["MY_API_KEY"]
)
# API key as a query parameter (e.g., some legacy APIs)
auth_scheme, auth_credential = token_to_scheme_credential(
"apikey",
"query",
"api_key", # the query param name
os.environ["MY_API_KEY"]
)
toolset = OpenAPIToolset(
spec_str=spec_content,
spec_str_type="yaml",
auth_scheme=auth_scheme,
auth_credential=auth_credential,
)
 
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 42/71


---
*Page 43*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Pattern 2: OAuth 2.0 / OpenID Connect (for user-delegated access)
ADK supports OAuth2 by allowing you to configure an auth_scheme and
auth_credential when you initialize your OpenAPIToolset. This configuration
primarily handles credentials like a client_id and client_secret.
from google.adk.auth.auth_schemes import OpenIdConnectWithConfig
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAu
# Define the OAuth scheme
auth_scheme = OpenIdConnectWithConfig(
authorization_endpoint="https://accounts.google.com/o/oauth2/auth",
token_endpoint="https://oauth2.googleapis.com/token",
scopes=["https://www.googleapis.com/auth/calendar.readonly"]
)
# Define the credentials (from your OAuth app registration)
auth_credential = AuthCredential(
auth_type=AuthCredentialTypes.OPEN_ID_CONNECT,
oauth2=OAuth2Auth(
client_id=os.environ["OAUTH_CLIENT_ID"],
client_secret=os.environ["OAUTH_CLIENT_SECRET"],
)
)
toolset = OpenAPIToolset(
spec_str=spec_content,
spec_str_type="yaml",
auth_scheme=auth_scheme,
auth_credential=auth_credential,
)
 
When a tool requires user login or consent, typically OAuth 2.0 or OIDC, the
ADK framework pauses execution and signals your agent client application,
which is responsible for handling the consent flow and passing the resulting
token back to the agent. This human-in-the-loop auth flow is covered in
depth in the official ADK authentication docs.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 43/71


---
*Page 44*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Pattern 3: Per-tool credential configuration (advanced)
If different tools in the same toolset need different credentials, say, a spec
that mixes public and authenticated endpoints, you can configure auth at
the individual RestApiTool level after generation:
tools = toolset.get_tools()
for tool in tools:
if tool.name in ["create_order", "update_profile", "delete_account"]:
tool.configure_auth_scheme(admin_auth_scheme)
tool.configure_auth_credential(admin_credential)
⚠
Security note from the official docs: Storing sensitive credentials like
access tokens and especially refresh tokens directly in session state might
pose security risks depending on your session storage backend. For
database or persistent storage, strongly consider encrypting token data
before storing it and managing encryption keys securely. In production,
fetch credentials from Secret Manager at startup, never hardcode them or
store them in session state unencrypted.
The Golden Rule for OpenAPI Tool Responses
ADK’s RestApiTool wraps all HTTP responses in a structured dictionary with
a status field, data for the response body, and status_code for the HTTP
status. This allows the LLM to reason about success and error states clearly.
The structure the model sees for every API call looks like this:
# A successful response
{
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 44/71


---
*Page 45*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
"status": "success",
"data": {
"items": [...],
"total_count": 42
},
"status_code": 200
}
# A failed response
{
"status": "error",
"data": {
"message": "Resource not found",
"documentation_url": "https://docs.github.com/..."
},
"status_code": 404
}
ADK generates this wrapping automatically for tools created via
OpenAPIToolset , which is one of the reasons it produces more reliable
agents than manually written HTTP wrappers where developers often forget
to handle non-200 responses.
When you write the agent’s instruction, you can leverage this structure
explicitly:
instruction="""
...
If a tool returns status 'error', do not retry automatically.
Tell the user what went wrong using the message in the 'data' field
and suggest what they might correct (e.g., check the repository name or permissions)
"""
 
This instruction pattern, teaching the agent how to handle structured errors,
is what separates a demo agent from a production-grade one.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 45/71


---
*Page 46*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
💡
Pro Tip: Not every API publishes an OpenAPI spec, and some that do
publish poor ones with vague operationId values or missing parameter
descriptions. If the generated tool names are cryptic ( op_1234,
operation_post_v2) or descriptions are empty, the model will pick wrong
tools constantly. In that case, write a thin Function Tool wrapper instead: it
costs 20 lines of code and gives you full control over the name, description,
and docstring that the model sees. Use OpenAPIToolset when the spec is high
quality; fall back to Function Tools when it isn't.
Two tool types down, one to go. Next Section we look at SkillToolset , ADK's
approach to modular, context-efficient knowledge that loads only when the
agent actually needs it. Then in Section 6, we'll bring all four together with
the production decision tree that tells you exactly which one to reach for in
any situation.
SkillToolset (Context-Efficient Modular Knowledge)
The three tool types you’ve seen so far all execute something: code runs, an
HTTP request fires, an API gets called. SkillToolset works differently. It
doesn't execute anything. Instead, it gives your agent specialist knowledge,
exactly when that knowledge is needed, and not a token before.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 46/71


---
*Page 47*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
SkillToolset
Why SkillToolset Exists
Consider what happens when you want your agent to be a specialist in
multiple domains. You could dump all the instructions into the agent’s
system prompt: SQL optimisation rules, code review standards, API
documentation, security guidelines, all of it, all the time. But every word in
the system prompt is sent to the model on every single turn, whether the
user is asking about SQL or just saying hello. This is called context bloat,
and at scale it’s expensive, slow, and increasingly inaccurate as the context
fills up.
The Skills feature allows you to create modular packages of Skill instructions
and resources that agents can load on demand. This approach helps you
organise your agent’s capabilities and optimise the context window by only
loading instructions when they are needed.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 47/71


---
*Page 48*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
The mechanism is called Progressive Disclosure, borrowed from UI design.
The structure of a Skill allows it to be loaded incrementally to minimise the
impact on the operating context window of the agent. At L1, only the skill’s
name and a one-line description enter the context, enough for the model to
know the skill exists. At L2, the full instruction set loads when the user’s
request triggers that skill. At L3, reference documents and assets load only if
the instructions direct the model to retrieve them. Three layers, each
expanding only on demand.
SkillToolset is the adapter that plugs this system into ADK's tools interface.
Use the SkillToolset class to include one or more Skills in your agent
definition and then add it to your agent's tools list. From the agent's
perspective, a skill looks like a tool. From the context window's perspective,
it's a fraction of the cost.
File-Based vs. Inline Skills
There are two ways to define skills for SkillToolset, and they serve different
purposes. File-based skills are the right choice for stable, reusable
knowledge that you might share across agents or publish for others to
install. Inline skills are better for dynamic knowledge that your code
generates or modifies at runtime.
File-based skills live in a directory with a SKILL.md file at the root. The
SKILL.md contains a YAML frontmatter block (L1 metadata) and a markdown
body (L2 instructions). Reference documents and assets go in subdirectories
named references/ and assets/. Only the SKILL.md is required, everything
else is optional.
A real SQL optimiser skill directory looks like this:
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 48/71


---
*Page 49*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
my_agent/
agent.py
skills/
sql_optimizer/
SKILL.md # Required: metadata + core instructions
references/
postgres_hints.md # Loaded on demand if the model asks for it
index_patterns.md # Common indexing strategies reference
assets/
slow_query_examples.sql # Example patterns to avoid
And the SKILL.md file for that skill:
---
name: sql-optimizer
description: >
Expert SQL query optimiser for PostgreSQL. Use when the user asks to
improve query performance, debug slow queries, or review query plans.
Do NOT use for general Python or application code review.
---
## SQL Optimisation Workflow
Step 1: Ask the user for the slow query and the EXPLAIN ANALYZE output if available.
Step 2: Identify the bottleneck — missing index, N+1 pattern, full table scan, or jo
Step 3: Read `references/index_patterns.md` if the bottleneck involves indexing.
Step 4: Propose a rewritten query with a clear explanation of what changed and why.
Step 5: Suggest how to verify the improvement using EXPLAIN ANALYZE.
Always explain tradeoffs. A faster query that requires a large index may not
always be the right choice for write-heavy tables.
 
Notice the description in the frontmatter. This is the L1 metadata, the only
part the model sees until the skill is triggered. It needs to be precise enough
that the model knows when to activate the skill, and specific enough that it
doesn't fire on unrelated requests.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 49/71


---
*Page 50*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Now, loading both a file-based skill and an inline skill into a single
SkillToolset:
import pathlib
from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir, models
from google.adk.tools import skill_toolset
# File-based: loads SKILL.md and all bundled resources from disk
sql_skill = load_skill_from_dir(
pathlib.Path(__file__).parent / "skills" / "sql_optimizer"
)
# Inline: defined in code — useful when content is dynamic or environment-specific
review_skill = models.Skill(
frontmatter=models.Frontmatter(
name="code-reviewer",
description=(
"Reviews Python code for quality, security, and performance issues. "
"Use when the user asks to review, audit, or improve Python code. "
"Do NOT use for SQL, YAML, or infrastructure code."
),
),
instructions=(
"Step 1: Scan for security issues — hardcoded credentials, SQL injection ris
"unsafe deserialization, or missing input validation.\n"
"Step 2: Check for performance anti-patterns — unnecessary loops, missing ca
"blocking I/O in async functions.\n"
"Step 3: Review code clarity — variable naming, function length, missing doc
"Step 4: Return a structured report with CRITICAL, WARNING, and SUGGESTION c
"Always include a corrected code snippet for any CRITICAL finding."
),
# Inline skills can also bundle reference content directly in code
resources=models.Resources(
references={
"security_checklist.md": (
"# Security Checklist\n"
"- Never store secrets in code\n"
"- Validate all external input\n"
"- Use parameterised queries for all DB operations\n"
),
}
),
)
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 50/71


---
*Page 51*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
# Both skills in one toolset — the agent gets both capabilities
engineering_toolset = skill_toolset.SkillToolset(
skills=[sql_skill, review_skill]
)
engineering_agent = Agent(
model="gemini-2.5-flash",
name="engineering_assistant",
instruction=(
"You are a senior engineering assistant. "
"You specialise in SQL optimisation and Python code review. "
"Use your skills when relevant, and be explicit about which skill you're app
),
tools=[engineering_toolset]
)
The inline method of Skill definition enables you to dynamically modify
skills from your ADK agent code, which makes it particularly useful when
skill instructions need to reference environment-specific configuration,
when you’re generating skill content programmatically, or when you’re
prototyping before committing to a file structure.
When SkillToolset Beats a Function Tool
The mental model is simple. Reach for a Function Tool when your capability
requires executable code — something must run, a value must be computed,
an API must be called. Reach for SkillToolset when your capability is
fundamentally a body of knowledge and a set of instructions — something
the model needs to know and follow, not run.
A few concrete comparisons that make this distinction clear:
Checking live inventory requires a database query, so it’s a Function Tool.
Knowing how to interpret inventory data for a specific domain —
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 51/71


---
*Page 52*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
understanding what “safety stock” means in your warehouse context, or how
to decide between “low stock” and “out of stock” — is a skill.
Sending an email requires calling an SMTP client or an API, so it’s a Function
Tool. Knowing how to write a professional customer apology email in your
company’s tone and format, with the right escalation language for different
severity levels, is a skill.
Fetching a GitHub issue is a tool call. Knowing your team’s code review
standards, what makes a PR acceptable for merge, and how to leave
constructive feedback in your organisation’s voice is a skill.
The pattern: tools handle doing, skills handle knowing. In a well-architected
ADK agent, the two work together — a function tool fetches the raw data, and
a skill provides the specialist knowledge to interpret and act on it correctly.
💡
One more reason to prefer SkillToolset over bloating your system
prompt: when you add a new skill to SkillToolset, only its L1 metadata (one
line) hits the context. When you add a new paragraph to your system
prompt, it's there permanently, in every single request, forever. Skills are
additive and lightweight. System prompt additions compound your token
costs with every deployment.
The Production Decision Tree: Which Tool Type Should You
Use?
You now have four tool types in your toolkit. The question isn’t which one is
best — it’s which one is right for the specific capability you’re building. Here
is the exact decision process to follow every time.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 52/71


---
*Page 53*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Work through these questions in order, and you’ll land on the right answer
every time:
Production Decision Tree
Does your capability require running code, calling an API, querying a
database, or producing a computed value?
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 53/71


---
*Page 54*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
If the answer is no — if what you actually need is for the agent to know
something and follow a set of domain-specific instructions, the right choice is
SkillToolset. Write a SKILL.md with the specialist knowledge baked in. If the
knowledge is so simple it fits in two or three sentences, just put it in the
agent instruction instead.
If the answer is yes, keep going.
Is there an existing MCP server for this service or capability?
Check the MCP server registry. If one exists and it’s maintained — GitHub,
Slack, PostgreSQL, Filesystem, Google Drive — use McpToolset. This is the
fastest path from idea to working agent. You get a production-quality tool
implementation, authentication support, and a schema the community has
already validated, for zero lines of implementation code. Always pair it with
an aggressive tool_filter.
If no MCP server exists, keep going.
Does your API have a published OpenAPI specification?
If yes, use OpenAPIToolset. Load the spec, configure authentication once,
and every endpoint becomes a callable tool automatically. This pays for
itself the moment your API has more than three or four endpoints you want
to expose. Inspect the generated tool names first, if operationId values in
the spec are vague or absent, the model will pick wrong tools, and you're
better off writing Function Tools for the specific endpoints you need.
If no OpenAPI spec exists, the answer is Function Tool. Write the function,
annotate every parameter, write the docstring as if it's a prompt for the
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 54/71


---
*Page 55*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
model (because it is), return a structured dict, and handle errors explicitly.
A quick reference in plain language:
Use a Function Tool when you’re writing custom logic that doesn’t have an
existing MCP server or OpenAPI spec, when you need precise control over
the schema and description the model sees, or when you’re wrapping a
third-party library that has no web API at all.
Use McpToolset when the service you need already publishes an MCP
server, especially for popular developer tools — GitHub, Slack, databases,
filesystems. It’s always faster than building from scratch.
Use OpenAPIToolset when you have an API with a high-quality OpenAPI
spec and multiple endpoints to expose. It eliminates boilerplate and keeps
your agent code clean. Avoid it when the spec quality is poor.
Use SkillToolset when the capability is domain knowledge, workflow
instructions, or specialist expertise rather than executable code. It keeps
your context window lean and your agent modular.
And when capabilities span multiple types, a GitHub tool for fetching data
combined with a code-review skill for interpreting it, combine them in the
same tools=[] list. ADK supports mixing all four types freely, and that
combination is exactly how production-grade agents are built.
💡
The production smell test: If you find yourself writing a 500-word
paragraph in your agent instruction to describe how to handle one type of
request, stop. That paragraph is a skill waiting to be extracted. If you find
yourself writing the fifth wrapper function for a REST API that publishes an
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 55/71


---
*Page 56*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
OpenAPI spec, stop. That’s OpenAPIToolset's job. The right tool type makes
your agent code shorter, cleaner, and cheaper to run.
Action Confirmations: Human-in-the-Loop for Dangerous Tools
Every section in this post has been about giving your agent more capability.
This one is about restraint. The most production-critical pattern in agent
development is not a tool type or an architecture choice. It is the simple
discipline of asking a human before doing something that cannot be
undone.
What Action Confirmation Is
Some agent workflows require confirmation for decision making,
verification, security, or general oversight. In these cases, you want to get a
response from a human or supervising system before proceeding with a
workflow. The Tool Confirmation feature in ADK allows a tool to pause its
execution and interact with a user for confirmation before proceeding.
This is the Human-in-the-Loop pattern, and it applies to any tool that writes,
sends, modifies, or deletes anything. If a user asks your agent to “send the
weekly report email,” the agent should show them the recipient, subject, and
body, and wait for an explicit yes before a single packet leaves your server. If
a user asks to delete a record, the agent should name exactly which record
and wait. If a user triggers a production deployment, the agent should
summarise what is about to change and require confirmation.
The rule of thumb: if the action is reversible in under 30 seconds, you can
skip confirmation. If it is not, you cannot.
Two Ways to Implement It in ADK
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 56/71


---
*Page 57*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
ADK provides two confirmation patterns, each suited to a different level of
complexity.
Boolean Confirmation is for the simple case: a yes or no before the tool
runs. You can configure a FunctionTool with a require_confirmation
parameter. This option pauses the tool for a yes or no confirmation
response. You can pass either True to always confirm, or a callable that
evaluates the tool's arguments and decides dynamically whether
confirmation is needed.
from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
def place_order(order_items: dict[str, int]) -> dict:
"""
Place a customer order.
Args:
order_items: Items to order. A dict of item name to quantity.
Valid items: 'burger', 'fry', 'soda'.
Returns:
dict with 'status', 'order_items', and 'total'.
"""
PRICES = {"burger": 10, "fry": 5, "soda": 3}
total = sum(qty * PRICES.get(item, 0) for item, qty in order_items.items())
return {"status": "success", "order_items": order_items, "total": total}
def needs_confirmation(tool_args: dict) -> bool:
"""Only ask for confirmation on orders over $100."""
PRICES = {"burger": 10, "fry": 5, "soda": 3}
total = sum(
qty * PRICES.get(item, 0)
for item, qty in tool_args.get("order_items", {}).items()
)
return total > 100
restaurant_agent = Agent(
model="gemini-2.5-flash",
name="restaurant_agent",
instruction="You help customers place orders at a fast-food restaurant.",
tools=[
FunctionTool(
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 57/71


---
*Page 58*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
place_order,
require_confirmation=needs_confirmation # callable or just True
),
],
)
When the condition returns true, the agent pauses execution and displays a
confirmation dialog to the user. After the user provides {"confirmed": true},
the tool call proceeds. If they decline, the agent abandons the tool call and
informs the user.
Advanced Confirmation is for cases where you need structured input back
from the user before the tool can proceed — not just a yes or no, but actual
data. Think of a deploy_to_production tool that needs the user to type the
deployment environment name as a deliberate acknowledgement, or a
send_bulk_email tool that requires the user to confirm the recipient count
explicitly.
from google.adk.tools.function_tool import FunctionTool
def delete_customer_records(
customer_ids: list[str],
reason: str
) -> dict:
"""
Permanently delete customer records from the database.
This action cannot be undone.
Args:
customer_ids: List of customer IDs to delete.
reason: The business reason for deletion (for the audit log).
Returns:
dict with 'status', 'deleted_count', and 'audit_log_id'.
"""
# Deletion logic here
result = db.bulk_delete(customer_ids, reason=reason)
return {
"status": "success",
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 58/71


---
*Page 59*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
"deleted_count": len(customer_ids),
"audit_log_id": result.audit_id
}
# Always confirm, with a structured prompt explaining what's at stake
delete_tool = FunctionTool(
delete_customer_records,
require_confirmation=True,
# The confirmation_prompt is shown to the user in the confirmation dialog
confirmation_prompt=(
"You are about to PERMANENTLY DELETE {len(customer_ids)} customer record(s).
"This cannot be undone. Type 'confirm' to proceed or 'cancel' to abort."
)
)
The Docstring Trick (For Non-Confirmation-API Runtimes)
You can configure how a confirmation request is communicated to a user
via the ADK web user interface, which displays a dialog box to the user
requesting input. Google But if you are running your agent in a custom
runtime that does not use the ADK web UI, or if you want a belt-and-
suspenders approach, there is a second layer you should always add:
instruction in the docstring itself.
python
 
async def deploy_to_production(
service_name: str,
image_tag: str,
tool_context: ToolContext
) -> dict:
"""
Deploy a service to the production environment.
IMPORTANT: ALWAYS confirm with the user before calling this tool.
Before calling, show the user: the service name, the image tag being deployed,
and the current production version it will replace. Wait for explicit confirmati
Args:
service_name: The Cloud Run service to deploy (e.g., 'api-gateway').
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 59/71


---
*Page 60*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
image_tag: The Docker image tag to deploy (e.g., 'v2.4.1-prod').
Returns:
dict with 'status', 'service_name', 'deployed_tag', and 'rollout_url'.
"""
deployment = cloud_run.deploy(service=service_name, image=image_tag)
return {
"status": "success",
"service_name": service_name,
"deployed_tag": image_tag,
"rollout_url": deployment.console_url
}
The model reads the docstring on every turn. “ALWAYS confirm with the user
before calling this tool” is an instruction to the LLM, not to a human
developer. In the vast majority of cases, Gemini will show the user the
details and wait for approval before ever calling the function. Combined
with require_confirmation=True on the FunctionTool wrapper, you have two
independent layers of protection.
💡
 The production contract: every tool in your agent that creates, modifies,
sends, or deletes anything should have both require_confirmation set and a
confirmation instruction in its docstring. The first protects against the
model being overconfident. The second protects against runtimes that do
not support the confirmation API yet.
Tool Performance Tips for Production
Agent quality and agent performance are not the same thing. A perfectly
designed tool that takes three seconds to respond on every turn will frustrate
users and inflate your costs at scale. These six tips are the ones that move
the needle most in production, ranked by impact.
1. Pre-install MCP server packages in your container image
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 60/71


---
*Page 61*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Every time your agent process starts cold and launches a local MCP server
via npx, it potentially downloads the package from npm. On a Cloud Run
instance with a fresh container, this can add 10 to 30 seconds to agent startup
time. The fix costs you one line in your Dockerfile and eliminates cold start
latency permanently:
# In your Dockerfile — pre-install MCP servers at build time
FROM python:3.12-slim
RUN apt-get update && apt-get install -y nodejs npm
RUN npm install -g @modelcontextprotocol/server-filesystem \
@modelcontextprotocol/server-postgres \
@modelcontextprotocol/server-brave-search
# Now StdioConnectionParams starts instantly — no npm download at runtime
2. Filter MCP tools aggressively — every tool definition costs tokens
This was covered in Section 3d but it bears repeating as a performance
principle. Before a tool is called, the model must decide which tool to use
from everything in its context. Every extra tool definition increases the
tokens sent on every request and the time the model spends on tool
selection. Expose 5 tools, not 50. Use tool_filter. Your latency and accuracy
both improve.
3. Cache expensive tool results in session state
If two different turns in a conversation need the same database result, the
second call is wasted money and latency. Cache the result in
tool_context.state on the first call:
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 61/71


---
*Page 62*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
async def get_customer_profile(
customer_id: str,
tool_context: ToolContext
) -> dict:
"""
Fetch customer profile. Cached within the session to avoid repeated DB calls.
...
"""
cache_key = f"cache:customer:{customer_id}"
cached = tool_context.state.get(cache_key)
if cached:
return cached # Return instantly — no DB round-trip
profile = await customer_db.get(customer_id)
result = {"status": "success", "customer": profile.to_dict()}
tool_context.state[cache_key] = result # Cache for this session
return result
 
This pattern uses before_tool_callback or direct state access to check for a
cached result before allowing the API or database call to proceed, and then
saves the result after a successful call. GoogleUse the cache: key prefix
convention to make cached entries visually distinct from regular state when
debugging.
4. Always set timeouts on async tools
A tool call with no timeout can hang the entire agent turn indefinitely. A user
sees a spinner forever. On Cloud Run, you’re paying for every second of that
hung request. Set an explicit timeout on every tool that makes a network
call, and return a structured error when it expires:
import asyncio
import httpx
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 62/71


---
*Page 63*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
async def get_live_stock_price(symbol: str) -> dict:
"""..."""
try:
async with httpx.AsyncClient(timeout=5.0) as client:
response = await client.get(f"https://finance-api.internal/quote/{symbol
response.raise_for_status()
return {"status": "success", "symbol": symbol, "price": response.json()[
except asyncio.TimeoutError:
return {"status": "error", "error_code": "TIMEOUT",
"message": f"Price service timed out for {symbol}. Try again shortly
except httpx.HTTPStatusError as e:
return {"status": "error", "error_code": "API_ERROR",
"message": f"Could not fetch price (HTTP {e.response.status_code})."
```
**5. Keep total tools per agent below 10**
The model helps decide which tools to call when a user prompts the agent. Too many t
**6. Write terse but precise docstrings**
Every word in a function docstring is sent to the model on every single agent turn a
---
# Closing: What to Build Next
You now have the complete ADK tool ecosystem in your toolkit. Function Tools for cus
The next natural step is understanding how agents remember things across turns and a
After that, **Blog 6: Multi-Agent Systems with ADK** takes everything you've learned
The full companion code for this blog, with runnable examples for all four tool type
```
blog-04-adk-tools/
01_function_tool/
agent.py # Simple + ToolContext + caching examples
test_tools.py # Unit tests for all function tools
02_mcp_tool/
local_agent.py # StdioConnectionParams filesystem agent
remote_agent.py # GitHub MCP via StreamableHTTP
03_openapi_tool/
agent.py # GitHub Issues agent via OpenAPI spec
auth_examples.py # API key + OAuth2 patterns
04_skill_toolset/
agent.py # Engineering assistant with SQL + review skills
skills/
sql_optimizer/
SKILL.md
references/
index_patterns.md
05_action_confirmation/
agent.py # Restaurant order + deployment confirmation examples
README.md # Decision tree + setup instructions
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 63/71


---
*Page 64*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
What You Now Know
You started this post with a list of tool types. You’re leaving it with a complete
mental model for one of the most consequential architectural decisions in
any ADK agent: what mechanism should power each capability.
Function Tools give you full control over custom logic and are the
foundation everything else builds on. MCP Tools connect your agent to an
entire ecosystem of third-party services without a line of integration code.
OpenAPI Tools eliminate the boilerplate of wrapping REST APIs when a spec
exists. SkillToolset keeps your context window lean by loading specialist
knowledge progressively, only when the agent actually needs it. Action
Confirmations keep humans in the loop for anything irreversible. And the
performance habits in Section 8 are what separate an agent that works in a
demo from one that works reliably at scale.
The decision tree in Section 6 is the practical output of all of this. Screenshot
it, bookmark it, or copy it into your team’s internal docs. The next time
you’re building a new capability for an agent — before you write a single line
of code — work through those four questions. The right tool type almost
always becomes obvious before you open your editor.
Now that your agent can do things, the next question is whether it can
remember things. Blog 5 goes deep on ADK’s Sessions, State, and Memory
system — how to build agents that persist context across turns, remember
user preferences across sessions, and stay coherent in long multi-step
conversations.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 64/71


---
*Page 65*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Resources and Further Reading
Everything referenced in this blog, ready to open:
📘
ADK Skills documentation — how SkillToolset, load_skill_from_dir,
and the Skills experimental feature work inside ADK:
google.github.io/adk-docs/skills
📘
agentskills.io specification — the complete open standard for Skill
structure, naming rules, frontmatter fields, and the Progressive
Disclosure model: agentskills.io/specification
💻
Full project repository — every file from this blog, ready to clone and
run: github.com/simranjeet97/SelfExtendingAgent_ADKGoogle
🐍
ADK skills_agent sample — Google’s official Skills example including
both file-based and inline Skill definitions: github.com/google/adk-
python/tree/main/contributing/samples/skills_agent
If this guide helped you…
If you learned something new or found this breakdown useful:
Drop a comment — share which metrics you’ve found most reliable in your
projects.
Clap (or double-clap!) to help more AI builders discover this guide.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 65/71


---
*Page 66*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Share it with your teammates or community, every conversation brings us
closer to better, fairer AI evaluation.
GenAI Full Roadmap [ Learning LLM — RAG -Agentic AI with Resources] :
https://youtu.be/4yZ7mp6cIIg
👨‍💻
Agentic AI 14+ Projects- https://www.youtube.com/playlist?
list=PLYIE4hvbWhsAkn8VzMWbMOxetpaGp-p4k
👨‍💻
Learn RAG from Scratch — https://www.youtube.com/playlist?
list=PLYIE4hvbWhsAKSZVAn5oX1k0oGQ6Mnf1d
👨‍💻
Complete Source Code of all 75 Day Hard
🌀
GitHub —
https://github.com/simranjeet97/75DayHard_GenAI_LLM_Challenge
🔀
Kaggle Notebook — https://www.kaggle.com/simranjeetsingh1430
👨‍💻
Exclusive End to End Projects on GenAI or Deep Learning or Machine
Learning in a Domain Specific way —
https://www.youtube.com/@freebirdscrew2023
If you like the article and would like to support me make sure to:
👏 👉🏻
Clap for the story (100 Claps) and follow me Simranjeet Singh
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 66/71


---
*Page 67*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
📑
View more content on my Medium Profile
🔔
Follow Me: Medium | GitHub | Linkedin | Community
🚀
Help me in reaching to a wider audience by sharing my content with
your friends and colleagues.
What do you choose?
Google AI Agent Claude Code Artificial Intelligence Technology
Written by Simranjeet Singh
Following
3.6K followers · 40 following
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 67/71


---
*Page 68*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
AI/ML Engineer l | GenAI Expert | Finance and Banking | 3K Medium + 14K
YouTube | Machine Learning | Deep Learning | NLP
No responses yet
Rae Steele
What are your thoughts?
More from Simranjeet Singh
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 68/71


---
*Page 69*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
InArtificial Intelligence in Plain … by Simranjeet Si… InArtificial Intelligence in Plain … by Simranjeet Si…
Uber Architecture – Part 1: Why Your First Google ADK Agent with
Tracking 5 Million Drivers Every… Skills: Build a Weather and News…
Every second, 83,000 drivers tap their GPS I’ve read three tutorials. Installed five
chip. frameworks. Watched two YouTube videos…
5d ago 2 5d ago 34
InArtificial Intelligence in Plain … by Simranjeet Si… Simranjeet Singh
Agentic AI Projects: Build 14 Don’t Build a Distributed System
Hands‑On AI Agents + Key Desig… Until You Master These 5…
Explore 14 real-world Agentic AI projects and Before building microservices, understand
2 key tutorials. Learn to build autonomous… these 5 core patterns that keep distributed…
Jul 6, 2025 328 4 Mar 11 1
See all from Simranjeet Singh
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 69/71


---
*Page 70*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Recommended from Medium
Han HELOIR YAN, Ph.D. ☕ InTech and AI Guild by Shashwat
What Cursor Didn’t Say About Bye-Bye MCP: Says Perplexity and
Composer 2 (And What a Develop… Cloudflare
The benchmark was innovative. The After months of hype, Perplexity’s CTO just
engineering was real. The model ID told a… announced they are moving away from the…
4d ago 1.4K 9 Mar 13 275 13
The Latency Gambler InLet’s Code Futureby Deep concept
Anthropic Says Engineers Won’t 6 Tools That Made My Life Easier as
Exist in a Year. It’s Also Paying… a Software Engineer
The most honest job posting in tech history Make your development environment work
might also be the most revealing thing about… for you, not against you.
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 70/71


---
*Page 71*


3/25/26, 2:07 PM Master Google ADK Tools, MCP, OpenAPI Tools, and Learn When to use them? | Medium
Mar 11 463 15 Mar 13 531 10
InLevel Up Coding by Youssef Hosni InTowards AIby Divy Yadav
Claude Code — MEMORY.md: Vectorless RAG: Your RAG Pipeline
Everything you need to know & ho… Doesn’t Need a Vector Database
Read the full article for free through this friend How reasoning-based retrieval beats
link. similarity search on structured documents,…
Mar 18 244 2 5d ago 177 4
See more recommendations
https://medium.com/@simranjeetsingh1497/mastering-adk-tools-function-tools-mcp-tools-openapi-tools-when-to-use-each-8f18c2d9cdbb 71/71