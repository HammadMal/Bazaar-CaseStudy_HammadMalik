from datetime import datetime
from app import db

class Inventory(db.Model):
    """Inventory model representing store-specific product quantities."""
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    min_stock_level = db.Column(db.Integer, default=0)
    max_stock_level = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define the unique constraint for store_id and product_id combination
    __table_args__ = (
        db.UniqueConstraint('store_id', 'product_id', name='uix_inventory_store_product'),
    )
    
    def __repr__(self):
        return f'<Inventory store:{self.store_id} product:{self.product_id} qty:{self.quantity}>'