#!/usr/bin/env python3
"""
Statistical analysis helper for Experiment 2 result folders.

Reads prompt-based generation stats files and writes:
- Wilson 95% confidence intervals for per-attempt success rates.
- Wilson 95% confidence intervals for prompt success rates.
- Pairwise exact McNemar tests comparing manual vs each generated grammar at
  prompt-success level.
- Cochran's Q across all grammars at prompt-success level when possible.

This script does not generate models or call any LLM.
"""

import argparse
import json
import math
import os
from pathlib import Path


def wilson_ci(successes, total, z=1.959963984540054):
    if total == 0:
        return {"rate": 0.0, "lower": 0.0, "upper": 0.0}

    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    margin = (
        z
        * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total)
        / denom
    )
    return {"rate": p, "lower": center - margin, "upper": center + margin}


def load_stats_files(language_dir):
    stats_files = sorted(Path(language_dir).glob("*/stats_*.json"))
    stats = {}
    for path in stats_files:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        stats[data["grammar_id"]] = data
    return stats


def prompt_success_vector(stats):
    by_prompt = {}
    for result in stats.get("results", []):
        idx = result["prompt_index"]
        by_prompt.setdefault(idx, False)
        by_prompt[idx] = by_prompt[idx] or bool(result.get("is_valid"))
    return [by_prompt[idx] for idx in sorted(by_prompt)]


def exact_mcnemar(a, b):
    if len(a) != len(b):
        raise ValueError("McNemar vectors must have the same length")

    b01 = sum((not x) and y for x, y in zip(a, b))
    b10 = sum(x and (not y) for x, y in zip(a, b))
    discordant = b01 + b10
    if discordant == 0:
        p_value = 1.0
    else:
        from scipy.stats import binomtest

        p_value = binomtest(min(b01, b10), discordant, 0.5).pvalue

    return {
        "manual_fail_generated_success": b01,
        "manual_success_generated_fail": b10,
        "discordant_pairs": discordant,
        "p_value_exact": p_value,
    }


def analyze_language(language_dir):
    stats = load_stats_files(language_dir)
    if "manual" not in stats:
        raise ValueError(f"No manual stats found in {language_dir}")

    results = {
        "language_dir": str(language_dir),
        "confidence_intervals": {},
        "mcnemar_manual_vs_generated": {},
        "cochran_q_prompt_success": None,
    }

    for grammar_id, data in stats.items():
        attempt_ci = wilson_ci(data.get("valid_models", 0), data.get("total_attempts", 0))
        prompt_vector = prompt_success_vector(data)
        prompt_ci = wilson_ci(sum(prompt_vector), len(prompt_vector))

        results["confidence_intervals"][grammar_id] = {
            "attempt_success_rate": attempt_ci,
            "prompt_success_rate": prompt_ci,
            "valid_models": data.get("valid_models", 0),
            "total_attempts": data.get("total_attempts", 0),
            "prompts_with_success": sum(prompt_vector),
            "total_prompts": len(prompt_vector),
        }

    manual_vector = prompt_success_vector(stats["manual"])
    generated_ids = sorted(g for g in stats if g != "manual")

    for grammar_id in generated_ids:
        generated_vector = prompt_success_vector(stats[grammar_id])
        results["mcnemar_manual_vs_generated"][grammar_id] = exact_mcnemar(
            manual_vector, generated_vector
        )

    all_ids = ["manual"] + generated_ids
    vectors = [prompt_success_vector(stats[g]) for g in all_ids]
    if vectors and len({len(v) for v in vectors}) == 1:
        from statsmodels.stats.contingency_tables import cochrans_q

        # rows are prompts, columns are grammars
        matrix = [[int(vectors[col][row]) for col in range(len(vectors))]
                  for row in range(len(vectors[0]))]
        q_result = cochrans_q(matrix)
        results["cochran_q_prompt_success"] = {
            "grammar_ids": all_ids,
            "statistic": float(q_result.statistic),
            "p_value": float(q_result.pvalue),
        }

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Compute Experiment 2 CIs, McNemar tests, and Cochran's Q"
    )
    parser.add_argument(
        "--experiment-dir",
        required=True,
        help="Directory containing codintxt_experiment and/or dflow_experiment",
    )
    parser.add_argument(
        "--output-dir",
        default="../version_2_results/statistical_tests",
        help="Directory for statistical output JSON files",
    )
    args = parser.parse_args()

    experiment_dir = Path(args.experiment_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for language_dir in sorted(experiment_dir.glob("*_experiment")):
        results = analyze_language(language_dir)
        output_path = output_dir / f"{language_dir.name}_statistical_tests.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
