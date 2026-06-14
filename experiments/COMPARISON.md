# Method Comparison

## Current Best Runs

| Method | Train Metric | Test Metric | Verdict |
| --- | --- | --- | --- |
| Tissue baseline | Log-space R² = 0.905891 | WSD MAPE = 1.5601%, 8-1-1 MAPE = 1.5994% | Simple baseline, useful as contrast. |
| Tissue + normalized-progress correction | Log-space R² = 0.912989 | WSD MAPE = 1.4924%, 8-1-1 MAPE = 1.4925% | Best own-method candidate so far. |
| MPL baseline | Train log-space R² = 0.824753 | Test log-space R² = 0.805011 | More expressive reproduced baseline on the same pkl data. |

## Takeaway

- The normalized-progress correction improves the Tissue model without changing the overall framework too much.
- The early-step residuals are smaller in the improved Tissue run than in the plain Tissue baseline across all schedules, which matches the intended correction.
- MPL remains important as the reproduced multi-power-law baseline and contrast case.
- Final choice: present the normalized-progress Tissue variant as the project's own method candidate, with MPL as the second reproduced baseline.
