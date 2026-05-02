import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()
Faker.seed(42)
np.random.seed(42)

class CommunityReferralGenerator:
    def __init__(self, screenings_csv_path):
        """Initialize with SDOH screenings"""
        self.screenings = pd.read_csv(screenings_csv_path)
        print(f"Loaded {len(self.screenings)} SDOH screenings")
        
        # Service types based on SDOH domains
        self.service_types = {
            'Food Assistance': ['food_security_score'],
            'Housing Support': ['housing_status'],
            'Transportation Vouchers': ['transportation_barriers'],
            'Utility Assistance': ['utility_assistance_needed'],
            'Employment Services': ['employment_status'],
            'Mental Health Support': ['social_isolation_score'],
            'Financial Counseling': ['financial_strain'],
            'Legal Aid': ['housing_status', 'safety_concerns'],
            'Care Coordination': ['sdoh_risk_score']
        }
    
    def generate_referrals(self, output_path='data/raw/community_referrals.csv'):
        """Generate community program referrals based on SDOH needs"""
        
        referrals = []
        
        # Focus on moderate and high-risk patients
        high_risk_screenings = self.screenings[
            self.screenings['risk_category'].isin(['Moderate Risk', 'High Risk'])
        ]
        
        print(f"Generating referrals for {len(high_risk_screenings)} at-risk screenings...")
        
        for idx, screening in high_risk_screenings.iterrows():
            # Determine services needed
            needed_services = self._determine_needed_services(screening)
            
            # Generate 1-4 referrals per screening
            num_referrals = min(len(needed_services), random.randint(1, 4))
            selected_services = random.sample(needed_services, num_referrals)
            
            for service_type in selected_services:
                referral_date = pd.to_datetime(screening['screening_date']) + timedelta(days=random.randint(0, 7))
                
                # Referral status and completion
                status, completion_date, outcome = self._generate_referral_outcome(
                    referral_date,
                    screening['risk_category']
                )
                
                referral = {
                    'referral_id': f"REF-{screening['screening_id']}-{fake.uuid4()[:8]}",
                    'screening_id': screening['screening_id'],
                    'patient_id': screening['patient_id'],
                    'referral_date': referral_date.strftime('%Y-%m-%d'),
                    'service_type': service_type,
                    'referring_provider': fake.name(),
                    'referring_location': screening['screening_location'],
                    'community_partner': self._get_community_partner(service_type),
                    'referral_status': status,
                    'completion_date': completion_date,
                    'days_to_completion': (pd.to_datetime(completion_date) - referral_date).days if completion_date else None,
                    'outcome_category': outcome,
                    'follow_up_scheduled': random.random() > 0.3 if status == 'Completed' else False,
                    'notes': self._generate_outcome_notes(service_type, status)
                }
                
                referrals.append(referral)
            
            if (idx + 1) % 100 == 0:
                print(f"Generated referrals for {idx + 1} screenings...")
        
        # Create DataFrame
        df = pd.DataFrame(referrals)
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        print(f"\n✅ Generated {len(df)} community referrals")
        print(f"📁 Saved to: {output_path}")
        
        # Print summary
        self._print_summary(df)
        
        return df
    
    def _determine_needed_services(self, screening):
        """Determine which services a patient needs based on screening"""
        services = []
        
        # Food assistance
        if screening['food_security_score'] >= 1:
            services.append('Food Assistance')
        
        # Housing support
        if screening['housing_status'] in ['Homeless', 'Unstable Housing', 'Temporary/Transitional']:
            services.append('Housing Support')
        
        # Transportation
        if screening['transportation_barriers']:
            services.append('Transportation Vouchers')
        
        # Utilities
        if screening['utility_assistance_needed']:
            services.append('Utility Assistance')
        
        # Employment
        if screening['employment_status'] == 'Unemployed':
            services.append('Employment Services')
        
        # Mental health / social support
        if screening['social_isolation_score'] >= 3:
            services.append('Mental Health Support')
        
        # Financial counseling
        if screening['financial_strain'] in ['Moderate Strain', 'Severe Strain']:
            services.append('Financial Counseling')
        
        # Legal aid for housing/safety issues
        if screening['housing_status'] in ['Homeless', 'Unstable Housing'] or screening['safety_concerns']:
            services.append('Legal Aid')
        
        # Care coordination for high-risk patients
        if screening['sdoh_risk_score'] >= 7:
            services.append('Care Coordination')
        
        return services
    
    def _generate_referral_outcome(self, referral_date, risk_category):
        """Generate realistic referral status and completion"""
        
        # Completion rates vary by risk category
        completion_prob = {
            'High Risk': 0.55,      # Higher barriers to completion
            'Moderate Risk': 0.70,
            'Low Risk': 0.80
        }.get(risk_category, 0.65)
        
        # Determine status
        if random.random() < completion_prob:
            status = 'Completed'
            days_to_complete = random.randint(7, 90)
            completion_date = (referral_date + timedelta(days=days_to_complete)).strftime('%Y-%m-%d')
            outcome = random.choice([
                'Service Received - Patient Satisfied',
                'Service Received - Ongoing Support',
                'Partial Service - Additional Needs Identified'
            ])
        elif random.random() < 0.15:
            status = 'Declined'
            completion_date = None
            outcome = random.choice([
                'Patient Declined',
                'Not Interested in Service',
                'Already Receiving Similar Service'
            ])
        elif random.random() < 0.30:
            status = 'Unable to Contact'
            completion_date = None
            outcome = 'Unable to Reach Patient After 3 Attempts'
        else:
            status = 'Pending'
            completion_date = None
            outcome = 'Awaiting Patient Response'
        
        return status, completion_date, outcome
    
    def _get_community_partner(self, service_type):
        """Get community partner organization for service type"""
        partners = {
            'Food Assistance': ['Denver Food Bank', 'Food for Thought Denver', 'Community Harvest', 'Meals on Wheels'],
            'Housing Support': ['Metro Denver Homeless Initiative', 'Colorado Coalition for the Homeless', 'St. Francis Center'],
            'Transportation Vouchers': ['RTD Access-a-Ride', 'Mile High United Way Transport', 'Freedom Rides'],
            'Utility Assistance': ['LEAP Program', 'Energy Outreach Colorado', 'Project Warmth'],
            'Employment Services': ['Goodwill Job Connection', 'Denver Workforce Center', 'Re:Vision Career Services'],
            'Mental Health Support': ['Mental Health Center of Denver', 'Community Reach Center', 'Denver Health Behavioral'],
            'Financial Counseling': ['Mile High United Way Financial Coaching', 'GreenPath Financial Wellness'],
            'Legal Aid': ['Colorado Legal Services', 'Metro Volunteer Lawyers'],
            'Care Coordination': ['CommunityHealth CHW Program', 'Denver Health Care Management']
        }
        return random.choice(partners.get(service_type, ['Community Partner']))
    
    def _generate_outcome_notes(self, service_type, status):
        """Generate realistic outcome notes"""
        if status == 'Completed':
            return f"{service_type} provided. Patient reported improved situation."
        elif status == 'Declined':
            return f"Patient declined {service_type}. Provided alternative resources."
        elif status == 'Unable to Contact':
            return "Multiple contact attempts made. Left voicemail with callback number."
        else:
            return f"Referral sent to partner organization. Awaiting confirmation."
    
    def _print_summary(self, df):
        """Print summary statistics"""
        print("\n" + "="*50)
        print("Community Referral Summary")
        print("="*50)
        print(f"\nTotal Referrals: {len(df)}")
        print(f"Unique Patients: {df['patient_id'].nunique()}")
        print(f"\nReferral Status:")
        print(df['referral_status'].value_counts())
        print(f"\nCompletion Rate: {(df['referral_status'] == 'Completed').sum() / len(df) * 100:.1f}%")
        print(f"\nTop Services:")
        print(df['service_type'].value_counts().head(5))
        print(f"\nAverage Days to Completion: {df[df['days_to_completion'].notna()]['days_to_completion'].mean():.1f} days")
        print("="*50)

# Main execution
if __name__ == "__main__":
    print("🤝 Community Referral Data Generator")
    print("="*50)
    
    # Generate referrals
    generator = CommunityReferralGenerator('data/raw/sdoh_screenings.csv')
    referrals_df = generator.generate_referrals(
        output_path='data/raw/community_referrals.csv'
    )
    
    print("\n✅ Community referral data generation complete!")