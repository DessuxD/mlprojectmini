import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta

def generate_synthetic_data(num_samples=1000):
    np.random.seed(42)
    
    # Input features with realistic ranges
    # Granulation Time (mins): 20 to 60
    granulation_time = np.random.normal(40, 10, num_samples)
    
    # Binder Amount (kg): 2 to 10
    binder_amount = np.random.normal(6, 2, num_samples)
    
    # Drying Temperature (C): 40 to 80
    drying_temp = np.random.normal(60, 10, num_samples)
    
    # Drying Time (mins): 30 to 120
    drying_time = np.random.normal(75, 20, num_samples)
    
    # Compression Force (kN): 10 to 30
    compression_force = np.random.normal(20, 5, num_samples)
    
    # Machine Speed (rpm): 20 to 60
    machine_speed = np.random.normal(40, 10, num_samples)
    
    # Clip values to ensure no physically impossible negative or out of bounds values
    granulation_time = np.clip(granulation_time, 15, 75)
    binder_amount = np.clip(binder_amount, 1, 15)
    drying_temp = np.clip(drying_temp, 30, 95)
    drying_time = np.clip(drying_time, 20, 150)
    compression_force = np.clip(compression_force, 5, 40)
    machine_speed = np.clip(machine_speed, 10, 80)
    
    # --- Feature Engineering & Interactions for Targets ---
    
    # 1. Energy Consumption (kWh)
    # Increases with temp, time, compression force, and speed
    energy = (drying_temp * drying_time * 0.05) + (compression_force * machine_speed * 0.08) + (granulation_time * 0.5)
    # Add noise
    energy += np.random.normal(0, 15, num_samples)
    
    # Introduce energy anomalies (spikes) randomly in 5% of data
    anomaly_indices = np.random.choice(num_samples, size=int(0.05 * num_samples), replace=False)
    energy[anomaly_indices] *= np.random.uniform(1.5, 2.5, size=len(anomaly_indices))
    
    # 2. Yield (%)
    # Best yield when binder is around 6-8, compression force around 20-25
    binder_penalty = np.abs(binder_amount - 7) * 2
    compression_penalty = np.abs(compression_force - 22) * 1.5
    yield_pct = 100 - binder_penalty - compression_penalty - np.random.normal(2, 3, num_samples)
    yield_pct = np.clip(yield_pct, 60, 99.9)
    
    # 3. Quality (%)
    # Best quality when drying temp is around 60 and drying time is around 75
    temp_penalty = np.abs(drying_temp - 60) * 1.2
    time_penalty = np.abs(drying_time - 75) * 0.5
    quality_pct = 100 - temp_penalty - time_penalty - np.random.normal(1, 2, num_samples)
    quality_pct = np.clip(quality_pct, 50, 99.9)
    
    # 4. Performance Score (0-100)
    # High yield and high quality, but penalize high energy
    normalized_energy = (energy - np.min(energy)) / (np.max(energy) - np.min(energy) + 1e-5)
    performance = (yield_pct * 0.4) + (quality_pct * 0.4) - (normalized_energy * 30)
    performance = np.clip(performance, 0, 100)
    
    # Generate batch IDs and timestamps
    base_time = datetime.now() - timedelta(days=30)
    timestamps = [base_time + timedelta(hours=i*4) for i in range(num_samples)]
    batch_ids = [f"BATCH_{1000+i}" for i in range(num_samples)]
    
    df = pd.DataFrame({
        'batch_id': batch_ids,
        'timestamp': [t.strftime("%Y-%m-%d %H:%M:%S") for t in timestamps],
        'granulation_time': np.round(granulation_time, 2),
        'binder_amount': np.round(binder_amount, 2),
        'drying_temp': np.round(drying_temp, 2),
        'drying_time': np.round(drying_time, 2),
        'compression_force': np.round(compression_force, 2),
        'machine_speed': np.round(machine_speed, 2),
        'energy_consumption': np.round(energy, 2),
        'yield_pct': np.round(yield_pct, 2),
        'quality_pct': np.round(quality_pct, 2),
        'performance_score': np.round(performance, 2)
    })
    
    return df

def init_data(data_dir="data"):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    df = generate_synthetic_data(1000)
    csv_path = os.path.join(data_dir, "batch_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"Generated {len(df)} samples and saved to {csv_path}")
    
    # Also save the last 50 as history for the dashboard in JSON format
    history = df.tail(50).to_dict(orient='records')
    json_path = os.path.join(data_dir, "batch_history.json")
    with open(json_path, 'w') as f:
        json.dump(history, f, indent=4)
    print(f"Saved {len(history)} recent batches to {json_path}")
    
if __name__ == "__main__":
    # Create the data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    init_data(data_dir)
