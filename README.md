# Predicting Loss Curves of LLM Pretraining

This repository contains the final project for Task 2 of Topics in Deep Learning Theory.
The project studies whether a loss law fitted on a cosine learning-rate schedule can predict loss curves under other schedules.

Repository: <https://github.com/Xiaoxiao-2002/TDLT2026-final-project.git>

## Project Summary

We reproduce two loss-curve prediction baselines and develop lightweight corrections to the Tissue-style momentum law:

- Tissue / momentum law: compact scaling law based on accumulated learning-rate features.
- Multi-Power Law: more expressive reproduced baseline for cross-schedule loss prediction.
- Step-progress Tissue correction: adds a decaying early transient term using normalized step progress.
- Intrinsic-progress Tissue correction: uses normalized accumulated learning-rate area as the progress variable.

The final presentation source is `docs/final_slides.md`.

## Main Files

| Path | Purpose |
| --- | --- |
| `reproduce_1.py` | Tissue baseline, step-progress correction, intrinsic-progress ablation, residual diagnostics, and comparison figure. |
| `reproduce_2.py` | Multi-Power Law reproduction using the course-provided pkl loss curves. |
| `loss curves/gpt_loss+lrs.pkl` | Course-provided cosine, WSD, and 8-1-1 loss curves. |
| `experiments/` | Saved configs, fitted parameters, predictions, residuals, and metrics. |
| `figures/` | Figures used in the final slides. |
| `docs/final_slides.md` | Final slide source with GitHub link. |
| `docs/method_development_comparison.md` | Short note comparing the two Tissue correction variants. |

## Data and Protocol

The project uses `loss curves/gpt_loss+lrs.pkl`, which contains:

- `M:100M_gpt_D:20B_scheduler:cosine_rope`
- `M:100M_gpt_D:20B_scheduler:wsd_rope`
- `M:100M_gpt_D:20B_scheduler:811_rope`

The protocol follows the course requirement:

- Fit on the cosine learning-rate schedule.
- Evaluate transfer to WSD.
- Use 8-1-1 as an additional cross-schedule stress test.

## Environment

Use Python 3.10+ or 3.12.

```bash
pip install -r requirements.txt
```

The project scripts depend on NumPy, SciPy, pandas, Matplotlib, and scikit-learn.
PyTorch is not required.

## Reproduction

Run the Tissue baseline and both Tissue correction variants:

```bash
python reproduce_1.py
```

Run the Multi-Power Law baseline:

```bash
python reproduce_2.py --sample-stride 16
```

Each run writes timestamped artifacts under `experiments/`.

## Export Slides

The repository stores the Marp slide source in `docs/final_slides.md`.
After editing, export the PDF locally with Marp or the VS Code Marp extension, then place the exported file at:

```text
docs/final_slides.pdf
```

The previous PDF export was removed from the repository because it was older than the current slide source.

## Reported Results

The final slides use these saved results:

| Method | Saved run | Fit metric | Transfer metric |
| --- | --- | --- | --- |
| Tissue baseline | `experiments/tissue_baseline/2026-05-31_183420/` | Cosine log-space R2 = 0.905891 | WSD MAPE = 1.5601%; 8-1-1 MAPE = 1.5994% |
| Tissue + step-progress correction | `experiments/tissue_improved/2026-05-31_225220/` | Cosine log-space R2 = 0.912989 | WSD MAPE = 1.4924%; 8-1-1 MAPE = 1.4925% |
| Tissue + intrinsic-progress correction | `experiments/tissue_intrinsic_progress/2026-06-16_103841/` | Cosine log-space R2 = 0.914654 | WSD MAPE = 1.5504%; 8-1-1 MAPE = 1.5766% |
| Multi-Power Law | `experiments/mpl_baseline/2026-06-14_153414/` | Train log-space R2 = 0.824753 | Test log-space R2 = 0.805011 |

Because nonlinear fitting can produce small numeric differences across reruns, the slides report the saved runs above.

## Main Figures

- `figures/scaling_law_fit_and_prediction.png`: Tissue baseline cosine fit and cross-schedule prediction.
- `figures/reproduce_2_mpl_fit_and_prediction.png`: Multi-Power Law reproduction.
- `figures/tissue_residual_diagnostic.png`: residual diagnostic for Tissue baseline and step-progress correction.
- `figures/tissue_method_comparison.png`: comparison of Tissue baseline, step-progress correction, and intrinsic-progress correction.

## Conclusion

The step-progress correction gives the best cross-schedule transfer in the current pkl setting.
The intrinsic-progress correction is theoretically cleaner and improves the cosine fit, but it transfers worse to WSD and 8-1-1 when only one fitted schedule is available.
This makes it a useful ablation rather than the final main method.
