from datetime import datetime
from app import db

class StockMovement(db.Model):
    """StockMovement model tracking all inventory changes."""
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    movement_type = db.Column(db.String(20), nullable=False)  # 'stock-in', 'sale', 'removal', 'transfer', etc.
    quantity = db.Column(db.Integer, nullable=False)
    previous_quantity = db.Column(db.Integer, nullable=False)
    new_quantity = db.Column(db.Integer, nullable=False)
    reference_id = db.Column(db.String(50))  # Purchase order, invoice, etc.
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<StockMovement {self.movement_type} {self.quantity} of product:{self.product_id} at store:{self.store_id}>'