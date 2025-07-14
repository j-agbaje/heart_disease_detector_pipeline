#!/usr/bin/env python3
"""
Script to load heart data to MySQL and predict latest patient using saved Keras model
"""

import os, sys
import pandas as pd
import numpy as np
import tensorflow as tf
import requests
from pymongo import MongoClient
from datetime import datetime
from sklearn.preprocessing import LabelEncoder, SimpleImputer, StandardScaler
from sqlalchemy import text
import pickle

# Paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.database import SessionLocal

# Constants
API_BASE_URL = "http://localhost:8000"
MONGO_URL = "mongodb://localhost:27017/"
MODEL_PATH = "models/heart_disease_model.h5.pkl"

# === Load and preprocess CSV === #
def preprocess_csv(df):
    data = df.copy()
    data.drop(["id", "dataset"], axis=1, inplace=True)
    
    categorical = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
    for col in categorical:
        data[col] = LabelEncoder().fit_transform(data[col].astype(str))

    imputer = SimpleImputer(strategy="median")
    numerical = ["age", "trestbps", "chol", "thalch", "oldpeak"]
    data[numerical] = imputer.fit_transform(data[numerical])

    data["num"] = data["num"].apply(lambda x: 0 if x == 0 else 1)
    return data

def clear_existing_data():
    db = SessionLocal()
    db.execute(text("DELETE FROM patients"))
    db.commit()
    db.close()
    print("✅ Cleared existing patient records")

def insert_to_mysql(data):
    db = SessionLocal()
    for _, row in data.iterrows():
        query = text("""
            INSERT INTO patients (
                patient_age, gender, chest_pain_type, resting_blood_pressure, 
                cholesterol_level, fasting_blood_sugar, resting_ecg_results, 
                max_heart_rate, exercise_induced_angina, st_depression, 
                exercise_peak_slope, major_vessels_count, thalassemia_type, 
                heart_disease_diagnosis
            ) VALUES (
                :age, :sex, :cp, :trestbps, :chol, :fbs, :restecg, 
                :thalch, :exang, :oldpeak, :slope, :ca, :thal, :num
            )
        """)
        db.execute(query, row.to_dict())
    db.commit()
    db.close()
    print("✅ Inserted CSV data to MySQL")

# === Model Prediction === #
def load_model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def fetch_latest_patient():
    try:
        res = requests.get(f"{API_BASE_URL}/patients/latest/data")
        return res.json() if res.status_code == 200 else None
    except:
        print("❌ Could not fetch latest patient from API.")
        return None

def preprocess_patient(patient):
    mappings = {
        'sex': {'Male': 1, 'Female': 0},
        'cp': {'typical angina': 0, 'atypical angina': 1, 'non-anginal': 2, 'asymptomatic': 3},
        'restecg': {'normal': 0, 'st-t abnormality': 1, 'lv hypertrophy': 2},
        'slope': {'upsloping': 0, 'flat': 1, 'downsloping': 2},
        'thal': {'normal': 0, 'fixed defect': 1, 'reversable defect': 2}
    }
    df = pd.DataFrame([patient])
    df['sex_encoded'] = df['sex'].map(mappings['sex'])
    df['cp_encoded'] = df['cp'].map(mappings['cp'])
    df['fbs_encoded'] = df['fbs'].astype(int)
    df['restecg_encoded'] = df['restecg'].map(mappings['restecg'])
    df['exang_encoded'] = df['exang'].astype(int)
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
    return scaler.fit_transform(X)

def predict_latest():
    model = load_model()
    patient = fetch_latest_patient()
    if not patient: return

    X = preprocess_patient(patient)
    prob = model.predict(X)[0][0]
    pred = 1 if prob > 0.5 else 0
    confidence = prob if pred == 1 else (1 - prob)
    risk = "High Risk" if pred else "Low Risk"

    print(f"\n📌 Patient ID: {patient['id']} - {risk} ({confidence:.2%})")

    try:
        mongo = MongoClient(MONGO_URL)
        mongo["heart_disease_predictor"]["predictions"].insert_one({
            "patient_id": patient["id"],
            "prediction": pred,
            "probability": float(prob),
            "confidence": float(confidence),
            "risk_level": risk,
            "timestamp": datetime.now(),
            "patient_data": patient,
            "model_type": "keras_neural_network"
        })
        print("✅ Stored prediction in MongoDB")
    except Exception as e:
        print(f"⚠️ Failed to store prediction: {e}")

if __name__ == "__main__":
    # Load and insert data
    df = pd.read_csv("data/heart.csv")
    clear_existing_data()
    cleaned = preprocess_csv(df)
    insert_to_mysql(cleaned)

    # Predict latest
    predict_latest()

