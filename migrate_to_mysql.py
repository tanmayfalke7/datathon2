#!/usr/bin/env python
"""
Migration script to transfer data from SQLite to MySQL
"""

import os
import sqlite3
import pymysql
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Get MySQL connection details from environment variables
db_url = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:password@localhost/certificate_dashboard')

# Parse the connection string
# Format: mysql+pymysql://username:password@host/database_name
parts = db_url.replace('mysql+pymysql://', '').split('@')
credentials = parts[0].split(':')
host_db = parts[1].split('/')

username = credentials[0]
password = credentials[1] if len(credentials) > 1 else ''
host = host_db[0]
database = host_db[1] if len(host_db) > 1 else 'certificate_dashboard'

# SQLite database path
sqlite_db_path = 'certificates.db'

def connect_to_sqlite():
    """Connect to the SQLite database"""
    if not os.path.exists(sqlite_db_path):
        print(f"SQLite database not found at {sqlite_db_path}")
        return None
    
    return sqlite3.connect(sqlite_db_path)

def connect_to_mysql():
    """Connect to the MySQL database"""
    try:
        connection = pymysql.connect(
            host=host,
            user=username,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def migrate_data():
    """Migrate data from SQLite to MySQL"""
    sqlite_conn = connect_to_sqlite()
    mysql_conn = connect_to_mysql()
    
    if not sqlite_conn or not mysql_conn:
        print("Failed to connect to one or both databases")
        return
    
    try:
        # Create cursors
        sqlite_cursor = sqlite_conn.cursor()
        mysql_cursor = mysql_conn.cursor()
        
        # Migrate users
        print("Migrating users...")
        sqlite_cursor.execute("SELECT * FROM user")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            # Convert datetime objects to strings
            created_at = user['created_at']
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            mysql_cursor.execute(
                "INSERT INTO user (id, username, email, password_hash, created_at) VALUES (%s, %s, %s, %s, %s)",
                (user['id'], user['username'], user['email'], user['password_hash'], created_at)
            )
        
        # Migrate courses
        print("Migrating courses...")
        sqlite_cursor.execute("SELECT * FROM course")
        courses = sqlite_cursor.fetchall()
        
        for course in courses:
            # Convert datetime objects to strings
            created_at = course['created_at']
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            mysql_cursor.execute(
                "INSERT INTO course (id, name, domain, duration, difficulty, prerequisites, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (course['id'], course['name'], course['domain'], course['duration'], course['difficulty'], course['prerequisites'], created_at)
            )
        
        # Migrate user certificates
        print("Migrating user certificates...")
        sqlite_cursor.execute("SELECT * FROM user_certificate")
        certificates = sqlite_cursor.fetchall()
        
        for cert in certificates:
            # Convert datetime objects to strings
            completion_date = cert['completion_date']
            if isinstance(completion_date, str):
                completion_date = datetime.fromisoformat(completion_date.replace('Z', '+00:00'))
            
            mysql_cursor.execute(
                "INSERT INTO user_certificate (id, user_id, course_id, completion_date, performance_score, feedback, image_path) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (cert['id'], cert['user_id'], cert['course_id'], completion_date, cert['performance_score'], cert['feedback'], cert['image_path'])
            )
        
        # Commit the transaction
        mysql_conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        mysql_conn.rollback()
    
    finally:
        # Close connections
        sqlite_conn.close()
        mysql_conn.close()

if __name__ == "__main__":
    print("Starting migration from SQLite to MySQL...")
    migrate_data() 