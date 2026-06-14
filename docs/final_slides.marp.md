---
marp: true
theme: gaia
paginate: true
size: 16:9
backgroundColor: #ffffff
color: #1f2937
style: |
  section {
    font-family: "Noto Serif CJK SC", "Source Han Serif SC", serif;
    letter-spacing: 0.2px;
    font-size: 32px;
    line-height: 1.30;
  }
  h1, h2, h3 {
    color: #0f172a;
    line-height: 1.16;
  }
  strong {
    color: #0b5cab;
  }
  .muted {
    color: #5b6472;
  }
  .small {
    font-size: 1em;
  }
  .figure-center {
    display: flex;
    justify-content: center;
  }
  .figure-center img {
    display: block;
    max-width: none;
  }
  section.figure-slide h2 {
    margin-bottom: 0.45em;
  }
  section.figure-slide .figure-center {
    margin-top: 0.1em;
  }
  .figure-1000 img {
    width: 1000px !important;
  }
  .figure-1100 img {
    width: 1100px !important;
  }
  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    align-items: start;
  }
  .callout {
    background: #eef5ff;
    border-left: 6px solid #0b5cab;
    padding: 16px 18px;
    border-radius: 10px;
  }
  section.title-slide h2 {
    margin-bottom: 2.2em;
  }
  section.title-slide .muted {
    margin-top: 0;
  }
---

<!-- _class: title-slide -->

# Predicting Loss Curve of LLM Pretraining

## Task 2 Final Project

<div class="muted">
Group: Tianze Lu · Ruoyu Wang · Feiyue Ye

Student IDs: confirm before submission

GitHub repository: TODO - create repository and paste URL before submission
</div>

---

## Why this problem matters

- Pretraining loss curves are the most direct signal of whether an LLM training run is healthy.
- If we can predict the loss curve under a new learning-rate schedule, we can reduce schedule tuning cost.
- Task 2 asks us to fit on cosine and predict on WSD, then go beyond the reproduced baselines.

<div class="callout">
The core question is not just fitting one curve well, but transferring the fitted law across different learning-rate schedules.
</div>

---

## Problem setup

- Train on the cosine schedule.
- Predict on WSD, with 8-1-1 as an extra cross-schedule test.
- Use the observed loss curve together with the schedule signal.

<div class="callout">
The task is to transfer a fitted law across schedules, not only to fit one curve well.
</div>

---

## Evaluation

- Main metrics: log-space R² and MAPE.
- Secondary metrics: MAE, RMSE, PredE, and WorstE.
- The final comparison focuses on cross-schedule test error.
- Reported numbers use the saved best runs under `experiments/`.

---

## Baseline 1: Tissue / Momentum Law

The simplified form is:

$$
L(t) = L_0 + A S_1(t)^{-\alpha} - C S_2(t)
$$

- Fits the cosine schedule reasonably well.
- But it tends to **overpredict early-stage loss**.
- That early transient mismatch is the main weakness we observed.
- Full curve visualization is on the next slide.

---

<!-- _class: figure-slide -->

## Baseline 1: Full Figure

<div class="figure-center figure-1000">

<img src="../figures/scaling_law_fit_and_prediction.png" alt="Baseline 1 figure" />

</div>

---

## Baseline 2: Multi-Power Law

The 7-parameter MPL is more expressive:

$$
L(t) = L_0 + A S_1(t)^{-\alpha} + B \cdot \text{drop}(t)
$$

- More flexible seven-parameter form.
- Uses the same course pkl data as the Tissue reproduction.
- Fits on cosine and predicts WSD plus 8-1-1.
- This is the more expressive reproduced baseline.
- Full curve visualization is on the next slide.

---

<!-- _class: figure-slide -->

## Baseline 2: Full Figure

<div class="figure-center figure-1000">

<img src="../figures/reproduce_2_mpl_fit_and_prediction.png" alt="Baseline 2 figure" />

</div>

---

<!-- _class: figure-slide -->

## Failure mode we found

<div class="figure-center figure-1100">

<img src="../figures/tissue_residual_diagnostic.png" alt="Residual diagnostic figure" />

</div>

<div class="small muted">
The early-step residuals are consistently negative in the plain Tissue baseline, meaning the model overpredicts the early transient.
</div>

---

## Our method candidate

We keep the original Tissue structure and add a small progress-aware correction:

$$
L(t) = L_0 + A S_1(t)^{-\alpha} - C S_2(t) - D e^{-\tau p(t)}
$$

where $p(t)$ is normalized progress from 0 to 1.

**Why this helps**

- It changes only the part that fails most clearly.
- It stays simple and interpretable.
- It reduces the early-step mismatch without redesigning the whole model.

---

## Main results

| Method | Fit metric | Test metric |
| --- | --- | --- |
| Tissue baseline | Cosine log-space R² = 0.905891 | WSD MAPE = 1.5601%; 8-1-1 MAPE = 1.5994% |
| Tissue + progress correction | Cosine log-space R² = 0.912989 | WSD MAPE = 1.4924%; 8-1-1 MAPE = 1.4925% |
| MPL baseline | Train log-space R² = 0.824753 | Test log-space R² = 0.805011 |

<div class="callout">
The lightweight progress-aware Tissue variant improves the plain baseline, while MPL provides a more expressive reproduction baseline on the same pkl data.
</div>

---

## What we conclude

- Cross-schedule loss prediction is feasible, but the trajectory is highly schedule-sensitive.
- The plain Tissue baseline has a clear early transient error.
- The normalized-progress correction reduces that error and improves test MAPE.
- MPL remains an important reproduced baseline and contrast case.

<div class="callout">
Final choice: use the progress-aware Tissue variant as the project's own lightweight method, and use MPL as the second reproduced baseline.
</div>

---

## Limitations and next steps

- The current improvement is still lightweight and may not capture every schedule change.
- A more expressive schedule-aware term is a natural next step.
- If time allows, the final version can add one more ablation or a stronger schedule encoding.

<div class="muted small">
Thank you.
</div>
