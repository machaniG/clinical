
# Causal Effect of Smoking Cessation on Long-Term Weight Gain


## Research Question

What is the causal effect of quitting smoking on 11-year weight change among adult smokers, and how does this effect vary across patient subgroups?

Using observational longitudinal data from the NHEFS (National Health and Nutrition Examination Survey Data I Epidemiologic Follow-up Study) (N = 1,566 complete cases), I estimated the Average Treatment Effect (ATE) and Conditional Average Treatment Effects (CATE) of smoking cessation (qsmk: 1 = quit, 0 = continued) on weight change between 1971 and 1982 (wt82_71, in kg).

----

## Methodology & Identification Strategy

To isolate the causal effect from baseline differences between quitters and persistent smokers, I constructed a Directed Acyclic Graph (DAG) and adjusted for 9 pre-treatment clinical and demographic confounders measured in 1971 (sex, age, race, education, smokeintensity, smokeyrs, exercise, active, wt71), while strictly excluding post-treatment variables, colliders, and instrumental variables (price71, tax71).

I triangulated the causal effect across three distinct adjustment frameworks using DoWhy, EconML, and scikit-learn:

1. **G-Computation (Outcome Modeling):** Estimates counterfactual potential outcomes under universal cessation \(E[Y(1)]\) vs. continued smoking \(E[Y(0)]\).
2. **Inverse Probability of Treatment Weighting (IPTW)**: Balances baseline covariates using standardized logistic regression propensity scores with bootstrap confidence intervals.
3. **Double Machine Learning (LinearDML):** Uses cross-fitted Random Forest nuisance models for both outcome and treatment to capture non-linear confounding.
4. **Heterogeneous Treatment Effect Analysis (CausalForestDML):** Estimates subgroup-specific CATEs across age, baseline weight, smoking intensity, and smoking duration.

----

## Key Findings


### **1. Population Average Treatment Effect (ATE)**

All three adjustment strategies converge on a consistent causal weight gain of ~3.1 to 3.4 kg attributable to quitting smoking:


| Estimation Strategy | Adjustment Mechanism | Estimated Effect | Details / Uncertainty |
| ------ | ----- | ---- | ----- |
|G-Computation | Outcome model \(E[Y \mid T, X]\) |	**+3.14 kg** | \(E[Y(1)] = +4.98\text{ kg}\) vs. \(E[Y(0)] = +1.83\text{ kg}\) |
| Propensity Score Weighting (IPTW)	| Treatment model \(P(T=1 \mid X)\)	| +3.33 kg	| 95% Bootstrap CI: **[2.58 kg, 4.09 kg]** |
| Double Machine Learning (LinearDML) | Orthogonal ML (Outcome + Treatment)	| **+3.44 kg** |Cross-fitted Random Forest nuisance learners | 


- Separating Aging from Cessation: G-computation shows that adults who continued smoking still gained **1.83 kg** on average over the 11-year window, whereas quitting increased average total weight gain to **4.98 kg**.


### **2. Subgroup Heterogeneity (CATE by Age)**

CausalForestDML indicates that post-cessation weight gain is highest among younger adults and declines with age, though individual-level confidence intervals are wide:

| Age Group	| Estimated CATE |	95% Confidence Interval |
| --- | ---- | ---- |
| 20–40 years |	**+4.34 kg** | [-0.81 kg, 9.48 kg] |
| 41–60 years | **+4.03 kg** | [-0.37 kg, 8.43 kg] |
| 61+ years | **+3.30 kg** | [-0.08 kg, 6.67 kg] |



### **3. Refutation & Sensitivity Checks**

- **Random Common Cause:** Estimate remained unchanged at **3.33 kg** (\(p = 1.0\)), confirming estimator stability.
- **Placebo Treatment:** Replacing treatment with random noise collapsed the effect to **0.63 kg** (\(p = 0.18 > 0.05\), statistically indistinguishable from zero).
- **Unobserved Confounding Stress-Test:** Across simulated hidden confounders, the adjusted ATE remained strictly positive **(0.62 kg to 3.52 kg)**, demonstrating robustness against moderate unmeasured bias.



## Tech Stack

• Python 3.12 / 3.13
• Causal Inference: dowhy, econml, causaldata
• Machine Learning & Data: scikit-learn, pandas, numpy