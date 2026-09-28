"""Core logic: ask an LLM to judge an answer, and parse its response.

Both evaluate.py (batch run) and app.py (Streamlit UI) use this file.
"""

import json

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()  # reads GEMINI_API_KEY from a .env file

MODEL = "gemini-3.1-flash-lite"  # free tier; change here to swap models
PASS_THRESHOLD = 4  # both scores must be >= this for the answer to pass
MAX_ATTEMPTS = 2  # retry once if the LLM returns bad JSON

client = genai.Client()  # reads GEMINI_API_KEY from the environment automatically

PROMPT = """You are a strict evaluator of AI-generated answers.

Question: {question}
Reference answer (assumed correct): {expected_answer}
Answer to evaluate: {answer}

Score the answer from 1 to 5 on two criteria:
- relevance: does it actually address the question? (1 = off-topic, 5 = fully on-topic)
- correctness: is it factually consistent with the reference answer, with no wrong or
  invented claims? (1 = wrong or made up, 5 = fully correct)

Respond with ONLY a JSON object, no other text:
{{"relevance": <1-5>, "correctness": <1-5>, "reason": "<one short sentence>"}}"""


def parse_scores(text):
    """Pull the JSON object out of the LLM's reply and check it is valid."""
    start, end = text.find("{"), text.rfind("}") + 1  # ignores any extra text or ``` fences
    data = json.loads(text[start:end])

    for key in ("relevance", "correctness"):
        if not isinstance(data[key], int) or not 1 <= data[key] <= 5:
            raise ValueError(f"{key} must be an integer from 1 to 5")
    data["reason"] = str(data.get("reason", ""))
    return data


def evaluate_answer(question, answer, expected_answer):
    """Return a dict: relevance, correctness, reason, passed (or error if it failed)."""
    prompt = PROMPT.format(
        question=question, expected_answer=expected_answer, answer=answer
    )

    last_error = None
    for _ in range(MAX_ATTEMPTS):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,  # more repeatable scores
                    max_output_tokens=300,
                ),
            )
            scores = parse_scores(response.text)
            # Pass/fail is decided by our code, not the LLM, so the rule is transparent.
            scores["passed"] = (
                scores["relevance"] >= PASS_THRESHOLD
                and scores["correctness"] >= PASS_THRESHOLD
            )
            return scores
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            last_error = e  # malformed output -> try again

    return {"error": f"Could not parse LLM output: {last_error}"}