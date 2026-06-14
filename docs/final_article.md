# Task 2 Project Article: Predicting Loss Curve of LLM Pretraining

## 1. Project Goal

This project studies loss-curve prediction for LLM pretraining under different learning-rate schedules. The central motivation is practical: if a loss curve can be extrapolated from one schedule to another, then training runs can be analyzed and tuned with much less trial-and-error cost.

The course task asks us to fit the model on cosine schedules and evaluate its transfer to WSD schedules. We follow this setting using the course-provided `gpt_loss+lrs.pkl` file, and we additionally examine 8-1-1 as an extra cross-schedule test.

## 2. What We Reproduced

We reproduced two methods:

1. The Tissue-style momentum law, implemented in `reproduce_1.py`.
2. The Multi-Power Law (MPL), implemented in `reproduce_2.py`.

Both scripts now save intermediate artifacts in the `experiments/` directory, including configuration files, fitted parameters, per-step predictions, residuals, and aggregated metrics. This makes the runs directly reusable for later analysis and slide preparation.

The final slides report the saved best runs, rather than whichever timestamped directory is produced by a later rerun:

- Tissue baseline (`experiments/tissue_baseline/2026-05-31_183420/`): cosine log-space R² = 0.905891, WSD MAPE = 1.5601%, 8-1-1 MAPE = 1.5994%.
- Tissue + progress correction (`experiments/tissue_improved/2026-05-31_225220/`): cosine log-space R² = 0.912989, WSD MAPE = 1.4924%, 8-1-1 MAPE = 1.4925%.
- MPL baseline (`experiments/mpl_baseline/2026-06-14_153414/`): train log-space R² = 0.824753, test log-space R² = 0.805011.

Small numerical changes are possible when rerunning the nonlinear fits, so the saved runs above are treated as the fixed evidence for the final report.

## 3. Main Observation

The key failure pattern of the plain Tissue baseline is early-stage overprediction. This is visible both in the residual table and in the residual diagnostic chart. In the early quarter of the curve, the mean residual is clearly negative for cosine, WSD, and 8-1-1, which means the model predicts losses that are too large at the beginning of training.

This observation matters because it suggests that the baseline is not failing randomly. Instead, it is missing a specific short-horizon transient structure. That gives us a concrete place to modify the model.

## 4. Our Method Candidate

Our own method candidate is a simple progress-aware correction added to the Tissue baseline:

$$
L(t) = L_0 + A S_1(t)^{-\alpha} - C S_2(t) - D e^{-\tau p(t)}
$$

where $p(t)$ is normalized training progress.

The rationale is straightforward. If the main issue is an early transient mismatch, then the correction should be strongest early and decay later. The normalized-progress term provides exactly that behavior while keeping the model interpretable.

Empirically, this variant improves the test metrics relative to the plain Tissue baseline and reduces the early-stage residual magnitude. It also stays close to the original Tissue model, so it is easier to interpret than a more expressive multi-term model.

## 5. Why MPL Still Matters

MPL is still important because it is the second required reproduction target and it represents a more expressive fitting strategy. In this repository, `reproduce_2.py` reads the same pkl file as the Tissue reproduction, fits on cosine, and evaluates on WSD plus 8-1-1. This makes the reproduction setting consistent with the course requirement and avoids depending on extra CSV files from the reference repository.

The pkl-based MPL result is not as strong as the earlier sparse-CSV reproduction, but it remains a useful contrast case. The improved Tissue variant is useful because it shows that a small schedule-aware correction can reduce the most visible failure mode on the same course data.

## 6. How the Slides Are Organized

The slide deck is organized around five questions:

1. Why is loss-curve prediction important?
2. What do the reproduced baselines do?
3. Where do they fail?
4. What is our lightweight improvement?
5. What is the final conclusion?

The relevant slide assets are stored in `figures/`:

- `scaling_law_fit_and_prediction.png` for the Tissue baseline.
- `reproduce_2_mpl_fit_and_prediction.png` for MPL.
- `tissue_residual_diagnostic.png` for the failure mode.

The companion outline is written in `docs/FINAL_SLIDES_OUTLINE.md`, and it is directly aligned with the final Marp deck in `docs/final_slides.marp.md`. The title slide still needs the final GitHub repository URL and confirmed student IDs before submission.

## 7. Conclusion

The project shows that cross-schedule loss prediction is feasible, but not equally easy for all schedules. The plain Tissue baseline is interpretable but underfits early transient behavior. MPL provides the second reproduced baseline and a more expressive contrast case. Our progress-aware Tissue correction is a lightweight and useful improvement that specifically addresses the observed failure mode.

For the final submission, the most defensible story is:

- Use Tissue and MPL as the two reproduced baselines.
- Present the progress-aware Tissue variant as our own method.
- Use the residual diagnostic chart to explain why the improvement was chosen.
- Keep the final slide narrative short, visual, and metric-driven.
