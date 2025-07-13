-- database/sql/procedures.sql
USE heart_disease_predictor;

DELIMITER //

CREATE PROCEDURE InsertPatient (
    IN p_patient_id INT,
    IN p_patient_age INT,
    IN p_gender ENUM('Male', 'Female'),
    IN p_data_source VARCHAR(20),
    IN p_chest_pain_type VARCHAR(50),
    IN p_resting_blood_pressure INT,
    IN p_cholesterol_level INT,
    IN p_fasting_blood_sugar ENUM('TRUE', 'FALSE'),
    IN p_resting_ecg_results VARCHAR(50),
    IN p_max_heart_rate INT,
    IN p_exercise_induced_angina ENUM('TRUE', 'FALSE'),
    IN p_st_depression FLOAT,
    IN p_exercise_peak_slope VARCHAR(50),
    IN p_major_vessels_count INT,
    IN p_thalassemia_type VARCHAR(50),
    IN p_heart_disease_diagnosis INT
)
BEGIN
    IF p_patient_age IS NULL OR p_patient_age <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Age must be positive';
    END IF;
    
    IF p_patient_age > 120 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Age seems unrealistic (>120)';
    END IF;

    IF p_resting_blood_pressure IS NOT NULL AND p_resting_blood_pressure <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Resting blood pressure must be positive';
    END IF;

    IF p_cholesterol_level IS NOT NULL AND p_cholesterol_level <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cholesterol level must be positive';
    END IF;

    IF p_max_heart_rate IS NOT NULL AND (p_max_heart_rate <= 0 OR p_max_heart_rate > 250) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Max heart rate must be between 1 and 250';
    END IF;

    INSERT INTO patients (
        patient_id, patient_age, gender, data_source, chest_pain_type, 
        resting_blood_pressure, cholesterol_level, fasting_blood_sugar,
        resting_ecg_results, max_heart_rate, exercise_induced_angina, 
        st_depression, exercise_peak_slope, major_vessels_count, 
        thalassemia_type, heart_disease_diagnosis
    ) VALUES (
        p_patient_id, p_patient_age, p_gender, p_data_source, p_chest_pain_type, 
        p_resting_blood_pressure, p_cholesterol_level, p_fasting_blood_sugar,
        p_resting_ecg_results, p_max_heart_rate, p_exercise_induced_angina, 
        p_st_depression, p_exercise_peak_slope, p_major_vessels_count, 
        p_thalassemia_type, p_heart_disease_diagnosis
    );
END //

CREATE TRIGGER after_patient_insert
AFTER INSERT ON patients
FOR EACH ROW
BEGIN
  INSERT INTO patient_logs (patient_id, action_type)
  VALUES (NEW.patient_id, 'INSERT');
END //

DELIMITER ;
