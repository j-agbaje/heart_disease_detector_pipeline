from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from datetime import datetime

from api.models import Patient, PatientCreate, PatientUpdate

from api.database import get_mysql_db, test_connections

app = FastAPI(title="Heart Disease Predictor API", version="1.0.0")

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

# CRUD Operations for Patients

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

        # Get last inserted ID
        last_id_result = db.execute(text("SELECT LAST_INSERT_ID()"))
        patient_id = last_id_result.scalar()

        if patient_id is None:
            raise HTTPException(status_code=400, detail="Could not retrieve inserted patient ID")

        created_patient = db.execute(
            text("SELECT * FROM patients WHERE patient_id = :patient_id"),
            {"patient_id": patient_id}
        ).fetchone()

        if not created_patient:
            raise HTTPException(status_code=404, detail="Inserted patient not found")

        return Patient(
            id=created_patient.patient_id,
            age=created_patient.patient_age,
            sex=created_patient.gender,
            dataset=created_patient.data_source,
            cp=created_patient.chest_pain_type,
            trestbps=created_patient.resting_blood_pressure,
            chol=created_patient.cholesterol_level,
            fbs=created_patient.fasting_blood_sugar,
            restecg=created_patient.resting_ecg_results,
            thalch=created_patient.max_heart_rate,
            exang=created_patient.exercise_induced_angina,
            oldpeak=created_patient.st_depression,
            slope=created_patient.exercise_peak_slope,
            ca=created_patient.major_vessels_count,
            thal=created_patient.thalassemia_type,
            num=created_patient.heart_disease_diagnosis,
            created_at=created_patient.record_created_at
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating patient: {str(e)}")

@app.get("/patients/", response_model=List[Patient])
async def get_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_mysql_db)):
    """Get all patients with pagination"""
    try:
        result = db.execute(
            text("SELECT * FROM patients LIMIT :limit OFFSET :skip"),
            {"limit": limit, "skip": skip}
        )
        patients = result.fetchall()
        
        return [Patient(
            id=p.patient_id,
            age=p.patient_age,
            sex=p.gender,
            dataset=p.data_source,
            cp=p.chest_pain_type,
            trestbps=p.resting_blood_pressure,
            chol=p.cholesterol_level,
            fbs=p.fasting_blood_sugar,
            restecg=p.resting_ecg_results,
            thalch=p.max_heart_rate,
            exang=p.exercise_induced_angina,
            oldpeak=p.st_depression,
            slope=p.exercise_peak_slope,
            ca=p.major_vessels_count,
            thal=p.thalassemia_type,
            num=p.heart_disease_diagnosis,
            created_at=p.record_created_at
        ) for p in patients]
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching patients: {str(e)}")

@app.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: int, db: Session = Depends(get_mysql_db)):
    """Get a specific patient by ID"""
    try:
        result = db.execute(
            text("SELECT * FROM patients WHERE patient_id = :patient_id"),
            {"patient_id": patient_id}
        )
        patient = result.fetchone()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
            
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
            created_at=patient.record_created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching patient: {str(e)}")

@app.put("/patients/{patient_id}", response_model=Patient)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_mysql_db),
):
    """Update a patient record"""

    # 1️⃣  Make sure the patient exists
    existing = db.execute(
        text("SELECT * FROM patients WHERE patient_id = :patient_id"),
        {"patient_id": patient_id},
    ).fetchone()

    if not existing:
        raise HTTPException(status_code=404, detail="Patient not found")

    # 2️⃣  Map API‑field ➜ real DB column
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

    # 3️⃣  Build the SET‑clause only for provided fields
    for api_field, value in patient_update.dict(exclude_unset=True).items():
        if api_field in field_mapping:
            db_col = field_mapping[api_field]
            update_fields.append(f"{db_col} = :{api_field}")
            update_values[api_field] = value

    if not update_fields:
        # nothing to update
        return await get_patient(patient_id, db)

    # 4️⃣  Execute UPDATE
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

    # 5️⃣  Return the fresh record
    return await get_patient(patient_id, db)

@app.delete("/patients/{patient_id}")
async def delete_patient(patient_id: int, db: Session = Depends(get_mysql_db)):
    """Delete a patient record"""
    try:
        existing = db.execute(
            text("SELECT * FROM patients WHERE patient_id = :patient_id"),
            {"patient_id": patient_id}
        ).fetchone()
        
        if not existing:
            raise HTTPException(status_code=404, detail="Patient not found")

        # First delete any dependent records
        db.execute(
            text("DELETE FROM patient_logs WHERE patient_id = :patient_id"),
            {"patient_id": patient_id}
        )

        # Then delete the patient
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
    """Get the latest patient data for prediction"""
    try:
        result = db.execute(
            text("SELECT * FROM patients ORDER BY record_created_at DESC LIMIT 1")
        )
        patient = result.fetchone()
        
        if not patient:
            raise HTTPException(status_code=404, detail="No patients found")
            
        return {
            "id": patient.patient_id,
            "age": patient.patient_age,
            "sex": patient.gender,
            "cp": patient.chest_pain_type,
            "trestbps": patient.resting_blood_pressure,
            "chol": patient.cholesterol_level,
            "fbs": patient.fasting_blood_sugar,
            "restecg": patient.resting_ecg_results,
            "thalch": patient.max_heart_rate,
            "exang": patient.exercise_induced_angina,
            "oldpeak": patient.st_depression,
            "slope": patient.exercise_peak_slope,
            "ca": patient.major_vessels_count,
            "thal": patient.thalassemia_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching latest patient: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    