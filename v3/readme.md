# Bazaar Inventory Management System v3 - Phase 1: Containerization & Load Balancing

## Overview

In **Phase 1**, the application has been containerized using Docker and set up for multi-container deployment using Docker Compose. Nginx is configured as a load balancer to distribute traffic across multiple backend API instances. Additionally, a health check endpoint has been implemented to monitor the status of the application containers.

## What has been done in Phase 1?

- **Dockerized the Application**: The application is now containerized using Docker. This allows for easy deployment, scaling, and consistency across environments.
  
- **Multi-Container Setup with Docker Compose**: 
  - A **backend API** is containerized to handle inventory management logic.
  - **Nginx** is configured as a reverse proxy and load balancer to distribute incoming traffic across multiple API instances.
  - A **PostgreSQL** database is used for storing product and inventory data.

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

As always you can interact with the Inventory system like you did in v2, for more information please check readme file in that folder. 

If you want to test the previous functionality make sure you :
Ensure that Postman points to Nginx, not directly to the backend API. Try using:

http://localhost/api/v2/auth/login


instead of  

http://localhost:5000/api/v2/auth/login


