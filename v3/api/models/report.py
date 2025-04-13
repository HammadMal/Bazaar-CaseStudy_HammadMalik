from datetime import datetime
import json
from app import db

class Report(db.Model):
    """Report model for storing report metadata and results."""
    __tablename__ = 'reports'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    report_type = db.Column(db.String(50), nullable=False)
    parameters = db.Column(db.Text)  # Stored as JSON
    status = db.Column(db.String(20), default='queued')  # queued, processing, completed, failed
    result = db.Column(db.Text)  # Stored as JSON
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Report {self.id}: {self.report_type} - {self.status}>'
    
    def set_parameters(self, parameters):
        """Store parameters as JSON string."""
        if parameters:
            self.parameters = json.dumps(parameters)
    
    def get_parameters(self):
        """Get parameters as Python dict."""
        if self.parameters:
            return json.loads(self.parameters)
        return {}
    
    def set_result(self, result):
        """Store result as JSON string."""
        if result:
            self.result = json.dumps(result)
    
    def get_result(self):
        """Get result as Python dict."""
        if self.result:
            return json.loads(self.result)
        return None