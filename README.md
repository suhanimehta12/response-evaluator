# AI Response Evaluator

A small tool that uses an LLM as a judge to score AI-generated answers, then checks how well the judge agrees with my own manual labels.

**Stack:** Python, Anthropic API, Streamlit

## How it works

1. Each test case has a question, a reference answer, an AI-generated answer, and my manual label (`pass` / `fail`).
2. `evaluator.py` sends these to an LLM and asks for JSON: `relevance` (1-5), `correctness` (1-5), and a one-sentence reason.
3. The output is parsed and validated. If it is malformed, the call is retried once.
4. Pass/fail is decided in code: both scores must be at least 4 (`PASS_THRESHOLD`).
5. `evaluate.py` runs all test cases, prints average scores, and reports **agreement with my labels**.

## Project structure

```
evaluator.py           # core logic: prompt, LLM call, JSON parsing, pass/fail rule
evaluate.py            # batch run over the dataset + summary metrics
app.py                 # Streamlit UI (single answer + full dataset)
evaluation_data.json   # 18 test cases: 10 good answers, 8 bad (off-topic, wrong, hallucinated)
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # then add your Anthropic API key
```

## Run

```bash
python evaluate.py          # batch evaluation in the terminal
streamlit run app.py        # web UI
```

## Design choices

- **Temperature 0** for more repeatable scores.
- **Structured JSON output** with validation and one retry, since LLMs sometimes return malformed output.
- **Pass/fail rule lives in code**, not in the prompt, so it is transparent and easy to change.
- **Deliberately bad answers** in the dataset (off-topic, subtly wrong, hallucinated). An evaluator that only sees good answers proves nothing.
- **Agreement with manual labels** is the key metric: it measures whether the judge can be trusted.

## Limitations

- LLM judges can be inconsistent and may favour longer answers.
- The dataset is small (18 cases), so the agreement number is indicative, not statistically strong.
- The judge relies on the reference answer, so it cannot catch errors if the reference itself is wrong.
- Only one model and one prompt were tested.

## Possible next steps

- Compare different prompts or models on the same dataset.
- Add more edge cases (partially correct answers, very long answers).
- Run each case several times to measure score consistency.
