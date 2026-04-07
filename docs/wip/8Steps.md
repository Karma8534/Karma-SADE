# 8Steps

*Converted from: 8Steps.PDF*



---
*Page 1*


Open in app
11
Search Write
Member-only story
I Stopped Vibe Coding
and Built a Real App.
The Method Nobody
Teaches.
I’ve been shipping software for 30 years. I
turned that into an 8-step process for building
real apps with AI.
Phil | Rentier Digital Following 7 min read · Mar 28, 2026
88 1
Y ou asked an AI to build you an app. It looks
good and it works. Almost. The moment you
touch one feature, another one breaks.


---
*Page 2*


Every time a real user tries it, there’s a bug. (No no,
don’t click that.) The login doesn’t actually protect
anything. One user’s clients show up in another
user’s dashboard. The payment page collects the
credit card but never records the transaction.
Your process is broken. The code is just the
symptom.
TLDR: Stop telling the AI “build me X.” Start
specifying what X means, what it implies, how to
verify it. Eight steps, same loop every time. Start with
your next feature.


---
*Page 3*


Vibe coding vs. blueprints: one breaks everything, one actually ships.
I built a straw-bale house with my own hands. Five
years. The parallel with software (I’ve been in IT
for 30 years) is uncanny: same need for sequence,
same need to understand each specialty without
becoming a specialist. I turned that into a method
so you can develop your app like a pro.
The gap nobody talks about
Vibe coding is broken. Not the tools. Not the AI.
The way people use it.
Every tutorial shows the same thing: type a
prompt, get an app, celebrate. And it works, for a
demo. A screen with buttons that look right.
Then you need the app to do real things. Multiple
users who each see only their own data. Payments
that actually process. A new feature that doesn’t
silently break three old ones.


---
*Page 4*


The AI optimizes for “works right now.” A real app
needs “still works in six months.” That gap is not
about code quality. It’s about knowing what to ask
for, in what order, and how to check that you got it.
The Blueprint Method
Eight steps. Same loop for every feature, from a
simple client list to Stripe payment integration.
1. Global spec. What do you want, in plain
language? “I want to manage clients.” Vague on
purpose. Just enough to start.
2. Implications. The step most people skip, and the
one that saves you. Ask the AI: “What does this
imply technically? What tables, pages, components
do I need?” The AI unpacks your request into a list
of concrete things that need to exist. Some you
expected. Others (an ID column, timestamps,
validation rules) you didn’t think of. Now you see
the full picture before building anything.


---
*Page 5*


3. Detailed spec. Get specific. Fields, types,
validation, error handling, what happens when
something goes wrong. This is where “build me a
client list” becomes usable.
4. Build. Hand the detailed spec to the AI. Let it
build.
5. Explain. Ask the AI: “Explain what you just built
and why.” You don’t read the code. But you
understand the flow. This understanding
accumulates. By your tenth feature, you have a rich
mental model of your entire app.
6. Verify. Check that it works. Not by reading code.
By using the app, testing edge cases, and asking
the AI “what could go wrong with this?”
7. What can go wrong. Every feature has specific
traps. Auth? The AI stores passwords in plain text.
Payments? It ignores webhook failures. Security?
Overly permissive policies. Name the traps so you
catch them.


---
*Page 6*


8. Non-regression. Check that everything from
previous features still works. The most common
vibe coding failure: adding something new that
silently breaks three old things.
The depth increases as you go. Your first spec is
two sentences. By the time you’re doing payments,
it’s two pages. Same method. Your skill grows.
A concrete example: authentication
This is where vibe coding fails most spectacularly.
Before.
“Add a login to my app.”
The AI builds a page with email and password
fields, a button, a redirect. It looks like a login. The
UI is fine. But auth is not a UI feature. Auth is
infrastructure. The login page is the visible 10%.
The other 90% is session management, token
validation, route protection, data isolation. The AI
skips all of it because you didn’t ask.


---
*Page 7*


You ship it. User A logs in. User B logs in. User B
sees User A’s data.
After.
Same feature, with the method.
Step 1 (global spec): “Each user has their own
account. They log in with email and password.
Once logged in, they see only their data.”
Step 2 (implications): you prompt the AI to explain
what this means technically. It comes back with:
authentication vs authorization (two different
things), sessions, tokens, route protection, and
linking data to users (every record needs a user_id
column). You didn’t know you needed half of this.
Now you do. Before writing a single prompt to
build anything.
Step 3 (detailed spec): sign up with email
confirmation. Login with email and password.
Logout button. Session that auto-expires after


---
*Page 8*


inactivity. Route protection for ALL pages except
login and signup. A user_id column on every data
table. Automatic filtering by user on every query.
That’s a contract. Every expectation stated, every
behavior defined.
Then you build, verify, name the traps (sessions
that never expire, user_id checked on INSERT but
not on UPDATE or DELETE), and check regression
against every previous feature. You know the loop.
Same eight steps.
The difference between “add a login” and this is
the difference between a door that looks locked
and a door that actually is.
The construction sequence
Build in this order:
Setup and deploy (get something live
immediately, even a blank page)


---
*Page 9*


Understand the building blocks (frontend,
backend, database, how they talk)
Design the interface before building it
(vocabulary + consistency rules)
Your first feature (simple CRUD, learn the loop)
Data relationships (things that connect to other
things)
Authentication (who are you)
Data isolation (each user sees only their own
data)
Testing (automate the verification you’ve been
doing by hand)
Dashboard and polish (make it feel like a
product)
Payments (the feature with the most expensive
bugs)
Go live for real (production deploy, domain,
monitoring)


---
*Page 10*


Each step builds on the previous. You can’t add
authentication before you have pages to protect.
You can’t add payments before you have users to
charge. You can’t test effectively before you have
features to test.
Every vibe coding disaster I’ve seen follows the
same pattern: someone built the cool feature first
(payments, dashboards, fancy UI) and bolted on
the boring stuff later (auth, security, error
handling). The boring stuff never fits right because
it was never part of the architecture.
Skip ahead, and you’re wiring electricity in a house
with no walls.
The death loop (and how to escape it)
Friday afternoon. You just want to ship one more
fix before the weekend. The bug is small. You
prompt the AI. The fix works. Except now the
sidebar is broken. You prompt again. Sidebar fixed,
but the save button doesn’t submit anymore. One


---
*Page 11*


more prompt. Save works, sidebar broke again,
and the login page is a white screen.
Your pool is waiting. Your kids are asking when
you’re done. You keep prompting. Three rounds
🫠
ago you had one bug. Now you have four.
That’s the death loop.
Each patch fixes one thing and breaks another
because the AI keeps treating symptoms. The root
cause is still there, buried under layers of quick
fixes. You’re not debugging anymore. You’re
making it worse with every prompt.
The exit is always the same. You stop prompting.
You revert to the last version that worked (this is
why Git exists). And you come back with a different
prompt: “Don’t fix the symptom. Explain what this
error means at the root. I’ve tried fixing it twice
and each fix created new bugs.”


---
*Page 12*


Sometimes the feature is too tangled to save. You
revert and rebuild it from scratch with a better
spec. Sounds painful. Actually faster than a sixth
round of whack-a-mole.
Teams get stuck in death loops for weeks. That’s
why the diagnosis in Bloomberg’s AI coding
productivity crisis was off: they measured output
speed, not loop frequency.
Spec quality is everything
Same feature. Two specs. Two results.
Bad spec: “Build me a client page.”
The AI guesses everything. Layout, columns,
buttons, what happens when there’s no data. The
result is random. You didn’t specify anything, so
the AI filled every blank with its own judgment.
Which is often wrong.
Good spec: “Build a client list page with a sidebar
navigation. In the main area, a table with columns:


---
*Page 13*


name, phone, email, city. A search bar above the
table. An ‘Add client’ button that opens a modal
form. When there are no clients, show ‘No clients
yet, add your first one’ with a button. Loading state
with a skeleton. Error state with a user-friendly
message.”
Every element is specified. The result is
predictable. And (this is the key) you can verify it,
because you know exactly what you asked for.
Bad spec = bad contract. The AI fills the blanks
with guesses. Good spec = good contract. Every
expectation stated, every behavior defined. I built
the full prompt contracts framework after enough
features went sideways. Same principle: the spec is
the product.
This is learnable. Your first spec will be two
sentences. By your tenth, you’ll write two pages
without thinking about it. The method trains you,
one feature at a time.


---
*Page 14*


Spec. Build. Verify. Repeat.
The AI writes all the code. I write zero. But I
specify exactly what I want, I understand what was
built (without reading code), and I verify
everything systematically. That’s how I ship
production apps with real users, real payments,
and data isolation that actually holds.
“Building” and “shipping” are not the same verb.
You asked an AI to build you an app. Now you
know how to actually ship it. Eight steps, same
loop. Tedious. Not sexy.
Following through is on you.
(*) The cover is AI-generated. The straw-bale house
is real though.


---
*Page 15*


The difference between a demo and a real app isn’t
code quality-it’s knowing what to ask for and how to
verify it. We cover the production patterns that turn
vibe-coded features into shipping-ready infrastructure.
→ Get the welcome kit
Originally published at https://rentierdigital.xyz on
March 28, 2026.
Programming Artificial Intelligence Vibe Coding
Software Development Claude Code
Written by Phil | Rentier Digital
Following
5.4K followers · 4 following
Claude Code in production. What works, what
breaks, what ships.


---
*Page 16*


Responses (1)
To respond to this story,
get the free Medium app.
Phil Mickelson
6 days ago
I've been writing code for about 45 years (Polymorphic 88 first
computer!) Bottom line, just getting into AI coding and I've been following
you for a couple of weeks or so. Your posts are GREAT! And, given my
experience with writing code, this one… more
3
More from Phil | Rentier Digital


---
*Page 17*


Phil | Rentier Digital Phil | Rentier Digital
gitignore Protects Your I’m a Control Freak. My
R N t Y M h VPN Sh ld B
Your .gitignore protects your I replaced Tailscale with self-
A l d h t d N tBi d b hi d T fi
5d ago 6d ago
Phil | Rentier Digital Phil | Rentier Digital
Why CLIs Beat MCP for Spotify Built “Honk” to
AI A t A d H R l C di I B il
“mcp were a mistake. bash is Last week, Spotify’s co-CEO
b tt ” t ld W ll St t th t hi b t
Feb 17 Feb 20
See all from Phil | Rentier Digital
Recommended from Medium


---
*Page 18*


In by In by
The Ai Studio Ai studio AI Software Engi… Joe Nje…
How to Build Multiple Anthropic Leaks (New)
AI A t U i Cl d M th (A d
A practical guide to Claude Mythos is the new
t t i d l i d AI d l A th i
Mar 3 6d ago
In by In by
Write A Catal… 𝐍𝐀𝐉𝐄𝐄𝐁… How To Pro… Marcellinus Pr…
AI Business Ideas That The Shocking Truth
S ll N Will B Ab t P i I
Why the next wave of AI Here’s what passive income
i f ith AI t ll l k lik
Mar 23 Mar 24


---
*Page 19*


In by In by
CodeX MayhemCode AI Advanc… Marco Rodrigu…
Mini PC vs Desktop PC 10 Tips to Make Your
f L l LLM i 2026 Lif E i With
Most people buying hardware Learn the most useful
f l l AI i 2026 k th d h t i t ll
Mar 26 Mar 7
See more recommendations