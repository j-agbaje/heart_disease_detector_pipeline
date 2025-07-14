# Heart Disease Predictor_pipeline

## Prerequisites

- Python 3.6 or higher
- MySQL Server installed & running (locally or remote)
- MongoDB Atlas account (for cloud MongoDB) or local MongoDB server
- Virtual environment tool (`venv` recommended)

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/j-agbaje/heart_disease_detector_pipeline.git
cd heart-disease-predictor
```
### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate      # For Linux/macOS
# venv\Scripts\activate       # For Windows
```
### 3.Install Python dependencies
```bash
pip install -r requirements.txt
```
### 4. Set up MySQL database
- Create a MySQL database named heart_disease_predictor
- Run the SQL scripts to create schema and stored procedures:
```
mysql -u <username> -p heart_disease_predictor < database/sql/schema.sql
mysql -u <username> -p heart_disease_predictor < database/sql/procedures.sql
```
### 5. Set up MongoDB
- Create a free cluster on MongoDB Atlas
- Create a database user and whitelist your IP address
- Update .env file with your MongoDB connection string:
```bash
MONGO_URL=mongodb+srv://<username>:<password>@cluster0.mongodb.net/heart_disease_predictor?retryWrites=true&w=majority
```
### 6. Load dataset into both databases
- Load data into MySQL:
```bash
python scripts/load_data.py
```
- Migrate MySQL data into MongoDB:
```bash
python scripts/migrate_to_mongo.py
```
### 7. Run the FastAPI backend
```
uvicorn api.main:app --reload
```
API will be accessible at:[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Swagger docs:[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

ReDoc docs [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
