"""Run the evaluator on every test case and report how well it matches my labels.

Usage: python evaluate.py
"""

import json

from evaluator import evaluate_answer

with open("evaluation_data.json") as f:
    test_cases = json.load(f)

results = []
for case in test_cases:
    result = evaluate_answer(case["question"], case["answer"], case["expected_answer"])
    result["question"] = case["question"]
    result["label"] = case["label"]  # my manual label: "pass" or "fail"
    results.append(result)

    if "error" in result:
        print(f"[ERROR] {case['question']}: {result['error']}")
        continue

    verdict = "pass" if result["passed"] else "fail"
    match = "OK      " if verdict == result["label"] else "MISMATCH"
    print(
        f"[{match}] R={result['relevance']} C={result['correctness']} "
        f"judge={verdict} mine={result['label']} | {case['question']}"
    )

# --- Summary ---
scored = [r for r in results if "error" not in r]
if not scored:
    raise SystemExit("No results were scored.")

avg_relevance = sum(r["relevance"] for r in scored) / len(scored)
avg_correctness = sum(r["correctness"] for r in scored) / len(scored)
agree = sum(("pass" if r["passed"] else "fail") == r["label"] for r in scored)

print("\n--- Summary ---")
print(f"Cases scored:        {len(scored)}/{len(results)}")
print(f"Average relevance:   {avg_relevance:.2f}")
print(f"Average correctness: {avg_correctness:.2f}")
print(f"Agreement with my labels: {agree}/{len(scored)} ({agree / len(scored):.0%})")

print("\nMismatches (worth reading):")
for r in scored:
    if ("pass" if r["passed"] else "fail") != r["label"]:
        print(f"  - {r['question']} -> {r['reason']}")

with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
