import os
import sys
from dotenv import load_dotenv
from app01 import db, Course
from sqlalchemy import text

# Load environment variables
load_dotenv()

def migrate_course_table():
    """Migrate the Course table to add new fields"""
    try:
        # Check if the new columns already exist
        with db.engine.connect() as connection:
            # Get column names
            result = connection.execute(text("SHOW COLUMNS FROM course"))
            columns = [row[0] for row in result]
            
            # Add new columns if they don't exist
            if 'url' not in columns:
                connection.execute(text("ALTER TABLE course ADD COLUMN url VARCHAR(255)"))
                print("Added 'url' column")
            
            if 'description' not in columns:
                connection.execute(text("ALTER TABLE course ADD COLUMN description TEXT"))
                print("Added 'description' column")
            
            if 'rating' not in columns:
                connection.execute(text("ALTER TABLE course ADD COLUMN rating FLOAT DEFAULT 0.0"))
                print("Added 'rating' column")
            
            if 'students_count' not in columns:
                connection.execute(text("ALTER TABLE course ADD COLUMN students_count INT DEFAULT 0"))
                print("Added 'students_count' column")
            
            if 'price' not in columns:
                connection.execute(text("ALTER TABLE course ADD COLUMN price FLOAT DEFAULT 0.0"))
                print("Added 'price' column")
            
            if 'instructor' not in columns:
                connection.execute(text("ALTER TABLE course ADD COLUMN instructor VARCHAR(100)"))
                print("Added 'instructor' column")
            
            if 'last_updated' not in columns:
                connection.execute(text("ALTER TABLE course ADD COLUMN last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
                print("Added 'last_updated' column")
            
            # Increase the size of the name column if needed
            connection.execute(text("ALTER TABLE course MODIFY COLUMN name VARCHAR(200)"))
            print("Updated 'name' column size")
            
            connection.commit()
        
        print("Course table migration completed successfully.")
        
    except Exception as e:
        print(f"Error migrating Course table: {e}")
        db.session.rollback()

if __name__ == "__main__":
    migrate_course_table() 