# FROM python:3

# WORKDIR /usr/src/app

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# CMD [ "python", "./your-daemon-or-script.py" ]

# taken from https://hub.docker.com/_/python



FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

# Install Python dependencies with explicit versions
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 5000

# Run the application using Python directly
CMD ["python", "-c", "from app import app; app.run(host='0.0.0.0', port=5000)"]