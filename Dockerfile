FROM python:3.13-slim

LABEL maintainer="Sean Cohmer"
LABEL description="Maintenance Logger Server"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml uv.lock ./

# Install UV package manager for faster installs
RUN pip install uv

# Install Python dependencies
RUN uv sync --frozen

# Copy application files
COPY main.py ./
COPY templates/ ./templates/

# Create directory for database and ensure proper permissions
RUN mkdir -p /app/data && \
    touch /app/data/maintenance_logs.db && \
    chown -R 1000:1000 /app/data

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/log', timeout=5)" || exit 1

# Run the application
CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]