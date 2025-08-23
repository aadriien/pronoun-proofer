# Use slim Python base image to reduce size
FROM python:3.11.5-slim

# Set working directory
WORKDIR /app

# Install system dependencies in a single layer and clean up
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies and clean up in single layer
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete && \
    find /usr/local/lib/python3.11/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Copy only the necessary application code (excluding coref/ folder)
COPY bot.py .
COPY src/ ./src/

# Set environment variables for optimization
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port (Railway uses PORT env var)
EXPOSE ${PORT:-8000}

# Run the application
CMD ["python", "bot.py"]
