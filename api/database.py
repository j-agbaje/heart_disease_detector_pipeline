"""
api/database.py
Unified DB connector for MySQL (SQLAlchemy) + MongoDB (Atlas or local)

Add a .env file in your project root with e.g.:

MYSQL_URL=mysql+pymysql://heartuser:1234@localhost/heart_disease_predictor
MONGO_URI=mongodb+srv://backend_user:HeartGroup2025!@cluster0.ryllb1l.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGO_DB_NAME=heart_disease_db     # optional (defaults to 'heart_disease_db')
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from dotenv import load_dotenv

# ------------------------------------------------------------------
# 1. Load environment variables
# ------------------------------------------------------------------
load_dotenv()

# ------------------------------------------------------------------
# 2. MySQL (SQLAlchemy) setup
# ------------------------------------------------------------------
DEFAULT_MYSQL_URL = "mysql+pymysql://heartuser:1234@localhost/heart_disease_predictor"
MYSQL_URL = os.getenv("MYSQL_URL", DEFAULT_MYSQL_URL)

engine = create_engine(MYSQL_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ------------------------------------------------------------------
# 3. MongoDB (Atlas or local) setup
# ------------------------------------------------------------------
DEFAULT_MONGO_URI = "mongodb://localhost:27017/"
MONGO_URI = os.getenv("MONGO_URI", DEFAULT_MONGO_URI)
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "heart_disease_db")

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB_NAME]

# ------------------------------------------------------------------
# 4. Dependency helpers
# ------------------------------------------------------------------
def get_mysql_db():
    """Yield a SQLAlchemy session (used with Depends)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_mongo_db():
    """Return the MongoDB database handle"""
    return mongo_db

# ------------------------------------------------------------------
# 5. Quick connectivity check (called on startup)
# ------------------------------------------------------------------
def test_connections() -> bool:
    """Ping both databases; return True if both succeed."""
    try:
        # MySQL ping
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ MySQL connection successful")

        # Mongo ping
        mongo_db.command("ping")
        print("✅ MongoDB connection successful")

        return True
    except Exception as exc:
        print(f"❌ Database connection failed: {exc}")
        return False
