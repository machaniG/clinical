# Estimate ATE using Double Machine Learning via EconML
"""
Propensity score weighting relies on getting the treatment model right. 
Double Machine Learning (DML) uses two machine learning models—one predicting the outcome from confounders, 
and one predicting the treatment from confounders—and models the causal effect from the residuals.
"""
import os
import logging
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from econml.dml import LinearDML

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Estimate ATE using Double Machine Learning via EconML
def estimate_ate_dml(model, identified_estimand):
    """
    Estimate the Average Treatment Effect (ATE) using Double Machine Learning (DML) via EconML.
    we call econml's LinearDML directly inside DoWhy so we keep the causal graph and refutation pipeline intact.

    Parameters:
    - model: CausalModel object from DoWhy
    - identified_estimand: The identified causal estimand from the CausalModel
    
    Returns:
    - estimate_dml: The estimated ATE using DML
    """
    estimate_dml = model.estimate_effect(
        identified_estimand,
        method_name="backdoor.econml.dml.LinearDML",
        target_units="ate",
        method_params={
            "init_params": {
                # ML model to predict outcome (continuous weight change)
                "model_y": RandomForestRegressor(n_estimators=100, min_samples_leaf=10, random_state=42),
                # ML model to predict treatment (binary quit smoking)
                "model_t": RandomForestClassifier(n_estimators=100, min_samples_leaf=10, random_state=42),
                "discrete_treatment": True,
                "cv": 5 # Cross-fitting prevents overfitting bias
            },
            "fit_params": {}
        }
    )

    logger.info(f"DML Estimated Causal Effect (ATE): {estimate_dml.value:.2f} kg")
    return estimate_dml
