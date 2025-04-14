from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
import random

# Create database engines for read and write operations
def setup_db_engines(app):
    """
    Set up separate database engines for read and write operations.
    
    Returns:
        tuple: (write_engine, read_engine)
    """
    # Get database URLs from environment or config
    write_db_url = app.config.get('WRITE_DATABASE_URL', os.environ.get('WRITE_DATABASE_URL'))
    read_db_url = app.config.get('READ_DATABASE_URL', os.environ.get('READ_DATABASE_URL'))
    
    # If specific read database URL isn't provided, use the write URL
    if not read_db_url:
        read_db_url = write_db_url
    
    # Create engines with appropriate configurations
    write_engine = create_engine(
        write_db_url,
        pool_size=10,
        max_overflow=20,
        pool_recycle=300  # Recycle connections after 5 minutes
    )
    
    read_engine = create_engine(
        read_db_url,
        pool_size=20,  # Larger pool for read operations
        max_overflow=30,
        pool_recycle=300,
        pool_timeout=10,  # Lower timeout for read connections
        execution_options={'readonly': True}  # Mark as readonly if supported by dialect
    )
    
    return write_engine, read_engine

# Session factories
def get_write_session(write_engine):
    """Get a database session for write operations."""
    return scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=write_engine)
    )

def get_read_session(read_engine, write_engine):
    """
    Get a database session for read operations.
    Falls back to write engine if read engine is unavailable.
    """
    try:
        # For simplicity, we'll add a basic load balancing mechanism if multiple read replicas
        # In a real-world scenario, this would be more sophisticated
        if isinstance(read_engine, list):
            # Select a random read replica
            selected_engine = random.choice(read_engine)
        else:
            selected_engine = read_engine
            
        return scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=selected_engine)
        )
    except Exception as e:
        current_app.logger.warning(f"Failed to get read session: {str(e)}. Falling back to write session.")
        return get_write_session(write_engine)

# Core session manager
class DBSessionManager:
    """
    Database session manager for read/write separation.
    """
    def __init__(self, app=None):
        self.write_engine = None
        self.read_engine = None
        self.write_session_factory = None
        self.read_session_factory = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask application."""
        self.write_engine, self.read_engine = setup_db_engines(app)
        self.write_session_factory = get_write_session(self.write_engine)
        self.read_session_factory = get_read_session(self.read_engine, self.write_engine)
        
        # Register teardown context
        app.teardown_appcontext(self.teardown)
    
    def get_session(self, for_write=False):
        """
        Get appropriate database session based on operation type.
        
        Args:
            for_write (bool): If True, return a session for write operations
                             If False, return a session for read operations
        
        Returns:
            SQLAlchemy session
        """
        if for_write:
            return self.write_session_factory()
        return self.read_session_factory()
    
    def teardown(self, exception=None):
        """Remove database sessions at the end of the request."""
        if self.write_session_factory:
            self.write_session_factory.remove()
        if self.read_session_factory:
            self.read_session_factory.remove()

# Create a global instance
db_manager = DBSessionManager()