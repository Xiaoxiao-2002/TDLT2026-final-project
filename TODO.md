# TODO

This TODO tracks the remaining work needed to make the Task 2 final project submission-ready.

## Submission Essentials

- [x] Reproduce the Tissue-style momentum law baseline in `reproduce_1.py`.
- [x] Reproduce the Multi-Power Law baseline in `reproduce_2.py`.
- [x] Save experiment artifacts under `experiments/`.
- [x] Save final slide figures under `figures/`.
- [x] Create a root `README.md` with project goal, setup, commands, results, and submission notes.
- [x] Create a root `requirements.txt` for the scripts used in this project.
- [x] Create this project-level TODO tracker.
- [ ] Create the GitHub repository and replace the repository placeholder in `docs/final_slides.marp.md`.
- [ ] Confirm group member student IDs and add them to the title slide.
- [ ] Export the final Marp slide deck to `docs/final_slides.marp.pdf` after the GitHub link and IDs are filled in.

## Experimental Evidence

- [x] Use `experiments/tissue_baseline/2026-05-31_183420/` as the saved Tissue baseline result.
- [x] Use `experiments/tissue_improved/2026-05-31_225220/` as the saved progress-aware Tissue result.
- [x] Use `experiments/mpl_baseline/2026-06-14_153414/` as the saved Multi-Power Law result.
- [x] Report Tissue baseline: cosine log-space R2 = 0.905891; WSD MAPE = 1.5601%; 8-1-1 MAPE = 1.5994%.
- [x] Report Tissue + progress correction: cosine log-space R2 = 0.912989; WSD MAPE = 1.4924%; 8-1-1 MAPE = 1.4925%.
- [x] Report MPL baseline on pkl data: train log-space R2 = 0.824753; test log-space R2 = 0.805011.
- [x] Use `figures/scaling_law_fit_and_prediction.png` for the Tissue baseline.
- [x] Use `figures/reproduce_2_mpl_fit_and_prediction.png` for MPL.
- [x] Use `figures/tissue_residual_diagnostic.png` for the failure-mode diagnosis.

## Documentation Polish

- [x] Keep `docs/final_slides.marp.md` focused on the short presentation story.
- [x] Keep `docs/final_article.md` aligned with the same metrics, figures, and conclusion.
- [ ] Do a final visual pass on the exported PDF: title slide, formulas, figure sizes, and result slide readability.
- [ ] Verify the final email subject and recipient list from the course requirement before submission.

## Optional Enhancements

- [ ] Add one ablation for the progress-aware Tissue correction if there is time.
- [ ] Add a compact result-table figure if the Markdown table is not readable enough in slides.
- [ ] Add a stronger schedule-aware correction term as future work, not as a required final result.

## Final Position

- MPL should be presented as the more expressive reproduced baseline and a contrast case on the same course pkl data.
- The normalized-progress Tissue correction should be presented as our own lightweight method.
- The residual diagnostic should explain why the progress-aware correction was chosen.
