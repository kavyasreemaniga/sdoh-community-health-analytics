-- Report: Health equity metrics by demographic groups
-- Identifies disparities in screening rates, risk distribution, and service access

{{
    config(
        materialized='table'
    )
}}

WITH patient_summary AS (
    SELECT * FROM {{ ref('fct_patient_sdoh_summary') }}
),

demographic_metrics AS (
    SELECT
        race,
        ethnicity,
        age_group,
        zip,
        city,
        
        -- Population counts
        COUNT(*) AS total_patients,
        
        -- Screening metrics
        SUM(CASE WHEN last_screening_date IS NOT NULL THEN 1 ELSE 0 END) AS patients_screened,
        ROUND(100.0 * SUM(CASE WHEN last_screening_date IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS screening_rate,
        
        -- Risk distribution
        AVG(COALESCE(sdoh_risk_score, 0)) AS avg_risk_score,
        SUM(CASE WHEN risk_category = 'High Risk' THEN 1 ELSE 0 END) AS high_risk_count,
        SUM(CASE WHEN risk_category = 'Moderate Risk' THEN 1 ELSE 0 END) AS moderate_risk_count,
        SUM(CASE WHEN risk_category = 'Low Risk' THEN 1 ELSE 0 END) AS low_risk_count,
        ROUND(100.0 * SUM(CASE WHEN risk_category = 'High Risk' THEN 1 ELSE 0 END) / 
              NULLIF(SUM(CASE WHEN last_screening_date IS NOT NULL THEN 1 ELSE 0 END), 0), 1) AS high_risk_pct,
        
        -- Service utilization
        SUM(total_referrals) AS total_referrals,
        SUM(completed_referrals) AS completed_referrals,
        ROUND(AVG(NULLIF(referral_completion_rate, 0)), 1) AS avg_completion_rate,
        
        -- Specific SDOH needs
        SUM(CASE WHEN housing_status IN ('Homeless', 'Unstable Housing') THEN 1 ELSE 0 END) AS housing_insecure_count,
        SUM(CASE WHEN food_security_score >= 1 THEN 1 ELSE 0 END) AS food_insecure_count,
        SUM(CASE WHEN transportation_barriers THEN 1 ELSE 0 END) AS transport_barriers_count,
        SUM(CASE WHEN is_unemployed THEN 1 ELSE 0 END) AS unemployed_count,
        
        -- Unmet needs
        SUM(CASE WHEN high_risk_no_referrals THEN 1 ELSE 0 END) AS high_risk_no_services
        
    FROM patient_summary
    GROUP BY race, ethnicity, age_group, zip, city
    HAVING COUNT(*) >= 5  -- Privacy threshold: only show groups with 5+ patients
)

SELECT * FROM demographic_metrics
ORDER BY total_patients DESC
