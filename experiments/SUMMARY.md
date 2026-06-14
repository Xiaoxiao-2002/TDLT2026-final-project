# Baseline Experiment Summary

## Latest Runs

- Tissue baseline: `experiments/tissue_baseline/2026-05-31_183420/`
- MPL baseline: `experiments/mpl_baseline/2026-06-14_153414/`

## Key Metrics

| Baseline | Train Metric | Test Metric | Notes |
| --- | --- | --- | --- |
| Tissue | Log-space R² = 0.905891 | WSD MAPE = 1.5601%, 8-1-1 MAPE = 1.5994% | Prediction overshoots strongly in early steps, then gets closer later. |
| Tissue + progress correction | Log-space R² = 0.912989 | WSD MAPE = 1.4924%, 8-1-1 MAPE = 1.4925% | Normalized-progress transient correction improves cross-schedule test error. |
| MPL | Train log-space R² = 0.824753 | Test log-space R² = 0.805011 | More expressive reproduced baseline, evaluated on sampled checkpoints from the same pkl data. |

## Residual Pattern Diagnosis

- Tissue baseline shows a strong early-step overprediction: the mean residual is negative early in all schedules and approaches zero later.
- The progress-aware Tissue variant reduces the clearest early-stage Tissue failure mode.
- The pkl-based MPL reproduction is now evaluated on cosine, WSD, and 8-1-1 from the same course data source.

## Working Interpretation

- The current Tissue form seems too rigid for the early loss transient.
- The normalized-progress correction is a better lightweight method candidate than the S1-based correction.
- MPL remains the more expressive reproduced baseline, while the improved Tissue variant is the main own-method candidate.
