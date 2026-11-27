import logging
from config import (
    treatment,
    outcome,
    confounders,
    stress_test_treatment_strengths,
    stress_test_outcome_strengths,
)
from modules import baseline_estimate, refute_estimate, load_data, estimate_ate_dml
from modules.results_export import save_analysis_results

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    # Load the dataset
    df = load_data()
    model, identified_estimand, estimate, baseline_ci = baseline_estimate(
        df, treatment, outcome, confounders
    )
    refutation_results = refute_estimate(model, estimate, identified_estimand)
    dml_estimate = estimate_ate_dml(model, identified_estimand)
    save_analysis_results(
        baseline_effect=estimate,
        baseline_ci=baseline_ci,
        dml_effect=dml_estimate,
        refutation_results=refutation_results,
        treatment_strengths=stress_test_treatment_strengths,
        outcome_strengths=stress_test_outcome_strengths,
    )
    logger.info("Combined analysis results saved to 'causal_analysis_results.csv'.")


# Run the main function
if __name__ == "__main__":
    main()

# how to run this script:
# python run_causal_model.py or
# python -m causal-inference.run_causal_model