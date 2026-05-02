# SDOH Community Health Analytics - Dataset Summary

**Generated:** $(25-April-2026)

## Dataset Overview

### 1. Synthetic Patients (Synthea)
- **Source:** Synthea FHIR Generator
- **Total Patients:** 1,000
- **Geography:** Colorado (Denver metro area)
- **ZIP Codes:** 80010-80264 (35 ZIP codes)
- **Demographics:** Diverse by age, race, ethnicity
- **Clinical Data:** Conditions, encounters, medications, labs

### 2. SDOH Screenings (PRAPARE Framework)
- **Total Screenings:** 1,725
- **Unique Patients:** 1,000
- **Screening Rate:** 100% (all patients screened at least once)
- **Average Screenings per Patient:** 1.7

**Risk Distribution:**
- Low Risk: ~60%
- Moderate Risk: ~30%
- High Risk: ~10%

**SDOH Domains Covered:**
1. Housing Stability
2. Food Security (Hunger Vital Sign)
3. Transportation Access
4. Utility Assistance Needs
5. Safety & Domestic Violence
6. Employment Status
7. Education Level
8. Social Support & Isolation
9. Financial Strain
10. Insurance Status

### 3. Community Referrals & Interventions
- **Total Referrals:** 1,520
- **Unique Patients Served:** 566
- **Completion Rate:** 69.0%
- **Average Days to Completion:** 49.5 days

**Referral Status Breakdown:**
- Completed: 1,049 (69.0%)
- Pending: 269 (17.7%)
- Unable to Contact: 130 (8.6%)
- Declined: 72 (4.7%)

**Top Service Types:**
1. Housing Support (307 referrals)
2. Food Assistance (257 referrals)
3. Financial Counseling (225 referrals)
4. Legal Aid (219 referrals)
5. Mental Health Support (153 referrals)

## Data Quality Notes

✅ **Completeness:** All patients have demographics and at least one screening
✅ **Realism:** Risk distribution and completion rates match real-world SDOH programs
✅ **Temporal Coverage:** Screenings span 2 years (2023-2025)
✅ **Referral Logic:** Referrals aligned with identified SDOH needs

## Ready for Phase 2: Database & Pipeline Development
