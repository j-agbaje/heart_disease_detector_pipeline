from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime
import numpy as np
from pydantic import BaseModel

# Import your existing models and database functions
from api.models import PatientCreate, PatientUpdate
from api.database import get_mysql_db, get_mongo_db, test_connections

import os
import pickle

# Load ML model
model_path = os.path.join("models", "heart_disease_model.h5.pkl")
with open(model_path, "rb") as f:
    model = pickle.load(f)

app = FastAPI(title="Heart Disease Predictor API", version="1.0.0")

# Updated Patient response model
class Patient(BaseModel):
    id: int
    age: int
    sex: str
    dataset: str
    cp: str
    trestbps: int
    chol: int
    fbs: str
    restecg: str
    thalch: int
    exang: str
    oldpeak: float
    slope: str
    ca: int
    thal: str
    num: int
    created_at: datetime
    prediction: Optional[int] = None
    health_status: Optional[str] = None

    class Config:
        from_attributes = True

@app.on_event("startup")
async def startup_event():
    """Test database connections on startup"""
    if not test_connections():
        raise Exception("Failed to connect to databases")

@app.get("/")
async def root():
    return {"message": "Heart Disease Predictor API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

# -------------------
# MySQL CRUD Endpoints
# -------------------

@app.post("/patients/", response_model=Patient)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_mysql_db)):
    try:
        query = text("""
            CALL InsertPatient(
                :patient_id, :age, :sex, :dataset, :cp, :trestbps, :chol, :fbs, 
                :restecg, :thalch, :exang, :oldpeak, :slope, :ca, :thal, :num
            )
        """)

        db.execute(query, {
            "patient_id": None,  # for auto_increment
            "age": patient.age,
            "sex": patient.sex,
            "dataset": patient.dataset,
            "cp": patient.cp,
            "trestbps": patient.trestbps,
            "chol": patient.chol,
            "fbs": patient.fbs,
            "restecg": patient.restecg,
            "thalch": patient.thalch,
            "exang": patient.exang,
            "oldpeak": patient.oldpeak,
            "slope": patient.slope,
            "ca": patient.ca,
            "thal": patient.thal,
            "num": patient.num
        })
        db.commit()

        last_id_result = db.execute(text("SELECT LAST_INSERT_ID()"))
        patient_id = last_id_result.scalar()

        if patient_id is None:
            raise HTTPException(status_code=400, detail="Could not retrieve inserted patient ID")

        return await get_patient(patient_id, db)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating patient: {str(e)}")

@app.get("/patients/", response_model=List[Patient])
async def get_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_mysql_db)):
    try:
        result = db.execute(
            text("SELECT * FROM patients LIMIT :limit OFFSET :skip"),
            {"limit": limit, "skip": skip}
        )
        patients = result.fetchall()
        
        return [await format_patient_response(p, db) for p in patients]
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching patients: {str(e)}")

@app.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: int, db: Session = Depends(get_mysql_db)):
    try:
        result = db.execute(
            text("SELECT * FROM patients WHERE patient_id = :patient_id"),
            {"patient_id": patient_id}
        )
        patient = result.fetchone()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
            
        return await format_patient_response(patient, db)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching patient: {str(e)}")

async def format_patient_response(patient, db):
    """Helper function to format patient response with prediction"""
    # Prepare features for prediction
    features = [
        patient.patient_age,
        1 if patient.gender.lower() == "male" else 0,
        ["typical angina", "atypical angina", "non-anginal", "asymptomatic"].index(patient.chest_pain_type),
        patient.resting_blood_pressure,
        patient.cholesterol_level,
        1 if str(patient.fasting_blood_sugar).upper() == "TRUE" else 0,
        ["normal", "st-t abnormality", "lv hypertrophy"].index(patient.resting_ecg_results),
        patient.max_heart_rate,
        1 if str(patient.exercise_induced_angina).upper() == "TRUE" else 0,
        patient.st_depression,
        ["upsloping", "flat", "downsloping"].index(patient.exercise_peak_slope),
        patient.major_vessels_count,
        ["normal", "fixed defect", "reversable defect"].index(patient.thalassemia_type),
    ]

    # Get prediction
    input_data = np.array([features])
    prediction = int(model.predict(input_data)[0])
    health_status = "Healthy ✅" if prediction == 0 else "At Risk (Heart Disease) ⚠️"

    return Patient(
        id=patient.patient_id,
        age=patient.patient_age,
        sex=patient.gender,
        dataset=patient.data_source,
        cp=patient.chest_pain_type,
        trestbps=patient.resting_blood_pressure,
        chol=patient.cholesterol_level,
        fbs=patient.fasting_blood_sugar,
        restecg=patient.resting_ecg_results,
        thalch=patient.max_heart_rate,
        exang=patient.exercise_induced_angina,
        oldpeak=patient.st_depression,
        slope=patient.exercise_peak_slope,
        ca=patient.major_vessels_count,
        thal=patient.thalassemia_type,
        num=patient.heart_disease_diagnosis,
        created_at=patient.record_created_at,
        prediction=prediction,
        health_status=health_status
    )

@app.put("/patients/{patient_id}", response_model=Patient)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_mysql_db),
):
    existing = db.execute(
        text("SELECT * FROM patients WHERE patient_id = :patient_id"),
        {"patient_id": patient_id},
    ).fetchone()

    if not existing:
        raise HTTPException(status_code=404, detail="Patient not found")

    field_mapping = {
        "age": "patient_age",
        "sex": "gender",
        "dataset": "data_source",
        "cp": "chest_pain_type",
        "trestbps": "resting_blood_pressure",
        "chol": "cholesterol_level",
        "fbs": "fasting_blood_sugar",
        "restecg": "resting_ecg_results",
        "thalch": "max_heart_rate",
        "exang": "exercise_induced_angina",
        "oldpeak": "st_depression",
        "slope": "exercise_peak_slope",
        "ca": "major_vessels_count",
        "thal": "thalassemia_type",
        "num": "heart_disease_diagnosis",
    }

    update_fields = []
    update_values = {"patient_id": patient_id}

    for api_field, value in patient_update.dict(exclude_unset=True).items():
        if api_field in field_mapping:
            db_col = field_mapping[api_field]
            update_fields.append(f"{db_col} = :{api_field}")
            update_values[api_field] = value

    if not update_fields:
        return await get_patient(patient_id, db)

    query = text(
        f"UPDATE patients SET {', '.join(update_fields)} "
        "WHERE patient_id = :patient_id"
    )
    try:
        db.execute(query, update_values)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating patient: {e}")

    return await get_patient(patient_id, db)

@app.delete("/patients/{patient_id}")
async def delete_patient(patient_id: int, db: Session = Depends(get_mysql_db)):
    try:
        existing = db.execute(
            text("SELECT * FROM patients WHERE patient_id = :patient_id"),
            {"patient_id": patient_id}
        ).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Delete dependent logs first (MySQL foreign keys)
        db.execute(
            text("DELETE FROM patient_logs WHERE patient_id = :patient_id"),
            {"patient_id": patient_id}
        )

        db.execute(
            text("DELETE FROM patients WHERE patient_id = :patient_id"),
            {"patient_id": patient_id}
        )
        db.commit()

        return {"message": f"Patient {patient_id} and related logs deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting patient: {str(e)}")

@app.get("/patients/latest/data")
async def get_latest_patient_data(db: Session = Depends(get_mysql_db)):
    try:
        result = db.execute(
            text("SELECT * FROM patients ORDER BY record_created_at DESC LIMIT 1")
        )
        patient = result.fetchone()
        
        if not patient:
            raise HTTPException(status_code=404, detail="No patients found")
            
        return await format_patient_response(patient, db)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching latest patient: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
