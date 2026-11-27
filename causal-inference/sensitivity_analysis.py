# heterogeinity analysis
"""
Explore Heterogeneous Treatment Effects (CATE)

In healthcare, an average effect hides who benefits or suffers most. 
Conditional Average Treatment Effects (CATE) estimate how the effect of quitting smoking 
varies across patient characteristics (effect_modifiers), such as age, baseline weight (wt71), 
and smoking intensity (smokeintensity).
Here, we use Causal Forest DML, which builds trees specifically designed to split patients into subgroups with different treatment effects.
"""

import pandas as pd

from dowhy import CausalModel
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from modules import load_data
from config import treatment, outcome, confounders, effect_modifiers
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def perform_sensitivity_analysis():
    # Load the dataset
    df = load_data()

    # Re-declare CausalModel specifying effect_modifiers
    model_cate = CausalModel(
        data=df,
        treatment=treatment,
        outcome=outcome,
        common_causes=confounders,
        effect_modifiers=effect_modifiers
    )
    estimand_cate = model_cate.identify_effect(proceed_when_unidentifiable=True)

    # 2. Fit CausalForestDML
    logger.info("Fitting CausalForestDML for CATE estimation...")
    estimate_cate = model_cate.estimate_effect(
        estimand_cate,
        method_name="backdoor.econml.dml.CausalForestDML",
        target_units="ate",
        method_params={
            "init_params": {
                "model_y": RandomForestRegressor(n_estimators=100, min_samples_leaf=10, random_state=42),
                "model_t": RandomForestClassifier(n_estimators=100, min_samples_leaf=10, random_state=42),
                "discrete_treatment": True,
                "n_estimators": 200,
                "random_state": 42
            },
            "fit_params": {}
        }
    )

    # 3. Predict individual CATE for each patient in the dataset
    # Access the underlying EconML estimator to get personalized predictions and intervals
    logger.info("Predicting individual CATE for each patient...")
    raw_cf = estimate_cate.estimator.estimator
    lower_ci, upper_ci = raw_cf.effect_interval(df[effect_modifiers].values, alpha=0.05)

    df["predicted_cate"] = raw_cf.effect(df[effect_modifiers].values).ravel()
    df["cate_lower_95"] = lower_ci.ravel()
    df["cate_upper_95"] = upper_ci.ravel()


    logger.info("Inspecting subgroups: Comparing weight gain for younger vs. older smokers...")
    df["age_group"] = pd.cut(df["age"], bins=[20, 40, 60, 80], labels=["20-40", "41-60", "61+"])
    subgroup_summary = df.groupby("age_group", observed=False)[["predicted_cate", "cate_lower_95", "cate_upper_95"]].mean()

    # save the subgroup summary to a CSV file
    subgroup_summary.to_csv("subgroup_cate_summary.csv")
    logger.info("Subgroup CATE summary saved to 'subgroup_cate_summary.csv'.")

    logger.info("Subgroup Summary:")
    logger.info(subgroup_summary.round(2))


if __name__ == "__main__":
    perform_sensitivity_analysis()

# how to run it: 
# python sensitivity_analysis.py 