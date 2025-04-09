import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def check_course_urls():
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
            
        # Create SQLAlchemy engine
        engine = create_engine(database_url)
        
        # Connect to the database
        with engine.connect() as connection:
            # Query course URLs
            result = connection.execute(text("SELECT name, url FROM course"))
            courses = result.fetchall()
            
            print("\nCourse URLs:")
            print("-" * 50)
            for course in courses:
                print(f"Course: {course[0]}")
                print(f"URL: {course[1]}")
                print("-" * 50)
            
            # Count courses with and without URLs
            result = connection.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN url IS NOT NULL THEN 1 ELSE 0 END) as with_url,
                    SUM(CASE WHEN url IS NULL THEN 1 ELSE 0 END) as without_url
                FROM course
            """))
            stats = result.fetchone()
            
            print("\nURL Statistics:")
            print(f"Total courses: {stats[0]}")
            print(f"Courses with URL: {stats[1]}")
            print(f"Courses without URL: {stats[2]}")
            
    except Exception as e:
        print(f"Error checking course URLs: {str(e)}")
        raise

if __name__ == "__main__":
    check_course_urls() 