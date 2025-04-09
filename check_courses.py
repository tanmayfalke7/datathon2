import os
import sys
from dotenv import load_dotenv
from app01 import app, db, Course

# Load environment variables
load_dotenv()

def check_courses():
    """Check if there are any courses in the database"""
    try:
        with app.app_context():
            # Query all courses
            courses = Course.query.all()
            
            print(f"Found {len(courses)} courses in the database:")
            
            if len(courses) == 0:
                print("No courses found in the database. Please run add_courses.py to add sample courses.")
                return False
            
            # Print details of each course
            for i, course in enumerate(courses, 1):
                print(f"\nCourse {i}:")
                print(f"  ID: {course.id}")
                print(f"  Name: {course.name}")
                print(f"  Domain: {course.domain}")
                print(f"  Difficulty: {course.difficulty}")
                print(f"  Duration: {course.duration} hours")
                if course.description:
                    print(f"  Description: {course.description[:100]}...")
            
            return True
            
    except Exception as e:
        print(f"Error checking courses: {e}")
        return False

if __name__ == "__main__":
    check_courses() 