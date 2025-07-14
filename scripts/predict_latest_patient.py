#!/usr/bin/env python3
"""
Script to predict heart disease on the latest patient using a saved Keras model.
"""

import os, sys
import requests
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler

# Load project paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from api.database import SessionLocal

# Constants
API_BASE_URL = "http://127.0.0.1:8000"
MODEL_PATH = "models/heart_disease_model.h5.pkl"
MONGO_URL = "mongodb://localhost:27017/"

def fetch_latest_patient():
    print("📥 Fetching latest patient...")
    try:
        res = requests.get(f"{API_BASE_URL}/patients/latest/data")
        if res.status_code == 200:
            return res.json()
        else:
            print(f"❌ Failed to fetch: Status code {res.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return None

def preprocess(patient):
    print("🔄 Preprocessing patient data...")
    df = pd.DataFrame([patient])

    # Mapping for encoding categorical fields
    mappings = {
        'sex': {'Male': 1, 'Female': 0},
        'cp': {'typical angina': 0, 'atypical angina': 1, 'non-anginal': 2, 'asymptomatic': 3},
        'restecg': {'normal': 0, 'st-t abnormality': 1, 'lv hypertrophy': 2},
        'slope': {'upsloping': 0, 'flat': 1, 'downsloping': 2},
        'thal': {'normal': 0, 'fixed defect': 1, 'reversable defect': 2},
        'fbs': {'FALSE': 0, 'TRUE': 1},
        'exang': {'FALSE': 0, 'TRUE': 1},
    }

    # Encode all required fields
    df['sex_encoded'] = df['sex'].map(mappings['sex'])
    df['cp_encoded'] = df['cp'].map(mappings['cp'])
    df['fbs_encoded'] = df['fbs'].map(mappings['fbs'])
    df['restecg_encoded'] = df['restecg'].map(mappings['restecg'])
    df['exang_encoded'] = df['exang'].map(mappings['exang'])
    df['slope_encoded'] = df['slope'].map(mappings['slope']).fillna(1)
    df['thal_encoded'] = df['thal'].map(mappings['thal']).fillna(0)
    df['ca'] = df['ca'].fillna(0)

    features = [
        'age', 'sex_encoded', 'cp_encoded', 'trestbps', 'chol', 'fbs_encoded',
        'restecg_encoded', 'thalch', 'exang_encoded', 'oldpeak', 'slope_encoded',
        'ca', 'thal_encoded'
    ]

    X = df[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled

def load_model():
    print("📦 Loading model...")
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def store_prediction_in_mongo(patient_id, pred, prob, confidence, risk_level, patient_data):
    try:
        mongo = MongoClient(MONGO_URL)
        collection = mongo["heart_disease_predictor"]["predictions"]
        collection.insert_one({
            "patient_id": patient_id,
            "prediction": pred,
            "probability": float(prob),
            "confidence": float(confidence),
            "risk_level": risk_level,
            "timestamp": datetime.now(),
            "patient_data": patient_data,
            "model_type": "keras_neural_network"
        })
        print("✅ Stored prediction in MongoDB")
    except Exception as e:
        print(f"⚠️ Failed to store prediction: {e}")

def predict_and_log():
    model = load_model()
    patient = fetch_latest_patient()

    if not patient:
        print("❌ No patient data available.")
        return

    X = preprocess(patient)
    prob = model.predict(X)[0][0]
    pred = 1 if prob > 0.5 else 0
    confidence = prob if pred == 1 else (1 - prob)
    risk = "High Risk" if pred else "Low Risk"

    print(f"\n📌 Patient ID: {patient['id']} – {risk} ({confidence:.2%})")
    store_prediction_in_mongo(
        patient_id=patient["id"],
        pred=pred,
        prob=prob,
        confidence=confidence,
        risk_level=risk,
        patient_data=patient
    )

def main():
    predict_and_log()

if __name__ == "__main__":
    main()
