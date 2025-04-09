import os
import sys
from dotenv import load_dotenv
from app01 import app, db, User

# Load environment variables
load_dotenv()

def add_test_user():
    """Add a test user to the database"""
    try:
        with app.app_context():
            # Check if user already exists
            username = "testuser"
            email = "test@example.com"
            
            if User.query.filter_by(username=username).first():
                print(f"User '{username}' already exists.")
                return
            
            # Create new user
            new_user = User(username=username, email=email)
            new_user.set_password("password123")
            
            # Add to database
            db.session.add(new_user)
            db.session.commit()
            
            print(f"Successfully added test user: {username}")
            print("Username: testuser")
            print("Password: password123")
            
    except Exception as e:
        print(f"Error adding test user: {e}")
        if 'db' in locals():
            db.session.rollback()
        sys.exit(1)

if __name__ == "__main__":
    add_test_user() 