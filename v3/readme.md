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

{
    "status": "healthy",
    "container_id": "some-container-id"
}


Each time you check the health endpoint, you'll get a different container_id, indicating that each replica (container) of the API is running independently.

### 3. Test Inventory System via Nginx

As always you can interact with the Inventory system like you did in v3, for more information please check readme file in that folder. 

If you want to test the previous functionality make sure you :
Ensure that Postman points to Nginx, not directly to the backend API. Try using:

http://localhost/api/v3/auth/login


instead of  

http://localhost:5000/api/v3/auth/login


### 4. Check Redis for Session Management

The application is stateless, with sessions now managed by Redis. You can test Redis functionality by storing and retrieving data as follows:
```
docker exec -it bazaar-redis redis-cli

```

Test Redis Connection: In the Redis CLI, you can test the connection by typing:
Ping

You should get a PONG response if Redis is working correctly.



# Bazaar Inventory Management System v3 - Phase 2:


```

1. The API will be available at:
```
http://localhost/api/v3/
```

2 RabbitMQ Management UI is available at:
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


POST /api/v3/reports/inventory-summary/async


Enter the Authorization and Bearer Token in postman 

Body
```
{}
```

### Response : 



{
    "estimated_completion_time": "30-60 seconds",
    "message": "Report generation queued successfully",
    "report_id": "3cabb60d-35fe-495c-8570-f9f69b9e8e35",
    "status": "queued"
}

Check report status:

GET /api/v3/reports/status/3cabb60d-35fe-495c-8570-f9f69b9e8e35



{
    "completed_at": "2025-04-13T19:31:15.539623",
    "created_at": "2025-04-13T19:31:15.510947",
    "report_id": "3cabb60d-35fe-495c-8570-f9f69b9e8e35",
    "report_type": "inventory_summary",
    "status": "completed",
    "updated_at": "2025-04-13T19:31:15.543102"
}



Check report result: 

http://localhost/api/v3/reports/result/3cabb60d-35fe-495c-8570-f9f69b9e8e35

Enter the Authorization and Bearer Token in postman 

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




## Production Considerations

This project is licensed under the MIT License - see the LICENSE file for details.




### Read Write Seperation Phase 3 



Fill this later 


### Cache 

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

```bash
Postman GET "http://localhost/api/v3/cache/stats" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Clear product caches:

```bash
Postman POST "http://localhost/api/v3/cache/products/clear" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Clear all caches:

```bash
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