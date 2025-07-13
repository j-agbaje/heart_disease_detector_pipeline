from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import sys
import os

# MySQL Configuration
MYSQL_URL = "mysql+pymysql://heartuser:1234@localhost/heart_disease_predictor"
engine = create_engine(MYSQL_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MongoDB Configuration
MONGO_URL = "mongodb://localhost:27017/"
mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client["heart_disease_predictor"]

def get_mysql_db():
    """Get MySQL database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_mongo_db():
    """Get MongoDB database"""
    return mongo_db

def test_connections():
    """Test both database connections"""
    try:
        # Test MySQL
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ MySQL connection successful")
        
        # Test MongoDB
        mongo_db.command('ping')
        print("✅ MongoDB connection successful")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
