import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConnection:
    """Manage PostgreSQL database connections"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'sdoh_analytics')
        self.user = os.getenv('DB_USER', 'sdoh_user')
        self.password = os.getenv('DB_PASSWORD')
        
        # Create connection string
        self.connection_string = (
            f"postgresql://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )
        
        # Create engine
        self.engine = None
        self.session = None
    
    def connect(self):
        """Create database engine and session"""
        try:
            self.engine = create_engine(
                self.connection_string,
                echo=False,  # Set to True to see SQL queries
                pool_pre_ping=True
            )
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"✅ Connected to PostgreSQL")
                print(f"   Version: {version[:50]}...")
            
            # Create session factory
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            return self.engine
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()
        print("✅ Database connection closed")
    
    def execute_query(self, query):
        """Execute a SQL query and return results"""
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return result.fetchall()
    
    def get_table_count(self, schema, table):
        """Get row count for a table"""
        query = f"SELECT COUNT(*) FROM {schema}.{table}"
        result = self.execute_query(query)
        return result[0][0]

# Test connection function
def test_connection():
    """Test database connection"""
    print("="*50)
    print("Testing Database Connection")
    print("="*50)
    
    db = DatabaseConnection()
    engine = db.connect()
    
    # List schemas
    schemas_query = "SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('bronze', 'staging', 'marts')"
    schemas = db.execute_query(schemas_query)
    
    print(f"\n📊 Schemas found:")
    for schema in schemas:
        print(f"   - {schema[0]}")
    
    # List tables in bronze schema
    tables_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'bronze' ORDER BY table_name"
    tables = db.execute_query(tables_query)
    
    print(f"\n📋 Tables in bronze schema:")
    for table in tables:
        print(f"   - {table[0]}")
    
    db.close()
    print("\n" + "="*50)

if __name__ == "__main__":
    test_connection()