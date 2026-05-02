-- Staging model: Standardize community referral and intervention data
-- Source: bronze.community_referrals

WITH source AS (
    SELECT * FROM {{ source('bronze', 'community_referrals') }}
),

standardized AS (
    SELECT
        -- IDs
        referral_id,
        screening_id,
        patient_id,
        
        -- Referral details
        referral_date,
        service_type,
        
        -- Categorize service types into broader groups
        CASE
            WHEN service_type LIKE '%Food%' THEN 'Basic Needs'
            WHEN service_type LIKE '%Housing%' THEN 'Basic Needs'
            WHEN service_type LIKE '%Utility%' THEN 'Basic Needs'
            WHEN service_type LIKE '%Transportation%' THEN 'Transportation'
            WHEN service_type LIKE '%Employment%' THEN 'Economic Stability'
            WHEN service_type LIKE '%Financial%' THEN 'Economic Stability'
            WHEN service_type LIKE '%Mental Health%' THEN 'Health & Wellness'
            WHEN service_type LIKE '%Legal%' THEN 'Safety & Legal'
            WHEN service_type LIKE '%Care Coordination%' THEN 'Care Management'
            ELSE 'Other'
        END AS service_category,
        
        -- Provider info
        referring_provider,
        referring_location,
        community_partner,
        
        -- Status tracking
        referral_status,
        CASE referral_status
            WHEN 'Completed' THEN TRUE
            ELSE FALSE
        END AS is_completed,
        CASE referral_status
            WHEN 'Pending' THEN TRUE
            ELSE FALSE
        END AS is_pending,
        CASE referral_status
            WHEN 'Declined' THEN TRUE
            ELSE FALSE
        END AS is_declined,
        
        -- Completion metrics
        completion_date,
        COALESCE(days_to_completion, 
                 (CURRENT_DATE - referral_date)::INTEGER) AS days_since_referral,
        days_to_completion,
        
        -- Performance categorization
        CASE
            WHEN days_to_completion IS NULL THEN 'Not Completed'
            WHEN days_to_completion <= 30 THEN 'Fast (<30 days)'
            WHEN days_to_completion <= 60 THEN 'Standard (30-60 days)'
            ELSE 'Slow (>60 days)'
        END AS completion_speed_category,
        
        -- Outcome
        outcome_category,
        COALESCE(follow_up_scheduled, FALSE) AS follow_up_scheduled,
        notes,
        
        -- Metadata
        ingestion_timestamp
        
    FROM source
)

SELECT * FROM standardized
