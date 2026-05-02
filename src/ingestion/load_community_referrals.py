import pandas as pd
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.append(str(Path(__file__).parent.parent))
from utils.db_connection import DatabaseConnection

class CommunityReferralLoader:
    """Load community referral data into PostgreSQL"""
    
    def __init__(self, csv_path='data/raw/community_referrals.csv'):
        self.csv_path = csv_path
        self.db = DatabaseConnection()
        self.engine = self.db.connect()
    
    def load_referrals(self):
        """Load referrals into bronze.community_referrals"""
        print("="*50)
        print("Loading Community Referral Data")
        print("="*50)
        
        # Read CSV
        print(f"\n📖 Reading {self.csv_path}...")
        df = pd.read_csv(self.csv_path)
        print(f"   Found {len(df)} referrals")
        
        # Convert boolean column
        if 'follow_up_scheduled' in df.columns:
            df['follow_up_scheduled'] = df['follow_up_scheduled'].astype(bool)
        
        # Load into database
        print(f"\n💾 Loading into bronze.community_referrals...")
        df.to_sql(
            name='community_referrals',
            con=self.engine,
            schema='bronze',
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000
        )
        
        # Verify
        count = self.db.get_table_count('bronze', 'community_referrals')
        print(f"✅ Loaded {count} referrals into bronze.community_referrals")
        
        # Show status distribution
        print(f"\n📊 Referral Status Distribution:")
        dist = pd.read_sql(
            "SELECT referral_status, COUNT(*) as count FROM bronze.community_referrals GROUP BY referral_status ORDER BY count DESC",
            self.engine
        )
        print(dist.to_string(index=False))
        
        # Show top services
        print(f"\n📊 Top Service Types:")
        services = pd.read_sql(
            "SELECT service_type, COUNT(*) as count FROM bronze.community_referrals GROUP BY service_type ORDER BY count DESC LIMIT 5",
            self.engine
        )
        print(services.to_string(index=False))
        
        self.db.close()
        return count

if __name__ == "__main__":
    loader = CommunityReferralLoader()
    loader.load_referrals()