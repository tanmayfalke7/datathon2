import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def update_course_urls():
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
            
        # Create SQLAlchemy engine
        engine = create_engine(database_url)
        
        # Course URLs mapping
        course_urls = {
            'Full Stack Development': 'https://www.coursera.org/specializations/full-stack-development',
            'Machine Learning': 'https://www.coursera.org/learn/machine-learning',
            'Data Analysis': 'https://www.coursera.org/professional-certificates/google-data-analytics'
        }
        
        # Connect to the database
        with engine.connect() as connection:
            # Update each course URL
            for course_name, url in course_urls.items():
                connection.execute(
                    text("UPDATE course SET url = :url WHERE name = :name"),
                    {"url": url, "name": course_name}
                )
            connection.commit()
            
            print("Successfully updated course URLs")
            
            # Verify the updates
            result = connection.execute(text("SELECT name, url FROM course"))
            courses = result.fetchall()
            
            print("\nUpdated Course URLs:")
            print("-" * 50)
            for course in courses:
                print(f"Course: {course[0]}")
                print(f"URL: {course[1]}")
                print("-" * 50)
            
    except Exception as e:
        print(f"Error updating course URLs: {str(e)}")
        raise

if __name__ == "__main__":
    update_course_urls() 