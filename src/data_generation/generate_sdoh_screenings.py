import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()
Faker.seed(42)
np.random.seed(42)

class SDOHScreeningGenerator:
    def __init__(self, patients_csv_path):
        """Initialize with patients from Synthea CSV"""
        self.patients = pd.read_csv(patients_csv_path)
        print(f"Loaded {len(self.patients)} patients from Synthea")
        
    def generate_screenings(self, screenings_per_patient=2, output_path='data/raw/sdoh_screenings.csv'):
        """Generate PRAPARE-based SDOH screenings"""
        
        screenings = []
        
        for idx, patient in self.patients.iterrows():
            # Get patient details
            patient_id = patient['Id']
            zip_code = patient['ZIP'] if 'ZIP' in patient else '21202'
            race = patient['RACE'] if 'RACE' in patient else 'white'
            ethnicity = patient['ETHNICITY'] if 'ETHNICITY' in patient else 'nonhispanic'
            
            # Determine base risk based on demographics (for realistic variation)
            base_risk = self._calculate_base_risk(zip_code, race, ethnicity)
            
            # Generate 1-3 screenings over past 2 years
            num_screenings = random.randint(1, screenings_per_patient)
            
            for i in range(num_screenings):
                screening_date = datetime.now() - timedelta(days=random.randint(0, 730))
                
                screening = {
                    'screening_id': f"SCR-{patient_id}-{i+1}",
                    'patient_id': patient_id,
                    'screening_date': screening_date.strftime('%Y-%m-%d'),
                    
                    # PRAPARE Domain 1: Housing
                    'housing_status': self._generate_housing_status(base_risk),
                    'housing_quality_concerns': random.random() < base_risk * 0.3,
                    
                    # PRAPARE Domain 2: Food Security (0-2 Hunger Vital Sign)
                    'food_security_score': self._generate_food_security(base_risk),
                    
                    # PRAPARE Domain 3: Transportation
                    'transportation_barriers': random.random() < base_risk * 0.4,
                    'missed_appts_due_to_transport': random.random() < base_risk * 0.25,
                    
                    # PRAPARE Domain 4: Utilities
                    'utility_assistance_needed': random.random() < base_risk * 0.3,
                    'utility_shutoff_threat': random.random() < base_risk * 0.15,
                    
                    # PRAPARE Domain 5: Safety
                    'safety_concerns': random.random() < base_risk * 0.2,
                    'domestic_violence_risk': random.random() < base_risk * 0.1,
                    
                    # PRAPARE Domain 6: Employment
                    'employment_status': self._generate_employment_status(base_risk),
                    
                    # PRAPARE Domain 7: Education
                    'education_level': self._generate_education_level(base_risk),
                    
                    # PRAPARE Domain 8: Social Support
                    'social_isolation_score': self._generate_social_isolation(base_risk),
                    'has_primary_support_person': random.random() > base_risk * 0.5,
                    
                    # PRAPARE Domain 9: Financial Strain
                    'financial_strain': self._generate_financial_strain(base_risk),
                    'insurance_status': self._generate_insurance_status(base_risk),
                    
                    # Metadata
                    'screened_by': fake.name(),
                    'screening_location': random.choice(['Primary Care Clinic', 'Community Health Center', 'Home Visit', 'ED']),
                    'language_of_screening': 'English' if random.random() > 0.15 else random.choice(['Spanish', 'Vietnamese', 'Somali']),
                }
                
                screenings.append(screening)
            
            if (idx + 1) % 100 == 0:
                print(f"Generated screenings for {idx + 1} patients...")
        
        # Create DataFrame
        df = pd.DataFrame(screenings)
        
        # Add composite risk score
        df['sdoh_risk_score'] = df.apply(self._calculate_risk_score, axis=1)
        df['risk_category'] = df['sdoh_risk_score'].apply(
            lambda x: 'High Risk' if x >= 7 else ('Moderate Risk' if x >= 4 else 'Low Risk')
        )
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        print(f"\n✅ Generated {len(df)} SDOH screenings")
        print(f"📁 Saved to: {output_path}")
        
        # Print summary stats
        self._print_summary(df)
        
        return df
    
    def _calculate_base_risk(self, zip_code, race, ethnicity):
        """Calculate base SDOH risk based on demographics - Baltimore City"""
        base_risk = 0.25  # 25% baseline (higher than national avg)
        
        # Higher risk for certain Baltimore ZIP codes
        high_risk_zips = [
            '21201', '21202', '21205', '21213', '21216', 
            '21217', '21223', '21225', '21226', '21229'
        ]
        
        moderate_risk_zips = [
            '21206', '21207', '21211', '21218', '21224'
        ]
        
        low_risk_zips = [
            '21208', '21209', '21210', '21212', '21228'
        ]
        
        zip_str = str(zip_code)
        
        if zip_str in high_risk_zips:
            base_risk += 0.20  # 45% total
        elif zip_str in moderate_risk_zips:
            base_risk += 0.10  # 35% total
        elif zip_str in low_risk_zips:
            base_risk -= 0.05  # 20% total
        
        # Adjust for race/ethnicity
        if race == 'black':
            base_risk += 0.12
        if ethnicity == 'hispanic':
            base_risk += 0.08
        
        return min(base_risk, 0.65)  # Cap at 65%
    
    def _generate_housing_status(self, base_risk):
        """Generate housing status"""
        options = ['Stable Housing', 'Unstable Housing', 'Homeless', 'Temporary/Transitional']
        weights = [
            1 - base_risk,
            base_risk * 0.5,
            base_risk * 0.2,
            base_risk * 0.3
        ]
        weights = [w / sum(weights) for w in weights]  # Normalize
        return np.random.choice(options, p=weights)
    
    def _generate_food_security(self, base_risk):
        """Generate food security score (0=secure, 2=very insecure)"""
        weights = [1 - base_risk, base_risk * 0.6, base_risk * 0.4]
        weights = [w / sum(weights) for w in weights]
        return np.random.choice([0, 1, 2], p=weights)
    
    def _generate_employment_status(self, base_risk):
        """Generate employment status"""
        options = ['Employed Full-Time', 'Employed Part-Time', 'Unemployed', 'Retired', 'Disabled', 'Student']
        weights = [
            0.45 * (1 - base_risk),
            0.20,
            base_risk * 0.4,
            0.15,
            base_risk * 0.2,
            0.10
        ]
        weights = [w / sum(weights) for w in weights]
        return np.random.choice(options, p=weights)
    
    def _generate_education_level(self, base_risk):
        """Generate education level"""
        options = ['Less than High School', 'High School/GED', 'Some College', 'Associate Degree', 'Bachelor Degree', 'Graduate Degree']
        weights = [
            base_risk * 0.3,
            base_risk * 0.4 + 0.2,
            0.25,
            0.15,
            0.15 * (1 - base_risk),
            0.10 * (1 - base_risk)
        ]
        weights = [w / sum(weights) for w in weights]
        return np.random.choice(options, p=weights)
    
    def _generate_social_isolation(self, base_risk):
        """Generate social isolation score (0-4, higher = more isolated)"""
        weights = [
            0.3 * (1 - base_risk),
            0.3,
            0.2,
            base_risk * 0.3,
            base_risk * 0.2
        ]
        weights = [w / sum(weights) for w in weights]
        return np.random.choice([0, 1, 2, 3, 4], p=weights)
    
    def _generate_financial_strain(self, base_risk):
        """Generate financial strain level"""
        options = ['No Strain', 'Mild Strain', 'Moderate Strain', 'Severe Strain']
        weights = [
            0.4 * (1 - base_risk),
            0.3,
            base_risk * 0.4,
            base_risk * 0.3
        ]
        weights = [w / sum(weights) for w in weights]
        return np.random.choice(options, p=weights)
    
    def _generate_insurance_status(self, base_risk):
        """Generate insurance status"""
        options = ['Private Insurance', 'Medicaid', 'Medicare', 'Uninsured', 'Other']
        weights = [
            0.50 * (1 - base_risk),
            base_risk * 0.5,
            0.20,
            base_risk * 0.3,
            0.05
        ]
        weights = [w / sum(weights) for w in weights]
        return np.random.choice(options, p=weights)
    
    def _calculate_risk_score(self, row):
        """Calculate composite SDOH risk score (0-10 scale)"""
        score = 0
        
        # Housing (0-3 points)
        housing_scores = {
            'Stable Housing': 0,
            'Unstable Housing': 2,
            'Temporary/Transitional': 2,
            'Homeless': 3
        }
        score += housing_scores.get(row['housing_status'], 0)
        
        # Food security (0-2 points)
        score += row['food_security_score']
        
        # Transportation (0-1 point)
        score += 1 if row['transportation_barriers'] else 0
        
        # Utilities (0-1 point)
        score += 1 if row['utility_assistance_needed'] else 0
        
        # Employment (0-2 points)
        score += 2 if row['employment_status'] == 'Unemployed' else 0
        
        # Social isolation (0-2 points)
        score += min(row['social_isolation_score'] // 2, 2)
        
        # Financial strain (0-2 points)
        financial_scores = {'No Strain': 0, 'Mild Strain': 0, 'Moderate Strain': 1, 'Severe Strain': 2}
        score += financial_scores.get(row['financial_strain'], 0)
        
        return min(score, 10)  # Cap at 10
    
    def _print_summary(self, df):
        """Print summary statistics"""
        print("\n" + "="*50)
        print("SDOH Screening Summary")
        print("="*50)
        print(f"\nTotal Screenings: {len(df)}")
        print(f"Unique Patients: {df['patient_id'].nunique()}")
        print(f"\nRisk Distribution:")
        print(df['risk_category'].value_counts())
        print(f"\nAverage Risk Score: {df['sdoh_risk_score'].mean():.2f}")
        print(f"\nHousing Status:")
        print(df['housing_status'].value_counts())
        print(f"\nFood Insecurity Rate: {(df['food_security_score'] > 0).sum() / len(df) * 100:.1f}%")
        print(f"Transportation Barriers: {df['transportation_barriers'].sum() / len(df) * 100:.1f}%")
        print(f"Utility Assistance Needed: {df['utility_assistance_needed'].sum() / len(df) * 100:.1f}%")
        print("="*50)

# Main execution
if __name__ == "__main__":
    print("🏥 SDOH Screening Data Generator")
    print("="*50)
    
    # Path to Synthea patients CSV
    patients_csv = 'data/raw/csv/patients.csv'
    
    # Generate screenings
    generator = SDOHScreeningGenerator(patients_csv)
    screenings_df = generator.generate_screenings(
        screenings_per_patient=2,
        output_path='data/raw/sdoh_screenings.csv'
    )
    
    print("\n✅ SDOH screening data generation complete!")
    