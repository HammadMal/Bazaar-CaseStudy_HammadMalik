# Bazaar Inventory Management System v3 - Phase 1: Containerization & Load Balancing

## Overview

In **Phase 1**, the application has been containerized using Docker and set up for multi-container deployment using Docker Compose. Nginx is configured as a load balancer to distribute traffic across multiple backend API instances. Additionally, a health check endpoint has been implemented to monitor the status of the application containers.

## What has been done in Phase 1?

- **Dockerized the Application**: The application is now containerized using Docker. This allows for easy deployment, scaling, and consistency across environments.
  
- **Multi-Container Setup with Docker Compose**: 
  - A **backend API** is containerized to handle inventory management logic.
  - **Nginx** is configured as a reverse proxy and load balancer to distribute incoming traffic across multiple API instances.
  - A **PostgreSQL** database is used for storing product and inventory data.


  - **Stateless Application with Redis**: The application has been made stateless by using **Redis** for session storage. This allows session data to be shared across all instances of the API, ensuring that any API instance can handle the request independently of the others.

- **Health Check Implementation**: A `/health` endpoint is provided, which returns the health status of the containers along with the container ID.

## How to Check the Phase 1 Implementation

If you'd like to check the Phase 1 implementation, follow these steps:

### 1. **Build and Start the Application with Docker Compose**

Make sure you have Docker and Docker Compose installed on your machine. Then, run the following command to build and start the containers:

```bash
docker-compose build --no-cache
docker compose up -d
```

Now you can see different containers running.  


### 2. Load Balancing 
After the containers are up and running, you can check the health of the system by visiting the /health endpoint. This will give you a response with the status and container ID.

```
http://localhost/health
```

You should see a response similar to this:

```json
{
    "status": "healthy",
    "container_id": "some-container-id"
}
```

Each time you check the health endpoint, you'll get a different container_id, indicating that each replica (container) of the API is running independently.

### 3. Test Inventory System via Nginx

As always you can interact with the Inventory system like you did in v2, for more information please check readme file in that folder. 

If you want to test the previous functionality make sure you :
Ensure that Postman points to Nginx, not directly to the backend API. Try using:

```
http://localhost/api/v3/auth/login
```

instead of  

```
http://localhost:5000/api/v3/auth/login
```

### 4. Check Redis for Session Management

The application is stateless, with sessions now managed by Redis. You can test Redis functionality by storing and retrieving data as follows:
```bash
docker exec -it bazaar-redis redis-cli
```

Test Redis Connection: In the Redis CLI, you can test the connection by typing:
```
PING
```

You should get a PONG response if Redis is working correctly.


# Bazaar Inventory Management System v3 - Phase 2:

1. The API will be available at:
```
http://localhost/api/v3/
```

2. RabbitMQ Management UI is available at:
```
http://localhost:15672

Use username: Bazaar
password: bazaar_secure_password
```

### Initial Login

The system is initialized with an admin user:
- Username: `admin`
- Password: `admin`

*Note: Change the admin password in production environments.*

## API Documentation

### Authentication

```
POST /api/v3/auth/login
POST /api/v3/auth/register
POST /api/v3/auth/refresh
```

### Products

```
GET /api/v3/products/
GET /api/v3/products/{id}
POST /api/v3/products/
PUT /api/v3/products/{id}
DELETE /api/v3/products/{id}
GET /api/v3/products/categories
```

### Inventory

```
GET /api/v3/inventory/store/{store_id}
GET /api/v3/inventory/product/{product_id}
POST /api/v3/inventory/stock-in
POST /api/v3/inventory/sale
POST /api/v3/inventory/remove
GET /api/v3/inventory/movements
```

### Stores

```
GET /api/v3/stores/
GET /api/v3/stores/{id}
POST /api/v3/stores/
PUT /api/v3/stores/{id}
DELETE /api/v3/stores/{id}
GET /api/v3/stores/regions
```

### Reports

```
GET /api/v3/reports/low-stock
GET /api/v3/reports/stock-movements
GET /api/v3/reports/inventory-summary
POST /api/v3/reports/inventory-summary/async
GET /api/v3/reports/product-performance
POST /api/v3/reports/product-performance/async
GET /api/v3/reports/status/{report_id}
GET /api/v3/reports/result/{report_id}
```

## Project Structure

```
v3/
├── api/                  # API application code
│   ├── models/           # SQLAlchemy models
│   ├── routes/           # API routes/endpoints
│   ├── services/         # Business logic services
│   ├── utils/            # Utility functions
│   ├── app.py            # Flask application factory
│   ├── config.py         # Configuration
│   ├── messaging.py      # Message queue integration
│   ├── worker.py         # Background worker
│   └── requirements.txt  # Python dependencies
├── nginx/                # Nginx configuration
├── init-scripts/         # Initialization scripts
├── docker-compose.yml    # Docker Compose configuration
└── .env                  # Environment variables
```

## Monitoring and Management

### Health Check

You can monitor the health of the API instances with:
```
GET /health
```

This returns the container ID and connection status to the database and message queue.

### Scaling

To scale the number of API or worker instances:
```bash
docker-compose up -d --scale api=5 --scale worker=3
```

### RabbitMQ Management

Access the RabbitMQ management console at `http://localhost:15672` to monitor queues, messages, and connections.


### Asynchronous Reports

For more complex reports that may take longer to generate, Bazaar provides asynchronous report generation through the message queue system:


#### Asynchronous Report Workflow:

1. Request a report generation through the async endpoint
2. Receive a report ID in the response
3. Check the report status using `GET /api/v3/reports/status/{report_id}`
4. When status shows "completed", retrieve the report with `GET /api/v3/reports/result/{report_id}`

#### Example:

Request an inventory summary report:

```
POST /api/v3/reports/inventory-summary/async
```

Enter the Authorization and Bearer Token in postman 

Body
```json
{}
```

### Response:

```json
{
    "estimated_completion_time": "30-60 seconds",
    "message": "Report generation queued successfully",
    "report_id": "3cabb60d-35fe-495c-8570-f9f69b9e8e35",
    "status": "queued"
}
```

Check report status:

```
GET /api/v3/reports/status/3cabb60d-35fe-495c-8570-f9f69b9e8e35
```

```json
{
    "completed_at": "2025-04-13T19:31:15.539623",
    "created_at": "2025-04-13T19:31:15.510947",
    "report_id": "3cabb60d-35fe-495c-8570-f9f69b9e8e35",
    "report_type": "inventory_summary",
    "status": "completed",
    "updated_at": "2025-04-13T19:31:15.543102"
}
```

Check report result: 

```
http://localhost/api/v3/reports/result/3cabb60d-35fe-495c-8570-f9f69b9e8e35
```

Enter the Authorization and Bearer Token in postman 

```json
{
    "completed_at": "2025-04-13T19:31:15.539623",
    "created_at": "2025-04-13T19:31:15.510947",
    "report_id": "3cabb60d-35fe-495c-8570-f9f69b9e8e35",
    "report_type": "inventory_summary",
    "result": {
        "summary": {
            "total_inventory_value": 25000.0,
            "total_products": 100,
            "total_stores": 5
        },
        "top_categories": [
            {
                "category": "Electronics",
                "total_quantity": 500,
                "total_value": 10000.0
            },
            {
                "category": "Clothing",
                "total_quantity": 750,
                "total_value": 7500.0
            }
        ],
        "top_stores": [
            {
                "id": 1,
                "name": "Main Store",
                "total_quantity": 1200,
                "total_value": 12000.0
            },
            {
                "id": 2,
                "name": "Downtown",
                "total_quantity": 800,
                "total_value": 8000.0
            }
        ]
    },
    "status": "completed"
}
```

# Read-Write Separation (Phase 3)

## Overview

The Bazaar Inventory System implements database read-write separation to optimize performance and scalability. This architecture separates database operations into read operations (handled by read replicas) and write operations (handled by the primary database).

## Implementation Details

### Database Configuration

The system uses a PostgreSQL primary-replica setup:

- **Primary Database**: Handles all write operations (INSERT, UPDATE, DELETE)
- **Read Replica**: Handles read operations (SELECT), reducing load on the primary

```yaml
# From docker-compose.yml
db:
  image: postgres:14
  container_name: bazaar-db-primary
  # Primary database configuration

db_replica:
  image: postgres:14
  container_name: bazaar-db-replica
  command: postgres -c hot_standby=on
  # Read replica configuration
```

### Database Router

A custom database router (`database_router.py`) directs queries to the appropriate database:

```python
class DBSessionManager:
    """
    Database session manager for read/write separation.
    """
    def get_session(self, for_write=False):
        """
        Get appropriate database session based on operation type.
        
        Args:
            for_write (bool): If True, return a session for write operations
                             If False, return a session for read operations
        """
        if for_write:
            return self.write_session_factory()
        return self.read_session_factory()
```

### API Implementation

Service layers and route handlers use the appropriate connection based on the operation:

```python
# Example of read operation
read_session = db_manager.get_session(for_write=False)
products = read_session.query(Product).all()

# Example of write operation
write_session = db_manager.get_session(for_write=True)
write_session.add(new_product)
write_session.commit()
```

## Benefits

1. **Improved Read Performance**: Read queries are distributed across replicas
2. **Reduced Primary Load**: Primary database focuses on write operations
3. **Better Scalability**: Read capacity can be scaled by adding more replicas
4. **Improved Availability**: System can continue operating in read-only mode if primary is down

## Testing Read-Write Separation

You can test the read-write separation by:

1. **Health Check**: The `/health` endpoint shows connection status for both databases:

```
GET http://localhost/health
```

Expected Response:
```json
{
  "status": "healthy",
  "container_id": "container-id",
  "write_database": "connected",
  "read_database": "connected",
  "message_queue": "connected",
  "cache": "connected"
}
```

2. **Load Testing**: Use a tool like JMeter or Locust to generate read-heavy load and verify:
   - Read operations are directed to the replica
   - Write operations are directed to the primary

## Failover Behavior

If the read replica becomes unavailable, the system automatically falls back to using the primary database for reads to ensure continuous operation.


# Caching Implementation for Bazaar Inventory System Phase 4

## Overview

This document describes the caching implementation for the Bazaar Inventory System, which uses Redis for caching frequently accessed data to improve response times and reduce database load.

## Key Features

- **Redis-based caching**: Uses Redis as the caching backend
- **Configurable timeouts**: Cache expiration is configurable per endpoint
- **Automatic cache invalidation**: Cache is automatically cleared when data is modified
- **Cache management endpoints**: Admin-only endpoints for monitoring and managing the cache

## Cached Endpoints

The following endpoints are cached:

1. **Product Listing**: `GET /api/v3/products/` - Cached for 5 minutes
2. **Product Details**: `GET /api/v3/products/{id}` - Cached for 5 minutes
3. **Product Categories**: `GET /api/v3/products/categories` - Cached for 10 minutes

## Cache Invalidation

The cache is automatically invalidated when:

- A new product is created
- A product is updated
- A product is deactivated (soft deleted)

## Cache Management Endpoints

The following endpoints are available for cache management (admin only):

1. **Get Cache Statistics**: `GET /api/v3/cache/stats`
2. **Clear Product Caches**: `POST /api/v3/cache/products/clear`
3. **Clear All Caches**: `POST /api/v3/cache/clear`

## Example Usage

### Get cache statistics:

```
Postman GET "http://localhost/api/v3/cache/stats" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Clear product caches:

```
Postman POST "http://localhost/api/v3/cache/products/clear" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Clear all caches:

```
Postman POST "http://localhost/api/v3/cache/clear" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Configuration

Cache settings can be adjusted in `config.py`. The default settings are:

```python
# Cache configuration
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes default cache timeout
CACHE_KEY_PREFIX = 'bazaar_cache:'
```

## Redis Configuration in Docker

Redis is configured with the following settings in `docker-compose.yml`:

```yaml
redis:
  image: redis:alpine
  container_name: bazaar-redis
  restart: always
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru --appendonly yes
  volumes:
    - redis_data:/data
  networks:
    - bazaar-network
```

Key settings:
- `maxmemory 512mb`: Limits Redis memory usage to 512MB
- `maxmemory-policy allkeys-lru`: When memory limit is reached, least recently used keys are evicted
- `appendonly yes`: Enables persistence to disk for data durability


# API Rate Limiting

## Overview

Bazaar Inventory System implements API rate limiting to prevent abuse and ensure fair usage of resources. This document explains the current rate limiting implementation and how to test it.

## Current Implementation

The system uses Flask-Limiter for rate limiting, which is configured in `app.py`:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

Rate limits are applied to specific endpoints using decorators. For example, the login endpoint has:

```python
@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    # Function implementation
```

Other endpoints with rate limiting include:

- **Login**: `@limiter.limit("10 per minute")`
- **Registration**: `@limiter.limit("5 per hour")`
- **Stock-in**: `@limiter.limit("200 per day")`
- **Sale**: `@limiter.limit("300 per day")`
- **Product creation**: `@limiter.limit("100 per day")`

## How It Works

1. **Request Identification**: By default, clients are identified by their IP address.
2. **Limit Enforcement**: Once a client exceeds their allotted requests within the time window, further requests are rejected with a 429 Too Many Requests status code.
3. **Storage**: Rate limit counters are stored in Redis, as configured in `config.py`:
   ```python
   RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
   RATELIMIT_STRATEGY = 'fixed-window'
   ```

## Testing Rate Limiting with Postman

### Test Case: Login Rate Limiting

This test verifies that the login endpoint limits requests to 10 per minute per IP address.

#### Test Steps:

1. **Set up a Postman request**
   - Create a new POST request to `http://localhost/api/v3/auth/login`
   - Set Content-Type header to `application/json`
   - Set the request body to:
     ```json
     {
       "username": "admin",
       "password": "admin"
     }
     ```

2. **Using Postman Runner**
   - Click on the "Runner" button in Postman
   - Add your login request to the collection runner
   - Set the iteration count to 12 (to ensure we exceed the limit)
   - Set the delay between requests to 1000ms (1 second)
   - Click "Run" to start the test

3. **Execute the test**
   - The first 10 requests should succeed (HTTP 200)
   - The 11th and subsequent requests should be rate limited (HTTP 429)

3. **Expected response for rate-limited requests:**
   ```
   HTTP/1.1 429 TOO MANY REQUESTS
   Content-Type: text/html; charset=utf-8
   Retry-After: [seconds until reset]
   X-RateLimit-Limit: 10
   X-RateLimit-Remaining: 0
   X-RateLimit-Reset: [timestamp]

   429 Too Many Requests: You have exceeded your request rate
   ```

4. **Reviewing the results**
   - In the Postman Runner results, you'll see the HTTP status codes for each request
   - You can click on individual requests to see detailed responses

5. **Wait for the rate limit to reset** (1 minute from first request)
   - After the reset period, running the test again should succeed for the first 10 requests

## Response Headers

When rate limiting is in effect, the following headers are included in responses:

- `X-RateLimit-Limit`: The maximum number of requests allowed in the time window
- `X-RateLimit-Remaining`: The number of remaining requests in the current time window
- `X-RateLimit-Reset`: The time when the current rate limit window resets
- `Retry-After`: The number of seconds to wait before retrying

## Configuration

Global rate limit settings are defined in `config.py`:

```python
RATELIMIT_DEFAULT = "200 per day, 50 per hour"
RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
RATELIMIT_STRATEGY = 'fixed-window'
```

## Monitoring Rate Limiting with Postman

You can monitor rate limiting through Postman by:

1. **Response Headers**: Check the response headers in Postman to see the current rate limit status:
   - `X-RateLimit-Limit`
   - `X-RateLimit-Remaining`
   - `X-RateLimit-Reset`

2. **Test Logs**: In the Postman Runner, you can see which requests succeeded and which were rate limited

3. **Application logs**: Rate limit events are also logged in your application logs

4. **Redis**: If needed, you can examine the rate limit keys in Redis using Redis CLI:
   ```bash
   docker exec -it bazaar-redis redis-cli
   keys *rate-limit*
   ```