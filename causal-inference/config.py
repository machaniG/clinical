# Define Treatment, Outcome, and Confounders
treatment = "qsmk"         # 1 = quit smoking, 0 = did not quit
outcome = "wt82_71"        # Weight change in kg (1982 minus 1971)

# Baseline patient characteristics that affect both quitting and weight gain
confounders = [
    "sex", "age", "race", "education", 
    "smokeintensity", "smokeyrs", "exercise", "active", "wt71"
]

# define effect modifiers (features along which the treatment effect may vary)
# to be used for heterogeneity analysis to explore whether effects differ by age, sex or baseline smoking intensity
effect_modifiers = ["age", "wt71", "smokeintensity", "smokeyrs"]

stress_test_treatment_strengths = [0.01, 0.05, 0.1]
stress_test_outcome_strengths = [0.5, 1.0, 2.0]