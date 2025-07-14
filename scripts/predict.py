#!/usr/bin/env python3
"""
Script to fetch latest patient data and make predictions using Keras model
"""

import requests
import numpy as np
import pandas as pd
from datetime import datetime
import sys
import os
from pymongo import MongoClient
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pickle

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE_URL = "http://localhost:8000"
MONGO_URL = "mongodb://localhost:27017/"

def load_keras_model():
    """Load the trained Keras model"""
    try:
        model = tf.keras.models.load_model('models/heart_disease_model.h5')
        print("✅ Keras model loaded successfully")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

def fetch_latest_patient():
    """Fetch the latest patient data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/patients/latest/data")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error fetching patient data: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the FastAPI server is running.")
        return None

def preprocess_patient_data(patient_data):
    """Preprocess patient data for Keras model prediction"""
    try:
        # Create a DataFrame with the patient data
        df = pd.DataFrame([patient_data])
        
        # Encode categorical variables
        # Sex: Male=1, Female=0
        df['sex_encoded'] = df['sex'].map({'Male': 1, 'Female': 0})
        
        # Chest pain type encoding
        cp_mapping = {
            'typical angina': 0,
            'atypical angina': 1, 
            'non-anginal': 2,
            'asymptomatic': 3
        }
        df['cp_encoded'] = df['cp'].map(cp_mapping)
        
        # FBS: boolean to int
        df['fbs_encoded'] = df['fbs'].astype(int)
        
        # Rest ECG encoding
        restecg_mapping = {
            'normal': 0,
            'st-t abnormality': 1,
            'lv hypertrophy': 2
        }
        df['restecg_encoded'] = df['restecg'].map(restecg_mapping)
        
        # Exercise induced angina
        df['exang_encoded'] = df['exang'].astype(int)
        
        # Slope encoding
        slope_mapping = {
            'upsloping': 0,
            'flat': 1,
            'downsloping': 2
        }
        df['slope_encoded'] = df['slope'].map(slope_mapping).fillna(1)  # Default to flat
        
        # Thal encoding
        thal_mapping = {
            'normal': 0,
            'fixed defect': 1,
            'reversable defect': 2
        }
        df['thal_encoded'] = df['thal'].map(thal_mapping).fillna(0)  # Default to normal
        
        # Handle missing CA values
        df['ca'] = df['ca'].fillna(0)
        
        # Select features for prediction (adjust based on your model's input)
        features = [
            'age', 'sex_encoded', 'cp_encoded', 'trestbps', 'chol',
            'fbs_encoded', 'restecg_encoded', 'thalch', 'exang_encoded',
            'oldpeak', 'slope_encoded', 'ca', 'thal_encoded'
        ]
        
        # Create feature vector
        X = df[features].values
        
        # Normalize the features (you might need to adjust this based on your training)
        # For now, we'll use simple standardization
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        return X_scaled
        
    except Exception as e:
        print(f"❌ Error preprocessing data: {e}")
        return None

def make_prediction():
    """Main function to fetch data and make prediction"""
    print("🔄 Loading Keras model...")
    model = load_keras_model()
    
    if model is None:
        return
    
    print("🔄 Fetching latest patient data...")
    patient_data = fetch_latest_patient()
    
    if patient_data is None:
        return
    
    print(f"📊 Patient ID: {patient_data['id']}")
    print(f"👤 Age: {patient_data['age']}, Sex: {patient_data['sex']}")
    
    print("🔄 Preprocessing data...")
    X = preprocess_patient_data(patient_data)
    
    if X is None:
        return
    
    # Make prediction
    print("🔄 Making prediction...")
    prediction_prob = model.predict(X)[0][0]
    prediction = 1 if prediction_prob > 0.5 else 0
    
    # Interpret prediction
    risk_level = "High Risk" if prediction == 1 else "Low Risk"
    confidence = prediction_prob if prediction == 1 else (1 - prediction_prob)
    
    print("\n" + "="*50)
    print("🏥 HEART DISEASE PREDICTION RESULTS")
    print("="*50)
    print(f"Patient ID: {patient_data['id']}")
    print(f"Prediction: {risk_level}")
    print(f"Probability: {prediction_prob:.4f}")
    print(f"Confidence: {confidence:.2%}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    # Store prediction in MongoDB
    try:
        mongo_client = MongoClient(MONGO_URL)
        mongo_db = mongo_client["heart_disease_predictor"]
        
        prediction_doc = {
            "patient_id": patient_data['id'],
            "prediction": int(prediction),
            "probability": float(prediction_prob),
            "confidence": float(confidence),
            "risk_level": risk_level,
            "timestamp": datetime.now(),
            "patient_data": patient_data,
            "model_type": "keras_neural_network"
        }
        
        result = mongo_db.predictions.insert_one(prediction_doc)
        print(f"✅ Prediction stored in MongoDB with ID: {result.inserted_id}")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not store prediction in MongoDB: {e}")
    
    return {
        "patient_id": patient_data['id'],
        "prediction": int(prediction),
        "probability": float(prediction_prob),
        "risk_level": risk_level
    }

if __name__ == "__main__":
    make_prediction()
