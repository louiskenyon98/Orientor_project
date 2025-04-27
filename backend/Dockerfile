# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 
# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies with optimized settings for ML libraries
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8000/api/health || exit 1' > /healthcheck.sh && \
    chmod +x /healthcheck.sh

# Healthcheck using the script
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD /healthcheck.sh

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "run.py"]
