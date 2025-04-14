# Bazaar Inventory Management System - Stage 2

A robust inventory management system built using Flask, PostgreSQL, and Docker. This system allows managing product inventory across multiple stores with proper authentication, API throttling, and comprehensive reporting.

Previously I built a simple frontend with some inventory management tools, in this version I will skip the frontend and focus on
building a scalable backend for our service. We will check the functionality of our API endpoints through POSTMAN. 

## Architecture Overview

The Stage 2 architecture introduces several improvements over Stage 1:

- **Multi-store Support**: Central product catalog with store-specific inventory
- **REST API**: Proper RESTful API endpoints with versioning (v2)
- **Authentication**: JWT-based authentication and role-based access control
- **Rate Limiting**: API throttling to prevent abuse
- **PostgreSQL Database**: Scalable relational database replacing SQLite
- **Docker Containerization**: Simplified deployment and environment consistency
- **Redis Cache**: For rate limiting and potential future caching needs

## Technical Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Containerization**: Docker and Docker Compose
- **Rate Limiting**: Redis-backed Flask-Limiter
- **API**: RESTful API design with JSON responses

## Project Setup

### Prerequisites

- Docker and Docker Compose installed
- Git (optional)
- Postman (for testing the API)

### Installation

1. Clone or download the repository:
```bash
git clone <repository-url>
cd "foldername"
```

2. Start the application with Docker Compose:
```bash
docker-compose up -d
```

3. The API will be available at: `http://localhost:5000`

4. Verify the API is running by accessing: `http://localhost:5000/health`
   - You should see: `{"status":"healthy"}`

## API Testing Guide

This section provides step-by-step instructions to test the API endpoints with sample data.

### 1. Authentication
#### Register for user: 
- **URL**: `POST http://localhost:5000/api/v2/auth/login`
- **Headers**: 
  - Content-Type: application/json

- **Body**:
```json
{
  "username": "Hammad",
  "email": "email123@yahoo.com",
  "password": "123456"
}
```

- **Expected Response**:
```json
{
    "message": "User registered successfully",
    "user_id": 1
}
```

#### Admin Login (Get Access Token)
- **URL**: `POST http://localhost:5000/api/v2/auth/login`
- **Headers**: 
  - Content-Type: application/json
- **Body**:
```json
{
  "username": "admin",
  "password": "admin"
}
```
- **Expected Response**:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0NDUzMDk5MSwianRpIjoiY2IyNTYxMGYtYjdlZS00Yjk2LWFkOWMtYTRkMzU4ODAwNzQ4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NDQ1MzA5OTEsImV4cCI6MTc0NDUzNDU5MX0.de6rCbkaS1t14eAj43pE0K6udqkB5_hBMB0VA5nhEak",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0NDUzMDk5MSwianRpIjoiNDg1OTE3MTAtNzFhNi00NjE4LTljYzEtOGQ2YjgwNWUxOTk5IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxIiwibmJmIjoxNzQ0NTMwOTkxLCJleHAiOjE3NDcxMjI5OTF9.k1un0dzGkAZEGUz-ZEmzHzJygZApJrMEXKIu4-DtFTY",
    "user": {
        "email": "admin@bazaar.com",
        "id": 1,
        "role": "admin",
        "store_id": null,
        "username": "admin"
    }
}
```
- **Important**: Save the access_token - you'll need it for all subsequent requests

#### Using the Token
- For all authenticated endpoints, add this header:
- **Headers**:
  - Authorization: Bearer YOUR_ACCESS_TOKEN

### 2. Store Management

#### Create a New Store
- **URL**: `POST http://localhost:5000/api/v2/stores`
- **Headers**:
  - Authorization: Bearer YOUR_ACCESS_TOKEN
  - Content-Type: application/json
- **Body**:
```json
{
  "code": "STORE1",
  "name": "Main Street Store",
  "address": "123 Main Street",
  "city": "Karachi",
  "region": "Sindh",
  "country": "Pakistan",
  "phone": "+92123456789",
  "email": "mainst@bazaar.com"
}
```
- **Expected Response**:
```json
{
    "message": "Store created successfully",
    "store_id": 1
}
```

#### List All Stores
- **URL**: `GET http://localhost:5000/api/v2/stores`
- **Headers**:
  - Authorization: Bearer YOUR_ACCESS_TOKEN
- **Expected Response** (example):
```json
{
    "items": [
        {
            "active": true,
            "address": "123 Main Street",
            "city": "Karachi",
            "code": "STORE2",
            "country": "Pakistan",
            "created_at": "2025-04-13T07:57:46.468059",
            "email": "mainst@bazaar.com",
            "id": 1,
            "name": "Main Street Store",
            "phone": "+92123456789",
            "region": "Sindh"
        }
    ],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total_items": 1,
        "total_pages": 1
    }
}
```

### 3. Product Management

#### Create a New Product
- **URL**: `POST http://localhost:5000/api/v2/products`
- **Headers**:
  - Authorization: Bearer YOUR_ACCESS_TOKEN
  - Content-Type: application/json
- **Body**:
```json
{
  "sku": "LPT-001",
  "name": "Dell XPS 13",
  "description": "13-inch laptop with Intel Core i7",
  "category": "Electronics",
  "unit": "pcs",
  "price": 1299.99
}
```
- **Expected Response**:
```json
{
    "message": "Product created successfully",
    "product_id": 1
}
```

#### List All Products
- **URL**: `GET http://localhost:5000/api/v2/products`
- **Headers**:
  - Authorization: Bearer YOUR_ACCESS_TOKEN
- **Expected Response** (example):
```json
{
    "items": [
        {
            "active": true,
            "category": "Electronics",
            "created_at": "2025-04-13T07:59:23.429368",
            "description": "13-inch laptop with Intel Core i7",
            "id": 1,
            "name": "Dell XPS 13",
            "price": 1299.99,
            "sku": "LPT-001",
            "unit": "pcs",
            "updated_at": "2025-04-13T07:59:23.429375"
        }
    ],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total_items": 1,
        "total_pages": 1
    }
}
```

### 4. Inventory Management

#### Stock In (Add Inventory)
- **URL**: `POST http://localhost:5000/api/v2/inventory/stock-in`
- **Headers**:
  - Authorization: Bearer YOUR_ACCESS_TOKEN
  - Content-Type: application/json
- **Body**:
```json
{
  "store_id": 1,
  "product_id": 1,
  "quantity": 10,
  "reference_id": "PO-12345",
  "notes": "Initial stock",
  "min_stock_level": 2,
  "max_stock_level": 20
}
```
- **Expected Response**:
```json
{
    "inventory": {
        "new_quantity": 10,
        "previous_quantity": 0,
        "product_id": 1,
        "store_id": 1
    },
    "message": "Stock added successfully",
    "movement_id": 1
}
```

#### Get Store Inventory
- **URL**: `GET http://localhost:5000/api/v2/inventory/store/1`
- **Headers**:
  - Authorization: Bearer YOUR_ACCESS_TOKEN
- **Expected Response** (example):
```json
{
    "items": [
        {
            "inventory_id": 1,
            "last_updated": "2025-04-13T08:00:43.964671",
            "max_stock_level": 20,
            "min_stock_level": 2,
            "product": {
                "category": "Electronics",
                "id": 1,
                "name": "Dell XPS 13",
                "sku": "LPT-001",
                "unit": "pcs"
            },
            "quantity": 10
        }
    ],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total_items": 1,
        "total_pages": 1
    },
    "store": {
        "code": "STORE2",
        "id": 1,
        "name": "Main Street Store"
    }
}
```

#### Record a Sale
- **URL**: `POST http://localhost:5000/api/v2/inventory/sale`
- **Headers**:
  - Authorization: Bearer YOUR_ACCESS_TOKEN
  - Content-Type: application/json
- **Body**:
```json
{
  "store_id": 1,
  "product_id": 1,
  "quantity": 2,
  "reference_id": "INV-7890",
  "notes": "Sale to Customer X"
}
```
- **Expected Response**:
```json
{
    "inventory": {
        "new_quantity": 8,
        "previous_quantity": 10,
        "product_id": 1,
        "store_id": 1
    },
    "message": "Sale recorded successfully",
    "movement_id": 2
}
```

### 5. Reporting

#### Low Stock Report 
- **URL**: `GET http://localhost:5000/api/v2/reports/low-stock`
- **Headers**:
  - Authorization: Bearer YOUR_ACCESS_TOKEN
- **Expected Response** (example):
```json
{
    "count": 1,
    "items": [
        {
            "category": "Electronics",
            "current_quantity": 2,
            "min_stock_level": 2,
            "product_id": 1,
            "product_name": "Dell XPS 13",
            "sku": "LPT-001",
            "stock_percentage": 100.0,
            "store_id": 1,
            "store_name": "Main Street Store"
        }
    ]
}
```
### The above will run when the current quantity hits min_stock_level.

#### Inventory Summary
- **URL**: `GET http://localhost:5000/api/v2/reports/inventory-summary`
- **Headers**:
  - Authorization: Bearer YOUR_ACCESS_TOKEN
- **Expected Response** (example):
```json
{
    "summary": {
        "total_inventory_value": 10399.92,
        "total_products": 1,
        "total_stores": 1
    },
    "top_categories": [
        {
            "category": "Electronics",
            "total_quantity": 8,
            "total_value": 10399.92
        }
    ],
    "top_stores": [
        {
            "id": 1,
            "name": "Main Street Store",
            "total_quantity": 8,
            "total_value": 10399.92
        }
    ]
}
```

### Testing Flow for Beginners

Use this sequence of API calls to test the system:

1. **Login** to get your access token
2. **List stores** to see existing stores
3. **Create a new store**
4. **List products** to see existing products
5. **Create a new product**
6. **Stock in** the new product
7. **View inventory** for a store
8. **Record a sale**
9. **Check low stock report** to see if any products need restocking
10. **Review inventory summary** to get overall value

## Troubleshooting

### Common Issues and Solutions

1. **Authentication Errors**:
   - Ensure you're using the correct token
   - Check that you've prefixed the token with "Bearer "
   - Tokens expire after 1 hour; get a new token if needed

2. **404 Not Found Errors**:
   - Double-check the URL (remember to include `/api/v2/` in all paths)
   - Ensure you're using the correct HTTP method (GET, POST, etc.)

3. **Database Connection Issues**:
   - Ensure PostgreSQL container is running
   - Check the database logs: `docker-compose logs db`

4. **Container Won't Start**:
   - Try rebuilding: `docker-compose build --no-cache`
   - Check for port conflicts: something might already be using port 5000


## Design Decisions

### Multi-Store Architecture
- **Central Product Catalog:** All stores share a common product database, enabling consistent product information across the organization
- **Store-Specific Inventory:** Each store maintains separate inventory records, allowing for location-specific stock management
- **Event-Based Stock Movement:** All inventory changes are tracked as events with timestamps, users, and references for complete audit trail

### Database Design
- **Relational Database:** Chose PostgreSQL for ACID compliance, transaction support, and better concurrency handling
- **Normalization:** Database schema follows proper normalization principles to avoid data redundancy
- **Foreign Key Constraints:** Enforces data integrity across related tables
- **Timestamp Tracking:** All entities include created_at and updated_at fields for audit and tracking

### Security Implementation
- **JWT Authentication:** Secure, stateless authentication using JSON Web Tokens
- **Role-Based Access Control:** Three primary roles - admin, store_manager, and store_user
- **Store-Based Permissions:** Users have access only to their assigned stores (except admins)
- **Password Hashing:** Passwords are securely hashed and never stored in plain text
- **Rate Limiting:** API endpoints are protected against brute force and DoS attacks

### Containerization Strategy
- **Docker Isolation:** Each component runs in its own container for better isolation and scalability
- **Simplified Deployment:** Docker Compose orchestration simplifies setup across environments
- **Environment Consistency:** Ensures consistent behavior across development and production
- **Volume Persistence:** Database data persists across container restarts

## Key Assumptions
- **Internet Connectivity:** Assumes reliable internet connectivity for API communications between stores
- **Data Volume:** System can handle moderate transaction volumes (up to thousands per day per store)
- **Concurrency:** Multiple users may access the system simultaneously from different stores
- **Transaction Size:** Most inventory operations involve reasonable quantities (not millions of items in a single transaction)
- **Product Uniqueness:** Products are unique across the entire organization with a single central catalog
- **User Access Patterns:** Store users primarily access their own store's data, while admins need cross-store visibility

## API Design

### Design Principles
- **RESTful Architecture:** Clear resource-oriented design with appropriate HTTP methods
- **Versioning:** All endpoints prefixed with `/api/v2/` to allow future version changes
- **Consistent Response Format:** Standardized success and error response structures
- **Pagination:** All list endpoints support pagination to handle large data sets
- **Filtering:** Flexible query parameters for filtering data
- **Authentication:** JWT-based with refresh token capability
- **Documentation:** Comprehensive API documentation with examples

### Endpoint Structure
- **Authentication Endpoints:** `/api/v2/auth/*` for login, registration, token refresh
- **Product Endpoints:** `/api/v2/products/*` for central catalog management
- **Inventory Endpoints:** `/api/v2/inventory/*` for stock management
- **Store Endpoints:** `/api/v2/stores/*` for store management
- **Reporting Endpoints:** `/api/v2/reports/*` for analytics and insights

### Security Measures
- **Input Validation:** All request data is validated before processing
- **Rate Limiting:** Prevents API abuse with per-endpoint limits
- **Authorization Middleware:** Enforces access control at the route level
- **Secure Headers:** Properly configured security headers

## Evolution Rationale (v1 → v2)

### Architectural Evolution
- **From Monolith to API Service:**
  - v1: Single-application monolith with direct HTML rendering
  - v2: API-first design with separation of concerns, enabling multiple front-end options
- **From Single to Multi-Store:**
  - v1: Limited to a single store's inventory
  - v2: Supports multiple stores sharing a central product catalog
- **From Basic to Advanced Security:**
  - v1: Simple session-based authentication
  - v2: JWT-based authentication with role-based access control
- **From File-based to Relational Database:**
  - v1: SQLite for simplicity
  - v2: PostgreSQL for scalability and concurrency

### Technical Implementation Changes
- **Database Migration:**
  - Enhanced schema with store-related tables
  - Added foreign key relationships
  - Improved indexing strategy
- **Authentication System:**
  - Implemented JWT token-based authentication
  - Added token refresh mechanism
  - Created role-based authorization
- **API Structure:**
  - Organized endpoints into logical blueprints
  - Added versioning support
  - Implemented consistent response formatting
- **Containerization:**
  - Added Docker and Docker Compose
  - Created separate containers for API, database, and cache
  - Implemented volume persistence
- **Performance Enhancements:**
  - Added Redis for rate limiting and caching
  - Implemented database connection pooling
  - Optimized query patterns