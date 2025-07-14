from sqlalchemy import create_engine, text
from pymongo import MongoClient

# Update with your MySQL connection details
MYSQL_URL = "mysql+pymysql://heartuser:1234@localhost/heart_disease_predictor"

# Paste your MongoDB Atlas connection string here
MONGO_URI = "mongodb+srv://backend_user:HeartGroup2025!@cluster0.ryllb1l.mongodb.net/heart_disease_predictor?retryWrites=true&w=majority"

def migrate_mysql_to_mongo():
    # Connect MySQL
    engine = create_engine(MYSQL_URL)

    # Connect MongoDB Atlas
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client["heart_disease_predictor"]
    mongo_patients_collection = mongo_db["patients"]

    with engine.connect() as conn:
        # Select all patients
        result = conn.execute(text("SELECT * FROM patients"))
        rows = result.fetchall()

        docs = []
        for row in rows:
            doc = {
                "patient_id": row.patient_id,
                "age": row.patient_age,
                "sex": row.gender,
                "dataset": row.data_source,
                "cp": row.chest_pain_type,
                "trestbps": row.resting_blood_pressure,
                "chol": row.cholesterol_level,
                "fbs": row.fasting_blood_sugar,
                "restecg": row.resting_ecg_results,
                "thalch": row.max_heart_rate,
                "exang": row.exercise_induced_angina,
                "oldpeak": row.st_depression,
                "slope": row.exercise_peak_slope,
                "ca": row.major_vessels_count,
                "thal": row.thalassemia_type,
                "num": row.heart_disease_diagnosis,
                "created_at": row.record_created_at.isoformat() if row.record_created_at else None
            }
            docs.append(doc)

        if docs:
            # Insert all documents into MongoDB collection
            mongo_patients_collection.insert_many(docs)
            print(f"✅ Inserted {len(docs)} patients into MongoDB")
        else:
            print("No data found in MySQL patients table")

if __name__ == "__main__":
    migrate_mysql_to_mongo()
