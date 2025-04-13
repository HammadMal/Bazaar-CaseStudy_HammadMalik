from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session  # Temporarily comment out

from config import get_config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
session = Session()  # Temporarily comment out

def create_app():
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(get_config())
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    session.init_app(app)  # Temporarily comment out

    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        return str(identity) if identity is not None else None

    CORS(app)
    
    # Import models to ensure they're registered with SQLAlchemy
    # We import here to avoid circular imports
    from models.store import Store
    from models.product import Product
    from models.inventory import Inventory
    from models.stock_movement import StockMovement
    from models.user import User
    
    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.inventory import inventory_bp
    from routes.stores import stores_bp
    from routes.reports import reports_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v2/auth')
    app.register_blueprint(products_bp, url_prefix='/api/v2/products')
    app.register_blueprint(inventory_bp, url_prefix='/api/v2/inventory')
    app.register_blueprint(stores_bp, url_prefix='/api/v2/stores')
    app.register_blueprint(reports_bp, url_prefix='/api/v2/reports')
    
    @app.route('/health')
    def health_check():
        import socket
        import os
        
        # Get container ID or hostname
        container_id = os.environ.get('HOSTNAME', socket.gethostname())
        
        return {
            'status': 'healthy',
            'container_id': container_id
        }, 200
    
    return app

# Create the app instance
app = create_app()

# Initialize database
with app.app_context():
    try:
        db.create_all()
        from models.user import User
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@bazaar.com', role='admin')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created successfully')
    except Exception as e:

        print(f"Database initialization note: {str(e)}")
        db.session.rollback()




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)