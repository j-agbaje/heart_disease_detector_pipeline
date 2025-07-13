-- database/sql/schema.sql
DROP DATABASE IF EXISTS `heart_disease_predictor`;
CREATE DATABASE `heart_disease_predictor`;
USE `heart_disease_predictor`;

-- Create reference tables
CREATE TABLE `cp` (
    `description` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`description`)
);

CREATE TABLE `restecg` (
    `description` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`description`)
);

CREATE TABLE `slope` (
    `description` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`description`)
);

CREATE TABLE `dataset` (
    `name` VARCHAR(20) NOT NULL,
    PRIMARY KEY (`name`)
);

CREATE TABLE `thal` (
    `description` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`description`)
);

-- Insert reference data
INSERT INTO cp VALUES 
('typical angina'),('atypical angina'),('non-anginal'),('asymptomatic');

INSERT INTO restecg VALUES 
('normal'),('lv hypertrophy'),('st-t abnormality');

INSERT INTO slope VALUES 
('upsloping'),('flat'),('downsloping');

INSERT INTO dataset VALUES 
('Cleveland'),('Hungary'),('Switzerland'),('VA Long Beach');

INSERT INTO thal VALUES 
('normal'),('fixed defect'),('reversable defect');

-- Create audit log table
CREATE TABLE patient_logs (
  log_id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT,
  action_type VARCHAR(20) NOT NULL,
  logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create main patients table
CREATE TABLE `patients` (
    `patient_id` INT NOT NULL,
    `patient_age` INT NULL,
    `gender` ENUM('Male', 'Female') NULL,
    `data_source` VARCHAR(50) NULL,
    `chest_pain_type` VARCHAR(50) NULL,
    `resting_blood_pressure` INT NULL,
    `cholesterol_level` INT NULL,
    `fasting_blood_sugar` ENUM('TRUE', 'FALSE') NULL,
    `resting_ecg_results` VARCHAR(50) NULL,
    `max_heart_rate` INT NULL,
    `exercise_induced_angina` ENUM('TRUE', 'FALSE') NULL,
    `st_depression` FLOAT NULL,
    `exercise_peak_slope` VARCHAR(50) NULL,
    `major_vessels_count` INT NULL,
    `thalassemia_type` VARCHAR(50) NULL,
    `heart_disease_diagnosis` INT NULL,
    record_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    record_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`patient_id`)
);

-- Add foreign key constraints
ALTER TABLE `patient_logs` ADD CONSTRAINT `fk_patient_logs_patient_id` 
FOREIGN KEY(`patient_id`) REFERENCES `patients` (`patient_id`);

ALTER TABLE `patients` ADD CONSTRAINT `fk_patients_dataset` 
FOREIGN KEY(`data_source`) REFERENCES `dataset` (`name`);

ALTER TABLE `patients` ADD CONSTRAINT `fk_patients_cp` 
FOREIGN KEY(`chest_pain_type`) REFERENCES `cp` (`description`);

ALTER TABLE `patients` ADD CONSTRAINT `fk_patients_restecg` 
FOREIGN KEY(`resting_ecg_results`) REFERENCES `restecg` (`description`);

ALTER TABLE `patients` ADD CONSTRAINT `fk_patients_slope` 
FOREIGN KEY(`exercise_peak_slope`) REFERENCES `slope` (`description`);

ALTER TABLE `patients` ADD CONSTRAINT `fk_patients_thal` 
FOREIGN KEY(`thalassemia_type`) REFERENCES `thal` (`description`);
