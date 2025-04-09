# Adding Courses to the Certificate Dashboard

This guide explains how to add the provided courses to your Certificate Dashboard database.

## Prerequisites

- MySQL database set up and running
- Python environment with required packages installed
- `.env` file configured with database connection details

## Steps to Add Courses

1. **Migrate the Course Table**

   First, run the migration script to add the new fields to the Course table:

   ```bash
   python migrate_course_table.py
   ```

   This will add the following fields to the Course table:
   - `url`: Link to the course
   - `description`: Course description
   - `rating`: Course rating (0-5)
   - `students_count`: Number of students enrolled
   - `price`: Course price
   - `instructor`: Course instructor name
   - `last_updated`: Timestamp of last update

2. **Add Courses to the Database**

   Run the script to add the courses to the database:

   ```bash
   python add_courses.py
   ```

   This script will:
   - Check if courses already exist in the database
   - Add only new courses that don't already exist
   - Display a summary of how many courses were added

## Course Categories

The courses are organized into three main categories:

1. **Full Stack Development**
   - Web development bootcamps
   - JavaScript courses
   - React and Node.js courses

2. **Machine Learning**
   - AI and ML fundamentals
   - Deep learning
   - Data science with Python

3. **Data Analysis**
   - Data science with R
   - Python for data analysis
   - SQL and Tableau

## Troubleshooting

If you encounter any issues:

1. **Database Connection Errors**
   - Verify your `.env` file has the correct database connection string
   - Ensure MySQL is running and accessible

2. **Migration Errors**
   - Check if you have the necessary permissions to alter tables
   - Verify the database user has ALTER TABLE privileges

3. **Course Addition Errors**
   - Check the console output for specific error messages
   - Verify the Course model in `app01.py` matches the database schema

## Next Steps

After adding the courses:

1. Restart your Flask application
2. Test the recommendation system by uploading a certificate
3. Verify that course recommendations are displayed correctly

For any questions or issues, please refer to the main README.md file or contact the development team. 