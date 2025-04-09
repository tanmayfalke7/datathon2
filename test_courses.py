import os
import sys
from dotenv import load_dotenv
from test_app import db, Course

# Load environment variables
load_dotenv()

def test_courses():
    """Test if courses are in the database"""
    try:
        # Query all courses
        courses = Course.query.all()
        print(f"Found {len(courses)} courses in the database")
        
        if len(courses) == 0:
            print("No courses found in the database. Please run add_courses.py first.")
            return
        
        # Print details of the first 5 courses
        for i, course in enumerate(courses[:5]):
            print(f"\nCourse {i+1}:")
            print(f"  Name: {course.name}")
            print(f"  Domain: {course.domain}")
            print(f"  Difficulty: {course.difficulty}")
            print(f"  Duration: {course.duration} hours")
            print(f"  Description: {course.description[:100]}...")
        
        if len(courses) > 5:
            print(f"\n... and {len(courses) - 5} more courses")
            
    except Exception as e:
        print(f"Error testing courses: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_courses() 