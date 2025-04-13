# FROM python:3

# WORKDIR /usr/src/app

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# CMD [ "python", "./your-daemon-or-script.py" ]

# taken from https://hub.docker.com/_/python



# Production-optimized Dockerfile
FROM python:3.10-slim AS builder

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install dependencies into a virtual environment
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Production image
FROM python:3.10-slim

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

WORKDIR /app

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "app:app"]