import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def add_course_links():
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
            
        # Create SQLAlchemy engine
        engine = create_engine(database_url)
        
        # Connect to the database
        with engine.connect() as connection:
            # Check if URL column exists
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'course' AND column_name = 'url'
            """))
            
            column_exists = result.scalar() > 0
            
            # Add URL column if it doesn't exist
            if not column_exists:
                connection.execute(text("""
                    ALTER TABLE course 
                    ADD COLUMN url VARCHAR(255)
                """))
                print("Added URL column to course table")
            
            # Update course links
            # You can customize this dictionary with your course links
            course_links = {
                "Python for Beginners": "https://www.coursera.org/learn/python",
                "Data Science Fundamentals": "https://www.coursera.org/learn/data-science",
                "Machine Learning Basics": "https://www.coursera.org/learn/machine-learning",
                "Web Development with Flask": "https://www.coursera.org/learn/flask",
                "Advanced Python Programming": "https://www.coursera.org/learn/advanced-python",
                "Deep Learning Specialization": "https://www.coursera.org/specializations/deep-learning",
                "Full Stack Web Development": "https://www.coursera.org/specializations/full-stack",
                "Data Analysis with Python": "https://www.coursera.org/learn/data-analysis-python",
                "Natural Language Processing": "https://www.coursera.org/specializations/natural-language-processing",
                "Cloud Computing Fundamentals": "https://www.coursera.org/learn/cloud-computing"
            }
            
            # Update each course with its link
            for course_name, url in course_links.items():
                connection.execute(
                    text("UPDATE course SET url = :url WHERE name = :name"),
                    {"url": url, "name": course_name}
                )
            
            connection.commit()
            
        print("Successfully added course links to the database")
        
    except Exception as e:
        print(f"Error adding course links: {str(e)}")
        raise

if __name__ == "__main__":
    add_course_links() 