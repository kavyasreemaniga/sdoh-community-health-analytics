"""
Master data loading script - loads all CSV data into PostgreSQL
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from load_patients import PatientDataLoader
from load_sdoh_screenings import SDOHScreeningLoader
from load_community_referrals import CommunityReferralLoader

def load_all_data():
    """Load all data into bronze schema"""
    print("\n" + "="*60)
    print(" 🏥 SDOH Community Health Analytics - Data Loading Pipeline")
    print("="*60)
    
    try:
        # Load patients
        print("\n[1/3] Loading Patients...")
        patient_loader = PatientDataLoader()
        patient_count = patient_loader.load_patients()
        
        # Load SDOH screenings
        print("\n[2/3] Loading SDOH Screenings...")
        screening_loader = SDOHScreeningLoader()
        screening_count = screening_loader.load_screenings()
        
        # Load community referrals
        print("\n[3/3] Loading Community Referrals...")
        referral_loader = CommunityReferralLoader()
        referral_count = referral_loader.load_referrals()
        
        # Summary
        print("\n" + "="*60)
        print(" ✅ DATA LOADING COMPLETE!")
        print("="*60)
        print(f"  📊 Patients:            {patient_count:,}")
        print(f"  📊 SDOH Screenings:     {screening_count:,}")
        print(f"  📊 Community Referrals: {referral_count:,}")
        print("="*60)
        print("\n🎯 Ready for Phase 3: dbt Transformations!\n")
        
    except Exception as e:
        print(f"\n❌ Error during data loading: {e}")
        raise

if __name__ == "__main__":
    load_all_data()