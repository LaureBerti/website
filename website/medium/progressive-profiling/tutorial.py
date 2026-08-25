"""
Progressive sampling for data quality profiling — a runnable, self-contained
teaching version of the benchmark in:

  L. Berti-Equille, "Data Quality Profiling at Scale with Progressive Sampling:
  A Benchmark for Data-Centric AI Pipelines", Transactions on Large-Scale Data-
  and Knowledge-Centered Systems (TLDKS), Springer.

The paper benchmarks 9 samplers on real datasets up to 7.4M rows. Here we
reproduce its *qualitative* finding on a small synthetic dataset you can run in
seconds: representativeness beats domain knowledge — a schema-free random or
cluster sample estimates the data quality profile more accurately than a
proxy-guided MCMC sampler that deliberately hunts for "dirty" rows.

Numbers printed here are computed live on synthetic data and are illustrative;
the paper's headline results (e.g. 0.49% error for random uniform vs 19.5% for
DAG-MCMC on NYC 311 at a 5% budget) come from the real datasets.
"""
import os
import time

import matplotlib
matplotlib.use("Agg")  # headless-safe: save figures, never plt.show()
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_FIG = os.path.join(_HERE, "figures")
os.makedirs(_FIG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Quality profile — four indicators, matching the paper's definitions
# ─────────────────────────────────────────────────────────────────────────────
def compute_quality_profile(df, weights=None):
    """Missing, duplicate, outlier and inconsistency rates for a DataFrame.

    weights: optional per-row importance weights (Horvitz-Thompson correction).
    A biased sampler that over-samples dirty rows must down-weight them, or its
    profile is inflated. Blind samplers pass weights=None (uniform).
    """
    n = len(df)
    if n == 0:
        return dict(missing_rate=0.0, duplicate_rate=0.0, outlier_rate=0.0,
                    inconsistency_rate=0.0)
    w = np.ones(n) if weights is None else np.asarray(weights, dtype=float)
    w = w / w.sum()

    numeric = df.select_dtypes(include=[np.number])

    # missing: weighted fraction of missing cells
    miss_cell = df.isna().to_numpy().mean(axis=1)                 # per-row
    missing_rate = float(np.dot(w, miss_cell))

    # duplicate: weighted fraction of rows that are non-first duplicates
    dup = df.duplicated(keep="first").to_numpy().astype(float)
    duplicate_rate = float(np.dot(w, dup))

    # outlier: weighted fraction of numeric cells outside Tukey (1.5*IQR) fences
    if numeric.shape[1]:
        arr = numeric.to_numpy(dtype=float)
        q1 = np.nanpercentile(arr, 25, axis=0)
        q3 = np.nanpercentile(arr, 75, axis=0)
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        out = ((arr < lo) | (arr > hi))
        out_row = np.nan_to_num(out).mean(axis=1)
        outlier_rate = float(np.dot(w, out_row))
    else:
        outlier_rate = 0.0

    # inconsistency: violations of the functional dependency zip -> city.
    # A row violates if its city differs from the modal city for its zip
    # (so we count the actual bad rows, not every row of an impure zip).
    inconsistency_rate = 0.0
    if {"zip", "city"}.issubset(df.columns):
        modal = df.groupby("zip")["city"].transform(
            lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0]
        )
        viol = (df["city"].to_numpy() != modal.to_numpy()).astype(float)
        inconsistency_rate = float(np.dot(w, viol))

    return dict(missing_rate=missing_rate, duplicate_rate=duplicate_rate,
                outlier_rate=outlier_rate, inconsistency_rate=inconsistency_rate)


def bounded_relative_error(est, gt):
    """Mean bounded relative error across indicators (paper's metric).

    Denominator floor = max(gt, 0.05) prevents blow-up near zero; each
    per-indicator error is capped at 1.0 (100%).
    """
    errs = []
    for k in gt:
        errs.append(min(abs(est[k] - gt[k]) / max(gt[k], 0.05), 1.0))
    return float(np.mean(errs))


# ─────────────────────────────────────────────────────────────────────────────
# 2. Samplers — two blind, one proxy-guided (matching the paper's two families)
# ─────────────────────────────────────────────────────────────────────────────
def sample_random_uniform(df, k, rng):
    idx = rng.choice(len(df), size=min(k, len(df)), replace=False)
    return df.iloc[idx], None


def sample_cluster(df, k, rng):
    """k = max(10, sqrt(N)) contiguous blocks; draw whole blocks until budget met."""
    n = len(df)
    n_blocks = max(10, int(np.sqrt(n)))
    blocks = np.array_split(np.arange(n), n_blocks)
    order = rng.permutation(n_blocks)
    picked, taken = [], 0
    for b in order:
        picked.append(blocks[b])
        taken += len(blocks[b])
        if taken >= k:
            break
    return df.iloc[np.concatenate(picked)], None


def _error_proxy(df):
    """Per-row error-likelihood score = outlier-col fraction + missing fraction."""
    numeric = df.select_dtypes(include=[np.number])
    score = df.isna().to_numpy().mean(axis=1)  # missing fraction
    if numeric.shape[1]:
        arr = numeric.to_numpy(dtype=float)
        q1 = np.nanpercentile(arr, 25, axis=0)
        q3 = np.nanpercentile(arr, 75, axis=0)
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        out = np.nan_to_num((arr < lo) | (arr > hi)).mean(axis=1)
        score = score + out
    return score + 1e-6  # keep strictly positive for weighting


def sample_metropolis(df, k, rng):
    """Proxy-guided: sample rows with probability proportional to a dirtiness proxy.

    Because it over-samples dirty rows, it returns Horvitz-Thompson weights
    (w propto 1/prob) so compute_quality_profile can de-bias the estimate.
    """
    proxy = _error_proxy(df)
    prob = proxy / proxy.sum()
    k = min(k, len(df))
    idx = rng.choice(len(df), size=k, replace=False, p=prob)
    weights = 1.0 / prob[idx]  # inverse-probability (HT) weights
    return df.iloc[idx], weights


SAMPLERS = {
    "random_uniform (blind)": sample_random_uniform,
    "cluster (blind)": sample_cluster,
    "metropolis (proxy-guided)": sample_metropolis,
}


# ─────────────────────────────────────────────────────────────────────────────
# 3. A synthetic dataset with known, injected quality problems
# ─────────────────────────────────────────────────────────────────────────────
def make_dirty_dataset(n=200_000, seed=0):
    rng = np.random.default_rng(seed)
    age = rng.normal(40, 12, n)
    out_mask = rng.random(n) < 0.01                      # ~1% extreme outliers
    age[out_mask] += rng.normal(300, 50, out_mask.sum())
    income = rng.lognormal(10.5, 0.6, n)
    zips = rng.integers(10000, 10050, n).astype(str)
    cities = np.where(rng.random(n) < 0.03, "MysteryCity",  # FD violations zip->city
                      pd.Series(zips).map(lambda z: f"City_{z[-2:]}").to_numpy())
    df = pd.DataFrame({"age": age, "income": income, "zip": zips, "city": cities})
    # inject missing values (~4% of cells in two columns)
    for col in ("age", "income"):
        mask = rng.random(n) < 0.04
        df.loc[mask, col] = np.nan
    # inject duplicate rows (~2%)
    dup_idx = rng.choice(n, size=int(0.02 * n), replace=False)
    df = pd.concat([df, df.iloc[dup_idx]], ignore_index=True)
    return df.sample(frac=1.0, random_state=seed).reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Progressive benchmark: error vs budget, averaged over seeds
# ─────────────────────────────────────────────────────────────────────────────
def run_benchmark(df, budgets=(0.01, 0.02, 0.05, 0.10, 0.20), seeds=(0, 1, 2, 3, 4)):
    gt = compute_quality_profile(df)  # full-scan ground truth
    print(f"Full-scan profile (ground truth) on {len(df):,} rows:")
    for k, v in gt.items():
        print(f"  {k:20s} {v:.4f}")
    print()

    results = {name: {"err": [], "time": []} for name in SAMPLERS}
    for name, fn in SAMPLERS.items():
        for b in budgets:
            errs, times = [], []
            for s in seeds:
                rng = np.random.default_rng(1000 + s)
                k = int(b * len(df))
                t0 = time.perf_counter()
                sample, weights = fn(df, k, rng)
                est = compute_quality_profile(sample, weights=weights)
                times.append(time.perf_counter() - t0)
                errs.append(bounded_relative_error(est, gt))
            results[name]["err"].append(np.mean(errs))
            results[name]["time"].append(np.mean(times))
        print(f"{name:28s} error@5% = {results[name]['err'][budgets.index(0.05)]:.3%}")
    return gt, list(budgets), results


# ─────────────────────────────────────────────────────────────────────────────
# 5. Visualisation
# ─────────────────────────────────────────────────────────────────────────────
def plot_error_vs_budget(budgets, results):
    plt.figure(figsize=(7, 4.5))
    for name, r in results.items():
        plt.plot([b * 100 for b in budgets], [e * 100 for e in r["err"]],
                 marker="o", label=name)
    plt.xlabel("Sampling budget (% of rows scanned)")
    plt.ylabel("Mean bounded relative error (%)")
    plt.title("Profiling accuracy vs sampling budget")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    out = os.path.join(_FIG, "error_vs_budget.png")
    plt.savefig(out, dpi=120)
    plt.close()
    print(f"Plot saved to {out}")


def plot_error_at_budget(budgets, results, budget=0.05):
    i = budgets.index(budget)
    names = list(results)
    errs = [results[n]["err"][i] * 100 for n in names]
    colors = ["#2a9d8f", "#2a9d8f", "#e76f51"]  # blind green, proxy orange
    plt.figure(figsize=(7, 4))
    plt.barh(names, errs, color=colors)
    for y, e in enumerate(errs):
        plt.text(e + 0.2, y, f"{e:.2f}%", va="center")
    plt.xlabel(f"Mean bounded relative error (%) at {int(budget*100)}% budget")
    plt.title("Representativeness beats domain knowledge")
    plt.tight_layout()
    out = os.path.join(_FIG, "error_at_5pct.png")
    plt.savefig(out, dpi=120)
    plt.close()
    print(f"Plot saved to {out}")


if __name__ == "__main__":
    print("Building synthetic dirty dataset...\n")
    df = make_dirty_dataset(n=200_000, seed=0)
    gt, budgets, results = run_benchmark(df)
    plot_error_vs_budget(budgets, results)
    plot_error_at_budget(budgets, results, budget=0.05)
    print("\nTakeaway: the blind samplers match the full-scan profile at a few "
          "percent of the data; the proxy-guided sampler pays for its bias.")
