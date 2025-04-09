-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS certificate_dashboard;

-- Use the database
USE certificate_dashboard;

-- Create the user table
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create the course table
CREATE TABLE IF NOT EXISTS course (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(50) NOT NULL,
    duration INT NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    prerequisites VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create the user_certificate table
CREATE TABLE IF NOT EXISTS user_certificate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    course_id INT NOT NULL,
    completion_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    performance_score FLOAT,
    feedback TEXT,
    image_path VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE CASCADE
);

-- Insert sample courses
INSERT INTO course (name, domain, duration, difficulty, prerequisites) VALUES
('Python for Beginners', 'Programming', 20, 'Beginner', 'None'),
('Advanced Python Programming', 'Programming', 40, 'Advanced', 'Python for Beginners'),
('Machine Learning Fundamentals', 'AI/ML', 30, 'Intermediate', 'Python for Beginners'),
('Data Science Essentials', 'Data Science', 35, 'Intermediate', 'Python for Beginners'),
('Web Development with Flask', 'Web Development', 25, 'Intermediate', 'Python for Beginners'),
('Deep Learning Basics', 'AI/ML', 45, 'Advanced', 'Machine Learning Fundamentals'),
('SQL for Data Analysis', 'Data Science', 15, 'Beginner', 'None'),
('Full Stack Development', 'Web Development', 50, 'Advanced', 'Web Development with Flask');

-- Create indexes for better performance
CREATE INDEX idx_user_username ON user(username);
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_course_domain ON course(domain);
CREATE INDEX idx_course_difficulty ON course(difficulty);
CREATE INDEX idx_certificate_user ON user_certificate(user_id);
CREATE INDEX idx_certificate_course ON user_certificate(course_id); 