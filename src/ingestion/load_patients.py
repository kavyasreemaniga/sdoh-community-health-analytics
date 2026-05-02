import pandas as pd
import sys
from pathlib import Path
from sqlalchemy import text 

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.db_connection import DatabaseConnection

class PatientDataLoader:
    """Load Synthea patient data into PostgreSQL"""
    
    def __init__(self, csv_path='data/raw/csv/patients.csv'):
        self.csv_path = csv_path
        self.db = DatabaseConnection()
        self.engine = self.db.connect()
    
    def load_patients(self):
        """Load patients CSV into bronze.patients table"""
        print("="*50)
        print("Loading Patient Data")
        print("="*50)
        
        # Read CSV
        print(f"\n📖 Reading {self.csv_path}...")
        df = pd.read_csv(self.csv_path)
        print(f"   Found {len(df)} patients")
        
        # Rename columns to match database schema (lowercase)
        column_mapping = {
            'Id': 'patient_id',
            'BIRTHDATE': 'birth_date',
            'DEATHDATE': 'death_date',
            'SSN': 'ssn',
            'DRIVERS': 'drivers',
            'PASSPORT': 'passport',
            'PREFIX': 'prefix',
            'FIRST': 'first_name',
            'LAST': 'last_name',
            'MAIDEN': 'maiden',
            'MARITAL': 'marital_status',
            'RACE': 'race',
            'ETHNICITY': 'ethnicity',
            'GENDER': 'gender',
            'BIRTHPLACE': 'birthplace',
            'ADDRESS': 'address',
            'CITY': 'city',
            'STATE': 'state',
            'COUNTY': 'county',
            'ZIP': 'zip',
            'LAT': 'lat',
            'LON': 'lon',
            'HEALTHCARE_EXPENSES': 'healthcare_expenses',
            'HEALTHCARE_COVERAGE': 'healthcare_coverage',
            'INCOME': 'income'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Select only columns that exist in database
        db_columns = list(column_mapping.values())
        df = df[[col for col in db_columns if col in df.columns]]

        # TRUNCATE table first (preserves structure, removes data)
        print(f"\n🗑️  Truncating bronze.patients...")
        with self.engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE bronze.patients CASCADE"))
            conn.commit()
        
        # Load into database
        print(f"\n💾 Loading into bronze.patients...")
        df.to_sql(
            name='patients',
            con=self.engine,
            schema='bronze',
            if_exists='append',  # Use 'append' to add to existing data
            index=False,
            method='multi',
            chunksize=1000
        )
        
        # Verify
        count = self.db.get_table_count('bronze', 'patients')
        print(f"✅ Loaded {count} patients into bronze.patients")
        
        # Show sample
        print(f"\n📊 Sample data:")
        sample = pd.read_sql(
            "SELECT patient_id, first_name, last_name, race, ethnicity, city, zip FROM bronze.patients LIMIT 5",
            self.engine
        )
        print(sample.to_string(index=False))
        
        self.db.close()
        return count

if __name__ == "__main__":
    loader = PatientDataLoader()
    loader.load_patients()