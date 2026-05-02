-- Report: Community program performance metrics by service type and month
-- Shows referral volumes, completion rates, and service delivery timelines

{{
    config(
        materialized='table'
    )
}}

WITH referrals AS (
    SELECT * FROM {{ ref('stg_community_referrals') }}
),

monthly_metrics AS (
    SELECT
        service_type,
        service_category,
        DATE_TRUNC('month', referral_date)::DATE AS month,
        
        -- Volume metrics
        COUNT(*) AS total_referrals,
        COUNT(DISTINCT patient_id) AS unique_patients,
        
        -- Status metrics
        SUM(CASE WHEN is_completed THEN 1 ELSE 0 END) AS completed_referrals,
        SUM(CASE WHEN is_pending THEN 1 ELSE 0 END) AS pending_referrals,
        SUM(CASE WHEN is_declined THEN 1 ELSE 0 END) AS declined_referrals,
        
        -- Performance metrics
        ROUND(100.0 * SUM(CASE WHEN is_completed THEN 1 ELSE 0 END) / COUNT(*), 1) AS completion_rate,
        ROUND(AVG(CASE WHEN days_to_completion IS NOT NULL THEN days_to_completion END), 1) AS avg_days_to_completion,
        MIN(CASE WHEN days_to_completion IS NOT NULL THEN days_to_completion END) AS min_days_to_completion,
        MAX(CASE WHEN days_to_completion IS NOT NULL THEN days_to_completion END) AS max_days_to_completion,
        
        -- Quality indicators
        SUM(CASE WHEN follow_up_scheduled THEN 1 ELSE 0 END) AS follow_ups_scheduled,
        ROUND(100.0 * SUM(CASE WHEN follow_up_scheduled THEN 1 ELSE 0 END) / 
              NULLIF(SUM(CASE WHEN is_completed THEN 1 ELSE 0 END), 0), 1) AS follow_up_rate
        
    FROM referrals
    GROUP BY service_type, service_category, DATE_TRUNC('month', referral_date)
),

performance_targets AS (
    SELECT
        *,
        CASE
            WHEN completion_rate >= 80 THEN 'Exceeds Target'
            WHEN completion_rate >= 60 THEN 'Meets Target'
            ELSE 'Below Target'
        END AS performance_status,
        
        CASE
            WHEN avg_days_to_completion <= 30 THEN 'Fast'
            WHEN avg_days_to_completion <= 60 THEN 'Standard'
            ELSE 'Needs Improvement'
        END AS timeline_status
        
    FROM monthly_metrics
)

SELECT * FROM performance_targets
ORDER BY month DESC, total_referrals DESC
