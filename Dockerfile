FROM python:3.11.5-slim

WORKDIR /app

# Install system dependencies and clean up in one layer
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip cache purge \
    # Remove the biggest space wasters immediately after install
    && find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete \
    && find /usr/local/lib/python3.11/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true \
    # Remove torch development files (biggest offender)
    && rm -rf /usr/local/lib/python3.11/site-packages/torch/include \
    && rm -rf /usr/local/lib/python3.11/site-packages/torch/share \
    && rm -rf /usr/local/lib/python3.11/site-packages/torch/test \
    # Remove numpy tests and docs
    && rm -rf /usr/local/lib/python3.11/site-packages/numpy/tests \
    && rm -rf /usr/local/lib/python3.11/site-packages/numpy/doc \
    # Remove all test directories
    && find /usr/local/lib/python3.11/site-packages -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.11/site-packages -name "test" -type d -exec rm -rf {} + 2>/dev/null || true \
    # Remove documentation
    && find /usr/local/lib/python3.11/site-packages -name "*.md" -delete \
    && find /usr/local/lib/python3.11/site-packages -name "*.rst" -delete \
    && find /usr/local/lib/python3.11/site-packages -name "*.txt" -delete \
    # Remove package metadata
    && find /usr/local/lib/python3.11/site-packages -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.11/site-packages -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true

# Copy only essential application code
COPY bot.py .
COPY src/ ./src/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE ${PORT:-8000}

CMD ["python", "bot.py"]
