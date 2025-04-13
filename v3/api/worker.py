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