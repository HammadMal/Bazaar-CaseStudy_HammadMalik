from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session

from config import get_config
from database_router import db_manager

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
session = Session()

# Import message queue
from messaging import message_queue

def create_app():
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(get_config())
    
    # Set up database URLs for read/write separation
    app.config['WRITE_DATABASE_URL'] = app.config.get('SQLALCHEMY_DATABASE_URI')
    app.config['READ_DATABASE_URL'] = app.config.get('SQLALCHEMY_READ_REPLICA_URI', 
                                                     app.config.get('SQLALCHEMY_DATABASE_URI'))
    
    # Initialize database manager with separate read/write connections
    db_manager.init_app(app)
    
    # Initialize SQLAlchemy with the write engine for schema management
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize other extensions
    jwt.init_app(app)
    limiter.init_app(app)
    session.init_app(app)
    
    # Initialize message queue with app
    message_queue.init_app(app)

    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        return str(identity) if identity is not None else None

    CORS(app)
    
    # Import models to ensure they're registered with SQLAlchemy
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
    
    app.register_blueprint(auth_bp, url_prefix='/api/v3/auth')
    app.register_blueprint(products_bp, url_prefix='/api/v3/products')
    app.register_blueprint(inventory_bp, url_prefix='/api/v3/inventory')
    app.register_blueprint(stores_bp, url_prefix='/api/v3/stores')
    app.register_blueprint(reports_bp, url_prefix='/api/v3/reports')
    
    @app.route('/health')
    def health_check():
        import socket
        import os
        
        # Get container ID or hostname
        container_id = os.environ.get('HOSTNAME', socket.gethostname())
        
        # Check write database connection
        write_db_status = "connected"
        try:
            # Use the write session for this check
            write_session = db_manager.get_session(for_write=True)
            write_session.execute("SELECT 1")
        except Exception:
            write_db_status = "disconnected"
        
        # Check read database connection
        read_db_status = "connected"
        try:
            # Use the read session for this check
            read_session = db_manager.get_session(for_write=False)
            read_session.execute("SELECT 1")
        except Exception:
            read_db_status = "disconnected"
        
        # Check message queue connection
        mq_status = "connected" if message_queue.connection and message_queue.connection.is_open else "disconnected"
        
        return {
            'status': 'healthy',
            'container_id': container_id,
            'write_database': write_db_status,
            'read_database': read_db_status,
            'message_queue': mq_status
        }, 200
    
    return app

# Create the app instance
app = create_app()

# Initialize database
with app.app_context():
    try:
        # Use write connection for schema creation and admin user setup
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