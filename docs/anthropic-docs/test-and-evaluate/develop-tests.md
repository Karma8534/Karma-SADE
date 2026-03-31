---
source: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
scraped: 2026-03-23
---

# Define success criteria and build evaluations

---

Building a successful LLM-based application starts with clearly defining your success criteria and then designing evaluations to measure performance against them. This cycle is central to prompt engineering.

## Define your success criteria

Good success criteria are:
- **Specific:** Clearly define what you want to achieve. Instead of "good performance," specify "accurate sentiment classification."
- **Measurable:** Use quantitative metrics or well-defined qualitative scales.
- **Achievable:** Base your targets on industry benchmarks, prior experiments, AI research, or expert knowledge.
- **Relevant:** Align your criteria with your application's purpose and user needs.

Example metrics and measurement methods:

**Quantitative metrics:**
- Task-specific: F1 score, BLEU score, perplexity
- Generic: Accuracy, precision, recall
- Operational: Response time (ms), uptime (%)

**Quantitative methods:**
- A/B testing: Compare performance against a baseline model or earlier version.
- User feedback: Implicit measures like task completion rates.
- Edge case analysis: Percentage of edge cases handled without errors.

**Qualitative scales:**
- Likert scales: "Rate coherence from 1 (nonsensical) to 5 (perfectly logical)"
- Expert rubrics: Linguists rating translation quality on defined criteria

Example for sentiment analysis:
- **Bad**: The model should classify sentiments well
- **Good**: Our sentiment analysis model should achieve an F1 score of at least 0.85 on a held-out test set of 10,000 diverse Twitter posts, which is a 5% improvement over our current baseline.

### Common success criteria

- **Task fidelity**: How well does the model perform on the task? Consider edge case handling.
- **Consistency**: How similar are responses for similar types of input?
- **Relevance and coherence**: Does the model directly address the user's questions? Is information presented logically?
- **Tone and style**: Does the output style match expectations for the target audience?
- **Privacy preservation**: How does the model handle personal or sensitive information?
- **Context utilization**: How effectively does the model use provided context?
- **Latency**: What is the acceptable response time?
- **Price**: What is your budget for running the model?

Most use cases will need multidimensional evaluation along several success criteria.

---

## Build evaluations

### Eval design principles

1. **Be task-specific:** Design evals that mirror your real-world task distribution. Include edge cases (irrelevant inputs, overly long inputs, ambiguous test cases).
2. **Automate when possible:** Structure questions to allow for automated grading (multiple-choice, string match, code-graded, LLM-graded).
3. **Prioritize volume over quality:** More questions with slightly lower signal automated grading is better than fewer questions with high-quality human hand-graded evals.

### Example evals

#### Task fidelity (sentiment analysis) - exact match evaluation

Exact match evals measure whether the model's output exactly matches a predefined correct answer. Perfect for tasks with clear-cut, categorical answers.

```python
import anthropic

tweets = [
    {"text": "This movie was a total waste of time. 👎", "sentiment": "negative"},
    {"text": "The new album is 🔥! Been on repeat all day.", "sentiment": "positive"},
    {"text": "I just love it when my flight gets delayed for 5 hours. #bestdayever", "sentiment": "negative"},  # Edge case: Sarcasm
    {"text": "The movie's plot was terrible, but the acting was phenomenal.", "sentiment": "mixed"},  # Edge case: Mixed sentiment
    # ... 996 more tweets
]

client = anthropic.Anthropic()

def get_completion(prompt: str):
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=50,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text

def evaluate_exact_match(model_output, correct_answer):
    return model_output.strip().lower() == correct_answer.lower()

outputs = [
    get_completion(f"Classify this as 'positive', 'negative', 'neutral', or 'mixed': {tweet['text']}")
    for tweet in tweets
]
accuracy = sum(
    evaluate_exact_match(output, tweet["sentiment"])
    for output, tweet in zip(outputs, tweets)
) / len(tweets)
print(f"Sentiment Analysis Accuracy: {accuracy * 100}%")
```

#### Consistency (FAQ bot) - cosine similarity evaluation

Cosine similarity measures semantic similarity between vectors. Ideal for evaluating consistency because similar questions should yield semantically similar answers.

```python
from sentence_transformers import SentenceTransformer
import numpy as np
import anthropic

faq_variations = [
    {
        "questions": [
            "What's your return policy?",
            "How can I return an item?",
            "Wut's yur retrn polcy?",  # Edge case: Typos
        ],
        "answer": "Our return policy allows...",
    },
    # ... 47 more FAQs
]

def evaluate_cosine_similarity(outputs):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = [model.encode(output) for output in outputs]
    cosine_similarities = np.dot(embeddings, embeddings.T) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(embeddings, axis=1).T
    )
    return np.mean(cosine_similarities)

for faq in faq_variations:
    outputs = [get_completion(question) for question in faq["questions"]]
    similarity_score = evaluate_cosine_similarity(outputs)
    print(f"FAQ Consistency Score: {similarity_score * 100}%")
```

#### Tone and style (customer service) - LLM-based Likert scale

LLM-based Likert scale is ideal for evaluating nuanced aspects like empathy, professionalism, or patience.

```python
def evaluate_likert(model_output, target_tone):
    tone_prompt = f"""Rate this customer service response on a scale of 1-5 for being {target_tone}:
    <response>{model_output}</response>
    1: Not at all {target_tone}
    5: Perfectly {target_tone}
    Output only the number."""

    # Best practice: use a different model to evaluate than the model used to generate
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=50,
        messages=[{"role": "user", "content": tone_prompt}],
    )
    return int(response.content[0].text.strip())
```

#### Privacy preservation (medical chatbot) - LLM-based binary classification

Binary classification to determine if a response contains PHI (Protected Health Information).

```python
def evaluate_binary(model_output, query_contains_phi):
    if not query_contains_phi:
        return True

    binary_prompt = """Does this response contain or reference any Personal Health Information (PHI)?
    PHI refers to any individually identifiable health data...

    <response>{model_output}</response>
    Output only 'yes' or 'no'."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=50,
        messages=[{"role": "user", "content": binary_prompt}],
    )
    return response.content[0].text.strip().lower() == "no"
```

> **Tip:** Writing hundreds of test cases can be hard to do by hand! Get Claude to help you generate more from a baseline set of example test cases.

---

## Grade your evaluations

Choose the fastest, most reliable, most scalable method:

1. **Code-based grading:** Fastest and most reliable, extremely scalable, but lacks nuance for complex judgements.
   - Exact match: `output == golden_answer`
   - String match: `key_phrase in output`

2. **Human grading:** Most flexible and high quality, but slow and expensive. Avoid if possible.

3. **LLM-based grading:** Fast and flexible, scalable and suitable for complex judgement. Test to ensure reliability first then scale.

### Tips for LLM-based grading

- **Have detailed, clear rubrics**: "The answer should always mention 'Acme Inc.' in the first sentence. If it does not, the answer is automatically graded as 'incorrect.'"
- **Empirical or specific**: Instruct the LLM to output only 'correct' or 'incorrect', or to judge from a scale of 1-5. Purely qualitative evaluations are hard to assess quickly and at scale.
- **Encourage reasoning**: Ask the LLM to think first before deciding an evaluation score, then discard the reasoning. This increases evaluation performance for tasks requiring complex judgement.

```python
def build_grader_prompt(answer, rubric):
    return f"""Grade this answer based on the rubric:
    <rubric>{rubric}</rubric>
    <answer>{answer}</answer>
    Think through your reasoning in <thinking> tags, then output 'correct' or 'incorrect' in <result> tags."""

def grade_completion(output, golden_answer):
    grader_response = (
        client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": build_grader_prompt(output, golden_answer)}],
        )
        .content[0]
        .text
    )
    return "correct" if "correct" in grader_response.lower() else "incorrect"
```

## Next steps

- Brainstorm success criteria for your use case with Claude on claude.ai
- More code examples: [Evals cookbook](https://platform.claude.com/cookbook/misc-building-evals)
