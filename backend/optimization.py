import optuna
import joblib
import numpy as np
import os
import shap
import pandas as pd

# Suppress Optuna logging to prevent spam
optuna.logging.set_verbosity(optuna.logging.WARNING)

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
model_dir = os.path.join(project_root, "models")

scaler_path = os.path.join(model_dir, "scaler.joblib")
model_path = os.path.join(model_dir, "xgb_multi_model.joblib")

try:
    scaler = joblib.load(scaler_path)
    model = joblib.load(model_path)
except Exception as e:
    print(f"Warning: Models not loaded. {e}")
    scaler = None
    model = None

explainer = None

def get_shap_values(input_dict):
    """
    Returns SHAP feature importance for energy consumption.
    """
    global explainer
    
    if scaler is None or model is None:
        return []

    if explainer is None:
        # MultiOutputRegressor wraps a list of estimators. 
        # Target 0 is energy_consumption
        xgb_energy_model = model.estimators_[0]
        explainer = shap.TreeExplainer(xgb_energy_model)
    
    # Ensure order
    features = [
        'granulation_time', 'binder_amount', 'drying_temp',
        'drying_time', 'compression_force', 'machine_speed'
    ]
    
    df = pd.DataFrame([input_dict], columns=features)
    scaled_input = scaler.transform(df)
    
    shap_values = explainer.shap_values(scaled_input)
    vals = shap_values[0]
    
    result = []
    for i, feature in enumerate(features):
        result.append({
            "feature": feature,
            "value": float(vals[i])
        })
    return result

def optimize_parameters(current_params):
    """
    Find optimal parameters using Optuna.
    Objective: Minimize Energy while ensuring Quality >= 90% and Yield >= 90%.
    """
    if scaler is None or model is None:
        return current_params, [0, 0, 0]

    def objective(trial):
        # Define search space relative to current params or global
        # To make it realistic, search around +/- 30% of current params, bounded by global limits
        def get_bounds(val, min_b, max_b):
            return max(min_b, val * 0.7), min(max_b, val * 1.3)
            
        gt = trial.suggest_float("granulation_time", *get_bounds(current_params['granulation_time'], 15, 75))
        ba = trial.suggest_float("binder_amount", *get_bounds(current_params['binder_amount'], 1, 15))
        dt = trial.suggest_float("drying_temp", *get_bounds(current_params['drying_temp'], 30, 95))
        dtime = trial.suggest_float("drying_time", *get_bounds(current_params['drying_time'], 20, 150))
        cf = trial.suggest_float("compression_force", *get_bounds(current_params['compression_force'], 5, 40))
        ms = trial.suggest_float("machine_speed", *get_bounds(current_params['machine_speed'], 10, 80))
        
        X_df = pd.DataFrame([{
            'granulation_time': gt,
            'binder_amount': ba,
            'drying_temp': dt,
            'drying_time': dtime,
            'compression_force': cf,
            'machine_speed': ms
        }])
        
        X_scaled = scaler.transform(X_df)
        preds = model.predict(X_scaled)[0]
        
        energy = preds[0]
        yield_pct = preds[1]
        quality_pct = preds[2]
        
        return energy, yield_pct, quality_pct

    # Minimize energy, maximize yield, maximize quality
    study = optuna.create_study(directions=["minimize", "maximize", "maximize"])
    study.optimize(objective, n_trials=100)
    
    valid_trials = []
    for t in study.trials:
        if t.values and len(t.values) == 3:
            eng, yld, qual = t.values
            if qual >= 90 and yld >= 90:
                valid_trials.append(t)
                
    if not valid_trials:
        # Fallback: minimize energy - 10*(yield + quality)
        best_trial = min(study.trials, key=lambda t: t.values[0] - 10*(t.values[1] + t.values[2]))
    else:
        # valid trial with lowest energy
        best_trial = min(valid_trials, key=lambda t: t.values[0])
        
    return best_trial.params, best_trial.values

if __name__ == "__main__":
    pass
