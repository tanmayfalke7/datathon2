from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import uuid
from dotenv import load_dotenv
import secrets
import numpy as np
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import base64
import random

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Additional recommended settings
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 3600,
    'pool_size': 10,
    'max_overflow': 20
}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in hours
    difficulty = db.Column(db.String(20), nullable=False)
    prerequisites = db.Column(db.String(200))
    description = db.Column(db.Text)
    instructor = db.Column(db.String(100))
    rating = db.Column(db.Float, default=0.0)
    students_count = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0.0)
    url = db.Column(db.String(255))  # URL to the course
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserCertificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    completion_date = db.Column(db.DateTime, default=datetime.utcnow)
    performance_score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    image_path = db.Column(db.String(255))  # Path to the certificate image

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    certificates = db.relationship('UserCertificate', backref='user', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ML Model for Course Recommendations
def train_recommendation_model():
    # Get all certificates with their associated courses
    certificates = UserCertificate.query.all()
    
    if not certificates:
        # If no certificates exist, return a default model
        return None
    
    # Prepare data for training
    X = []
    y = []
    
    for cert in certificates:
        course = Course.query.get(cert.course_id)
        if course:
            # Features: course domain, duration, difficulty
            features = [
                1 if course.domain == 'Programming' else 0,
                1 if course.domain == 'AI/ML' else 0,
                1 if course.domain == 'Data Science' else 0,
                1 if course.domain == 'Web Development' else 0,
                course.duration,
                1 if course.difficulty == 'Beginner' else 0,
                1 if course.difficulty == 'Intermediate' else 0,
                1 if course.difficulty == 'Advanced' else 0
            ]
            X.append(features)
            y.append(cert.course_id)
    
    if len(X) < 2:
        # Not enough data to train a model
        return None
    
    # Convert to numpy arrays
    X = np.array(X)
    y = np.array(y)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)
    
    # Save the model and scaler
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/course_recommender.joblib')
    joblib.dump(scaler, 'models/scaler.joblib')
    
    return model, scaler

def get_course_recommendations(user_data):
    """Get course recommendations based on user's completed course"""
    try:
        print(f"Getting recommendations for user data: {user_data}")
        
        # Get the domain and difficulty of the completed course
        domain = user_data.get('domain', 'Programming')  # Default to Programming if not specified
        difficulty = user_data.get('difficulty', 'Beginner')  # Default to Beginner if not specified
        
        print(f"Using domain: {domain}, difficulty: {difficulty}")
        
        # Get courses in the same domain
        domain_courses = Course.query.filter_by(domain=domain).all()
        print(f"Found {len(domain_courses)} courses in domain {domain}")
        
        if not domain_courses:
            print(f"No courses found in domain {domain}, using default recommendations")
            return get_default_recommendations(user_data)
        
        # Get user's previously completed courses
        user_id = user_data.get('user_id')
        completed_courses = []
        if user_id:
            completed_certificates = UserCertificate.query.filter_by(user_id=user_id).all()
            completed_courses = [cert.course_id for cert in completed_certificates]
            print(f"User has completed {len(completed_courses)} courses")
        
        # Sort courses by rating and students count, but exclude completed courses
        available_courses = [c for c in domain_courses if c.id not in completed_courses]
        if not available_courses:
            print("No available courses in domain after excluding completed ones")
            return get_default_recommendations(user_data)
            
        # Sort by rating and students count
        sorted_courses = sorted(
            available_courses,
            key=lambda x: (x.rating * 0.7 + (x.students_count / 100000) * 0.3),
            reverse=True
        )
        
        recommendations = []
        
        # If the completed course was intermediate, recommend:
        # 1. One intermediate course in the same domain
        # 2. One advanced course in the same domain
        if difficulty.lower() == 'intermediate':
            print("Finding intermediate and advanced course recommendations")
            # Find intermediate courses (excluding completed ones)
            intermediate_courses = [c for c in sorted_courses 
                                 if c.difficulty.lower() == 'intermediate']
            
            # Find advanced courses
            advanced_courses = [c for c in sorted_courses 
                              if c.difficulty.lower() == 'advanced']
            
            print(f"Found {len(intermediate_courses)} intermediate courses and {len(advanced_courses)} advanced courses")
            
            # Add one intermediate course if available (randomly select from top 3)
            if intermediate_courses:
                top_intermediate = intermediate_courses[:min(3, len(intermediate_courses))]
                selected_course = random.choice(top_intermediate)
                recommendations.append({
                    'id': selected_course.id,
                    'name': selected_course.name,
                    'domain': selected_course.domain,
                    'duration': selected_course.duration,
                    'difficulty': selected_course.difficulty,
                    'prerequisites': selected_course.prerequisites,
                    'description': selected_course.description,
                    'instructor': selected_course.instructor,
                    'rating': selected_course.rating,
                    'url': selected_course.url
                })
            
            # Add one advanced course if available (randomly select from top 3)
            if advanced_courses:
                top_advanced = advanced_courses[:min(3, len(advanced_courses))]
                selected_course = random.choice(top_advanced)
                recommendations.append({
                    'id': selected_course.id,
                    'name': selected_course.name,
                    'domain': selected_course.domain,
                    'duration': selected_course.duration,
                    'difficulty': selected_course.difficulty,
                    'prerequisites': selected_course.prerequisites,
                    'description': selected_course.description,
                    'instructor': selected_course.instructor,
                    'rating': selected_course.rating,
                    'url': selected_course.url
                })
        
        # If the completed course was advanced, recommend:
        # 1. One advanced course in the same domain
        # 2. One advanced course in a related domain
        elif difficulty.lower() == 'advanced':
            print("Finding advanced course recommendations")
            # Find other advanced courses in the same domain
            same_domain_advanced = [c for c in sorted_courses 
                                  if c.difficulty.lower() == 'advanced']
            
            # Get advanced courses from related domains
            related_domains = {
                'Data Analysis': ['Machine Learning', 'Full-Stack Development'],
                'Full-Stack Development': ['Data Analysis', 'Machine Learning'],
                'Machine Learning': ['Data Analysis', 'Full-Stack Development']
            }
            
            related_domain_courses = []
            if domain in related_domains:
                for related_domain in related_domains[domain]:
                    related_courses = Course.query.filter_by(
                        domain=related_domain,
                        difficulty='Advanced'
                    ).all()
                    # Filter out completed courses
                    related_courses = [c for c in related_courses if c.id not in completed_courses]
                    related_domain_courses.extend(related_courses)
            
            print(f"Found {len(same_domain_advanced)} advanced courses in same domain and {len(related_domain_courses)} in related domains")
            
            # Sort related domain courses
            related_domain_courses.sort(
                key=lambda x: (x.rating * 0.7 + (x.students_count / 100000) * 0.3),
                reverse=True
            )
            
            # Add one advanced course from the same domain if available (randomly select from top 3)
            if same_domain_advanced:
                top_same_domain = same_domain_advanced[:min(3, len(same_domain_advanced))]
                selected_course = random.choice(top_same_domain)
                recommendations.append({
                    'id': selected_course.id,
                    'name': selected_course.name,
                    'domain': selected_course.domain,
                    'duration': selected_course.duration,
                    'difficulty': selected_course.difficulty,
                    'prerequisites': selected_course.prerequisites,
                    'description': selected_course.description,
                    'instructor': selected_course.instructor,
                    'rating': selected_course.rating,
                    'url': selected_course.url
                })
            
            # Add one advanced course from a related domain if available (randomly select from top 3)
            if related_domain_courses:
                top_related = related_domain_courses[:min(3, len(related_domain_courses))]
                selected_course = random.choice(top_related)
                recommendations.append({
                    'id': selected_course.id,
                    'name': selected_course.name,
                    'domain': selected_course.domain,
                    'duration': selected_course.duration,
                    'difficulty': selected_course.difficulty,
                    'prerequisites': selected_course.prerequisites,
                    'description': selected_course.description,
                    'instructor': selected_course.instructor,
                    'rating': selected_course.rating,
                    'url': selected_course.url
                })
        
        # If the completed course was beginner, recommend:
        # 1. One intermediate course in the same domain
        # 2. One beginner course in a related domain
        else:  # beginner
            print("Finding intermediate and beginner course recommendations")
            # Find intermediate courses in the same domain
            intermediate_courses = [c for c in sorted_courses 
                                 if c.difficulty.lower() == 'intermediate']
            
            # Get beginner courses from related domains
            related_domains = {
                'Data Analysis': ['Machine Learning', 'Full-Stack Development'],
                'Full-Stack Development': ['Data Analysis', 'Machine Learning'],
                'Machine Learning': ['Data Analysis', 'Full-Stack Development']
            }
            
            related_domain_courses = []
            if domain in related_domains:
                for related_domain in related_domains[domain]:
                    related_courses = Course.query.filter_by(
                        domain=related_domain,
                        difficulty='Beginner'
                    ).all()
                    # Filter out completed courses
                    related_courses = [c for c in related_courses if c.id not in completed_courses]
                    related_domain_courses.extend(related_courses)
            
            print(f"Found {len(intermediate_courses)} intermediate courses and {len(related_domain_courses)} beginner courses in related domains")
            
            # Sort related domain courses
            related_domain_courses.sort(
                key=lambda x: (x.rating * 0.7 + (x.students_count / 100000) * 0.3),
                reverse=True
            )
            
            # Add one intermediate course if available (randomly select from top 3)
            if intermediate_courses:
                top_intermediate = intermediate_courses[:min(3, len(intermediate_courses))]
                selected_course = random.choice(top_intermediate)
                recommendations.append({
                    'id': selected_course.id,
                    'name': selected_course.name,
                    'domain': selected_course.domain,
                    'duration': selected_course.duration,
                    'difficulty': selected_course.difficulty,
                    'prerequisites': selected_course.prerequisites,
                    'description': selected_course.description,
                    'instructor': selected_course.instructor,
                    'rating': selected_course.rating,
                    'url': selected_course.url
                })
            
            # Add one beginner course from a related domain if available (randomly select from top 3)
            if related_domain_courses:
                top_related = related_domain_courses[:min(3, len(related_domain_courses))]
                selected_course = random.choice(top_related)
                recommendations.append({
                    'id': selected_course.id,
                    'name': selected_course.name,
                    'domain': selected_course.domain,
                    'duration': selected_course.duration,
                    'difficulty': selected_course.difficulty,
                    'prerequisites': selected_course.prerequisites,
                    'description': selected_course.description,
                    'instructor': selected_course.instructor,
                    'rating': selected_course.rating,
                    'url': selected_course.url
                })
        
        # If no recommendations were found, use default recommendations
        if not recommendations:
            print("No specific recommendations found, using default recommendations")
            return get_default_recommendations(user_data)
        
        print(f"Returning {len(recommendations)} recommendations")
        return recommendations
        
    except Exception as e:
        print(f"Error getting recommendations: {str(e)}")
        return get_default_recommendations(user_data)

def get_default_recommendations(user_data):
    """Get default course recommendations when no specific recommendations are available"""
    try:
        print("Getting default recommendations")
        
        # Get user's previously completed courses
        user_id = user_data.get('user_id')
        completed_courses = []
        if user_id:
            completed_certificates = UserCertificate.query.filter_by(user_id=user_id).all()
            completed_courses = [cert.course_id for cert in completed_certificates]
            print(f"User has completed {len(completed_courses)} courses")
        
        # Get all courses excluding completed ones
        all_courses = Course.query.all()
        available_courses = [c for c in all_courses if c.id not in completed_courses]
        
        if not available_courses:
            print("No available courses for default recommendations")
            return []
        
        # Sort by rating and students count
        sorted_courses = sorted(
            available_courses,
            key=lambda x: (x.rating * 0.7 + (x.students_count / 100000) * 0.3),
            reverse=True
        )
        
        # Get top 5 courses
        top_courses = sorted_courses[:min(5, len(sorted_courses))]
        
        # Randomly select 2 courses from the top 5
        selected_courses = random.sample(top_courses, min(2, len(top_courses)))
        
        recommendations = []
        for course in selected_courses:
            recommendations.append({
                'id': course.id,
                'name': course.name,
                'domain': course.domain,
                'duration': course.duration,
                'difficulty': course.difficulty,
                'prerequisites': course.prerequisites,
                'description': course.description,
                'instructor': course.instructor,
                'rating': course.rating,
                'url': course.url
            })
        
        print(f"Returning {len(recommendations)} default recommendations")
        return recommendations
        
    except Exception as e:
        print(f"Error getting default recommendations: {str(e)}")
        return []

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/courses', methods=['GET'])
@login_required
def get_courses():
    courses = Course.query.all()
    print(f"API: Returning {len(courses)} courses")
    return jsonify([{
        'id': course.id,
        'name': course.name,
        'domain': course.domain,
        'duration': course.duration,
        'difficulty': course.difficulty,
        'prerequisites': course.prerequisites,
        'description': course.description,
        'rating': course.rating,
        'instructor': course.instructor,
        'url': course.url  # Add URL to the response
    } for course in courses])

@app.route('/api/recommendations/<int:course_id>', methods=['GET'])
@login_required
def get_recommendations_by_course(course_id):
    course = Course.query.get_or_404(course_id)
    user_data = {
        'domain': course.domain,
        'duration': course.duration,
        'difficulty': course.difficulty
    }
    recommendations = get_course_recommendations(user_data)
    return jsonify(recommendations)

@app.route('/api/recommendations', methods=['POST'])
@login_required
def get_recommendations():
    try:
        data = request.json
        print(f"Received recommendation request with data: {data}")
        
        if not data:
            print("No data provided in request")
            return jsonify([])
            
        recommendations = get_course_recommendations(data)
        print(f"Returning {len(recommendations)} recommendations")
        return jsonify(recommendations)
    except Exception as e:
        print(f"Error in recommendations API: {str(e)}")
        return jsonify([])

@app.route('/api/certificates', methods=['POST'])
@login_required
def add_certificate():
    try:
        data = request.form
        print("Received form data:", data)
        
        # Handle image upload
        image_path = None
        if 'certificate_image' not in request.files:
            print("No certificate_image in request.files")
            return jsonify({'error': 'No file uploaded'}), 400
            
        file = request.files['certificate_image']
        if not file or not file.filename:
            print("No selected file or empty filename")
            return jsonify({'error': 'No file selected'}), 400
            
        # Generate a unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Ensure upload directory exists
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_path, exist_ok=True)
        
        try:
            file_path = os.path.join(upload_path, unique_filename)
            print(f"Saving file to: {file_path}")
            file.save(file_path)
            image_path = os.path.join('uploads', unique_filename)
            print(f"File saved successfully at {file_path}")
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
        
        if 'course_id' not in data:
            print("No course_id in form data")
            return jsonify({'error': 'Course ID is required'}), 400
            
        # Create new certificate
        new_certificate = UserCertificate(
            user_id=current_user.id,
            course_id=data['course_id'],
            performance_score=data.get('performance_score'),
            feedback=data.get('feedback'),
            image_path=image_path
        )
        
        try:
            db.session.add(new_certificate)
            db.session.commit()
            print(f"Certificate added successfully for user {current_user.id}")
        except Exception as e:
            print(f"Database error: {str(e)}")
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        
        # Get course details for recommendations
        course = Course.query.get(data['course_id'])
        
        # Get recommendations based on the uploaded certificate
        user_data = {
            'domain': course.domain,
            'duration': course.duration,
            'difficulty': course.difficulty
        }
        
        recommendations = get_course_recommendations(user_data)
        
        return jsonify({
            'message': 'Certificate added successfully',
            'recommendations': recommendations
        })
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/statistics/<int:user_id>')
@login_required
def get_statistics(user_id):
    # Ensure users can only access their own statistics
    if current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    certificates = UserCertificate.query.filter_by(user_id=user_id).all()
    stats = {
        'total_courses': len(certificates),
        'domains': {},
        'difficulty_levels': {},
        'average_score': 0,
        'certificates': []  # Add certificates data for progress chart
    }
    
    if certificates:
        total_score = 0
        for cert in certificates:
            course = Course.query.get(cert.course_id)
            stats['domains'][course.domain] = stats['domains'].get(course.domain, 0) + 1
            stats['difficulty_levels'][course.difficulty] = stats['difficulty_levels'].get(course.difficulty, 0) + 1
            if cert.performance_score:
                total_score += cert.performance_score
                
            # Add certificate data for progress chart
            stats['certificates'].append({
                'completion_date': cert.completion_date.isoformat(),
                'course_name': course.name,
                'domain': course.domain,
                'difficulty': course.difficulty,
                'performance_score': cert.performance_score
            })
        
        stats['average_score'] = total_score / len(certificates)
    
    return jsonify(stats)

@app.route('/api/certificates/<int:user_id>')
@login_required
def get_user_certificates(user_id):
    # Ensure users can only access their own certificates
    if current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    certificates = UserCertificate.query.filter_by(user_id=user_id).all()
    result = []
    
    for cert in certificates:
        course = Course.query.get(cert.course_id)
        result.append({
            'id': cert.id,
            'course_id': cert.course_id,
            'course_name': course.name,
            'domain': course.domain,
            'duration': course.duration,
            'difficulty': course.difficulty,
            'performance_score': cert.performance_score,
            'completion_date': cert.completion_date.isoformat(),
            'image_path': cert.image_path
        })
    
    return jsonify(result)

@app.route('/upload', methods=['GET'])
@login_required
def upload_certificate():
    return render_template('upload_certificate.html')

@app.route('/download_report')
@login_required
def download_report():
    # Get user data
    user = current_user
    certificates = UserCertificate.query.filter_by(user_id=user.id).all()
    
    # Get statistics
    stats = {
        'total_courses': len(certificates),
        'domains': {},
        'difficulty_levels': {},
        'average_score': 0
    }
    
    if certificates:
        total_score = 0
        for cert in certificates:
            course = Course.query.get(cert.course_id)
            stats['domains'][course.domain] = stats['domains'].get(course.domain, 0) + 1
            stats['difficulty_levels'][course.difficulty] = stats['difficulty_levels'].get(course.difficulty, 0) + 1
            if cert.performance_score:
                total_score += cert.performance_score
        
        if len(certificates) > 0:
            stats['average_score'] = total_score / len(certificates)
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    elements.append(Paragraph(f"<b>{user.username}'s</b> Certificate Progress Report", title_style))
    elements.append(Spacer(1, 12))
    
    # Add date
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1  # Center alignment
    )
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", date_style))
    elements.append(Spacer(1, 20))
    
    # Add statistics
    elements.append(Paragraph("Statistics", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    # Create statistics table
    stats_data = [
        ["Total Courses", str(stats['total_courses'])],
        ["Average Score", f"{stats['average_score']:.1f}%"]
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 20))
    
    # Generate charts
    # Domain Distribution Chart
    if stats['domains']:
        elements.append(Paragraph("Domain Distribution", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        plt.figure(figsize=(6, 4))
        plt.pie(stats['domains'].values(), labels=stats['domains'].keys(), autopct='%1.1f%%')
        plt.title('Course Domains')
        
        # Save chart to buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.close()
        
        # Add chart to PDF
        img_data = img_buffer.getvalue()
        img = Image(io.BytesIO(img_data), width=5*inch, height=3.5*inch)
        elements.append(img)
        elements.append(Spacer(1, 20))
    
    # Difficulty Levels Chart
    if stats['difficulty_levels']:
        elements.append(Paragraph("Difficulty Levels", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        plt.figure(figsize=(6, 4))
        plt.bar(stats['difficulty_levels'].keys(), stats['difficulty_levels'].values())
        plt.title('Difficulty Distribution')
        plt.xlabel('Difficulty Level')
        plt.ylabel('Number of Courses')
        
        # Save chart to buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.close()
        
        # Add chart to PDF
        img_data = img_buffer.getvalue()
        img = Image(io.BytesIO(img_data), width=5*inch, height=3.5*inch)
        elements.append(img)
        elements.append(Spacer(1, 20))
    
    # Course Progress Chart
    if certificates:
        elements.append(Paragraph("Course Progress", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Group certificates by month
        monthly_data = {}
        for cert in certificates:
            date = cert.completion_date
            month_year = f"{date.year}-{date.month:02d}"
            if month_year not in monthly_data:
                monthly_data[month_year] = 0
            monthly_data[month_year] += 1
        
        # Sort months chronologically
        sorted_months = sorted(monthly_data.keys())
        
        # Calculate cumulative progress
        cumulative = 0
        cumulative_data = []
        for month in sorted_months:
            cumulative += monthly_data[month]
            cumulative_data.append(cumulative)
        
        # Format month labels
        month_labels = []
        for month in sorted_months:
            year, month_num = month.split('-')
            date = datetime(int(year), int(month_num), 1)
            month_labels.append(date.strftime('%b %Y'))
        
        plt.figure(figsize=(6, 4))
        plt.plot(month_labels, cumulative_data, marker='o')
        plt.title('Course Completion Progress')
        plt.xlabel('Month')
        plt.ylabel('Total Courses Completed')
        plt.grid(True)
        
        # Save chart to buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.close()
        
        # Add chart to PDF
        img_data = img_buffer.getvalue()
        img = Image(io.BytesIO(img_data), width=5*inch, height=3.5*inch)
        elements.append(img)
        elements.append(Spacer(1, 20))
    
    # Add certificates table
    elements.append(Paragraph("Completed Courses", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    if certificates:
        # Create table data
        table_data = [["Course Name", "Domain", "Difficulty", "Score", "Completion Date"]]
        
        for cert in certificates:
            course = Course.query.get(cert.course_id)
            table_data.append([
                course.name,
                course.domain,
                course.difficulty,
                f"{cert.performance_score or 'N/A'}%",
                cert.completion_date.strftime('%Y-%m-%d')
            ])
        
        # Create table
        table = Table(table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 0.75*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No certificates found.", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Return PDF as download
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{user.username}_progress_report.pdf",
        mimetype='application/pdf'
    )

@app.route('/api/certificates/<int:certificate_id>', methods=['DELETE'])
@login_required
def delete_certificate(certificate_id):
    try:
        # Get the certificate
        certificate = UserCertificate.query.get_or_404(certificate_id)
        
        # Check if the certificate belongs to the current user
        if certificate.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Delete the certificate image file if it exists
        if certificate.image_path:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(certificate.image_path))
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Delete the certificate from the database
        db.session.delete(certificate)
        db.session.commit()
        
        return jsonify({'message': 'Certificate deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 