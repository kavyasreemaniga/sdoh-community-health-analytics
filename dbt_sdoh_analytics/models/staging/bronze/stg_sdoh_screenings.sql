-- Staging model: Standardize SDOH screening data with risk calculations
-- Source: bronze.sdoh_screenings (PRAPARE framework)

WITH source AS (
    SELECT * FROM {{ source('bronze', 'sdoh_screenings') }}
),

standardized AS (
    SELECT
        -- IDs
        screening_id,
        patient_id,
        screening_date,
        
        -- Housing domain
        housing_status,
        COALESCE(housing_quality_concerns, FALSE) AS housing_quality_concerns,
        CASE housing_status
            WHEN 'Homeless' THEN 3
            WHEN 'Unstable Housing' THEN 2
            WHEN 'Temporary/Transitional' THEN 2
            ELSE 0
        END AS housing_risk_points,
        
        -- Food security domain
        COALESCE(food_security_score, 0) AS food_security_score,
        CASE
            WHEN food_security_score >= 2 THEN 'Food Insecure - Severe'
            WHEN food_security_score = 1 THEN 'Food Insecure - Mild'
            ELSE 'Food Secure'
        END AS food_security_status,
        
        -- Transportation domain
        COALESCE(transportation_barriers, FALSE) AS transportation_barriers,
        COALESCE(missed_appts_due_to_transport, FALSE) AS missed_appts_due_to_transport,
        
        -- Utilities domain
        COALESCE(utility_assistance_needed, FALSE) AS utility_assistance_needed,
        COALESCE(utility_shutoff_threat, FALSE) AS utility_shutoff_threat,
        
        -- Safety domain
        COALESCE(safety_concerns, FALSE) AS safety_concerns,
        COALESCE(domestic_violence_risk, FALSE) AS domestic_violence_risk,
        
        -- Employment domain
        employment_status,
        CASE employment_status
            WHEN 'Unemployed' THEN TRUE
            ELSE FALSE
        END AS is_unemployed,
        
        -- Education domain
        education_level,
        CASE education_level
            WHEN 'Less than High School' THEN 'Low'
            WHEN 'High School/GED' THEN 'Medium'
            WHEN 'Some College' THEN 'Medium'
            WHEN 'Associate Degree' THEN 'Medium'
            ELSE 'High'
        END AS education_level_category,
        
        -- Social support domain
        COALESCE(social_isolation_score, 0) AS social_isolation_score,
        COALESCE(has_primary_support_person, FALSE) AS has_primary_support_person,
        CASE
            WHEN social_isolation_score >= 3 THEN TRUE
            ELSE FALSE
        END AS is_socially_isolated,
        
        -- Financial domain
        financial_strain,
        insurance_status,
        CASE financial_strain
            WHEN 'Severe Strain' THEN 2
            WHEN 'Moderate Strain' THEN 1
            ELSE 0
        END AS financial_strain_points,
        
        -- Composite risk
        COALESCE(sdoh_risk_score, 0) AS sdoh_risk_score,
        risk_category,
        CASE risk_category
            WHEN 'High Risk' THEN 3
            WHEN 'Moderate Risk' THEN 2
            WHEN 'Low Risk' THEN 1
            ELSE 0
        END AS risk_category_numeric,
        
        -- Metadata
        screened_by,
        screening_location,
        language_of_screening,
        ingestion_timestamp
        
    FROM source
)

SELECT * FROM standardized
