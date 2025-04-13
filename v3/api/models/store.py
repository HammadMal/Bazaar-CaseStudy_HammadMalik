from datetime import datetime
from app import db

class Store(db.Model):
    """Store model representing retail locations."""
    __tablename__ = 'stores'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    country = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Store {self.code}: {self.name}>'