# syntax=docker/dockerfile:1

# Use the latest official Python image as base
FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY dashboards/ ./dashboards/
COPY .env ./

# Expose port
EXPOSE 8000

# Healthcheck (optional, for Docker Compose/K8s)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI app with Uvicorn
CMD ["python", "-m", "src.main", "run"]