# Medium Stories — Laure Berti-Equille

Published data-science / data-quality tutorials, each with runnable code and figures.
Medium profile: https://medium.com/@laure.berti2

| Published | Story (read on Medium) | Post | Code |
|-----------|------------------------|------|------|
| 2026-08-14 | [Data Quality Profiling at Scale: Why Random Sampling Beats Clever Sampling](https://medium.com/@laure.berti2/data-quality-profiling-at-scale-why-random-sampling-beats-clever-sampling-96d82eafc76f) | [post](progressive-profiling/1-progressive-profiling-post.md) | [`progressive-profiling/`](progressive-profiling/) · [tutorial.py](progressive-profiling/tutorial.py) |
| 2026-05-20 | [Anomaly Detection from Classical Methods, Deep Learning to LLM Zero-Shot Detectors](https://medium.com/@laure.berti2/anomaly-detection-from-classical-methods-deep-learning-to-llm-zero-shot-detectors-ad5a98d2f79e) | [post](anomaly-detection/anomaly-detection-llms-post.md) | [`anomaly-detection/`](anomaly-detection/) · [tutorial.py](anomaly-detection/tutorial.py) |
| 2026-05-20 | [Uncertainty Quantification for ML Practitioners: Conformal Prediction, Ensembles, and When to Trust Your Model](https://medium.com/@laure.berti2/when-to-trust-your-model-uncertainty-quantification-for-ml-practitioners-fa0be4e7a4de) | [post](uncertainty-quantification/uncertainty-quantification-post.md) | [`uncertainty-quantification/`](uncertainty-quantification/) · [tutorial.py](uncertainty-quantification/tutorial.py) |
| 2026-05-06 | [The Statistical Integrity Trap: What Every Data Scientist Must Know](https://medium.com/@laure.berti2/the-statistical-integrity-trap-what-every-data-scientist-must-know-4cefcf95d2b5) | [post](p-hacking-data-snooping/3-p-hacking-data-snooping-post.md) | [`p-hacking-data-snooping/`](p-hacking-data-snooping/) · [tutorial.py](p-hacking-data-snooping/tutorial.py) |

Each folder contains the post Markdown, a self-contained `tutorial.py`, and its `figures/`.

```bash
cd <story-folder>
pip install numpy pandas matplotlib scikit-learn scipy   # per-tutorial deps
python3 tutorial.py
```
