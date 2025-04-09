import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

class CourseRecommender:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.domain_encoder = LabelEncoder()
        self.difficulty_encoder = LabelEncoder()
        
    def prepare_data(self, data):
        # Convert categorical variables to numerical
        data['domain_encoded'] = self.domain_encoder.fit_transform(data['domain'])
        data['difficulty_encoded'] = self.difficulty_encoder.fit_transform(data['difficulty'])
        
        # Select features for training
        features = ['duration', 'domain_encoded', 'difficulty_encoded']
        X = data[features]
        
        # Scale the features
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled
    
    def train(self, historical_data):
        """
        Train the recommendation model using historical course completion data
        historical_data should be a DataFrame with columns:
        - duration: course duration in hours
        - domain: course domain
        - difficulty: course difficulty level
        - next_course: the course that was taken next (target variable)
        """
        X = self.prepare_data(historical_data)
        y = historical_data['next_course']
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train the model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Calculate and return accuracy
        train_accuracy = self.model.score(X_train, y_train)
        test_accuracy = self.model.score(X_test, y_test)
        
        return {
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy
        }
    
    def recommend(self, user_data):
        """
        Recommend next courses based on user's current course data
        user_data should be a DataFrame with columns:
        - duration: course duration in hours
        - domain: course domain
        - difficulty: course difficulty level
        """
        X = self.prepare_data(user_data)
        recommendations = self.model.predict_proba(X)
        
        # Get top 3 recommendations
        top_3_indices = np.argsort(recommendations[0])[-3:][::-1]
        top_3_courses = self.model.classes_[top_3_indices]
        top_3_probabilities = recommendations[0][top_3_indices]
        
        return list(zip(top_3_courses, top_3_probabilities))
    
    def save_model(self, path):
        """Save the trained model and encoders"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'domain_encoder': self.domain_encoder,
            'difficulty_encoder': self.difficulty_encoder
        }
        joblib.dump(model_data, path)
    
    def load_model(self, path):
        """Load a trained model and encoders"""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.domain_encoder = model_data['domain_encoder']
        self.difficulty_encoder = model_data['difficulty_encoder']

# Example usage:
if __name__ == "__main__":
    # Create sample data
    sample_data = pd.DataFrame({
        'duration': [40, 60, 30, 45, 50],
        'domain': ['Programming', 'AI/ML', 'Data Science', 'Programming', 'AI/ML'],
        'difficulty': ['Beginner', 'Intermediate', 'Beginner', 'Advanced', 'Intermediate'],
        'next_course': ['Python Advanced', 'Deep Learning', 'Data Analysis', 'Web Development', 'NLP']
    })
    
    # Initialize and train the model
    recommender = CourseRecommender()
    accuracy = recommender.train(sample_data)
    print(f"Model accuracy: {accuracy}")
    
    # Test recommendations
    test_data = pd.DataFrame({
        'duration': [45],
        'domain': ['Programming'],
        'difficulty': ['Intermediate']
    })
    
    recommendations = recommender.recommend(test_data)
    print("\nRecommended courses:")
    for course, probability in recommendations:
        print(f"{course}: {probability:.2%} confidence") 