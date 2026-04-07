# Deep Reinforcement Learning_ Concepts, Optimization & Algorithms

*Converted from: Deep Reinforcement Learning_ Concepts, Optimization & Algorithms.pdf*



---
*Page 1*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
by Kuriko IWAI
Home > Research Archive > log #331
Deep Reinforcement Learning for Self-Evolving AI
Building self-learning systems
Machine Learning Data Science Python
By Kuriko IWAI
Table of Contents
Introduction
Deep Reinforcement Learning
Reinforcement Learning Part
Deep Learning Part
Addressing the Limitations of Traditional Reinforcement Learning
Use Cases
The Core of Optimization Problems in Reinforcement Learning
Fundamental Iteration Approaches for Solving MDPs
The Learning Process: How DRL Agents Interact and Learn
Step 1. Observe the state of environment
https://kuriko-iwai.com/deep-reinforcement-learning 1/27


---
*Page 2*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
Step 2. Select an action
Step 3. Receive a reward or penalty
Step 4. Update the policy
Tackling Exploration-Exploitation Dilemma
Epsilon-Greedy Strategy
2. Upper Confidence Bound (UCB)
3. Thompson Sampling
Major Categories of Deep Reinforcement Learning Algorithms
Model-Free RL
Model-Based RL
Simulation
Setting Up the Environment
Initializing the DQN Agent
Selecting an Action
Taking an action based on the state
Adding memory
Learning from the environment
Training DRL
Rule-Based Controller
Results
Wrapping Up
https://kuriko-iwai.com/deep-reinforcement-learning 2/27


---
*Page 3*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
Introduction
Deep Reinforcement Learning (DRL) are key component in AI, combining the principles of reinforcement
learning with the power of deep neural networks.
In this article, I’ll explore its core concepts and advantages with performance comparison of the DRL agent
and traditional method.
Deep Reinforcement Learning
Deep Reinforcement Learning (DRL) is a machine learning method that combines the concept of
Reinforcement Learning (RL) and Deep Learning (DL).
◼ Reinforcement Learning Part
Reinforcement Learning is a trial-and-error learning process where an agent learns to make sequential
decisions by interacting with an environment, receiving rewards based on its actions.
The agent's primary objective here is to learn a policy that maximizes its cumulative reward over time by
identifying the optimal action for each situation (state).
▫ KEY COMPONENTS
Traditional RL (and hence DRL) has key components:
Agent: A learner (deep neural network) that makes decisions
Environment: The world the agent interacts with
State: A snapshot of the environment at a particular moment
Action: A choice the agent makes based on the current state.
Policy: The agent's strategy and rules learned for choosing an action in a given state.
Reward: A feedback signal from the environment indicating the immediate consequence of the agent's
action in that state. This can be positive or negative.
For example, let us consider a self-driving car: its controller (the agent) interprets the road image (state)
and, guided by its learned policy, chooses to steer left (action). A smooth drive then yields a reward of 3.
The approach of RL is fundamentally different from other machine learning paradigms;
https://kuriko-iwai.com/deep-reinforcement-learning 3/27


---
*Page 4*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
Supervised Learning: Relies on predefined input-output pairs.
Unsupervised Learning: Seeks inherent structures in unlabeled data.
RL agent (and DRL agent): Continuously learns through direct interaction and feedback from the
environment.
◼ Deep Learning Part
The "Deep" in DRL implies the integration of Deep Learning techniques.
In DRL, the DRL agent is implemented as a multi-layered neural network, enabling it to process and learn
from highly complex and high-dimensional states, such as raw pixel data from images or intricate sensor
readings.
These "deep" neural networks excel at automatically learning patterns from raw data without explicit feature
engineering.
◼ Addressing the Limitations of Traditional Reinforcement Learning
Traditional RL faces significant limitations when applied to complex, real-world scenarios. DRL emerges as a
solution to overcome these challenges:
1. The Curse of Dimensionality & Handling Complex States:
Traditional RL: Struggles with complex and high-dimensional states. As the number of
states in an environment grows, the amount of memory and computation required to store
and update value functions exponentially increases, quickly becoming unfeasible (later
explain more in details).
DRL Solution: Utilizes DRL agents backed by deep neural networks. They can map high-
dimensional states to detailed context for making decisions.
2. Inability to Handle Raw Sensory Data & End-to-End Learning:
Traditional RL: Requires predefined, low-dimensional representations of the
environment. It cannot directly process raw sensory data (e.g., pixel data from a camera,
audio signals) without manual feature extraction or state discretization.
DRL Solution: Learns directly from raw sensory data without the need for manual feature
engineering. The deep neural networks automatically extract relevant features and
representations from this raw input, enabling the agent to learn complex behaviors from
the ground up. This end-to-end approach simplifies the design process and allows for
more nuanced learning.
3. Limited Generalization:
Traditional RL: Struggles to generalize their learning to unseen states, often requiring
explicit learning for every possible scenario.
DRL Solution: DLR agents leverage the generalization capabilities of deep neural
networks. They can apply learned knowledge to unseen states, making them more
https://kuriko-iwai.com/deep-reinforcement-learning 4/27


---
*Page 5*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
adaptable to real-world complexity.
Below diagram illustrates the key differences between DRL and traditional RL, highlighting how deep neural
networks enhance the agent's ability to perceive and act in sophisticated environments:
Kernel Labs | Kuriko IWAI | kuriko-iwai.com
Figure A. Comparison of DRL and traditional RL (Created by Kuriko IWAI)
In essence, DRL's use of deep neural networks as the agent allows it to process high-dimensional inputs,
learn complex mappings, and generalize effectively, addressing the core limitations of the traditional RL.
◼ Use Cases
DRL has revolutionized various domains due to its ability to handle complexity and learn autonomously. Its
use cases include:
Gaming: Achieving superhuman performance in strategic games (Go, Chess) and video games (Atari,
StarCraft II, Dota 2) by learning complex strategies through self-play.
Robotics: Enabling robots to perform intricate tasks like grasping, manipulation, locomotion, and
navigation in diverse and dynamic environments.
Autonomous Vehicles: Developing decision-making systems for self-driving cars, including path
planning, collision avoidance, and adaptive control in varied traffic conditions.
Finance: Optimizing algorithmic trading strategies, portfolio management, risk assessment, and fraud
detection by analyzing vast, real-time market data.
Healthcare: Personalizing treatment plans, assisting in medical diagnosis, optimizing drug discovery
processes, and enhancing robotic surgical procedures.
Energy Management: Optimizing energy consumption in large data centers and smart grids by
predicting usage patterns and managing power distribution.
The Core of Optimization Problems in Reinforcement Learning
https://kuriko-iwai.com/deep-reinforcement-learning 5/27


---
*Page 6*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
Among all different types of DRL algorithms (or RL in general), its optimization problem is to find an optimal
policy π∗ that can maximize the expected sum of discounted rewards by keep taking a “good“ action in each
state.
Mathematically, it is defined with these states S and actions A as conditions:
∞
π∗ = argm
π
ax E
∑
γkR t+k+1 ∣ S t = s,A t = π(S t )
k=0
discounted reward
where:
π∗ : The optimal policy that maximizes the expected cumulative discounted reward.
E[⋅] : The expected value (the average value over many possible discounted rewards).
γ_k : The discount factor γ at time k.
R_t+k+1 : The reward received at time step t+k+1.
S_t = s : Under the condition where the state at time t is s.
A_t = π(S_t) : Under the condition where the action at time t is determined by the policy π applied to
state S_t .
Take a look at key components.
The discount factor γ controls the discount rate of rewards. The reward at time step t is discounted by a
factor of γ^t . Since the discount factor ranges from zero to less than one:
γ ∈ [0,1)
to make the discounted reward large, the algorithm is strongly incentivized to accrue positive rewards as
soon as possible and postpone negative rewards as long as possible.
This is a similar concept to the interest rate in economic applications where a dollar today is worth more than
a dollar tomorrow.
A policy π denotes any function that can map states to actions:
π : S ↦ A
When the algorithm executes a policy π, it takes an action a such that:
a = π(s) s ∈ S,a ∈ A
Given that the policy represents actions, the expected sum of the discounted rewards is dictated by the state
and policy:
Vπ (s) = E[R(s
0
)+γR(s
1
)+γ2R(s
2
)+⋯ ∣ s
0
= s,π]⋯(1)
where Vπ(s) is a value function that represents expected total of the discount rewards.
Using the value function, the optimization problem is redefined:
π∗ = argmaxVπ (s)
π
https://kuriko-iwai.com/deep-reinforcement-learning 6/27


---
*Page 7*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
Mathematical process of the continuous iteration from the time step zero to t looks like:
Kernel Labs | Kuriko IWAI | kuriko-iwai.com
Figure B. Mathematical application of DRL (Created by Kuriko IWAI)
▫ TRANSITION PROBABILITY AND BELLMAN OPTIMALITY EQUATION
The Bellman Optimality Equation is a recursive relationship in RL that characterizes the optimal value
function for an MDP.
It states that the optimal value of a state (or state-action pair) under an optimal policy is equal to the
immediate reward plus the discounted optimal value of the next state:
Vπ (s) = R(s)immediate reward +γ s′ ∈ SP (s′)Vπ (s′) ⋯(2)
∑ sπ(s)
where:
P_sπ(s') : The transition probability that represents the probability of transitioning from state s to
state s’ when taking action a.
s' : The next state following to the state s.
The transition probability represents the probability of transitioning from state s to state s’ when taking
action a. In other words, P_s π(s’) answers the question:
“If I'm in state s and I choose to take action a, what is the probability that I will end up in state s’?”
Leveraging the concept, the value function also represents the expected long-term return (e.g., total
accumulated reward) that can be achieved starting from state s′ and then following an optimal policy from
that point onwards.
https://kuriko-iwai.com/deep-reinforcement-learning 7/27


---
*Page 8*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
◼ Fundamental Iteration Approaches for Solving MDPs
There are two efficient algorithms for solving the optimization problem of DRL: 1) Policy Iteration and 2) Value
Iteration.
▫ 1) POLICY ITERATION
Policy iteration is a method that directly optimizes a parameterized policy to maximize expected discount
rewards. The algorithm first:
1. Initialize a policy π randomly, and then
2. Repeat until convergence:
V : = Vπ
π(s) := argmax P (s′)V(s′) ⋯(3)
sa
a∈A
∑
s′
where:
π(s) : The policy at state s (or an action at time step s).
P_sa (s') : The transition probability.
V(s') : The value function (or state-value function) of state s′.
The initial reward R(s) and discount factor γ in the formula (2) are omitted from the objective function formula
(3) because both are constant with respect to an action a.
Key characteristics of Policy Iteration include:
Explicitly maintains a policy: It directly works with and updates the policy.
Guaranteed to converge: Each policy improvement step guarantees a strictly better or equal policy,
and since there's a finite number of policies, it will converge to the optimal one.
Policy evaluation can be computationally expensive: Solving the system of linear equations for
value evaluation can be slow, especially for large state spaces. However, it often converges in fewer
iterations of the overall policy iteration loop than the value iteration.
▫ 2) VALUE ITERATION
Value iteration on the other hand, optimizes the value function first and then compute the optimal policy. Until
converge, the algorithm leverages the formula (2) to find the optimal value function:
V(s) := R(s)+maxγ P (s′)V(s′)
sa
a∈A ∑
s′
This update is applied repeatedly for all states until the value function converges.
Once V∗(s) is obtained, the optimal policy π∗(s) is derived by choosing the action a that maximizes the
expected return for each state s:
https://kuriko-iwai.com/deep-reinforcement-learning 8/27


---
*Page 9*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
π∗ = argmaxVπ (s)
π
Key characteristics of Value Iteration include:
Directly computes optimal value function: It focuses on finding V∗(s) first, and then the policy is a
byproduct.
Combines evaluation and improvement: Each iteration of Value Iteration implicitly performs a one-
step policy evaluation and improvement simultaneously by taking the max over actions a.
Simpler to implement: The single update rule is generally easier to code.
May require more iterations: It often takes more iterations to converge to the optimal value function
compared to Policy Iteration, but each iteration is computationally cheaper since it doesn't involve
solving a system of linear equations.
▫ COMPARISON OF POLICY ITERATION AND VALUE ITERATION
The below table shows basic comparison of policy iteration and value iteration:
Kernel Labs | Kuriko IWAI | kuriko-iwai.com
Figure C. Comparison of Policy Iteration and Value Iteration (Created by Kuriko IWAI)
The choice between Policy Iteration and Value Iteration often depends on the complexity of the MDP.
For small, tabular MDPs, Policy Iteration can feel more intuitive because it directly manages and improves
the policy.
However, when dealing with larger tabular MDPs, Value Iteration often becomes the preferred method. Its
simpler per-iteration cost makes it more efficient in these expanded scenarios.
https://kuriko-iwai.com/deep-reinforcement-learning 9/27


---
*Page 10*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
In DRL, where state and action spaces are typically continuous or extremely high-dimensional, classical
Policy Iteration or Value Iteration are not applied in their pure, tabular forms.
Instead, DRL adapts their fundamental principles of iterative improvement for values or policies by integrating
deep neural networks into the system. As we discussed in the previous section, these networks enable the
algorithms to handle the immense complexity of real-world problems.
The Learning Process: How DRL Agents Interact and Learn
With the optimal problem and core mathematical approaches being defined, the DRL agents (deep neural
networks) implement the algorithm to solve the optimal problem, interacting with an environment in a DRL
system.
As we saw in the previous section, this interaction forms a continuous learning loop until the convergence.
The DRL agent's primary function is to learn an optimal policy—a strategy that dictates the best action to take
in any given state to maximize cumulative reward.
This learning process is iterative and experience-driven. Specifically, at each time step, the agent:
◼ Step 1. Observe the state of environment
The agent receives a representation of the current situation from the environment (state) as a numerical
vector or a high-dimensional input like an image, and feed it to the deep neural network.
◼ Step 2. Select an action
Utilizing its deep neural network, the agent processes the observed state and, based on its current policy
(which is encoded within the network's weights), chooses an action.
Exploration-exploitation strategies are employed to balance trying new actions (exploration) with
leveraging known good actions (exploitation).
◼ Step 3. Receive a reward or penalty
After executing an action, the environment provides feedback in the form of a scalar reward signal.
A positive reward indicates a desirable outcome, while a negative reward (penalty) indicates an undesirable
one.
This reward signal is the primary driver of the learning process, informing the agent whether its chosen
action moved it closer to or further from the desired objective.
https://kuriko-iwai.com/deep-reinforcement-learning 10/27


---
*Page 11*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
◼ Step 4. Update the policy
The received reward and the transition from the previous state to the new state along with the action taken
make an experience tuple.
This experience is used to update the parameters (weights and biases) of the deep neural network.
◼ Tackling Exploration-Exploitation Dilemma
Exploration-Exploitation dilemma refers to the fundamental challenge an autonomous agent faces in deciding
whether to:
Exploit its current knowledge to choose actions that are believed to yield the highest immediate reward.
Explore the environment by trying new, potentially suboptimal actions to gather more information, which
could lead to discovering better long-term strategies and higher cumulative rewards.
This dilemma is crucial because an agent needs to learn about its environment (exploration) to find optimal
policies, but also needs to leverage what it has learned (exploitation) to maximize its performance.
An overemphasis on exploitation might lead the agent to get stuck in a sub-optimal local optimum, while
excessive exploration can lead to inefficient learning and poor performance by trying too many ineffective
actions.
To tackle this challenge, here are three major exploration-exploitation strategies used in DRL, along with their
mathematical formulations:
◼ Epsilon-Greedy Strategy
The epsilon-greedy (ϵ-greedy) strategy is one of the simplest and most widely used methods.
It balances exploration and exploitation by selecting a random action with a small probability ϵ (exploration)
and choosing the action with the highest estimated Q-value (greedy action) with probability 1−ϵ
(exploitation).
Mathematical Formulation
Let Q(s, a) be the estimated value (e.g., Q-value) of taking action a in state s.
This value represents the expected long-term reward if the agent takes action a in state s and then follows an
optimal policy afterward.
The action selection rule for ϵ-greedy is to choose the action such that:
1 −ϵ + ϵ if a = argmaxa′ ∈ A(s)Q(s,a′)⋯ when action a’ has max. Q value
P(a ∣ s) = ∣A(s)∣
{ ϵ if a = argmaxa′ ∈ A(s)Q(s,a′)
∣A(s)∣
Where:
https://kuriko-iwai.com/deep-reinforcement-learning 11/27


---
*Page 12*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
P(a|s) : The probability of choosing action a given state s.
ϵ : The exploration probability (a value between 0 and 1).
A(s) : The set of all possible actions in state s.
|A(s)| : The number of all possible actions in state s.
Exploitation Part (1 - ϵ)
a = argmax Q(s, a') denotes the action a′ that has the maximum estimated Q-value in state s.
In such case, with the probability 1−ϵ, the agent chooses the "greedy" action.
The greedy action is the one that currently has the highest estimated Q-value for the current state s.
This is the exploitation part, where the agent leverages its current knowledge to maximize immediate reward.
Exploration Part (ϵ)
With probability ϵ, the agent chooses an action randomly from all available actions in state s. This includes
the greedy action itself.
Since there are |A(s)| possible actions in the state s, each action (including the greedy one) has a probability
of 1 / |A(s)| of being chosen if a random action is selected.
So, the probability of any non-greedy action being chosen is simply ϵ / |A(s)|, which is defined in the second
line of the formula.
Decaying ϵ
A common practice in the ϵ-greedy strategy is to use a decaying ϵ, where ϵ starts high to encourage
exploration early in training and gradually decreases over time to favor exploitation as the agent learns more
about the optimal policy. For example,
ϵ = ϵ +(ϵ −ϵ )e−λt
t min max min
where λ is a decay rate.
Applicable DRL Algorithms:
DQN (Deep Q-Network)
Double DQN (DDQN)
C51
QR-DQN
HER (Hindsight Experience Replay) (often combined with algorithms like DQN)
◼ 2. Upper Confidence Bound (UCB)
UCB is an optimistic exploration strategy that prioritizes actions based on both their estimated value and the
uncertainty around that estimate.
https://kuriko-iwai.com/deep-reinforcement-learning 12/27


---
*Page 13*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
It operates on the principle of optimism in the face of uncertainty, meaning it prefers actions that have
been less explored but have the potential for high rewards.
Mathematical Formulation
For each action a in a given state s, the UCB value is calculated as:
InN
t
USB(s,a) = Q(s,a)+ c
N(s,a)
exploration bonus
Where:
Q(s, a) : The current estimated value (e.g., Q-value) of taking action a in state s.
N_t : The total number of times any action has been taken up to time t (or the number of times state s
has been visited, or a similar global count).
N(s, a) : The number of times action a has been taken in state s.
c>0 : An exploration parameter that controls the degree of exploration. A higher c encourages more
exploration.
The second term acts as an exploration bonus.
Actions that have been taken fewer times (small N(s, a)) will have a larger bonus, encouraging exploration of
less-visited state-action pairs.
And as an action is explored more, N(s, a) increases, and its exploration bonus decreases.
Applicable DRL Algorithms:
AlphaZero: Heavily relies on Monte Carlo Tree Search (MCTS), which uses a variant of UCB to guide its
node selection, balancing exploration of less-visited nodes with exploitation of promising ones.
◼ 3. Thompson Sampling
Thompson Sampling is a Bayesian approach to the exploration-exploitation dilemma.
Instead of directly calculating an exploration bonus, it maintains a probability distribution over the value of
each action.
At each step, it samples a value for each action from its respective posterior distribution and then chooses
the action with the highest sampled value.
Mathematical Formulation:
Let us consider a case where a prior distribution over the true mean reward of each action is Bernoulli.
For each action a, define parameters of a uniform prior:
α = 1 , β = 1
a a
https://kuriko-iwai.com/deep-reinforcement-learning 13/27


---
*Page 14*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
where α_a / β_a represents the number of success / failure actions respectively.
At each time step t:
1. Sample from Posterior: For each action a, draw a sample θ_a from its posterior Beta distribution:
θ ∼ Beta(α ,β )
a a a
The sampled θ_a represents a plausible true reward probability for action a.
2. Select Action: Choose the optimal action a^∗ that maximizes the sampled value:
a∗ = argmaxθ
a
3. Execute Action and Observe Reward: Execute the optimal action in the environment and observe the
reward R ∈ {0, 1}.
4. Update Parameters: Update the parameters for the optimal action based on the observed reward:
(1)
α∗ ← α∗ +1 if R = 1 (2)
a a
(3)
β∗ ← β∗ +1 if R = 0
a a
Applicable DRL Algorithms:
SAC (Soft Actor-Critic): Conceptually aligning with the probabilistic sampling nature of Thompson
Sampling.
World Models: Learning an accurate model of the environment often involves quantifying the
uncertainty in the model's predictions.
This continuous cycle of observation, action, reward, and policy update allows the DRL agent to
progressively learn complex behaviors and solve the optimal problem in dynamic environments without
explicit programming for every possible scenario.
In the next section, I’ll detail major DRL algorithms to define the rules.
Major Categories of Deep Reinforcement Learning Algorithms
D/RL algorithms are the specific sets of rules with computational methods that agents use to learn how to
make optimal decisions in an environment.
These algorithms define:
How the agent perceives its environment: How it takes in observations or states.
How it selects actions: Based on its current understanding and goals.
How it updates its knowledge: Using the rewards (or penalties) it receives from the environment to
improve its future decision-making.
https://kuriko-iwai.com/deep-reinforcement-learning 14/27


---
*Page 15*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
Different algorithms have different strengths and weaknesses, making them suitable for various types of
problems and environments.
The below diagram shows categories of the algorithms. At the highest level, RL algorithms fall into two main
paradigms: Model-Free RL and Model-Based RL. Then, these are further categorized by data acquisition
type: Online RL (policy-based), Off-policy RL (value-based), and Offline RL.
Kernel Labs | Kuriko IWAI | kuriko-iwai.com
Figure D. Categorizing D/RL algorithms (Created by Kuriko IWAI)
◼ Model-Free RL
Model-Free RL algorithms learn optimal policies or value functions directly from interactions with the
environment, without explicitly building a model of the environment's dynamics.
The category is further split into:
▫ ONLINE RL (POLICY OPTIMIZATION)
These methods directly optimize a parameterized policy to maximize expected returns.
Examples include Policy Gradient, A2C/A3C, PPO (Proximal Policy Optimization), and TRPO (Trust Region
Policy Optimization).
Best when:
Continuous or High-Dimensional Action Spaces: Essential when the agent’s actions are not discrete
choices (like pressing a button) but rather continuous values (like steering angles).
https://kuriko-iwai.com/deep-reinforcement-learning 15/27


---
*Page 16*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
Learning Stochastic (Random) Policies: When the agent needs to take probabilistic behavior (e.g.,
sometimes turn left, sometimes turn right, with certain probabilities), rather than always performing the
same action deterministically, this method’s inherent randomness is beneficial.
Stable Training: Compared to some pure value-based methods, this method tends to be more stable
during training because they directly optimize the policy, incorporating mechanisms to constrain policy
updates.
▫ OFF-POLICY RL (Q-LEARNING)
These algorithms learn an action-value function (Q-function) that estimates the expected return of taking a
certain action in a given state.
Prominent examples include DQN (Deep Q-Network), C51, QR-DQN (Quantile Regression DQN), and HER
(Hindsight Experience Replay).
Best when:
Discrete State and Action Spaces: Works well when the number of states and actions is relatively
small and can be easily enumerated.
Model-Free Learning: No mathematical model of the environment's dynamics and its reward structure
available at hand.
Off-Policy Learning: Learn the optimal policy efficiently by leveraging all experiences, even those from
exploratory actions.
▫ OFFLINE RL
This approach utilizes a fixed, pre-collected dataset of transitions (states, actions, rewards, next states) to
learn a policy.
Crucially, the agent does not interact with the environment during the learning process. It learns entirely
from data that was generated by a different (often unknown) policy.
Best when:
Interacting with the real environment is expensive, dangerous, or impractical. This is often the
case in robotics, healthcare, or autonomous driving, where trial-and-error in the real world could lead to
damage or harm.
Large datasets of past interactions are readily available. For instance, logs from previous system
operations, user interactions, or simulations.
Safety and stability during deployment are paramount. Since the policy is learned from static data,
there's less risk of exploring dangerous or suboptimal actions during training in a live environment.
Reproducibility is important. The fixed dataset ensures that experiments can be replicated precisely.
◼ Model-Based RL
https://kuriko-iwai.com/deep-reinforcement-learning 16/27


---
*Page 17*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
Model-Based RL algorithms, on the other hand, attempt to learn or are given a model of the environment's
dynamics (a transition function P(s′ | s, a) and a reward function R(s, a, s′)). This model is then used for
planning or to improve policy learning.
This category is subdivided into:
▫ GIVEN ENVIRONMENT DYNAMICS
In this scenario, the environment is already known or provided, allowing the agent to use it for planning and
decision-making.
Best when: A highly accurate model of the environment is available or can be precisely defined like games
with fixed rules like chess or Go.
This enables robust planning and can lead to very efficient learning and strong performance.
AlphaZero is a notable example, which leverages a planning algorithm (Monte Carlo Tree Search) with a
learned value and policy network.
▫ UNKNOWN ENVIRONMENT DYNAMICS
This approach focuses on trying to learn an unknown model of the environment's dynamics.
Best when: The environment dynamics are unknown but can be learned from data.
The approach is highly sample-efficient as it can generate synthetic experiences for training, reducing the
need for costly real-world interactions. So, it is useful for safety-critical applications where simulating risks is
crucial like designing and testing the aircraft engine.
Algorithm examples include World Models, I2A (Imagination-Augmented Agents), MBMF (Model-Based Model-
Free), and MBVE (Model-Based Value Expansion).
Simulation
I’ll demonstrate the performance of a foundational DRL algorithm, DQN, and a traditional rule-based
controller for comparison, using the CartPole-v1 environment from Gymnasium due to its simplicity.
◼ Setting Up the Environment
First, set up the environment.
11 iimmppoorrtt ggyymmnnaassiiuumm aass ggyymm
22
33 eennvv__nnaammee == ""CCaarrttPPoollee--vv11""
44 eennvv == ggyymm..mmaakkee((eennvv__nnaammee))
https://kuriko-iwai.com/deep-reinforcement-learning 17/27


---
*Page 18*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
55
66 ssttaattee__ssiizzee == eennvv..oobbsseerrvvaattiioonn__ssppaaccee..sshhaappee[[00]]
77 aaccttiioonn__ssiizzee == eennvv..aaccttiioonn__ssppaaccee..nn
88
◼ Initializing the DQN Agent
Initialize the DQNAgent class with state, action, discount factor for rewards, batch size, and loss function
(MSE):
11 iimmppoorrtt ttoorrcchh..nnnn aass nnnn
22
33 ccllaassss DDQQNNAAggeenntt::
44 ddeeff ____iinniitt____((
55 sseellff,,
66 ssttaattee__ssiizzee,,
77 aaccttiioonn__ssiizzee,,
88 ggaammmmaa==00..9999,,
99 bbaattcchh__ssiizzee==6644
1100 ))::
1111 sseellff..ssttaattee__ssiizzee == ssttaattee__ssiizzee
1122 sseellff..aaccttiioonn__ssiizzee == aaccttiioonn__ssiizzee
1133 sseellff..ggaammmmaa == ggaammmmaa ## ddiissccoouunntt ffaaccttoorr ffoorr ffuuttuurree rreewwaarrddss
1144 sseellff..bbaattcchh__ssiizzee == bbaattcchh__ssiizzee ## ttrraaiinniinngg mmiinnii--bbaattcchh ssiizzee
1155 sseellff..ccrriitteerriioonn == nnnn..MMSSEELLoossss(()) ## lloossss ffuunnccttiioonn ((MMSSEE))
1166
◼ Selecting an Action
This step involves implementing the Q-network's forward pass and the epsilon-greedy strategy.
First, define the Policy class as a neural network. Then, within the DQNAgent class, add the select_action
function to choose an action with the maximum Q-value for exploitation, or a random action for exploration.
11 iimmppoorrtt ttoorrcchh
22 iimmppoorrtt ttoorrcchh..nnnn aass nnnn
33 iimmppoorrtt rraannddoomm
44
55 ## ddeeffiinnee ppoolliiccyy nneettwwoorrkk
66 ccllaassss PPoolliiccyy((nnnn..MMoodduullee))::
77 ddeeff ____iinniitt____((sseellff,, ssttaattee__ssiizzee,, aaccttiioonn__ssiizzee))::
88 ssuuppeerr((PPoolliiccyy,, sseellff))..____iinniitt____(())
99 sseellff..ffcc11 == nnnn..LLiinneeaarr((ssttaattee__ssiizzee,, 112288)) ## ffiirrsstt ffuullllyy ccoonnnneecctteedd llaayyeerr
1100 sseellff..rreelluu == nnnn..RReeLLUU(()) ## RReeLLUU aaccttiivvaattiioonn ffuunnccttiioonn
1111 sseellff..ffcc22 == nnnn..LLiinneeaarr((112288,, 112288)) ## sseeccoonndd ffuullllyy ccoonnnneecctteedd llaayyeerr
1122 sseellff..ffcc33 == nnnn..LLiinneeaarr((112288,, aaccttiioonn__ssiizzee)) ## oouuttppuutt llaayyeerr:: qq--vvaalluueess ffoorr eeaacchh aaccttiioonn
1133
1144 ddeeff ffoorrwwaarrdd__ppaassss((sseellff,, xx)):: ## ddeeffiinneess ffoorrwwaarrdd ppaassss ooff tthhee ppoolliiccyy
1155 xx == sseellff..rreelluu((sseellff..ffcc11((xx))))
1166 xx == sseellff..rreelluu((sseellff..ffcc22((xx))))
1177 rreettuurrnn sseellff..ffcc33((xx))
https://kuriko-iwai.com/deep-reinforcement-learning 18/27


---
*Page 19*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
1188
1199
2200 ## uuppddaattee ddqqnn aaggeenntt
2211 ccllaassss DDQQNNAAggeenntt::
2222 ddeeff ____iinniitt____((
2233 sseellff,,
2244 ssttaattee__ssiizzee,,
2255 aaccttiioonn__ssiizzee,,
2266 ggaammmmaa==00..9999,,
2277 bbaattcchh__ssiizzee==6644,,
2288 eeppssiilloonn__ssttaarrtt==11..00,,
2299 ))::
3300 sseellff..ssttaattee__ssiizzee == ssttaattee__ssiizzee
3311 sseellff..aaccttiioonn__ssiizzee == aaccttiioonn__ssiizzee
3322 sseellff..ggaammmmaa == ggaammmmaa ## ddiissccoouunntt ffaaccttoorr ffoorr ffuuttuurree rreewwaarrddss
3333 sseellff..bbaattcchh__ssiizzee == bbaattcchh__ssiizzee ## ttrraaiinniinngg mmiinnii--bbaattcchh ssiizzee
3344 sseellff..ccrriitteerriioonn == nnnn..MMSSEELLoossss(())
3355
3366 ## aaddddiinngg
3377 sseellff..eeppssiilloonn == eeppssiilloonn__ssttaarrtt ## iinniittiiaall eexxpplloorraattiioonn rraattee
3388 sseellff..ppoolliiccyy__nneett == PPoolliiccyy((ssttaattee__ssiizzee,, aaccttiioonn__ssiizzee)) ## aaddddiinngg ppoolliiccyy nneett
3399
4400
4411 ddeeff sseelleecctt__aaccttiioonn((sseellff,, ssttaattee)):: ## eeppssiilloonn--ggrreeeeddyy ttoo sseelleecctt aann aaccttiioonn
4422 iiff rraannddoomm..rraannddoomm(()) << sseellff..eeppssiilloonn:: ## cchhoooossee aa rraannddoomm aaccttiioonn ((eexxpplloorraattiioonn)) ww
4433 rreettuurrnn rraannddoomm..rraannddrraannggee((sseellff..aaccttiioonn__ssiizzee))
4444 eellssee:: ## cchhoooossee aann aaccttiioonn wwiitthh mmaaxx.. qq--vvaalluuee ((eexx
4455 ssttaattee == ttoorrcchh..FFllooaattTTeennssoorr((ssttaattee))..uunnssqquueeeezzee((00)) ## ccoonnvveerrtt ssttaattee ttoo ppyyttoorrcchh tteennssoorr
4466 wwiitthh ttoorrcchh..nnoo__ggrraadd(())::
4477 qq__vvaalluueess == sseellff..ppoolliiccyy__nneett((ssttaattee))
4488 rreettuurrnn ttoorrcchh..aarrggmmaaxx((qq__vvaalluueess))..iitteemm(())
4499
◼ Taking an action based on the state
11 aaggeenntt == DDQQNNAAggeenntt((ssttaattee__ssiizzee,, aaccttiioonn__ssiizzee))
22
33 ## ssttaattee ffrroomm tthhee eennvviirroonnmmeenntt
44 ssttaattee,, __ == eennvv..rreesseett(())
55
66 ## sseelleecctt aann aaccttiioonn bbaasseedd oonn tthhee ssttaattee
77 aaccttiioonn == aaggeenntt..sseelleecctt__aaccttiioonn((ssttaattee))
88
99 ## rreecceeiivvee nneexxtt ssttaattee,, rreewwaarrdd
1100 nneexxtt__ssttaattee,, rreewwaarrdd,, ddoonnee,, ttrruunnccaatteedd,, __ == eennvv..sstteepp((aaccttiioonn))
1111
 
◼ Adding memory
Although this is optional, I added memory to the DQN agent to store experiences (state, action, reward,
next_state, done) and allow sampling mini-batches randomly.
https://kuriko-iwai.com/deep-reinforcement-learning 19/27


---
*Page 20*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
This randomness can break correlations in the training data and stabilizes the learning process.
11 iimmppoorrtt ttoorrcchh
22 iimmppoorrtt ttoorrcchh..nnnn aass nnnn
33 iimmppoorrtt rraannddoomm
44 ffrroomm ccoolllleeccttiioonnss iimmppoorrtt ddeeqquuee
55
66 ## ddeeffiinneess mmeemmoorryy
77 ccllaassss RReeppllaayyBBuuffffeerr::
88 ddeeff ____iinniitt____((sseellff,, ccaappaacciittyy))::
99 sseellff..bbuuffffeerr == ddeeqquuee((mmaaxxlleenn==ccaappaacciittyy))
1100
1111 ddeeff ppuusshh((sseellff,, ssttaattee,, aaccttiioonn,, rreewwaarrdd,, nneexxtt__ssttaattee,, ddoonnee))::
1122 eexxppeerriieennccee == ((ssttaattee,, aaccttiioonn,, rreewwaarrdd,, nneexxtt__ssttaattee,, ddoonnee))
1133 sseellff..bbuuffffeerr..aappppeenndd((eexxppeerriieennccee)) ## aadddd aann eexxppeerriieennccee ttuuppllee ttoo tthhee bbuuffffeerr
1144
1155 ddeeff ssaammppllee((sseellff,, bbaattcchh__ssiizzee))::
1166 rreettuurrnn rraannddoomm..ssaammppllee((sseellff..bbuuffffeerr,, bbaattcchh__ssiizzee)) ## rraannddoommllyy ssaammppllee aa bbaattcchh ooff eexxppeerriieenncceess ffrroomm
1177
1188 ddeeff ____lleenn____((sseellff))::
1199 rreettuurrnn lleenn((sseellff..bbuuffffeerr))
2200
2211
2222 ccllaassss DDQQNNAAggeenntt::
2233 ddeeff ____iinniitt____((
2244 sseellff,,
2255 ssttaattee__ssiizzee,,
2266 aaccttiioonn__ssiizzee,,
2277 ggaammmmaa==00..9999,,
2288 bbaattcchh__ssiizzee==6644,,
2299 eeppssiilloonn__ssttaarrtt==11..00,,
3300 rreeppllaayy__bbuuffffeerr__ccaappaacciittyy==1100000000,,
3311 ))::
3322 sseellff..ssttaattee__ssiizzee == ssttaattee__ssiizzee
3333 sseellff..aaccttiioonn__ssiizzee == aaccttiioonn__ssiizzee
3344 sseellff..ggaammmmaa == ggaammmmaa
3355 sseellff..bbaattcchh__ssiizzee == bbaattcchh__ssiizzee
3366 sseellff..ccrriitteerriioonn == nnnn..MMSSEELLoossss(())
3377 sseellff..eeppssiilloonn == eeppssiilloonn__ssttaarrtt
3388 sseellff..ppoolliiccyy__nneett == PPoolliiccyy((ssttaattee__ssiizzee,, aaccttiioonn__ssiizzee))
3399
4400 ## aaddddeedd
4411 sseellff..mmeemmoorryy == RReeppllaayyBBuuffffeerr((rreeppllaayy__bbuuffffeerr__ccaappaacciittyy))
4422
4433
4444 ddeeff sseelleecctt__aaccttiioonn((sseellff,, ssttaattee))::
4455 iiff rraannddoomm..rraannddoomm(()) << sseellff..eeppssiilloonn::
4466 rreettuurrnn rraannddoomm..rraannddrraannggee((sseellff..aaccttiioonn__ssiizzee))
4477 eellssee::
4488 ssttaattee == ttoorrcchh..FFllooaattTTeennssoorr((ssttaattee))..uunnssqquueeeezzee((00))
4499 wwiitthh ttoorrcchh..nnoo__ggrraadd(())::
5500 qq__vvaalluueess == sseellff..ppoolliiccyy__nneett((ssttaattee))
5511 rreettuurrnn ttoorrcchh..aarrggmmaaxx((qq__vvaalluueess))..iitteemm(())
5522
 
https://kuriko-iwai.com/deep-reinforcement-learning 20/27


---
*Page 21*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
◼ Learning from the environment
Lastly, define the learn function and relevant variables in the DQNAgent class.
11 iimmppoorrtt ttoorrcchh
22 iimmppoorrtt ttoorrcchh..nnnn aass nnnn
33 iimmppoorrtt ttoorrcchh..ooppttiimm aass ooppttiimm
44 iimmppoorrtt rraannddoomm
55
66
77 ccllaassss DDQQNNAAggeenntt::
88 ddeeff ____iinniitt____((
99 sseellff,,
1100 ssttaattee__ssiizzee,,
1111 aaccttiioonn__ssiizzee,,
1122 ggaammmmaa==00..9999,,
1133 bbaattcchh__ssiizzee==6644,,
1144 eeppssiilloonn__ssttaarrtt==11..00,,
1155 rreeppllaayy__bbuuffffeerr__ccaappaacciittyy==1100000000,,
1166 lleeaarrnniinngg__rraattee==00..000011,,
1177 eeppssiilloonn__eenndd==00..0011,,
1188 eeppssiilloonn__ddeeccaayy==00..999955,,
1199 ))::
2200 sseellff..ssttaattee__ssiizzee == ssttaattee__ssiizzee
2211 sseellff..aaccttiioonn__ssiizzee == aaccttiioonn__ssiizzee
2222 sseellff..ggaammmmaa == ggaammmmaa
2233 sseellff..bbaattcchh__ssiizzee == bbaattcchh__ssiizzee
2244 sseellff..ccrriitteerriioonn == nnnn..MMSSEELLoossss(())
2255 sseellff..eeppssiilloonn == eeppssiilloonn__ssttaarrtt
2266 sseellff..ppoolliiccyy__nneett == PPoolliiccyy((ssttaattee__ssiizzee,, aaccttiioonn__ssiizzee))
2277 sseellff..mmeemmoorryy == RReeppllaayyBBuuffffeerr((rreeppllaayy__bbuuffffeerr__ccaappaacciittyy))
2288
2299 ## aaddddiinngg ttaarrggeett nneett ffoorr lleeaarrnniinngg ((uuppddaattiinngg qq vvaallss))
3300 sseellff..ttaarrggeett__nneett == PPoolliiccyy((ssttaattee__ssiizzee,, aaccttiioonn__ssiizzee))
3311
3322 ## aaddddiinngg ooppttiimmiizzeerr ttoo uuppddaattee tthhee ppoolliiccyy
3333 sseellff..ooppttiimmiizzeerr == ooppttiimm..AAddaamm((sseellff..ppoolliiccyy__nneett..ppaarraammeetteerrss(()),, llrr==lleeaarrnniinngg__rraattee))
3344
3355 ## aaddddiinngg eepplliissoonn ddeeccaayy
3366 sseellff..eeppssiilloonn__eenndd == eeppssiilloonn__eenndd ## mmiinniimmuumm eexxpplloorraattiioonn rraattee
3377 sseellff..eeppssiilloonn__ddeeccaayy == eeppssiilloonn__ddeeccaayy ## eeppssiilloonn ddeeccaayy rraattee
3388
3399
4400 ddeeff sseelleecctt__aaccttiioonn((sseellff,, ssttaattee))::
4411 iiff rraannddoomm..rraannddoomm(()) << sseellff..eeppssiilloonn::
4422 rreettuurrnn rraannddoomm..rraannddrraannggee((sseellff..aaccttiioonn__ssiizzee))
4433 eellssee::
4444 ssttaattee == ttoorrcchh..FFllooaattTTeennssoorr((ssttaattee))..uunnssqquueeeezzee((00))
4455 wwiitthh ttoorrcchh..nnoo__ggrraadd(())::
4466 qq__vvaalluueess == sseellff..ppoolliiccyy__nneett((ssttaattee))
4477 rreettuurrnn ttoorrcchh..aarrggmmaaxx((qq__vvaalluueess))..iitteemm(())
4488
4499
5500 ddeeff lleeaarrnn((sseellff))::
5511 iiff lleenn((sseellff..mmeemmoorryy)) << sseellff..bbaattcchh__ssiizzee::
5522 rreettuurrnn
5533
5544 ## ssaammppllee aa bbaattcchh ooff eexxppeerriieenncceess
https://kuriko-iwai.com/deep-reinforcement-learning 21/27


---
*Page 22*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
5555 eexxppeerriieenncceess == sseellff..mmeemmoorryy..ssaammppllee((sseellff..bbaattcchh__ssiizzee))
5566 ssttaatteess,, aaccttiioonnss,, rreewwaarrddss,, nneexxtt__ssttaatteess,, ddoonneess == zziipp((**eexxppeerriieenncceess))
5577
5588 ## ccoonnvveerrtt ttoo PPyyTToorrcchh tteennssoorrss
5599 ssttaatteess == ttoorrcchh..FFllooaattTTeennssoorr((ssttaatteess))
6600 aaccttiioonnss == ttoorrcchh..LLoonnggTTeennssoorr((aaccttiioonnss))..uunnssqquueeeezzee((11))
6611 rreewwaarrddss == ttoorrcchh..FFllooaattTTeennssoorr((rreewwaarrddss))..uunnssqquueeeezzee((11))
6622 nneexxtt__ssttaatteess == ttoorrcchh..FFllooaattTTeennssoorr((nneexxtt__ssttaatteess))
6633 ddoonneess == ttoorrcchh..FFllooaattTTeennssoorr((ddoonneess))..uunnssqquueeeezzee((11))
6644
6655 ## ccoommppuuttee qq--vvaalluueess ffoorr tthhee ccuurrrreenntt ssttaattee
6666 ccuurrrreenntt__qq__vvaalluueess == sseellff..ppoolliiccyy__nneett((ssttaatteess))..ggaatthheerr((11,, aaccttiioonnss))
6677
6688 ## ccoommppuuttee mmaaxx qq--vvaalluuee ffoorr tthhee nneexxtt ssttaatteess uussiinngg tthhee ttaarrggeett nneettwwoorrkk..
6699 nneexxtt__qq__vvaalluueess == sseellff..ttaarrggeett__nneett((nneexxtt__ssttaatteess))..ddeettaacchh(())..mmaaxx((11))[[00]]..uunnssqquueeeezzee((11))
7700
7711 ## ccoommppuutteess tthhee ttaarrggeett qq--vvaalluueess:: RR((ss)) ++ ggaammmmaa ** mmaaxx((QQ((ss'',, aa'')))) ((iiff ddoonnssee,, ssttoopp uuppddaattiinngg))
7722 ttaarrggeett__qq__vvaalluueess == rreewwaarrddss ++ sseellff..ggaammmmaa ** nneexxtt__qq__vvaalluueess iiff nnoott ddoonneess..vvaalluueess eellssee rreewwaarrddss
7733
7744 ## ccoommppuuttee lloossss bbeettwweeeenn ccuurrrreenntt qq--vvaalluueess aanndd ttaarrggeett qq--vvaalluueess
7755 lloossss == sseellff..ccrriitteerriioonn((ccuurrrreenntt__qq__vvaalluueess,, ttaarrggeett__qq__vvaalluueess))
7766
7777 ## ooppttiimmiizzee tthhee ppoolliiccyy nneettwwoorrkk,, uuppddaattiinngg wweeiigghhttss
7788 sseellff..ooppttiimmiizzeerr..zzeerroo__ggrraadd(())
7799 lloossss..bbaacckkwwaarrdd(())
8800 sseellff..ooppttiimmiizzeerr..sstteepp(())
8811
8822 ## ddeeccaayy eeppssiilloonn ((eexxpplloorraattiioonn rraattee))
8833 sseellff..eeppssiilloonn == mmaaxx((sseellff..eeppssiilloonn__eenndd,, sseellff..eeppssiilloonn ** sseellff..eeppssiilloonn__ddeeccaayy))
8844
◼ Training DRL
To combine all components, I first initialize the environment, then the DQN agent, begin the training epochs,
and finally close the environment.
11 ## ttrraaiinn tthhee ddrrll
22 iimmppoorrtt ggyymmnnaassiiuumm aass ggyymm
33
44 ## ssttaarrtt aann eennvv
55 eennvv__nnaammee == ""CCaarrttPPoollee--vv11""
66 eennvv == ggyymm..mmaakkee((eennvv__nnaammee))
77 ssttaattee__ssiizzee == eennvv..oobbsseerrvvaattiioonn__ssppaaccee..sshhaappee[[00]]
88 aaccttiioonn__ssiizzee == eennvv..aaccttiioonn__ssppaaccee..nn
99
1100 ## iinniittiiaattee ddqqnn aaggeenntt
1111 aaggeenntt == DDQQNNAAggeenntt((ssttaattee__ssiizzee,, aaccttiioonn__ssiizzee))
1122
1133 ## ttrraaiinniinngg eeppoocchhss
1144 ssccoorreess == [[]]
1155 nnuumm__eeppiissooddeess == 550000
1166 uuppddaattee__ttaarrggeett__eevveerryy == 1100
1177 ffoorr eeppiissooddee iinn rraannggee((11,, nnuumm__eeppiissooddeess ++ 11))::
1188 ssttaattee,, iinnffoo == eennvv..rreesseett(())
https://kuriko-iwai.com/deep-reinforcement-learning 22/27


---
*Page 23*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
1199 ssccoorree == 00
2200 ddoonnee == FFaallssee
2211 ttrruunnccaatteedd == FFaallssee
2222
2233 wwhhiillee nnoott ddoonnee aanndd nnoott ttrruunnccaatteedd::
2244 ## sseelleecctt aann aaccttiioonn
2255 aaccttiioonn == aaggeenntt..sseelleecctt__aaccttiioonn((ssttaattee))
2266
2277 ## eexxeeccuuttee aann aaccttiioonn
2288 nneexxtt__ssttaattee,, rreewwaarrdd,, ddoonnee,, ttrruunnccaatteedd,, iinnffoo == eennvv..sstteepp((aaccttiioonn))
2299
3300 ## ssttoorree tthhee eexxppeerriieennccee iinn tthhee mmeemmoorryy
3311 aaggeenntt..mmeemmoorryy..ppuusshh((ssttaattee,, aaccttiioonn,, rreewwaarrdd,, nneexxtt__ssttaattee,, ddoonnee))
3322
3333 ## uuppddaattee ssttaattee,, rreewwaarrddss
3344 ssttaattee == nneexxtt__ssttaattee
3355 ssccoorree ++== rreewwaarrdd
3366
3377 ## lleeaarrnniinngg ffrroomm aa bbaattcchh eexxppeerriieennccee
3388 aaggeenntt..lleeaarrnn(())
3399
4400 ssccoorreess..aappppeenndd((ssccoorree))
4411
4422 ## cclloossee tthhee eennvv
4433 eennvv..cclloossee(())
4444
◼ Rule-Based Controller
For the rule-based controller, set up a simulation where state[2] and state[3] indicate the pole angle and
angular velocity respectively, and if the pole is leaning right, push right. If leaning left, push left, while
considering angular velocity for better performance.
11
22 ddeeff rruullee__bbaasseedd__aaccttiioonn((ssttaattee))::
33 iiff ssttaattee[[22]] >> 00..0011::
44 rreettuurrnn 11 ## ppuusshh rriigghhtt
55 eelliiff ssttaattee[[22]] << --00..0011::
66 rreettuurrnn 00 ## ppuusshh lleefftt
77 eellssee::
88 iiff ssttaattee[[33]] >> 00::
99 rreettuurrnn 11
1100 eellssee::
1111 rreettuurrnn 00
1122
Then, Similar to the DQN agent, set up the same environment and train the rule-based method.
11 iimmppoorrtt ggyymmnnaassiiuumm aass ggyymm
22
33 eennvv == ggyymm..mmaakkee((eennvv__nnaammee))
44 ssccoorreess == [[]]
55 nnuumm__eeppiissooddeess == 550000
https://kuriko-iwai.com/deep-reinforcement-learning 23/27


---
*Page 24*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
66
77 ffoorr eeppiissooddee iinn rraannggee((11,, nnuumm__eeppiissooddeess ++ 11))::
88 ssttaattee,, iinnffoo == eennvv..rreesseett(())
99 ssccoorree == 00
1100 ddoonnee == FFaallssee
1111 ttrruunnccaatteedd == FFaallssee
1122
1133 wwhhiillee nnoott ddoonnee aanndd nnoott ttrruunnccaatteedd::
1144 aaccttiioonn == rruullee__bbaasseedd__aaccttiioonn((ssttaattee)) ## aaggeenntt cchhoooosseess aaccttiioonn bbaasseedd oonn ssiimmppllee rruulleess
1155 ssttaattee,, rreewwaarrdd,, ddoonnee,, ttrruunnccaatteedd,, iinnffoo == eennvv..sstteepp((aaccttiioonn))
1166 ssccoorree ++== rreewwaarrdd
1177
1188 ssccoorreess..aappppeenndd((ssccoorree))
1199
2200 eennvv..cclloossee(())
2211
◼ Results
The DQN agent achieves higher and more consistent performance, successfully solving the CartPole
environment. This indicates that it has learned a more robust and generalized strategy for balancing the pole
than the fixed rules.
Kernel Labs | Kuriko IWAI | kuriko-iwai.com
Figure E. Comparison of the cumulative rewards of the DQN agent and rule-based controller (Created by
Kuriko IWAI)
https://kuriko-iwai.com/deep-reinforcement-learning 24/27


---
*Page 25*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
Rule-Based Controller (Red line):
Initial Performance: The rule-based controller starts with a relatively high score (around 100),
indicating it has some inherent understanding of how to balance the pole.
Lack of Learning: Throughout the 500 episodes, its performance fluctuates but generally stays within a
certain range, mostly between 100 and 200, hence it does not show an upward trend over time. This is
characteristic of a rule-based system; its logic is fixed and does not adapt or learn from
experience. It performs as well as its hand-coded rules allow, but no better.
Below the Threshold: Critically, the rule-based controller fails to consistently cross and maintain the
"CartPole Solved Threshold" of 195. While it touches or slightly exceeds it at times, it doesn't
demonstrate a sustained ability to keep the pole balanced for the required duration.
DQN Agent (Blue Line):
Initial Performance (Exploration Phase): The DQN agent starts with very low scores (near 0) in the
initial episodes without any prior knowledge. It must explore the environment to understand its dynamics
and reward structure. This initial phase is where exploration (e.g., via ϵ-greedy) is most active.
Learning and Improvement: Around episode 50, the DQN agent's performance rapidly increases,
demonstrating the learning capabilities of the deep reinforcement learning algorithm. It quickly
surpasses the rule-based controller and begins to regularly cross the solved threshold.
Solving the Environment: The most significant observation is that the DQN agent consistently and
significantly surpasses the "CartPole Solved Threshold" (195) for extended periods. For example, it
reaches scores well over 300 multiple times, indicating it has learned a highly effective policy for
balancing the pole.
Fluctuations and Generalization: While there are still fluctuations (e.g., dips around episodes 200-
250), the overall trend is a much higher average performance than the rule-based method, and it
consistently recovers to high scores. These fluctuations can be due to various factors like exploration,
changes in experience replay buffer, or network updates.
Overall Summary:
Although the DQN agent has an initial learning curve, its ability to learn and adapt from experience ultimately
allows it to outperform and consistently solve the CartPole problem.
Wrapping Up
In our experiment We will run a simulation over the DQN agent and the rule-based controller in the CartPole-
v1 environment.
By comparing metrics like the average number of steps the pole remains balanced (i.e., the score) over
many episodes, we saw the DRL agents' superior performance due to their ability to learn more nuanced and
adaptive control policies compared to the fixed logic of the traditional method.
Overall, DRL represents a powerful paradigm for building intelligent systems that can learn complex
behaviors from interaction.
https://kuriko-iwai.com/deep-reinforcement-learning 25/27


---
*Page 26*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
By combining the goal-driven learning of reinforcement learning with the function approximation capabilities of
deep learning, DRL has provided solutions across many domains.
Related Books for Further Understanding
These books cover the wide range of theories and practices; from fundamentals to PhD level.
Linear Algebra Done Right Foundations of Machine Designing Data-Intensive
Learning, second edition Applications: The Big Ideas
(Adaptive Computation and Behind Reliable, Scalable, and
Machine Learning series) Maintainable Systems
Designing Machine Learning Machine Learning Design
Systems: An Iterative Process Patterns: Solutions to
for Production-Ready Common Challenges in Data
Applications Preparation, Model Building,
and MLOps
Write a comment...
https://kuriko-iwai.com/deep-reinforcement-learning 26/27


---
*Page 27*


3/5/26, 6:17 PM Deep Reinforcement Learning: Concepts, Optimization & Algorithms
Post Comment
Share What You Learned
Kuriko IWAI, "Deep Reinforcement Learning for Self-Evolving AI" in Kernel Labs
https://kuriko-iwai.com/deep-reinforcement-learning
Looking for Solutions?
Deploying ML Systems 👉 Book a briefing session
Hiring an ML Engineer 👉 Drop an email
Learn by Doing 👉 Enroll AI Engineering Masterclass
Written by Kuriko IWAI. All images, unless otherwise noted, are by the author. All experimentations on this blog utilize synthetic or licensed data.
© 2024-2026 Kernel Labs Pte. Ltd. All rights reserved.
Access latest deep dives Subscribe
Archive Contact
https://kuriko-iwai.com/deep-reinforcement-learning 27/27