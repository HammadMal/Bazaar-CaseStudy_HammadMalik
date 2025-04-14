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
cd bazaar-inventory-v2
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

## Evolution from Stage 1 to Stage 2

The key improvements in Stage 2 include:

1. **Multi-store Architecture**: From single store to multiple store support
2. **API-first Design**: Built as an API service rather than a monolithic web app
3. **Production-ready Database**: PostgreSQL instead of SQLite
4. **Authentication System**: Added user management and authentication
5. **Docker Containerization**: For consistent deployment
6. **Comprehensive Reporting**: Added detailed reporting capabilities