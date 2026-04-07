# Titans170vsLLM

*Converted from: Titans170vsLLM.pdf*



---
*Page 1*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
AI Advances
Member-only story
A 170M Model Just Beat GPT-4.
Google’s TITANS Explains Why Size
Doesn’t Matter
A technical deep dive into test-time learning, surprise-gated memory,
and what cognitive science teaches us about machine memory.
Delanoe Pirard Follow 28 min read · Dec 31, 2025
842 18
Open in app
1
Search Write
https://medium.com/p/69b319f1f516 1/66


---
*Page 2*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Search Write
The convergence of biological memory and artificial intelligence — where neuroscience meets neural
networks.
⚠
If you’re not a Medium member, you can read this article for free using
my friend link: Read for free.
What if the key to better AI memory has been hiding in cognitive psychology
textbooks all along?
On December 31, 2024, Google Research published TITANS, an architecture
that implements principles neuroscientists have studied for decades:
multiple memory systems operating at different timescales, a surprise
mechanism that modulates memory encoding, and adaptive forgetting that
preserves system plasticity.
https://medium.com/p/69b319f1f516 2/66


---
*Page 3*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
The results are significant: models with 170M to 760M parameters
outperform GPT-4 on the BABILong benchmark, designed to evaluate
reasoning over extremely long contexts. But the numbers aren’t the story.
The story is what TITANS reveals about the fundamental limitations of
current architectures, and what cognitive science suggests we should build
instead.
This article goes deep. We’ll cover:
The Atkinson-Shiffrin memory model and its neural substrates
The mathematics of test-time learning (with complete derivations)
How TITANS implements associative memory inspired by hippocampal
mechanisms
What Complementary Learning Systems theory predicts about this
approach’s limitations
An honest assessment of what works and what doesn’t
Note: This article is the technical companion to my previous piece
“Transformers Are Dead. Google Killed Them — Then Went Silent”
(December 17, 2025), which covered TITANS’ benchmarks, critical analysis,
and reproducibility issues. Here, we dive into the why: the neuroscientific
and mathematical foundations that explain how the architecture works at a
mechanistic level.
Transformers Are Dead. Google Killed Them — Then Went Silent
A deep dive into Google’s neural long-term memory architecture
that claims 2M+ token context windows with O(n)…
medium.com
https://medium.com/p/69b319f1f516 3/66


---
*Page 4*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
TITANS Explained: Quick Summary
TITANS implements multiple memory systems inspired by cognitive
science: working memory (attention), long-term memory (neural
memory module), persistent memory (fixed parameters)
Key mechanism: the model uses a gradient-based “surprise metric” to
decide what to store, analogous to noradrenergic modulation in the brain
Mathematical foundation: online learning with momentum, connecting
to Polyak acceleration and the delta rule from classical learning theory
Theoretical advance: TITANS provably solves problems outside TC⁰,
transcending the expressivity limits of standard Transformers
Empirical result: 170M-760M parameter models outperform GPT-4 on
BABILong (long-context benchmark)
Critical limitation: an independent analysis (Di Nepi et al., 2025) shows
that memory alone cannot learn when the backbone is frozen, exactly
what Complementary Learning Systems theory predicts
https://medium.com/p/69b319f1f516 4/66


---
*Page 5*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
When 760M parameters outperform giants — the TITANS empirical triumph.
The Thesis
This article argues that TITANS matters not for its benchmarks, but for what
it reveals about the fundamental requirements of artificial memory. As a
transformer alternative, TITANS challenges the core assumption that
“attention is all you need.”
Cognitive science has known for decades that effective memory requires:
1. Multiple systems operating at different timescales
2. Selective encoding based on surprise and salience
https://medium.com/p/69b319f1f516 5/66


---
*Page 6*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
3. Active forgetting to prevent interference
Other architectures have already attempted to integrate these principles.
Memoria (2023) proposed a neuroscience-inspired multi-scale memory. But
TITANS innovates through its specific implementation: a deep MLP as the
persistent memory module, and the loss gradient as a direct measure of
surprise. This approach transforms real-time learning: each unexpected
token modifies the network weights, exactly like a surprising event imprints
more deeply in our memory.
The results suggest that this precise combination isn’t a luxury. It’s necessary
for effective long-context processing.
Let me show you the science.
Why GPT-4 and Transformers Forget: The Memory Problem
December 31, 2024. A Google Research team publishes a paper with an
intriguing title: “Titans: Learning to Memorize at Test Time”.
The results are remarkable.
Models with 170 to 760 million parameters outperform GPT-4 on BABILong,
a benchmark designed to test reasoning over extremely long contexts. The
paper reports:
“TITANS outperforms all baselines, including extremely large models like GPT-4,
despite having many fewer parameters”.
https://medium.com/p/69b319f1f516 6/66


---
*Page 7*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
This is not a marginal improvement.
The benchmark in question is called BABILong (Kuratov et al., 2024). It
doesn’t test the ability to generate fluent text or solve equations. It tests
something more fundamental: the ability to retrieve precise information
buried in a document of several million tokens, but also to reason over
scattered facts: logical chaining, deduction, induction. The digital equivalent
of searching for a specific sentence in an entire library, then connecting it to
other passages to draw a conclusion.
GPT-4, despite its ~1.8 trillion parameters (Semianalysis 2023 estimate,
unconfirmed by OpenAI), fails miserably. Most large language models do
too. They can generate poems, write code, hold philosophical conversations.
But ask them to retrieve a fact mentioned 500,000 tokens earlier, and they
collapse.
The paradox is clear: the most powerful models in the world are, in a sense,
profoundly amnesic.
The Google researchers (Ali Behrouz, Peilin Zhong, and Vahab Mirrokni)
identified the source of the problem. And their solution draws inspiration
from a system that has worked remarkably well for millions of years: the
human brain.
The Quadratic Attention Problem That Limits GPT-4
Every AI researcher knows this problem. Most pretend it doesn’t exist.
https://medium.com/p/69b319f1f516 7/66


---
*Page 8*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
To understand TITANS, you must first understand why Transformers (the
architecture behind ChatGPT, Claude, Gemini) have a fundamental problem
with long-term memory.
The Impossible Equation
The attention mechanism, the heart of Transformers, works like this: for
each token, the model calculates its relationship with all other tokens in the
context (Vaswani et al., 2017). This is what allows it to understand that “he”
in “John ate an apple. He found it delicious” refers to John.
The problem: this operation has O(n²) complexity.
Note: These values are approximate estimates for a ~7B parameter model, including KV cache and activations.
Actual figures vary depending on specific architecture and numerical precision (FP16, BF16, FP32).
Double the context length, and the cost quadruples. At 2 million tokens,
even the most powerful GPU clusters struggle.
https://medium.com/p/69b319f1f516 8/66


---
*Page 9*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
The quadratic wall — when doubling context means quadrupling computational cost.
This is why most models are limited to 4K-128K tokens of “effective” context.
Some claim to support 1M tokens, but benchmarks reveal a different reality:
popular LLMs effectively use only 10–20% of their context window (Kuratov
et al., 2024).
Classic Solutions (and Their Limits)
The industry has tried several approaches:
https://medium.com/p/69b319f1f516 9/66


---
*Page 10*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Each solution makes a trade-off. Linear attention loses precision. Recurrent
models forget the distant past. RAG adds latency and failure points.
The fundamental question remains unanswered: how do you give a model
truly long memory, without sacrificing either precision or efficiency?
Have you ever hit the context limit in your projects? How did you work around it?
Share your experience in the comments.
But the researchers didn’t just identify the problem. They found a solution in
an unexpected place, and it changes everything we thought about AI
architecture.
World Models: How Dreaming Beats Memorizing in AI
The chief scientist of OpenAI left. The chief AI scientist of Meta left.
Together, they raised over $35 billion. Their…
https://medium.com/p/69b319f1f516 10/66


---
*Page 11*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
medium.com
The Neuroscience Behind TITANS: A Deep Dive into Human
Memory Systems
When computer science hit a wall, neuroscience opened a door.
The solution didn’t come from computer science. It came from six decades
of cognitive psychology research that most AI researchers have never read.
The Atkinson-Shiffrin Model and Its Evolution
https://medium.com/p/69b319f1f516 11/66


---
*Page 12*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
In 1968, Richard Atkinson and Richard Shiffrin proposed the modal model of
memory (Atkinson & Shiffrin, 1968), establishing the foundations for all
subsequent memory research. Their insight: memory is not a monolithic
system but a hierarchy of specialized subsystems.
Nelson Cowan’s 2001 revision, his famous article “The magical number 4 in
short-term memory”, refined this model with rigorous behavioral data, and
his later work integrated modern neuroscientific findings (Cowan, 2010):
The crucial insight TITANS exploits: these systems operate at different
timescales with different update rules.
Working memory uses active maintenance: constant neural firing to keep
information available. Metabolically expensive, capacity-limited.
Long-term memory uses synaptic plasticity: physical changes to connection
weights. Slow to form, but persistent and high-capacity.
The fundamental flaw of Transformers: attention is computationally
analogous to working memory (active comparison of all elements), but we
force it to also serve as long-term storage. This is architecturally incoherent.
https://medium.com/p/69b319f1f516 12/66


---
*Page 13*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Memory as hierarchy — sensory, working, and long-term systems in elegant balance.
Hippocampal Indexing Theory
A deeper problem: how does the brain avoid interference between new and
old memories?
The hippocampus doesn’t store memories directly. It stores indices: pointers
to distributed patterns in the neocortex (Teyler & DiScenna, 1986). During
sleep and rest, the hippocampus “replays” these indices, gradually
transferring knowledge to the neocortex through a process called systems
consolidation (Frankland & Bontempi, 2005).
This solves the stability-plasticity dilemma: how to learn new things without
catastrophically forgetting old ones?
TITANS’ neural memory module mirrors this architecture:
https://medium.com/p/69b319f1f516 13/66


---
*Page 14*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Memory matrix M = the “index” (hippocampal analog)
Surprise-gated updates = selective encoding
Momentum decay = progressive consolidation
The Neurochemistry of Surprise and Memory Consolidation
McGaugh’s work on emotional memory (McGaugh, 2013) reveals a specific
mechanism: during emotionally activating events, the locus coeruleus (a
brainstem nucleus) releases norepinephrine. The basolateral amygdala,
target of this norepinephrine, then modulates hippocampal plasticity and
memory consolidation.
The mathematical signature of this process:
Memory strength ∝ Prediction error × Activation signal
This is exactly TITANS’ surprise mechanism:
Prediction error = loss function gradient
Activation signal = learned gating factor (θ_t)
TITANS’ momentum term captures the temporal persistence of this
modulatory signal:
S_t = η_t · S_{t-1} - θ_t · ∇loss
https://medium.com/p/69b319f1f516 14/66


---
*Page 15*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
The term η_t · S_{t-1} propagates surprise forward in time, allowing salient
events to influence storage of subsequent tokens. This temporal propagation
is computationally analogous to the prolonged noradrenergic modulation
observed in neurobiology.
The hippocampus as master librarian — indexing without storing, directing without holding.
The Synaptic Homeostasis Hypothesis and Adaptive Forgetting
The brain doesn’t just form new memories. It actively forgets. The synaptic
homeostasis hypothesis (SHY) proposed by Tononi & Cirelli (2006) posits
that during sleep, global synaptic downscaling occurs: synaptic strength is
proportionally reduced, preserving only the strongest connections.
The functional purpose: maintaining signal-to-noise ratio. Without
forgetting, old memories would overwhelm new ones.
https://medium.com/p/69b319f1f516 15/66


---
*Page 16*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
TITANS’ forget gate (α_t) implements this principle:
M_t = (1 - α_t) · M_{t-1} + S_t
When α_t → 1, past memory is erased. When α_t → 0, past memory is
preserved. The key insight: α_t is learned and data-dependent, allowing the
model to decide when forgetting is appropriate.
This contrasts with recurrent models like Mamba, where forgetting is a fixed
architectural property, not an adaptive computation.
TITANS’ Three-Memory System: Short-Term, Long-Term, and
Persistent
TITANS introduces a three “hyper-head” architecture (Behrouz et al., 2024),
each corresponding to a distinct type of memory.
The Three-System Office
Imagine an office with three filing systems:
1. Post-its (Core / Attention): Short-term memory
Stuck on the screen, immediately visible
Limited capacity (fixed context window)
Very precise information, direct relationships
https://medium.com/p/69b319f1f516 16/66


---
*Page 17*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Disappear when removed
This is classic Transformer attention. As the paper states: “attention due to its
limited context but accurate dependency modeling performs as a short-term
memory” (Behrouz et al., 2024).
2. The Archivist (Long-Term Memory Module / LMM): Long-term memory
In an adjacent office, with filing cabinets
Virtually unlimited capacity
Knows how to summarize and compress information
Can forget what’s no longer relevant
Continuously learns, even during work
This is TITANS’ major innovation: a “neural long-term memory module that
learns to memorize historical context” (Behrouz et al., 2024). A neural network
that continues learning during inference.
https://medium.com/p/69b319f1f516 17/66


---
*Page 18*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Three systems, one office — the elegant architecture of hybrid memory.
3. The Procedure Manual (Persistent Memory): Persistent memory
A fixed reference book
Doesn’t change based on tasks
Encodes knowledge about the task itself
Independent of input data
These are “learnable but data-independent parameters that encodes the knowledge
about a task” (Behrouz et al., 2024). They encode “how to do” rather than
“what.”
https://medium.com/p/69b319f1f516 18/66


---
*Page 19*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Critical note: An independent reimplementation by Sapienza University of
Rome shows that “persistent tokens alone have negligible or even negative
effects” (Di Nepi et al., 2025). It’s the adaptive neural memory that makes the
difference.
The Formal Architecture
Input x ∈ R^(N x d)
|
v
+----+----+----+
| | | |
v v v v
[Core] [LMM] [Persistent]
| | |
+----+----+
|
v
Output
The fundamental difference from a Transformer: the LMM allows “update
the weights of the neural memory even at test time” (Behrouz et al., 2024). In the
parallelized implementation, this update occurs by segments (chunks)
rather than strictly token by token, enabling efficient GPU processing.
https://medium.com/p/69b319f1f516 19/66


---
*Page 20*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
The Mathematics of Test-Time Learning: A Rigorous Treatment
https://medium.com/p/69b319f1f516 20/66


---
*Page 21*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
https://medium.com/p/69b319f1f516 21/66


---
*Page 22*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
The mathematics beneath — where elegance meets precision in ways that demand attention.
Most explanations skim over the math. We won’t.
Setting the Stage: Learning as Optimization
TITANS’ key innovation is treating inference as online learning. Each new
token triggers an optimization step that updates memory.
Let’s formalize this. Consider a memory module parameterized by M. Given
an input sequence (x₁, x₂, …, xₙ), each token is projected into three distinct
vectors:
Key: kₜ = xₜ · Wₖ
Value: vₜ = xₜ · Wᵥ
Query: qₜ = xₜ · W_q
This key/value/query distinction is fundamental. The memory learns to
associate keys with values, not to reconstruct the input directly.
Associative recall loss (Behrouz et al., 2024, Equation 12):
ℓ(Mₜ₋₁; xₜ) = ‖Mₜ₋₁(kₜ) - vₜ‖₂²
This loss measures the gap between what the memory predicts for a given
key (M(kₜ)) and the target value (vₜ). It’s associative memory: “when I see this
key, what value should I retrieve?”
https://medium.com/p/69b319f1f516 22/66


---
*Page 23*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
The gradient of this loss measures surprise: how much the memory’s
prediction deviates from the expected value.
The Complete Update Equations
TITANS’ memory update follows a modified gradient descent with three key
innovations (Behrouz et al., 2024, Equations 13–15):
1. Surprise signal with momentum:
Sₜ = ηₜ · Sₜ₋₁ - θₜ · ∇ₘℓ(Mₜ₋₁; xₜ)
2. Memory update with forgetting:
Mₜ = (1 - αₜ) · Mₜ₋₁ + Sₜ
3. Output retrieval:
yₜ = Mₜ(qₜ)
where qₜ is the query derived from the input.
Deriving the Connection to Online Learning Theory
Let’s break down why these equations work.
https://medium.com/p/69b319f1f516 23/66


---
*Page 24*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Claim: TITANS implements a convex combination of two learning signals:
1. Immediate correction (standard gradient descent)
2. Accumulated momentum (exponential moving average of past
corrections)
Proof sketch: Let’s expand Sₜ recursively:
Sₜ = -θₜ · ∇ℓₜ + ηₜ · Sₜ₋₁
= -θₜ · ∇ℓₜ + ηₜ · (-θₜ₋₁ · ∇ℓₜ₋₁ + ηₜ₋₁ · Sₜ₋₂)
= -θₜ · ∇ℓₜ - ηₜ·θₜ₋₁ · ∇ℓₜ₋₁ - ηₜ·ηₜ₋₁·θₜ₋₂ · ∇ℓₜ₋₂ - ...
= -Σᵢ₌₀^∞ (∏ⱼ₌ₜ₋ᵢ^ₜ₋₁ ηⱼ) · θₜ₋ᵢ · ∇ℓₜ₋ᵢ
This is an exponentially weighted moving average of past gradients. This
structure connects to the notion of momentum in optimization, introduced
by Polyak (1964) in the context of accelerating gradient method convergence.
The weighting ∏ηⱼ decays geometrically: recent surprises count more than
older ones.
The Stability-Plasticity Trade-off: A Mathematical View
The forget gate αₜ controls the system’s learning rate:
https://medium.com/p/69b319f1f516 24/66


---
*Page 25*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
The effective memory horizon τ is approximately:
τ ≈ 1 / E[αₜ]
If average forgetting αₜ ≈ 0.01, the model “remembers” roughly the last 100
surprise updates.
Why Momentum Matters: The “Post-Event Information” Problem
Consider a sequence: “The CEO announced … [1000 tokens of context] …
that she would resign.”
Without momentum:
“CEO” → some surprise
“announced” → low surprise
“she” → low surprise
“resign” → HIGH surprise
https://medium.com/p/69b319f1f516 25/66


---
*Page 26*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
The problem: “resign” is surprising, but the context (CEO, announced, she) is
critical to understanding why it matters.
With momentum (η > 0):
“resign” triggers high Sₜ
This Sₜ propagates BACKWARD through the momentum buffer
When we store “resign,” we also reinforce storage of “CEO,” “announced,”
etc.
Mathematically: momentum creates temporal credit assignment. Information
relevant to a surprise is stored even if it wasn’t surprising itself.
Theorem 4.1: TITANS Transcends TC⁰
The key theoretical result from the paper (Behrouz et al., 2024, Section 4):
Theorem 4.1: Unlike Transformers, diagonal linear recurrent models, and
DeltaNet — all limited to TC⁰ — TITANS are capable of solving problems beyond
TC⁰.
What this means: TC⁰ is the class of problems solvable by constant-depth
threshold circuits. It includes certain counting and pattern-matching
problems, but excludes certain state-tracking problems, i.e., tasks requiring
maintenance of arbitrary state over unbounded sequences.
TC⁰ limitations have been demonstrated for State-Space Models by Merrill et
al. (2024), who show these models cannot solve basic state-tracking
problems like permutation composition, entity tracking in narratives, or
code evaluation.
https://medium.com/p/69b319f1f516 26/66


---
*Page 27*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Proof intuition:
1. Standard attention computes a fixed function of the input (once trained)
2. TITANS’ memory changes its weights during inference
3. This dynamic weight update is equivalent to running a learning algorithm
4. Learning algorithms can track arbitrary states
5. Therefore, TITANS can solve problems that Transformers cannot
About memory depth: Section 3.1 of the paper separately discusses the
impact of memory module depth (L_M ≥ 1). Experiments show that deeper
memories (L_M ≥ 2) are more effective in practice for maintaining good
perplexity on long sequences, although this condition is not explicitly
mentioned in Theorem 4.1’s statement.
The Outer Product Structure
A crucial detail: TITANS’ memory update uses an outer product structure.
The gradient of the associative loss can be written:
∇ₘℓ = (Mₜ₋₁·kₜ - vₜ) ⊗ kₜᵀ
where ⊗ denotes the outer product. The error is calculated between the
memory output (M·k) and the target value (v), not the input x directly. This is
an important distinction.
https://medium.com/p/69b319f1f516 27/66


---
*Page 28*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
This structure corresponds to the Hebbian update rule (“neurons that fire
together wire together”), and more precisely to the delta rule from neural
network theory (Widrow & Hoff, 1960).
Combined with the forget gate:
Mₜ = (1 - αₜ) · Mₜ₋₁ + θₜ · (Mₜ₋₁·kₜ - vₜ) ⊗ kₜᵀ
This is the delta rule augmented with:
1. Forgetting (the (1-αₜ) term)
2. Momentum (the ηₜ·Sₜ₋₁ term)
Comparison: Learning Rules Across Architectures
Synthesis based on analysis of the TITANS paper and literature on linear recurrent
models:
TITANS is the first to combine all three innovations: delta rule correction,
adaptive forgetting, and temporal momentum.
https://medium.com/p/69b319f1f516 28/66


---
*Page 29*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Transformers Are Dead. Google Killed Them — Then Went Silent
A deep dive into Google’s neural long-term memory architecture
that claims 2M+ token context windows with O(n)…
medium.com
Deep Neural Memory vs Linear Attention: TITANS’ Key
Innovation
The Fundamental Theorem
A key theoretical result from the TITANS paper (Behrouz et al., 2024,
Theorem 4.1):
Theorem 4.1: Unlike Transformers, diagonal linear recurrent models, and
DeltaNet — all limited to TC⁰ (Merrill et al., 2024) — TITANS are capable of
solving problems beyond TC⁰.
Translation: TITANS are strictly more expressive than Transformers on certain
classes of state-tracking problems.
Why Depth Matters
TITANS’ memory can be a multi-layer MLP with L_M >= 1 layers (Section
3.1).
https://medium.com/p/69b319f1f516 29/66


---
*Page 30*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
*Pedagogical analogy. The paper formally establishes that linear memory
corresponds to online linear regression (Section 3.1). Deep network expressivity
follows from the universal approximation theorem for MLPs (Hornik et al., 1989).
Experiments in Section 5.5 show that deep memory ( L_M >= 2):
Maintains better perplexity: “with the increase of memory depth, L_M,
the model can achieve better perplexity over all sequence length”
Is more robust: “deeper memory modules are more robust to the
sequence length when the model has less number of parameters”
The Efficiency/Expressivity Trade-off
Figures 7–8 of the paper illustrate the relationship between depth and
performance:
https://medium.com/p/69b319f1f516 30/66


---
*Page 31*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Note: Mamba serves as an external baseline in the paper’s comparisons, not L_M=1.
The paper concludes:
“Therefore, it is not always efficient to use deeper memory modules, showing a
trade-off between effectiveness and efficiency.” — Section 5.5
The choice of depth thus depends on the application context: latency
constraints, compute budget, and sequence length to process. The paper
doesn’t prescribe a universal optimal value for L_M.
MAC, MAG, MAL: The Three TITANS Architecture Variants
Explained
https://medium.com/p/69b319f1f516 31/66


---
*Page 32*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Three paths to memory integration — context, gate, or layer.
TITANS proposes three ways to integrate long-term memory with attention.
Each variant offers a different trade-off between performance and efficiency
(Behrouz et al., 2024, Section 4).
1. MAC (Memory as Context)
Sequence → Segmentation → Query Memory (ht = M(qt))
→ [Persistent | ht | Segment] → Attention → Memory Update → Output
Principle: Retrieved memory is concatenated to the attention context.
Mechanism (Section 4.1, Eq. 21):
https://medium.com/p/69b319f1f516 32/66


---
*Page 33*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
1. A query qt is generated from the current segment
2. Memory is queried before attention: ht = M*_{t-1}(qt)
3. Attention then operates on the concatenated sequence [persistent | ht |
segment]
4. The attention gradient guides memory update (what’s useful to store)
Advantages:
Memory provides enriched context to attention
Attention helps memory store only what’s useful for future predictions
Best performance on long-context tasks
BABILong Results (Figure 6(b), Section 5.4): Outperforms all baselines
including GPT-4, Llama3.1–70B, and hybrid models on reasoning tasks at 1M
tokens.
2. MAG (Memory as Gating)
┌─→ Memory Branch ──┐
Sequence ───────────┤ ├──→ Gating ──→ Output
└─→ Attention Branch ┘
Principle: Memory and attention are processed in parallel and combined via
a gating mechanism.
Mechanism (Section 4.2, Eq. 24–25):
https://medium.com/p/69b319f1f516 33/66


---
*Page 34*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Both branches (memory and attention) process the input independently
A learned gate decides each branch’s contribution to the final output
Advantages:
Parallelizable architecture
Good general performance
Results (Section 5.9, Table 5): Performance close to MAC on standard
language modeling tasks.
3. MAL (Memory as Layer)
Sequence → Memory Layer → Attention Layer → Output
Principle: Memory is a layer before attention.
Advantages:
Familiar architecture (similar to existing hybrids like Jamba, Zamba)
Faster due to Flash Attention compatibility
Easy to integrate into existing pipelines
Results (Sections 5.8–5.9): Slightly less performant than MAC/MAG on long
context, but better inference throughput.
Comparative Table
https://medium.com/p/69b319f1f516 34/66


---
*Page 35*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Qualitative synthesis based on results from Tables 1–2 and Table 5 (ablation),
Sections 5.1–5.9 (Behrouz et al., 2024):
Legend: + (baseline) to ++++ (best). Ratings are a qualitative interpretation of benchmarks presented in the
paper, not direct metrics.
Training TITANS at Scale: Parallelization and Chunking
The Challenge
The surprise mechanism resembles gradient descent at each token. Naively,
this is sequential and therefore slow.
The Solution: Chunking + Associative Scan
TITANS uses two techniques (Behrouz et al., 2024, Section 3.2):
1. Chunking
Divides the sequence into segments of size b
Computes gradients in parallel within each chunk (Eq. 16–17)
Propagates states between chunks
https://medium.com/p/69b319f1f516 35/66


---
*Page 36*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
2. Parallel Associative Scan
The momentum S_t = eta_t * S_{t-1} - theta_t * u_t is a linear
recurrence (Eq. 18)
It can be computed in O(log n) with a parallel scan (Blelloch, 1990)
Result: O(n) complexity instead of O(n²), with effective GPU parallelization.
Compared Throughput
According to Figure 9 and Section 5.8 of the paper (Behrouz et al., 2024):
TITANS’ memory module is slightly slower than Mamba2 and Gated
DeltaNet, primarily due to: (1) deep memory with a more expressive
transition process, and (2) Mamba2’s highly optimized kernel
implementation.
In contrast, TITANS MAL outperforms Transformer++ in throughput thanks
to the combined use of sliding window attention and Flash Attention.
USC Just Built Artificial Neurons That Could Make GPT-5 Run on
20 Watts
https://medium.com/p/69b319f1f516 36/66


---
*Page 37*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
After 70 years of von Neumann architecture, researchers create
neurons that think like nature — using silver ions, not…
medium.com
Empirical Results: A Summary
I wrote a detailed benchmark analysis in a previous article. Here I’ll
summarize the key results and focus on what the numbers mean rather than
listing them exhaustively.
The Main Result
On BABILong, a benchmark presented at NeurIPS 2024 (Datasets and
Benchmarks Track) testing 20 different reasoning tasks on extremely long
contexts (fact chains, induction, deduction, counting, list manipulation):
What Figure 6 of the TITANS paper shows:
The comparative curves reveal a major qualitative gap. As context length
increases toward 10⁶-10⁷ tokens:
TITANS (MAC) maintains stable accuracy around ~70%
GPT-4, Llama 3.1, and Mamba all drop below 40%
Note: These values are visual estimates read from Figure 6b graphs. The paper
doesn’t report precise numbers in a table, but the gap between curves is
unambiguous.
https://medium.com/p/69b319f1f516 37/66


---
*Page 38*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
The order of magnitude is striking: a model of a few hundred million
parameters (340M-760M depending on configurations tested) outperforms
models 300 to 500 times larger in active parameters. This isn’t an incremental
improvement; it’s a qualitative change in how information is retained over
long sequences.
Why This Matters (Beyond Bragging Rights)
The BABILong result isn’t just about retrieval. It demonstrates that test-time
learning fundamentally changes what’s achievable.
Standard architectures have a fixed computational budget per token. Once
trained, they can only apply learned functions, not learn new ones.
TITANS breaks this constraint. Each token can modify memory. Over a
million tokens, that’s a million micro-learning steps, effectively training a
small model during inference.
The implication: context length stops being a resource constraint and
becomes a learning opportunity.
Generalization Beyond Language
TITANS’ memory mechanism isn’t language-specific. Results on DNA
modeling (Section 5.7) and time series forecasting (Section 5.6) show
competitive performance, suggesting the core insight (surprise-gated
adaptive memory) generalizes across domains.
Important nuance: the performance gap on these tasks is less spectacular than on
long-context. TITANS is competitive there, not dominant.
https://medium.com/p/69b319f1f516 38/66


---
*Page 39*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
TITANS Reproducibility Issues: What “Titans Revisited” Found
The honest mirror — when revolutionary claims meet reproducibility questions.
I could have ended this article at the previous section. Most Medium articles
would have. But that would be dishonest.
In October 2025, a team from Sapienza University of Rome published “Titans
Revisited: A Lightweight Reimplementation and Critical Analysis” (Di Nepi et
al., 2025). Their goal: reimplement TITANS without official code and verify
the results.
The Reproducibility Problem
https://medium.com/p/69b319f1f516 39/66


---
*Page 40*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Google didn’t release TITANS’ code. The original paper leaves several
ambiguities:
Reimplementation Results
The Sapienza team tests TITANS on three tasks:
1. Masked Language Modeling (CC-News, 700K articles)
https://medium.com/p/69b319f1f516 40/66


---
*Page 41*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Source: Table 2, Di Nepi et al., 2025
Key finding: Persistent tokens alone have negligible or even negative effect.
It’s the neural memory that makes the difference (+0.003 in F1).
2. Recommendation (MovieLens 1M)
Source: Table 1, Di Nepi et al., 2025
https://medium.com/p/69b319f1f516 41/66


---
*Page 42*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Key finding: TITANS does NOT beat BERT4Rec on this task. But memory
improves MRR from 0.34 to 0.44 (+0.10).
3. Time Series Forecasting (ETTh1)
Source: Table 3, Di Nepi et al., 2025
Key finding: Memory alone (without attention) beats iTransformer and
LSTM. But results don’t reach those of the original paper.
The Chunking Problem
The analysis reveals that chunking is the main source of degradation:
https://medium.com/p/69b319f1f516 42/66


---
*Page 43*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Source: Figure 1b, Di Nepi et al., 2025
The smaller the chunks, the worse the performance. The problem: larger
chunks = higher computational cost (effective sequence for attention is 2x
chunk size + persistent tokens).
Test-Time Learning: The Unfulfilled Promise?
The Sapienza team tests the ability to truly learn during inference:
Setup: 30% train, 10% val, 60% test
Backbone frozen, only memory is updated
Result: after 50 epochs, variations are at the 4th decimal
Beyond 50 epochs, performance slowly degrades
https://medium.com/p/69b319f1f516 43/66


---
*Page 44*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Researchers’ conclusion: “Memory updates alone are insufficient for
significant test-time learning when the backbone is frozen.”
Learning during inference seems to require coordinated adaptation between
memory and backbone, not just memory alone.
Do these reproducibility issues invalidate the entire paper, or does the core idea
remain valuable? I’d love to hear your thoughts in the comments.
Transformers Are Dead. Google Killed Them — Then Went Silent
A deep dive into Google’s neural long-term memory architecture
that claims 2M+ token context windows with O(n)…
medium.com
What TITANS Can’t Do: Honest Limitations of Google’s Memory
Model
What TITANS Doesn’t Solve
1. Training cost
Deep memory slows training: throughput decreases with memory depth
(Section 5.8, Figure 8)
Kernels aren’t yet as optimized as Mamba2 or Flash Attention
2. Chunking = degradation (Di Nepi et al., 2025)
https://medium.com/p/69b319f1f516 44/66


---
*Page 45*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
The smaller the chunks, the worse the performance
Larger chunks = higher computational cost
Chunking is identified as the main source of degradation
3. Persistent tokens useless alone (Di Nepi et al., 2025)
Persistent tokens without neural memory contribute nothing
It’s adaptive learning that makes the difference
4. No large-scale pretraining (yet)
Experiments are at 170M-760M parameters
No “TITANS-7B” or “TITANS-70B” version available
Behavior at massive LLM scale unknown
5. Limited test-time learning (Di Nepi et al., 2025)
Memory updates alone are insufficient if the backbone is frozen
Probably requires coordinated memory + backbone adaptation
6. No official code
Google hasn’t released an implementation
Reimplementations reveal ambiguities in the paper
Open Questions
https://medium.com/p/69b319f1f516 45/66


---
*Page 46*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
How TITANS Connects to Linear Attention and State-Space
Models
TITANS in the Architecture Landscape
The TITANS paper (Behrouz et al., 2024, Section 2.1) situates the architecture
relative to two parallel research directions:
Direction 1: Improving the forgetting mechanism
GLA, LRU, Mamba2, Gated DeltaNet: add forget gates to manage memory
capacity
Direction 2: Improving the write operation
DeltaNet, Gated DeltaNet: use the delta rule (removal before addition)
https://medium.com/p/69b319f1f516 46/66


---
*Page 47*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
TITANS: An orthogonal approach
Uses a deep neural memory (MLP) instead of a linear matrix
Learns via online gradient descent with a surprise metric
Combines adaptive forgetting + momentum, but the fundamental
architecture differs
Comparison with Related Work
Compared to TTT (Test-Time Training):
“Compared to TTT, TITANS’ Neural Memory can better handle the memory
capacity by using momentum and also the forgetting mechanism (i.e., weight
decay).” — Section 2.1
Compared to Fast Weight Programmers (Schmidhuber, 1992):
TITANS draws inspiration from the concept of “fast weights” vs. “slow
weights”
The difference: gradient-based learning + adaptive gating + deep memory
The Fundamental Mechanisms
Note: The following diagram is a pedagogical synthesis, not a hierarchy presented
in the paper.
https://medium.com/p/69b319f1f516 47/66


---
*Page 48*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
The Cognitive Science Connection: What TITANS Reveals About
Intelligence
This is the part most AI coverage misses. TITANS isn’t just an engineering
improvement. It’s a theoretical statement about what memory-augmented
computation can achieve.
The Fast-Slow Learning Dichotomy
Cognitive scientists distinguish two learning systems (Kahneman, 2011):
TITANS maps directly to this:
Attention (Core) = System 1: fast, parallel, but capacity-limited
https://medium.com/p/69b319f1f516 48/66


---
*Page 49*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Neural Memory (LMM) = System 2: slower (requires gradient
computation), but adaptive
Complementary Learning Systems Theory
In neuroscience, the hippocampus and neocortex implement complementary
learning systems (McClelland et al., 1995):
Hippocampus: Rapid encoding of specific episodes
Neocortex: Slow extraction of statistical regularities
The hippocampus acts as a “buffer” that rapidly stores new experiences,
then progressively transfers structured knowledge to the neocortex through
replay during sleep.
TITANS’ architecture reflects this:
Memory module: Rapid adaptation to new tokens (hippocampal analog)
Backbone: Frozen during inference, encodes general knowledge
(neocortical analog)
The limitation identified by Di Nepi et al., 2025, that memory alone can’t
learn effectively when the backbone is frozen, is exactly what cognitive
science predicts. True learning requires coordination between fast and slow
systems.
The Binding Problem and Episodic Memory
How does the brain bind disparate features (color, shape, location) into
coherent memories?
https://medium.com/p/69b319f1f516 49/66


---
*Page 50*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
The hippocampus creates conjunctive representations: unique units that
encode feature combinations (O’Reilly & Rudy, 2001). This enables pattern
completion: given partial cues, the full memory can be retrieved.
TITANS’ memory matrix M serves a similar function. The outer product
update:
M += (value) ⊗ (key)ᵀ
creates conjunctive associations between input patterns. Given a query
similar to a stored key, memory retrieves the associated value, a form of
pattern completion.
What This Means for AGI
Here’s the speculative part.
Current LLMs are fantastic pattern matchers but poor learners. They can
retrieve immense knowledge but can’t update it.
TITANS suggests a path: architectures that continuously learn at multiple
timescales.
The brain doesn’t stop learning when you start a new task. Every experience
modifies synaptic weights, at rates ranging from milliseconds (short-term
plasticity) to years (slow consolidation).
Future AI systems will probably need this property. Not just to process long
contexts, but to adapt in real-time, learning from user feedback,
https://medium.com/p/69b319f1f516 50/66


---
*Page 51*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
incorporating new information, developing true understanding rather than
sophisticated retrieval.
TITANS is a small step in this direction. Memory updates are shallow.
Timescales are limited. But the principle is correct.
Why Yann LeCun Bet $3.5 Billion on World Models Over LLMs
After 12 years as Meta’s Chief AI Scientist, the Turing Award winner
walked away to prove Silicon Valley is betting on…
ai.gopubby.com
My Verdict: Will TITANS Replace Transformers?
What I Think
Reminder: this is my reading of the paper. I could be wrong.
TITANS represents the best current lead for solving the memory problem in
LLMs. Not the final solution, but the best lead.
Neuroscience-inspired neural memory isn’t a gimmick. It’s probably the
direction all large models will take in 2–3 years. The surprise mechanism for
filtering relevant information is too elegant to ignore.
But, and this is crucial, the current architecture isn’t ready for production at
scale. Chunking breaks performance. Test-time learning remains limited.
Integration with existing stacks isn’t trivial.
https://medium.com/p/69b319f1f516 51/66


---
*Page 52*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
What Will Happen
Short term (6–12 months): Google will probably integrate a version of
TITANS into Gemini. Not the full architecture, but the adaptive memory
module, hybrid with classic attention. We’ll see gains on long-context tasks
without the chunking drawbacks.
Medium term (12–24 months): Hybrid architectures will become
widespread. Attention for immediate context, neural memory for extended
context. Mamba, TITANS, and their descendants will converge toward
something new.
Long term (2–3 years): The pure Transformer, as we know it, will become a
niche architecture. Not dead, just niche. Like RNNs today: still useful in
some cases, but no longer the dominant paradigm.
https://medium.com/p/69b319f1f516 52/66


---
*Page 53*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
The metamorphosis ahead — when Transformers evolve into something beautifully new.
My Predictions (With Dates)
I’m putting my reputation on the line:
Q1 2026: At least one major lab (OpenAI, Anthropic, or Meta) will publish a
paper citing TITANS and proposing a “memory-augmented” architecture.
Mid-2026: The first open-source implementation will drop. Probably from
EleutherAI or Together AI. It won’t match Google’s results.
End of 2026: “Memory-augmented Transformer” will be the new “mixture of
experts.” Everyone will claim to have one.
2027–2028: The pure attention Transformer will be the new LSTM: taught in
courses as “historical,” used only in niche applications.
Bookmark this article. We’ll see who was right.
The Real Question
We talk a lot about long context. Infinite memory. Models that “understand”
entire documents.
But here’s what we still don’t know: does more memory mean better
reasoning?
Humans don’t need to remember everything to reason. We abstract. We
strategically forget. We compress experience into principles.
https://medium.com/p/69b319f1f516 53/66


---
*Page 54*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
TITANS and its successors will give us models with virtually unlimited
memory. The question is: what do we do with it? A glorified search engine?
Or something that resembles understanding?
Current benchmarks don’t measure this. And until we know how to measure
it, we won’t know if we’re truly making progress.
Will test-time learning become standard, or is this a dead end? Share your
prediction in the comments. I’m curious to see where the community stands.
What’s certain: the Transformer-only paradigm is cracking. TITANS is a symptom
of this transition, not its final destination. The race is no longer about who has the
most parameters. It’s about who best knows how to forget.
A Final Word
If you’ve made it this far, you’re part of the top 1% of readers who actually
care about understanding AI rather than just using it.
I have a request: if you found this useful, don’t just clap. Share it with one
person who you think would appreciate the depth.
The algorithm rewards superficial content. The only way for deep technical
writing to survive is for readers to actively distribute it.
https://medium.com/p/69b319f1f516 54/66


---
*Page 55*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
And if you disagree with my analysis, especially on the “Transformers are
the new RNNs” take, tell me in the comments. I’d rather be wrong and learn
than be right and stay ignorant.
Frequently Asked Questions About TITANS
What is Google TITANS?
TITANS (Learning to Memorize at Test Time) is a neural architecture
developed by Google Research that implements test-time learning with a
surprise-gated memory system inspired by human cognitive science. Unlike
standard Transformers, TITANS uses three memory systems: working
memory (attention), long-term memory (neural memory module), and
persistent memory (fixed parameters).
How does TITANS compare to GPT-4?
On the BABILong benchmark, TITANS models with 170M-760M parameters
outperform GPT-4 on long-context reasoning tasks, despite having
approximately 1000x fewer parameters. While GPT-4 drops below 40%
accuracy at 1M+ tokens, TITANS maintains around 70% accuracy.
Is TITANS a transformer alternative?
Yes. TITANS combines attention (short-term memory) with a neural memory
module (long-term memory), offering a hybrid approach that addresses the
quadratic attention bottleneck of pure Transformers. The architecture
transcends TC⁰ complexity limits that constrain standard Transformers.
When will TITANS be available?
https://medium.com/p/69b319f1f516 55/66


---
*Page 56*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Google has not released the official code as of December 2025. Independent
reimplementations exist but show performance gaps compared to the
original paper. Integration into Gemini is expected within 6–12 months
based on Google’s typical research-to-product cycle.
✦ DELANOE PIRARD ✦
Artificial Intelligence Researcher & Engineer
🌐
delanoe-pirard.com
💻
github.com/Aedelon
💼
linkedin.com/in/delanoe-pirard
𝕏 x.com/0xAedelon
👉
This article did help you ? Clap + Follow for the next one.
Sources
Main Paper
Behrouz, A., Zhong, P., & Mirrokni, V. (2024). “Titans: Learning to
Memorize at Test Time.” arXiv:2501.00663.
https://arxiv.org/abs/2501.00663
Critical Analysis
Di Nepi, G., Siciliano, F., & Silvestri, F. (2025). “Titans Revisited: A
Lightweight Reimplementation and Critical Analysis of a Test-Time
https://medium.com/p/69b319f1f516 56/66


---
*Page 57*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Memory Model.” arXiv:2510.09551. https://arxiv.org/abs/2510.09551
Cognitive Science and Neuroscience
Atkinson, R.C. & Shiffrin, R.M. (1968). “Human memory: A proposed
system and its control processes.” Psychology of Learning and
Motivation, 2, 89–195.
https://www.sciencedirect.com/science/article/pii/S0079742108604223
Davis, R.L. & Zhong, Y. (2021). “The Biology of Forgetting — A
Perspective.” Nature Reviews Neuroscience.
https://www.nature.com/articles/s41583-021-00548-3
Cowan, N. (2001). “The magical number 4 in short-term memory: A
reconsideration of mental storage capacity.” Behavioral and Brain
Sciences, 24(1), 87–185. https://pubmed.ncbi.nlm.nih.gov/11515286/
Cowan, N. (2010). “The Magical Mystery Four: How is Working Memory
Capacity Limited, and Why?” Current Directions in Psychological
Science, 19(1), 51–57.
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2864034/
Teyler, T.J. & DiScenna, P. (1986). “The hippocampal memory indexing
theory.” Behavioral Neuroscience, 100(2), 147–154.
https://pubmed.ncbi.nlm.nih.gov/3513286/
Frankland, P.W. & Bontempi, B. (2005). “The organization of recent and
remote memories.” Nature Reviews Neuroscience, 6, 119–130.
https://www.nature.com/articles/nrn1607
McGaugh, J.L. (2013). “Making lasting memories: Remembering the
significant.” PNAS, 110(Supplement 2), 10402–10407.
https://pmc.ncbi.nlm.nih.gov/articles/PMC3690616/
https://medium.com/p/69b319f1f516 57/66


---
*Page 58*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Strange, B.A., et al. (2003). “An emotion-induced retrograde amnesia in
humans is amygdala- and β-adrenergic-dependent.” PNAS, 100(23), 13626–
13631. https://www.nature.com/articles/nature01477
Tononi, G. & Cirelli, C. (2006). “Sleep function and synaptic
homeostasis.” Sleep Medicine Reviews, 10(1), 49–62.
https://pubmed.ncbi.nlm.nih.gov/16469429/
McClelland, J.L., McNaughton, B.L., & O’Reilly, R.C. (1995). “Why there
are complementary learning systems in the hippocampus and
neocortex.” Psychological Review, 102(3), 419–457.
https://psycnet.apa.org/record/1995-42327-001
O’Reilly, R.C. & Rudy, J.W. (2001). “Conjunctive representations in
learning and memory: Principles of cortical and hippocampal function.”
Psychological Review, 108(2), 311–345.
https://pubmed.ncbi.nlm.nih.gov/11438712/
Rouhani, N., et al. (2023). “Reward prediction errors create event
boundaries in memory.” Nature Human Behaviour.
https://www.nature.com/articles/s41562-023-01799-z
Anderson, M.C., et al. (2021). “Active forgetting: Adaptation of memory by
prefrontal control.” Annual Review of Psychology. PMC8467325.
https://pmc.ncbi.nlm.nih.gov/articles/PMC8467325/
Learning Theory and Optimization
Widrow, B. & Hoff, M.E. (1960). “Adaptive switching circuits.” IRE
WESCON Convention Record, Part 4, 96–104.
https://isl.stanford.edu/~widrow/papers/c1960adaptiveswitching.pdf
Polyak, B.T. (1964). “Some methods of speeding up the convergence of
iteration methods.” USSR Computational Mathematics and Mathematical
https://medium.com/p/69b319f1f516 58/66


---
*Page 59*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Physics, 4(5), 1–17. DOI: 10.1016/0041–5553(64)90137–5.
https://www.sciencedirect.com/science/article/abs/pii/0041555364901375
Hochreiter, S. & Schmidhuber, J. (1997). “Long Short-Term Memory.”
Neural Computation, 9(8), 1735–1780.
https://www.bioinf.jku.at/publications/older/2604.pdf
Expressivity and Complexity
Merrill, W., Sabharwal, A., & Smith, N.A. (2024). “The Illusion of State in
State-Space Models.” ICML 2024. https://openreview.net/forum?
id=QZgo9JZpLq
Hornik, K., Stinchcombe, M., & White, H. (1989). “Multilayer feedforward
networks are universal approximators.” Neural Networks, 2(5), 359–366.
DOI: 10.1016/0893–6080(89)90020–8. https://doi.org/10.1016/0893-
6080(89)90020-8
Attention and Transformers
Vaswani, A., et al. (2017). “Attention Is All You Need.” NeurIPS 2017.
https://arxiv.org/abs/1706.03762
Beltagy, I., Peters, M.E. & Cohan, A. (2020). “Longformer: The Long-
Document Transformer.” https://arxiv.org/abs/2004.05150
Zaheer, M., et al. (2020). “Big Bird: Transformers for Longer Sequences.”
NeurIPS 2020. https://arxiv.org/abs/2007.14062
Katharopoulos, A., et al. (2020). “Transformers are RNNs: Fast
Autoregressive Transformers with Linear Attention.” ICML 2020.
https://proceedings.mlr.press/v119/katharopoulos20a.html
Dao, T., et al. (2022). “FlashAttention: Fast and Memory-Efficient Exact
Attention with IO-Awareness.” NeurIPS 2022.
https://medium.com/p/69b319f1f516 59/66


---
*Page 60*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
https://arxiv.org/abs/2205.14135
Peng, B., et al. (2023). “RWKV: Reinventing RNNs for the Transformer
Era.” EMNLP 2023. https://arxiv.org/abs/2305.13048
Benchmarks
Kuratov, Y., et al. (2024). “BABILong: Testing the Limits of LLMs with
Long Context Reasoning-in-a-Haystack.” NeurIPS 2024.
https://arxiv.org/abs/2406.10149
Related Architectures
Carta, S., et al. (2023). “Memoria: Resolving Catastrophic Forgetting in
Deep Learning.” arXiv:2310.03052. https://arxiv.org/abs/2310.03052
Yang, S., Kautz, J., & Hatamizadeh, A. (2024). “Gated Delta Networks:
Improving Mamba2 with Delta Rule.” ICLR 2025.
https://arxiv.org/abs/2412.06464
Sun, Y., et al. (2024). “Learning to (Learn at Test Time): RNNs with
Expressive Hidden States.” arXiv:2407.04620.
https://arxiv.org/abs/2407.04620
Schmidhuber, J. (1992). “Learning to Control Fast-Weight Memories.”
Neural Computation, 4(1), 131–139.
https://direct.mit.edu/neco/article/4/1/131/5620
Gu, A. & Dao, T. (2023). “Mamba: Linear-time Sequence Modeling with
Selective State Spaces.” arXiv:2312.00752.
Parallelization
Blelloch, G.E. (1990). “Prefix Sums and Their Applications.” Technical
Report CMU-CS-90–190, Carnegie Mellon University.
https://www.cs.cmu.edu/~scandal/papers/CMU-CS-90-190.html
https://medium.com/p/69b319f1f516 60/66


---
*Page 61*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Other Sources
Semianalysis (2023). “GPT-4 Architecture, Infrastructure, Training
Dataset, Costs, Vision, MoE.” https://www.semianalysis.com/p/gpt-4-
architecture-infrastructure
Kahneman, D. (2011). “Thinking, Fast and Slow.” Farrar, Straus and
Giroux. https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow
Related Article
Pirard, D. (2025). “Transformers Are Dead. Google Killed Them — Then
Went Silent.” Medium, December 17, 2025.
https://medium.com/@aedelon/transformers-are-dead-google-killed-
them-then-went-silent-a379ed35409b
Artificial Intelligence Machine Learning Google Deep Learning Transformers
Published in AI Advances
Following
63K followers · Last published 13 hours ago
Democratizing access to artificial intelligence
Written by Delanoe Pirard
Follow
6.3K followers · 61 following
AI Researcher, AI Engineer. Building autonomous systems. Reinforcement
Learning, Computer Vision. Brussels 🇧🇪 https://www.delanoe-pirard.com/
https://medium.com/p/69b319f1f516 61/66


---
*Page 62*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Responses (18)
Rae Steele
What are your thoughts?
Stephen Gettel
Jan 2
What I appreciated most about this article is that it treats memory as an architectural responsibility rather than
a scaling problem. The benchmarks are interesting, but the deeper contribution is the clarity it brings to why
forcing attention to… more
12 1 reply Reply
Rob Ford
Jan 11
Wow, what an incredible article. Well done and thank you for all the time you put into it for our benefit.
3 Reply
Alex Amaya
Jan 3
Amazing and well-documented article, thank you Delanoe. It’s fascinating to see neuroscience-inspired ideas
being taken to the next level, this time with empirical validation and an honest discussion of limitations.
2 Reply
See all responses
https://medium.com/p/69b319f1f516 62/66


---
*Page 63*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
More from Delanoe Pirard and AI Advances
InAI Advancesby Delanoe Pirard InAI Advancesby Jose Crespo, PhD
A Discord Community Beat Meta’s Everyone’s Wrong About AI
LLaMA. The Secret? An… Programming — Except Maybe…
RWKV-7 scores 72.8% vs LLaMA’s 69.7% with The lens that makes AI coding bugs
3x fewer tokens. It runs in constant memory.… impossible, and no one taught you.
Feb 22 572 7 Jan 28 922 24
https://medium.com/p/69b319f1f516 63/66


---
*Page 64*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
InAI Advancesby Harish K Delanoe Pirard
I Tested 5 OCR Models on 6 Real- YOLO Is Dead. Meet RF-DETR, the
World Datasets — Here’s Which… Model That Just Crushed 10 Years…
There’s no single “best” OCR engine. RF-DETR Shatters the 60 AP Barrier — And
Tesseract is fastest, EasyOCR dominates… YOLO’s Decade-Long Reign With It
Feb 15 335 8 Dec 7, 2025 1K 21
See all from Delanoe Pirard See all from AI Advances
Recommended from Medium
https://medium.com/p/69b319f1f516 64/66


---
*Page 65*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
InActivated Thinker by Shane Collins InTowards Deep Learning by Sumit Pandey
Andrew Ng’s Brutal Reality Check: Mojo: The New Programming
If Your AI Strategy Is Just ‘Saving… Language That Could Reshape AI…
Why “efficiency” is a trap — and the “100x Mojo is 68,000x faster than Python. Built by
Rule” you need to survive the 2026 AI shift Swift’s creator, it could eliminate AI’s two-…
Feb 6 1.2K 37 Jan 5 259 12
Ignacio de Gregorio InJavarevisited by Harry
Anthropic Reveals China’s Dirty JSON Is Dying in the AI Era
Little AI Secret.
LMs prefer TOON and what token cost is
…While ousting themselves as huge forcing us to rethink data formats
hypocrites
Feb 24 1.99K 44 Jan 19 350 25
Can Artuc InData Science Collecti… by Tanmay Deshpan…
Linux 7.0: Google’s $1M Bug Finally I Analyzed 163K Lines of Kuzu’s
Fixed Codebase. Here’s Why Apple…
Google paid $1M in iouring bounties and How a 10-person startup built the graph
disabled it on Chrome OS. A maintainer calle… engine Apple’s on-device AI strategy was…
https://medium.com/p/69b319f1f516 65/66


---
*Page 66*


3/13/26, 1:45 AM Google's TITANS Explained: The Neuroscience of AI Memory | AI Advances
Feb 21 2.3K 18 Feb 14 427 9
See more recommendations
https://medium.com/p/69b319f1f516 66/66