from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Pydantic models for request/response validation

class PatientBase(BaseModel):
    age: int
    sex: str
    dataset: Optional[str]
    cp: Optional[str]
    trestbps: Optional[int]
    chol: Optional[int]
    fbs: Optional[str]
    restecg: Optional[str]
    thalch: Optional[int]
    exang: Optional[str]
    oldpeak: Optional[float]
    slope: Optional[str]
    ca: Optional[int]
    thal: Optional[str]
    num: Optional[int]

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    age: Optional[int]
    sex: Optional[str]
    dataset: Optional[str]
    cp: Optional[str]
    trestbps: Optional[int]
    chol: Optional[int]
    fbs: Optional[str]
    restecg: Optional[str]
    thalch: Optional[int]
    exang: Optional[str]
    oldpeak: Optional[float]
    slope: Optional[str]
    ca: Optional[int]
    thal: Optional[str]
    num: Optional[int]

class Patient(PatientBase):
    id: int
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

# If you have PredictionRequest and PredictionResponse, define them similarly
class PredictionRequest(BaseModel):
    # define the input features for prediction here
    pass

class PredictionResponse(BaseModel):
    # define prediction result fields here
    pass
