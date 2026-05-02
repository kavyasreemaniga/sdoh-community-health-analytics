-- ================================================
-- SDOH Community Health Analytics Database Schema
-- Bronze → Silver → Gold Architecture
-- ================================================

-- Drop schemas if they exist (for development)
DROP SCHEMA IF EXISTS bronze CASCADE;
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS marts CASCADE;

-- Create schemas
CREATE SCHEMA bronze;      -- Raw data ingestion
CREATE SCHEMA staging;     -- Cleaned/standardized data
CREATE SCHEMA marts;       -- Analytics-ready tables

-- Set search path
SET search_path TO bronze, staging, marts, public;

-- ================================================
-- BRONZE LAYER - Raw Data Ingestion
-- ================================================

-- Table: bronze.patients (from Synthea)
CREATE TABLE bronze.patients (
    patient_id VARCHAR(100) PRIMARY KEY,
    birth_date DATE,
    death_date DATE,
    ssn VARCHAR(20),
    drivers VARCHAR(20),
    passport VARCHAR(20),
    prefix VARCHAR(10),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    maiden VARCHAR(100),
    marital_status VARCHAR(1),
    race VARCHAR(50),
    ethnicity VARCHAR(50),
    gender VARCHAR(20),
    birthplace VARCHAR(200),
    address VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(2),
    county VARCHAR(100),
    zip VARCHAR(10),
    lat NUMERIC(10, 7),
    lon NUMERIC(10, 7),
    healthcare_expenses NUMERIC(12, 2),
    healthcare_coverage NUMERIC(12, 2),
    income INTEGER,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: bronze.encounters
CREATE TABLE bronze.encounters (
    encounter_id VARCHAR(100) PRIMARY KEY,
    patient_id VARCHAR(100) REFERENCES bronze.patients(patient_id),
    encounter_start TIMESTAMP,
    encounter_stop TIMESTAMP,
    encounter_class VARCHAR(50),
    encounter_code VARCHAR(20),
    encounter_description TEXT,
    base_encounter_cost NUMERIC(10, 2),
    total_claim_cost NUMERIC(10, 2),
    payer_coverage NUMERIC(10, 2),
    reason_code VARCHAR(20),
    reason_description TEXT,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: bronze.conditions
CREATE TABLE bronze.conditions (
    condition_id VARCHAR(100) PRIMARY KEY,
    patient_id VARCHAR(100) REFERENCES bronze.patients(patient_id),
    encounter_id VARCHAR(100),
    condition_start DATE,
    condition_stop DATE,
    condition_code VARCHAR(20),
    condition_description TEXT,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: bronze.observations
CREATE TABLE bronze.observations (
    observation_id VARCHAR(100) PRIMARY KEY,
    patient_id VARCHAR(100) REFERENCES bronze.patients(patient_id),
    encounter_id VARCHAR(100),
    observation_date TIMESTAMP,
    observation_code VARCHAR(20),
    observation_description TEXT,
    observation_value VARCHAR(100),
    observation_units VARCHAR(50),
    observation_type VARCHAR(50),
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: bronze.sdoh_screenings
CREATE TABLE bronze.sdoh_screenings (
    screening_id VARCHAR(100) PRIMARY KEY,
    patient_id VARCHAR(100) REFERENCES bronze.patients(patient_id),
    screening_date DATE,
    
    -- Housing domain
    housing_status VARCHAR(50),
    housing_quality_concerns BOOLEAN,
    
    -- Food security domain
    food_security_score INTEGER,  -- 0=secure, 2=very insecure
    
    -- Transportation domain
    transportation_barriers BOOLEAN,
    missed_appts_due_to_transport BOOLEAN,
    
    -- Utilities domain
    utility_assistance_needed BOOLEAN,
    utility_shutoff_threat BOOLEAN,
    
    -- Safety domain
    safety_concerns BOOLEAN,
    domestic_violence_risk BOOLEAN,
    
    -- Employment domain
    employment_status VARCHAR(50),
    
    -- Education domain
    education_level VARCHAR(50),
    
    -- Social support domain
    social_isolation_score INTEGER,  -- 0-4 scale
    has_primary_support_person BOOLEAN,
    
    -- Financial domain
    financial_strain VARCHAR(50),
    insurance_status VARCHAR(50),
    
    -- Composite score
    sdoh_risk_score INTEGER,  -- 0-10 scale
    risk_category VARCHAR(50),  -- Low/Moderate/High Risk
    
    -- Metadata
    screened_by VARCHAR(100),
    screening_location VARCHAR(100),
    language_of_screening VARCHAR(50),
    
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: bronze.community_referrals
CREATE TABLE bronze.community_referrals (
    referral_id VARCHAR(100) PRIMARY KEY,
    screening_id VARCHAR(100) REFERENCES bronze.sdoh_screenings(screening_id),
    patient_id VARCHAR(100) REFERENCES bronze.patients(patient_id),
    referral_date DATE,
    service_type VARCHAR(100),
    referring_provider VARCHAR(100),
    referring_location VARCHAR(100),
    community_partner VARCHAR(200),
    referral_status VARCHAR(50),  -- Pending, Completed, Declined, Unable to Contact
    completion_date DATE,
    days_to_completion INTEGER,
    outcome_category VARCHAR(200),
    follow_up_scheduled BOOLEAN,
    notes TEXT,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- Create Indexes for Performance
-- ================================================

-- Patient indexes
CREATE INDEX idx_patients_race ON bronze.patients(race);
CREATE INDEX idx_patients_ethnicity ON bronze.patients(ethnicity);
CREATE INDEX idx_patients_zip ON bronze.patients(zip);
CREATE INDEX idx_patients_city ON bronze.patients(city);

-- Encounter indexes
CREATE INDEX idx_encounters_patient ON bronze.encounters(patient_id);
CREATE INDEX idx_encounters_date ON bronze.encounters(encounter_start);
CREATE INDEX idx_encounters_class ON bronze.encounters(encounter_class);

-- Condition indexes
CREATE INDEX idx_conditions_patient ON bronze.conditions(patient_id);
CREATE INDEX idx_conditions_code ON bronze.conditions(condition_code);

-- SDOH screening indexes
CREATE INDEX idx_screenings_patient ON bronze.sdoh_screenings(patient_id);
CREATE INDEX idx_screenings_date ON bronze.sdoh_screenings(screening_date);
CREATE INDEX idx_screenings_risk ON bronze.sdoh_screenings(risk_category);

-- Referral indexes
CREATE INDEX idx_referrals_patient ON bronze.community_referrals(patient_id);
CREATE INDEX idx_referrals_screening ON bronze.community_referrals(screening_id);
CREATE INDEX idx_referrals_status ON bronze.community_referrals(referral_status);
CREATE INDEX idx_referrals_service ON bronze.community_referrals(service_type);

-- ================================================
-- Create Views for Data Quality Monitoring
-- ================================================

CREATE OR REPLACE VIEW bronze.vw_data_quality_summary AS
SELECT
    'patients' as table_name,
    COUNT(*) as total_rows,
    COUNT(patient_id) as non_null_pk,
    MAX(ingestion_timestamp) as last_ingestion
FROM bronze.patients
UNION ALL
SELECT
    'sdoh_screenings',
    COUNT(*),
    COUNT(screening_id),
    MAX(ingestion_timestamp)
FROM bronze.sdoh_screenings
UNION ALL
SELECT
    'community_referrals',
    COUNT(*),
    COUNT(referral_id),
    MAX(ingestion_timestamp)
FROM bronze.community_referrals;

-- ================================================
-- Grant Permissions
-- ================================================

GRANT USAGE ON SCHEMA bronze TO sdoh_user;
GRANT USAGE ON SCHEMA staging TO sdoh_user;
GRANT USAGE ON SCHEMA marts TO sdoh_user;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA bronze TO sdoh_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA staging TO sdoh_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA marts TO sdoh_user;

-- Grant permissions on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA bronze GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sdoh_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA staging GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sdoh_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA marts GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sdoh_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Database schema created successfully!';
    RAISE NOTICE '   - Bronze schema: Raw data tables';
    RAISE NOTICE '   - Staging schema: Ready for dbt models';
    RAISE NOTICE '   - Marts schema: Ready for analytics';
END $$;

