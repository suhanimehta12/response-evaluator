"""Streamlit UI for the evaluator.

Usage: streamlit run app.py
"""

import json

import streamlit as st

from evaluator import evaluate_answer

st.title("AI Response Evaluator")
st.caption("An LLM judges an answer for relevance and correctness.")

tab_single, tab_batch = st.tabs(["Evaluate one answer", "Run test dataset"])

# ---------- Tab 1: evaluate a single answer ----------
with tab_single:
    question = st.text_input("Question")
    expected = st.text_area("Reference answer (the correct answer)")
    answer = st.text_area("AI-generated answer to evaluate")

    if st.button("Evaluate"):
        if not (question and expected and answer):
            st.warning("Please fill in all three fields.")
        else:
            with st.spinner("Evaluating..."):
                result = evaluate_answer(question, answer, expected)

            if "error" in result:
                st.error(result["error"])
            else:
                col1, col2 = st.columns(2)
                col1.metric("Relevance", f"{result['relevance']}/5")
                col2.metric("Correctness", f"{result['correctness']}/5")
                st.write(f"**Reason:** {result['reason']}")
                if result["passed"]:
                    st.success("PASS")
                else:
                    st.error("FAIL")

# ---------- Tab 2: run the whole dataset ----------
with tab_batch:
    if st.button("Run evaluation_data.json"):
        with open("evaluation_data.json") as f:
            cases = json.load(f)

        rows = []
        progress = st.progress(0)
        for i, case in enumerate(cases):
            r = evaluate_answer(case["question"], case["answer"], case["expected_answer"])
            if "error" in r:
                rows.append({"Question": case["question"], "Judge": "error", "Mine": case["label"]})
            else:
                rows.append({
                    "Question": case["question"],
                    "Relevance": r["relevance"],
                    "Correctness": r["correctness"],
                    "Judge": "pass" if r["passed"] else "fail",
                    "Mine": case["label"],
                    "Reason": r["reason"],
                })
            progress.progress((i + 1) / len(cases))

        st.dataframe(rows)
        agree = sum(row["Judge"] == row["Mine"] for row in rows)
        st.metric("Agreement with my labels", f"{agree}/{len(rows)} ({agree / len(rows):.0%})")
