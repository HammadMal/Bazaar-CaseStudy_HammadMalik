import json
import os
import pika
import logging
from functools import wraps
from flask import current_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageQueue:
    """Message Queue client for RabbitMQ."""
    
    # Define queue names as constants
    INVENTORY_OPERATIONS_QUEUE = 'inventory_operations'
    REPORT_GENERATION_QUEUE = 'report_generation'
    NOTIFICATIONS_QUEUE = 'notifications'
    
    def __init__(self, app=None):
        self.connection = None
        self.channel = None
        self.app = app
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask application."""
        self.app = app
        
        # Add configuration defaults
        app.config.setdefault('RABBITMQ_URL', os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672'))
        
        # Set up connection when the application context is created
        app.before_request(self.connect)
        app.teardown_appcontext(self.close_connection)
    
    def connect(self):
        """Establish connection to RabbitMQ server."""
        if self.connection is None or self.connection.is_closed:
            try:
                # Get connection URL from app config or environment
                url = self.app.config.get('RABBITMQ_URL') if self.app else os.environ.get('RABBITMQ_URL')
                
                # Extract credentials from URL or use defaults from environment
                if 'amqp://' in url and '@' not in url:
                    # URL doesn't have credentials, so add them from environment
                    rabbit_user = os.environ.get('RABBITMQ_DEFAULT_USER', 'bazaar')
                    rabbit_pass = os.environ.get('RABBITMQ_DEFAULT_PASS', 'bazaar_secure_password')
                    
                    # Replace default URL with one that includes credentials
                    url_parts = url.split('://')
                    if len(url_parts) == 2:
                        url = f"{url_parts[0]}://{rabbit_user}:{rabbit_pass}@{url_parts[1]}"
                        logger.info(f"Using RabbitMQ URL with credentials: amqp://{rabbit_user}:***@{url_parts[1]}")
                
                # Create connection parameters
                parameters = pika.URLParameters(url)
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                
                # Declare queues - ensure they exist
                self.channel.queue_declare(queue=self.INVENTORY_OPERATIONS_QUEUE, durable=True)
                self.channel.queue_declare(queue=self.REPORT_GENERATION_QUEUE, durable=True)
                self.channel.queue_declare(queue=self.NOTIFICATIONS_QUEUE, durable=True)
                
                logger.info("Connected to RabbitMQ successfully")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
                self.connection = None
                self.channel = None
    
    def close_connection(self, exception=None):
        """Close the connection to RabbitMQ."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.connection = None
            self.channel = None
    
    def publish_message(self, queue_name, message):
        """Publish a message to the specified queue."""
        if not self.connection or not self.channel:
            self.connect()
        
        if not self.channel:
            logger.error("Failed to publish message: no channel available")
            return False
        
        try:
            # Convert message to JSON if it's a dict
            if isinstance(message, dict):
                message = json.dumps(message)
            
            # Publish the message
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            return True
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            self.close_connection()
            return False

    def publish_inventory_operation(self, operation_type, data):
        """Publish an inventory operation to the queue."""
        message = {
            'operation_type': operation_type,
            'data': data
        }
        return self.publish_message(self.INVENTORY_OPERATIONS_QUEUE, message)
    
    def publish_report_request(self, report_type, message_data):
        """Publish a report generation request to the queue."""
        # Ensure report_type is in the message data
        if isinstance(message_data, dict):
            message_data['report_type'] = report_type
        
        # Send the message
        return self.publish_message(self.REPORT_GENERATION_QUEUE, message_data)
    
    def publish_notification(self, notification_type, recipient, content):
        """Publish a notification to the queue."""
        message = {
            'notification_type': notification_type,
            'recipient': recipient,
            'content': content
        }
        return self.publish_message(self.NOTIFICATIONS_QUEUE, message)


# Create a global instance
message_queue = MessageQueue()

def with_message_queue(f):
    """Decorator to ensure message queue is connected before function execution."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        message_queue.connect()
        return f(*args, **kwargs)
    return decorated_function