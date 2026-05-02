-- Staging model: Clean and standardize patient demographics
-- Source: bronze.patients (Synthea data)

WITH source AS (
    SELECT * FROM {{ source('bronze', 'patients') }}
),

cleaned AS (
    SELECT
        -- IDs
        patient_id,
        
        -- Demographics
        birth_date,
        CASE 
            WHEN death_date IS NOT NULL THEN death_date
            ELSE NULL
        END AS death_date,
        
        -- Calculate age and age group
        DATE_PART('year', AGE(COALESCE(death_date, CURRENT_DATE), birth_date)) AS age,
        CASE
            WHEN DATE_PART('year', AGE(COALESCE(death_date, CURRENT_DATE), birth_date)) < 18 THEN 'Pediatric'
            WHEN DATE_PART('year', AGE(COALESCE(death_date, CURRENT_DATE), birth_date)) BETWEEN 18 AND 64 THEN 'Adult'
            ELSE 'Senior (65+)'
        END AS age_group,
        
        -- Name fields
        TRIM(CONCAT(first_name, ' ', last_name)) AS full_name,
        first_name,
        last_name,
        
        -- Standardized demographics
        LOWER(TRIM(gender)) AS gender,
        COALESCE(NULLIF(TRIM(race), ''), 'Unknown') AS race,
        COALESCE(NULLIF(TRIM(ethnicity), ''), 'Unknown') AS ethnicity,
        
        
        -- Geographic
        TRIM(address) AS address,
        TRIM(city) AS city,
        TRIM(state) AS state,
        TRIM(zip) AS zip,
        lat AS latitude,
        lon AS longitude,
        
        -- Financial
        COALESCE(healthcare_expenses, 0) AS healthcare_expenses,
        COALESCE(healthcare_coverage, 0) AS healthcare_coverage,
        income,
        
        -- Metadata
        ingestion_timestamp
        
    FROM source
)

SELECT * FROM cleaned
