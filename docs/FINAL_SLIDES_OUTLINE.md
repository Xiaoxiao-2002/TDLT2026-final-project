# Task 2 Final Slides Outline

## 1. Presentation Goal

The story should be simple:

1. Why loss-curve prediction matters for LLM pretraining.
2. What the two reproduced baselines do.
3. Where they fail and what pattern we observed.
4. What our lightweight improvement changes.
5. What the final conclusion is.

## 2. Recommended Slide Flow

### Slide 1. Title

- Project title: Predicting Loss Curve of LLM Pretraining.
- Task 2.
- Group members and IDs.
- GitHub repository link.

### Slide 2. Problem Introduction

- Explain why pretraining loss curves matter.
- Explain why cross-schedule prediction is useful.
- Message to emphasize: schedule changes can alter the whole training trajectory, so a good functional law is useful for prediction and analysis.

### Slide 3. Problem Setup

- Define the input: cosine schedule as training source, WSD as the required target schedule, and 8-1-1 as an extra target schedule.
- Define the output: predict future loss curve from fitted parameters.
- Mention the evaluation metrics we use: log-space R², MAPE, MAE, RMSE, PredE.

### Slide 4. Baseline 1: Tissue / Momentum Law

- Show the model form in one formula block.
- Use the existing fit-and-prediction figure:
  - [scaling_law_fit_and_prediction.png](../figures/scaling_law_fit_and_prediction.png)
- Key message:
  - It fits cosine reasonably.
  - It overpredicts strongly in early steps.
  - Cross-schedule test error is acceptable but not ideal.

### Slide 5. Baseline 2: Multi-Power Law

- Show the 7-parameter MPL form.
- Use the existing fit-and-prediction figure:
  - [reproduce_2_mpl_fit_and_prediction.png](../figures/reproduce_2_mpl_fit_and_prediction.png)
- Key message:
  - It uses the same course pkl data as the Tissue reproduction.
  - It fits cosine and predicts WSD plus 8-1-1.
  - It is the more expressive reproduced baseline and contrast case.

### Slide 6. Evidence of Failure Mode

- Show the residual-pattern summary table from `experiments/SUMMARY.md`.
- Use one compact visual if available later: early-vs-late residual bar chart.
- Key message:
  - Tissue's early residuals are consistently negative, meaning it overpredicts at the beginning.
  - This is the main target for our method.

### Slide 7. Our Method Candidate

- Name: Tissue + normalized-progress correction.
- Intuition:
  - Keep the original structure.
  - Add a light correction that depends on training progress.
- Key benefit:
  - Improves test MAPE on WSD and 8-1-1 without making the model much more complicated.

### Slide 8. Comparison Table

- Use a compact table based on `experiments/COMPARISON.md`.
- Show three rows:
  - Tissue baseline.
  - Tissue + normalized-progress correction.
  - MPL baseline.
- Key message:
  - MPL is the more expressive reproduced baseline and contrast case.
  - The improved Tissue variant is our method candidate and improves over the plain Tissue baseline.

### Slide 9. Conclusions

- Problem conclusion:
  - Cross-schedule loss prediction is feasible, but the loss trajectory is highly schedule-sensitive.
- Method conclusion:
  - A lightweight normalized-progress correction can reduce the early transient mismatch of the Tissue baseline.
- Experimental conclusion:
  - MPL remains an important reproduced baseline and contrast case.
  - Our improved Tissue variant is a simple but effective alternative candidate.
- One-sentence takeaway:
  - The best practical recipe is to use progress-aware correction when the early-stage loss transient is the dominant error source, while keeping MPL as a reproduced contrast baseline.

### Slide 10. Limitations and Future Work

- The current improvement is still lightweight and may not fully capture all schedule changes.
- A stronger schedule-aware term or a schedule-encoding variant may be a natural next step.
- Mention possible future work: better residual modeling, more schedules, more robust fitting.
- If there is time, mention that the current method is intentionally simple so that it stays explainable and easy to reproduce.

## 3. Figure Plan

### Already Available

- [figures/scaling_law_fit_and_prediction.png](../figures/scaling_law_fit_and_prediction.png)
- [figures/reproduce_2_mpl_fit_and_prediction.png](../figures/reproduce_2_mpl_fit_and_prediction.png)
- [figures/tissue_residual_diagnostic.png](../figures/tissue_residual_diagnostic.png)
- [experiments/SUMMARY.md](../experiments/SUMMARY.md)
- [experiments/COMPARISON.md](../experiments/COMPARISON.md)

### Still Worth Adding Before Final Slides

- One compact comparison table figure if the slide layout needs a visual instead of Markdown.

## 4. Conclusion Framework

Use the following logic on the last few slides:

1. Baseline reproduction is successful and reproducible.
2. MPL gives a more expressive reproduced contrast baseline on the same pkl data.
3. Tissue baseline reveals a clear early-stage overprediction issue.
4. The normalized-progress correction reduces that error and is a viable lightweight method.
5. The project contribution is a practical comparison plus a simple but effective improvement.

## 5. What to Say Verbally

- Do not over-explain formulas.
- Focus on the empirical story and the error pattern.
- Keep the narrative anchored to the question: can we predict loss curves across schedules?
- The final answer should sound like a concise research conclusion, not a code walkthrough.
