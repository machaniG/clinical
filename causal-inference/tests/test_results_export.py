import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from modules.results_export import save_analysis_results


class ResultsExportTests(unittest.TestCase):
    def test_saves_estimates_refutations_and_stress_test_grid(self):
        refutations = {
            "random_common_cause": SimpleNamespace(
                refutation_type="Random common cause",
                estimated_effect=2.0,
                new_effect=2.1,
                refutation_result={
                    "p_value": 0.25,
                    "is_statistically_significant": False,
                },
            ),
            "unobserved_common_cause": SimpleNamespace(
                refutation_type="Unobserved common cause",
                estimated_effect=2.0,
                new_effect=(1.5, 2.5),
                new_effect_array=[[1.5, 1.8], [2.2, 2.5]],
                refutation_result=None,
            ),
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "results.csv"
            save_analysis_results(
                baseline_effect=SimpleNamespace(value=2.0),
                baseline_ci=(1.0, 3.0),
                dml_effect=SimpleNamespace(value=2.2),
                refutation_results=refutations,
                treatment_strengths=[0.1, 0.2],
                outcome_strengths=[0.3, 0.4],
                output_path=output_path,
            )

            with output_path.open(newline="", encoding="utf-8") as csv_file:
                rows = list(csv.DictReader(csv_file))

        self.assertEqual(len(rows), 8)
        self.assertEqual(rows[0]["method"], "propensity_score_weighting")
        self.assertEqual(rows[0]["ci_lower"], "1.0")
        self.assertEqual(rows[1]["method"], "econml.LinearDML")
        self.assertEqual(rows[2]["p_value"], "0.25")
        scenarios = [row for row in rows if row["result_type"] == "stress_test_scenario"]
        self.assertEqual(len(scenarios), 4)
        self.assertEqual(scenarios[0]["treatment_strength"], "0.1")
        self.assertEqual(scenarios[0]["outcome_strength"], "0.3")
        self.assertEqual(scenarios[0]["new_effect"], "1.5")

    def test_rejects_mismatched_stress_grid(self):
        refutations = {
            "unobserved_common_cause": SimpleNamespace(
                refutation_type="Unobserved common cause",
                estimated_effect=2.0,
                new_effect=(1.5, 2.5),
                new_effect_array=[[1.5]],
                refutation_result=None,
            )
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "does not match"):
                save_analysis_results(
                    baseline_effect=SimpleNamespace(value=2.0),
                    baseline_ci=(1.0, 3.0),
                    dml_effect=SimpleNamespace(value=2.2),
                    refutation_results=refutations,
                    treatment_strengths=[0.1, 0.2],
                    outcome_strengths=[0.3],
                    output_path=Path(temp_dir) / "results.csv",
                )


if __name__ == "__main__":
    unittest.main()
