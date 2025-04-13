from datetime import datetime
import hashlib
from app import db

class User(db.Model):
    """User model for authentication and tracking operations."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='store_user')  # admin, store_manager, store_user
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))  # Optional store assignment
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username} role:{self.role}>'
    
    def set_password(self, password):
        """Hash and set the user password."""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()