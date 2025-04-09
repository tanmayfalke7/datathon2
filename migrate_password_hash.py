import os
from dotenv import load_dotenv
import pymysql
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def migrate_password_hash():
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
            
        # Create SQLAlchemy engine
        engine = create_engine(database_url)
        
        # Connect to the database
        with engine.connect() as connection:
            # Alter the password_hash column
            connection.execute(text("""
                ALTER TABLE user 
                MODIFY COLUMN password_hash VARCHAR(255) NOT NULL
            """))
            connection.commit()
            
        print("Successfully updated password_hash column length to 255")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        raise

if __name__ == "__main__":
    migrate_password_hash() 