import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
from datetime import datetime
import json
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

plt.rcParams.update({
    'font.size': 16,
    'axes.titlesize': 20,
    'axes.labelsize': 18,
    'xtick.labelsize': 15,
    'ytick.labelsize': 15,
    'legend.fontsize': 15,
    'figure.titlesize': 22,
})


def make_plot_output_path(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'figures')
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, filename)


def figure_registry_path():
    return make_plot_output_path('figure_registry.json')


def load_figure_registry():
    registry_path = figure_registry_path()
    if os.path.exists(registry_path):
        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    return {
        "version": 1,
        "updated_at": None,
        "figures": []
    }


def upsert_figure_entry(registry, entry):
    figures = registry.get('figures', [])
    updated = False
    for index, figure in enumerate(figures):
        if figure.get('filename') == entry['filename']:
            figures[index] = entry
            updated = True
            break

    if not updated:
        figures.append(entry)

    registry['figures'] = sorted(figures, key=lambda item: item.get('sort_order', 0))
    registry['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return registry


def write_figure_registry(registry):
    registry_path = figure_registry_path()
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    return registry_path


def markdown_table_row(values):
    return "| " + " | ".join(str(value) for value in values) + " |"


def write_results_summary(output_dir, registry):
    """Write a markdown summary generated from the structured registry."""
    report_path = os.path.join(output_dir, 'RESULTS.md')
    updated_at = registry.get('updated_at') or 'unknown'
    figures = registry.get('figures', [])

    lines = [
        '# Figure Results Summary',
        '',
        f'Generated automatically from `figure_registry.json` at {updated_at}.',
        '',
        '## Figure Index',
        '',
        '| Image | Description |',
        '| --- | --- |',
    ]

    for figure in figures:
        lines.append(markdown_table_row([
            f"[{figure['filename']}]({figure['filename']})",
            figure.get('description', ''),
        ]))

    lines.extend(['', '## Figure Details', ''])

    for figure in figures:
        lines.extend([
            f"### {figure['filename']}",
            '',
            f"- Data / Setting: {figure.get('data_setting', '')}",
            f"- Key Results: {figure.get('key_results', '')}",
            f"- Parameters: {figure.get('parameters', '')}",
            '',
        ])

    lines.extend([
        '## Text Supplement',
        '',
    ])

    for note in registry.get('notes', []):
        lines.append(f'- {note}')

    lines.extend([
        '',
        '## Latest Run Details',
        '',
        '| Item | Value |',
        '| --- | --- |',
    ])

    latest_run = registry.get('latest_run', {})
    for key, value in latest_run.items():
        lines.append(markdown_table_row([key, value]))

    lines.extend([
        '',
        '## Script Notes',
        '',
    ])

    for note in registry.get('script_notes', []):
        lines.append(f'- {note}')

    lines.append('')

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return report_path


def experiment_root_dir():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'experiments')
    os.makedirs(path, exist_ok=True)
    return path


def make_run_dir(baseline_name):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    run_dir = os.path.join(experiment_root_dir(), baseline_name, timestamp)
    os.makedirs(run_dir, exist_ok=True)
    for subdir in ['figures', 'logs', 'curves']:
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
    with open(path, 'w', encoding='utf-8') as handle:
        json.dump(_json_safe(data), handle, ensure_ascii=False, indent=2)


def save_csv(path, frame):
    frame.to_csv(path, index=False)


def build_prediction_frame(split_name, schedule_name, step, actual, predicted, lr_schedule, s1, s2):
    actual_clipped = np.maximum(actual, 1e-12)
    predicted_clipped = np.maximum(predicted, 1e-12)
    return pd.DataFrame({
        'split': split_name,
        'schedule': schedule_name,
        'step': step,
        'lr': lr_schedule,
        'actual_loss': actual,
        'predicted_loss': predicted,
        'residual': actual - predicted,
        'log_actual_loss': np.log(actual_clipped),
        'log_predicted_loss': np.log(predicted_clipped),
        'log_residual': np.log(actual_clipped) - np.log(predicted_clipped),
        's1': s1,
        's2': s2,
    })


def save_experiment_artifacts(run_dir, params, result, train_bundle, test_bundles, artifacts):
    method_name = artifacts.get('method_name', 'tissue_scaling_law')
    config = {
        'baseline': method_name,
        'run_dir': run_dir,
        'train_schedule': train_bundle['schedule_name'],
        'test_schedules': [bundle['schedule_name'] for bundle in test_bundles],
        'decay_factor': artifacts['decay_factor'],
        'figure_file': artifacts['figure_file'],
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    save_json(os.path.join(run_dir, 'config.json'), config)

    fit_params = {
        'params': {
            'L0': float(params[0]),
            'A': float(params[1]),
            'C': float(params[2]),
            'alpha': float(params[3]),
        },
        'optimization': {
            'success': bool(result.success),
            'status': int(result.status),
            'message': str(result.message),
            'fun': float(result.fun),
            'nfev': int(getattr(result, 'nfev', 0)),
            'nit': int(getattr(result, 'nit', 0)),
        },
    }
    save_json(os.path.join(run_dir, 'fit_params.json'), fit_params)

    metrics = {
        'train': {
            'log_r2': float(artifacts['train_metrics']['log_r2']),
        },
        'test': {
            'wsd_mape': float(artifacts['wsd_metrics']['mape']),
            '811_mape': float(artifacts['811_metrics']['mape']),
        },
    }
    save_json(os.path.join(run_dir, 'metrics.json'), metrics)

    combined_frames = [train_bundle['frame']]
    combined_frames.extend(bundle['frame'] for bundle in test_bundles)
    combined_frame = pd.concat(combined_frames, ignore_index=True)
    save_csv(os.path.join(run_dir, 'predictions.csv'), combined_frame)

    residual_frame = combined_frame[['split', 'schedule', 'step', 'actual_loss', 'predicted_loss', 'residual', 'log_actual_loss', 'log_predicted_loss', 'log_residual']].copy()
    save_csv(os.path.join(run_dir, 'residuals.csv'), residual_frame)

    def sanitize_filename(name):
        # replace characters invalid in file names (like ':' on Windows)
        return re.sub(r'[^A-Za-z0-9_.-]', '_', name)

    save_csv(os.path.join(run_dir, 'curves', 'train_curve.csv'), train_bundle['curve_frame'])
    for bundle in test_bundles:
        safe_name = sanitize_filename(bundle['schedule_name'])
        save_csv(os.path.join(run_dir, 'curves', f"{safe_name}.csv"), bundle['curve_frame'])

    figure_name = os.path.basename(artifacts['figure_file'])
    figure_copy_path = os.path.join(run_dir, 'figures', figure_name)
    if os.path.exists(artifacts['figure_file']):
        with open(artifacts['figure_file'], 'rb') as source, open(figure_copy_path, 'wb') as target:
            target.write(source.read())

    return {
        'config': os.path.join(run_dir, 'config.json'),
        'fit_params': os.path.join(run_dir, 'fit_params.json'),
        'metrics': os.path.join(run_dir, 'metrics.json'),
        'predictions': os.path.join(run_dir, 'predictions.csv'),
        'residuals': os.path.join(run_dir, 'residuals.csv'),
        'figure_copy': figure_copy_path,
    }


def downsample_series(x, y, target_points=700):
    """Downsample dense curves for clearer visualization."""
    if len(x) <= target_points:
        return x, y

    stride = max(1, int(np.ceil(len(x) / target_points)))
    return x[::stride], y[::stride]


def summarize_residual_window(frame, schedule_name, fraction=0.25):
    schedule_frame = frame[frame['schedule'] == schedule_name].sort_values('step')
    if schedule_frame.empty:
        raise ValueError(f'No rows found for schedule: {schedule_name}')

    residuals = schedule_frame['residual'].to_numpy()
    abs_residuals = np.abs(residuals)
    window_size = max(1, int(np.ceil(len(residuals) * fraction)))
    early = residuals[:window_size]
    late = residuals[-window_size:]
    early_abs = abs_residuals[:window_size]
    late_abs = abs_residuals[-window_size:]
    return {
        'early_mean': float(np.mean(early)),
        'early_mae': float(np.mean(early_abs)),
        'late_mean': float(np.mean(late)),
        'late_mae': float(np.mean(late_abs)),
    }


def generate_residual_diagnostic_figure(baseline_residuals_path, improved_residuals_path, output_filename='tissue_residual_diagnostic.png'):
    baseline_frame = pd.read_csv(baseline_residuals_path)
    improved_frame = pd.read_csv(improved_residuals_path)

    schedules = ['M:100M_gpt_D:20B_scheduler:cosine_rope', 'M:100M_gpt_D:20B_scheduler:wsd_rope', 'M:100M_gpt_D:20B_scheduler:811_rope']
    schedule_labels = ['Cosine', 'WSD', '8-1-1']

    baseline_summary = {schedule: summarize_residual_window(baseline_frame, schedule) for schedule in schedules}
    improved_summary = {schedule: summarize_residual_window(improved_frame, schedule) for schedule in schedules}

    metrics = [
        ('Early Mean Residual', 'early_mean', 'Residual'),
        ('Early MAE', 'early_mae', 'MAE'),
        ('Late Mean Residual', 'late_mean', 'Residual'),
        ('Late MAE', 'late_mae', 'MAE'),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(18, 7.0))
    axes = axes.flatten()
    x = np.arange(len(schedule_labels))
    width = 0.34
    colors = {'baseline': '#1f77b4', 'improved': '#ff7f0e'}

    for axis, (title, metric_key, y_label) in zip(axes, metrics):
        baseline_values = [baseline_summary[schedule][metric_key] for schedule in schedules]
        improved_values = [improved_summary[schedule][metric_key] for schedule in schedules]

        axis.bar(x - width / 2, baseline_values, width, label='Tissue baseline', color=colors['baseline'])
        axis.bar(x + width / 2, improved_values, width, label='Tissue + progress correction', color=colors['improved'])
        axis.set_title(title, fontsize=15, pad=5)
        axis.set_xticks(x)
        axis.set_xticklabels(schedule_labels, fontsize=13)
        axis.tick_params(axis='y', labelsize=12)
        axis.set_ylabel(y_label, fontsize=14)
        axis.grid(True, axis='y', alpha=0.25)
        axis.axhline(0, color='black', linewidth=0.8, alpha=0.25)

    fig.suptitle('Residual Pattern Diagnosis for Tissue Baseline vs Improved Variant', fontsize=20, y=1.00)
    fig.text(0.5, 0.885, 'Blue: Tissue baseline   |   Orange: Tissue + progress correction', ha='center', fontsize=13, color='#5b6472')
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))

    output_path = make_plot_output_path(output_filename)
    plt.savefig(output_path, dpi=180, bbox_inches='tight')
    plt.close(fig)

    registry = load_figure_registry()
    registry = upsert_figure_entry(registry, {
        'filename': output_filename,
        'sort_order': 15,
        'description': '2x2 residual comparison with larger typography for early and late residual patterns across schedules.',
        'data_setting': 'Early/late residual comparison on Tissue baseline and the normalized-progress correction across cosine, WSD, and 8-1-1.',
        'key_results': 'The improved method lowers early-step residual magnitude and early MAE across schedules; the visualization is optimized for slide readability.',
        'parameters': 'Built from the saved residuals.csv artifacts of the baseline and improved Tissue runs.',
    })
    registry['notes'] = [
        'Plot layout: 2 rows x 2 columns for a compact residual-diagnostic figure.',
        'Typography is increased so the bar labels and titles remain readable after slide export.',
        'The figure compares early and late residual behavior across cosine, WSD, and 8-1-1.',
    ]
    write_figure_registry(registry)
    write_results_summary(os.path.dirname(output_path), registry)
    return output_path

def compute_scaling_law_features(lr_schedule, decay_factor=0.999):
    """
    Compute S1 (forward area) and S2 (annealing area) for a given learning rate schedule.
    
    Args:
        lr_schedule: np.array of learning rates at each step (length = total_steps)
        decay_factor: lambda (momentum decay), paper uses 0.999 typically
    
    Returns:
        S1: np.array of forward area at each step
        S2: np.array of annealing area at each step
        m: np.array of annealing momentum at each step
    """
    steps = len(lr_schedule)
    S1 = np.zeros(steps)
    S2 = np.zeros(steps)
    m = np.zeros(steps)
    
    # Initialize first step
    S1[0] = lr_schedule[0]
    # m[0] remains 0 (as per paper: m_1 = 0)
    # S2[0] remains 0 (no annealing momentum at first step)
    
    # Compute recursively for remaining steps
    for i in range(1, steps):
        # S1 is cumulative sum of learning rates
        S1[i] = S1[i-1] + lr_schedule[i]
        
        # m_i = lambda * m_{i-1} + (eta_{i-1} - eta_i)
        # This captures the annealing amount with momentum
        annealing_amount = lr_schedule[i-1] - lr_schedule[i]
        m[i] = decay_factor * m[i-1] + annealing_amount
        
        # S2 is cumulative sum of annealing momentum
        S2[i] = S2[i-1] + m[i]
    
    return S1, S2, m

def scaling_law_loss(S1, S2, params):
    """
    Compute predicted loss using the scaling law with LR annealing.
    
    L(s) = L0 + A * S1^(-alpha) - C * S2
    
    Args:
        S1: forward area (can be scalar or array)
        S2: annealing area (can be scalar or array)
        params: (L0, A, C, alpha)
    """
    L0, A, C, alpha = params
    # protect against zero or negative S1 that would create inf/NaN when raising to -alpha
    safe_S1 = np.maximum(S1, 1e-12)
    return L0 + A * np.power(safe_S1, -alpha) - C * S2

def huber_loss(pred, target, delta=1e-3):
    """
    Huber loss as used in the paper (delta = 1e-3)
    Computed on log scale as per paper.
    """
    # Numeric protection: clip predictions and targets to a small positive value
    eps = 1e-12
    pred_clipped = np.maximum(pred, eps)
    target_clipped = np.maximum(target, eps)
    diff = np.log(pred_clipped) - np.log(target_clipped)
    abs_diff = np.abs(diff)
    
    loss = np.where(abs_diff <= delta,
                    0.5 * diff**2,
                    delta * (abs_diff - 0.5 * delta))
    return np.mean(loss)

def fit_scaling_law(S1_data, S2_data, loss_data, initial_params=None):
    """
    Fit the scaling law parameters (L0, A, C, alpha) to training data.
    
    Args:
        S1_data: array of S1 values from training runs
        S2_data: array of S2 values from training runs  
        loss_data: array of actual validation losses
        initial_params: initial guess for (L0, A, C, alpha)
    
    Returns:
        optimized parameters and optimization result object
    """
    if initial_params is None:
        # Reasonable initial guesses based on paper values
        # L0 ~ 2.6, A ~ 0.4, C ~ 0.4, alpha ~ 0.5
        initial_params = [2.6, 0.4, 0.4, 0.5]
    
    def objective(params):
        pred = scaling_law_loss(S1_data, S2_data, params)
        return huber_loss(pred, loss_data, delta=1e-3)
    
    # Set bounds: all parameters must be positive
    # L0 > 0 (base loss), A > 0, C > 0, alpha > 0
    bounds = [(0.001, None), (0.001, None), (0.001, None), (0.001, None)]
    
    # Try multiple random initializations to avoid local minima (as per paper)
    best_result = None
    best_loss = float('inf')
    
    # Grid of initial alpha and L0 guesses
    for alpha_guess in [0.3, 0.5, 0.7]:
        for L0_guess in [2.0, 2.6, 3.0]:
            init = [L0_guess, 0.4, 0.4, alpha_guess]
            result = minimize(objective, init, method='L-BFGS-B', bounds=bounds)
            
            if result.fun < best_loss:
                best_loss = result.fun
                best_result = result
    
    return best_result.x, best_result

def predict_loss_curve(lr_schedule, fitted_params, decay_factor=0.999):
    """
    Predict the full loss curve for a new learning rate schedule.
    
    Args:
        lr_schedule: np.array of learning rates for the new schedule
        fitted_params: (L0, A, C, alpha) from fitting
        decay_factor: lambda used during fitting
    
    Returns:
        predicted_losses: np.array of predicted validation losses
        S1, S2: computed features for inspection
    """
    S1, S2, _ = compute_scaling_law_features(lr_schedule, decay_factor)
    predicted_losses = scaling_law_loss(S1, S2, fitted_params)
    return predicted_losses, S1, S2


def improved_scaling_law_loss(S1, S2, progress, params):
    """Baseline scaling law plus an early-stage correction over normalized progress."""
    L0, A, C, alpha, D, tau = params
    safe_S1 = np.maximum(S1, 1e-12)
    early_correction = D * np.exp(-tau * np.clip(progress, 0.0, 1.0))
    return L0 + A * np.power(safe_S1, -alpha) - C * S2 - early_correction


def fit_improved_scaling_law(S1_data, S2_data, progress_data, loss_data, initial_params=None):
    """Fit a slightly richer model with an early transient correction term."""
    if initial_params is None:
        initial_params = [2.6, 0.4, 0.4, 0.5, 0.2, 1.0]

    def objective(params):
        pred = improved_scaling_law_loss(S1_data, S2_data, progress_data, params)
        return huber_loss(pred, loss_data, delta=1e-3)

    bounds = [
        (0.001, None),
        (0.001, None),
        (0.001, None),
        (0.001, None),
        (0.0, None),
        (1e-6, None),
    ]

    best_result = None
    best_loss = float('inf')

    for alpha_guess in [0.3, 0.5, 0.7]:
        for L0_guess in [2.0, 2.6, 3.0]:
            for D_guess in [0.05, 0.15, 0.3]:
                init = [L0_guess, 0.4, 0.4, alpha_guess, D_guess, 0.5]
                result = minimize(objective, init, method='L-BFGS-B', bounds=bounds)

                if result.fun < best_loss:
                    best_loss = result.fun
                    best_result = result

    return best_result.x, best_result


def predict_improved_loss_curve(lr_schedule, fitted_params, decay_factor=0.999):
    S1, S2, _ = compute_scaling_law_features(lr_schedule, decay_factor)
    progress = np.linspace(0.0, 1.0, len(lr_schedule), endpoint=True)
    predicted_losses = improved_scaling_law_loss(S1, S2, progress, fitted_params)
    return predicted_losses, S1, S2, progress

# ============================================================================
# DATA LOADING
# ============================================================================

def load_training_data(pkl_path):
    """
    Load training data from pkl file.
    
    The pkl file contains a dictionary with three DataFrames:
    - 'M:100M_gpt_D:20B_scheduler:811_rope': "8-1-1" learning rate schedule data
    - 'M:100M_gpt_D:20B_scheduler:wsd_rope': WSD learning rate schedule data  
    - 'M:100M_gpt_D:20B_scheduler:cosine_rope': Cosine learning rate schedule data
    
    Args:
        pkl_path: path to the pkl file containing training metrics
    
    Returns:
        data_dict: Dictionary with keys being schedule names and values being DataFrames
    """
    data_dict = pd.read_pickle(pkl_path)
    return data_dict

def extract_loss_and_lr(df):
    """
    Extract loss and learning rate arrays from the dataframe.
    
    Args:
        df: DataFrame with 'Metrics/loss' and 'lr' columns
    
    Returns:
        losses: np.array of actual validation losses
        lr_schedule: np.array of learning rates used at each step
    """
    losses = df['Metrics/loss'].values
    lr_schedule = df['lr'].values
    return losses, lr_schedule

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_workflow():
    """
    Example: Fit on Cosine LRS data, predict WSD and 8-1-1 LRS curves.
    
    The pkl file contains three learning rate schedules:
    - "8-1-1" LRS: Two-stage decay (80% and 90% of total steps)
    - WSD LRS: Warmup-Stable-Decay schedule
    - Cosine LRS: Cosine annealing schedule
    """
    
    # 1. Load training data from pkl file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pkl_path = os.path.join(script_dir, 'loss curves', 'gpt_loss+lrs.pkl')
    
    if not os.path.exists(pkl_path):
        print(f"Error: pkl file not found at {pkl_path}")
        return None, None
    
    data_dict = load_training_data(pkl_path)
    
    # Available schedules in the pkl file
    available_schedules = list(data_dict.keys())
    print(f"Available schedules in pkl file:")
    for schedule in available_schedules:
        print(f"  - {schedule} ({len(data_dict[schedule])} steps)")
    
    # Use cosine schedule for fitting (or "8-1-1" if you prefer)
    # Cosine is a more standard schedule for fitting the scaling law
    schedule_for_fitting = 'M:100M_gpt_D:20B_scheduler:cosine_rope'
    
    df_cosine = data_dict[schedule_for_fitting]
    actual_losses_cosine, lr_schedule_cosine = extract_loss_and_lr(df_cosine)
    
    print(f"\n=== Training on Cosine Schedule ===")
    print(f"Total steps: {len(actual_losses_cosine)}")
    print(f"Loss range: [{actual_losses_cosine.min():.6f}, {actual_losses_cosine.max():.6f}]")
    print(f"LR range: [{lr_schedule_cosine.min():.2e}, {lr_schedule_cosine.max():.2e}]")
    
    total_steps_cosine = len(actual_losses_cosine)
    steps_cosine = np.arange(1, total_steps_cosine + 1)
    
    # 2. Compute scaling law features from the loaded learning rate schedule
    S1_cosine, S2_cosine, _ = compute_scaling_law_features(lr_schedule_cosine, decay_factor=0.999)
    
    # 3. Fit the scaling law
    params, result = fit_scaling_law(S1_cosine, S2_cosine, actual_losses_cosine)
    L0, A, C, alpha = params
    
    print(f"\n=== Fitted Scaling Law Parameters ===")
    print(f"  L0 = {L0:.4f}")
    print(f"  A  = {A:.4f}")
    print(f"  C  = {C:.4f}")
    print(f"  α  = {alpha:.4f}")
    
    # Check R^2 on training data (use log-space R² to match the fitting loss)
    pred_train = scaling_law_loss(S1_cosine, S2_cosine, params)
    eps = 1e-12
    pred_train_clipped = np.maximum(pred_train, eps)
    actual_clipped = np.maximum(actual_losses_cosine, eps)
    ss_res_log = np.sum((np.log(actual_clipped) - np.log(pred_train_clipped))**2)
    ss_tot_log = np.sum((np.log(actual_clipped) - np.mean(np.log(actual_clipped)))**2)
    r2_log = 1 - ss_res_log / ss_tot_log
    print(f"  Log-space R² = {r2_log:.6f}")
    
    # 4. Predict loss curves for other schedules using the fitted model
    print(f"\n=== Predictions on Other Schedules ===")
    
    # Predict on WSD schedule
    df_wsd = data_dict['M:100M_gpt_D:20B_scheduler:wsd_rope']
    actual_losses_wsd, lr_schedule_wsd = extract_loss_and_lr(df_wsd)
    predicted_wsd, S1_wsd, S2_wsd = predict_loss_curve(lr_schedule_wsd, params, decay_factor=0.999)
    
    # Calculate prediction error on WSD
    wsd_error = np.mean(np.abs(predicted_wsd - actual_losses_wsd) / actual_losses_wsd) * 100
    # Clip extreme predicted outliers for display/plotting to avoid misleading large maxima
    wsd_clip_thresh = max(1.0, actual_losses_wsd.max() * 5.0)
    if predicted_wsd.max() > wsd_clip_thresh:
        print(f"Warning: WSD predicted max {predicted_wsd.max():.3f} exceeds display threshold {wsd_clip_thresh:.3f}, clipping for plots.")
    predicted_wsd_display = np.minimum(predicted_wsd, wsd_clip_thresh)
    wsd_mape = np.mean(np.abs(predicted_wsd - actual_losses_wsd) / np.maximum(actual_losses_wsd, 1e-12)) * 100
    print(f"WSD Prediction Error: {wsd_error:.3f}%")
    print(f"WSD Loss range - Actual: [{actual_losses_wsd.min():.6f}, {actual_losses_wsd.max():.6f}]")
    print(f"WSD Loss range - Predicted (display clipped): [{predicted_wsd_display.min():.6f}, {predicted_wsd_display.max():.6f}]")
    
    # Predict on 8-1-1 schedule
    df_811 = data_dict['M:100M_gpt_D:20B_scheduler:811_rope']
    actual_losses_811, lr_schedule_811 = extract_loss_and_lr(df_811)
    predicted_811, S1_811, S2_811 = predict_loss_curve(lr_schedule_811, params, decay_factor=0.999)
    
    # Calculate prediction error on 8-1-1
    error_811 = np.mean(np.abs(predicted_811 - actual_losses_811) / actual_losses_811) * 100
    # Clip extreme predicted outliers for display/plotting
    clip811_thresh = max(1.0, actual_losses_811.max() * 5.0)
    if predicted_811.max() > clip811_thresh:
        print(f"Warning: 8-1-1 predicted max {predicted_811.max():.3f} exceeds display threshold {clip811_thresh:.3f}, clipping for plots.")
    predicted_811_display = np.minimum(predicted_811, clip811_thresh)
    mape_811 = np.mean(np.abs(predicted_811 - actual_losses_811) / np.maximum(actual_losses_811, 1e-12)) * 100
    print(f"\n8-1-1 Prediction Error: {error_811:.3f}%")
    print(f"8-1-1 Loss range - Actual: [{actual_losses_811.min():.6f}, {actual_losses_811.max():.6f}]")
    print(f"8-1-1 Loss range - Predicted (display clipped): [{predicted_811_display.min():.6f}, {predicted_811_display.max():.6f}]")
    
    # 5. Plot results
    fig, axes = plt.subplots(3, 1, figsize=(16, 8.4), constrained_layout=True)
    
    # Determine y-axis ranges from data with small padding (similar to reproduce_2's autoscaling)
    def compute_ylim(actual, predicted):
        ymin = min(np.min(actual), np.min(predicted))
        ymax = max(np.max(actual), np.max(predicted))
        rng = max(ymax - ymin, 1e-6)
        pad = max(0.05 * rng, 0.01)
        return ymin - pad, ymax + pad

    def compute_display_bounds(actual, predicted, lower_pct=2.0, upper_pct=98.0, pad_frac=0.05, min_pad=0.01):
        combined = np.concatenate([np.asarray(actual).ravel(), np.asarray(predicted).ravel()])
        if combined.size == 0:
            return compute_ylim(actual, predicted)
        lo = float(np.percentile(combined, lower_pct))
        hi = float(np.percentile(combined, upper_pct))
        rng = max(hi - lo, 1e-6)
        pad = max(pad_frac * rng, min_pad)
        return lo - pad, hi + pad

    # Use percentile-based display bounds for plotting axes to avoid extreme spikes
    y_min_cosine, y_max_cosine = compute_display_bounds(actual_losses_cosine, pred_train)
    y_min_wsd, y_max_wsd = compute_display_bounds(actual_losses_wsd, predicted_wsd)
    y_min_811, y_max_811 = compute_display_bounds(actual_losses_811, predicted_811)
    
    # Plot 1: Training fit on Cosine schedule
    cosine_x_plot, cosine_y_plot = downsample_series(steps_cosine, actual_losses_cosine, target_points=700)
    cosine_pred_x_plot, cosine_pred_y_plot = downsample_series(steps_cosine, pred_train, target_points=700)
    # Clip display to percentile-based bounds to avoid early extreme spikes dominating the axis
    c_lo, c_hi = compute_display_bounds(actual_losses_cosine, pred_train)
    cosine_y_plot_display = np.clip(cosine_y_plot, c_lo, c_hi)
    cosine_pred_y_plot_display = np.clip(cosine_pred_y_plot, c_lo, c_hi)
    axes[0].plot(cosine_x_plot, cosine_y_plot_display, label='Actual Loss', alpha=0.8, linewidth=1.35)
    axes[0].plot(cosine_pred_x_plot, cosine_pred_y_plot_display, label='Fitted Model', linestyle='--', linewidth=1.9, color='red')
    axes[0].set_xlabel('Step')
    axes[0].set_ylabel('Validation Loss')
    # let Matplotlib autoscale y-axis (avoid forcing limits)
    axes[0].legend(loc='best', fontsize=9)
    axes[0].set_title(f'Cosine Fit (Log-space R² = {r2_log:.4f})')
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Prediction on WSD schedule
    steps_wsd = np.arange(1, len(actual_losses_wsd) + 1)
    wsd_x_plot, wsd_y_plot = downsample_series(steps_wsd, actual_losses_wsd, target_points=700)
    wsd_pred_x_plot, wsd_pred_y_plot = downsample_series(steps_wsd, predicted_wsd, target_points=700)
    w_lo, w_hi = compute_display_bounds(actual_losses_wsd, predicted_wsd)
    wsd_y_plot_display = np.clip(wsd_y_plot, w_lo, w_hi)
    wsd_pred_y_plot_display = np.clip(wsd_pred_y_plot, w_lo, w_hi)
    axes[1].plot(wsd_x_plot, wsd_y_plot_display, label='Actual Loss', alpha=0.8, linewidth=1.35)
    axes[1].plot(wsd_pred_x_plot, wsd_pred_y_plot_display, label='Predicted Loss', linestyle='--', linewidth=1.9, color='red')
    axes[1].set_xlabel('Step')
    axes[1].set_ylabel('Validation Loss')
    # let Matplotlib autoscale y-axis (avoid forcing limits)
    axes[1].legend(loc='best', fontsize=9)
    axes[1].set_title(f'WSD Prediction (MAPE = {wsd_error:.3f}%)')
    axes[1].grid(True, alpha=0.3)
    
    # Plot 3: Prediction on 8-1-1 schedule
    steps_811 = np.arange(1, len(actual_losses_811) + 1)
    curve_811_x_plot, curve_811_y_plot = downsample_series(steps_811, actual_losses_811, target_points=700)
    pred_811_x_plot, pred_811_y_plot = downsample_series(steps_811, predicted_811, target_points=700)
    e_lo, e_hi = compute_display_bounds(actual_losses_811, predicted_811)
    curve_811_y_plot_display = np.clip(curve_811_y_plot, e_lo, e_hi)
    pred_811_y_plot_display = np.clip(pred_811_y_plot, e_lo, e_hi)
    axes[2].plot(curve_811_x_plot, curve_811_y_plot_display, label='Actual Loss', alpha=0.8, linewidth=1.35)
    axes[2].plot(pred_811_x_plot, pred_811_y_plot_display, label='Predicted Loss', linestyle='--', linewidth=1.9, color='red')
    axes[2].axvline(int(0.8 * len(steps_811)), color='gray', linestyle=':', alpha=0.5, label='80% (First Decay)')
    axes[2].axvline(int(0.9 * len(steps_811)), color='gray', linestyle=':', alpha=0.5, label='90% (Second Decay)')
    axes[2].set_xlabel('Step')
    axes[2].set_ylabel('Validation Loss')
    # let Matplotlib autoscale y-axis (avoid forcing limits)
    axes[2].legend(loc='best', fontsize=9)
    axes[2].set_title(f'8-1-1 Prediction (MAPE = {error_811:.3f}%)')
    axes[2].grid(True, alpha=0.3)
    
    output_filename = 'scaling_law_fit_and_prediction.png'
    output_path = make_plot_output_path(output_filename)
    plt.savefig(output_path, dpi=180, bbox_inches='tight')

    L0, A, C, alpha = params
    registry = load_figure_registry()
    registry = upsert_figure_entry(registry, {
        "filename": output_filename,
        "sort_order": 10,
        "description": "Three-panel stacked summary of the cosine fit and cross-schedule predictions.",
        "data_setting": "Fit on M:100M_gpt_D:20B_scheduler:cosine_rope; predict on WSD and 8-1-1.",
        "key_results": f"Cosine Log-space R² = {r2_log:.6f}; WSD MAPE = {wsd_error:.3f}%; 8-1-1 MAPE = {error_811:.3f}%.",
        "parameters": f"L0 = {L0:.6f}, A = {A:.6f}, C = {C:.6f}, alpha = {alpha:.6f}.",
    })
    registry['notes'] = [
        "Plot layout: 3 rows x 1 column for a flatter rectangular figure.",
        "Dense curves are downsampled before plotting to reduce visual clutter.",
        "The figure no longer embeds a text block; this file carries the narrative summary instead.",
        "The first panel shows training fit on cosine, the second panel shows prediction on WSD, and the third panel shows prediction on 8-1-1.",
    ]
    registry['latest_run'] = {
        "Cosine total steps": len(actual_losses_cosine),
        "Cosine loss range": f"[{actual_losses_cosine.min():.6f}, {actual_losses_cosine.max():.6f}]",
        "Cosine LR range": f"[{lr_schedule_cosine.min():.2e}, {lr_schedule_cosine.max():.2e}]",
        "Cosine Log-space R²": f"{r2_log:.6f}",
        "WSD prediction error": f"{wsd_error:.3f}%",
        "8-1-1 prediction error": f"{error_811:.3f}%",
    }
    registry['script_notes'] = [
        "Source script: reproduce_1.py",
        f"Output image: {output_filename}",
        "Metadata source: figure_registry.json",
    ]
    registry_path = write_figure_registry(registry)
    report_path = write_results_summary(os.path.dirname(output_path), registry)

    train_frame = build_prediction_frame(
        'train',
        schedule_for_fitting,
        steps_cosine,
        actual_losses_cosine,
        pred_train,
        lr_schedule_cosine,
        S1_cosine,
        S2_cosine,
    )
    wsd_frame = build_prediction_frame(
        'test',
        'M:100M_gpt_D:20B_scheduler:wsd_rope',
        steps_wsd,
        actual_losses_wsd,
        predicted_wsd,
        lr_schedule_wsd,
        S1_wsd,
        S2_wsd,
    )
    curve_811_frame = build_prediction_frame(
        'test',
        'M:100M_gpt_D:20B_scheduler:811_rope',
        steps_811,
        actual_losses_811,
        predicted_811,
        lr_schedule_811,
        S1_811,
        S2_811,
    )
    run_dir = make_run_dir('tissue_baseline')
    artifact_paths = save_experiment_artifacts(
        run_dir,
        params,
        result,
        {
            'schedule_name': schedule_for_fitting,
            'frame': train_frame,
            'curve_frame': pd.DataFrame({
                'step': steps_cosine,
                'loss': actual_losses_cosine,
                'lr': lr_schedule_cosine,
                's1': S1_cosine,
                's2': S2_cosine,
            }),
        },
        [
            {
                'schedule_name': 'M:100M_gpt_D:20B_scheduler:wsd_rope',
                'frame': wsd_frame,
                'curve_frame': pd.DataFrame({
                    'step': steps_wsd,
                    'loss': actual_losses_wsd,
                    'lr': lr_schedule_wsd,
                    's1': S1_wsd,
                    's2': S2_wsd,
                }),
            },
            {
                'schedule_name': 'M:100M_gpt_D:20B_scheduler:811_rope',
                'frame': curve_811_frame,
                'curve_frame': pd.DataFrame({
                    'step': steps_811,
                    'loss': actual_losses_811,
                    'lr': lr_schedule_811,
                    's1': S1_811,
                    's2': S2_811,
                }),
            },
        ],
        {
            'decay_factor': 0.999,
            'figure_file': output_path,
            'train_metrics': {'log_r2': r2_log},
            'wsd_metrics': {'mape': wsd_mape},
            '811_metrics': {'mape': mape_811},
            'method_name': 'tissue_scaling_law',
        },
    )

    # Fit a lightweight improved variant with an early-stage transient correction.
    print(f"\n=== Fitting Improved Tissue Variant ===")
    progress_cosine = np.linspace(0.0, 1.0, len(actual_losses_cosine), endpoint=True)
    params_improved, result_improved = fit_improved_scaling_law(S1_cosine, S2_cosine, progress_cosine, actual_losses_cosine)
    L0_i, A_i, C_i, alpha_i, D_i, tau_i = params_improved
    print(f"  L0 = {L0_i:.4f}")
    print(f"  A  = {A_i:.4f}")
    print(f"  C  = {C_i:.4f}")
    print(f"  α  = {alpha_i:.4f}")
    print(f"  D  = {D_i:.4f}")
    print(f"  τ  = {tau_i:.4f}")

    pred_train_improved = improved_scaling_law_loss(S1_cosine, S2_cosine, progress_cosine, params_improved)
    pred_train_improved_clipped = np.maximum(pred_train_improved, eps)
    ss_res_log_improved = np.sum((np.log(actual_clipped) - np.log(pred_train_improved_clipped))**2)
    r2_log_improved = 1 - ss_res_log_improved / ss_tot_log
    print(f"  Improved Log-space R² = {r2_log_improved:.6f}")

    predicted_wsd_improved, S1_wsd_improved, S2_wsd_improved, progress_wsd_improved = predict_improved_loss_curve(lr_schedule_wsd, params_improved, decay_factor=0.999)
    wsd_error_improved = np.mean(np.abs(predicted_wsd_improved - actual_losses_wsd) / actual_losses_wsd) * 100

    predicted_811_improved, S1_811_improved, S2_811_improved, progress_811_improved = predict_improved_loss_curve(lr_schedule_811, params_improved, decay_factor=0.999)
    mape_811_improved = np.mean(np.abs(predicted_811_improved - actual_losses_811) / np.maximum(actual_losses_811, 1e-12)) * 100

    improved_train_frame = build_prediction_frame(
        'train',
        schedule_for_fitting,
        steps_cosine,
        actual_losses_cosine,
        pred_train_improved,
        lr_schedule_cosine,
        S1_cosine,
        S2_cosine,
    )
    improved_wsd_frame = build_prediction_frame(
        'test',
        'M:100M_gpt_D:20B_scheduler:wsd_rope',
        steps_wsd,
        actual_losses_wsd,
        predicted_wsd_improved,
        lr_schedule_wsd,
        S1_wsd_improved,
        S2_wsd_improved,
    )
    improved_811_frame = build_prediction_frame(
        'test',
        'M:100M_gpt_D:20B_scheduler:811_rope',
        steps_811,
        actual_losses_811,
        predicted_811_improved,
        lr_schedule_811,
        S1_811_improved,
        S2_811_improved,
    )
    run_dir_improved = make_run_dir('tissue_improved')
    artifact_paths_improved = save_experiment_artifacts(
        run_dir_improved,
        params_improved,
        result_improved,
        {
            'schedule_name': schedule_for_fitting,
            'frame': improved_train_frame,
            'curve_frame': pd.DataFrame({
                'step': steps_cosine,
                'loss': actual_losses_cosine,
                'lr': lr_schedule_cosine,
                's1': S1_cosine,
                's2': S2_cosine,
            }),
        },
        [
            {
                'schedule_name': 'M:100M_gpt_D:20B_scheduler:wsd_rope',
                'frame': improved_wsd_frame,
                'curve_frame': pd.DataFrame({
                    'step': steps_wsd,
                    'loss': actual_losses_wsd,
                    'lr': lr_schedule_wsd,
                    's1': S1_wsd_improved,
                    's2': S2_wsd_improved,
                }),
            },
            {
                'schedule_name': 'M:100M_gpt_D:20B_scheduler:811_rope',
                'frame': improved_811_frame,
                'curve_frame': pd.DataFrame({
                    'step': steps_811,
                    'loss': actual_losses_811,
                    'lr': lr_schedule_811,
                    's1': S1_811_improved,
                    's2': S2_811_improved,
                }),
            },
        ],
        {
            'decay_factor': 0.999,
            'figure_file': output_path,
            'train_metrics': {'log_r2': r2_log_improved},
            'wsd_metrics': {'mape': wsd_error_improved},
            '811_metrics': {'mape': mape_811_improved},
            'method_name': 'tissue_transient_correction',
        },
    )
    diagnostic_path = generate_residual_diagnostic_figure(
        artifact_paths['residuals'],
        artifact_paths_improved['residuals'],
    )
    print(f"✓ Improved run artifacts saved to '{run_dir_improved}'")
    print(f"✓ Improved WSD Prediction Error: {wsd_error_improved:.3f}%")
    print(f"✓ Improved 8-1-1 Prediction Error: {mape_811_improved:.3f}%")
    print(f"\n✓ Plot saved to '{output_path}'")
    print(f"✓ Residual diagnostic saved to '{diagnostic_path}'")
    print(f"✓ Registry saved to '{registry_path}'")
    print(f"✓ Summary saved to '{report_path}'")
    print(f"✓ Run artifacts saved to '{run_dir}'")
    
    return params, (predicted_wsd, predicted_811), artifact_paths

if __name__ == "__main__":
    params, prediction, artifacts = example_workflow()
