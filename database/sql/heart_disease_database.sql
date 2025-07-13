DROP DATABASE IF EXISTS `heart_disease_predictor`;
CREATE DATABASE `heart_disease_predictor`;
USE `heart_disease_predictor`;




CREATE TABLE `cp` (
    `description` VARCHAR(50)  NOT NULL ,
    PRIMARY KEY (
        `description`
    )
);

INSERT INTO cp VALUES
 ('typical angina'),('atypical angina'),('non-anginal'),('asymptomatic');

CREATE TABLE `restecg` (
    `description` VARCHAR(50)  NOT NULL ,
    PRIMARY KEY (
        `description`
    )
);

INSERT INTO restecg VALUES
 ('normal'),('lv hypertrophy'),('st-t abnormality');


CREATE TABLE `slope` (
    `description` VARCHAR(50)  NOT NULL ,
    PRIMARY KEY (
        `description`
    )
);

INSERT INTO slope VALUES
 ('upsloping'),('flat'),('downsloping');

CREATE TABLE `dataset` (
    `name` VARCHAR(20)  NOT NULL ,
    PRIMARY KEY (
        `name`
    )
);

INSERT INTO dataset VALUES
 ('Cleveland'),('Hungary'),('Switzerland'),('VA Long Beach');

CREATE TABLE `thal` (
    `description` VARCHAR(50)  NOT NULL ,
    PRIMARY KEY (
        `description`
    )
);

INSERT INTO thal VALUES
 ('normal'),('fixed defect'),('reversable defect');
 
 
 -- Trigger + audit log
CREATE TABLE patient_logs (
  log_id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT,
  action_type VARCHAR(20) NOT NULL,
  logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


 
 CREATE TABLE `patients` (
    `patient_id` INT  NOT NULL ,
    `patient_age` INT  NULL ,
    `gender` ENUM('Male', 'Female')  NULL ,
    `data_source` VARCHAR(50)   NULL ,
    `chest_pain_type` VARCHAR(50)  NULL ,
    `resting_blood_pressure` INT NULL ,
    `cholesterol_level` INT NULL ,
    `fasting_blood_sugar` ENUM('TRUE', 'FALSE') NULL ,
    `resting_ecg_results` VARCHAR(50) NULL ,
    `max_heart_rate` INT NULL ,
    `exercise_induced_angina` ENUM('TRUE', 'FALSE') NULL ,
    `st_depression` FLOAT NULL ,
    `exercise_peak_slope` VARCHAR(50) NULL ,
    `major_vessels_count` INT  NULL ,
    `thalassemia_type` VARCHAR(50) NULL ,
    `heart_disease_diagnosis` INT  NULL ,
    
    record_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    PRIMARY KEY (
        `patient_id`
    )
);

ALTER TABLE `patient_logs` ADD CONSTRAINT `fk_patient_logs_patient_id` FOREIGN KEY(`patient_id`)
REFERENCES `patients` (`patient_id`);

ALTER TABLE `patients` ADD CONSTRAINT `fk_patients_dataset` FOREIGN KEY(`data_source`)
REFERENCES `dataset` (`name`);

ALTER TABLE `patients` ADD CONSTRAINT `fk_patients_cp` FOREIGN KEY(`chest_pain_type`)
REFERENCES `cp` (`description`);

ALTER TABLE `patients` ADD CONSTRAINT `fk_patients_restecg` FOREIGN KEY(`resting_ecg_results`)
REFERENCES `restecg` (`description`);

ALTER TABLE `patients` ADD CONSTRAINT `fk_patients_slope` FOREIGN KEY(`exercise_peak_slope`)
REFERENCES `slope` (`description`);

ALTER TABLE `patients` ADD CONSTRAINT `fk_patients_thal` FOREIGN KEY(`thalassemia_type`)
REFERENCES `thal` (`description`);


-- Stored Procedure for inserting data (with validation)
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
    
    -- IF p_major_vessels_count IS NOT NULL AND (p_major_vessels_count < 0 OR p_major_vessels_count > 3) THEN
--         SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Major vessels count must be between 0 and 3';
--     END IF;
    
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
        patient_id, patient_age, gender, data_source, chest_pain_type, resting_blood_pressure, cholesterol_level, fasting_blood_sugar,
        resting_ecg_results, max_heart_rate, exercise_induced_angina, st_depression, exercise_peak_slope, major_vessels_count, thalassemia_type, heart_disease_diagnosis
    ) VALUES (
        p_patient_id, p_patient_age, p_gender, p_data_source, p_chest_pain_type, p_resting_blood_pressure, p_cholesterol_level, p_fasting_blood_sugar,
        p_resting_ecg_results, p_max_heart_rate, p_exercise_induced_angina, p_st_depression, p_exercise_peak_slope, p_major_vessels_count, p_thalassemia_type, p_heart_disease_diagnosis
    );
END //
DELIMITER ;


DELIMITER //
CREATE TRIGGER after_patient_insert
AFTER INSERT ON patients
FOR EACH ROW
BEGIN
  INSERT INTO patient_logs (patient_id, action_type)
  VALUES (NEW.patient_id, 'INSERT');
END //
DELIMITER ;

LOAD DATA LOCAL INFILE '/Users/jeremiah/Desktop/heart.csv'
INTO TABLE patients
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@csv_col1, @csv_col2, @csv_col3, @csv_col4, @csv_col5, @csv_col6, @csv_col7, @csv_col8, @csv_col9, @csv_col10, @csv_col11, @csv_col12, @csv_col13, @csv_col14, @csv_col15, @csv_col16)
SET
    patient_id = NULLIF(@csv_col1, ''),
    patient_age = NULLIF(@csv_col2, ''),
    gender = NULLIF(@csv_col3, ''),
    data_source = NULLIF(@csv_col4, ''),
    chest_pain_type = NULLIF(@csv_col5, ''),
    resting_blood_pressure = NULLIF(@csv_col6, ''),
    cholesterol_level = NULLIF(@csv_col7, ''),
    fasting_blood_sugar = NULLIF(@csv_col8, ''),
    resting_ecg_results = NULLIF(@csv_col9, ''),
    max_heart_rate = NULLIF(@csv_col10, ''),
    exercise_induced_angina = NULLIF(@csv_col11, ''),
    st_depression = NULLIF(@csv_col12, ''),
    exercise_peak_slope = NULLIF(@csv_col13, ''),
    major_vessels_count = NULLIF(@csv_col14, ''),
    thalassemia_type = NULLIF(@csv_col15, ''),
    heart_disease_diagnosis = NULLIF(@csv_col16, '');




-- 2. Check if data is in table
-- SELECT * FROM patients



