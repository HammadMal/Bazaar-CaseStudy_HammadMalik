import logging
from app import db
from messaging import message_queue

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications to users."""
    
    @staticmethod
    def send_low_stock_notification(store_id, product_id, quantity, min_stock_level):
        """Send notification about low stock levels."""
        try:
            # Get required data
            from models.product import Product
            from models.store import Store
            from models.user import User
            
            product = Product.query.get(product_id)
            store = Store.query.get(store_id)
            
            if not product or not store:
                logger.error(f"Could not find product {product_id} or store {store_id} for notification")
                return False
            
            # Find store manager and admin users to notify
            store_users = User.query.filter_by(store_id=store_id, role='store_manager').all()
            admin_users = User.query.filter_by(role='admin').all()
            
            recipients = [user.id for user in store_users + admin_users]
            
            # Create notification content
            content = {
                'type': 'low_stock',
                'store': {
                    'id': store.id,
                    'name': store.name
                },
                'product': {
                    'id': product.id,
                    'sku': product.sku,
                    'name': product.name
                },
                'current_quantity': quantity,
                'min_stock_level': min_stock_level,
                'percentage': round((quantity / min_stock_level) * 100, 2) if min_stock_level else 0
            }
            
            # Send notification to each recipient
            for recipient in recipients:
                message_queue.publish_notification('low_stock', recipient, content)
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending low stock notification: {str(e)}")
            return False
    
    @staticmethod
    def send_report_completed_notification(report_id, user_id):
        """Send notification about a completed report."""
        try:
            from models.report import Report
            from models.user import User
            
            report = Report.query.get(report_id)
            user = User.query.get(user_id)
            
            if not report or not user:
                logger.error(f"Could not find report {report_id} or user {user_id} for notification")
                return False
            
            # Create notification content
            content = {
                'type': 'report_completed',
                'report': {
                    'id': report.id,
                    'type': report.report_type,
                    'created_at': report.created_at.isoformat(),
                    'completed_at': report.completed_at.isoformat() if report.completed_at else None
                }
            }
            
            # Send notification
            message_queue.publish_notification('report_completed', user_id, content)
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending report completion notification: {str(e)}")
            return False