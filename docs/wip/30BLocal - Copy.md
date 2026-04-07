# 30BLocal - Copy

*Converted from: 30BLocal - Copy.PDF*



---
*Page 1*


Open in app
Search Write
GoPenAI
Member-only story
A 30B Qwen model
runs in real time on a
Raspberry Pi, here’s
why that matters
Sebastian Buzdugan Follow 8 min read · Jan 7, 2026
880 14
Click here to read this article for free:
https://medium.com/@sebuzdugan/a-30b-qwen-
model-runs-in-real-time-on-a-raspberry-pi-heres-
why-that-matters-d51bd8df9bb6?
sk=7677e55bbb68506f13258c61ce0d30a7


---
*Page 2*


A few years ago, I remember struggling to get a 7B
model to respond coherently on a laptop CPU. Fans
screaming, tokens dribbling out, patience wearing
thin. Back then, the idea of a 30B parameter model
running interactively on a Raspberry Pi would
have sounded like a bad joke.
And yet, here we are.
A 30B Qwen model now runs in real time on a
Raspberry Pi 5. Not batch mode. Not minutes per
response. Real, conversational speeds.
That result is not just a fun demo. It quietly breaks
several assumptions many of us still carry about
model size, hardware limits, and what “edge AI”
can realistically mean.
Let’s unpack why


---
*Page 3*


Why a 30B model on a Raspberry Pi
sounds impossible
If you have spent time around large language
models, you probably internalized a simple rule.
Bigger models need GPUs. Small devices get small
models.
This intuition came from real constraints. A 30B
parameter model in BF16 is roughly 60 GB just for
weights. Even aggressive quantization often keeps


---
*Page 4*


you well above what single board computers were
designed to handle.
On top of memory, there is compute. Transformers
are heavy on matrix multiplies. CPUs can do them,
but slowly. GPUs thrive here. Raspberry Pis do not.
So for years, the implicit boundary looked like this:
Edge devices run 3B to 7B models
Maybe 13B if you are patient
Anything beyond that belongs in the datacenter
The provocative claim from ByteShape is that this
boundary is no longer fixed. With the right model,
the right quantization, and the right runtime, a 30B
model can feel responsive even on a Raspberry Pi
5.
That alone is enough to make skeptics raise an
eyebrow.


---
*Page 5*


What “runs in real time” actually means in
practice
Before diving into optimization details, we need to
calibrate expectations. “Real time” is a slippery
term.
Tokens per second vs human perception
The reported throughput sits around 8 to 8.5
tokens per second. That number might sound low
if you are used to GPUs pushing hundreds of
tokens per second.
But raw throughput is not how humans experience
chat.
Most people read at roughly 200 to 300 words per
minute. Typing is slower. Conversation is slower
still. At around 8 tokens per second, text appears
fast enough to feel interactive, not frustrating.
There is also the question of time to first token.
Seeing a response start quickly matters more than


---
*Page 6*


total completion time. A steady stream beats a long
pause followed by a burst.
In other words, if it feels like someone is typing
back at you, the system wins.
Hardware constraints of a Raspberry Pi 5
The Raspberry Pi 5 brings meaningful
improvements over earlier models, but it is still
constrained.
You are dealing with:
A CPU that prioritizes efficiency over brute force
Limited memory bandwidth compared to
desktop systems
Tight thermal limits under sustained load
On this class of hardware, memory access often
dominates compute. Moving data becomes more
expensive than multiplying matrices.


---
*Page 7*


This is the first hint that model optimization on
edge devices is not just about FLOPs. It is about
bytes.
Meet the model: Qwen3–30B-A3B-
Instruct
The star of this story is Qwen3–30B-A3B-Instruct.
Qwen is a family of open models developed by
Alibaba, spanning multiple sizes and use cases.
The 30B variant sits in a sweet spot. Large enough
to reason well, small enough to be tractable with
aggressive optimization.
The “A3B” part refers to an architectural choice
inside the transformer. At a high level, it balances
attention and feed-forward components to
improve efficiency. You do not need to understand
the internals to appreciate the impact. It matters
because architecture influences memory access
patterns and kernel efficiency.


---
*Page 8*


Being instruction-tuned is equally important. Edge
use often means direct interaction with humans.
You want a model that follows prompts well
without extensive prompt engineering.
In short, this is not a raw base model forced onto
tiny hardware. It is a carefully chosen starting
point.
The optimization insight most people
miss
This is where the story gets interesting.
Why fewer bits don’t always mean faster
Quantization reduces the number of bits used to
store weights. Intuitively, fewer bits should mean
less memory and faster inference.
In practice, it is more complicated.
Ultra-low-bit formats like 4-bit often require extra
decoding steps. On CPUs, that decoding can


---
*Page 9*


become a bottleneck. You save memory bandwidth
but spend more cycles unpacking values.
In frameworks like llama.cpp, kernel
implementations matter a lot. Some quantization
formats map cleanly to efficient kernels. Others do
not.
The counterintuitive result is that a 5-bit or mixed-
bit format can outperform a 4-bit format on real
hardware.
Smaller is not always faster.
Treating memory as a fixed budget
ByteShape’s key insight is to treat memory as a
fixed budget, not a variable to minimize at all
costs.
Instead of asking “How low can we go in bits?”,
they ask:
How much memory do we have?


---
*Page 10*


Which formats maximize throughput within that
ceiling?
Which layouts best match CPU caches and
memory bandwidth?
This is a systems problem, not a pure ML one.
By choosing quantization schemes that play nicely
with llama.cpp kernels and the Raspberry Pi’s
memory subsystem, they unlock performance that
naive approaches leave on the table.
It is optimization guided by reality, not by theory
alone.
Quality vs speed: keeping over 90% of
BF16 performance
Speed is only half the story. A fast but incoherent
model is not very useful.
The optimized Qwen3–30B-A3B-Instruct reportedly
retains around 92 to 94 percent of BF16 baseline


---
*Page 11*


quality. BF16 here serves as the reference point,
essentially “full precision” for practical purposes.
This retention is measured conceptually through
standard evaluation tasks and qualitative behavior.
Does the model reason similarly? Does it follow
instructions with comparable reliability?
For a 30B model running on a Raspberry Pi, that
level of quality is unusual. Historically, edge
deployments of large models involved much
harsher tradeoffs.
This result suggests that with careful quantization,
quality degradation is no longer the dominant
concern people assume it to be.
How this compares to previous Raspberry
Pi LLM setups
To appreciate the shift, it helps to look backward.
What was possible before


---
*Page 12*


Before this, most comfortable Raspberry Pi setups
lived in the 7B to 13B range. Even then, users often
accepted:
Slower responses
Reduced context lengths
Noticeably weaker reasoning
These models were fine for simple chat,
summarization, or coding helpers. They struggled
with more complex tasks.
The hardware was the limiting factor, and
everybody knew it.
Why this result changes expectations
Running a 30B model at interactive speeds crosses
a psychological barrier. It reframes what counts as
“large” on edge hardware.
It means tasks that previously felt out of reach,
deeper reasoning, better instruction following,


---
*Page 13*


richer responses, start to become viable without a
GPU or cloud connection.
This does not mean smaller models are obsolete. It
means the ceiling moved.
ByteShape vs other toolchains
It is worth situating this result in the broader
ecosystem.
Tools like Unsloth focus heavily on training and
fine-tuning efficiency. They shine when you care
about leaderboard scores or maximizing quality on
a given dataset.
ByteShape’s emphasis is slightly different. The
focus is on user-perceived experience and real
throughput on constrained hardware.
At similar quality levels, ByteShape claims better
tokens per second than competing approaches.
The key word here is “at similar quality.”


---
*Page 14*


Benchmarks are tricky. Different evaluation suites
tell different stories. The important takeaway is not
who wins a chart. It is that optimization objectives
matter.
If you care about interaction on a Raspberry Pi,
throughput and responsiveness beat abstract
scores.
Why this matters beyond a cool demo
It is tempting to write this off as a neat trick. That
would be a mistake.
Implications for edge and offline AI
A responsive 30B model on a Raspberry Pi unlocks
real use cases:
Privacy-preserving assistants that never call
home
Reliable systems in disconnected or hostile
network environments


---
*Page 15*


Lower latency applications where cloud round
trips are unacceptable
These are not niche needs. They show up in
healthcare, manufacturing, education, and
personal computing.
The edge is where constraints force innovation.
Systems co-design is the real story
The deeper lesson is about co-design.
Progress here did not come from scaling the
model. It came from aligning architecture,
quantization, and hardware realities.
This mindset will matter more as we push models
into ever smaller and cheaper devices. The future
of AI is not just about bigger GPUs. It is about
better systems thinking.
The skeptics’ view: fair criticisms and
open questions


---
*Page 16*


Healthy skepticism keeps us honest.
This setup is not plug-and-play for average users. It
requires careful configuration and knowledge of
runtimes like llama.cpp.
Power consumption and thermals also matter.
Sustained high load on a Raspberry Pi 5 is very
different from short demos.
And for many tasks, a well-tuned 7B or 13B model
may still be the smarter choice. Simpler, faster,
cheaper.
The point is not that everyone should run 30B
models on SBCs. It is that the option now exists.
Where edge LLMs go from here
Looking ahead, a few trends stand out.
Single board computers will continue to improve
CPUs and memory bandwidth. Kernel and runtime
optimizations will compound those gains.


---
*Page 17*


Quantization research will likely become more
hardware-aware, less focused on theoretical bit
counts.
As these lines converge, the gap between “edge”
and “datacenter” AI will continue to narrow. Not
disappear, but narrow enough to change design
decisions.
Fun facts: large language models on tiny
computers
Here are a few details that put this milestone in
perspective.
A Raspberry Pi now runs models once considered
GPU-only.
A 5-bit quantized model can outperform a 4-bit one
on real hardware due to better cache alignment
and kernel support.
Human conversational speech averages around 2
to 3 words per second, making 8 tokens per second


---
*Page 18*


feel surprisingly natural.
Early Raspberry Pi models shipped with 256 to 512
MB of RAM. Today, we squeeze tens of billions of
parameters into the same form factor.
Resources
ByteShape blog post on Qwen3–30B-A3B-
Instruct: https://byteshape.com/blogs/Qwen3-
30B-A3B-Instruct-2507/
Hacker News discussion:
https://news.ycombinator.com/item?id=46518573
Reddit thread on LocalLLaMA:
https://www.reddit.com/r/LocalLLaMA/commen
ts/1q5m2n6/a_30b_qwen_model_walks_into_a_r
aspberry_pi_and/
llama.cpp project documentation:
https://github.com/ggerganov/llama.cpp
Conclusion


---
*Page 19*


A 30B model running in real time on a Raspberry
Pi forces us to rethink what “too big for edge”
really means.
This is less about a single model and more about a
shift in mindset. When you treat hardware
constraints as design inputs instead of blockers,
surprising things happen.
If you have a Raspberry Pi collecting dust, this
might be a good moment to dust it off and
experiment with local LLMs yourself.
Qwen AI Machine Learning Raspberry Pi Model
Published in GoPenAI
Follow
3.8K followers · Last published 13 hours ago
Where the ChatGPT community comes together to
share insights and stories.


---
*Page 20*


Written by Sebastian Buzdugan
Follow
724 followers · 390 following
ML Engineer | PhD Student in AI
Responses (14)
To respond to this story,
get the free Medium app.
David Wynter
Jan 24
Search for ezrknpu project on GitHub. It has taken quite some time to
exploit the 6 TOPS NPU on the RK3588 SoC seen on SBC like the Orange
Pi5. I always thought this was a missed opportunity. The custom binary
format for the models is an inhibitor though.
15 1 reply
Michael Harms he
Jan 25
In short, this is not a raw base model forced onto tiny
hardware. It is a carefully chosen starting point.


---
*Page 21*


I'm a newbie to this, but 30.5B in total and 3.3B activated, means that you
actually using a 3B model? Can someone explain me, how you made it
from 3B to 30B in a model?
11 2 replies
Roger Collins
Jan 25
More proof that the 'Big Boys' (Amazon, Google, MS, etrc) have a VERY
steep road to climb to pay for their data center investments. If I can run a
free model on a PI, I won't need to send $$$ to Amazon...
11 1 reply
See all responses
More from Sebastian Buzdugan and
GoPenAI


---
*Page 22*


Sebastian Buzdugan In by
GoPenAI Carlo C.
What Are MCP
Dashboard Studio RS:
S ? Th N AI
H W bA bl
Artificial intelligence is taking
A journey from vendor lock-in
bi l b d j t
t i fi t li t id
Mar 8, 2025 Dec 30, 2025
In by Sebastian Buzdugan
GoPenAI Yi Ai
How to Turn Any
An Advanced
W b it i t Fi
I t ti SQL A t
Most people talk about local
Solving Large Result-Set
LLM fi t i lik
B i i SQL A t
Jan 2 Feb 5
See all from Sebastian Buzdugan See all from GoPenAI
Recommended from Medium


---
*Page 23*


In by In by
AI Advanc… Jose Crespo, P… Predict Nov Tech
Anthropic is Killing I’m Skeptical of AI hype
Bit i b t h t h d
The AI-native currency When Anthropic, Google
l d i t hidi i D Mi d d O AI ll
Feb 17 Feb 2
In by In by
Activated Thin… Shane Coll… Level Up Cod… Teja Kusire…
The $830 Billion Wake- I Stopped Using
U C ll H Cl d Ch tGPT f 30 D
In one week, Anthropic didn’t 91% of you will abandon 2026
j t l d t th l ti b J 10th
Feb 17 Dec 28, 2025


---
*Page 24*


In by In by
GitBit John Gruber Write A Cat… Dr. Patricia Sc…
Websites Are Dead. Go As a Neuroscientist, I
H I t d Q it Th 5 M i
I finally did it. I launched a Most people do #1 within 10
bl Th I li d th h d i t f ki ( d it
Feb 10 Jan 14
See more recommendations