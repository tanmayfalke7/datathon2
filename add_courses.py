import os
import sys
from dotenv import load_dotenv
from app01 import app, db, Course
from datetime import datetime

# Load environment variables
load_dotenv()

def add_courses():
    courses_data = [
        # Data Analysis - Intermediate
        {
            'name': 'Google Data Analytics Professional Certificate',
            'domain': 'Data Analysis',
            'duration': 180,  # 6 months in hours
            'difficulty': 'Intermediate',
            'prerequisites': 'Basic computer skills',
            'description': 'Learn data analysis using SQL, Tableau, R, and data cleaning techniques.',
            'instructor': 'Google',
            'rating': 4.8,
            'students_count': 50000,
            'price': 49.0,
            'url': 'https://www.coursera.org/professional-certificates/google-data-analytics'
        },
        {
            'name': 'Data Analysis with Python',
            'domain': 'Data Analysis',
            'duration': 10,
            'difficulty': 'Intermediate',
            'prerequisites': 'Basic Python knowledge',
            'description': 'Master data analysis using Pandas, NumPy, and Matplotlib.',
            'instructor': 'freeCodeCamp',
            'rating': 4.7,
            'students_count': 75000,
            'price': 0.0,
            'url': 'https://www.freecodecamp.org/learn/data-analysis-with-python/'
        },
        {
            'name': 'Data Science MicroMasters',
            'domain': 'Data Analysis',
            'duration': 720,  # 10 months in hours
            'difficulty': 'Intermediate',
            'prerequisites': 'Basic programming knowledge',
            'description': 'Comprehensive data science program covering Python, probability, and data visualization.',
            'instructor': 'UC San Diego',
            'rating': 4.9,
            'students_count': 25000,
            'price': 1200.0,
            'url': 'https://www.edx.org/micromasters/uc-san-diegox-data-science'
        },
        {
            'name': 'SQL for Data Science',
            'domain': 'Data Analysis',
            'duration': 14,
            'difficulty': 'Intermediate',
            'prerequisites': 'Basic database knowledge',
            'description': 'Learn SQL for data science applications and database querying.',
            'instructor': 'UC Davis',
            'rating': 4.6,
            'students_count': 60000,
            'price': 49.0,
            'url': 'https://www.coursera.org/learn/sql-for-data-science'
        },
        {
            'name': 'Data Analysis with Pandas and Python',
            'domain': 'Data Analysis',
            'duration': 9,
            'difficulty': 'Intermediate',
            'prerequisites': 'Python basics',
            'description': 'Master data analysis using Pandas, including data cleaning and EDA.',
            'instructor': 'Udemy Instructor',
            'rating': 4.5,
            'students_count': 45000,
            'price': 29.99,
            'url': 'https://www.udemy.com/course/data-analysis-with-pandas/'
        },
        # Data Analysis - Advanced
        {
            'name': 'Advanced Data Analysis Nanodegree',
            'domain': 'Data Analysis',
            'duration': 216,  # 3 months in hours
            'difficulty': 'Advanced',
            'prerequisites': 'Intermediate data analysis skills',
            'description': 'Advanced data analysis covering A/B testing and predictive modeling.',
            'instructor': 'Udacity',
            'rating': 4.7,
            'students_count': 30000,
            'price': 999.0,
            'url': 'https://www.udacity.com/course/data-analyst-nanodegree--nd002'
        },
        {
            'name': 'Data Science Specialization',
            'domain': 'Data Analysis',
            'duration': 792,  # 11 months in hours
            'difficulty': 'Advanced',
            'prerequisites': 'Programming and statistics background',
            'description': 'Comprehensive data science program covering R, machine learning, and regression.',
            'instructor': 'Johns Hopkins University',
            'rating': 4.8,
            'students_count': 40000,
            'price': 999.0,
            'url': 'https://www.coursera.org/specializations/jhu-data-science'
        },
        {
            'name': 'Data Engineering with Google Cloud',
            'domain': 'Data Analysis',
            'duration': 160,  # 1 month in hours
            'difficulty': 'Advanced',
            'prerequisites': 'Basic cloud computing knowledge',
            'description': 'Learn data engineering using BigQuery and ETL pipelines.',
            'instructor': 'Google',
            'rating': 4.6,
            'students_count': 35000,
            'price': 49.0,
            'url': 'https://www.coursera.org/professional-certificates/gcp-data-engineering'
        },
        # Full-Stack Development - Intermediate
        {
            'name': 'The Web Developer Bootcamp 2024',
            'domain': 'Full-Stack Development',
            'duration': 65,
            'difficulty': 'Intermediate',
            'prerequisites': 'Basic computer skills',
            'description': 'Comprehensive web development bootcamp covering HTML, CSS, JavaScript, and Node.js.',
            'instructor': 'Colt Steele',
            'rating': 4.7,
            'students_count': 100000,
            'price': 49.99,
            'url': 'https://www.udemy.com/course/the-web-developer-bootcamp/'
        },
        {
            'name': 'Full-Stack Open',
            'domain': 'Full-Stack Development',
            'duration': 432,  # 6 months in hours
            'difficulty': 'Intermediate',
            'prerequisites': 'Basic programming knowledge',
            'description': 'Learn full-stack development with React, Node.js, and MongoDB.',
            'instructor': 'University of Helsinki',
            'rating': 4.8,
            'students_count': 80000,
            'price': 0.0,
            'url': 'https://fullstackopen.com/en/'
        },
        {
            'name': 'Meta Back-End Developer Professional Certificate',
            'domain': 'Full-Stack Development',
            'duration': 576,  # 8 months in hours
            'difficulty': 'Intermediate',
            'prerequisites': 'Basic programming knowledge',
            'description': 'Learn back-end development with Python, Django, and APIs.',
            'instructor': 'Meta',
            'rating': 4.6,
            'students_count': 45000,
            'price': 49.0,
            'url': 'https://www.coursera.org/professional-certificates/meta-back-end-developer'
        },
        {
            'name': 'JavaScript Algorithms and Data Structures',
            'domain': 'Full-Stack Development',
            'duration': 30,
            'difficulty': 'Intermediate',
            'prerequisites': 'Basic JavaScript knowledge',
            'description': 'Master JavaScript algorithms, data structures, and OOP concepts.',
            'instructor': 'freeCodeCamp',
            'rating': 4.7,
            'students_count': 90000,
            'price': 0.0,
            'url': 'https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/'
        },
        {
            'name': 'Angular - The Complete Guide',
            'domain': 'Full-Stack Development',
            'duration': 35,
            'difficulty': 'Intermediate',
            'prerequisites': 'Basic JavaScript knowledge',
            'description': 'Comprehensive guide to Angular, TypeScript, and Firebase.',
            'instructor': 'Maximilian Schwarzmüller',
            'rating': 4.8,
            'students_count': 70000,
            'price': 39.99,
            'url': 'https://www.udemy.com/course/the-complete-guide-to-angular-2/'
        },
        # Full-Stack Development - Advanced
        {
            'name': 'Full Stack Web Development with React Specialization',
            'domain': 'Full-Stack Development',
            'duration': 216,  # 3 months in hours
            'difficulty': 'Advanced',
            'prerequisites': 'Intermediate web development skills',
            'description': 'Advanced full-stack development using MERN stack and REST APIs.',
            'instructor': 'HKUST',
            'rating': 4.7,
            'students_count': 35000,
            'price': 499.0,
            'url': 'https://www.coursera.org/specializations/full-stack-react'
        },
        {
            'name': 'The Complete 2024 Web Development Bootcamp',
            'domain': 'Full-Stack Development',
            'duration': 55,
            'difficulty': 'Advanced',
            'prerequisites': 'Basic programming knowledge',
            'description': 'Comprehensive web development bootcamp covering React, Node.js, and GraphQL.',
            'instructor': 'Dr. Angela Yu',
            'rating': 4.8,
            'students_count': 85000,
            'price': 49.99,
            'url': 'https://www.udemy.com/course/the-complete-web-development-bootcamp/'
        },
        {
            'name': 'Advanced Web Developer Bootcamp',
            'domain': 'Full-Stack Development',
            'duration': 288,  # 4 months in hours
            'difficulty': 'Advanced',
            'prerequisites': 'Intermediate web development skills',
            'description': 'Advanced web development covering Progressive Web Apps and web performance.',
            'instructor': 'Udacity',
            'rating': 4.6,
            'students_count': 30000,
            'price': 999.0,
            'url': 'https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044'
        },
        # Machine Learning - Intermediate
        {
            'name': 'Machine Learning A-Z',
            'domain': 'Machine Learning',
            'duration': 44,
            'difficulty': 'Intermediate',
            'prerequisites': 'Basic Python knowledge',
            'description': 'Comprehensive machine learning course covering Python, Scikit-learn, and TensorFlow.',
            'instructor': 'Kirill Eremenko',
            'rating': 4.7,
            'students_count': 95000,
            'price': 49.99,
            'url': 'https://www.udemy.com/course/machinelearning/'
        },
        {
            'name': 'Deep Learning Specialization',
            'domain': 'Machine Learning',
            'duration': 360,  # 5 months in hours
            'difficulty': 'Intermediate',
            'prerequisites': 'Basic machine learning knowledge',
            'description': 'Comprehensive deep learning program covering neural networks, CNNs, and RNNs.',
            'instructor': 'Andrew Ng',
            'rating': 4.8,
            'students_count': 60000,
            'price': 499.0,
            'url': 'https://www.coursera.org/specializations/deep-learning'
        },
        # Machine Learning - Advanced
        {
            'name': 'Advanced Machine Learning with TensorFlow on GCP',
            'domain': 'Machine Learning',
            'duration': 160,  # 1 month in hours
            'difficulty': 'Advanced',
            'prerequisites': 'Intermediate machine learning knowledge',
            'description': 'Advanced machine learning using TensorFlow, AutoML, and Google Cloud Platform.',
            'instructor': 'Google',
            'rating': 4.7,
            'students_count': 40000,
            'price': 49.0,
            'url': 'https://www.coursera.org/specializations/advanced-machine-learning-tensorflow-gcp'
        },
        {
            'name': 'MIT Deep Learning for Self-Driving Cars',
            'domain': 'Machine Learning',
            'duration': 0,  # Self-paced
            'difficulty': 'Advanced',
            'prerequisites': 'Advanced machine learning knowledge',
            'description': 'Advanced deep learning concepts for autonomous vehicles and reinforcement learning.',
            'instructor': 'MIT',
            'rating': 4.9,
            'students_count': 25000,
            'price': 0.0,
            'url': 'https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf'
        }
    ]

    try:
        for course_data in courses_data:
            course = Course(
                name=course_data['name'],
                domain=course_data['domain'],
                duration=course_data['duration'],
                difficulty=course_data['difficulty'],
                prerequisites=course_data['prerequisites'],
                description=course_data['description'],
                instructor=course_data['instructor'],
                rating=course_data['rating'],
                students_count=course_data['students_count'],
                price=course_data['price'],
                url=course_data['url'],
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            db.session.add(course)
        
        db.session.commit()
        print("Successfully added all courses to the database!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding courses: {str(e)}")

if __name__ == '__main__':
    add_courses() 