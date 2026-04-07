# Paper page - LatentMem_ Customizing Latent Memory for Multi-Agent Systems

*Converted from: Paper page - LatentMem_ Customizing Latent Memory for Multi-Agent Systems.PDF*



---
*Page 1*


Search models, datasets, users...
Papers arxiv:2602.03036
LatentMem: Customizing Latent Memory for
Multi-Agent Systems
Published on Feb 2 · Submitted by Xiaoye Qu on Feb 6
Upvote 14 +6
Authors: Muxin Fu, Guibin Zhang, Xiangyuan Xue, Yafu Li, Zefeng He, Siyuan Huang,
Xiaoye Qu, Yu Cheng, Yang Yang
Abstract
LatentMem is a learnable multi-agent memory framework that customizes agent-
specific memories through latent representations, improving performance in multi-
agent systems without modifying underlying frameworks.
AI-generated summary
Large language model (LLM)-powered multi-agent systems (MAS) demonstrate
remarkable collective intelligence, wherein multi-agent memory serves as a pivotal
mechanism for continual adaptation. However, existing multi-agent memory designs
remain constrained by two fundamental bottlenecks: (i) memory homogenization arising
from the absence of role-aware customization, and (ii) information overload induced by
excessively fine-grained memory entries. To address these limitations, we propose
LatentMem, a learnable multi-agent memory framework designed to customize agent-
specific memories in a token-efficient manner. Specifically, LatentMem comprises an
experience bank that stores raw interaction trajectories in a lightweight form, and a
memory composer that synthesizes compact latent memories conditioned on retrieved
experience and agent-specific contexts. Further, we introduce Latent Memory Policy
Optimization (LMPO), which propagates task-level optimization signals through latent
memories to the composer, encouraging it to produce compact and high-utility
Ask HuggingChat about this Paper
representations. Extensive experiments across diverse benchmarks and mainstream MAS


---
*Page 2*


frameworks show that LatentMem achieves a performance gain of up to 19.36% over
vanilla settings and consistently outperforms existing memory architectures, without
requiring any modifications to the underlying frameworks.
View arXiv page View PDF GitHub 27 Add to collection
Community
Xiaoye08 Paper submitter 5 days ago
LatentMem: Customizing Latent Memory for Multi-Agent Systems
Reply
avahal 4 days ago
👉
arXivLens breakdown of this paper
https://arxivlens.com/PaperView/Details/latentmem-customizing-latent-memory-for-
multi-agent-systems-5687-aea17e91
Executive Summary
Detailed Breakdown
Practical Applications
Reply
librarian-bot 4 days ago
This is an automated message from the Librarian Bot. I found the following papers similar
to this paper.
The following papers were recommended by the Semantic Scholar API
StackPlanner: A Centralized Hierarchical Multi-Agent System with Task-Experience
Memory Management (2026)
AMA: Adaptive Memory via Multi-Agent Collaboration (2026)


---
*Page 3*


MemEvolve: Meta-Evolution of Agent Memory Systems (2025)
E-mem: Multi-agent based Episodic Context Reconstruction for LLM Agent Memory
(2026)
MemBuilder: Reinforcing LLMs for Long-Term Memory Construction via Attributed
Dense Rewards (2026)
Fine-Mem: Fine-Grained Feedback Alignment for Long-Horizon Memory Management
(2026)
Implicit Graph, Explicit Retrieval: Towards Efficient and Interpretable Long-horizon
Memory for Large Language Models (2026)
Please give a thumbs up to this comment if you found it helpful!
If you want recommendations for any Paper on Hugging Face checkout this Space
You can directly ask Librarian Bot for paper recommendations by tagging it in a comment:
@librarian-bot recommend
Reply
Edit Preview
Start discussing about this paper
Tap or paste here to upload images
Comment
Sign up or log in to comment


---
*Page 4*


Models citing this paper 1
Kana-s/LatentMem-Qwen3-4B
Text Generation • Updated 4 days ago
Datasets citing this paper 0
No dataset linking this paper
Cite arxiv.org/abs/2602.03036 in a dataset README.md to link it from this page.
Spaces citing this paper 0
No Space linking this paper
Cite arxiv.org/abs/2602.03036 in a Space README.md to link it from this page.
Collections including this paper 4
Agent Collection
42 items • Updated 4 days ago • 3
Memory Collection
14 items • Updated 4 days ago • 3
Papers Collection
13 items • Updated 4 days ago


---
*Page 5*


Memory for Multi-Agent Systems Collection
1 item • Updated 3 days ago
System theme
Company
TOS
Privacy
About
Careers
Website
Models
Datasets
Spaces
Pricing
Docs