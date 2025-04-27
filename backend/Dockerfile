# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt && rm -rf /root/.cache/pip

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    PATH=/root/.local/bin:$PATH

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:8000/api/health || exit 1' > /healthcheck.sh && \
    chmod +x /healthcheck.sh

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD /healthcheck.sh

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["python", "run.py"]
