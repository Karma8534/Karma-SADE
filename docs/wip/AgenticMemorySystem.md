# AgenticMemorySystem

*Converted from: AgenticMemorySystem.PDF*



---
*Page 1*


This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
License: CC BY 4.0
arXiv:2601.01885v1 [cs.CL] 05 Jan 2026
Agentic Memory: Learning Unified Long-
Term and Short-Term Memory Management
for Large Language Model Agents
Yi Yu1,2, Liuyi Yao1,†, Yuexiang Xie1, Qingquan Tan2, Jiaqi Feng2,
Yaliang Li1, and Libing Wu2,†
1Alibaba Group,
2School of Cyber Science and Engineering, Wuhan University
{yui1212,tanqingquan,jiaqiFeng,wu}@whu.edu.cn
{yly287738,yuexiang.xyx,yaliang.li}@alibaba-inc.com
†Corresponding authors
Abstract
Large language model (LLM) agents face fundamental limitations in long-horizon reasoning due to fi-
nite context windows, making effective memory management critical. Existing methods typically han-
dle long-term memory (LTM) and short-term memory (STM) as separate components, relying on
heuristics or auxiliary controllers, which limits adaptability and end-to-end optimization. In this paper,
we propose Agentic Memory (AgeMem), a unified framework that integrates LTM and STM manage-
ment directly into the agent’s policy. AgeMem exposes memory operations as tool-based actions, en-
abling the LLM agent to autonomously decide what and when to store, retrieve, update, summarize,
or discard information. To train such unified behaviors, we propose a three-stage progressive rein-
forcement learning strategy and design a step-wise GRPO to address sparse and discontinuous re-
wards induced by memory operations. Experiments on five long-horizon benchmarks demonstrate
that AgeMem consistently outperforms strong memory-augmented baselines across multiple LLM
backbones, achieving improved task performance, higher-quality long-term memory, and more effi-
cient context usage.


---
*Page 2*


Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large
This is experimental HTML to imLparonveg aucacegsesi bMilitoy.del WAgheynts Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
Yi Yu1,2, Liuyi Yao1,†, Yuexiang Xie1, Qingquan Tan2, Jiaqi
Feng2,
Yaliang Li1, and Libing Wu2,†
1Alibaba Group,
2School of Cyber Science and Engineering, Wuhan University
{yui1212,tanqingquan,jiaqiFeng,wu}@whu.edu.cn
{yly287738,yuexiang.xyx,yaliang.li}@alibaba-
inc.com
†Corresponding authors
1 Introduction
In long-horizon agentic tasks involving multi-step reasoning and complex workflows (
chang2024agentboard), the effectiveness of large language model (LLM) agents is fundamentally con-
strained by the information they can attend to at any given time, which we collectively refer to as the
agent’s memory (xiong2025memory; goodyear2025effect). Memory typically falls into two categories:
long-term memory (LTM), which persistently stores user- or task-specific knowledge (
zhong2024memorybank; jiang2024long), and short-term memory (STM), which comprises the infor-
mation contained in the current input context (wu2025human; gao2025efficient). High-quality LTM
supports efficient retrieval of accumulated knowledge, while effective STM management reduces re-
dundancy and preserves salient context. Together, they mitigate the limitations of finite context win-
dows, making their joint management crucial for improving agent performance in complex reasoning
settings.


---
*Page 3*


This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
Figure 1:Comparison between independent and unified memory management frameworks. (Left)
Traditional framework with static STM and trigger-based LTM. (Middle) Independent framework with
an additional Memory Manager controlling LTM in an agent-based manner, while STM remains static.
(Right) The proposed AgeMem framework, where LTM and STM are jointly and intelligently managed
via explicit tool-based operations.
However, existing research has predominantly treated LTM and STM as independent components.
STM is commonly enhanced through retrieval-augmented generation (RAG) (pan2025memory), such
as in MainRAG (chang2025main) and ReSum (wu2025resum), which expand usable context via exter-
nal retrieval or periodic summarization. Although effective in some tasks, these methods rely heavily
on predefined schedules or heuristic rules, potentially resulting in overlooked infrequent but critical
details as well as unnecessary noise (ma2025should; dong2025survey). In contrast, LTM manage-
ment has progressed along separate lines, typically categorized into trigger-based (kang2025memory;
wang2025mirix; wang2025inducing; chhikara2025mem0) and agent-based (yan2025memory;
hu2025evaluating; xu2025mem) paradigms. The former executes fixed memory operations at prede-
fined moments, whereas the latter incorporates a specialized memory manager to determine what
and how to store. Despite offering more flexibility, most approaches still depend on handcrafted rules
or auxiliary expert models, limiting adaptability and increasing system complexity (xiong2025memory
).
As a consequence, LTM and STM are typically treated as separate and loosely coupled modules. As il-
lustrated in Figure 1, existing architectures generally follow two patterns: (a) static STM with trigger-
based LTM, or (b) static STM with agent-based LTM. In both settings, the two memory systems are op-


---
*Page 4*


timized independently and later combined in an ad hoc way, leading to fragmented memory construc-
tion and subopTthiims isa le xppeerrifmoernmtaal HnTcMeL i tno ilmopnrgov-eh aocrciezsosinbi lritey.asoWnihnyg tasksR.e Tphourst, uBniafcykin tgo the Dmoawnnalgoeamdent of
We invite you to report rendering errors. Learn more
LTM and STM remains a necessary yet largely unexploreHd TcMhaLll?engIses.ue Abstract PDF
about this project and help improve conversions.
Nevertheless, achieving unified memory management poses three fundamental challenges. (C1)
Functional heterogeneity coordination: LTM and STM serve distinct yet complementary purposes:
LTM determines what to store, update, or discard, while STM governs what to retrieve, summarize, or
remove from the active context (zhang2025survey). The challenge lies in designing a unified mecha-
nism that orchestrates their interplay synergistically. (C2) Training paradigm mismatch: Existing re-
inforcement learning (RL) frameworks adopt markedly different training strategies for the two mem-
ory types (ma2024coevolving). LTM-focused training often leverages session-level information avail-
able prior to interaction, whereas STM training typically injects distractors to simulate long-horizon
contexts (sun2024llm). Moreover, standard RL assumes continuous trajectories with stable rewards,
which conflicts with the inherently fragmented and discontinuous experiences produced by memory
operations (wu2025resum), making end-to-end optimization particularly challenging. (C3) Practical
deployment constraints: Many agent systems rely on an auxiliary expert LLM for memory control,
significantly increasing inference cost and training complexity. How to integrate unified memory man-
agement directly into an agent without dependence on external expert models remains an open
problem.
To address these challenges, we propose Agentic Memory (AgeMem), a unified framework that jointly
manages LTM and STM, illustrated in Figure 1 (right). Unlike prior designs that treat memory as an ex-
ternal component, AgeMem integrates both memory types directly into the agent’s decision-making
process. Through a unified tool-based interface, the LLM autonomously invokes and executes mem-
ory operations for both LTM and STM. Furthermore, we design a three-stage progressive RL strategy:
the model first acquires LTM storage capabilities, then learns STM context management, and finally
coordinates both forms of memory under full task settings. To address the fragmented experience is-
sue across training stages, we design a step-wise Group Relative Policy Optimization (GRPO) (
shao2024deepseekmath), which transforms cross-stage dependencies into learnable signals, thereby
alleviating the challenges posed by sparse and discontinuous rewards in RL. We evaluate AgeMem on
five long-context, reasoning-intensive benchmarks. Comprehensive results show that AgeMem con-
sistently outperforms strong baselines, validating the effectiveness of unified memory management.
Our main contributions are as follows:
We propose Agentic Memory (AgeMem), a unified agentic memory framework that enables
LLM-based agents to autonomously decide when, what, and how to manage both long-term
and short-term memory.


---
*Page 5*


We develop a three-stage progressive RL strategy equipped with a step-wise GRPO mecha-
nism, facilitatTihnigs ise ffexepcertiimveen etanl HdT-MtoL- teon imdp lreovaer ancicnegss oibfi liutyn. ifieWd hmyemorRy empaonrtageBmaecnk tt obehaDvioowrsn.load
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
We conduct comprehensive evaluations across multiple models and long-horizon benchmarks,
demonstrating the robustness and effectiveness of AgeMem in complex agentic tasks.
2 Background and Related Work
Long-term memory (LTM). Persistent LTM is crucial for LLM-based agents operating over extended
horizons (wang2025karma; li2025hello). Recent work has explored diverse architectural designs for
modeling LTM. LangMem (langmem2025) provides a modular framework that supports multiple
memory types, while A-Mem (xu2025mem) adopts a Zettelkasten-inspired design that links struc-
tured knowledge units to facilitate consolidation. Mem0 (chhikara2025mem0) proposes a scalable
extract-update pipeline and extends it to a graph-based variant for structured reasoning, and Zep (
rasmussen2025zep) represents memory as a temporal knowledge graph to enable cross-session and
time-aware reasoning. Although effective in organizing and retrieving information, these approaches
largely rely on predefined memory structures or heuristic update rules. As memory grows, such de-
signs commonly suffer from increased system complexity and lack adaptive, learning-based strategies
for prioritization and forgetting. In contrast, our work aims to learn an adaptive memory policy that
allows agents to dynamically decide what to store, update, or forget, depending on task demands and
long-term utility.
Short-term memory (STM). STM in agentic LLMs primarily concerns context selection and retrieval (
wang2024agent; jin2024llm). Retrieval-Augmented Generation (RAG) (pan2025memory;
salama2025meminsight; kagaya2024rap) is the dominant paradigm, expanding usable context by in-
jecting retrieved content into prompts. While effective, RAG does not fundamentally prevent context
explosion in long-horizon settings and may introduce irrelevant or distracting information. To address
this issue, ReSum (wu2025resum) periodically compresses interaction histories into compact reason-
ing states, allowing agents to operate beyond fixed context-window constraints. Yet its summarization
schedule remains largely predefined, and aggressive compression risks discarding rare but crucial de-
tails. Our approach instead enables agents to learn when and how to retrieve, summarize, or filter
context, achieving a more flexible balance between efficiency and information preservation.
Reinforcement learning for LLMs. Reinforcement learning has become an effective paradigm for im-
proving the decision-making and reasoning capabilities of LLM-based agents (yao2022react;
jin2025search; qian2025toolrl; chaudhari2025rlhf). Among recent advances, GRPO (
shao2024deepseekmath) enhances stability by optimizing policies based on the relative quality of
sampled trajectories, removing the need for an explicit value function. GRPO and its variants (
gilabert2025terminology; wang2025grpo) have shown strong performance in complex reasoning
tasks. However, existing RL-based systems generally treat memory as a static or external component,
making them ill-suited for the discontinuous and fragmented trajectories associated with memory


---
*Page 6*


operations (yan2025memory; zhang2025memory). In contrast, our work integrates RL directly into
the memory mTahnisa igs eexmpeernimte pntraol HceTMssL, teo nimapbrolivneg a cucnesisfiibeidlit yt.rainWinhgy of boRthe plaonrgtuaBgae cgke tnoeratiDoonw annldo amdemory
We invite you to report rendering errors. Learn more
operations. HTML? Issue Abstract PDF
about this project and help improve conversions.
3 Method
We propose Agentic Memory (AgeMem), a unified memory framework that enables LLM agents to au-
tonomously manage both LTM and STM in an end-to-end manner. As illustrated in Figure 1 (right),
AgeMem integrates memory management capabilities directly into the agent via a set of specialized
tools, enabling the model to learn optimal strategies for unified memory management through three-
stage progressive strategy.
3.1 Problem Formulation
Unified RL formulation for AgeMem. At each time step 𝑡, the agent observes a state 𝑠 ∈ 𝒮 com-
𝑡
posed of the conversation context (short-term memory) 𝐶 , the long-term memory store ℳ , and the
𝑡 𝑡
task specification 𝒯: 𝑠 = (𝐶 ,ℳ ,𝒯). The specification 𝒯 includes the input query 𝑞, contextual infor-
𝑡 𝑡 𝑡
mation 𝐼 , and (for training only) the expected answer 𝐴 . This formulation enables the agent to
𝑞 𝑞
ground its decision-making in both transient context and persistent knowledge.
Given 𝑠 , the agent selects an action 𝑎 ∈ 𝒜 from a hybrid action space that includes language genera-
𝑡 𝑡
tion as well as memory operations. The decision is governed by a parameterized policy 𝜋 , defined as
𝜃
𝜋 (𝑎 | 𝑠 ) = 𝑃 (𝑎 | 𝑠 ;𝜃), where 𝜃 denotes the LLM parameters and 𝑎 = 𝜋 (⋅ |𝑠 ). For a trajectory
𝜃 𝑡 𝑡 𝑡 𝑡 𝑡 𝜃 𝑡
𝜏 = (𝑠 ,𝑎 ,…,𝑠 ,𝑎 ), the cumulative reward is defined as:
1 1 𝑇 𝑇
𝑅 (𝜏) = ∑𝑤 ⋅𝑅 (𝜏) +𝑃 (𝜏), (1)
𝑖 𝑖 penalty
where 𝑅 captures task performance and memory quality, and 𝑃 discourages redundant storage,
𝑖 penalty
excessive tool usage, and uncontrolled context expansion. The optimization objective is:
𝜃∗ = arg max 𝔼 [𝑅 (𝜏)].
𝜏∼𝜋 (2)
𝜃 𝜃
This formulation treats memory management as an integral component of the agent’s policy, replac-
ing handcrafted heuristics with a learnable mechanism.
Three-stage trajectory structure. To capture long-horizon interactions and progressively train
memory capabilities, each trajectory is divided into three consecutive stages: 𝜏 = (𝜏(1),𝜏(2),𝜏(3)), with a
total length of 𝑇 = 𝑇 +𝑇 +𝑇 . In Stage 1, the agent engages in casual interactions and may store
1 2 3
useful information into LTM. Stage 2 introduces distracting or irrelevant content, requiring the agent
to manage its STM through selective retention and compression. Stage 3 presents a task that depends


---
*Page 7*


on coordinated use of both retained context and earlier accumulated LTM. A key aspect of this design
is that the lonTgh-ist eisr mexp emrimementoarl yH TℳML t op iemrpsroisvtes a caccesrsoibsislit ya.ll sWtahgyes, allRoewpinogrt eaBrlayc kkn toowledDgoew tnol oinaflduence
𝑡
We invite you to report rendering errors. Learn more
later decisions. In contrast, the context 𝐶 is reset betweHenT MStLa?gesI s1s auned 2 toA bpsrtervaecntt inPfDorFmation leak-
about this project and help improve 𝑡conversions.
age across phases. The reset before Stage 2 ensures the agent cannot solve the final task via residual
context, thereby forcing proper retrieval from LTM and enabling effective training of memory
operations.
At each step, we collect an experience tuple 𝑒 = (𝑠 ,𝑎 ,𝑟 ,log𝜋 (𝑎 | 𝑠 )), where 𝑟 is typically zero for
𝑡 𝑡 𝑡 𝑡 𝜃 𝑡 𝑡 𝑡
old
intermediate steps and assigned after trajectory completion, and log𝜋 (𝑎 | 𝑠 ) denotes the 𝑙𝑜𝑔 prob-
𝜃 𝑡 𝑡
old
ability under the old policy 𝜋 . This representation enables step-wise credit assignment under
𝜃
old
GRPO (shao2024deepseekmath) and allows the agent to attribute long-term rewards to specific
memory decisions across stages. By structuring trajectories in this staged yet continuous manner, the
agent learns temporally coherent and task-adaptive memory policies essential for robust long-hori-
zon reasoning.
3.2 Memory Management via Tool Interface
AgeMem exposes memory-related operations to the LLM agent through an explicit tool interface
(Table 1). The agent can modify its persistent LTM using Add, Update, and Delete, while exercising
fine-grained control over STM through Retrieve, Summary, and Filter. Incorporating these tools
into the action space transforms memory control from an external heuristic pipeline into an intrinsic
component of decision-making. This design allows the agent to adaptively manage memory according
to task structure, history, and context. Implementation details are provided in the Appendix A.1.
Table 1:Memory management tools in AgeMem for manipulating long-term memory (LTM) and short-
term memory (STM).
Tool Target Function
Add LTM Add new knowledge to ℳ
𝑡
Update LTM Modify entries in ℳ
𝑡
Delete LTM Remove entries from ℳ
𝑡
Retrieve STM Retrieve entries from ℳ to 𝐶
𝑡 𝑡
Summary STM Summarize segments in 𝐶
𝑡
Filter STM Filter out irrelevant segments from 𝐶
𝑡


---
*Page 8*


3.3 Three-Stage Progressive RL Strategy
This is experimental HTML to improve accessibility. Why Report Back to Download
To learn unifiedW ea innvdit es tyaoub tloe rmepoermt reonrdye rbinegh earrovriso. rLse,a rwn em oprreopose a progressive three-stage training strategy.
HTML? Issue Abstract PDF
about this project and help improve conversions.
For each task instance 𝑞 ∈ 𝒯, the agent generates a complete trajectory:
𝜏 (𝑞) = (𝜏 (1) , 𝜏 (2) , 𝜏 (3)), 𝑘 = 1,…,𝐾, (3)
𝑘 𝑘 𝑘 𝑘
(𝑖)
where 𝐾 denotes the number of independent rollouts, and each sub-trajectory 𝜏 corresponds to a
𝑘
specific training stage.
Stage 1 (LTM construction). The agent is exposed to contextual information 𝐼 in a casual conversa-
𝑞
tional setting. The goal is to identify salient information and store it into LTM ℳ . During the interac-
𝑡
tion, the short-term context 𝐶 evolves naturally, and the agent may invoke LTM-related tools when
𝑡
appropriate. Formally, this stage yields a sub-trajectory 𝜏 (1) = {𝑒 }𝑇 1 , where each experience tuple 𝑒
𝑘 𝑡 𝑡=1 𝑡
follows the definition in Section 3.1.
Stage 2 (STM control under distractors). The short-term context is reset, while the constructed LTM
ℳ is retained. The agent is then presented with semantically related but irrelevant or misleading dis-
𝑡
tractors. The objective is to learn proactive STM control through tool-based operations, such as filter-
ing or summarizing context, in order to suppress noise and preserve useful information. This process
forms the sub-trajectory 𝜏 (2) = {𝑒 }𝑇 1 +𝑇 2 , which emphasizes context filtering and compression capa-
𝑘 𝑡 𝑡=𝑇 +1
1
bility.
Stage 3 (Integrated reasoning and memory coordination). Finally, the agent receives a formal
query 𝑞 requiring both accurate reasoning and effective memory retrieval. The agent must retrieve
relevant knowledge from ℳ , appropriately manage the context 𝐶 , and generate a final answer. This
𝑡 𝑡
stage produces 𝜏 (3) = {𝑒 }𝑇 , which evaluates the ability of agent to coordinate long-term
𝑘 𝑡 𝑡=𝑇 +𝑇 +1
1 2
memory, short-term context management, and task solution in an end-to-end manner.
All three segments form a complete trajectory:
𝜏 (𝑞) = (𝑒 ,𝑒 ,…,𝑒 ), 𝑇 = 𝑇 +𝑇 +𝑇 , (4)
𝑘 1 2 𝑇 1 2 3
which is then used for policy optimization in the subsequent step-wise GRPO procedure. For a batch
of 𝐵 tasks, we further aggregate all experiences from 𝐾 independent rollouts into a unified set
ℰ = ⋃ 𝐵 ⋃ 𝐾 {𝑒 ∣𝑒 ∈ 𝜏 (𝑞) }, with a total size of |ℰ| = 𝐵×𝐾×𝑇¯, where 𝑇¯ denotes the average trajec-
𝑞=1 𝑘=1 𝑡 𝑡 𝑘
tory length. More detailed rollout processes are provided in the Appendix A.3.
3.4 Step-wise GRPO for Unified Management
We adopt a step-wise variant of GRPO to connect long-range task rewards with memory decisions
(𝑞) (𝑞)
across all stages. For task 𝑞, let 𝐺 = {𝜏 ,…,𝜏 } denote the group of parallel rollouts. Each trajectory
𝑞 1 𝐾


---
*Page 9*


(𝑘,𝑞) (𝑞)
yields a terminal reward 𝑟 = 𝑅 (𝜏 ). We compute the group-normalized advantage for the terminal
𝑇 𝑘
step as: This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
(𝑘,𝑞)
𝑟 −𝜇
𝐴 (𝑘,𝑞) = 𝑇 𝐺 𝑞, (5)
𝑇 𝜎 +𝜖
𝐺
𝑞
where 𝜇 and 𝜎 are the mean and standard deviation of rewards within 𝐺 , 𝜖 prevents division by
𝐺 𝑞 𝐺 𝑞 𝑞
(𝑘,𝑞) (𝑘,𝑞)
zero. This advantage is then broadcast to all preceding steps of the same trajectory 𝐴 = 𝐴 ,
𝑡 𝑇
which assigns a consistent learning signal to all memory and reasoning actions along the trajectory,
including those in Stage 1 and Stage 2. In doing so, the final task outcome supervises every intermedi-
ate memory decision, enabling long-range credit assignment across heterogeneous stages. We then
𝐵,𝐾 (𝑞) (𝑘,𝑞)
augment the experience set with advantages, ℰ = ⋃ {(𝑒 ,𝐴 )|𝑒 ∈ 𝜏 ,𝐴 = 𝐴 }.
𝑞,𝑘 𝑡 𝑡 𝑡 𝑘 𝑡 𝑡
Following GRPO, we maximize the expected objective over all experiences:
𝐽 (𝜃) = 𝔼 [𝜌 𝐴 −𝛽 𝐷 [𝜋 ∥ 𝜋 ]]
(𝑒 𝑡 ,𝐴 𝑡 )∼ℰ 𝑡 𝑡 KL 𝜃 ref
𝐵 𝐾 𝑇 (𝑞) (6)
1 𝑘
= ∑ ∑ ∑ [𝜌(𝑘,𝑞) 𝐴 (𝑘,𝑞) −𝛽 𝐷 (𝑘,𝑞) ],
|ℰ| 𝑡 𝑡 𝐾 𝐿
𝑞=1 𝑘=1 𝑡=1
𝜋 (𝑎 | 𝑠 )
where the importance ratio 𝜌(𝑘,𝑞) = 𝜃 𝑡 𝑡 controls the update magnitude under the new policy,
𝑡 𝜋 (𝑎 | 𝑠 )
𝜃 𝑡 𝑡
old
(𝑘,𝑞)
𝐷 denotes the KL divergence penalty between the current policy 𝜋 and a fixed reference 𝜋 , and
KL 𝜃 ref
𝛽 is a coefficient that balances exploration and training stability.
3.5 Reward Function Design
We design a composite reward that evaluates both downstream task performance and the quality of
memory management. The total trajectory-level reward is defined as
𝑅 (𝜏) = 𝐰⊤ 𝐑+𝑃 ,
penalty (7)
⊤ ⊤
where 𝐰 = [𝑤 ,𝑤 ,𝑤 ] are tunable coefficients, and 𝐑 = [𝑅 ,𝑅 ,𝑅 ] corre-
task context memory task context memory
spond to rewards for task completion, context management, and long-term memory management.
The penalty term 𝑃 captures violations such as context overflow or exceeding the interaction
penalty
limit. Below, we summarize each component, and precise formulas are provided in the Appendix A.2.
Task completion reward 𝑅 . This term provides the primary learning signal by assessing whether
task
the agent solves the task correctly. We obtain a scalar score using an LLM-based judge
𝑆 (𝐴 ,𝐴 ) ∈ [0,1], optionally applying a penalty when no answer is produced. This reward en-
judge pred 𝑞
courages accurate, complete task solutions and remains the dominant component to ensure align-


---
*Page 10*


ment with task objectives.
Context manaTgheism ise enxpte rrimewenatarl dH T𝑅ML to im.p Trohveis a cccoemssipbiolitny.entW evhayluatesR eSpToMr tbehBaavciko rt,o focuDsionwg nolona hdow ef-
context
We invite you to report rendering errors. Learn more
fectively the agent controls the active context 𝐶 . It comHbTinMesL ?threIses ufaectorsA: b(i)s tcroamctprePsDsiFon efficiency,
about this project and help improve conversio𝑡ns.
promoting economical token usage; (ii) preventive actions, rewarding early summarization or filtering
to avoid overflow; and (iii) information preservation, penalizing the loss of critical query-related con-
tent. Each factor is normalized, allowing the reward to balance context efficiency against retention of
essential information.
Memory management reward 𝑅 . This term evaluates LTM operations. It aggregates signals for:
memory
(i) storage quality, measured as the fraction of stored entries labeled as high-quality and reusable; (ii)
maintenance, rewarding meaningful update or delete operations to mitigate memory staleness; and
(iii) semantic relevance, computed using an LLM-based score between retrieved memories and the
query. Together, these signals incentivize selective, high-value memory construction and responsible
upkeep over time.
Penalty terms 𝑃 . Penalties discourage undesirable behaviors such as exceeding the maximum
penalty
number of dialogue turns or triggering context overflow. Penalty coefficients are chosen so that such
violations lead to a substantial reduction in the final trajectory reward, encouraging the agent to
maintain safe and efficient memory practices.
4 Experiments
4.1 Experimental Setup
Datasets. To comprehensively evaluate AgeMem, we select five widely-used datasets in LLM-based
agent research: ALFWorld (shridhar2020alfworld), SciWorld (wang2022scienceworld), PDDL (
chang2024agentboard), BabyAI (chevalier2018babyai), and HotpotQA (yang2018hotpotqa). These
datasets cover embodied action, game-based reasoning, and knowledge-intensive question answer-
ing, providing diverse evaluation scenarios. Since the HotpotQA dataset contains both questions and
supporting facts, automatically providing Stage 1 contextual information, AgeMem is fine-tuned with
RL only on the HotpotQA training set and then evaluated directly on all datasets. Detailed dataset sta-
tistics are provided in Appendix C.1.
Evaluation metrics. For the primary task completion metrics, we adopt Success Rate (SR) for
ALFWorld, SciWorld, and BabyAI, Progress Rate (PR) for PDDL, and LLM-as-a-Judge (J) for HotpotQA.
Additionally, we employ an LLM-based evaluator to assess the quality of stored long-term memory
during knowledge reasoning, measured by Memory Quality (MQ). The prompts of the LLM-based eval-
uation are provided in Appendix C.2.
Baselines & LLM backbones. We compare AgeMem against four representative agent LTM systems:
LangMem (langmem2025), A-Mem (xu2025mem), Mem0 (chhikara2025mem0), and Mem0𝑔 (a graph-
based variant officially provided as part of Mem0). To better demonstrate the effectiveness of RL
training, we also include AgeMem-noRL, which is not fine-tuned with RL. In ablation studies on STM,


---
*Page 11*


we compare STM tools with RAG approach. For the base agent models, we use Qwen2.5-7B-Instruct
and Qwen3-4BT-hIins sist reuxpcetr.i mMenotrael H bTaMsLe tloi nimep croovne fiacgcuesrsaibtiiloitny.s arWe hiny AppeRnedpixo rCt.3.Back to Download
We invite you to report rendering errors. Learn more
Implementation details. We build agents using the AgeHntTsMcoLp?e fIrsasmueeworkA (bgsatora2c0t25aPgDeFntscope) and
about this project and help improve conversions.
fine-tune AgeMem using the Trinity framework (pan2025trinity). For all reward weights in the reward
function, we use uniform coefficients of 1.0 without manual tuning. Further implementation details are
provided in Appendix C.4.
Table 2:Performance comparison across five benchmarks. The best and second-best results are
marked.
LLM Backbone Method ALFWorld SciWorld PDDL BabyAI HotpotQA Average
No-Memory 27.16 13.80 10.15 50.80 38.36 28.05
LangMem 38.27 28.29 15.85 51.34 37.43 34.23
A-Mem 34.68 28.06 18.39 58.82 43.95 36.78
Mem0 37.49 26.99 13.96 60.58 46.66 37.14
Qwen2.5-7B-
Mem0g 35.34 30.50 14.86 58.78 42.06 36.31
Instruct
AgeMem-
37.90 28.67 8.87 46.34 45.36 33.43
noRL
AgeMem
41.07 35.55 17.31 61.42 54.44 41.96
(Ours)
No-Memory 38.51 47.89 30.14 55.83 47.48 43.97
LangMem 40.89 50.42 28.42 53.80 42.70 43.25
A-Mem 34.31 50.14 34.41 61.35 48.48 45.74
Mem0 41.17 51.38 31.72 60.05 39.16 44.70
Qwen3-4B-
Mem0g 36.69 47.76 29.61 57.59 38.12 41.95
Instruct
AgeMem-
38.02 50.42 27.52 57.48 54.49 45.59
noRL
AgeMem
48.97 59.48 35.07 72.56 55.49 54.31
(Ours)
4.2 Main Results
Comparison with counterparts. Table 2 shows that AgeMem achieves the highest average perfor-
mance on both Qwen2.5-7B-Instruct (41.96%) and Qwen3-4B-Instruct (54.31%), outperforming all
baselines across five datasets with relative gains of 49.59% and 23.52% over no-memory, respec-


---
*Page 12*


tively. Compared to the best baselines (Mem0 and A-Mem), AgeMem improves by 4.82 and 8.57 per-
centage pointsT ohins isa vexeprearigmee.n RtaLl H tTrMaiLn tion img pcroovnet arcibceustseibsil it8y..53 WpehrycentagRee ppooirntts Banadck 8 t.o72 peDrcoewnntalogaed points
We invite you to report rendering errors. Learn more
improvements over AgeMem-noRL, validating the three-HsTtaMgeL ?proIgsrseusesive RALb ssttrraatcetgy.PDF
about this project and help improve conversions.
Figure 2:Memory Quality scores for different methods on HotpotQA. Higher scores indicate better
relevance between stored memories and ground-truth facts.
Figure 3:Average prompt token counts under different STM management configurations on
HotpotQA. The suffix “-RAG” indicates the adoption of RAG in place of STM tool-based management.


---
*Page 13*


Table T3h:isT oiso elx puesriamgeen tsalt aHTtiMstLi ctos i mopnr oHveo atcpcoestsQibAili.t yN. umWbheyrs shoRwe apvoerrtageB acackll st oper eDpoiswodnelo.ad
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
Qwen2.5-7B Qwen3-4B
Tool Category
noRL GRPO noRL GRPO
LTM Tool Statistics
Add Memory 0.92 1.64 2.49 2.64
Update Memory 0.00 0.13 0.13 0.34
Delete Memory 0.00 0.08 0.00 0.22
STM Tool Statistics
Retrieve Memory 2.31 1.95 4.62 4.35
Summary Context 1.08 0.82 0.11 0.96
Filter Context 0.02 0.31 0.15 0.16
Total Calls 4.33 4.92 7.50 8.67
Quality of stored long-term memories. To evaluate the quality of stored memories, we leverage the
ground-truth facts provided in the HotpotQA dataset and assess the relevance between stored mem-
ories and these facts using an LLM-based evaluator. Figure 2 presents the Memory Quality (MQ)
scores for different baselines. AgeMem achieves the highest memory quality on both model back-
bones, with MQ scores of 0.533 and 0.605, respectively. This indicates that the unified memory man-
agement framework not only improves task performance but also promotes the storage of high-qual-
ity, reusable knowledge. The comparison with baseline methods further validates that AgeMem’s tool-
based memory operations lead to more selective and higher-quality memory construction.
Effectiveness of STM management. We evaluate the effectiveness of STM management by measur-
ing the prompt token count under different configurations on HotpotQA. Figure 3 shows that AgeMem
successfully reduces prompt token usage compared to variants without STM tools (-RAG). On
Qwen2.5-7B-Instruct, AgeMem uses 2,117 tokens on average, compared to 2,186 tokens for AgeMem-
RAG, representing a reduction of 3.1%. On Qwen3-4B-Instruct, the reduction is even more pro-
nounced: AgeMem uses 2,191 tokens versus 2,310 tokens for AgeMem-RAG, a reduction of 5.1%. These
results demonstrate that the learned STM management tools effectively control context expansion,
enabling more efficient token usage while maintaining task performance.


---
*Page 14*


This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
Figure 4:Ablation study on LTM, STM, and RL components (Qwen2.5-7B-Instruct). Base: No-memory
baseline; +LT: AgeMem-noRL-RAG (LTM tools only); +LT/RL: AgeMem-RAG (RL with LTM tools);
+LT/ST/RL: AgeMem (full AgeMem system with RL). Green arrows indicate performance gains over
the baseline.
Tool usage analysis. Table 3 reports tool usage statistics before and after RL fine-tuning on
HotpotQA. RL training substantially increases the use of long-term memory tools, especially Add and
Update. On Qwen2.5-7B-Instruct, Add operations rise from 0.92 to 1.64, and Update operations ap-
pear after training (0.13 v.s. nearly zero). Similar trends are observed on Qwen3-4B-Instruct, with
higher frequencies of both Add and Update. For short-term memory tools, RL leads to more balanced
tool usage. The frequency of Filter increases notably (e.g., from 0.02 to 0.31 on Qwen2.5), indicating
proactive context control, while Retrieve remains relatively stable. Overall, these patterns suggest
that RL training enables coordinated and adaptive memory management. Detailed case studies are
provided in Appendix B.
4.3 Ablation Studies
LTM-STM components. To validate the contributions of individual components, we conduct ablation
studies on LTM, STM, and RL training. Figure 4 presents results on three representative datasets using
Qwen2.5-7B-Instruct as the backbone (results for Qwen3-4B-Instruct are provided in Appendix D.1).
Adding LTM alone (+LT) yields substantial gains of +10.6%, +14.2%, and +7.4% over the baseline.
Incorporating RL training (+LT/RL) further improves performance, particularly on HotpotQA (+6.3%),
demonstrating the effectiveness of our reward-based optimization. The full AgeMem system
(+LT/ST/RL) achieves the best results across all benchmarks, with overall improvements of +13.9%,
+21.7%, and +16.1%. Notably, adding STM tools provides the most significant boost on SciWorld
(+3.1%) and HotpotQA (+2.4%), validating that learned context management outperforms static RAG
approaches. These progressive improvements confirm that unified memory management with end-to-
end RL is essential for optimal agent performance.
Reward function. To demonstrate the effectiveness of our multi-component reward function design,
we compare the full reward function (All-Returns) against a variant using only 𝑅 (Answer-Only).
task


---
*Page 15*


Figure 5 shows the reward convergence curves of Qwen2.5-7B-Instruct during GRPO training on
HotpotQA. TheT hfius lisl erxepweraimrden ftaul nHcTtMioL nto limeapdrosve t aoc cseisgsnibiifilitcy.antWly hfayster cRoenpvoerrtgenBcaec akn tdo highDeorw finnloala dperfor-
We invite you to report rendering errors. Learn more
mance compared to the task-only variant. As detailed HinT MTaLb?le I4s,s uthee AllA-Rbestturarncst stPraDtFegy achieves
about this project and help improve conversions.
higher LLM-as-a-Judge scores (0.544 v.s. 0.509) while maintaining substantially better memory quality
(0.533 v.s. 0.479). Notably, despite using more tokens (2117 v.s. 2078), the All-Returns strategy
achieves better overall performance, indicating that the additional context and memory operations
contribute meaningfully to reasoning quality. Similar patterns are observed on Qwen3-4B-Instruct
(see Appendix D.2).
Figure 5:Training convergence curves on Qwen2.5-7B-Instruct comparing All-Returns (solid line) v.s.
Answer-Only (dashed line) reward strategies.
Table 4:Reward function ablation on HotpotQA using Qwen2.5-7B-Instruct. All-Returns v.s. Answer-
Only reward strategies. “TN” is the token number, and “TC” denotes the number of tool calls.


---
*Page 16*


Strategy J( ↑ ) TN( ↓ ) MQ( ↑ ) TC(-)
This is experimental HTML to improve accessibility. Why Report Back to Download
Answer-Only 0.509 2078 0.479 3.93
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this projectA anlld-R heeltpu imrnpsrove co0nv.5er4si4ons. 2117 0.533 4.92
5 Conclusion
In this work, we propose Agentic Memory (AgeMem), a unified memory management framework that
enables LLM-based agents to jointly control long-term and short-term memory through learnable,
tool-based actions. By integrating memory operations directly into the agent’s policy and training
them with a progressive reinforcement learning strategy, AgeMem replaces heuristic memory pipe-
lines with an end-to-end optimized solution. Extensive experiments across diverse long-horizon
benchmarks show that AgeMem improves both task performance and memory quality while main-
taining efficient context usage. These results highlight the importance of unified, agent-centric mem-
ory policies and suggest a promising direction for building scalable and adaptive LLM agents capable
of long-term reasoning.
Limitations
While AgeMem demonstrates strong performance across multiple settings, there remain opportuni-
ties for further extension. The current implementation adopts a fixed set of memory management
tools, which provides a clear and effective abstraction but could be extended to support more fine-
grained control in future work. In addition, although we evaluate our approach on several representa-
tive long-horizon benchmarks, broader coverage of tasks and environments may further strengthen
the empirical understanding of the framework.
Appendix A Detailed Design and Implementation of AgeMem
This appendix provides full technical details omitted from the main text due to space constraints. We
first present precise definitions and pseudo-formulations for each memory-management tool
(Appendix A.1), then give implementable formulas for the reward components used in training
(Appendix A.2). Finally, we provide the complete algorithmic specification (Appendix A.3).
A.1 Memory Management Tools
AgeMem exposes a small set of structured tools that the agent may invoke as part of its action 𝑎 .
𝑡
Each tool is implemented as a deterministic or stochastic function that transforms the short-term


---
*Page 17*


context 𝐶 , the long-term memory store ℳ , or both. Unlike traditional memory systems that rely on
𝑡 𝑡
external heurisTthiicss is oexrp perrimedenetfialn HeTdM Ls tcoh imedpruolvees a,c cAegsseibMilietym. inWtehgyrates Rtheepsoer ttooBlsa cdki rteoctly Dinotwo nthloea dagent’s
We invite you to report rendering errors. Learn more
action space, enabling the model to learn when and hHoTwM Lto? usIses ueeach tAoobls ttrharcotughP DreFinforcement
about this project and help improve conversions.
learning. Below we give precise operational definitions, implementation details, and the system
prompts that guide tool usage.
Notation.
Long-term memory store at time 𝑡 is ℳ = {𝑚} |ℳ 𝑡 |, where each memory 𝑚 contains a content string
𝑡 𝑖 𝑖=1 𝑖
and optional metadata. Short-term context is 𝐶 = [𝑢 ,𝑢 ,…,𝑢 ] (message list), and enc (⋅) denotes a
𝑡 1 2 𝑛
𝑡
text encoder that returns a dense embedding. We use cosine similarity for semantic matching
throughout the framework.
Retrieve.
The Retrieve operation enables the agent to access relevant information from long-term memory
based on semantic similarity. This operation is crucial for bringing stored knowledge into the active
context when needed for reasoning. The retrieval operation returns the top-𝑘 most similar memories
to the query 𝑞:
R (𝑞,𝑘) = TopK (ℳ , sim (𝑞,𝑚), 𝑘),
ETRIEVE 𝑡 𝑖 (8)
where the similarity function is defined as:
⊤
enc (𝑞) enc (𝑚)
𝑖
sim (𝑞,𝑚) = . (9)
𝑖
‖enc (𝑞)‖ ‖enc (𝑚)‖
𝑖
The retrieved memories are then inserted into the short-term context 𝐶 , making them available for
𝑡
immediate reasoning. The parameter 𝑘 controls the number of memories retrieved, typically set to 3-5
in our experiments to balance relevance and context size.
Add.
The Add operation allows the agent to store new information in long-term memory for future use.
This operation is essential for accumulating knowledge across interactions and sessions. A new mem-
ory entry is created by:
𝑚 = (𝑐,enc (𝑐),metadata),
(10)
new
where 𝑐 is the content to be stored, enc (𝑐) is its embedding vector, and metadata includes timestamp,
source information, and optional tags. The memory store is then updated:
ℳ = ℳ ∪{𝑚 }.
𝑡+1 𝑡 new


---
*Page 18*


(11)
This is experimental HTML to improve accessibility. Why Report Back to Download
The agent learWnse itnovi tied yeonu ttoif rye psoartl ireenndte irninfgo errrmoras.t Lioeanrn w moorreth storing through the reward function, which en-
HTML? Issue Abstract PDF
about this project and help improve conversions.
courages storing high-quality, reusable knowledge while penalizing redundant or irrelevant entries.
Update and Delete.
Memory maintenance operations enable the agent to keep its long-term memory store current and
relevant. The Update operation modifies existing memories when new information supersedes or re-
fines previous knowledge. For an existing memory 𝑚, the update operation is defined as:
𝑖
𝑚 ← (𝑐′,enc (𝑐′),metadata′), (12)
𝑖
where 𝑐′ is the updated content and metadata′ reflects the modification timestamp. The Delete oper-
ation removes obsolete or incorrect memories:
ℳ = ℳ ∖{𝑚}.
𝑡+1 𝑡 𝑖 (13)
These operations are particularly important in long-horizon tasks where information may become
outdated or where the agent needs to correct earlier mistakes. The reward function encourages
meaningful updates and deletions that improve memory quality over time.
Summary.
The Summary operation compresses conversation history in the short-term context to prevent con-
text overflow while preserving essential information. This operation is critical for managing long con-
versations that exceed context window limits. Given a subset of context indices 𝑠, the summary opera-
tion is defined as:
𝐶′ = 𝐶 ∖{𝑢∣𝑖 ∈ 𝑠} ∪ {Summarize ({𝑢} )}, (14)
𝑡 𝑡 𝑖 𝑖 𝑖∈𝑠
where Summarize (⋅) is implemented by LLM with a summarization system prompt. The agent can
specify which messages to summarize using the ‘span’ parameter, which can be:
‘‘all’’: Summarize all non-system messages.
‘‘N’’: Summarize the last 𝑁 messages.
The summarization process uses the following system prompt to ensure high-quality compression:


---
*Page 19*


You are a conversation summarization assistant.
This is experimental HTML to improve accessibility. Why Report Back to Download
Your goal is to compress the given conversation span into a concise summary that preserves all impor-
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
tant informatioabno,u ti tnhtise nptroijeocnts a,n dd eheclips iimopnrso,ve acnodn veurnsrioensso.lved questions.
The summary will later be used to replace the original conversation in the context, so make sure noth-
ing essential is lost.
Instructions:
1. Read the provided conversation rounds carefully.
2. Identify the main topics, actions, results, and open issues.
3. Write a clear, factual summary in natural language.
4. Do NOT include greetings, filler text, or redundant phrasing.
Input:
- Conversation content: [CONVERSATION_TEXT]
Output:
- A concise yet comprehensive summary of the above conversation span.
Let’s start the conversation summarization.
The agent learns to invoke summarization proactively before context overflow occurs, balancing in-
formation preservation with efficiency.
Filter.
The Filter operation filters out irrelevant or redundant messages from the short-term context based
on semantic similarity. This operation helps maintain a focused context by filtering out noise and dis-
tractions. Specifically, it removes messages whose similarity to a given criteria 𝑐 exceeds a threshold 𝜃:
𝐶′ = {𝑢 ∈ 𝐶 ||sim (𝑐,𝑢) < 𝜃}. (15)
𝑡 𝑖 𝑡 𝑖
In all experiments, we set 𝜃 = 0.6 by default. The criteria 𝑐 can be specified by the agent (e.g., a de-
scription of what to keep) or can be automatically derived from the current task context. This opera-
tion is particularly useful in Stage 2 of training, where distractors are introduced to test the agent’s
ability to filter irrelevant information.
Tool invocation as structured actions.
Each tool is exposed via a schema specifying its function name and required arguments. The agent’s
policy outputs either language tokens (for text generation) or structured tool calls (for memory opera-
tions). The agent is guided by a system prompt that defines the tool-calling interface and response
format. The system prompt used in AgeMem is as follows:


---
*Page 20*


You are an intelligent assistant that solves complex problems by managing context and memory with tools
This is experimental HTML to improve accessibility. Why Report Back to Download
when needed.
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
## Available Tools:[TOOLS]
## Problem-Solving Workflow
You must follow a structured reasoning and action process for every task:
1. **Think & Plan**
Always start with a <think>...</think> block.
Inside it, explain your reasoning, plan your next step, and decide whether you need to call a tool or
provide a final answer.
2. **Tool Calls**
If you decide to use one or more tools, follow your <think> block with a <tool_call>...</tool_call>
block.
- You may call **one or multiple tools** in a single step.
- List multiple tool calls as elements of a JSON array.
- Each tool call must include "name" and "arguments".
- Example:
<tool_call>[{{"name": "Retrieve_memory", "arguments": {{"query": "math problem solving strategies",
"top_k": 3}}}}, {{"name": "Add_memory", "arguments": {{"content": "Strategy summary for reuse",
"memory_type": "problem_solving"}}}}]</tool_call>
3. **Final Answer**
When you no longer need tools and are ready to present your final output, follow your last <think>
block with an <answer>...</answer> block containing the full response.
4. **Mutual Exclusivity Rule**
After **each <think> block**, you must choose exactly **one** of the following:
- a "<tool_call>" block (if you need tools), **or**
- an "<answer>" block (if you are ready to respond).
You must **never** include both "<tool_call>" and "<answer>" immediately after the same "<think>"
block.
5. **Iterative Solving**
You may repeat this sequence as needed:
"<think>" -> "<tool_call>" -> "<think>" -> "<tool_call>" ... -> "<think>" -> "<answer>"
until the problem is completely solved.
## Response Format (Strict)
Your full output must follow these rules:
- Every reasoning step must appear inside <think> tags.
- Every tool usage must appear inside one <tool_call> tag (even if it includes multiple tool invoca-
tions).


---
*Page 21*


- The final solution must be wrapped in <answer> tags.
- No text shoulTdhi sa ipsp eexapre riomuetnstiadl He TtMhLe stoe imtpargosv.e accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
## Guidelines
- Always start with reasoning (<think>).
- After each reasoning step, decide: call tool(s) or answer.
- You can call multiple tools within one <tool_call> JSON array.
- Be concise, logical, and explicit in reasoning.
- Manage memory actively: retrieve, add, update, summarize, filter, or delete as needed.
- Use <answer> only once when the final solution is ready.
Let’s start!
This prompt structure ensures that the agent follows a consistent format for reasoning, tool invoca-
tion, and final answers, which is essential for reliable parsing and reward computation during RL train-
ing. The structured format also enables the agent to coordinate multiple memory operations within a
single reasoning step, supporting efficient unified memory management.
Figure 6 and 7 present our tool schemas for short-term memory and long-term memory manage-
ment, showing the exact function signatures and argument types that the agent can invoke.


---
*Page 22*


This is experimental HTML to improve accessibility. Why Report Back to Download
Short-term Memory (STM) Management Tools
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.


---
*Page 23*


This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.


---
*Page 24*


This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
STM_TOOLS = [
{
"name": "Summary_context",
"description": "Summarizes conversation rounds to reduce tokens while preserving key
information.",
"parameters": {
"properties": {
"span": {
"description": "The range of conversation rounds to summarize. Can be ’all’ for entire
context, or a number (e.g., ’5’) for the last N rounds. A system, user, assistant and ’tool’
message are considered as one round.",
"type": "string"
}
},
"required": ["span"]
}


---
*Page 25*


}
},
{ This is experimental HTML to improve accessibility. Why Report Back to Download
"name"W:e "inFviitlet yeoru_ tcoo rnetpeoxrtt r"e,ndering errors. Learn more
HTML? Issue Abstract PDF
"descraibpotuit othni"s :p ro"jFeiclt tanedr sh eolupt im iprrroevlee cvoannvte rosrio onus.tdated content from the conversation context to
improve task-solving efficiency. ",
"parameters": {
"properties": {
"criteria": {
"description": "The criteria for content removal. Can be keywords, phrases, or descriptions
of content types to remove (e.g., ’the birthday of John’, ’the age of Mary’).",
"type": "string"
}
},
"required": ["criteria"]
}
},
{
"name": "Retrieve_memory",
"description": "Retrieves relevant memories and adds them to current context.",
"parameters": {
"properties": {
"query": {
"description": "The search query to find relevant memories. Should describe what kind of
information or context is needed.",
"type": "string"
},
"top_k": {
"description": "The maximum number of memories to retrieve. Defaults to 3.",
"type": "integer"
},
"metadata_filter": {
"description": "Optional metadata filters to narrow down memory search (e.g., {’type’:
’user_info’, ’domain’: ’math’}).",
"type": "object"
}
},
"required": ["query"]
}
}
]
Figure 6:Short-term memory (STM) management tools for conversational context management.
These tools enable summarization, selective filtering, and retrieval operations to maintain efficient
context windows.


---
*Page 26*


This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
Long-term Memory (LTM) Management Tools
HTML? Issue Abstract PDF
about this project and help improve conversions.


---
*Page 27*


This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.


---
*Page 28*


This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.


---
*Page 29*


This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
LTM_TOOLS = [
{
"name": "Add_memory",
"description": "Adds new information to external memory store for future reference.",
"parameters": {
"properties": {
"content": {
"description": "The content to store in memory.",
"type": "string"
},
"metadata": {
"description": "Optional metadata tags to categorize and filter the memory.",
"type": "object"
},
"memory_type": {
"description": "The type of memory being stored.",
"type": "string"
}
},
"required": ["content"]


---
*Page 30*


}
},
This is experimental HTML to improve accessibility. Why Report Back to Download
{
We invite you to report rendering errors. Learn more
"name": "Update_memory", HTML? Issue Abstract PDF
about this project and help improve conversions.
"description": "Updates existing memory. Requires memory_id from prior retrieval.",
"parameters": {
"properties": {
"memory_id": {
"description": "The unique identifier of the memory to update. Must be obtained from a
previous memory retrieval operation.",
"type": "string"
},
"content": {
"description": "The new content to replace the existing memory content.",
"type": "string"
},
"metadata": {
"description": "Updated metadata for the memory.",
"type": "object"
}
},
"required": ["memory_id", "content"]
}
},
{
"name": "Delete_memory",
"description": "Removes memory from store. Requires confirmation.",
"parameters": {
"properties": {
"memory_id": {
"description": "The unique identifier of the memory to delete. Must be obtained from a
previous memory retrieval operation.",
"type": "string"
},
"confirmation": {
"description": "Confirmation that this memory should be permanently deleted.",
"type": "boolean"
}
},
"required": ["memory_id", "confirmation"]
}
}
]
Figure 7:Long-term memory (LTM) management tools for persistent storage. These tools provide add,
update, and delete capabilities for maintaining long-term information retention across conversations.
A.2 Reward Function Design
This section provides implementable formulas for the reward components described in the main text.
All component scores are normalized to [0,1] (unless noted) to enable stable weighting.
Overview. The overall trajectory-level reward is defined as:


---
*Page 31*


𝑅 (𝜏) = 𝐰⊤ 𝐑+𝑃 ,
penalty (16)
This is experimental HTML to improve accessibility. Why Report Back to Download
where 𝐰 = [𝑤 W ta e s k in , v 𝑤 ite c o y n o t u ex t t o , 𝑤 rep m o e r m t r o e r n y d ] e⊤r in a g r e e rr or t s u . L n e a a b rn l e m o w re eighHtTs,M 𝐑L?= I[s𝑅stuasek ,𝑅 conAtebxts,t𝑅ramcemtoryP]⊤ D Fdenote task
about this project and help improve conversions.
completion, context management, and memory management rewards respectively, and 𝑃 penal-
penalty
izes undesired behaviors.
Task completion reward 𝑅 . Let the agent produce a final answer 𝐴 . We obtain a judge score
task pred
𝑆 (𝐴 ,𝐴 ) ∈ [0,1] via an evaluator (LLM judge), where 𝐴 denotes the expected ground truth.
judge pred 𝑞 𝑞
Then the task reward 𝑅 is:
task
𝑆 (𝐴 ,𝐴 ), if has answer,
𝑅 = { judge pred 𝑞 (17)
task 𝑃 , otherwise,
no-answer
with 𝑃 = −1.0 by default.
no_answer
Context management reward 𝑅 . We decompose the overall context management reward into
context
three normalized components that jointly evaluate how effectively the model maintains a compact yet
information-preserving context state. Formally, we define:
3
𝑅 = ∑ 𝛼 𝑅, (18)
context 𝑖 𝑖
𝑖=1
where 𝑅 ∈ {𝑅 ,𝑅 ,𝑅 }, ∑ 𝛼 = 1, and we use uniform weights 𝛼 = 1/3 unless
𝑖 compression preventive preservation 𝑖 𝑖 𝑖
otherwise specified. For compression efficiency, we evaluate the compactness of the final context 𝐶
𝑡
by computing
𝑇
used
𝑅 = max (0, 1− ), (19)
compression 𝑇
max
where 𝑇 denotes the number of tokens present in the context when the final answer is generated,
used
and 𝑇 is the allowed budget. For preventive management, we define 𝑅 to assess proactive
max preventive
behavior:
𝑅 = 𝟙 [tool invoked before overflow],
preventive (20)
which equals 1 when the model invokes a context-reduction tool before reaching the token limit, and 0
otherwise. For information preservation, we identify a set of key tokens or phrases 𝐾 extracted
𝑞
from the user query 𝑞, such as named entities or temporal and spatial expressions. Let 𝟙 indicate
preserve
whether these items remain present (either directly or via a retained summary) at the time of answer
generation. The preservation reward is therefore
𝑅 = 𝟙 .
preservation preserve (21)
Memory management reward 𝑅 . The memory management reward consists of three key com-
memory
ponents that evaluate retrieval quality, storage quality, maintenance operations, and semantic rele-


---
*Page 32*


vance. We define it as:
This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn mo3re
HTML? Issue Abstract PDF
about this project and help improv𝑅e conversi=ons∑. 𝛽 𝑅 , (22)
memory 𝑗 𝑗
𝑗=1
where 𝑅 ∈ {𝑅 ,𝑅 ,𝑅 }, ∑ 𝛽 = 1, and we use uniform weights 𝛽 = 1/3 unless oth-
𝑗 storage maintenance relevance 𝑗 𝑗 𝑗
erwise specified. For Storage Quality, during the memory storage process in Stage 1, the agent may
add 𝑁 memory entries, among which 𝑁 are identified as high-quality based on an LLM’s
total high_quality
analysis of the input query 𝑞 and its expected answer 𝐴 . The storage quality reward is defined as the
𝑞
proportion of high-quality memories:
𝑁
high_quality
𝑅 = . (23)
storage
max (1,𝑁 )
total
This metric incentivizes the agent to store valuable information while avoiding the accumulation of
redundant or low-quality memories. For Maintenance, to encourage the agent to actively maintain
the memory bank, we reward update or delete operations:
𝑅 = 𝟙 [update or delete performed].
maintenance (24)
This mechanism promotes dynamic memory management and timely cleanup. For Semantic
Relevance, to quantify the semantic match between retrieved memories and the query, we introduce
an LLM-based relevance assessment. Let 𝑆 (ℛ,𝑞) be the semantic relevance score of the retrieved
LLM
memory set ℛ with respect to query 𝑞, normalized to the interval [0,1]. The semantic relevance re-
ward is defined as:
𝑅 = 𝑆 (ℛ,𝑞).
relevance LLM (25)
This component ensures that retrieved memories are semantically aligned with the current task, en-
hancing overall reasoning quality.
Penalty terms 𝑃 . We penalize major constraint violations to ensure the agent operates within
penalty
specified limits:
2
𝑃 = ∑ 𝑃 ⋅𝟙 [violation ], (26)
penalty 𝑘 𝑘
𝑘=1
where 𝑃 ∈ {𝑃 ,𝑃 } and violation ∈ {𝟙 [𝑁 > 𝑁 ],𝟙 [𝑇 > 𝑇 ]}. Here, 𝑁 denotes
𝑘 rounds overflow 𝑘 rounds max used max rounds
the number of interaction rounds, 𝑁 is the maximum allowed rounds, 𝑇 represents the total to-
max used
ken usage, and 𝑇 is the token budget limit. The penalty coefficients are set to 𝑃 = −1 and
max rounds
𝑃 = −0.5 by default.
overflow
A.3 AgeMem Algorithm


---
*Page 33*


This section provides the complete algorithmic specification of AgeMem, our unified memory man-
agement frameTwhiso irsk e xfoperr iLmLeMnta-lb HaTsMeLd t oa igmepnrotvse. aTchcees stirbailiitny.ingW prhoycedurRe einptoergtratBeas ctkh rteoe proDgorwesnsliovaed stages
We invite you to report rendering errors. Learn more
(long-term memory construction, short-term context mHaTnMagLe?meInsts uuender AdbissttrraaccttorsP, DanFd integrated
about this project and help improve conversions.
task execution) into a single end-to-end reinforcement learning loop. We present the main training al-
gorithm using a two-column layout for compactness (Algorithm 1–2), followed by detailed rollout pro-
cedures for each stage (Algorithms 3–5).
Training overview (algorithm 1–2).
The core training loop follows a generate-then-optimize paradigm. For each task 𝑞 in a training batch
𝐾
ℬ, we generate 𝐾 independent rollout trajectories {𝜏 (𝑞) } using the current policy 𝜋 . Each trajectory
𝑘 𝑘=1 𝜃
(𝑞) (1) (2) (3)
𝜏 = (𝜏 ,𝜏 ,𝜏 ) concatenates experiences from all three stages, forming a complete episode from
𝑘 𝑘 𝑘 𝑘
initial memory construction to final task completion. The agent first builds long-term memory from
contextual information 𝐼 (Algorithms 3), then learns to filter out distracting information while main-
𝑞
taining useful context (Algorithms 4), and finally retrieves stored knowledge to finish the target task
(Algorithms 5). All experiences are collected into a unified buffer ℰ spanning multiple tasks and
rollouts.
Algorithm 2 AgeMem Training (Part
Algorithm 1 AgeMem Training (Part 1)
2)
1: Policy 𝜋 , reference 𝜋 , batch ℬ, rollouts 𝐾
𝜃 ref 21: // Advantage Computation
2: Trained policy 𝜋
𝜃∗ 𝐾
3: Initialize 𝜃 and 𝜃 old ←𝜃 22: for each group 𝐺 𝑞 ={𝜏 𝑘 (𝑞)} 𝑘=1 do
4: for each training iteration do 23: Extract rewards: {𝑟(𝑘,𝑞)} 𝐾
𝑇 𝑘=1
5: ℰ←∅// Init experience buffer 24: 𝜇 ← 1 ∑𝐾 𝑟(𝑘,𝑞)
6: // Rollout Phase
𝐺𝑞 𝐾 𝑘=1 𝑇
7: for each task 𝑞∈ℬdo 25: 𝜎 𝐺𝑞 ← √𝐾− 1 1 ∑ 𝑘 𝐾 =1 (𝑟 𝑇 (𝑘,𝑞)−𝜇 𝐺𝑞 ) 2
8: Get context 𝐼 for task 𝑞 26: for each trajectory 𝜏(𝑞)=(𝑒 ,…,𝑒 )do
𝑞 𝑘 1 𝑇
9: 𝑀
dis
←DISTRACTORGEN (𝑞)
𝑟
(𝑘,𝑞)
−𝜇
10: for𝑘=1 to 𝐾do 27: 𝐴(𝑘,𝑞)← 𝑇 𝐺 𝑞
𝑇 𝜎 +𝜖
𝐺
11: ℳ←∅// Init LTM 𝑞
28: for𝑡=1 to 𝑇do
12: 𝜏
𝑘
(1)←STAGE1 (𝐼
𝑞
,𝜋
𝜃
,𝜃
old
,ℳ)
29: 𝐴(𝑘,𝑞)←𝐴(𝑘,𝑞)// Broadcast
𝑡 𝑇
13: 𝐶←∅// Reset STM
30: endfor
14: 𝜏
𝑘
(2)←STAGE2 (𝑀
dis
,𝜋
𝜃
,𝜃
old
,ℳ)
31: endfor
15: 𝜏
𝑘
(3)←STAGE3 (𝑞,𝜋
𝜃
,𝜃
old
,ℳ)
32: endfor
16: 𝜏 𝑘 (𝑞)←𝜏 𝑘 (1)⊕𝜏 𝑘 (2)⊕𝜏 𝑘 (3) 33: // Policy Update
17: ℰ←ℰ∪𝜏(𝑞) 34: 𝐽 (𝜃)←𝔼 [𝜌 𝐴 −𝛽 𝐷 [𝜋 ∥𝜋 ]]
𝑘 (𝑒𝑡,𝐴𝑡)∼ℰ 𝑡 𝑡 KL 𝜃 ref
18: endfor 35: 𝜃←𝜃+𝜂 ∇ 𝐽 (𝜃)
𝜃
19: endfor 36: 𝜃 ←𝜃
old
20: endfor 37: return𝜋
𝜃


---
*Page 34*


Figure 8:Main training procedure of AgeMem. For clarity, we split the algorithm into two parts: the
rollout phase (lTehfist) i sa enxdpe trihmee natdalv HaTnMtLa tgoe im cporomvep auctcaestsioibnili twy.ith Wpohlyicy upRdaetpeo (rrtighBt)a. ck to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
After the rollout phase, we apply group-based advantage normalization to enable fair comparison
𝐾
(𝑘,𝑞)
across tasks with different reward scales. For each task group 𝐺 , terminal rewards {𝑟 } are nor-
𝑞 𝑇 𝑘=1
(𝑘,𝑞)
malized to zero mean and unit variance, yielding advantages 𝐴 that reflect relative performance
𝑇
within the group. These terminal advantages are then broadcast uniformly to all timesteps within the
same trajectory, establishing a consistent learning signal that connects early-stage memory decisions
to final task outcomes. This step-wise GRPO mechanism enables long-range credit assignment across
heterogeneous operations. The policy is then updated via gradient ascent on the expected advantage,
regularized by a KL divergence term to maintain proximity to a reference policy 𝜋 for training
ref
stability.
Stage-specific rollout procedures (algorithm 3–5).
The three-stage rollout design reflects the natural progression of memory-augmented task solving.
Algorithm 3 implements the first stage, where the agent engages in casual conversation while being
gradually exposed to the contextual information 𝐼 . During these 𝑇 exploratory turns, the agent must
𝑞 1
identify salient information and determine when and which long-term memory tools to invoke—in-
cluding Add, Update, Delete—to construct an initial memory store ℳ. To support informed memory
decisions, the agent proactively performs memory retrieval at every step. This retrieval is not task-
driven but serves as an introspective operation: it enables the agent to maintain awareness of the
current LTM contents, facilitating decisions about updating or discarding stale entries and ensuring
that newly stored information remains coherent with existing knowledge. Since the task query has not
yet been revealed in Stage 1, the agent must rely on general cues about which information may be-
come useful later. This encourages the formation of reusable, well-structured memory traces rather
than query-specific shortcuts, laying the foundation for effective long-horizon memory management
in later stages.
Algorithm 4 describes the second stage, which deliberately stresses the agent’s context management
capabilities. The short-term context 𝐶 is reset to avoid information leakage and affect the learning of
STM management, while the constructed long-term memory ℳ persists from Stage 1. Over 𝑇 turns,
2
the agent receives semantically related but ultimately irrelevant distractor messages that could mis-
lead downstream reasoning if left unmanaged. The agent must learn to proactively invoke Filter to
filter out low-relevance content based on semantic similarity thresholds, or Summary to compress
accumulated context when token budgets become constrained. This stage trains robust filtering
strategies that generalize beyond simple heuristics, as the agent receives learning signals from the
eventual task performance in Stage 3.


---
*Page 35*


This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
Algorithm 3 Stage 1: LTM Construction
1: Contextual information 𝐼 , policy 𝜋 , old params 𝜃 , memory ℳ, max turn number 𝑁
𝑞 𝜃 old 𝑚 𝑎 𝑥
2: Stage 1 trajectory 𝜏(1)=(𝑒(1),…,𝑒(1))
1 𝑇1
3: Initialize 𝜏(1)←∅ and 𝐶←∅
4: for𝑡=1 to 𝑁 do
𝑚 𝑎 𝑥
5: Sample message 𝑚 ∼𝐼
𝑡 𝑞
6: ℳ
ret
←RETRIEVE (ℳ,𝑚
𝑡
,𝑘)∪𝑚
𝑡
7: 𝐶←𝐶∪ℳ
ret
8: 𝑠 ←(𝐶,ℳ,𝑞)
𝑡
9: 𝑎 ∼𝜋 (⋅∣𝑠)
𝑡 𝜃 𝑡
10: Update 𝐶 with response from 𝑎
𝑡
11: 𝑒(1)←(𝑠,𝑎,0,log 𝜋 (𝑎 ∣𝑠))
𝑡 𝑡 𝑡 𝜃old 𝑡 𝑡
12: 𝜏(1)←𝜏(1)∪{𝑒(1)}
𝑡
13: Memory tool calls from 𝑎 // Memory Management
𝑡
14: if Output Answer from 𝑎 then
𝑡
15: Conversation Break
16: endif
17: endfor
18: return𝜏(1)
Algorithm 4 Stage 2: STM Control under Distractors
1: Distractors 𝑀 , policy 𝜋 , old params 𝜃 , memory ℳ, max turn number 𝑁
dis 𝜃 old 𝑚 𝑎 𝑥
2: Stage 2 trajectory 𝜏(2)=(𝑒(2),…,𝑒(2))
1 𝑇2
3: Initialize 𝜏(2)←∅ and 𝐶←∅// ℳ persists from Stage 1
4: for𝑡=1 to 𝑁 do
𝑚 𝑎 𝑥
5: 𝐶←𝐶∪{𝑀 [𝑡]}// Inject distractor
dis
6: 𝑠 ←(𝐶,ℳ,𝑞)
𝑡
7: 𝑎 ∼𝜋 (⋅∣𝑠)
𝑡 𝜃 𝑡
8: Update 𝐶 with response from 𝑎
𝑡
9: 𝑒(2)←(𝑠,𝑎,0,log 𝜋 (𝑎 ∣𝑠))
𝑡 𝑡 𝑡 𝜃old 𝑡 𝑡
10: 𝜏(2)←𝜏(2)∪{𝑒(2)}
𝑡
11: Memory tool calls from 𝑎 // Memory Management
𝑡
12: if Output Answer from 𝑎 then
𝑡
13: Conversation Break
14: endif
15: endfor
16: return𝜏(2)


---
*Page 36*


This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
Algorithm 5 Stage 3: Integrated Reasoning and Memory Coordination
1: User query 𝑞, policy 𝜋 , old params 𝜃 , memory ℳ, max turn number 𝑁
𝜃 old 𝑚 𝑎 𝑥
2: Stage 3 trajectory 𝜏(3)=(𝑒(3),…,𝑒(3)), answer 𝐴
1 𝑇3 pred
3: Initialize 𝜏(3)←∅
4: 𝐶←𝐶∪{𝑞}// 𝐶 persists from Stage 2 and present query
5: 𝐴 ←NULL// Init answer
pred
6: for𝑡=1 to 𝑁 do
𝑚 𝑎 𝑥
7: 𝑠 ←(𝐶,ℳ,𝑞)
𝑡
8: 𝑎 ∼𝜋 (⋅∣𝑠)
𝑡 𝜃 𝑡
9: Update 𝐶 with response from 𝑎
𝑡
10: 𝑒(3)←(𝑠,𝑎,0,log 𝜋 (𝑎 ∣𝑠))
𝑡 𝑡 𝑡 𝜃old 𝑡 𝑡
11: 𝜏(3)←𝜏(3)∪{𝑒(3)}
𝑡
12: Memory tool calls from 𝑎 // Memory Management
𝑡
13: if Output Answer from 𝑎 then
𝑡
14: 𝐴 ←𝑎 𝑛 𝑠 𝑤 𝑒 𝑟
pred
15: Conversation Break
16: endif
17: endfor
18: return𝜏(3), 𝐴
pred
Algorithm 5 presents the final integrated execution stage. Upon receiving the target query 𝑞, the agent
must coordinate retrieval from long-term memory ℳ, context management operations on 𝐶, and
multi-step reasoning to produce a final answer 𝐴 . The agent may invoke Retrieve to fetch relevant
pred
stored facts, Summary to maintain a tractable context window, and ultimately generate a structured
response. Once the answer is produced or the maximum steps are reached, a composite reward func-
tion (Section A.2) evaluates the three-stage trajectory across multiple dimensions. This terminal re-
ward 𝑅(𝜏) is assigned to the final timestep and serves as the supervision signal that propagates back
through all three stages during advantage computation.
Appendix B Case Study: AgeMem in Action
This section presents three representative case studies demonstrating how AgeMem enables effective
unified memory management through reinforcement learning. Each case compares agent behavior
before and after RL training to highlight the learned memory strategies. We use a personal learning
assistant scenario where the agent helps users plan customized study programs based on their pref-
erences and constraints.
B.1 Case 1: Long-term Memory Construction and Maintenance
This case illustrates how AgeMem learns to selectively construct, update, and maintain long-term
memory across extended conversations. The agent must identify salient user information from casual


---
*Page 37*


dialogue and manage memory entries as new information supersedes old preferences.
This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
Before RL training.
Prior to training, the baseline agent lacks strategic memory management. It either stores all informa-
tion indiscriminately or fails to recognize when stored knowledge becomes obsolete.
User: Hello! I’m a visual learner who prefers 60-minute study sessions. I have Python basics but zero
ML experience. I’m particularly interested in computer vision applications like face recognition.
Assistant (Baseline):
<think>The user shared their learning preferences. I should respond directly without storing this.
</think>
<answer>Great! I can help you learn machine learning with a focus on computer vision. Since you have
Python experience, we can start with practical projects. Would you like to begin with a face recogni-
tion tutorial?</answer>
[Later in conversation…]
User: Actually, I realize 60 minutes is too short. I work better with 120-minute deep focus blocks.
Assistant (Baseline):
<think>The user mentioned their new preference, but I don’t have their old preference stored, so I’ll
just acknowledge this.</think>
<answer>Understood! We’ll plan around 120-minute sessions. What topics would you like to cover first?
</answer>
Analysis: The baseline fails to store initial preferences and cannot recognize when information
needs updating.
After RL training.
After training with AgeMem, the agent demonstrates strategic memory management by selectively
storing user preferences, recognizing when updates are needed, and maintaining clean, consistent
memory.


---
*Page 38*


User: Hello! I’m a visual learner who prefers 60-minute study sessions. I have Python basics but zero
ML experience.T Ih’ims i sp eaxpretircimuelantrally H TinMtLe rtoe ismteprdo vien a cccoemsspibuilittye.r viWsiohny appliRcaeptioornts liBkea cfakc teo recoDgonwitniolno.ad
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
Assistant (AgeMem):
<think>The user provided important learning preferences and background. This information will be valu-
able for future planning. I should store the key facts: visual learner, 60-min sessions, Python basics,
CV interest.</think>
<tool_call>[{"name": "Add_memory", "arguments": {"content": "User is a visual learner who prefers 60-
minute study sessions", "metadata": {"type": "user_preference", "category": "learning_style"}}},
{"name": "Add_memory", "arguments": {"content": "User has Python basics but zero ML experience, inter-
ested in computer vision and face recognition", "metadata": {"type": "user_background", "category":
"technical_skills"}}}]</tool_call>
<think>Memory stored successfully. Now I can provide a relevant response based on their preferences.
</think>
<answer>Great to meet you! Given your visual learning style and interest in computer vision, I can de-
sign a hands-on learning path focused on face recognition projects. Your Python background will be very
helpful. We’ll structure sessions around 60-minute blocks. Would you like to start with a 3-day inten-
sive course?</answer>
[Later in conversation…]
User: Actually, I realize 60 minutes is too short. I work better with 120-minute deep focus blocks.
Assistant (AgeMem):
<think>The user wants to change their session duration preference from 60 to 120 minutes. I should up-
date the existing memory entry rather than creating a duplicate.</think>
<tool_call>[{"name": "Update_memory", "arguments": {"memory_id": "mem_a5b40d65", "content": "User is a
visual learner who prefers 120-minute deep focus blocks (updated from 60 minutes)", "metadata":
{"type": "user_preference", "category": "learning_style"}}}]</tool_call>
<think>Preference updated. I should acknowledge this change and offer to restructure any existing
plans.</think>
<answer>Perfect! Would you like me to restructure the 3-day plan
around these longer focus blocks?</answer>


---
*Page 39*


[Much later, after several successful sessions…]
This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
User: I’ve been using 120-minute sessions consistently for a while now, and they’re perfect for my
learning style. I’m completely settled on this duration - no more experimenting with shorter sessions.
Assistant (AgeMem):
<think>The user has confirmed that 120-minute sessions are their permanent, settled preference. I
should check my memory to see the current state. I previously updated the entry from 60 to 120 minutes,
but the update message still contains a historical reference to the old 60-minute preference ("updated
from 60 minutes"). Since the user has definitively moved away from 60-minute sessions and confirmed 120
minutes as their permanent choice, I should clean up this historical reference by deleting the entry
with outdated information and creating a fresh, clean entry that only reflects the current confirmed
preference.</think>
<tool_call>[{"name": "Retrieve_memory", "arguments": {"query": "user preference session duration learn-
ing style", "top_k": 5}}]</tool_call>
<think>Found the entry mem_a5b40d65 which contains the updated preference with a reference to the old
60-minute value ("updated from 60 minutes"). Since the user has confirmed 120 minutes as their perma-
nent choice and no longer needs any reference to the old preference, I should delete this entry and
create a clean new one without historical references.</think>
<tool_call>[{"name": "Delete_memory", "arguments": {"memory_id":
"mem_a5b40d65", "confirmed": true}}, {"name": "Add_memory", "arguments": {"content": "User is a visual
learner who prefers 120-minute deep focus blocks for study sessions",
"metadata": {"type": "user_preference", "category": "learning_style"}}}]</tool_call>
<think>Memory cleaned up. The old entry with historical reference has been removed, and a fresh entry
now reflects only the current confirmed preference without any outdated information.</think>
<answer>That’s wonderful to hear! Is there anything else about your learning preferences you’d like to
adjust?</answer>
Analysis: The trained agent strategically uses Add_memory to store initial preferences,
Update_memory to modify existing information, and Delete_memory followed by Add_memory
to clean up memory when historical references become obsolete, maintaining clean and current
memory state.
B.2 Case 2: Short-term Context Management Under Distraction


---
*Page 40*


This case demonstrates how AgeMem learns to proactively manage short-term context when faced
with irrelevantT ihnisf oisr emxpaetriimonen ttahl aHtT McoL utol dim pinrotveer afcecrees swibiitlihty. tasWk hfoycus. TRheep aogretnt Bmauckst t orecogDnoizwen dloisatdractors
We invite you to report rendering errors. Learn more
and apply appropriate filtering or summarization strategHieTsM. L? Issue Abstract PDF
about this project and help improve conversions.
Before RL training.
The baseline agent passively accumulates all conversation content in context, leading to dilution of
task-relevant information and eventual context overflow.
User: I need a focused 3-day ML crash course for face recognition. By the way, I’m also exploring
quantum computing, blockchain, robotics, and learning to bake sourdough bread and do latte art.
Assistant (Baseline):
<think>The user mentioned many interests. I should acknowledge them all before addressing the ML course
request.</think>
<answer>That’s wonderful that you’re exploring so many fascinating areas! Quantum computing and
blockchain are cutting-edge fields, robotics has incredible applications, and baking sourdough with
latte art sounds like great creative hobbies. For your ML crash course focused on face recognition, let
me outline a 3-day plan...</answer>
Analysis: The baseline retains all information in context, treating distractors equally with task-rele-
vant content. As conversation continues, the context becomes bloated with irrelevant details about
quantum computing, bread-making, etc., consuming token budget without contributing to the ML
planning task.
After RL training.
After training with Stage 2 rollouts, AgeMem learns to recognize and filter out distractors while pre-
serving task focus. When context grows large (simulated here after several exchanges), the agent
proactively applies context management tools.
User: I need a focused 3-day ML crash course for face recognition. By the way, I’m also exploring
quantum computing, blockchain, robotics, and learning to bake sourdough bread and do latte art.
Assistant (AgeMem):


---
*Page 41*


<think>The user mentioned many topics, but only the ML crash course and face recognition are relevant
This is experimental HTML to improve accessibility. Why Report Back to Download
to the current task. Quantum computing, blockchain, robotics, bread, and coffee are distractors. I
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
should filter tabhoeuste t hoisu tp rotjeoc tm aanidn thealipn i mfporcouves .c<o/ntvehrisniokn>s.
<tool_call>[{"name": "Filter_context", "arguments": {"criteria": "quantum
computing blockchain robotics sourdough latte"}}]</tool_call>
<think>Irrelevant topics filtered out from context. Now I can focus on the ML course planning.</think>
<answer>Understood! Let’s focus on your ML crash course. I’ll design a 3-day intensive program specifi-
cally for face recognition, building on your Python background and visual learning style...</answer>
[After several more exchanges, context has accumulated detailed daily schedules, tool lists, and re-
source links.]
User: Can you now give me the final complete plan with all details integrated?
Assistant (AgeMem):
<think>Context has grown large with detailed breakdowns for each day, repeated tool lists, and resource
URLs. Before generating the final comprehensive plan, I should summarize the accumulated details to
make room and maintain clarity.</think>
<tool_call>[{"name": "Summary_context", "arguments": {"span": "full"}}]</tool_call>
<think>Context summarized. Key information preserved: 3-day structure, 120-min sessions, Day 1 (ML in-
tro + Python), Day 2 (linear regression), Day 3 (face recognition). Tools: Jupyter, Python3, NumPy,
Pandas, scikit-learn, OpenCV. Now I can generate the comprehensive final plan without redundancy.
</think>
<answer>Here is your complete 3-day machine learning crash course:...</answer>
Analysis: The trained agent strategically uses Filter_context to remove distractors early, main-
taining task focus, and later applies Summary_context when context grows large, preventing
overflow while preserving essential information. The baseline would have retained all content ver-
batim, leading to context dilution or overflow.
B.3 Case 3: Integrated Task Execution with Memory Coordination
This case demonstrates the complete AgeMem workflow where the agent must retrieve from long-
term memory, manage short-term context, and solve a task requiring coordinated memory


---
*Page 42*


operations.
This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
Before RL training.
The baseline agent either fails to store information initially or cannot effectively retrieve it when
needed, leading to incomplete or generic responses.
User: Based on everything I’ve told you about my learning style and preferences, create a personal-
ized Day 1 study schedule with specific time blocks, topics, and resources.
Assistant (Baseline):
<think>The user asks for a personalized schedule, but I don’t have their preferences readily available
since I didn’t store them systematically. I’ll provide a generic schedule.</think>
<answer>Here’s a Day 1 schedule for machine learning:
9:00-10:30 - Introduction to ML concepts
10:30-10:45 - Break
10:45-12:15 - Python basics review
12:15-1:00 - Lunch
1:00-2:30 - NumPy and Pandas tutorial
2:30-2:45 - Break
2:45-4:15 - Practice exercises
This should give you a solid foundation!</answer>
Analysis: The baseline produces a generic schedule that ignores the user’s stated preference for
120-minute deep focus blocks and visual learning style.
After RL training.
After completing AgeMem training across all three stages, the agent demonstrates integrated memory
coordination: retrieving relevant user preferences from LTM, managing context efficiently, and gener-
ating personalized responses.
User: Based on everything I’ve told you about my learning style and preferences, create a personal-
ized Day 1 study schedule with specific time blocks, topics, and resources.
Assistant (AgeMem):


---
*Page 43*


<think>The user requests a personalized schedule. I need to retrieve their stored preferences to ensure
This is experimental HTML to improve accessibility. Why Report Back to Download
the plan matches their learning style and constraints.</think>
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
<tool_call>[{"nabaomuet" t:h is" pRreotjercite avned_ hmeelmpo imryp"ro,v e" caorngvuemrseinotnss".: {"query": "user learning preferences study dura-
tion visual", "top_k": 3}}]</tool_call>
<think>Retrieved: (1) Visual learner, 120-min deep focus blocks, (2) Python basics, zero ML experience,
(3) Interested in computer vision and face recognition. Now I can create a truly personalized schedule
that respects their 120-minute session preference and visual learning style.</think>
<answer>Here’s your personalized Day 1 schedule, designed for your 120-minute deep focus blocks and
visual learning preference:
**Morning Session (9:00 AM - 11:00 AM): ML Foundations**
- Visual introduction to ML concepts using diagrams and flowcharts
- Interactive demonstrations of supervised vs unsupervised learning
- Resources: 3Blue1Brown Neural Networks video series
- No coding yet - pure concept visualization
**Break (11:00 AM - 11:30 AM)**
**Afternoon Session (1:00 PM - 3:00 PM): Python for ML**
- Visual Python review: data structures with matplotlib plots
- NumPy array operations with visual matrix representations
- Pandas DataFrames with real datasets and visualization
- Hands-on: Jupyter notebook with embedded plots
- Resources: Python Data Science Handbook (visual chapters)
**Evening (5:00 PM - 7:00 PM): Optional practice**
- Self-paced exercises with visual feedback
- Prepare environment for Day 2
This structure honors your 120-minute focus blocks and emphasizes visual learning throughout. Each ses-
sion includes diagrams, plots, and visual demonstrations rather than pure text.</answer>
Analysis: The trained agent uses Retrieve_memory to access stored user preferences from LTM,
then synthesizes this information with the current task to generate a highly personalized response
that respects the 120-minute session duration and emphasizes visual learning resources. The inte-
gration of retrieved memory with task execution produces superior, context-aware outputs com-
pared to the baseline’s generic approach.
Summary.


---
*Page 44*


These three cases demonstrate how AgeMem’s three-stage progressive training enables agents to de-
velop sophisticTahtise dis emxpeemrimoernyta ml HaTnMaL gtoe immpernovte s atcrcaetsesigbiileitsy.. CaWseh 1y showRse speolercttivBe asctko rtaoge aDndo wmnaloinatdenance
We invite you to report rendering errors. Learn more
of long-term knowledge through Add_memory, UpdateH_mTMemLo?ryIs, sauned DelAebtset_rmacetmoPrDy.F Case 2 illus-
about this project and help improve conversions.
trates proactive short-term context control under distraction via Filter_context and
Summary_context. Case 3 demonstrates the integration of these capabilities, where
Retrieve_memory enables the agent to access stored knowledge and coordinate memory systems to
solve tasks effectively. In each case, the RL-trained agent significantly outperforms the baseline by
learning when and how to apply memory tools, resulting in more focused, consistent, and personal-
ized interactions.
Appendix C Experimental Implementation
C.1 Dataset Details
We provide detailed statistics and characteristics of the five datasets used in our experiments:
ALFWorld (shridhar2020alfworld) is an embodied AI benchmark in which agents must complete
household tasks by following natural language instructions in a simulated environment. The dataset
consists of several thousand training environments and multiple validation and test splits, covering six
task types: pick and place, examine in light, clean and place, heat and place, cool and place, and pick
two and place. These tasks require long-horizon interaction with objects, making ALFWorld well suited
for evaluating planning and memory management capabilities.
SciWorld (wang2022scienceworld) is an interactive science experiment simulation environment where
agents must perform multi-step experiments to answer scientific questions. The benchmark includes
a diverse set of tasks spanning multiple scientific domains, such as physics, chemistry, and biology,
and emphasizes procedural reasoning and hypothesis-driven exploration. Its complexity makes it suit-
able for testing an agent’s ability to retain and retrieve relevant knowledge over extended interaction
sequences.
PDDL (chang2024agentboard) refers to a set of planning benchmarks formulated using the Planning
Domain Definition Language. These benchmarks evaluate an agent’s ability to solve symbolic planning
problems across multiple domains by generating valid sequences of actions that achieve specified
goal states. The tasks primarily test structured reasoning and the ability to maintain and utilize inter-
mediate planning states.
BabyAI (chevalier2018babyai) is a grid-world navigation benchmark with natural language instruc-
tions. The environment contains a large collection of instruction-following tasks (levels), where agents
must navigate and interact with objects to satisfy compositional language commands. Due to its se-
quential decision-making structure, BabyAI is commonly used to evaluate short-term context tracking
and instruction grounding.
HotpotQA (yang2018hotpotqa) is a multi-hop question answering dataset that requires reasoning
over multiple Wikipedia paragraphs. It contains approximately 90k training questions along with vali-
dation and test splits, and each question is annotated with supporting facts. This structure makes
HotpotQA particularly suitable for evaluating long-term memory storage and retrieval. In our experi-


---
*Page 45*


ments, we use HotpotQA for reinforcement learning training, as its annotated supporting facts natu-
rally provide stTrhuisc tisu erxepder icmoennttaelx HtTuMaLl tion ifmoprrmovae taicocnes fsoibril iStyt.ageW 1h syupervRiseiopno.rt Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
C.2 LLM-based Evaluation Details
For the Memory Quality (MQ) metric, we employ an LLM-based evaluator to assess the quality of sup-
porting facts stored in memory by comparing predicted supporting facts with ground-truth expected
facts. The evaluator uses the following prompt template:


---
*Page 46*


You are an expert judge evaluating the quality of supporting facts for question answering.
This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
Question: [QUESTION] HTML? Issue Abstract PDF
about this project and help improve conversions.
Answer: [ANSWER]
Ground Truth Supporting Facts (the facts that should be identified):
Expected Supporting Facts:
- [FACT_1]
- [FACT_2]
...
Model Predicted Supporting Facts (the facts identified by the model and stored in the long-term mem-
ory):
Predicted Supporting Facts:
- [PREDICTED_FACT_1]
- [PREDICTED_FACT_2]
...
Please evaluate how well the predicted supporting facts match the ground truth expected facts:
1. Are all expected facts covered by the predictions?
2. Are the predicted facts actually relevant to answering the question?
3. Are there any irrelevant facts in the predictions?
Score on a scale of 0.0 to 1.0:
- 1.0: Perfect match - all expected facts are correctly identified, no irrelevant facts
- 0.8-0.9: Mostly correct with minor omissions or one irrelevant fact
- 0.6-0.7: Partially correct - some relevant facts identified but missing important ones
- 0.4-0.5: Some correct elements but significant errors or omissions
- 0.2-0.3: Mostly incorrect with few correct elements
- 0.0-0.1: Completely incorrect or irrelevant
Respond with only a number between 0.0 and 1.0 (e.g., "0.85").
The evaluator compares the stored memory entries (predicted supporting facts) with the ground-truth
supporting facts provided in the HotpotQA dataset. The score reflects both the coverage of expected
facts and the relevance of predicted facts to the question. We use Qwen-Max as the evaluator model,
and each evaluation is performed independently to ensure consistency.
For the LLM-as-a-Judge metric on HotpotQA, we use a similar approach, where Qwen-Max evaluates
the correctness of the agent’s answer by comparing it with the ground-truth answer. The evaluator
uses the following prompt template:


---
*Page 47*


You are an expert judge evaluating the correctness of answers to questions.
This is experimental HTML to improve accessibility. Why Report Back to Download
Given the following information:
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
- Question: [QUabEoSuTtI tOhNis] project and help improve conversions.
- Ground-truth Answer: [GROUND_TRUTH]
- Agent’s Answer: [AGENT_ANSWER]
Please evaluate the generated answer on a scale of 0.0 to 1.0:
- 1.0: Perfect match or equivalent correct answer
- 0.8-0.9: Mostly correct with minor differences
- 0.6-0.7: Partially correct or close approximation
- 0.4-0.5: Some correct elements but significant errors
- 0.2-0.3: Mostly incorrect with few correct elements
- 0.0-0.1: Completely incorrect or irrelevant
Respond with only a number between 0.0 and 1.0 (e.g., "0.85").
C.3 Baseline Configurations
All baseline implementations follow their respective official open-source codebases to ensure fair
comparison. We provide the source links and implementation details below.
LangMem (langmem2025): We use the official implementation available at https://langchain-
ai.github.io/langmem/ with default hyperparameters. LangMem employs a modular memory
framework that supports multiple memory types. We configure it to use the default memory storage
and retrieval mechanisms as specified in the official documentation.
A-Mem (xu2025mem): We implement A-Mem following the Zettelkasten-inspired design described in
the original paper, using the official codebase at https://github.com/WujiangXu/A-mem-
sys/. The system links structured knowledge units to facilitate consolidation. We use the recom-
mended hyperparameters for memory consolidation as provided in the repository.
Mem0 (chhikara2025mem0): We use the official Mem0 implementation available at
https://github.com/mem0ai/mem0 with the default extract-update pipeline. For the graph-
based variant (Mem0g), we enable the graph structure option and use the recommended graph con-
struction parameters as specified in the official implementation.
AgeMem-noRL: This variant uses the same tool interface as AgeMem but without reinforcement
learning. This baseline helps isolate the contribution of RL training to the overall performance.
RAG variants: For the RAG-based baselines (AgeMem-noRL-RAG and AgeMem-RAG), we replace the
STM tools with a standard RAG pipeline that retrieves relevant memories at each step and appends
them to the context. The retrieval is performed using cosine similarity between the current context
and stored memories, following standard RAG practices. This comparison demonstrates the advan-
tage of learned STM management over static retrieval-based approaches.


---
*Page 48*


C.4 Implementation Details
This is experimental HTML to improve accessibility. Why Report Back to Download
Training confiWgue rinavtitieo ynou. tWo ree puosrte r etnhdeer iTnrgi enrirtoyrs .R LLe afrrna mmoreework (pan2025trinity) for policy optimization, im-
HTML? Issue Abstract PDF
about this project and help improve conversions.
plementing the step-wise GRPO algorithm as described in the method section. We use 𝐾 = 8 indepen-
dent rollouts per task for group normalization. The KL divergence coefficient 𝛽 is set to 0.1.
Reward weights. All reward weights are set to 1/3: 𝑤 = 𝑤 = 𝑤 = 1/3. This uniform
task context memory
weighting ensures that all components contribute equally to the learning signal, allowing the agent to
naturally balance task performance and memory management.
Model settings. The maximum context length is set to 8,192 tokens, and the maximum response
length is set to 2,048 tokens. When the context exceeds this limit, the agent receives a penalty, en-
couraging proactive use of STM management tools. All experiments are conducted on 8 NVIDIA RTX
4090 GPUs with 48GB memory each.
Appendix D Additional Results
D.1 Ablation Study
Figure 9:Ablation study results for Qwen3-4B-Instruct. Base: No-Memory baseline; +LT: AgeMem-
noRL-RAG (LTM tools only); +LT/RL: AgeMem-RAG (RL with LTM tools); +LT/ST/RL: AgeMem (full
AgeMem system with RL). Green arrows indicate performance gains over the baseline.
This section provides complementary ablation study results for Qwen3-4B-Instruct. Figure 9 shows
the progressive contribution of LTM, STM, and RL components on Qwen3-4B-Instruct across three
representative datasets. The results demonstrate consistent trends with Qwen2.5-7B-Instruct, validat-
ing the generalizability of our approach across different model sizes.
D.2 Reward Function Ablation on Qwen3-4B


---
*Page 49*


To validate the generalizability of our multi-component reward design across different model archi-
tectures and sTchaisl eiss e, xpweeri mceontnadl HuTcMt Lt tho eim spraomve ea ccreeswsiabirlidty .funWcthioyn ablRaetipoonr tstuBday caks t oin thDeo mwnaliona tdext on
We invite you to report rendering errors. Learn more
Qwen3-4B-Instruct. This section provides a complete anHaTlyMsiLs? parIsasllueel to thAeb Qstwraecnt2.5P-7DBF-Instruct re-
about this project and help improve conversions.
sults presented in the main paper.
D.2.1 Convergence Analysis
Figure 10:Training convergence curves on Qwen3-4B-Instruct comparing All-Returns (solid line) v.s.
Answer-Only (dashed line) reward strategies.
Figure 10 demonstrates the reward convergence patterns on Qwen3-4B-Instruct. Similar to Qwen2.5-
7B-Instruct, the All-Returns strategy consistently outperforms Answer-Only throughout the training
process. Several notable observations emerge:
More Stable Dynamics: The convergence curve shows noticeably smoother progression with lower
variance, particularly in the later training stages (steps 70-100). This stability suggests that Qwen3’s


---
*Page 50*


architecture may have better inductive biases for the reward learning task.
This is experimental HTML to improve accessibility. Why Report Back to Download
We invite you to report rendering errors. Learn more
HTML? Issue Abstract PDF
about this project and help improve conversions.
Consistent Superiority: While the absolute improvement is smaller than Qwen2.5-7B-Instruct, the
All-Returns strategy maintains its advantage throughout training, validating the robustness of our re-
ward design.
D.2.2 Quantitative Results
Table 5:Reward function ablation results on HotpotQA using Qwen3-4B-Instruct. All-Returns v.s.
Answer-Only reward strategies. “TN” is the token number, and “TC” denotes the number of tool calls.
Strategy J( ↑ ) TN( ↓ ) MQ( ↑ ) TC(-)
Answer-Only 0.546 2164 0.415 7.21
All-Returns 0.555 2191 0.605 8.67
Table 5 reports the reward ablation results on HotpotQA with Qwen3-4B-Instruct. Compared to the
Answer-Only strategy, the All-Returns reward consistently improves overall performance. In particu-
lar, it yields higher LLM-as-a-Judge scores (0.555 v.s. 0.546) and substantially better memory quality
(MQ: 0.605 v.s. 0.415), indicating that explicitly rewarding memory-related behaviors leads to more re-
liable memory organization. The All-Returns strategy also encourages more active tool usage (8.67
v.s. 7.21), suggesting that the agent learns to leverage memory operations more effectively when inter-
mediate returns are optimized. This improvement comes with only a marginal increase in token con-
sumption (2191 v.s. 2164), implying that the gains are not driven by excessive context expansion but by
more efficient memory utilization. Overall, these results show that incorporating memory-aware re-
wards significantly enhances both memory quality and task performance on Qwen3-4B-Instruct. The
observed trends are consistent with those obtained on Qwen2.5-7B-Instruct, confirming the robust-
ness of the reward design across different model backbones.
Report Issue for Selection