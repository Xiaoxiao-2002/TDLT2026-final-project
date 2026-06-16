# Method Development Comparison

This note compares two lightweight improvements to the Tissue-style momentum law.
Both variants keep the original Tissue baseline intact and are fitted on the cosine learning-rate schedule before being evaluated on WSD and 8-1-1.

## Methods

The original Tissue baseline is:

$$
L(t) = L_0 + A S_1(t)^{-\alpha} - C S_2(t).
$$

The previously used improvement adds a transient correction over normalized step progress:

$$
L(t) = L_0 + A S_1(t)^{-\alpha} - C S_2(t) - D e^{-\tau p_{\mathrm{step}}(t)},
$$

where $p_{\mathrm{step}}(t)=t/T$.

The new intrinsic-progress variant keeps the same correction form but uses cumulative learning-rate area as the progress variable:

$$
p_{\mathrm{intrinsic}}(t)=\frac{S_1(t)}{S_1(T)}.
$$

This choice is motivated by the intrinsic-time view: when the learning rate changes over time, effective optimization progress is better represented by accumulated step size than by raw iteration count.

## Latest Result

The table below uses the saved runs reported in the final slides.

| Method | Cosine log-space R2 | WSD MAPE | 8-1-1 MAPE |
| --- | ---: | ---: | ---: |
| Tissue baseline | 0.905891 | 1.5601% | 1.5994% |
| Tissue + step-progress correction | 0.912989 | 1.4924% | 1.4925% |
| Tissue + intrinsic-progress correction | 0.914654 | 1.5504% | 1.5766% |

Artifacts:

- `experiments/tissue_baseline/2026-05-31_183420/`
- `experiments/tissue_improved/2026-05-31_225220/`
- `experiments/tissue_intrinsic_progress/2026-06-16_103841/`
- `experiments/tissue_method_comparison/2026-06-16_103842/`
- `figures/tissue_method_comparison.png`

## Analysis

The intrinsic-progress correction gives the best cosine fit, which supports the idea that $S_1(t)/S_1(T)$ is a more schedule-aware progress variable than raw step count. However, it transfers worse than the step-progress correction on both WSD and 8-1-1 in the current pkl setting.

The practical conclusion is therefore conservative: the intrinsic-progress variant is theoretically cleaner, but the existing step-progress correction remains the stronger empirical method for the final reported cross-schedule prediction metrics. The intrinsic-progress result is still useful as an ablation, because it shows that a more theoretically motivated progress variable does not automatically improve transfer under limited fitting data.
