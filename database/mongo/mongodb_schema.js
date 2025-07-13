// use heart_disease_predictor; - uncomment in the mongodb shell
// Drop only reference collections (safe to recreate)
db.cp.drop();
db.restecg.drop();
db.slope.drop();
db.dataset.drop();
db.thal.drop();
db.patient_logs.drop();


// REFERENCE COLLECTIONS (Keep same)
db.cp.insertMany([
    { description: "typical angina" },
    { description: "atypical angina" },
    { description: "non-anginal" },
    { description: "asymptomatic" }
]);

db.restecg.insertMany([
    { description: "normal" },
    { description: "lv hypertrophy" },
    { description: "st-t abnormality" }
]);

db.slope.insertMany([
    { description: "upsloping" },
    { description: "flat" },
    { description: "downsloping" }
]);

db.dataset.insertMany([
    { name: "Cleveland" },
    { name: "Hungary" },
    { name: "Switzerland" },
    { name: "VA Long Beach" }
]);

db.thal.insertMany([
    { description: "normal" },
    { description: "fixed defect" },
    { description: "reversable defect" }
]);


// UPDATE EXISTING PATIENTS COLLECTION SCHEMA - created before changing schema during implementation

// Modify existing collection schema (preserves data)
db.runCommand({
    collMod: "patients",
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["id"],  
            properties: {
                id: {
                    bsonType: "int",
                    description: "Patient ID is required"
                },
                age: {
                    bsonType: ["int", "null"],
                    minimum: 1,
                    maximum: 120,
                    description: "Age must be between 1 and 120"
                },
                sex: {
                    enum: ["Male", "Female", "null"],
                    description: "Gender must be Male or Female"
                },
                dataset: {
                    bsonType: ["string", "null"],
                    description: "Data source (Cleveland, Hungary, etc.)"
                },
                cp: {
                    bsonType: ["string", "null"],
                    description: "Chest pain type"
                },
                trestbps: {
                    bsonType: ["int", "null"],
                    minimum: 1,
                    description: "Resting blood pressure must be positive"
                },
                chol: {
                    bsonType: ["int", "null"],
                    minimum: 1,
                    description: "Cholesterol level must be positive"
                },
                fbs: {
                    bsonType: ["bool", "null"],
                    description: "Fasting blood sugar > 120 mg/dl"
                },
                restecg: {
                    bsonType: ["string", "null"],
                    description: "Resting ECG results"
                },
                thalch: {
                    bsonType: ["int", "null"],
                    minimum: 1,
                    maximum: 250,
                    description: "Max heart rate must be between 1 and 250"
                },
                exang: {
                    bsonType: ["bool", "null"],
                    description: "Exercise induced angina"
                },
                oldpeak: {
                    bsonType: ["double", "null"],
                    description: "ST depression induced by exercise"
                },
                slope: {
                    bsonType: ["string", "null"],
                    description: "Slope of peak exercise ST segment"
                },
                ca: {
                    bsonType: ["int", "null"],
                    minimum: 0,
                    maximum: 3,
                    description: "Number of major vessels (0-3)"
                },
                thal: {
                    bsonType: ["string", "null"],
                    description: "Thalassemia type"
                },
                num: {
                    bsonType: ["int", "null"],
                    minimum: 0,
                    maximum: 4,
                    description: "Heart disease diagnosis (0=no disease, 1-4=disease)"
                }
            }
        }
    }
});

// Create patient_logs collection
db.createCollection("patient_logs", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["patient_id", "action_type"],
            properties: {
                patient_id: {
                    bsonType: "int",
                    description: "Patient ID is required"
                },
                action_type: {
                    bsonType: "string",
                    description: "Action type is required"
                },
                logged_at: {
                    bsonType: "date",
                    description: "Log timestamp"
                }
            }
        }
    }
});

// INDEXES FOR PERFORMANCE

// Primary key equivalent (will skip if exists)
try {
    db.patients.createIndex({ id: 1 }, { unique: true });
} catch (e) {
    if (e.code !== 85) throw e; // Ignore "index already exists" error
}

// Foreign key equivalent indexes
db.patients.createIndex({ dataset: 1 });
db.patients.createIndex({ cp: 1 });
db.patients.createIndex({ restecg: 1 });
db.patients.createIndex({ slope: 1 });
db.patients.createIndex({ thal: 1 });

// Performance indexes
db.patients.createIndex({ age: 1 });
db.patients.createIndex({ sex: 1 });
db.patients.createIndex({ num: 1 });

// Compound indexes for common queries
db.patients.createIndex({ 
    sex: 1, 
    age: 1, 
    num: 1 
});

// Audit log indexes
db.patient_logs.createIndex({ patient_id: 1 });
db.patient_logs.createIndex({ logged_at: 1 });
db.patient_logs.createIndex({ action_type: 1 });

print("=== MongoDB Heart Disease Database Schema Updated (Data Preserved) ===");