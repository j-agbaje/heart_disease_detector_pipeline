// database/mongo/init_mongo.js
db = db.getSiblingDB('heart_disease_predictor');

// Create collections
db.createCollection('patients');
db.createCollection('reference_data');

// Insert reference data
db.reference_data.insertMany([
  { type: 'chest_pain', values: ['typical angina', 'atypical angina', 'non-anginal', 'asymptomatic'] },
  { type: 'resting_ecg', values: ['normal', 'lv hypertrophy', 'st-t abnormality'] },
  { type: 'slope', values: ['upsloping', 'flat', 'downsloping'] },
  { type: 'dataset', values: ['Cleveland', 'Hungary', 'Switzerland', 'VA Long Beach'] },
  { type: 'thalassemia', values: ['normal', 'fixed defect', 'reversable defect'] }
]);

// Create indexes
db.patients.createIndex({ patient_id: 1 }, { unique: true });
db.patients.createIndex({ data_source: 1 });
db.patients.createIndex({ heart_disease_diagnosis: 1 });

print("MongoDB initialization completed successfully!");
