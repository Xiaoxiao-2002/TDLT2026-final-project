import argparse
import json
import os
import pickle
import sys
from datetime import datetime

import matplotlib

matplotlib.use("Agg")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import linregress

plt.rcParams.update({
    "font.size": 16,
    "axes.titlesize": 20,
    "axes.labelsize": 18,
    "xtick.labelsize": 15,
    "ytick.labelsize": 15,
    "legend.fontsize": 15,
    "figure.titlesize": 22,
})


TRAIN_SET = [
    "cosine",
]

TEST_SET = [
    "wsd",
    "811",
]

PKL_SCHEDULES = {
    "cosine": "M:100M_gpt_D:20B_scheduler:cosine_rope",
    "wsd": "M:100M_gpt_D:20B_scheduler:wsd_rope",
    "811": "M:100M_gpt_D:20B_scheduler:811_rope",
}

PARAM_INIT = {
    "C": [1.5],
    "beta": [0.5],
    "gamma": [0.6],
}


def project_root():
    return os.path.dirname(os.path.abspath(__file__))


def figures_dir():
    path = os.path.join(project_root(), "figures")
    os.makedirs(path, exist_ok=True)
    return path


def registry_path():
    return os.path.join(figures_dir(), "figure_registry.json")


def load_registry():
    path = registry_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {"version": 1, "updated_at": None, "figures": []}


def upsert_registry_entry(registry, entry):
    figures = registry.get("figures", [])
    for index, figure in enumerate(figures):
        if figure.get("filename") == entry["filename"]:
            figures[index] = entry
            break
    else:
        figures.append(entry)
    registry["figures"] = sorted(figures, key=lambda item: item.get("sort_order", 0))
    registry["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return registry


def write_registry(registry):
    path = registry_path()
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(registry, handle, ensure_ascii=False, indent=2)
    return path


def write_results_summary(registry):
    path = os.path.join(figures_dir(), "RESULTS.md")
    lines = [
        "# Figure Results Summary",
        "",
        f'Generated automatically from `figure_registry.json` at {registry.get("updated_at") or "unknown"}.',
        "",
        "## Figure Index",
        "",
        "| Image | Description |",
        "| --- | --- |",
    ]

    for figure in registry.get("figures", []):
        lines.append(
            f"| [{figure['filename']}]({figure['filename']}) | {figure.get('description', '')} |"
        )

    lines.extend(["", "## Figure Details", ""])
    for figure in registry.get("figures", []):
        lines.extend(
            [
                f"### {figure['filename']}",
                "",
                f"- Data / Setting: {figure.get('data_setting', '')}",
                f"- Key Results: {figure.get('key_results', '')}",
                f"- Parameters: {figure.get('parameters', '')}",
                "",
            ]
        )

    lines.extend(["## Text Supplement", ""])
    for note in registry.get("notes", []):
        lines.append(f"- {note}")

    lines.extend(["", "## Latest Run Details", "", "| Item | Value |", "| --- | --- |"])
    for key, value in registry.get("latest_run", {}).items():
        lines.append(f"| {key} | {value} |")

    lines.extend(["", "## Script Notes", ""])
    for note in registry.get("script_notes", []):
        lines.append(f"- {note}")

    lines.append("")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    return path


def experiment_root_dir():
    path = os.path.join(project_root(), "experiments")
    os.makedirs(path, exist_ok=True)
    return path


def make_run_dir(baseline_name):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir = os.path.join(experiment_root_dir(), baseline_name, timestamp)
    os.makedirs(run_dir, exist_ok=True)
    for subdir in ["figures", "logs", "curves"]:
        os.makedirs(os.path.join(run_dir, subdir), exist_ok=True)
    return run_dir


def _json_safe(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, dict):
        return {key: _json_safe(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(_json_safe(data), handle, ensure_ascii=False, indent=2)


def save_csv(path, frame):
    frame.to_csv(path, index=False)


def build_prediction_frame(split_name, schedule_name, curve, evaluation):
    # Convert to arrays and truncate to the minimum common length to avoid mismatches
    step = np.asarray(curve["step"])
    actual = np.asarray(curve["loss"])
    lr = np.asarray(curve["lrs"])
    predicted = np.asarray(evaluation.get("pred", np.zeros_like(actual)))
    s1 = np.asarray(evaluation.get("s1", np.zeros_like(actual)))

    min_len = min(len(step), len(actual), len(lr), len(predicted), len(s1))
    step = step[:min_len]
    actual = actual[:min_len]
    lr = lr[:min_len]
    predicted = predicted[:min_len]
    s1 = s1[:min_len]

    actual_clipped = np.maximum(actual, 1e-12)
    predicted_clipped = np.maximum(predicted, 1e-12)

    return pd.DataFrame({
        "split": np.full(min_len, split_name),
        "schedule": np.full(min_len, schedule_name),
        "step": step,
        "lr": lr,
        "actual_loss": actual,
        "predicted_loss": predicted,
        "residual": actual - predicted,
        "log_actual_loss": np.log(actual_clipped),
        "log_predicted_loss": np.log(predicted_clipped),
        "log_residual": np.log(actual_clipped) - np.log(predicted_clipped),
        "s1": s1,
    })


def save_experiment_artifacts(run_dir, params, fit_result, train_eval, test_eval, output_path, data_source, sample_stride):
    config = {
        "baseline": "multi_power_law",
        "data_source": data_source,
        "sample_stride": sample_stride,
        "train_set": TRAIN_SET,
        "test_set": TEST_SET,
        "figure_file": output_path,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_json(os.path.join(run_dir, "config.json"), config)

    fit_params = {
        "params": {
            "L0": float(params[0]),
            "A": float(params[1]),
            "alpha": float(params[2]),
            "B": float(params[3]),
            "C": float(params[4]),
            "beta": float(params[5]),
            "gamma": float(params[6]),
        },
        "optimization": {
            "success": bool(fit_result.success),
            "status": int(fit_result.status),
            "message": str(fit_result.message),
            "fun": float(fit_result.fun),
            "nfev": int(getattr(fit_result, "nfev", 0)),
            "nit": int(getattr(fit_result, "nit", 0)),
        },
    }
    save_json(os.path.join(run_dir, "fit_params.json"), fit_params)

    metrics = {
        "train_avg": train_eval["avg_metrics"],
        "test_avg": test_eval["avg_metrics"],
        "train_curves": {
            file_name: evaluated["metrics"] for file_name, evaluated in train_eval["curves"].items()
        },
        "test_curves": {
            file_name: evaluated["metrics"] for file_name, evaluated in test_eval["curves"].items()
        },
    }
    save_json(os.path.join(run_dir, "metrics.json"), metrics)

    prediction_frames = []
    residual_frames = []
    curve_dir = os.path.join(run_dir, "curves")

    for file_name, evaluated in train_eval["curves"].items():
        frame = build_prediction_frame("train", file_name, evaluated["curve"], evaluated)
        prediction_frames.append(frame)
        residual_frames.append(frame[["split", "schedule", "step", "actual_loss", "predicted_loss", "residual", "log_actual_loss", "log_predicted_loss", "log_residual"]])
        # Truncate arrays to common length before saving
        step_arr = np.asarray(evaluated["curve"]["step"])
        loss_arr = np.asarray(evaluated["curve"]["loss"])
        lr_arr = np.asarray(evaluated["curve"]["lrs"])
        s1_arr = np.asarray(evaluated.get("s1", np.zeros_like(loss_arr)))
        min_len = min(len(step_arr), len(loss_arr), len(lr_arr), len(s1_arr))
        save_csv(
            os.path.join(curve_dir, file_name),
            pd.DataFrame({
                "step": step_arr[:min_len],
                "loss": loss_arr[:min_len],
                "lr": lr_arr[:min_len],
                "s1": s1_arr[:min_len],
            }),
        )

    for file_name, evaluated in test_eval["curves"].items():
        frame = build_prediction_frame("test", file_name, evaluated["curve"], evaluated)
        prediction_frames.append(frame)
        residual_frames.append(frame[["split", "schedule", "step", "actual_loss", "predicted_loss", "residual", "log_actual_loss", "log_predicted_loss", "log_residual"]])
        # Truncate arrays to common length before saving
        step_arr = np.asarray(evaluated["curve"]["step"])
        loss_arr = np.asarray(evaluated["curve"]["loss"])
        lr_arr = np.asarray(evaluated["curve"]["lrs"])
        s1_arr = np.asarray(evaluated.get("s1", np.zeros_like(loss_arr)))
        min_len = min(len(step_arr), len(loss_arr), len(lr_arr), len(s1_arr))
        save_csv(
            os.path.join(curve_dir, file_name),
            pd.DataFrame({
                "step": step_arr[:min_len],
                "loss": loss_arr[:min_len],
                "lr": lr_arr[:min_len],
                "s1": s1_arr[:min_len],
            }),
        )

    combined_predictions = pd.concat(prediction_frames, ignore_index=True)
    combined_residuals = pd.concat(residual_frames, ignore_index=True)
    save_csv(os.path.join(run_dir, "train_predictions.csv"), combined_predictions[combined_predictions["split"] == "train"])
    save_csv(os.path.join(run_dir, "test_predictions.csv"), combined_predictions[combined_predictions["split"] == "test"])
    save_csv(os.path.join(run_dir, "residuals.csv"), combined_residuals)

    figure_name = os.path.basename(output_path)
    figure_copy_path = os.path.join(run_dir, "figures", figure_name)
    if os.path.exists(output_path):
        with open(output_path, "rb") as source, open(figure_copy_path, "wb") as target:
            target.write(source.read())

    return {
        "config": os.path.join(run_dir, "config.json"),
        "fit_params": os.path.join(run_dir, "fit_params.json"),
        "metrics": os.path.join(run_dir, "metrics.json"),
        "train_predictions": os.path.join(run_dir, "train_predictions.csv"),
        "test_predictions": os.path.join(run_dir, "test_predictions.csv"),
        "residuals": os.path.join(run_dir, "residuals.csv"),
        "figure_copy": figure_copy_path,
    }


def huber_loss(residual, delta=1e-3):
    residual = np.asarray(residual)
    abs_residual = np.abs(residual)
    return np.where(abs_residual <= delta, 0.5 * residual ** 2, delta * (abs_residual - 0.5 * delta))


def cosine_lrs(warmup, total, peak_lr, end_lr, const_warmup):
    step = np.arange(total)[warmup:]
    warmup_lrs = np.linspace(0, peak_lr, warmup) if not const_warmup else np.full(warmup, peak_lr)
    cosine_tail = end_lr + 0.5 * (peak_lr - end_lr) * (1 + np.cos(np.pi * (step - warmup) / (total - warmup)))
    return np.concatenate((warmup_lrs, cosine_tail))


def const_lrs(warmup, total, lr, const_warmup):
    warmup_lrs = np.linspace(0, lr, warmup) if not const_warmup else np.full(warmup, lr)
    return np.concatenate((warmup_lrs, np.full(total - warmup, lr)))


def two_stage_lrs(warmup, total, lr_a, lr_b, stage_a, const_warmup):
    warmup_lrs = np.linspace(0, lr_a, warmup) if not const_warmup else np.full(warmup, lr_a)
    stage_a_lrs = np.full(stage_a - warmup, lr_a)
    stage_b_lrs = np.full(total - stage_a, lr_b)
    return np.concatenate((warmup_lrs, stage_a_lrs, stage_b_lrs))


def wsd_lrs(warmup, total, decay, peak_lr, end_lr, const_warmup):
    step = np.arange(total)[decay:]
    warmup_lrs = np.linspace(0, peak_lr, warmup) if not const_warmup else np.full(warmup, peak_lr)
    decay_lrs = peak_lr ** ((total - step) / (total - decay)) * end_lr ** ((step - decay) / (total - decay))
    return np.concatenate((warmup_lrs, np.full(decay - warmup, peak_lr), decay_lrs))


def wsdld_lrs(warmup, total, decay, peak_lr, end_lr, const_warmup):
    step = np.arange(total)[decay:]
    warmup_lrs = np.linspace(0, peak_lr, warmup) if not const_warmup else np.full(warmup, peak_lr)
    decay_lrs = peak_lr * (1 - (step - decay) / (total - decay)) + end_lr * (step - decay) / (total - decay)
    return np.concatenate((warmup_lrs, np.full(decay - warmup, peak_lr), decay_lrs))


def resolve_schedule(file_name):
    if "cosine" in file_name:
        total = int(file_name.split("_")[1].split(".")[0])
        return cosine_lrs(2160, total, 3e-4, 3e-5, False)
    if "constant" in file_name:
        total = int(file_name.split("_")[1].split(".")[0])
        return const_lrs(2160, total, 3e-4, False)
    if "wsdcon" in file_name:
        total = 16000
        lr_b = int(file_name.split("_")[1].split(".")[0]) * 1e-5
        return two_stage_lrs(2160, total, 3e-4, lr_b, 8000, False)
    if "wsdld" in file_name:
        return wsdld_lrs(2160, 24000, 20000, 3e-4, 3e-5, False)
    if "wsd" in file_name:
        return wsd_lrs(2160, 24000, 20000, 3e-4, 3e-5, False)
    raise ValueError(f"Unsupported schedule type for {file_name}")


def load_curve(folder_path, file_name):
    path = os.path.join(folder_path, file_name)
    frame = pd.read_csv(path)
    step = frame["step"].to_numpy(dtype=int)
    loss = frame["loss"].to_numpy(dtype=float)

    if step.max() == 24000:
        mask = step < 24000
        step = step[mask]
        loss = loss[mask]

    lrs = resolve_schedule(file_name)
    return {"step": step, "loss": loss, "lrs": lrs}


def load_data(folder_path):
    data = {}
    for file_name in TRAIN_SET + TEST_SET:
        data[file_name] = load_curve(folder_path, file_name)
    return data


def load_pkl_curve(frame, sample_stride):
    # Use zero-based positions for model indexing; the pkl step column can include
    # endpoint labels that are one past the last valid ndarray index.
    step = np.arange(len(frame), dtype=int)
    loss = frame["Metrics/loss"].to_numpy(dtype=float)
    lrs = frame["lr"].to_numpy(dtype=float)

    keep = np.arange(0, len(step), sample_stride)
    if keep[-1] != len(step) - 1:
        keep = np.append(keep, len(step) - 1)

    return {
        "step": step[keep],
        "loss": loss[keep],
        "lrs": lrs,
    }


def load_pkl_data(pkl_path, sample_stride):
    with open(pkl_path, "rb") as handle:
        raw_data = pickle.load(handle)

    data = {}
    for short_name in TRAIN_SET + TEST_SET:
        schedule_key = PKL_SCHEDULES[short_name]
        data[short_name] = load_pkl_curve(raw_data[schedule_key], sample_stride)
    return data


def compute_features(lrs):
    lr_sum = np.cumsum(lrs)
    lr_gap = np.zeros_like(lrs)
    lr_gap[1:] = np.diff(lrs)
    return lr_sum, lr_gap


def mpl_predict(params, lrs, step):
    l0, a, alpha, b, c, beta, gamma = params
    lr_sum, lr_gap = compute_features(lrs)
    s1 = lr_sum[step]
    pred = np.empty_like(step, dtype=float)

    for idx, s in enumerate(step):
        if s <= 0:
            drop_term = 0.0
        else:
            lr_slice = lrs[1 : s + 1]
            gap_slice = lr_gap[1 : s + 1]
            tail_sum = lr_sum[s] - lr_sum[:s]
            transformed = 1.0 - np.power(1.0 + c * np.power(lr_slice, -gamma) * tail_sum, -beta)
            drop_term = np.sum(gap_slice * transformed)
        pred[idx] = l0 + a * np.power(max(s1[idx], 1e-12), -alpha) + b * drop_term

    return np.maximum(pred, 1e-12), s1


def train_objective(params, data, train_set):
    total = 0.0
    for file_name in train_set:
        curve = data[file_name]
        pred, _ = mpl_predict(params, curve["lrs"], curve["step"])
        actual = np.maximum(curve["loss"], 1e-12)
        residual = np.log(actual) - np.log(pred)
        total += np.sum(huber_loss(residual))
    return total


def fit_parameters(data, train_set):
    fit_data = {}
    for file_name in train_set:
        curve = data[file_name]
        fit_data[file_name] = {
            "step": curve["step"][::16],
            "loss": curve["loss"][::16],
            "lrs": curve["lrs"],
        }

    min_loss = min(fit_data[file_name]["loss"].min() for file_name in train_set)
    log_y_list = []
    log_x_list = []

    for file_name in train_set:
        curve = fit_data[file_name]
        lr_sum = np.cumsum(curve["lrs"])
        log_x_list.append(np.log(np.maximum(lr_sum[curve["step"]], 1e-12)))
        log_y_list.append(np.log(np.maximum(curve["loss"] - min_loss + 0.01, 1e-12)))

    log_x = np.concatenate(log_x_list)
    log_y = np.concatenate(log_y_list)
    slope, intercept, _, _, _ = linregress(log_x, log_y)

    l0_guesses = [min_loss, min_loss + 0.1]
    a_guesses = [max(0.05, np.exp(intercept))]
    alpha_guesses = [max(0.1, -slope)]
    b_guesses = [150.0, 350.0]

    best_result = None
    best_loss = float("inf")
    bounds = [(1e-8, None)] * 7

    for l0 in l0_guesses:
        for a in a_guesses:
            for alpha in alpha_guesses:
                for b in b_guesses:
                    for c in PARAM_INIT["C"]:
                        for beta in PARAM_INIT["beta"]:
                            for gamma in PARAM_INIT["gamma"]:
                                init = np.array([l0, a, alpha, b, c, beta, gamma], dtype=float)
                                result = minimize(
                                    train_objective,
                                    init,
                                    args=(fit_data, train_set),
                                    method="L-BFGS-B",
                                    bounds=bounds,
                                    options={"maxiter": 20, "ftol": 1e-9, "gtol": 1e-7},
                                )
                                if result.fun < best_loss:
                                    best_loss = result.fun
                                    best_result = result

    return best_result.x, best_result


def evaluate_curve(params, curve):
    pred, s1 = mpl_predict(params, curve["lrs"], curve["step"])
    actual = curve["loss"]
    actual_clipped = np.maximum(actual, 1e-12)
    pred_clipped = np.maximum(pred, 1e-12)
    residual = np.log(actual_clipped) - np.log(pred_clipped)

    mse = np.mean((actual - pred) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(actual - pred))
    prede = np.mean(np.abs(actual - pred) / np.maximum(actual, 1e-12))
    worst = np.max(np.abs(actual - pred) / np.maximum(actual, 1e-12))
    r2 = 1.0 - np.sum((actual - pred) ** 2) / np.sum((actual - np.mean(actual)) ** 2)
    log_r2 = 1.0 - np.sum(residual ** 2) / np.sum((np.log(actual_clipped) - np.mean(np.log(actual_clipped))) ** 2)
    huber = np.sum(huber_loss(residual))

    return {
        "pred": pred,
        "s1": s1,
        "metrics": {
            "huber": huber,
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "prede": prede,
            "worst": worst,
            "r2": r2,
            "log_r2": log_r2,
        },
    }


def evaluate_dataset(params, data, file_names):
    results = {}
    for file_name in file_names:
        evaluated = evaluate_curve(params, data[file_name])
        evaluated["curve"] = data[file_name]
        results[file_name] = evaluated

    metric_names = ["huber", "mse", "rmse", "mae", "prede", "worst", "r2", "log_r2"]
    averages = {
        metric_name: float(np.mean([results[file_name]["metrics"][metric_name] for file_name in file_names]))
        for metric_name in metric_names
    }
    return results, averages


def downsample(x, y, target_points=700):
    if len(x) <= target_points:
        return x, y
    stride = max(1, int(np.ceil(len(x) / target_points)))
    return x[::stride], y[::stride]


def build_report(params, train_eval, test_eval, output_name):
    test_parts = [
        f"{name.upper()} log-space R² = {test_eval['curves'][name]['metrics']['log_r2']:.6f}"
        for name in TEST_SET
    ]
    registry = load_registry()
    registry = upsert_registry_entry(
        registry,
        {
            "filename": output_name,
            "sort_order": 20,
            "description": "Standalone Multi-Power Law reproduction with 7 fitted parameters and cross-schedule prediction.",
            "data_setting": "Train on cosine curve from the course pkl file; report WSD prediction and 8-1-1 extension.",
            "key_results": (
                f"Train avg log-space R² = {train_eval['avg_metrics']['log_r2']:.6f}; "
                f"Test avg log-space R² = {test_eval['avg_metrics']['log_r2']:.6f}; "
                f"Cosine log-space R² = {train_eval['curves']['cosine']['metrics']['log_r2']:.6f}; "
                f"{'; '.join(test_parts)}."
            ),
            "parameters": (
                f"L0 = {params[0]:.6f}, A = {params[1]:.6f}, alpha = {params[2]:.6f}, "
                f"B = {params[3]:.6f}, C = {params[4]:.6f}, beta = {params[5]:.6f}, gamma = {params[6]:.6f}."
            ),
        },
    )
    registry["notes"] = [
        "This script now fits the full 7-parameter Multi-Power Law model.",
        "The script reads the course-provided gpt_loss+lrs.pkl file directly.",
        "Dense pkl curves are sampled at a fixed stride to match the sparse-checkpoint setting used by the MPL reproduction.",
        "The summary page is regenerated automatically from figure_registry.json.",
    ]
    registry["latest_run"] = {
        "Train avg log-space R²": f"{train_eval['avg_metrics']['log_r2']:.6f}",
        "Test avg log-space R²": f"{test_eval['avg_metrics']['log_r2']:.6f}",
        "Cosine log-space R²": f"{train_eval['curves']['cosine']['metrics']['log_r2']:.6f}",
        "WSD log-space R²": f"{test_eval['curves']['wsd']['metrics']['log_r2']:.6f}",
        "8-1-1 log-space R²": f"{test_eval['curves']['811']['metrics']['log_r2']:.6f}",
    }
    registry["script_notes"] = [
        "Source file: reproduce_2.py",
        f"Output image: {output_name}",
        "Metadata source: figure_registry.json",
    ]
    registry_path_written = write_registry(registry)
    summary_path = write_results_summary(registry)
    return registry_path_written, summary_path


def plot_results(train_curve, train_eval, test_eval, output_name):
    total_panels = 1 + len(TEST_SET)
    fig, axes = plt.subplots(total_panels, 1, figsize=(16, 2.8 * total_panels), constrained_layout=True)
    if total_panels == 1:
        axes = [axes]

    train_x = train_curve["step"]
    train_y = train_curve["loss"]
    train_pred = train_eval["pred"]
    train_x_plot, train_y_plot = downsample(train_x, train_y)
    train_pred_x_plot, train_pred_y_plot = downsample(train_x, train_pred)
    axes[0].plot(train_x_plot, train_y_plot, label="Actual Loss", alpha=0.8, linewidth=1.35)
    axes[0].plot(train_pred_x_plot, train_pred_y_plot, label="MPL Fit", linestyle="--", linewidth=1.9, color="red")
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("Validation Loss")
    axes[0].set_title(f"Cosine Fit (Log-space R² = {train_eval['metrics']['log_r2']:.4f})")
    axes[0].legend(loc="best", fontsize=9)
    axes[0].grid(True, alpha=0.3)

    title_map = {"wsd": "WSD", "811": "8-1-1"}
    for axis_index, schedule_name in enumerate(TEST_SET, start=1):
        curve = test_eval[schedule_name]["curve"]
        pred = test_eval[schedule_name]["pred"]
        x_plot, y_plot = downsample(curve["step"], curve["loss"])
        pred_x_plot, pred_y_plot = downsample(curve["step"], pred)
        axes[axis_index].plot(x_plot, y_plot, label="Actual Loss", alpha=0.8, linewidth=1.35)
        axes[axis_index].plot(pred_x_plot, pred_y_plot, label="Predicted Loss", linestyle="--", linewidth=1.9, color="red")
        axes[axis_index].set_xlabel("Step")
        axes[axis_index].set_ylabel("Validation Loss")
        display_name = title_map.get(schedule_name, schedule_name.upper())
        axes[axis_index].set_title(f"{display_name} Prediction (Log-space R² = {test_eval[schedule_name]['metrics']['log_r2']:.4f})")
        axes[axis_index].legend(loc="best", fontsize=9)
        axes[axis_index].grid(True, alpha=0.3)

    output_path = os.path.join(figures_dir(), output_name)
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return output_path


def run(sample_stride):
    pkl_path = os.path.join(project_root(), "loss curves", "gpt_loss+lrs.pkl")
    print(f"Loading curves from {pkl_path}")
    data = load_pkl_data(pkl_path, sample_stride)
    print(f"Fitting on {len(TRAIN_SET)} training curves and predicting {len(TEST_SET)} test curves")
    print(f"Using pkl sample stride = {sample_stride}")
    params, fit_result = fit_parameters(data, TRAIN_SET)
    print(f"Best objective = {fit_result.fun:.6f}")

    train_curves, train_avg = evaluate_dataset(params, data, TRAIN_SET)
    test_curves, test_avg = evaluate_dataset(params, data, TEST_SET)
    train_eval = {"curves": train_curves, "avg_metrics": train_avg}
    test_eval = {"curves": test_curves, "avg_metrics": test_avg}

    output_name = "reproduce_2_mpl_fit_and_prediction.png"
    output_path = plot_results(data["cosine"], train_curves["cosine"], test_curves, output_name)
    registry_path_written, summary_path = build_report(params, train_eval, test_eval, output_name)
    run_dir = make_run_dir("mpl_baseline")
    artifact_paths = save_experiment_artifacts(
        run_dir,
        params,
        fit_result,
        train_eval,
        test_eval,
        output_path,
        "loss curves/gpt_loss+lrs.pkl",
        sample_stride,
    )

    print(f"✓ Train avg log-space R² = {train_eval['avg_metrics']['log_r2']:.6f}")
    print(f"✓ Test avg log-space R² = {test_eval['avg_metrics']['log_r2']:.6f}")
    print(f"✓ Cosine log-space R² = {train_curves['cosine']['metrics']['log_r2']:.6f}")
    print(f"✓ WSD log-space R² = {test_curves['wsd']['metrics']['log_r2']:.6f}")
    print(f"✓ 8-1-1 log-space R² = {test_curves['811']['metrics']['log_r2']:.6f}")
    print(f"✓ Plot saved to '{output_path}'")
    print(f"✓ Registry saved to '{registry_path_written}'")
    print(f"✓ Summary saved to '{summary_path}'")
    print(f"✓ Run artifacts saved to '{run_dir}'")

    return params, train_eval, test_eval, artifact_paths


def parse_args():
    parser = argparse.ArgumentParser(description="Standalone Multi-Power Law reproduction script.")
    parser.add_argument(
        "--sample-stride",
        type=int,
        default=16,
        help="Evaluate every Nth pkl checkpoint for MPL fitting/prediction.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.sample_stride)
