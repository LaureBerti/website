# p_hacking_simulation.py

import numpy as np
from scipy.stats import ttest_ind

np.random.seed(42)

# Null hypothesis is TRUE: both groups are drawn from the same distribution
# We expect 5% false positives at alpha = 0.05

n_simulations = 10_000
n_tests_per_sim = 20   # run 20 variations of the same test
alpha = 0.05

false_positive_single = 0
false_positive_hacked = 0

for _ in range(n_simulations):
    # Single honest test
    x1 = np.random.normal(0, 1, 50)
    x2 = np.random.normal(0, 1, 50)
    _, p = ttest_ind(x1, x2)
    if p < alpha:
        false_positive_single += 1

    # P-hacking: run 20 sub-variants, stop at first significant result
    found_significant = False
    for t in range(n_tests_per_sim):
        x1 = np.random.normal(0, 1, 50)
        x2 = np.random.normal(0, 1, 50)
        _, p = ttest_ind(x1, x2)
        if p < alpha:
            found_significant = True
            break
    if found_significant:
        false_positive_hacked += 1

fpr_single = false_positive_single / n_simulations
fpr_hacked = false_positive_hacked / n_simulations

print(f"False positive rate — single honest test: {fpr_single:.1%}  (expected ~5%)")
print(f"False positive rate — p-hacking (20 tries): {fpr_hacked:.1%}  (expected ~64%)")


# ────────────────────────────────────────────────────────────


# multiple_comparisons.py
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests

np.random.seed(0)
n_tests = 20
n_per_group = 50

# Generate 20 tests under the null (no real effect)
p_values = []
for _ in range(n_tests):
    x1 = np.random.normal(0, 1, n_per_group)
    x2 = np.random.normal(0, 1, n_per_group)
    _, p = ttest_ind(x1, x2)
    p_values.append(p)

p_values = np.array(p_values)
print(f"Raw p-values: {p_values.round(3)}")
print(f"Significant at α=0.05 (uncorrected): {(p_values < 0.05).sum()} / {n_tests}")

# Bonferroni: controls FWER (Family-Wise Error Rate)
# Rejects at p < α/n_tests
reject_bonferroni, p_bonf, _, _ = multipletests(p_values, alpha=0.05, method="bonferroni")
print(f"\nBonferroni significant: {reject_bonferroni.sum()} / {n_tests}")

# Benjamini-Hochberg: controls FDR (False Discovery Rate) — less conservative
reject_bh, p_bh, _, _ = multipletests(p_values, alpha=0.05, method="fdr_bh")
print(f"Benjamini-Hochberg significant: {reject_bh.sum()} / {n_tests}")


# ────────────────────────────────────────────────────────────


# data_snooping_demo.py
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

np.random.seed(42)
# 200 features, only 5 informative → selection leakage is amplified
X, y = make_classification(n_samples=200, n_features=200, n_informative=5,
                            n_redundant=0, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# --- WRONG: select features using all data (leaks test set labels) ---
selector_wrong = SelectKBest(f_classif, k=10)
selector_wrong.fit(X, y)                       # ← snooping: test labels included
clf_wrong = LogisticRegression(max_iter=1000, random_state=42)
clf_wrong.fit(selector_wrong.transform(X_train), y_train)
acc_wrong = accuracy_score(y_test, clf_wrong.predict(selector_wrong.transform(X_test)))

# --- CORRECT: feature selection inside a Pipeline (sees only X_train, y_train) ---
pipeline = Pipeline([
    ("selector", SelectKBest(f_classif, k=10)),
    ("clf", LogisticRegression(max_iter=1000, random_state=42))
])
pipeline.fit(X_train, y_train)                 # selector never sees X_test or y_test
acc_correct = accuracy_score(y_test, pipeline.predict(X_test))

print(f"Accuracy (snooping — feature selection on all data): {acc_wrong:.3f}")
print(f"Accuracy (correct — Pipeline):                       {acc_correct:.3f}")
print(f"Optimistic bias from snooping:                       {acc_wrong - acc_correct:+.3f}")


# ────────────────────────────────────────────────────────────


import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests

np.random.seed(0)
n_segments = 15

# Simulate 15 t-tests under the null (no real effect in any segment)
p_values = [ttest_ind(
    np.random.binomial(1, 0.10, 200),  # control: 10% conversion
    np.random.binomial(1, 0.10, 200),  # treatment: same 10% conversion
)[1] for _ in range(n_segments)]

reject, _, _, _ = multipletests(p_values, alpha=0.05, method="fdr_bh")
print(f"Significant before correction: {sum(p < 0.05 for p in p_values)}")
print(f"Significant after BH correction: {reject.sum()}")
# Typical output:
# Significant before correction: 1 (or 2)
# Significant after BH correction: 0
# All "significant" results were false positives.


# ────────────────────────────────────────────────────────────
# Visualisation 1: false positive rate — honest test vs p-hacking

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import ttest_ind

np.random.seed(42)
n_tests_range   = [1, 2, 5, 10, 15, 20, 30, 50]
expected_fpr    = [1 - (1 - 0.05) ** k for k in n_tests_range]

fig, ax = plt.subplots(figsize=(8, 4))
ax.axhline(0.05, color="steelblue", linestyle="--", label="Honest single test (α=0.05)")
ax.plot(n_tests_range, expected_fpr, "o-", color="tomato", label="P-hacking (stop-at-first-sig)")
ax.set_xlabel("Number of attempts before reporting")
ax.set_ylabel("Family-wise false positive rate")
ax.set_title("How P-Hacking Inflates False Positive Rates")
ax.set_ylim(0, 1)
ax.legend()
ax.fill_between(n_tests_range, 0.05, expected_fpr, alpha=0.15, color="tomato")
plt.tight_layout()

import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
plt.savefig(_os.path.join(_HERE, "p_hacking_fpr.png"), dpi=120)
print("Plot saved to p_hacking_fpr.png")

# Visualisation 2: raw p-values before and after multiple-comparison correction
from statsmodels.stats.multitest import multipletests

np.random.seed(42)
n_tests = 20
p_values = np.array([ttest_ind(
    np.random.normal(0, 1, 50), np.random.normal(0, 1, 50)
)[1] for _ in range(n_tests)])

reject_bonf, p_bonf, _, _ = multipletests(p_values, alpha=0.05, method="bonferroni")
reject_bh,   p_bh,   _, _ = multipletests(p_values, alpha=0.05, method="fdr_bh")

x = np.arange(n_tests)
fig, ax = plt.subplots(figsize=(11, 4))
ax.bar(x - 0.25, p_values,  width=0.25, color="steelblue", alpha=0.85, label="Raw p-value")
ax.bar(x,        p_bonf,    width=0.25, color="orange",    alpha=0.85, label="Bonferroni adjusted")
ax.bar(x + 0.25, p_bh,      width=0.25, color="green",     alpha=0.85, label="BH adjusted")
ax.axhline(0.05, color="red", linestyle="--", linewidth=1, label="α = 0.05")
ax.set_xlabel("Test index")
ax.set_ylabel("p-value")
ax.set_title("Multiple Comparison Correction: Raw vs Bonferroni vs Benjamini-Hochberg")
ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig(_os.path.join(_HERE, "multiple_comparisons.png"), dpi=120)
print("Plot saved to multiple_comparisons.png")
