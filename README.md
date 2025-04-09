# Certificate Analysis Dashboard

A web application for analyzing and tracking certificates, with user authentication and image upload capabilities.

## Features

- User authentication (login/register)
- Certificate management with image upload
- Course recommendations based on user data
- Performance statistics and visualizations
- Dashboard for tracking progress

## Setup Instructions

### Prerequisites

- Python 3.8+
- MySQL Server
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd certificate_dashboard
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the MySQL database:
   ```
   # Log in to MySQL
   mysql -u root -p
   
   # Create the database
   CREATE DATABASE certificate_dashboard;
   
   # Exit MySQL
   exit;
   ```

5. Configure environment variables:
   - Copy the `.env.example` file to `.env` (or edit the existing `.env` file)
   - Update the database credentials and other settings as needed

6. Initialize the database:
   ```
   python app01.py
   ```
   This will create the necessary tables in the MySQL database.

### Migrating from SQLite (if applicable)

If you have an existing SQLite database and want to migrate to MySQL:

1. Make sure your MySQL database is set up and configured in the `.env` file
2. Run the migration script:
   ```
   python migrate_to_mysql.py
   ```
3. The script will transfer all data from the SQLite database to MySQL

### Running the Application

1. Start the Flask server:
   ```
   python app01.py
   ```

2. Access the application at http://localhost:5000

## Project Structure

- `app01.py`: Main application file
- `ml_model.py`: Machine learning model for recommendations
- `migrate_to_mysql.py`: Script for migrating data from SQLite to MySQL
- `templates/`: HTML templates
- `static/`: Static files (CSS, JavaScript, uploaded images)
- `requirements.txt`: Python dependencies

## Database Schema

The application uses MySQL with the following tables:

- `user`: Stores user information
- `course`: Stores course information
- `user_certificate`: Stores user certificates with image paths

## Environment Variables

The following environment variables can be configured in the `.env` file:

- `DATABASE_URL`: MySQL connection string
- `SECRET_KEY`: Flask secret key for session management
- `UPLOAD_FOLDER`: Directory for storing uploaded images
- `MAX_CONTENT_LENGTH`: Maximum file upload size in bytes

## License

[MIT License](LICENSE) 