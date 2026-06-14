# Figure Results Summary

Generated automatically from `figure_registry.json` at 2026-06-14 15:34:14.

## Figure Index

| Image | Description |
| --- | --- |
| [scaling_law_fit_and_prediction.png](scaling_law_fit_and_prediction.png) | Three-panel stacked summary of the cosine fit and cross-schedule predictions. |
| [tissue_residual_diagnostic.png](tissue_residual_diagnostic.png) | 2x2 residual comparison for early and late residual patterns across schedules. |
| [reproduce_2_mpl_fit_and_prediction.png](reproduce_2_mpl_fit_and_prediction.png) | Standalone Multi-Power Law reproduction with 7 fitted parameters and cross-schedule prediction. |

## Figure Details

### scaling_law_fit_and_prediction.png

- Data / Setting: Fit on M:100M_gpt_D:20B_scheduler:cosine_rope; predict on WSD and 8-1-1.
- Key Results: Cosine Log-space R2 = 0.905891; WSD MAPE = 1.560%; 8-1-1 MAPE = 1.599%.
- Parameters: L0 = 2.638559, A = 1.133871, C = 0.127926, alpha = 0.690522.

### tissue_residual_diagnostic.png

- Data / Setting: Early/late residual comparison on Tissue baseline and the normalized-progress correction across cosine, WSD, and 8-1-1.
- Key Results: The improved method lowers early-step residual magnitude and early MAE across schedules.
- Parameters: Built from saved residuals.csv artifacts: tissue_baseline/2026-05-31_183420 and tissue_improved/2026-05-31_225220.

### reproduce_2_mpl_fit_and_prediction.png

- Data / Setting: Train on cosine curve from the course pkl file; report WSD prediction and 8-1-1 extension.
- Key Results: Train avg log-space R² = 0.824753; Test avg log-space R² = 0.805011; Cosine log-space R² = 0.824753; WSD log-space R² = 0.804552; 811 log-space R² = 0.805471.
- Parameters: L0 = 2.150848, A = 1.369870, alpha = 0.259880, B = 150.002466, C = 1.505599, beta = 0.594647, gamma = 0.666948.

## Text Supplement

- This script now fits the full 7-parameter Multi-Power Law model.
- The script reads the course-provided gpt_loss+lrs.pkl file directly.
- Dense pkl curves are sampled at a fixed stride to match the sparse-checkpoint setting used by the MPL reproduction.
- The summary page is regenerated automatically from figure_registry.json.

## Latest Run Details

| Item | Value |
| --- | --- |
| Train avg log-space R² | 0.824753 |
| Test avg log-space R² | 0.805011 |
| Cosine log-space R² | 0.824753 |
| WSD log-space R² | 0.804552 |
| 8-1-1 log-space R² | 0.805471 |

## Script Notes

- Source file: reproduce_2.py
- Output image: reproduce_2_mpl_fit_and_prediction.png
- Metadata source: figure_registry.json
