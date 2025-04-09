import pymysql
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

# Load environment variables
load_dotenv()

# Get database connection details from environment variables
db_url = os.environ.get('DATABASE_URL')

def parse_db_url(url):
    """Parse database URL and return connection parameters"""
    # Remove the mysql+pymysql:// prefix if present
    if url.startswith('mysql+pymysql://'):
        url = url.replace('mysql+pymysql://', 'mysql://')
    
    parsed = urlparse(url)
    return {
        'host': parsed.hostname,
        'user': parsed.username,
        'password': unquote(parsed.password) if parsed.password else '',
        'db': parsed.path.lstrip('/') if parsed.path else 'certificate_dashboard'
    }

def check_mysql_connection():
    try:
        # Parse the database URL
        db_params = parse_db_url(db_url)
        
        print(f"Attempting to connect to MySQL with these parameters:")
        print(f"Host: {db_params['host']}")
        print(f"User: {db_params['user']}")
        print(f"Database: {db_params['db']}")
        
        # First try to connect without specifying a database
        connection = pymysql.connect(
            host=db_params['host'],
            user=db_params['user'],
            password=db_params['password'],
            charset='utf8mb4'
        )
        
        print("Successfully connected to MySQL server!")
        
        # Check if database exists
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES LIKE %s", (db_params['db'],))
            result = cursor.fetchone()
            
            if not result:
                print(f"Database '{db_params['db']}' does not exist. Creating it now...")
                cursor.execute(f"CREATE DATABASE {db_params['db']}")
                print(f"Database '{db_params['db']}' created successfully!")
            else:
                print(f"Database '{db_params['db']}' already exists.")
        
        connection.close()
        return True
    
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure MySQL server is running")
        print("2. Verify your username and password are correct")
        print("3. Check if the MySQL server is accessible from your machine")
        print("4. Try connecting with a MySQL client like MySQL Workbench")
        return False

if __name__ == "__main__":
    check_mysql_connection() 