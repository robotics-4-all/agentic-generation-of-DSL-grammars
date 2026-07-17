#!/usr/bin/env python3
"""
Statistical analysis for Experiment 1 ablation results.

Reads the archived condition-level combined_dataset.csv files and writes clean
JSON/CSV/Markdown outputs. This script does not call any LLM.

Important design note:
Experiment 1 conditions contain independently generated grammar sets. Cochran's Q
and McNemar require paired binary observations, so this script records a pairing
assessment and uses independent-sample tests unless shared grammar ids are found.
"""

import argparse
import csv
import json
import math
import random
from pathlib import Path


CONDITIONS = [
    ("condition_1_baseline", "1: Baseline", "1)-initial-results-no-refinement"),
    (
        "condition_2_structural_optimization",
        "2: + Structural Optimization",
        "2)-results-step-after-refinement-before-metrics",
    ),
    (
        "condition_3_valid_examples",
        "3: + Valid Examples",
        "3)-results-after-refinement-example-valid-models",
    ),
    (
        "condition_4_contrastive",
        "4: + Contrastive",
        "4)-results-after-refinement-example-valid-invalid-models",
    ),
    (
        "condition_5_refinement",
        "5: + Refinement",
        "5)-results-after-refinement-example-valid-invalid-models-refinement",
    ),
    (
        "condition_6_curriculum",
        "6: + Curriculum",
        "6) -results-after-refinement-example-valid-invalid-models-refinement-pyramid",
    ),
    (
        "condition_7_documentation",
        "7: + Documentation",
        "7) -results-after-refinement-example-valid-invalid-models-refinement-pyramid-documentation",
    ),
]


def normal_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def two_sided_normal_p(z):
    return 2.0 * (1.0 - normal_cdf(abs(z)))


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


def mean(values):
    return sum(values) / len(values) if values else 0.0


def median(values):
    values = sorted(values)
    n = len(values)
    if n == 0:
        return 0.0
    mid = n // 2
    if n % 2:
        return values[mid]
    return (values[mid - 1] + values[mid]) / 2


def sample_sd(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((x - m) ** 2 for x in values) / (len(values) - 1))


def bootstrap_mean_ci(values, iterations=10000, seed=20260609):
    rng = random.Random(seed)
    n = len(values)
    if n == 0:
        return {"mean": 0.0, "lower": 0.0, "upper": 0.0}
    boot = []
    for _ in range(iterations):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        boot.append(mean(sample))
    boot.sort()
    lower = boot[int(0.025 * iterations)]
    upper = boot[int(0.975 * iterations) - 1]
    return {"mean": mean(values), "lower": lower, "upper": upper}


def load_condition_rows(results_root, folder_name):
    path = (
        Path(results_root)
        / folder_name
        / "correlation_analysis"
        / "data"
        / "combined_dataset.csv"
    )
    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return path, rows


def rank_values(groups):
    combined = []
    for group_idx, values in enumerate(groups):
        for value in values:
            combined.append((value, group_idx))
    combined.sort(key=lambda item: item[0])

    ranks = []
    tie_counts = []
    i = 0
    while i < len(combined):
        j = i + 1
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        tie_len = j - i
        if tie_len > 1:
            tie_counts.append(tie_len)
        for k in range(i, j):
            ranks.append((combined[k][1], avg_rank))
        i = j
    return ranks, tie_counts


def chi_square_sf_even_df(x, df):
    """Survival function for chi-square when df is an even integer."""
    if x < 0 or df <= 0 or df % 2:
        return None
    half_x = x / 2.0
    terms = sum((half_x ** i) / math.factorial(i) for i in range(df // 2))
    return math.exp(-half_x) * terms


def kruskal_wallis(groups):
    n_total = sum(len(g) for g in groups)
    ranks, tie_counts = rank_values(groups)
    rank_sums = [0.0 for _ in groups]
    for group_idx, rank in ranks:
        rank_sums[group_idx] += rank

    h = 12.0 / (n_total * (n_total + 1.0))
    h *= sum((rank_sums[i] ** 2) / len(groups[i]) for i in range(len(groups)))
    h -= 3.0 * (n_total + 1.0)

    tie_correction = 1.0
    if tie_counts:
        tie_correction -= sum(t ** 3 - t for t in tie_counts) / (
            n_total ** 3 - n_total
        )
    if tie_correction > 0:
        h /= tie_correction

    df = len(groups) - 1
    return {
        "statistic": h,
        "df": df,
        "p_value": chi_square_sf_even_df(h, df),
        "tie_correction": tie_correction,
    }


def mann_whitney_u(x, y):
    n1 = len(x)
    n2 = len(y)
    ranks, tie_counts = rank_values([x, y])
    r1 = sum(rank for group_idx, rank in ranks if group_idx == 0)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    u2 = n1 * n2 - u1
    u = min(u1, u2)

    n = n1 + n2
    mean_u = n1 * n2 / 2.0
    tie_term = sum(t ** 3 - t for t in tie_counts)
    var_u = n1 * n2 / 12.0 * ((n + 1) - tie_term / (n * (n - 1)))
    z = (u - mean_u) / math.sqrt(var_u) if var_u > 0 else 0.0
    return {
        "u": u,
        "z": z,
        "p_value_normal_approx": two_sided_normal_p(z),
    }


def two_proportion_z(success_a, total_a, success_b, total_b):
    p1 = success_a / total_a
    p2 = success_b / total_b
    pooled = (success_a + success_b) / (total_a + total_b)
    se = math.sqrt(pooled * (1 - pooled) * (1 / total_a + 1 / total_b))
    z = (p2 - p1) / se if se > 0 else 0.0
    return {
        "difference_b_minus_a": p2 - p1,
        "z": z,
        "p_value_two_sided": two_sided_normal_p(z),
    }


def holm_adjust(p_values):
    indexed = sorted(enumerate(p_values), key=lambda item: item[1])
    adjusted = [None] * len(p_values)
    running_max = 0.0
    m = len(p_values)
    for rank, (idx, p_value) in enumerate(indexed):
        adj = min(1.0, (m - rank) * p_value)
        running_max = max(running_max, adj)
        adjusted[idx] = running_max
    return adjusted


def format_pct(value):
    return f"{value * 100:.2f}%"


def write_csv(path, rows, fieldnames):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Compute statistical tests for Experiment 1 ablation results"
    )
    parser.add_argument(
        "--results-root",
        default="../version_1_results/experiment_results",
        help="Root folder containing archived Experiment 1 condition folders",
    )
    parser.add_argument(
        "--output-dir",
        default="../version_2_results/statistical_tests/experiment1",
        help="Directory where statistical outputs will be written",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    condition_data = []
    for condition_id, label, folder_name in CONDITIONS:
        csv_path, rows = load_condition_rows(args.results_root, folder_name)
        rates = [float(r["overall_success_rate"]) for r in rows]
        successes = [int(float(r["overall_success_count"])) for r in rows]
        totals = [int(float(r["overall_total_attempts"])) for r in rows]
        total_successes = sum(successes)
        total_attempts = sum(totals)

        condition_data.append(
            {
                "condition_id": condition_id,
                "label": label,
                "folder_name": folder_name,
                "csv_path": str(csv_path),
                "rows": rows,
                "rates": rates,
                "total_successes": total_successes,
                "total_attempts": total_attempts,
            }
        )

    summary_rows = []
    for data in condition_data:
        rates = data["rates"]
        pooled_ci = wilson_ci(data["total_successes"], data["total_attempts"])
        mean_ci = bootstrap_mean_ci(rates)
        summary_rows.append(
            {
                "condition_id": data["condition_id"],
                "label": data["label"],
                "n_grammars": len(rates),
                "mean_success_rate": mean(rates),
                "mean_ci_lower": mean_ci["lower"],
                "mean_ci_upper": mean_ci["upper"],
                "median_success_rate": median(rates),
                "std_dev": sample_sd(rates),
                "min_success_rate": min(rates),
                "max_success_rate": max(rates),
                "perfect_grammars": sum(1 for r in rates if r == 1.0),
                "zero_success_grammars": sum(1 for r in rates if r == 0.0),
                "pooled_successes": data["total_successes"],
                "pooled_attempts": data["total_attempts"],
                "pooled_success_rate": pooled_ci["rate"],
                "pooled_ci_lower": pooled_ci["lower"],
                "pooled_ci_upper": pooled_ci["upper"],
            }
        )

    global_test = kruskal_wallis([d["rates"] for d in condition_data])

    adjacent_tests = []
    for idx in range(len(condition_data) - 1):
        a = condition_data[idx]
        b = condition_data[idx + 1]
        mw = mann_whitney_u(a["rates"], b["rates"])
        prop = two_proportion_z(
            a["total_successes"],
            a["total_attempts"],
            b["total_successes"],
            b["total_attempts"],
        )
        adjacent_tests.append(
            {
                "comparison": f"{a['label']} vs {b['label']}",
                "condition_a": a["condition_id"],
                "condition_b": b["condition_id"],
                "mean_difference_b_minus_a": mean(b["rates"]) - mean(a["rates"]),
                "mann_whitney_u": mw["u"],
                "mann_whitney_z": mw["z"],
                "mann_whitney_p": mw["p_value_normal_approx"],
                "pooled_difference_b_minus_a": prop["difference_b_minus_a"],
                "two_proportion_z": prop["z"],
                "two_proportion_p": prop["p_value_two_sided"],
            }
        )

    mw_adjusted = holm_adjust([row["mann_whitney_p"] for row in adjacent_tests])
    prop_adjusted = holm_adjust([row["two_proportion_p"] for row in adjacent_tests])
    for row, mw_adj, prop_adj in zip(adjacent_tests, mw_adjusted, prop_adjusted):
        row["mann_whitney_p_holm"] = mw_adj
        row["two_proportion_p_holm"] = prop_adj

    grammar_id_sets = [
        {row["grammar_id"] for row in data["rows"]} for data in condition_data
    ]
    shared_ids = set.intersection(*grammar_id_sets)
    pairing_assessment = {
        "shared_grammar_ids_across_all_conditions": len(shared_ids),
        "paired_binary_tests_appropriate": len(shared_ids) > 0,
        "conclusion": (
            "Shared grammar ids were found; paired tests may be possible after "
            "constructing matched binary outcomes."
            if shared_ids
            else "No shared grammar ids across all seven conditions. Experiment 1 "
            "conditions appear to be independent generated grammar sets, so "
            "Cochran's Q and McNemar tests are not appropriate for the archived "
            "condition-level data. Independent-sample tests are reported instead."
        ),
    }

    results = {
        "analysis": "Experiment 1 ablation statistical tests",
        "input_root": str(Path(args.results_root)),
        "output_dir": str(output_dir),
        "pairing_assessment": pairing_assessment,
        "condition_summaries": summary_rows,
        "global_kruskal_wallis": global_test,
        "adjacent_condition_tests": adjacent_tests,
    }

    with open(output_dir / "experiment1_statistical_tests.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    write_csv(
        output_dir / "condition_summary.csv",
        summary_rows,
        [
            "condition_id",
            "label",
            "n_grammars",
            "mean_success_rate",
            "mean_ci_lower",
            "mean_ci_upper",
            "median_success_rate",
            "std_dev",
            "min_success_rate",
            "max_success_rate",
            "perfect_grammars",
            "zero_success_grammars",
            "pooled_successes",
            "pooled_attempts",
            "pooled_success_rate",
            "pooled_ci_lower",
            "pooled_ci_upper",
        ],
    )

    write_csv(
        output_dir / "adjacent_condition_tests.csv",
        adjacent_tests,
        [
            "comparison",
            "condition_a",
            "condition_b",
            "mean_difference_b_minus_a",
            "mann_whitney_u",
            "mann_whitney_z",
            "mann_whitney_p",
            "mann_whitney_p_holm",
            "pooled_difference_b_minus_a",
            "two_proportion_z",
            "two_proportion_p",
            "two_proportion_p_holm",
        ],
    )

    markdown_lines = [
        "# Experiment 1 Statistical Tests",
        "",
        "## Pairing Assessment",
        "",
        pairing_assessment["conclusion"],
        "",
        "## Condition Summary",
        "",
        "| Condition | Mean [95% CI] | Median | SD | Pooled Rate [95% CI] | Perfect | Zero |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        markdown_lines.append(
            "| {label} | {mean} [{lo}, {hi}] | {median} | {sd:.3f} | "
            "{pooled} [{plo}, {phi}] | {perfect}/100 | {zero}/100 |".format(
                label=row["label"],
                mean=format_pct(row["mean_success_rate"]),
                lo=format_pct(row["mean_ci_lower"]),
                hi=format_pct(row["mean_ci_upper"]),
                median=format_pct(row["median_success_rate"]),
                sd=row["std_dev"],
                pooled=format_pct(row["pooled_success_rate"]),
                plo=format_pct(row["pooled_ci_lower"]),
                phi=format_pct(row["pooled_ci_upper"]),
                perfect=row["perfect_grammars"],
                zero=row["zero_success_grammars"],
            )
        )

    markdown_lines.extend(
        [
            "",
            "## Global Test",
            "",
            (
                f"Kruskal-Wallis H = {global_test['statistic']:.4f}, "
                f"df = {global_test['df']}, p = {global_test['p_value']:.4g}."
            ),
            "",
            "## Adjacent Condition Comparisons",
            "",
            "| Comparison | Mean Diff | Mann-Whitney p (Holm) | Pooled Diff | Two-proportion p (Holm) |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in adjacent_tests:
        markdown_lines.append(
            "| {comparison} | {mean_diff} | {mw_p:.4g} ({mw_holm:.4g}) | "
            "{pooled_diff} | {prop_p:.4g} ({prop_holm:.4g}) |".format(
                comparison=row["comparison"],
                mean_diff=format_pct(row["mean_difference_b_minus_a"]),
                mw_p=row["mann_whitney_p"],
                mw_holm=row["mann_whitney_p_holm"],
                pooled_diff=format_pct(row["pooled_difference_b_minus_a"]),
                prop_p=row["two_proportion_p"],
                prop_holm=row["two_proportion_p_holm"],
            )
        )

    with open(output_dir / "experiment1_statistical_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines) + "\n")

    print(f"Wrote outputs to {output_dir}")
    print(
        f"Kruskal-Wallis H={global_test['statistic']:.4f}, "
        f"p={global_test['p_value']:.4g}"
    )
    print(pairing_assessment["conclusion"])


if __name__ == "__main__":
    main()
