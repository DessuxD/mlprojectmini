import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import xgboost as xgb
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def train_models():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, "data", "batch_data.csv")
    model_dir = os.path.join(project_root, "models")
    
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    df = pd.read_csv(data_path)
    
    features = [
        'granulation_time', 'binder_amount', 'drying_temp',
        'drying_time', 'compression_force', 'machine_speed'
    ]
    targets = [
        'energy_consumption', 'yield_pct', 'quality_pct', 'performance_score'
    ]
    
    X = df[features]
    y = df[targets]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 1. Anomaly Detection (Isolation Forest on Input Features)
    # This flags if parameters are wildly out of normal ranges
    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    iso_forest.fit(X_train_scaled)
    
    # 2. Multi-output Regression
    # We use XGBoost
    xgb_estimator = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    # Using MultiOutputRegressor to fit one regressor per target
    model = MultiOutputRegressor(xgb_estimator)
    model.fit(X_train_scaled, y_train)
    
    # Evaluation
    predictions = model.predict(X_test_scaled)
    
    print("--- Model Evaluation ---")
    for i, target in enumerate(targets):
        pred_i = predictions[:, i]
        actual_i = y_test.iloc[:, i].values
        
        mae = mean_absolute_error(actual_i, pred_i)
        rmse = np.sqrt(mean_squared_error(actual_i, pred_i))
        r2 = r2_score(actual_i, pred_i)
        
        mape = np.mean(np.abs((actual_i - pred_i) / actual_i)) * 100
        
        print(f"Target: {target}")
        print(f"  MAE:  {mae:.4f}")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  R2:   {r2:.4f}")
        print(f"  MAPE: {mape:.4f}%")
        print()
    
    # Calculate energy residuals for z-score anomaly detection later
    train_predictions = model.predict(X_train_scaled)
    energy_residuals = y_train['energy_consumption'].values - train_predictions[:, 0]
    energy_residual_std = np.std(energy_residuals)
    
    # Save the models
    joblib.dump(scaler, os.path.join(model_dir, "scaler.joblib"))
    joblib.dump(iso_forest, os.path.join(model_dir, "iso_forest.joblib"))
    joblib.dump(model, os.path.join(model_dir, "xgb_multi_model.joblib"))
    
    # Save some metadata
    metadata = {
        'features': features,
        'targets': targets,
        'energy_residual_std': float(energy_residual_std)
    }
    with open(os.path.join(model_dir, "metadata.json"), 'w') as f:
        import json
        json.dump(metadata, f, indent=4)
        
    print("Models saved successfully.")

if __name__ == "__main__":
    train_models()
