#!/usr/bin/env python3
"""
Training Script for XGBoost ETA and Queue Prediction Models.

Loads pilgrimage traffic data from 'tirthtrack_eta_training_dataset_100000.json'
and trains high-precision XGBoost regression models for travel duration & queue waiting time.
Exports JSON model artifacts to app/ml/artifacts/

Usage:
    python scripts/train_xgboost_model.py
"""

import json
import os
import sys
import numpy as np

# Ensure project root is in import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
except ImportError as e:
    print(f"Error: Missing required packages for training: {e}")
    print("Please ensure dependencies are installed via: pip install -r requirements.txt")
    sys.exit(1)


def find_dataset_file() -> str:
    """Find the dataset file path across standard search locations."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, "..", "..", "tirthtrack_eta_training_dataset_100000.json"),
        os.path.join(script_dir, "..", "tirthtrack_eta_training_dataset_100000.json"),
        os.path.abspath("tirthtrack_eta_training_dataset_100000.json"),
    ]
    for candidate in candidates:
        norm = os.path.normpath(candidate)
        if os.path.exists(norm):
            return norm
    return ""


def load_dataset_records(dataset_path: str) -> list[dict]:
    """Load JSON records from dataset file."""
    print("Loading dataset from", dataset_path)
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "records" in data:
        records = data["records"]
    elif isinstance(data, list):
        records = data
    else:
        records = []
    print(f"Successfully loaded {len(records):,} records.")
    return records


def extract_features_from_records(records: list[dict]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Extract feature matrices and targets for ETA travel duration and queue waiting time models."""
    n_samples = len(records)
    
    # Feature matrices allocation
    X_eta = np.zeros((n_samples, 11), dtype=np.float32)
    y_eta = np.zeros(n_samples, dtype=np.float32)

    X_queue = np.zeros((n_samples, 7), dtype=np.float32)
    y_queue = np.zeros(n_samples, dtype=np.float32)

    for i, r in enumerate(records):
        dist = float(r.get("route_distance_meters", 0.0))
        base_dur = float(r.get("route_duration_seconds", 0.0))
        hour = float(r.get("hour_of_day", 12))
        dow = float(r.get("day_of_week", 0))
        crowd = float(r.get("crowd_density_index", 0.0))
        fest = 1.0 if r.get("festival_active", False) else 0.0
        weather = float(r.get("weather_severity", 0.0))
        traffic = float(r.get("traffic_density", 0.0))
        closure = 1.0 if r.get("road_closure", False) else 0.0
        accident = 1.0 if r.get("accident_reported", False) else 0.0
        holiday = 1.0 if r.get("holiday", False) else 0.0

        # Travel duration features (11):
        # [distance_meters, base_duration_seconds, hour_of_day, day_of_week, crowd_density_index, is_festival, weather_severity, traffic_density, road_closure, accident_reported, holiday]
        X_eta[i] = [dist, base_dur, hour, dow, crowd, fest, weather, traffic, closure, accident, holiday]
        y_eta[i] = float(r.get("actual_travel_time_seconds", base_dur))

        # Queue features (7):
        # [arrival_hour, day_of_week, crowd_density_index, is_festival, weather_severity, traffic_density, holiday]
        X_queue[i] = [hour, dow, crowd, fest, weather, traffic, holiday]
        y_queue[i] = float(r.get("queue_time_seconds", 0.0))

    return X_eta, y_eta, X_queue, y_queue


def train_and_save_models():
    """Train XGBoost models on the pilgrimage dataset and export JSON artifacts."""
    output_dir = os.path.join(os.path.dirname(__file__), "..", "app", "ml", "artifacts")
    os.makedirs(output_dir, exist_ok=True)

    print("==================================================")
    print("Training XGBoost ETA & Queue Models...")
    print("==================================================")

    dataset_path = find_dataset_file()
    if dataset_path:
        records = load_dataset_records(dataset_path)
        X_eta, y_eta, X_queue, y_queue = extract_features_from_records(records)
    else:
        print("[Warning] Real dataset file not found. Generating synthetic fallback dataset...")
        # Synthetic fallback logic
        np.random.seed(42)
        n = 5000
        dist = np.random.uniform(500, 50000, n)
        base_dur = dist / np.random.uniform(8.0, 20.0, n)
        hour = np.random.randint(0, 24, n)
        dow = np.random.randint(0, 7, n)
        crowd = np.random.uniform(0.0, 1.0, n)
        fest = np.random.choice([0.0, 1.0], size=n, p=[0.8, 0.2])
        weather = np.random.uniform(0.0, 1.0, n)
        traffic = np.random.uniform(0.0, 1.0, n)
        closure = np.random.choice([0.0, 1.0], size=n, p=[0.95, 0.05])
        accident = np.random.choice([0.0, 1.0], size=n, p=[0.95, 0.05])
        holiday = np.random.choice([0.0, 1.0], size=n, p=[0.9, 0.1])

        X_eta = np.column_stack([dist, base_dur, hour, dow, crowd, fest, weather, traffic, closure, accident, holiday])
        delay = 1.0 + (crowd * 0.6) + (traffic * 0.5) + (fest * 0.4) + (weather * 0.3)
        y_eta = base_dur * delay

        X_queue = np.column_stack([hour, dow, crowd, fest, weather, traffic, holiday])
        y_queue = (crowd * 30.0 + fest * 45.0) * 60.0

    # 1. Train Travel Duration Model
    print("\n[1/2] Training Travel Duration Model (XGBoost Regressor)...")
    X_train, X_test, y_train, y_test = train_test_split(X_eta, y_eta, test_size=0.2, random_state=42)

    eta_model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=7,
        learning_rate=0.06,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        n_jobs=-1,
    )
    eta_model.fit(X_train, y_train)

    y_pred = eta_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    print(f"   -> Travel Model Test MAE: {mae:.2f} seconds ({mae/60:.2f} mins)")
    print(f"   -> Travel Model Test RMSE: {rmse:.2f} seconds")
    print(f"   -> Travel Model Test R2 Score: {r2:.4f}")

    eta_model_path = os.path.join(output_dir, "xgb_eta_model.json")
    eta_model.save_model(eta_model_path)
    print(f"   -> Saved ETA model to: {eta_model_path}")

    # 2. Train Queue Waiting Time Model
    print("\n[2/2] Training Temple Queue Waiting Model (XGBoost Regressor)...")
    X_train_q, X_test_q, y_train_q, y_test_q = train_test_split(X_queue, y_queue, test_size=0.2, random_state=42)

    queue_model = xgb.XGBRegressor(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.06,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        n_jobs=-1,
    )
    queue_model.fit(X_train_q, y_train_q)

    y_pred_q = queue_model.predict(X_test_q)
    mae_q = mean_absolute_error(y_test_q, y_pred_q)
    rmse_q = np.sqrt(mean_squared_error(y_test_q, y_pred_q))
    r2_q = r2_score(y_test_q, y_pred_q)
    print(f"   -> Queue Model Test MAE: {mae_q:.2f} seconds ({mae_q/60:.2f} mins)")
    print(f"   -> Queue Model Test RMSE: {rmse_q:.2f} seconds")
    print(f"   -> Queue Model Test R2 Score: {r2_q:.4f}")

    queue_model_path = os.path.join(output_dir, "xgb_queue_model.json")
    queue_model.save_model(queue_model_path)
    print(f"   -> Saved Queue model to: {queue_model_path}")

    print("\n==================================================")
    print("Model training complete! Artifacts saved successfully.")
    print("==================================================")


if __name__ == "__main__":
    train_and_save_models()
