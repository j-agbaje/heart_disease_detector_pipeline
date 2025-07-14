#!/usr/bin/env python3
"""
Load heart‑disease CSV into the `patients` table (MySQL)

Prerequisites
-------------
1. In MySQL, make `patient_id` AUTO_INCREMENT once:

   ALTER TABLE patients
     MODIFY patient_id INT NOT NULL AUTO_INCREMENT;

2. CSV file located at data/heart.csv
"""

import os
import sys
import pandas as pd
import math
from sqlalchemy import text

# Fix module path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

from api.database import SessionLocal  # This should now work


CSV_PATH = "data/heart.csv"
CHUNK_SIZE = 1000        # rows per commit

def as_enum(val, true_string="TRUE"):
    """Convert various truthy values to the ENUM strings used in MySQL."""
    return "TRUE" if str(val).upper() in {"1", "TRUE", "T", "YES"} else "FALSE"

def nan_to_none(v):
    """Return None if v is NaN; otherwise return v unchanged."""
    return None if (isinstance(v, float) and math.isnan(v)) else v

def load_heart_data():
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df):,} rows from {CSV_PATH}")

    # Pre-clean frame once so we touch each cell only a single time
    df = df.applymap(nan_to_none)

    # Replace ENUM-like columns
    df["fbs"]   = df["fbs"].apply(as_enum)
    df["exang"] = df["exang"].apply(as_enum)

    inserted = 0
    session  = SessionLocal()

    try:
        insert_stmt = text("""
            INSERT INTO patients (
                patient_age, gender, data_source, chest_pain_type,
                resting_blood_pressure, cholesterol_level, fasting_blood_sugar,
                resting_ecg_results, max_heart_rate, exercise_induced_angina,
                st_depression, exercise_peak_slope, major_vessels_count,
                thalassemia_type, heart_disease_diagnosis
            ) VALUES (
                :age, :sex, :dataset, :cp,
                :trestbps, :chol, :fbs,
                :restecg, :thalch, :exang,
                :oldpeak, :slope, :ca,
                :thal, :num
            )
        """)

        for start in range(0, len(df), CHUNK_SIZE):
            chunk = df.iloc[start : start + CHUNK_SIZE]

            # Build a list of dictionaries ready for executemany()
            bind_params = [
                {
                    "age":       int(row.age),
                    "sex":       str(row.sex),
                    "dataset":   str(row.dataset),
                    "cp":        str(row.cp),
                    "trestbps":  nan_to_none(row.trestbps),
                    "chol":      nan_to_none(row.chol),
                    "fbs":       row.fbs,        # already TRUE/FALSE
                    # Handle restecg: replace None/NaN with 'normal'
                    "restecg":   str(row.restecg) if row.restecg and not pd.isna(row.restecg) else "normal",
                    "thalch":    nan_to_none(row.thalch),
                    "exang":     row.exang,      # already TRUE/FALSE
                    "oldpeak":   nan_to_none(row.oldpeak),
                    "slope":     str(row.slope) if row.slope else "flat",
                    "ca":        nan_to_none(row.ca),
                    "thal":      str(row.thal) if row.thal else "normal",
                    "num":       nan_to_none(row.num),
                }
                for row in chunk.itertuples(index=False)
            ]

            session.execute(insert_stmt, bind_params)
            session.commit()
            inserted += len(bind_params)
            print(f"✅  Inserted {inserted:,} / {len(df):,} rows")

        print(f"\n🎉 Finished! {inserted:,} total rows inserted.")
    except Exception as e:
        session.rollback()
        print("❌  Aborted – rolled back last chunk.\nReason:", e)
    finally:
        session.close()

if __name__ == "__main__":
    load_heart_data()
