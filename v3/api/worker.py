#!/usr/bin/env python
import os
import sys
import time
import json
import logging
import pika
from pika.exceptions import AMQPConnectionError
from datetime import datetime
import traceback
from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base




# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///bazaar.db')
RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672')
QUEUE_RETRY_INTERVAL = int(os.environ.get('QUEUE_RETRY_INTERVAL', 5))  # seconds
QUEUE_MAX_RETRIES = int(os.environ.get('QUEUE_MAX_RETRIES', 3))

# Define queue names as constants
INVENTORY_OPERATIONS_QUEUE = 'inventory_operations'
REPORT_GENERATION_QUEUE = 'report_generation'
NOTIFICATIONS_QUEUE = 'notifications'

# Set up database connection
engine = create_engine(DATABASE_URL)
Session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()


# Define minimal models needed for the worker
# This avoids circular import issues
class Report(Base):
    __tablename__ = 'reports'
    
    
    id = Column(String(36), primary_key=True)
    report_type = Column(String(50), nullable=False)
    parameters = Column(Text)
    status = Column(String(20), default='queued')
    result = Column(Text)
    user_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    def set_result(self, result):
        """Store result as JSON string."""
        if result:
            import json
            self.result = json.dumps(result)
    
    def get_parameters(self):
        """Get parameters as Python dict."""
        if self.parameters:
            import json
            return json.loads(self.parameters)
        return {}

def connect_to_rabbitmq():
    """Establish connection to RabbitMQ with retry logic"""
    max_retries = 10
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Connecting to RabbitMQ (attempt {attempt+1}/{max_retries})...")
            
            # Extract credentials from environment or use defaults
            rabbit_url = RABBITMQ_URL
            
            # Add credentials if not present in the URL
            if 'amqp://' in rabbit_url and '@' not in rabbit_url:
                rabbit_user = os.environ.get('RABBITMQ_DEFAULT_USER', 'bazaar')
                rabbit_pass = os.environ.get('RABBITMQ_DEFAULT_PASS', 'bazaar_secure_password')
                
                # Replace default URL with one that includes credentials
                url_parts = rabbit_url.split('://')
                if len(url_parts) == 2:
                    rabbit_url = f"{url_parts[0]}://{rabbit_user}:{rabbit_pass}@{url_parts[1]}"
                    logger.info(f"Using RabbitMQ URL with credentials: amqp://{rabbit_user}:***@{url_parts[1]}")
            
            parameters = pika.URLParameters(rabbit_url)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            # Declare queues to ensure they exist
            channel.queue_declare(queue=INVENTORY_OPERATIONS_QUEUE, durable=True)
            channel.queue_declare(queue=REPORT_GENERATION_QUEUE, durable=True)
            channel.queue_declare(queue=NOTIFICATIONS_QUEUE, durable=True)
            
            # Set QoS to limit the number of unacknowledged messages
            channel.basic_qos(prefetch_count=1)
            
            logger.info("Connected to RabbitMQ successfully")
            return connection, channel
        
        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max connection attempts reached. Exiting.")
                sys.exit(1)

def process_inventory_operation(ch, method, properties, body):
    """Process inventory operation messages"""
    try:
        logger.info(f"Processing inventory operation: {body}")
        
        # Parse message
        message = json.loads(body)
        operation_type = message.get('operation_type')
        data = message.get('data', {})
        
        # Create database session
        session = Session()
        report = None
        
        try:
            logger.info(f"Processing {operation_type} operation for product {data.get('product_id')} at store {data.get('store_id')}")
            
            # Process based on operation type
            if operation_type == 'stock-in':
                # Simple acknowledgment for now, actual implementation would go here
                logger.info("Stock-in operation processed")
                
            elif operation_type == 'sale':
                # Simple acknowledgment for now, actual implementation would go here
                logger.info("Sale operation processed")
                
            elif operation_type == 'removal':
                # Simple acknowledgment for now, actual implementation would go here
                logger.info("Removal operation processed")
                
            else:
                logger.warning(f"Unknown operation type: {operation_type}")
            
            # Commit the transaction
            session.commit()
            logger.info(f"Successfully processed {operation_type} operation")
            
        except Exception as e:
            # Rollback the transaction on error
            session.rollback()
            logger.error(f"Error processing inventory operation: {str(e)}")
            traceback.print_exc()
            
        finally:
            # Close the session
            session.close()
        
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        traceback.print_exc()
        
        # Reject the message and requeue it
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def process_report_request(ch, method, properties, body):
    """Process report generation requests"""
    try:
        logger.info(f"Processing report request: {body}")
        
        # Parse message
        message = json.loads(body)
        report_id = message.get('report_id')
        report_type = message.get('report_type')
        parameters = message.get('parameters', {})
        user_id = message.get('user_id')
        
        if not report_id:
            logger.error("No report_id in message")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
            
        # Log more details for debugging
        logger.info(f"Looking for report with ID: {report_id}")
        
        # Create database session
        session = Session()
        report = None
        
        try:
            # Fetch the report by ID
            report = session.query(Report).filter_by(id=report_id).first()
            
            if not report:
                logger.error(f"Report {report_id} not found in database")
                # Rejecting the message so it will be processed again
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                return
            
            # Update report status to processing
            report.status = 'processing'
            session.commit()
            
            # Generate report based on type
            result = None
            
            if report_type == 'inventory_summary':
                # Generate a simple mock report for demonstration
                logger.info(f"Generating inventory summary report {report_id}")
                result = {
                    'summary': {
                        'total_stores': 5,
                        'total_products': 100,
                        'total_inventory_value': 25000.00
                    },
                    'top_categories': [
                        {'category': 'Electronics', 'total_quantity': 500, 'total_value': 10000.00},
                        {'category': 'Clothing', 'total_quantity': 750, 'total_value': 7500.00}
                    ],
                    'top_stores': [
                        {'id': 1, 'name': 'Main Store', 'total_quantity': 1200, 'total_value': 12000.00},
                        {'id': 2, 'name': 'Downtown', 'total_quantity': 800, 'total_value': 8000.00}
                    ]
                }
                
            elif report_type == 'product_performance':
                # Generate a simple mock report for demonstration
                logger.info(f"Generating product performance report {report_id}")
                result = {
                    'start_date': '2025-03-01',
                    'end_date': '2025-04-01',
                    'top_selling_products': [
                        {'product_id': 1, 'sku': 'ELEC-001', 'name': 'Smartphone', 'category': 'Electronics', 'total_quantity_sold': 150},
                        {'product_id': 2, 'sku': 'ELEC-002', 'name': 'Laptop', 'category': 'Electronics', 'total_quantity_sold': 75}
                    ]
                }
                
            else:
                logger.warning(f"Unknown report type: {report_type}")
                result = {'error': f'Unknown report type: {report_type}'}
            
            # Update report with results
            report.status = 'completed'
            report.completed_at = datetime.utcnow()
            report.set_result(result)
            session.commit()
            
            logger.info(f"Successfully generated report {report_id}")
            
            # Send notification (actual implementation would use a proper notification service)
            logger.info(f"Notification sent: Report {report_id} completed for user {user_id}")
            
        except Exception as e:
            # Update report status to failed
            if report:
                report.status = 'failed'
                report.set_result({'error': str(e)})
                session.commit()
            
            # Rollback the transaction on error
            session.rollback()
            logger.error(f"Error generating report: {str(e)}")
            traceback.print_exc()
            
        finally:
            # Close the session
            session.close()
        
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        traceback.print_exc()
        
        # Reject the message and requeue it
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def process_notification(ch, method, properties, body):
    """Process notification messages"""
    try:
        logger.info(f"Processing notification: {body}")
        
        # Parse message
        message = json.loads(body)
        notification_type = message.get('notification_type')
        recipient = message.get('recipient')
        content = message.get('content', {})
        
        # Here you would implement your notification logic
        # This could include sending emails, push notifications, etc.
        logger.info(f"Sending {notification_type} notification to recipient {recipient}")
        
        # For this example, we'll just log the notification
        logger.info(f"Notification content: {content}")
        
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logger.error(f"Error processing notification: {str(e)}")
        traceback.print_exc()
        
        # Reject the message and requeue it
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    """Main worker function"""
    logger.info("Starting Bazaar worker...")
    
    while True:
        try:
            # Connect to RabbitMQ
            connection, channel = connect_to_rabbitmq()
            
            # Set up consumers for each queue
            channel.basic_consume(
                queue=INVENTORY_OPERATIONS_QUEUE,
                on_message_callback=process_inventory_operation
            )
            
            channel.basic_consume(
                queue=REPORT_GENERATION_QUEUE,
                on_message_callback=process_report_request
            )
            
            channel.basic_consume(
                queue=NOTIFICATIONS_QUEUE,
                on_message_callback=process_notification
            )
            
            logger.info("Worker is waiting for messages. To exit press CTRL+C")
            
            # Start consuming messages
            channel.start_consuming()
            
        except AMQPConnectionError as e:
            logger.error(f"RabbitMQ connection error: {str(e)}")
            logger.info(f"Reconnecting in {QUEUE_RETRY_INTERVAL} seconds...")
            time.sleep(QUEUE_RETRY_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Worker shutting down...")
            if connection and connection.is_open:
                connection.close()
            break
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            traceback.print_exc()
            if connection and connection.is_open:
                connection.close()
            logger.info(f"Restarting worker in {QUEUE_RETRY_INTERVAL} seconds...")
            time.sleep(QUEUE_RETRY_INTERVAL)

if __name__ == "__main__":
    main()