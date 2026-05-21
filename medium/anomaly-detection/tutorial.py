# anomaly_comparison.py
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from scipy.stats import zscore

np.random.seed(42)

# 200 normal 2D points + 10 injected anomalies at the corners
X_normal = np.random.randn(200, 2)
X_anomaly = np.array([
    [4, 4], [-4, 4], [4, -4], [-4, -4],
    [5, 0], [0, 5], [-5, 0], [0, -5],
    [3.5, 3.5], [-3.5, -3.5]
])
X = np.vstack([X_normal, X_anomaly])
true_labels = np.array([1] * 200 + [-1] * 10)  # 1=normal, -1=anomaly

# Isolation Forest
iso = IsolationForest(contamination=0.05, random_state=42)
iso_pred = iso.fit_predict(X)

# LOF
lof = LocalOutlierFactor(n_neighbors=20, contamination=0.05)
lof_pred = lof.fit_predict(X)

# Z-score on first feature (univariate)
z = zscore(X[:, 0])
z_pred = np.where(np.abs(z) > 2.5, -1, 1)

def recall(pred, truth):
    caught = ((pred == -1) & (truth == -1)).sum()
    return caught / (truth == -1).sum()

print(f"Isolation Forest recall: {recall(iso_pred, true_labels):.0%}")
print(f"LOF recall:              {recall(lof_pred, true_labels):.0%}")
print(f"Z-score recall:          {recall(z_pred, true_labels):.0%}")


# ────────────────────────────────────────────────────────────


# time_series_anomaly.py
import numpy as np
from scipy.stats import zscore

np.random.seed(42)

# 365 days of temperature: seasonal sine wave + noise
t = np.linspace(0, 2 * np.pi, 365)
temp = 15 + 10 * np.sin(t) + np.random.normal(0, 1, 365)

# Inject 3 anomalous spikes
anomaly_days = [50, 150, 300]
temp[anomaly_days] += 15

# Method 1: global z-score
global_z = zscore(temp)
global_detected = set(np.where(np.abs(global_z) > 3)[0])

# Method 2: rolling z-score (30-day window)
window = 30
rolling_z = np.zeros(365)
for i in range(window, 365):
    w = temp[i - window:i]
    rolling_z[i] = (temp[i] - w.mean()) / (w.std() + 1e-8)

rolling_detected = set(np.where(np.abs(rolling_z) > 3)[0])

print(f"True anomaly days:     {anomaly_days}")
print(f"Global z-score found:  {sorted(global_detected)}")
print(f"Rolling z-score found: {sorted(rolling_detected)}")


# ────────────────────────────────────────────────────────────


# llm_anomaly_demo.py
# Requires: pip install ollama  +  ollama running locally (ollama pull llama3.2)

try:
    import ollama
    _OLLAMA_AVAILABLE = True
except ImportError:
    _OLLAMA_AVAILABLE = False

def llm_anomaly_check(description: str) -> str:
    prompt = f"""You are a data quality expert. Analyze this data point and decide if it is anomalous.

Data point: {description}

Respond with: NORMAL or ANOMALOUS, then one sentence explaining why."""

    if not _OLLAMA_AVAILABLE:
        return "ollama not installed — run: pip install ollama"
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

test_cases = [
    "Temperature sensor: 22°C at 2pm in Paris on a summer day",
    "Temperature sensor: -45°C at noon in Paris on a summer day",
    "Transaction: $4.99 for a coffee in New York City",
    "Transaction: $45,000 for a coffee in New York City",
]

for case in test_cases:
    result = llm_anomaly_check(case)
    print(f"Input: {case}")
    print(f"LLM:   {result}\n")


# ────────────────────────────────────────────────────────────


from sklearn.ensemble import IsolationForest
import numpy as np

X = np.random.randn(100, 3)
X[0] = [10, 10, 10]  # one obvious anomaly

model = IsolationForest(contamination=0.01, random_state=42)
pred = model.fit_predict(X)
anomaly_indices = np.where(pred == -1)[0]
print("Detected anomalies at indices:", anomaly_indices)
# Output: Detected anomalies at indices: [0]


# ────────────────────────────────────────────────────────────


from sklearn.neighbors import LocalOutlierFactor
import numpy as np

X = np.random.randn(100, 2)
X[:5] += 10  # 5 anomalies injected

lof = LocalOutlierFactor(n_neighbors=20)
scores = lof.fit_predict(X)
anomalies = np.where(scores == -1)[0]  # -1 = anomaly in LOF
print(f"Found {len(anomalies)} anomalies")


# ────────────────────────────────────────────────────────────
# Visualisation: anomaly detection results comparison

import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from scipy.stats import zscore

np.random.seed(42)
X_normal  = np.random.randn(200, 2)
X_anomaly = np.array([[4,4],[-4,4],[4,-4],[-4,-4],[5,0],[0,5],[-5,0],[0,-5],[3.5,3.5],[-3.5,-3.5]])
X         = np.vstack([X_normal, X_anomaly])
true_labels = np.array([1]*200 + [-1]*10)

iso_pred = IsolationForest(contamination=0.05, random_state=42).fit_predict(X)
lof_pred = LocalOutlierFactor(n_neighbors=20, contamination=0.05).fit_predict(X)
z_pred   = np.where(np.abs(zscore(X[:, 0])) > 2.5, -1, 1)

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, pred, title in zip(axes, [iso_pred, lof_pred, z_pred],
                            ["Isolation Forest", "LOF", "Z-score (1D)"]):
    ax.scatter(X[pred == 1, 0],  X[pred == 1, 1],  c="steelblue", s=15, alpha=0.6, label="Normal")
    ax.scatter(X[pred == -1, 0], X[pred == -1, 1], c="tomato",    s=60, marker="x", linewidths=2, label="Detected anomaly")
    ax.scatter(X[true_labels == -1, 0], X[true_labels == -1, 1],
               facecolors="none", edgecolors="gold", s=120, linewidths=1.5, label="True anomaly")
    ax.set_title(title)
    ax.legend(fontsize=7)
plt.suptitle("Anomaly Detection — Method Comparison", fontsize=12)
plt.tight_layout()

import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
plt.savefig(_os.path.join(_HERE, "anomaly_comparison.png"), dpi=120)
plt.show()
print("Plot saved to anomaly_comparison.png")

# Time series anomaly visualisation
np.random.seed(42)
t    = np.linspace(0, 2 * np.pi, 365)
temp = 15 + 10 * np.sin(t) + np.random.normal(0, 1, 365)
anomaly_days = [50, 150, 300]
temp[anomaly_days] += 15

rolling_z = np.zeros(365)
for i in range(30, 365):
    w = temp[i-30:i]
    rolling_z[i] = (temp[i] - w.mean()) / (w.std() + 1e-8)
rolling_detected = np.where(np.abs(rolling_z) > 3)[0]

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(temp, color="steelblue", lw=1, label="Temperature")
ax.scatter(anomaly_days, temp[anomaly_days], color="gold", zorder=5, s=80, label="True anomalies")
ax.scatter(rolling_detected, temp[rolling_detected], color="tomato", marker="x", s=60, lw=2, label="Rolling z-score detected")
ax.set_xlabel("Day")
ax.set_ylabel("°C")
ax.set_title("Time-series Anomaly Detection (rolling z-score, window=30)")
ax.legend()
plt.tight_layout()
plt.savefig(_os.path.join(_HERE, "timeseries_anomaly.png"), dpi=120)
plt.show()
print("Plot saved to timeseries_anomaly.png")
