# Multi-stage build to minimize final image size

# Stage 1: Build dependencies
FROM python:3.11.5-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --target=/app/dependencies -r requirements.txt

# Stage 2: Runtime image
FROM python:3.11.5-slim

WORKDIR /app

# Copy only the installed packages from builder stage
COPY --from=builder /app/dependencies /usr/local/lib/python3.11/site-packages

# Copy only necessary application code
COPY bot.py .
COPY src/ ./src/

# Aggressive cleanup - remove unnecessary files from packages
RUN find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete && \
    find /usr/local/lib/python3.11/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -name "test" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.11/site-packages -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true

# Set environment variables for optimization
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE ${PORT:-8000}

# Run the application
CMD ["python", "bot.py"]
