from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import json
from typing import List, Dict, Any, Optional

from .optimization import optimize_parameters, get_shap_values

app = FastAPI(title="Batch Process API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
model_dir = os.path.join(project_root, "models")
data_dir = os.path.join(project_root, "data")

try:
    scaler = joblib.load(os.path.join(model_dir, "scaler.joblib"))
    model = joblib.load(os.path.join(model_dir, "xgb_multi_model.joblib"))
    iso_forest = joblib.load(os.path.join(model_dir, "iso_forest.joblib"))
    with open(os.path.join(model_dir, "metadata.json"), 'r') as f:
        metadata = json.load(f)
except Exception as e:
    print(f"Warning: Models not loaded. {e}")
    metadata = {'energy_residual_std': 10.0}

class BatchInput(BaseModel):
    granulation_time: float
    binder_amount: float
    drying_temp: float
    drying_time: float
    compression_force: float
    machine_speed: float

class AnomalyInput(BatchInput):
    actual_energy: Optional[float] = None

@app.get("/history")
def get_history():
    history_path = os.path.join(data_dir, "batch_history.json")
    if os.path.exists(history_path):
        with open(history_path, 'r') as f:
            return json.load(f)
    return []

@app.post("/predict")
def predict(data: BatchInput):
    input_dict = data.dict()
    df = pd.DataFrame([input_dict])
    
    scaled_input = scaler.transform(df)
    preds = model.predict(scaled_input)[0]
    
    # Check if anomalous parameters
    anomaly_score = iso_forest.predict(scaled_input)[0]
    is_anomaly = int(anomaly_score) == -1
    
    return {
        "predictions": {
            "energy_consumption": float(preds[0]),
            "yield_pct": float(preds[1]),
            "quality_pct": float(preds[2]),
            "performance_score": float(preds[3])
        },
        "is_parameter_anomaly": is_anomaly
    }

@app.post("/anomaly")
def check_anomaly(data: AnomalyInput):
    input_dict = data.dict(exclude={'actual_energy'})
    df = pd.DataFrame([input_dict])
    scaled_input = scaler.transform(df)
    
    preds = model.predict(scaled_input)[0]
    pred_energy = float(preds[0])
    
    alerts = []
    
    if data.actual_energy is not None:
        residual = data.actual_energy - pred_energy
        std = metadata.get('energy_residual_std', 10.0)
        
        if residual > 2 * std:
            alerts.append("Energy Spike Detected")
        elif residual > std:
            alerts.append("High Energy Usage")
            
        if data.actual_energy > pred_energy * 1.2:
            alerts.append("Deviation from predicted vs actual")
            
    # Check parameter anomalies as well
    anomaly_score = iso_forest.predict(scaled_input)[0]
    if int(anomaly_score) == -1:
        alerts.append("Unusual Parameters Detected")
        
    return {
        "alerts": alerts,
        "predicted_energy": pred_energy,
        "actual_energy": data.actual_energy
    }

@app.post("/optimize")
def optimize(data: BatchInput):
    input_dict = data.dict()
    best_params, best_values = optimize_parameters(input_dict)
    
    recommendations = []
    for key in input_dict:
        diff = best_params[key] - input_dict[key]
        if abs(diff) > input_dict[key] * 0.05: # > 5% change
            action = "Increase" if diff > 0 else "Reduce"
            name = key.replace('_', ' ').title()
            recommendations.append(f"{action} {name} to {best_params[key]:.1f}")
            
    return {
        "optimal_parameters": best_params,
        "expected_outcomes": {
            "energy_consumption": float(best_values[0]),
            "yield_pct": float(best_values[1]),
            "quality_pct": float(best_values[2])
        },
        "recommendations": recommendations
    }

@app.post("/explain")
def explain(data: BatchInput):
    input_dict = data.dict()
    shap_values = get_shap_values(input_dict)
    
    # Sort by absolute impact
    shap_values.sort(key=lambda x: abs(x['value']), reverse=True)
    
    return {
        "shap_values": shap_values
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
