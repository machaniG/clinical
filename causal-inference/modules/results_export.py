import csv
from collections.abc import Mapping, Sequence
from numbers import Real
from pathlib import Path


RESULT_COLUMNS = [
    "result_type",
    "method",
    "refutation_type",
    "estimate",
    "ci_lower",
    "ci_upper",
    "original_effect",
    "new_effect",
    "new_effect_min",
    "new_effect_max",
    "p_value",
    "is_statistically_significant",
    "treatment_strength",
    "outcome_strength",
]


def _number(value):
    return float(value) if isinstance(value, Real) else None


def _refutation_row(result_type, method, refutation):
    row = {
        "result_type": result_type,
        "method": method,
        "refutation_type": refutation.refutation_type,
        "original_effect": _number(refutation.estimated_effect),
    }

    new_effect = refutation.new_effect
    numeric_effect = _number(new_effect)
    if numeric_effect is not None:
        row["new_effect"] = numeric_effect
    elif (
        isinstance(new_effect, Sequence)
        and len(new_effect) == 2
        and all(_number(value) is not None for value in new_effect)
    ):
        row["new_effect_min"], row["new_effect_max"] = (
            _number(value) for value in new_effect
        )

    significance = refutation.refutation_result
    if isinstance(significance, Mapping):
        row["p_value"] = _number(significance.get("p_value"))
        row["is_statistically_significant"] = significance.get(
            "is_statistically_significant"
        )
    return row


def _stress_test_rows(refutation, treatment_strengths, outcome_strengths):
    effects = refutation.new_effect_array
    if len(effects) != len(treatment_strengths) or any(
        len(row) != len(outcome_strengths) for row in effects
    ):
        raise ValueError("Stress-test effect grid does not match the configured strengths.")

    rows = [
        _refutation_row("stress_test_summary", "unobserved_common_cause", refutation)
    ]
    for treatment_index, treatment_strength in enumerate(treatment_strengths):
        for outcome_index, outcome_strength in enumerate(outcome_strengths):
            effect = _number(effects[treatment_index][outcome_index])
            if effect is None:
                raise ValueError("Stress-test effect grid contains a non-numeric value.")
            rows.append(
                {
                    "result_type": "stress_test_scenario",
                    "method": "unobserved_common_cause",
                    "original_effect": _number(refutation.estimated_effect),
                    "new_effect": effect,
                    "treatment_strength": treatment_strength,
                    "outcome_strength": outcome_strength,
                }
            )
    return rows


def save_analysis_results(
    baseline_effect,
    baseline_ci,
    dml_effect,
    refutation_results,
    treatment_strengths,
    outcome_strengths,
    output_path="causal_analysis_results.csv",
):
    rows = [
        {
            "result_type": "estimate",
            "method": "propensity_score_weighting",
            "estimate": _number(baseline_effect.value),
            "ci_lower": _number(baseline_ci[0]),
            "ci_upper": _number(baseline_ci[1]),
        },
        {
            "result_type": "estimate",
            "method": "econml.LinearDML",
            "estimate": _number(dml_effect.value),
        },
    ]

    for method, refutation in refutation_results.items():
        if method == "unobserved_common_cause":
            rows.extend(
                _stress_test_rows(
                    refutation, treatment_strengths, outcome_strengths
                )
            )
        else:
            rows.append(_refutation_row("refutation", method, refutation))

    with Path(output_path).open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
