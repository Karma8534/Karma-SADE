# FixBadCode

*Converted from: FixBadCode.PDF*



---
*Page 1*


Open in app
11
Search Write
Spec-Driven
Development: Why
Your AI Writes Bad
Code Without It
The problem isn’t your AI. It’s the format you’re
feeding it.
Vishal Mysore Follow 6 min read · 5 days ago


---
*Page 2*


65 4
There’s a pattern playing out in engineering teams
everywhere right now.
A developer opens their AI coding assistant, pastes
in a user story, and types: “Build this.” The AI
obliges. The code compiles. The tests pass. And
somewhere buried in the implementation is a
decision the developer never made — a default the
AI chose, a behavior nobody specified, a shortcut
that made sense in isolation and causes a
production incident six weeks later.
The developer blames the AI. But the AI did exactly
what it was asked to do.
That’s the real problem.
You’re Not Writing Prompts. You’re
Writing Contracts.


---
*Page 3*


When you ask a human engineer to implement a
feature, they bring years of context with them.
They’ve shipped broken systems before. They
know that “delete the record” is probably wrong.
They’ll ask clarifying questions, flag edge cases in
standup, and push back when something smells
off.
An AI has none of that organizational memory. It
has the text you gave it, and nothing else.
So when your prompt says “allow users to archive
their account,” the AI makes a decision: Does
archive mean soft-delete? Hard-delete? Suspend
billing? Revoke access? Preserve data? Each of
those is a legitimate interpretation. The AI picks
the most statistically plausible one based on its
training data — and moves on.
You don’t find out which interpretation it chose
until you read the code. Or until a user’s data
disappears.


---
*Page 4*


The problem isn’t intelligence. It’s interface. You’re
handing the AI a wish, when what it needs is a
contract.
The Ambiguity Tax
Every underspecified input to an AI carries what I
call an ambiguity tax.
The AI resolves that ambiguity silently, by
choosing defaults. And each default is a decision
you didn’t make — a behavior you didn’t review,
didn’t test, and didn’t consciously approve.
In a small script, this is manageable. In a
production system, ambiguity compounds.
Consider a prompt like: “Build a subscription
cancellation flow.”
The narrative-first AI interprets this as: set the
subscription status to cancelled, redirect the user


---
*Page 5*


to a confirmation page. Done. Reasonable.
Probably wrong.
What about prorated refunds? What about the
billing cycle — does cancellation take effect
immediately or at period end? What about users on
an annual plan cancelling in month two? What
about the audit log required by your payment
processor? What about reactivation — does the
same subscription ID persist?
None of that was in the prompt. So the AI guessed.
And it guessed consistently, confidently, and
completely invisibly.
You inherit every one of those guesses the moment
you run git commit.
The Format Is the Problem
The user story format — “As a [user], I want [action]
so that [outcome]” — was never designed for


---
*Page 6*


machines. It was designed to create empathy. To
give a development team a human anchor for what
they were building.
That empathy layer is exactly what makes it a poor
AI interface.
User stories are compressed. They rely on shared
context, professional intuition, and the ability to
ask follow-up questions in a sprint planning
meeting. Feed a user story to an AI and you’re
handing it the headline and asking it to reconstruct
the article.
What AI actually needs is the opposite of
compression. It needs expansion — explicit system
boundaries, stated constraints, declared
relationships, and defined failure modes — all
expressed in plain language before
implementation begins.
Not pseudocode. Not a schema. Just: here is the
world this feature lives in, here are the rules that


---
*Page 7*


govern it, and here is what correct looks like.
From Narrative to Determinism
The shift is simpler than it sounds. You’re not
learning a new language or adopting a new
toolchain. You’re changing what you describe.
Instead of describing what a user wants, describe
the system they’re interacting with.
Four dimensions cover most of it:
WHAT — the entities, their states, and how they
relate. “A subscription can be active, paused, or
cancelled. A cancelled subscription retains its data for
90 days before permanent deletion.”
WHO — the actors and their permission
boundaries. “Account owners can cancel their
subscription. Team members cannot. Billing admins
can view but not modify subscription status.”


---
*Page 8*


WHY — the business rules that constrain behavior.
“A subscription cannot be cancelled if there is an
outstanding invoice. Users must clear their balance
first.”
HOW — the technical constraints that shape the
implementation. “This runs on a Node.js backend
with Stripe for billing. All subscription state changes
must go through Stripe webhooks, not direct database
writes.”
Now hand that to an AI.
The output changes entirely — not because the AI
got smarter, but because you removed the
ambiguity it was silently resolving. It doesn’t need
to guess what “archive” means. You told it. It
doesn’t need to infer whether data should be
preserved. You declared it. It doesn’t need to
decide how billing interacts with cancellation. You
specified it.
That’s not autocomplete. That’s leverage.


---
*Page 9*


The Hidden Benefit: You Think Better Too
Here’s what nobody talks about when they discuss
AI-assisted development: the act of writing a
system-first specification forces you to make
decisions you were previously deferring.
Most underspecified prompts aren’t lazy — they’re
premature. The developer hasn’t yet resolved what
the correct behavior should be, so they hand the
ambiguity to the AI and hope for the best.
Writing a WHAT/WHO/WHY/HOW breakdown
before you prompt forces you to resolve those
decisions explicitly, in plain language, before any
code exists. You can’t write “a subscription cannot be
cancelled if there is an outstanding invoice” without
first deciding: is that actually the right rule? What
happens if the invoice is disputed? Does this apply
to free trials?


---
*Page 10*


The specification process surfaces decisions that
were going to get made by default — either by you,
intentionally, or by the AI, silently.
Intentional is almost always better.
What This Looks Like in Practice
You don’t need a 20-page document. For most
features, a single structured block of plain English
is enough.
Here’s a lightweight format that works:
Feature: Subscription Cancellation
WHAT:
A Subscription has three possible states: active, can
Cancellation is permanent — a cancelled subscription
a new subscription must be created instead. Subscript
for 90 days post-cancellation, then purged.
WHO:
Account owners can initiate cancellation. Team member
Billing admins can view cancellation status but canno


---
*Page 11*


WHY:
A subscription cannot be cancelled while an unpaid in
Cancellation must trigger an immediate webhook to the
All state changes must be written to the audit log wi
the ID of the user who initiated the action.
HOW:
Node.js backend, Stripe for billing.
Subscription state lives in Stripe — the database ref
not the other way around.
That’s it. Four paragraphs. Every significant
decision is explicit. Every constraint is stated. The
AI has no ambiguity left to resolve on your behalf.
Feed this to your coding assistant alongside the
implementation task and compare the output to
what you get from a user story alone. The
difference isn’t subtle.
The Deeper Shift
We’re in the middle of a transition that most
engineering teams haven’t fully processed yet.


---
*Page 12*


AI is moving from autocomplete to collaborator.
And collaborators need context, not just
commands. They need to understand the system,
not just the task. They need to know the rules
before they write the code.
The user story format served us well for a decade
of human-to-human coordination. It’s a poor
interface for human-to-AI development. Not
because AI is inferior — but because AI is
different. It doesn’t share your context. It doesn’t
attend your standups. It doesn’t know what you
meant. It only knows what you wrote.
Write better. Get better code back.
The skill that’s going to separate strong AI-era
engineers from the rest isn’t prompt engineering
in the clever, trick-the-model sense. It’s
specification thinking — the ability to decompose a
system clearly, state its rules explicitly, and remove
ambiguity before it compounds into bugs.


---
*Page 13*


That skill isn’t new. It’s just more important than
it’s ever been.
Written by Vishal Mysore
Follow
2K followers · 5 following
Holder of multiple patents in AI and software
engineering. Passionate about building scalable
systems, optimizing performance, & driving AI-
powered innovation.
Responses (4)
To respond to this story,
get the free Medium app.
venkat
2 days ago
The killer point here that everyone should think here - “prompts are like
contracts “


---
*Page 14*


2
Fabien
4 days ago
Great post! Small thing on your example: your WHY feels more like
business rules (unpaid invoice, webhook, audit log) than the actual
reason the feature exists.
2
Colby McHenry he/him
1 day ago
BeadsDashboard does this really well
1
See all responses
More from Vishal Mysore


---
*Page 15*


Vishal Mysore Vishal Mysore
What is BMAD- When to Use a
METHOD™? A Si l K l d G h (A
The BMAD-METHOD™ Knowledge graphs are having
(B kth h M th d f t E
Sep 8, 2025 Jan 5
Vishal Mysore Vishal Mysore
How PageIndex Works: GitHub Spec Kit vs
A St b St BMAD M th d A
PageIndex is a vectorless, GitHub’s open-source Spec Kit
i b d t i l i t lkit f d i
Mar 1 Sep 15, 2025
See all from Vishal Mysore
Recommended from Medium


---
*Page 16*


Pankaj Vishal Mysore
Anthropic just added BMAD-METHOD™ :
it t t f AI kill B ildi C t AI
On March 3, Anthropic BMAD (BMad Method) is a
d t d kill t ith d ft
Mar 10 Dec 1, 2025
Neel Thomas In by
Level Up Coding Chris Bao
How BMAD and Ralph
Exploring Spec Driven
A R l ti i i A
D l t (SDD)
Imagine starting your workday
Introduction
b d ibi h t t
Feb 3 Mar 26


---
*Page 17*


In by Balu Kosuri
ArcKit Mark Craddock
I Turned Andrej
ArcKit: Discovering
K th ’
Wh t G t H
By Balasubramanyam Kosuri
ArcKit v4.5.2 introduces three
d th t h
Mar 25 Mar 21
See more recommendations