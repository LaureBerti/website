# conformal_prediction.py
import numpy as np
from sklearn.datasets import make_regression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

np.random.seed(42)
X, y = make_regression(n_samples=1000, n_features=10, noise=20, random_state=42)

# Split into train / calibration / test (60 / 20 / 20)
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.4, random_state=42)
X_cal, X_test, y_cal, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Train base model on training set
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Calibration step: compute residuals on calibration set
cal_preds = model.predict(X_cal)
residuals = np.abs(y_cal - cal_preds)  # nonconformity scores

# Choose coverage level: 90% → use 90th percentile of residuals as interval half-width
coverage = 0.90
q_hat = np.quantile(residuals, coverage)
print(f"Conformal quantile (q̂) for {coverage:.0%} coverage: {q_hat:.2f}")

# Predict on test set with intervals
test_preds = model.predict(X_test)
lower = test_preds - q_hat
upper = test_preds + q_hat

# Measure empirical coverage
covered = ((y_test >= lower) & (y_test <= upper)).mean()
avg_width = (upper - lower).mean()

print(f"Empirical coverage: {covered:.1%}  (target: {coverage:.0%})")
print(f"Average interval width: {avg_width:.2f}")


# ────────────────────────────────────────────────────────────


# ensemble_uncertainty.py
import numpy as np
from sklearn.datasets import make_regression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

np.random.seed(42)
X, y = make_regression(n_samples=500, n_features=10, noise=20, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Collect predictions from each tree
tree_preds = np.array([tree.predict(X_test) for tree in model.estimators_])
# tree_preds shape: (n_estimators, n_test_samples)

ensemble_mean = tree_preds.mean(axis=0)   # same as model.predict(X_test)
ensemble_std  = tree_preds.std(axis=0)    # uncertainty: disagreement between trees

# Sort test samples by uncertainty
order = np.argsort(ensemble_std)
print("5 most confident predictions (lowest std):")
for i in order[:5]:
    print(f"  pred={ensemble_mean[i]:7.1f}  std={ensemble_std[i]:.1f}  true={y_test[i]:.1f}")

print("\n5 least confident predictions (highest std):")
for i in order[-5:]:
    print(f"  pred={ensemble_mean[i]:7.1f}  std={ensemble_std[i]:.1f}  true={y_test[i]:.1f}")


# ────────────────────────────────────────────────────────────


# quantile_regression.py
import numpy as np
from sklearn.datasets import make_regression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split

np.random.seed(42)
X, y = make_regression(n_samples=500, n_features=10, noise=20, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train three models: median, 5th percentile, 95th percentile
model_median = GradientBoostingRegressor(loss="quantile", alpha=0.50, n_estimators=100, random_state=42)
model_lower  = GradientBoostingRegressor(loss="quantile", alpha=0.05, n_estimators=100, random_state=42)
model_upper  = GradientBoostingRegressor(loss="quantile", alpha=0.95, n_estimators=100, random_state=42)

for m in [model_median, model_lower, model_upper]:
    m.fit(X_train, y_train)

pred_median = model_median.predict(X_test)
pred_lower  = model_lower.predict(X_test)
pred_upper  = model_upper.predict(X_test)

covered = ((y_test >= pred_lower) & (y_test <= pred_upper)).mean()
avg_width = (pred_upper - pred_lower).mean()
print(f"Empirical coverage: {covered:.1%}  (target: 90%)")
print(f"Average interval width: {avg_width:.2f}")

# Inspect the first 5 predictions
print("\nSample predictions:")
print(f"{'Lower':>10} {'Median':>10} {'Upper':>10} {'True':>10} {'Covered':>8}")
for i in range(5):
    covered_i = pred_lower[i] <= y_test[i] <= pred_upper[i]
    print(f"{pred_lower[i]:10.1f} {pred_median[i]:10.1f} {pred_upper[i]:10.1f} "
          f"{y_test[i]:10.1f} {'yes' if covered_i else 'NO':>8}")


# ────────────────────────────────────────────────────────────


import numpy as np
from sklearn.datasets import make_regression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

np.random.seed(42)
X, y = make_regression(n_samples=400, n_features=5, noise=15, random_state=42)
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.4, random_state=42)
X_cal, X_test, y_cal, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

model = RandomForestRegressor(n_estimators=50, random_state=42)
model.fit(X_train, y_train)
residuals = np.abs(y_cal - model.predict(X_cal))

for coverage in [0.80, 0.90, 0.95]:
    q_hat = np.quantile(residuals, coverage)
    width = 2 * q_hat    # interval spans [pred - q̂, pred + q̂]
    print(f"Coverage {coverage:.0%} → q̂={q_hat:.1f}, width={width:.1f}")

# Output:
# Coverage 80% → q̂=32.8, width=65.5
# Coverage 90% → q̂=41.1, width=82.2
# Coverage 95% → q̂=51.1, width=102.2


# ────────────────────────────────────────────────────────────
# Visualisation: conformal prediction intervals on test set

import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_regression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

np.random.seed(42)
X, y = make_regression(n_samples=500, n_features=10, noise=20, random_state=42)
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.4, random_state=42)
X_cal, X_test, y_cal, y_test     = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
residuals  = np.abs(y_cal - model.predict(X_cal))
q_hat      = np.quantile(residuals, 0.90)
test_preds = model.predict(X_test)
lower, upper = test_preds - q_hat, test_preds + q_hat
covered = (y_test >= lower) & (y_test <= upper)

# Sort by predicted value for a cleaner plot
order = np.argsort(test_preds)[:50]   # first 50 for clarity
fig, ax = plt.subplots(figsize=(12, 5))
xs = range(len(order))
ax.fill_between(xs, lower[order], upper[order], alpha=0.3, color="steelblue", label="90% conformal interval")
ax.plot(xs, test_preds[order], color="steelblue", lw=1.5, label="Predicted")
ax.scatter([i for i, o in enumerate(order) if covered[o]],  y_test[order[covered[order]]],
           color="green", s=20, alpha=0.8, label="Covered")
ax.scatter([i for i, o in enumerate(order) if not covered[o]], y_test[order[~covered[order]]],
           color="tomato", s=40, marker="x", lw=2, label="NOT covered")
ax.set_xlabel("Test sample (sorted by prediction)")
ax.set_ylabel("Target value")
ax.set_title(f"Conformal Prediction Intervals (90%) — empirical coverage {covered.mean():.1%}")
ax.legend()
plt.tight_layout()

import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
plt.savefig(_os.path.join(_HERE, "conformal_intervals.png"), dpi=120)
plt.show()
print("Plot saved to conformal_intervals.png")

# Coverage vs width trade-off across quantile levels
coverages_target = [0.70, 0.80, 0.90, 0.95, 0.99]
empirical_cov, widths = [], []
for cov in coverages_target:
    q = np.quantile(residuals, cov)
    emp = ((y_test >= test_preds - q) & (y_test <= test_preds + q)).mean()
    empirical_cov.append(emp)
    widths.append(2 * q)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.plot([c * 100 for c in coverages_target], [c * 100 for c in empirical_cov], "o-", color="steelblue")
ax1.plot([70, 100], [70, 100], "--", color="gray", label="Ideal")
ax1.set_xlabel("Target coverage (%)")
ax1.set_ylabel("Empirical coverage (%)")
ax1.set_title("Coverage calibration")
ax1.legend()
ax2.plot([c * 100 for c in coverages_target], widths, "s-", color="tomato")
ax2.set_xlabel("Target coverage (%)")
ax2.set_ylabel("Average interval width")
ax2.set_title("Coverage–width trade-off")
plt.tight_layout()
plt.savefig(_os.path.join(_HERE, "coverage_tradeoff.png"), dpi=120)
plt.show()
print("Plot saved to coverage_tradeoff.png")
