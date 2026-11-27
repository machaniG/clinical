# Refute and Stress-Test Findings
import logging
from config import stress_test_treatment_strengths, stress_test_outcome_strengths

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def refute_estimate(model, estimate, identified_estimand):
    """
    Refute the estimated causal effect using various methods to test robustness.

    Parameters:
    - estimate: The estimated causal effect from the CausalModel
    - identified_estimand: The identified causal estimand from the CausalModel

    Returns:
    - refutation_results: A dictionary containing the results of the refutation tests
    """
    logger.info("Refuting findings...")
    """Since observational healthcare data can suffer from hidden bias, we run refutation tests to see if our estimate breaks easily.
    """
    # 1. Refute the estimate using a random common cause
    """Random common cause is a variable that is not causally related to either the treatment or the outcome.
    We can use this to test if our estimate is robust to the presence of such a variable.
    If the estimate changes significantly, it suggests that our estimate may be sensitive to hidden confounding
    adds an independent random variable as a confounderto the model and re-estimates the effect. 
    The causal estimate should NOT change significantly.
    If the new estimate is significantly different from the original estimate, it suggests that the original estimate may be sensitive to hidden confounding.
    """

    refute_random_common_cause = model.refute_estimate(
        identified_estimand,
        estimate,
        method_name="random_common_cause"
    )
    logger.info(f"Random Common Cause Refutation: {refute_random_common_cause}")


    # 2. Refute the estimate using a placebo treatment
    """
    A placebo treatment is a treatment that is known to have no effect on the outcome.
    We can use this to test if our estimate is robust to the presence of such a treatment
    Replaces actual treatment with random noise. The new estimated effect should drop close to 0.
    """
    refute_placebo = model.refute_estimate(
        identified_estimand,
        estimate,
        method_name="placebo_treatment_refuter",
        placebo_type="permute"
    )
    logger.info(f"Placebo Treatment Refutation: {refute_placebo}")

    # stress test the estimate by adding a random confounder
    # --- STRESS TEST: Unobserved Common Cause ---
    """Simulates an unmeasured confounder with varying strengths of effect on 
    Treatment (effect_strength_on_treatment) and Outcome (effect_strength_on_outcome).
    """
    res_unobserved = model.refute_estimate(
        identified_estimand,
        estimate,
        method_name="add_unobserved_common_cause",
        confounders_effect_on_treatment="binary_flip",
        confounders_effect_on_outcome="linear",
        effect_strength_on_treatment=stress_test_treatment_strengths,
        effect_strength_on_outcome=stress_test_outcome_strengths
    )
    
    logger.info(f"Unobserved Common Cause Refutation: {res_unobserved}")

    # save the refutation results in a dictionary
    refutation_results = {
        "random_common_cause": refute_random_common_cause,
        "placebo_treatment": refute_placebo,
        "unobserved_common_cause": res_unobserved
    }
    return refutation_results