#!/usr/bin/env python3
"""
Script to load heart disease data from CSV into MySQL database
"""

import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os
import numpy as np

# Add parent directory to path to import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import engine, SessionLocal

def clean_data_for_db(row):
    """Clean and validate data before database insertion"""
    cleaned_row = {}
    
    # Handle patient_id
    cleaned_row['patient_id'] = int(row['patient_id'])
    
    # Handle age - check for NaN
    if pd.isna(row['age']) or str(row['age']).lower() == 'nan':
        cleaned_row['age'] = 50  # Default age
    else:
        cleaned_row['age'] = int(float(row['age']))
    
    # Handle sex
    cleaned_row['sex'] = str(row['sex'])
    
    # Handle dataset
    cleaned_row['dataset'] = str(row['dataset'])
    
    # Handle chest pain type
    cleaned_row['cp'] = str(row['cp'])
    
    # Handle resting blood pressure - check for NaN
    if pd.isna(row['trestbps']) or str(row['trestbps']).lower() == 'nan':
        cleaned_row['trestbps'] = 120  # Default BP
    else:
        cleaned_row['trestbps'] = int(float(row['trestbps']))
    
    # Handle cholesterol - check for NaN
    if pd.isna(row['chol']) or str(row['chol']).lower() == 'nan':
        cleaned_row['chol'] = 200  # Default cholesterol
    else:
        cleaned_row['chol'] = int(float(row['chol']))
    
    # Handle fasting blood sugar (convert to string for ENUM)
    if pd.isna(row['fbs']) or str(row['fbs']).lower() == 'nan':
        cleaned_row['fbs'] = 'FALSE'
    else:
        cleaned_row['fbs'] = 'TRUE' if str(row['fbs']).upper() == 'TRUE' or row['fbs'] == True or row['fbs'] == 1 else 'FALSE'
    
    # Handle resting ECG results - CRITICAL FIX
    if pd.isna(row['restecg']) or str(row['restecg']).lower() == 'nan':
        cleaned_row['restecg'] = 'normal'  # Default to normal
    else:
        cleaned_row['restecg'] = str(row['restecg'])
    
    # Handle max heart rate - check for NaN
    if pd.isna(row['thalch']) or str(row['thalch']).lower() == 'nan':
        cleaned_row['thalch'] = 150  # Default max heart rate
    else:
        cleaned_row['thalch'] = int(float(row['thalch']))
    
    # Handle exercise induced angina
    if pd.isna(row['exang']) or str(row['exang']).lower() == 'nan':
        cleaned_row['exang'] = 'FALSE'
    else:
        cleaned_row['exang'] = 'TRUE' if str(row['exang']).upper() == 'TRUE' or row['exang'] == True or row['exang'] == 1 else 'FALSE'
    
    # Handle ST depression (oldpeak) - CRITICAL FIX
    if pd.isna(row['oldpeak']) or str(row['oldpeak']).lower() == 'nan':
        cleaned_row['oldpeak'] = 0.0  # Default to 0.0
    else:
        cleaned_row['oldpeak'] = float(row['oldpeak'])
    
    # Handle slope
    if pd.isna(row['slope']) or str(row['slope']).lower() == 'nan':
        cleaned_row['slope'] = 'flat'  # Default to flat
    else:
        cleaned_row['slope'] = str(row['slope'])
    
    # Handle major vessels count (ca) - CRITICAL FIX
    if pd.isna(row['ca']) or str(row['ca']).lower() == 'nan':
        cleaned_row['ca'] = 0  # Default to 0
    else:
        try:
            cleaned_row['ca'] = int(float(row['ca']))  # Convert to float first, then int
        except (ValueError, TypeError):
            cleaned_row['ca'] = 0  # Default if conversion fails
    
    # Handle thalassemia type
    if pd.isna(row['thal']) or str(row['thal']).lower() == 'nan':
        cleaned_row['thal'] = 'normal'  # Default to normal
    else:
        cleaned_row['thal'] = str(row['thal'])
    
    # Handle heart disease diagnosis - check for NaN
    if pd.isna(row['num']) or str(row['num']).lower() == 'nan':
        cleaned_row['num'] = 0  # Default to no disease
    else:
        cleaned_row['num'] = int(float(row['num']))
    
    return cleaned_row

def clear_existing_data():
    """Clear existing data from patients table"""
    try:
        db = SessionLocal()
        db.execute(text("DELETE FROM patients"))
        db.commit()
        db.close()
        print("✅ Cleared existing data from patients table")
    except Exception as e:
        print(f"⚠️  Error clearing existing data: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()

def load_heart_data():
    """Load heart disease data from CSV into MySQL database"""
    try:
        # Clear existing data first to avoid duplicate key errors
        clear_existing_data()
        
        # Read the CSV file
        df = pd.read_csv('data/heart.csv')
        print(f"Loaded {len(df)} records from CSV")
        
        # Create database session
        db = SessionLocal()
        
        # Insert data row by row
        inserted_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Clean the data
                cleaned_data = clean_data_for_db({
                    'patient_id': index + 1,  # Use row index + 1 as patient_id
                    'age': row['age'],
                    'sex': row['sex'],
                    'dataset': row['dataset'],
                    'cp': row['cp'],
                    'trestbps': row['trestbps'],
                    'chol': row['chol'],
                    'fbs': row['fbs'],
                    'restecg': row['restecg'],
                    'thalch': row['thalch'],
                    'exang': row['exang'],
                    'oldpeak': row['oldpeak'],
                    'slope': row['slope'],
                    'ca': row['ca'],
                    'thal': row['thal'],
                    'num': row['num']
                })
                
                # Updated query with correct column names including patient_id
                query = text("""
                    INSERT INTO patients (
                        patient_id, patient_age, gender, data_source, chest_pain_type, 
                        resting_blood_pressure, cholesterol_level, fasting_blood_sugar, 
                        resting_ecg_results, max_heart_rate, exercise_induced_angina, 
                        st_depression, exercise_peak_slope, major_vessels_count, 
                        thalassemia_type, heart_disease_diagnosis
                    ) VALUES (
                        :patient_id, :age, :sex, :dataset, :cp, :trestbps, :chol, :fbs, 
                        :restecg, :thalch, :exang, :oldpeak, :slope, :ca, :thal, :num
                    )
                """)
                
                db.execute(query, cleaned_data)
                inserted_count += 1
                
                if inserted_count % 100 == 0:
                    print(f"Inserted {inserted_count} records...")
                    
            except Exception as e:
                error_count += 1
                print(f"Error inserting row {index + 1}: {e}")
                print(f"Problematic data: {row.to_dict()}")
                continue
        
        db.commit()
        db.close()
        
        print(f"✅ Successfully inserted {inserted_count} records into MySQL database")
        if error_count > 0:
            print(f"⚠️  {error_count} records failed to insert")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()

if __name__ == "__main__":
    load_heart_data()
