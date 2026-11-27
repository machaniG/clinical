import pandas as pd
from dowhy import CausalModel
import logging
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def baseline_estimate(df, treatment, outcome, confounders):
    # Create a CausalModel object specifying the graph structure
    logger.info("Creating CausalModel...")
    model = CausalModel(
        data=df,
        treatment=treatment,
        outcome=outcome,
        common_causes=confounders
    )

    # Optional: Visualize the graph (requires graphviz/pydot)
    #model.view_model()

    # Identify the causal estimand based on the DAG
    logger.info("Identifying causal estimand...")
    identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)
    logger.info(f"Identified estimand: {identified_estimand}")

    # Baseline estimate
    # Estimate the Average Treatment Effect (ATE) using Propensity Score Weighting
    logger.info("Estimating causal effect...")
    estimate = model.estimate_effect(
    identified_estimand,
    method_name="backdoor.propensity_score_weighting",
    target_units="ate",
    method_params={
        "weighting_scheme": "ips_weight",
        "propensity_score_model": make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1000)
        )
    }
    )
   
    logger.info(f"Estimated Causal Effect (ATE): {estimate.value:.2f} kg")

    # Compute 95% Confidence Intervals using bootstrapping
    ci = estimate.get_confidence_intervals()
    logger.info(f"95% Confidence Interval: {ci}")

    # save the estimate and confidence intervals to a CSV file
    results_df = pd.DataFrame({
        "estimate": [estimate.value],
        "ci_lower": [ci[0]],
        "ci_upper": [ci[1]]
    })
    results_df.to_csv("causal_estimate_results.csv", index=False)

    return model, identified_estimand, estimate, ci
