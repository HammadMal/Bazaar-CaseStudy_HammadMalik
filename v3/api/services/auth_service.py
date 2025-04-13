from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token

from app import db
from models.user import User

class AuthService:
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate a user and return user object if successful."""
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return None
            
        if not user.is_active:
            return None
            
        # Update last login timestamp
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return user
    
    @staticmethod
    def generate_tokens(user_id):
        """Generate access and refresh tokens for a user."""
        access_token = create_access_token(identity=str(user_id))
        refresh_token = create_refresh_token(identity=str(user_id))
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    
    @staticmethod
    def register_user(username, email, password, role='store_user', store_id=None):
        """Register a new user."""
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return None, 'Username already exists'
            
        if User.query.filter_by(email=email).first():
            return None, 'Email already exists'
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            role=role,
            store_id=store_id
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return new_user, None