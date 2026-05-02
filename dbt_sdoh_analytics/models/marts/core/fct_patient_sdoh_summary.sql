-- Fact table: Patient-level SDOH summary with most recent screening and intervention status
-- One row per patient with current SDOH risk and service utilization

{{
    config(
        materialized='table',
        unique_key='patient_id'
    )
}}


WITH patients AS (
    SELECT * FROM {{ ref('stg_patients') }}
),

latest_screening AS (
    SELECT
        patient_id,
        screening_id,
        screening_date AS last_screening_date,
        housing_status,
        food_security_score,
        food_security_status,
        transportation_barriers,
        is_unemployed,
        social_isolation_score,
        is_socially_isolated,
        financial_strain,
        insurance_status,
        sdoh_risk_score,
        risk_category,
        risk_category_numeric,
        screening_location,
        ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY screening_date DESC) as rn
    FROM {{ ref('stg_sdoh_screenings') }}
),

latest_screening_filtered AS (
    SELECT * FROM latest_screening WHERE rn = 1
),

referral_summary AS (
    SELECT
        patient_id,
        COUNT(*) AS total_referrals,
        SUM(CASE WHEN is_completed THEN 1 ELSE 0 END) AS completed_referrals,
        SUM(CASE WHEN is_pending THEN 1 ELSE 0 END) AS pending_referrals,
        SUM(CASE WHEN is_declined THEN 1 ELSE 0 END) AS declined_referrals,
        MAX(referral_date) AS last_referral_date,
        AVG(CASE WHEN days_to_completion IS NOT NULL THEN days_to_completion END) AS avg_days_to_completion,
        COUNT(DISTINCT service_type) AS unique_services_received
    FROM {{ ref('stg_community_referrals') }}
    GROUP BY patient_id
),

final AS (
    SELECT
        -- Patient demographics
        p.patient_id,
        p.full_name,
        p.age,
        p.age_group,
        p.gender,
        p.race,
        p.ethnicity,
        p.city,
        p.state,
        p.zip,
        p.latitude,
        p.longitude,
        
        -- SDOH screening status
        s.last_screening_date,
        CASE
            WHEN s.last_screening_date IS NULL THEN 'Never Screened'
            WHEN (CURRENT_DATE - s.last_screening_date)::INTEGER <= 180 THEN 'Recently Screened (<6 months)'
            WHEN (CURRENT_DATE - s.last_screening_date)::INTEGER <= 365 THEN 'Screened (6-12 months)'
            ELSE 'Screening Overdue (>12 months)'
        END AS screening_status,
        
        -- SDOH risk assessment
        COALESCE(s.sdoh_risk_score, 0) AS sdoh_risk_score,
        COALESCE(s.risk_category, 'Not Screened') AS risk_category,
        COALESCE(s.risk_category_numeric, 0) AS risk_category_numeric,
        
        -- Specific SDOH domains
        s.housing_status,
        s.food_security_score,
        s.food_security_status,
        s.transportation_barriers,
        s.is_unemployed,
        s.social_isolation_score,
        s.is_socially_isolated,
        s.financial_strain,
        s.insurance_status,
        s.screening_location AS last_screening_location,
        
        -- Referral metrics
        COALESCE(r.total_referrals, 0) AS total_referrals,
        COALESCE(r.completed_referrals, 0) AS completed_referrals,
        COALESCE(r.pending_referrals, 0) AS pending_referrals,
        COALESCE(r.declined_referrals, 0) AS declined_referrals,
        r.last_referral_date,
        r.avg_days_to_completion,
        COALESCE(r.unique_services_received, 0) AS unique_services_received,
        
        -- Calculated metrics
        CASE
            WHEN r.total_referrals > 0 THEN ROUND(100.0 * r.completed_referrals / r.total_referrals, 1)
            ELSE NULL
        END AS referral_completion_rate,
        
        CASE
            WHEN s.risk_category = 'High Risk' AND (r.total_referrals = 0 OR r.total_referrals IS NULL) THEN TRUE
            ELSE FALSE
        END AS high_risk_no_referrals,
        
        CASE
            WHEN s.risk_category IN ('Moderate Risk', 'High Risk') AND r.pending_referrals > 0 THEN TRUE
            ELSE FALSE
        END AS has_pending_services,
        
        -- Metadata
        CURRENT_TIMESTAMP AS dbt_updated_at
        
    FROM patients p
    LEFT JOIN latest_screening_filtered s ON p.patient_id = s.patient_id
    LEFT JOIN referral_summary r ON p.patient_id = r.patient_id
)

SELECT * FROM final
