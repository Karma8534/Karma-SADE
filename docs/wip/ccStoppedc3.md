# ccStoppedc3

*Converted from: ccStoppedc3.PDF*



---
*Page 1*


Open in app
11
Search Write
Member-only story
Anthropic Killed My
OpenClaw Setup 3
Times. The Third Time,
I Stopped Blaming
Them.
Flat-rate AI was a gym membership. The real
trap isn’t the price hike. It’s what Anthropic
wants you to switch to.
Phil | Rentier Digital Following 7 min read · 23 hours ago
40 2
Anthropic just killed OpenClaw. Your Claude Max
subscription no longer covers third-party tools.


---
*Page 2*


Boris Cherny dropped the news on X on a Friday
night (classic), and the community lost it. Everyone
is screaming about the price.
They’re screaming about the wrong thing.
TL;DR: Flat-rate AI for agents was never a business
model, it was VC subsidizing adoption. Anthropic is
pushing you toward Cowork and first-party tooling,
which is vendor lock-in dressed as optimization. But
unlike telecom, AI models are interchangeable. The
switching cost is near zero. Run env | grep ANTHROPIC
before you do anything else.


---
*Page 3*


Three setups, zero self-awareness, one API key. Spoiler: it was me.
I know because this is the third time it happened
to me. January: a wall of 403s, my OpenClaw
instance dead, me binge-reading Cherny’s tweets
like a maniac. I yelled at the screen. Everyone was
yelling. February: I rebuilt. Kimi K2.5, fifteen
dollars a month, pride of the guy who found the
fire escape while the building burns. Today: I just
nodded. No surprise, no anger. And that’s when it
clicked: the problem was never Anthropic. The
problem is that we all believed an all-you-can-eat
buffet for machines that eat 24/7 could last. The
real trap isn’t the price hike. It’s what Anthropic
wants you to switch to instead.
The Gym Membership Model
There’s a French saying: better pray to God directly
than bother with the saints. I never trusted
wrappers. Not for long, anyway.


---
*Page 4*


But OpenClaw wasn’t just a wrapper. It was an
arbitrage play. A $200/month Claude Max
subscription routed through a third-party harness
that removed all rate limits. Power users were
doing somewhere between one and five thousand
dollars of compute on that subscription. A gym
membership where you move your entire
company’s fitness program into the squat rack and
expect the gym owner to smile about it.
The mobile carriers figured this out twenty years
ago. “ Unlimited data” was always a bet that most
people would scroll Twitter on the train, not tether
their laptop and download entire seasons of
whatever. The bet held because humans sleep, eat,
commute. AI agents don’t. They run twenty-four
hours, seven days, consuming tokens at a pace that
makes the carrier math implode.
This is not an Anthropic-specific problem. Cursor
went through the same “important pricing
updates.” Back in August 2025, an article on


---
*Page 5*


Medium called “The AI Subscription Illusion”
already described the prisoner’s dilemma
perfectly: if one provider switches to usage-based
pricing, they lose users to whichever VC-funded
competitor still maintains the flat-rate illusion.
Everyone knows the model is broken, nobody
wants to blink first.
Every company that offered flat-rate access to
frontier models eventually hits the same wall: the
better the model gets, the more compute each
agent session burns. The capacity cost scales with
capability. The math doesn’t care who you blame.
Now, to be fair: the flat-rate era wasn’t useless. It
let thousands of builders discover and adopt AI
agents in the first place. Anthropic wasn’t wrong to
offer it. They were wrong to pretend it would last.
Nobody ships a buffet where the food gets more
expensive to make every quarter.
The Trap Nobody’s Discussing


---
*Page 6*


Everyone on X is debating the price. Nobody is
talking about the destination.
Anthropic is pushing you toward Cowork and
Claude Code first-party. The official justification is
technical: first-party tools optimize the “prompt
cache hit rate,” meaning they reuse previously
processed text to save compute. Third-party
harnesses like OpenClaw bypass those
optimizations. Translation: you pay less, but you’re
locked into their compute pipeline, optimized for
THEM, not for you.
I’ve been building with CLIs and open tooling long
enough to know where this ends. Proprietary
ecosystems always start with “we optimized it for
you” and end with “you can’t leave.” The telecom
playbook. The enterprise SaaS playbook. The cloud
vendor playbook. Every single time.
And the first-party tooling has its own problems.
Cowork shipped with prompt injection


---
*Page 7*


vulnerabilities that let attackers steal files via
whitelisted curl commands within forty-eight
hours of launch. That’s the tool they want you to
migrate to. The “optimized” alternative.
Wrappers aren’t better, by the way. Lovable ran
fifty-seven incidents in ninety days. Security
researchers found sixteen vulnerabilities in a
single hosted app. Users get charged for the AI’s
own debugging loops. Whether you go through the
saints or through the church, the intermediary
adds a failure mode you didn’t ask for.
Anthropic has patched some of those Cowork
issues since January. The point isn’t that Cowork is
dangerous today. The point is structural: when you
depend on a single vendor for your model, your
tooling, AND your compute pipeline, every bug is a
single point of failure. Every pricing change hits
you with no escape route. Every “important
update” email is a hostage negotiation where you
already gave up your leverage.


---
*Page 8*


Your stack is only as independent as the vendor
you can’t replace.
What I Actually Pay (And One Command
to Run Before You Switch)
Three things, quick.
First: Anthropic isn’t slamming the door
completely. They’re installing a toll booth. Existing
subscribers get a one-time credit equal to their
monthly plan cost. There are discounted “extra
usage” bundles if you want to keep your Claude
login. And there’s a refund option by email. You
can keep going with Claude through extra usage or
switch to an API key. Not a wall. A price increase
with a grace period.
Second: what I actually pay. I already solved this
problem in February, so I won’t re-do the whole
tutorial. I rebuilt the entire setup for $15/month
with Kimi K2.5 as primary and MiniMax as


---
*Page 9*


fallback. Two $5 VPS instances for redundancy,
works fine, ships every day.
Third, and this is the one nobody covers: the silent
billing gotcha.
If you have ANTHROPIC_API_KEY set anywhere in your
shell environment, claude -p will use it silently
instead of your OAuth subscription. No warning,
no prompt, no confirmation dialog. It just bills
your API account. You think you're on your Max
subscription, burning through your flat-rate
allowance. You're not. You're on pay-per-token and
the meter is running.
Run this right now:
env | grep ANTHROPIC
Or if you want to be thorough:


---
*Page 10*


grep -r ANTHROPIC_API_KEY ~ 2>/dev/null
If either returns something and you thought you
were on your subscription, you have a problem.
Fix it before you do anything else.
(And yes, the service_tier and total_cost_usd
fields in Claude's JSON output are misleading. They
show data even on OAuth/Max where they don't
reflect actual billing. That's a metadata/reporting
issue, not a real charge. But a stray API key in your
environment? That one's real.)
A ghost env var is all it takes to turn your “free”
session into a bill.
Why AI Isn’t Telecom (And Why You Win
This Time)
The gym membership analogy breaks down at one
specific point, and it breaks in your favor.


---
*Page 11*


In mobile, the carriers won the war. Switching
networks meant different coverage maps, slow
number portability, early termination fees. The
switching cost was enormous. You could complain
about AT&T all you wanted. You were staying with
AT&T.
In AI, models are interchangeable. I proved it
three times: Claude to Kimi K2.5, same stack, same
quality for agent workloads. OpenClaw already
supports Codex, MiniMax, Z.AI, Gemma 4. The
community is already voting with its feet. Google
just released Gemma 4 under Apache 2.0 with day-
one OpenClaw compatibility, and the dev
🔓
community received it like a jailbreak . Running
Gemma 4 locally on an RTX GPU means zero API
costs. Zero vendor dependency. The model runs on
your hardware.
The switching cost in AI is close to zero. That one
fact changes everything about the power dynamic.
Anthropic’s vendor lock-in strategy cannot work


---
*Page 12*


long-term because the moment they make the cage
uncomfortable, you walk into the next one. Or
better: you stop using cages entirely.
The multi-model stack is the exit. The only
question worth asking isn’t “how much does it
cost” but “how many providers can you lose before
your pipeline stops.”
In six months, Anthropic will have a new pricing
tier with a corporate name and a blog post
explaining why it’s better for everyone. OpenAI
⚰
will have copied it. “RIP flat-rate” with emojis.
Meanwhile, the people who build will have already
moved. Not because they’re smarter. Because they
understood one simple thing: in a world where
models are interchangeable, the only real risk is
depending on a single provider.
How many providers do you have left if this one
closes tomorrow?


---
*Page 13*


Sources
Boris Cherny’s X thread on the OpenClaw
subscription cutoff (April 3, 2026). Amit, “The AI
Subscription Illusion: Why Flat-Rate Pricing Is
Failing” (Medium, August 2025).
(*) The cover is AI-generated. The lobbying budget
for that gymnasium metaphor was surprisingly
reasonable.
When Anthropic killed OpenClaw for the third time, I
stopped blaming them-and realized the real trap is
vendor lock-in disguised as optimization. The welcome
kit includes the CLI blueprint, so you can build
interchangeable agent tooling that survives the next
pricing shift.
→ Get the welcome kit
Originally published at https://rentierdigital.xyz on
April 4, 2026.


---
*Page 14*


Artificial Intelligence Technology Anthropic Claude
Openclaw Claude Code
Written by Phil | Rentier Digital
Following
5.4K followers · 4 following
Claude Code in production. What works, what
breaks, what ships.
Responses (2)
To respond to this story,
get the free Medium app.
Chad Williams
14 hours ago
Thanks for the frequent and honest sharing
It’s obvious if you’re running any kind of business, or expect ‘service


---
*Page 15*


availability’. You can’t afford not to have redundant/failover service
providers or services routes to provide a dependable offering… more
1 reply
Kunle Gbadebo
14 hours ago
Yo Phil, what's your X @??
Would love to read more of your content.
1 reply
More from Phil | Rentier Digital
Phil | Rentier Digital In by
Generati… Phil | Rentier …
Spotify Built “Honk” to
Every Claude Code
R l C di I B il
T t i l T h Y
Last week, Spotify’s co-CEO
CLAUDE.md, slash
t ld W ll St t th t hi b t
d lti Cl d


---
*Page 16*


Feb 20 Feb 22
Phil | Rentier Digital Phil | Rentier Digital
I Watched 25 Claude Anthropic Just Crashed
C d Y T b Vid $15 Billi i
Learning Claude Code from I typed /security-review into
Y T b i lik l i t Cl d C d F id
Feb 17 Feb 22
See all from Phil | Rentier Digital
Recommended from Medium


---
*Page 17*


Alex Rozdolskyi In by
AI Advanc… Marco Rodrigu…
5 OpenClaw
10 Tips to Make Your
A t ti Th t G
Lif E i With
We don’t have bandwidth” is
Learn the most useful
b i td t d
d h t i t ll
Feb 16 Mar 7
In by In by
Activated… Adi Insights and… CodeX MayhemCode
I Ignored 40+ The Mac Mini M4 vs
O F Alt ti AMD Mi i PC D b t I
Everyone is building agent The Mac Mini M4 versus AMD
f k M t P th i i PC ti h
Mar 21 5d ago
Ewan Mak In by
Predict srgg6701
Mac Mini M4 vs AMD
You Have No Idea How
Mi i PC f L l AI
S d S Alt
The single most important
OpenAI stopped being a
b h b i l l
l It’


---
*Page 18*


5d ago Mar 27
See more recommendations