import pandas as pd
import sys
from pathlib import Path
from sqlalchemy import text 

sys.path.append(str(Path(__file__).parent.parent))
from utils.db_connection import DatabaseConnection

class SDOHScreeningLoader:
    """Load SDOH screening data into PostgreSQL"""
    
    def __init__(self, csv_path='data/raw/sdoh_screenings.csv'):
        self.csv_path = csv_path
        self.db = DatabaseConnection()
        self.engine = self.db.connect()
    
    def load_screenings(self):
        """Load SDOH screenings into bronze.sdoh_screenings"""
        print("="*50)
        print("Loading SDOH Screening Data")
        print("="*50)
        
        # Read CSV
        print(f"\n📖 Reading {self.csv_path}...")
        df = pd.read_csv(self.csv_path)
        print(f"   Found {len(df)} screenings")
        
        # Convert boolean strings to actual booleans
        bool_columns = [
            'housing_quality_concerns', 'transportation_barriers',
            'missed_appts_due_to_transport', 'utility_assistance_needed',
            'utility_shutoff_threat', 'safety_concerns',
            'domestic_violence_risk', 'has_primary_support_person',
            'follow_up_scheduled'
        ]
        
        for col in bool_columns:
            if col in df.columns:
                df[col] = df[col].astype(bool)
        
        # Load into database
        print(f"\n💾 Loading into bronze.sdoh_screenings...")
        df.to_sql(
            name='sdoh_screenings',
            con=self.engine,
            schema='bronze',
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000
        )
        
        # Verify
        count = self.db.get_table_count('bronze', 'sdoh_screenings')
        print(f"✅ Loaded {count} screenings into bronze.sdoh_screenings")
        
        # Show risk distribution
        print(f"\n📊 Risk Distribution:")
        dist = pd.read_sql(
            "SELECT risk_category, COUNT(*) as count FROM bronze.sdoh_screenings GROUP BY risk_category ORDER BY count DESC",
            self.engine
        )
        print(dist.to_string(index=False))
        
        self.db.close()
        return count

if __name__ == "__main__":
    loader = SDOHScreeningLoader()
    loader.load_screenings()