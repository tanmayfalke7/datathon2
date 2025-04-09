import os
import sys
from dotenv import load_dotenv
from app01 import app, db, User

# Load environment variables
load_dotenv()

def check_users():
    """Check if there are any users in the database"""
    try:
        with app.app_context():
            # Query all users
            users = User.query.all()
            
            print(f"Found {len(users)} users in the database:")
            
            if len(users) == 0:
                print("No users found in the database. Please register a new user.")
                return False
            
            # Print details of each user
            for i, user in enumerate(users, 1):
                print(f"\nUser {i}:")
                print(f"  ID: {user.id}")
                print(f"  Username: {user.username}")
                print(f"  Email: {user.email}")
                print(f"  Created at: {user.created_at}")
            
            return True
            
    except Exception as e:
        print(f"Error checking users: {e}")
        return False

if __name__ == "__main__":
    check_users() 