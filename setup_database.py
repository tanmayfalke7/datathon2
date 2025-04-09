import os
import sys
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Set up the MySQL database and tables"""
    try:
        # Parse database URL
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            print("Error: DATABASE_URL not found in environment variables")
            sys.exit(1)
            
        # Extract connection details from URL
        # Format: mysql+pymysql://username:password@host/database
        parts = db_url.replace('mysql+pymysql://', '').split('@')
        user_pass = parts[0].split(':')
        host_db = parts[1].split('/')
        
        username = user_pass[0]
        password = user_pass[1]
        host = host_db[0]
        database = host_db[1]
        
        # Connect to MySQL server
        connection = pymysql.connect(
            host=host,
            user=username,
            password=password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        try:
            with connection.cursor() as cursor:
                # Create database if it doesn't exist
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
                print(f"Database '{database}' created or already exists")
                
                # Use the database
                cursor.execute(f"USE {database}")
                
                # Create Course table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS course (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        domain VARCHAR(50) NOT NULL,
                        duration INT NOT NULL,
                        difficulty VARCHAR(20) NOT NULL,
                        prerequisites VARCHAR(200),
                        url VARCHAR(255),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        description TEXT,
                        rating FLOAT DEFAULT 0.0,
                        students_count INT DEFAULT 0,
                        price FLOAT DEFAULT 0.0,
                        instructor VARCHAR(100),
                        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                print("Course table created or already exists")
                
                # Create User table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(80) NOT NULL UNIQUE,
                        email VARCHAR(120) NOT NULL UNIQUE,
                        password_hash VARCHAR(128) NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("User table created or already exists")
                
                # Create UserCertificate table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_certificate (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        course_id INT NOT NULL,
                        completion_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        performance_score FLOAT,
                        feedback TEXT,
                        image_path VARCHAR(255),
                        FOREIGN KEY (user_id) REFERENCES user(id),
                        FOREIGN KEY (course_id) REFERENCES course(id)
                    )
                """)
                print("UserCertificate table created or already exists")
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_course_domain ON course(domain)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_course_difficulty ON course(difficulty)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_certificate_user ON user_certificate(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_certificate_course ON user_certificate(course_id)")
                print("Indexes created or already exist")
                
        finally:
            connection.close()
            
        print("Database setup completed successfully")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database() 