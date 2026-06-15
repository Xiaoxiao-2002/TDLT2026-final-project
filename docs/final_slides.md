---
marp: true
theme: gaia
paginate: true
size: 16:9
backgroundColor: #fbfcfe
color: #172033
style: |
  :root {
    --ink: #172033;
    --muted: #5d6b82;
    --line: #d7dde8;
    --blue: #0b5cab;
    --teal: #0f8b8d;
    --coral: #e95f45;
    --pale: #eef5ff;
    --soft: #f4f7fb;
    --dark: #111827;
  }
  section {
    font-family: "Noto Serif CJK SC", "Source Han Serif SC", "Cambria", serif;
    font-size: 29px;
    line-height: 1.28;
    letter-spacing: 0;
    padding: 58px 72px 50px 72px;
    background: #fbfcfe;
  }
  section::after {
    color: #718096;
    font-size: 18px;
  }
  h1, h2, h3 {
    color: var(--ink);
    line-height: 1.12;
    margin: 0 0 20px 0;
    letter-spacing: 0;
  }
  h1 {
    font-size: 58px;
  }
  h2 {
    font-size: 42px;
  }
  h3 {
    font-size: 26px;
  }
  p, li {
    color: var(--ink);
  }
  ul {
    margin: 0;
    padding-left: 1.05em;
  }
  li {
    margin: 0.22em 0;
  }
  strong {
    color: var(--blue);
  }
  table {
    font-size: 22px;
    width: 100%;
  }
  th {
    background: #e9f2ff;
    color: #14355f;
  }
  td, th {
    padding: 9px 12px;
  }
  code {
    font-family: "Consolas", "Cascadia Mono", monospace;
    color: #153e75;
  }
  .muted {
    color: var(--muted);
  }
  .small {
    font-size: 22px;
  }
  .tiny {
    font-size: 18px;
  }
  .kicker {
    color: var(--teal);
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  .title-slide {
    background: #f7f9fc;
    color: #0b1220;
    border-left: 34px solid #0b1730;
  }
  .title-slide h1,
  .title-slide h2,
  .title-slide p,
  .title-slide .muted {
    color: #0b1220;
  }
  .title-slide h1 {
    max-width: 920px;
    margin-top: 36px;
  }
  .title-slide h2 {
    font-size: 30px;
    color: #1f2937;
    margin-top: 14px;
    margin-bottom: 92px;
  }
  .title-meta {
    border-left: 7px solid #0b5cab;
    padding-left: 20px;
    font-size: 23px;
    color: #0b1220;
  }
  .hero-stat {
    position: absolute;
    right: 76px;
    bottom: 68px;
    width: 310px;
    padding: 22px 24px;
    background: #ffffff;
    border: 1px solid #cfd8e6;
    box-shadow: 0 16px 42px rgba(15, 23, 42, 0.12);
  }
  .hero-stat .num {
    font-size: 54px;
    font-weight: 800;
    color: #0b5cab;
  }
  .hero-stat .label {
    font-size: 19px;
    color: #334155;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 26px;
    align-items: start;
  }
  .grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }
  .panel {
    background: #ffffff;
    border: 1px solid var(--line);
    padding: 20px 22px;
    min-height: 128px;
  }
  .panel.dark {
    background: #172033;
    color: #ffffff;
    border: none;
  }
  .panel.dark h3,
  .panel.dark p {
    color: #ffffff;
  }
  .panel.accent {
    border-left: 8px solid var(--coral);
  }
  .panel.teal {
    border-left: 8px solid var(--teal);
  }
  .panel.blue {
    border-left: 8px solid var(--blue);
  }
  .metric-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-top: 18px;
  }
  .metric {
    background: #ffffff;
    border: 1px solid var(--line);
    padding: 20px 18px;
    min-height: 120px;
  }
  .metric .value {
    font-size: 40px;
    font-weight: 800;
    color: var(--blue);
    line-height: 1;
  }
  .metric .label {
    margin-top: 10px;
    font-size: 19px;
    color: var(--muted);
  }
  .flow {
    display: grid;
    grid-template-columns: 1fr 40px 1fr 40px 1fr;
    gap: 12px;
    align-items: center;
    margin-top: 18px;
  }
  .arrow {
    text-align: center;
    color: var(--coral);
    font-size: 36px;
    font-weight: 800;
  }
  .tag {
    display: inline-block;
    background: var(--pale);
    color: #153e75;
    border: 1px solid #c9def8;
    padding: 4px 10px;
    font-size: 18px;
    font-weight: 700;
    margin: 0 6px 8px 0;
  }
  .formula {
    background: #ffffff;
    border-left: 8px solid var(--blue);
    padding: 18px 22px 14px 22px;
    margin: 12px 0 18px 0;
    font-size: 28px;
  }
  .formula.compact {
    font-size: 20px;
    padding: 12px 16px 10px 16px;
    margin: 10px 0 14px 0;
  }
  .figure-center {
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .figure-center img {
    display: block;
    max-width: none;
  }
  .figure-980 img {
    width: 980px !important;
  }
  .figure-1060 img {
    width: 1060px !important;
  }
  .figure-1120 img {
    width: 1120px !important;
  }
  section.figure-slide {
    padding-top: 44px;
  }
  section.figure-slide h2 {
    margin-bottom: 10px;
  }
  .caption {
    font-size: 19px;
    color: var(--muted);
    text-align: center;
    margin-top: 8px;
  }
  .result-table table {
    font-size: 20px;
  }
  .conclusion {
    background: linear-gradient(135deg, #111827 0%, #153e75 70%, #0f8b8d 100%);
    color: #ffffff;
  }
  .conclusion h2,
  .conclusion h3,
  .conclusion p,
  .conclusion li,
  .conclusion .muted {
    color: #ffffff;
  }
---

<!-- _class: title-slide -->

<div class="kicker">Topics in Deep Learning Theory - Task 2</div>

# Predicting Loss Curves of LLM Pretraining

## Cosine-to-WSD transfer with reproduced scaling-law baselines and a progress-aware correction

<div class="title-meta">
Group: Tianze Lu · Ruoyu Wang · Feiyue Ye<br>
Student IDs: 2501110068 · 2501111525 · 2501111527<br>
Repository: https://github.com/Xiaoxiao-2002/TDLT2026-final-project.git
</div>

<div class="hero-stat">
<div class="num">1.492%</div>
<div class="label">WSD MAPE after our progress-aware Tissue correction</div>
</div>

---

## Project Requirements Covered

<div class="grid-3">
<div class="panel blue">
<h3>Reproduction</h3>
<p class="small">Implement Tissue / momentum law and Multi-Power Law under the same cosine-to-WSD setting.</p>
</div>
<div class="panel teal">
<h3>Diagnosis</h3>
<p class="small">Use residuals and schedule-wise prediction plots to locate baseline failure modes.</p>
</div>
<div class="panel accent">
<h3>Method</h3>
<p class="small">Propose a lightweight correction fitted on cosine and tested on WSD and 8-1-1.</p>
</div>
</div>

<div class="metric-row">
<div class="metric">
<div class="value">3</div>
<div class="label">learning-rate schedules: cosine, WSD, 8-1-1</div>
</div>
<div class="metric">
<div class="value">2</div>
<div class="label">reproduced baselines: Tissue and MPL</div>
</div>
<div class="metric">
<div class="value">1</div>
<div class="label">interpretable progress-aware variant</div>
</div>
</div>

---

## Motivation

<div class="grid-2">
<div>

Pretraining loss curves are often the earliest reliable signal of whether a run is healthy.

- Full LLM pretraining runs are expensive.
- Learning-rate schedules change the entire optimization trajectory.
- A transferable loss law lets us estimate a new schedule before running a full pretraining experiment.

</div>
<div class="panel dark">
<h3>Central question</h3>
<p>Can a loss law fitted only on a cosine schedule predict the loss curve under WSD?</p>
<p class="small muted">The project is about cross-schedule transfer, not only curve fitting.</p>
</div>
</div>

---

## Data and Evaluation Protocol

<div class="flow">
<div class="panel blue">
<h3>Fit</h3>
<p class="small">Course pkl curve with cosine learning-rate schedule.</p>
</div>
<div class="arrow">></div>
<div class="panel teal">
<h3>Predict</h3>
<p class="small">WSD is the required target schedule; 8-1-1 is an extra stress test.</p>
</div>
<div class="arrow">></div>
<div class="panel accent">
<h3>Evaluate</h3>
<p class="small">Use log-space R², MAPE, MAE, RMSE, PredE, and residual plots.</p>
</div>
</div>

<br>

<span class="tag">input: learning-rate history</span>
<span class="tag">output: predicted loss curve</span>
<span class="tag">train: cosine</span>
<span class="tag">test: WSD + 8-1-1</span>

---

## Related Methods We Reproduce

<div class="grid-2">
<div class="panel blue">
<h3>Tissue / Momentum Law</h3>
<p class="small">Compact and interpretable law based on learning-rate accumulated features.</p>
<p class="small"><strong>Strength:</strong> stable fitting and readable parameters.</p>
<p class="small"><strong>Risk:</strong> too rigid for the early-stage loss drop.</p>
</div>

<div class="panel teal">
<h3>Multi-Power Law</h3>
<p class="small">More expressive: seven-parameter model for loss prediction across schedules.</p>
<p class="small"><strong>Strength:</strong> richer functional form.</p>
<p class="small"><strong>Risk:</strong> harder to fit and less directly interpretable.</p>
</div>
</div>

<div class="panel accent" style="margin-top: 22px;">
<p class="small"><strong>Our design choice:</strong> keep Tissue's interpretability, then add the correction suggested by its residual pattern.</p>
</div>

---

## Baseline 1: Tissue / Momentum Law

<div class="formula">

$$
L(t) = L_0 + A S_1(t)^{-\alpha} - C S_2(t)
$$

</div>

<div class="grid-2">
<div>

- Fit parameters on cosine.
- Predict WSD and 8-1-1 without refitting.
- Main metric for comparison: WSD MAPE.

</div>
<div class="metric">
<div class="value">1.560%</div>
<div class="label">WSD MAPE for plain Tissue baseline</div>
</div>
</div>

<div class="panel accent" style="margin-top: 18px;">
<p class="small"><strong>Observed issue:</strong> Tissue fits the general trend, but its residuals reveal biased predictions.</p>
</div>

---

<!-- _class: figure-slide -->

## Tissue Baseline: Fit and Transfer

<div class="figure-center figure-1060">
<img src="../figures/scaling_law_fit_and_prediction.png" alt="Tissue baseline fit and cross-schedule prediction" />
</div>

<div class="caption">Cosine fit, WSD transfer, and 8-1-1 transfer from the saved Tissue baseline run.</div>

---

## Baseline 2: Multi-Power Law

<div class="formula">

$$
L(t) = L_0 + A S_1(t)^{-\alpha} + B \cdot \mathrm{drop}(t)
$$

</div>

<div class="formula compact">

$$
\mathrm{drop}(t)=\sum_{i=1}^{t}(\eta_i-\eta_{i-1})\left[1-\left(1+c\eta_i^{-\gamma}(S_1(t)-S_1(i))\right)^{-\beta}\right].
$$

</div>

<div class="grid-2">
<div>

- Full pkl-based reproduction in `reproduce_2.py`.
- Downsamples the dense pkl curve before fitting, similar to a sparse-checkpoint setup.
- Serves as the more expressive reproduced contrast baseline.

</div>
<div class="metric">
<div class="value">0.805</div>
<div class="label">average test log-space R² for MPL</div>
</div>
</div>

---

<!-- _class: figure-slide -->

## Multi-Power Law: Fit and Transfer

<div class="figure-center figure-1060">
<img src="../figures/reproduce_2_mpl_fit_and_prediction.png" alt="MPL fit and cross-schedule prediction" />
</div>

<div class="caption">MPL is more expressive, but the pkl-based reproduction is not stronger than the corrected Tissue variant on the chosen metric.</div>

---

<!-- _class: figure-slide -->

## Limitation Analysis: Where Tissue Fails

<div class="figure-center figure-1120">
<img src="../figures/tissue_residual_diagnostic.png" alt="Residual diagnostic for Tissue baseline and improved variant" />
</div>

<div class="caption">Negative residuals mean actual loss is lower than predicted loss; the diagnostic shows where the correction moves bias closer to zero.</div>

---

## Our Method: Progress-Aware Tissue Correction

<div class="formula">

$$
L(t) = L_0 + A S_1(t)^{-\alpha} - C S_2(t) - D e^{-\tau p(t)}
$$

</div>

<div class="grid-2">
<div class="panel teal">
<h3>What changes?</h3>
<p class="small">Add a decaying correction term over normalized progress p(t), where p(t) ranges from 0 to 1.</p>
</div>
<div class="panel blue">
<h3>Why this term?</h3>
<p class="small">It is strongest early, then vanishes, matching the residual pattern found in the baseline.</p>
</div>
</div>

<div class="panel accent" style="margin-top: 20px;">
<p class="small"><strong>Contribution:</strong> a small, interpretable schedule-transfer correction instead of a large black-box residual model.</p>
</div>

---

## Main Quantitative Results

<div class="result-table">

| Method | Fit metric | Cross-schedule metric | Role |
| --- | --- | --- | --- |
| Tissue baseline | cosine log-space R² = 0.905891 | WSD MAPE = 1.5601%<br>8-1-1 MAPE = 1.5994% | reproduced baseline |
| Tissue + progress correction | cosine log-space R² = 0.912989 | WSD MAPE = 1.4924%<br>8-1-1 MAPE = 1.4925% | our method |
| Multi-Power Law | train log-space R² = 0.824753 | test log-space R² = 0.805011 | reproduced contrast |

</div>

<div class="metric-row">
<div class="metric">
<div class="value">-4.3%</div>
<div class="label">relative WSD MAPE reduction vs Tissue baseline</div>
</div>
<div class="metric">
<div class="value">-6.7%</div>
<div class="label">relative 8-1-1 MAPE reduction vs Tissue baseline</div>
</div>
<div class="metric">
<div class="value">simple</div>
<div class="label">only two added parameters: D and τ</div>
</div>
</div>

---

## Reproducibility and Code Map

<div class="grid-2">
<div class="panel blue">
<h3>reproduce_1.py</h3>
<p class="small">Tissue baseline, our progress-aware variant, residual analysis, and diagnostic figure.</p>
</div>
<div class="panel teal">
<h3>reproduce_2.py</h3>
<p class="small">Multi-Power Law reproduction with pkl loading, sampled checkpoints, metrics, and plot export.</p>
</div>
</div>

<div class="grid-2" style="margin-top: 22px;">
<div class="panel accent">
<h3>experiments/</h3>
<p class="small">Saved configs, fitted parameters, predictions, residuals, and metrics for each run.</p>
</div>
<div class="panel">
<h3>figures/</h3>
<p class="small">Main visual evidence used in the final slides and report.</p>
</div>
</div>

---

## Division of Labor

<div class="grid-3">
<div class="panel blue">
<h3>Tianze Lu</h3>
<p class="small">Main code implementation, Tissue baseline reproduction, improved method experiments.</p>
</div>
<div class="panel teal">
<h3>Ruoyu Wang</h3>
<p class="small">Final slide design, result organization and polishing.</p>
</div>
<div class="panel accent">
<h3>Feiyue Ye</h3>
<p class="small">Literature notes, result checking, and final formatting support.</p>
</div>
</div>

<div class="panel" style="margin-top: 24px;">
<p>Source code, saved experiment artifacts, figures, report notes, and final slides are all included in the repository.</p>
</div>

---

<!-- _class: conclusion -->

## Conclusions and Next Steps

<div class="grid-2">
<div>

- Cross-schedule loss prediction is feasible, but schedule-sensitive.
- Tissue is interpretable but misses the early-stage loss drop.
- MPL is a useful reproduced contrast baseline.
- Our progress-aware Tissue variant directly targets the observed failure mode.

</div>
<div class="panel dark">
<h3>Final takeaway</h3>
<p>Residual diagnosis can guide small, interpretable improvements to scaling-law transfer.</p>
<p class="small">Next: stronger schedule encoding, phase-wise fitting, or regularized residual modeling.</p>
</div>
</div>
