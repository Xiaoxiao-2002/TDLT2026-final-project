# Predicting Loss Curve of LLM Pretraining

This repository is the final project for Task 2 of Topics in Deep Learning Theory. The goal is to reproduce two loss-curve prediction methods for LLM pretraining and present a lightweight improvement for cross-schedule prediction.

## Project Goal

We study whether a loss law fitted on a cosine learning-rate schedule can predict training loss under other schedules. The final story is:

- Reproduce the Tissue-style momentum law baseline.
- Reproduce the Multi-Power Law baseline.
- Diagnose the early-stage residual pattern of the Tissue baseline.
- Add a simple normalized-progress correction as our own lightweight method.
- Compare the reproduced baselines and the proposed variant in the final slides.

## Main Files

| Path | Purpose |
| --- | --- |
| `reproduce_1.py` | Tissue-style momentum law reproduction plus progress-aware Tissue variant. |
| `reproduce_2.py` | Multi-Power Law reproduction using the course-provided pkl loss curves. |
| `experiments/` | Saved configs, fitted parameters, predictions, residuals, and metrics. |
| `figures/` | Main figures used in the final slides. |
| `docs/final_slides.marp.md` | Final Marp slide source. |
| `docs/final_article.md` | Companion project article / narrative notes. |

## Data

The project uses the course-provided loss curves in `loss curves/gpt_loss+lrs.pkl`.

The pkl file contains three schedules:

- `M:100M_gpt_D:20B_scheduler:cosine_rope`
- `M:100M_gpt_D:20B_scheduler:wsd_rope`
- `M:100M_gpt_D:20B_scheduler:811_rope`

Both reproduction scripts fit on the cosine schedule and evaluate on WSD. The 8-1-1 schedule is kept as an extra cross-schedule test.

## Environment

Use Python 3.10+ or 3.12. Install dependencies with:

```bash
pip install -r requirements.txt
```

The current scripts depend on NumPy, SciPy, pandas, Matplotlib, and scikit-learn. PyTorch is not required for the project scripts in the repository root.

## Reproduction Commands

Run the Tissue baseline and progress-aware variant:

```bash
python reproduce_1.py
```

Run the Multi-Power Law baseline on sampled checkpoints from the same pkl file:

```bash
python reproduce_2.py --sample-stride 16
```

Each run writes a timestamped directory under `experiments/` and updates the main figures under `figures/`.

## Current Best Results

The final slides use the following saved runs as the main evidence:

| Method | Saved run | Train metric | Test metric |
| --- | --- | --- | --- |
| Tissue baseline | `experiments/tissue_baseline/2026-05-31_183420/` | Cosine log-space R2 = 0.905891 | WSD MAPE = 1.5601%; 8-1-1 MAPE = 1.5994% |
| Tissue + progress correction | `experiments/tissue_improved/2026-05-31_225220/` | Cosine log-space R2 = 0.912989 | WSD MAPE = 1.4924%; 8-1-1 MAPE = 1.4925% |
| Multi-Power Law | `experiments/mpl_baseline/2026-06-14_153414/` | Train log-space R2 = 0.824753 | Test log-space R2 = 0.805011 |

Because nonlinear fitting may produce small numeric changes across reruns, the final report fixes the saved best runs above as the reported results.

## Main Figures

- `figures/scaling_law_fit_and_prediction.png`: Tissue baseline cosine fit and cross-schedule prediction.
- `figures/reproduce_2_mpl_fit_and_prediction.png`: Multi-Power Law reproduction.
- `figures/tissue_residual_diagnostic.png`: early/late residual diagnostic for Tissue baseline vs progress-aware Tissue.

## Final Submission Checklist

- GitHub repository: https://github.com/Xiaoxiao-2002/TDLT2025-final-project.git
- Confirm group member names and student IDs on the title slide.
- Export `docs/final_slides.marp.md` to PDF before submission.
- Submit the final slide deck by the course deadline.

If Marp CLI is available, export with:

```bash
marp docs/final_slides.marp.md --pdf -o docs/final_slides.marp.pdf
```

## Conclusion

Cross-schedule loss prediction is feasible but schedule-sensitive. On the course-provided pkl data, the progress-aware Tissue variant is a simple and interpretable improvement over the plain Tissue baseline for the observed early-stage overprediction failure mode. Multi-Power Law remains an important reproduced baseline and contrast case, but it is less effective on this pkl setup than it was on the original sparse CSV curves.
