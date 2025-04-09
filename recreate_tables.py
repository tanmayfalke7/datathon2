import os
import sys
from dotenv import load_dotenv
from app01 import app, db

# Load environment variables
load_dotenv()

def recreate_tables():
    """Recreate all database tables"""
    try:
        with app.app_context():
            print("Dropping all tables...")
            db.drop_all()
            
            print("Creating all tables...")
            db.create_all()
            
            print("Tables recreated successfully!")
            return True
            
    except Exception as e:
        print(f"Error recreating tables: {e}")
        return False

if __name__ == "__main__":
    recreate_tables() 