# Multi-stage build with ultra-minimal final image

# Stage 1: Build dependencies
FROM python:3.11.5-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies to a specific directory
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --target=/build/deps -r requirements.txt && \
    # Ultra-aggressive cleanup to save space
    find /build/deps -name "*.pyc" -delete && \
    find /build/deps -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /build/deps -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /build/deps -name "test" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /build/deps -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /build/deps -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /build/deps -name "*.so" -exec strip {} \; 2>/dev/null || true && \
    # Remove documentation and examples
    find /build/deps -name "docs" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /build/deps -name "doc" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /build/deps -name "examples" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /build/deps -name "example" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /build/deps -name "*.md" -delete && \
    find /build/deps -name "*.rst" -delete && \
    find /build/deps -name "*.txt" -delete && \
    # Remove unused torch/transformers components (keeping only what's needed)
    find /build/deps -name "torch/include" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /build/deps -name "torch/share" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /build/deps -name "transformers/models" -type d -exec find {} -name "*.bin" -delete \; 2>/dev/null || true && \
    # Remove pytest since it's not needed in production
    rm -rf /build/deps/pytest* /build/deps/_pytest* /build/deps/pluggy* 2>/dev/null || true && \
    # Remove flask since you're not running a web server
    rm -rf /build/deps/flask* /build/deps/werkzeug* /build/deps/jinja2* /build/deps/click* /build/deps/itsdangerous* 2>/dev/null || true && \
    # Remove large numpy components not needed
    find /build/deps/numpy -name "*.so" -exec strip {} \; 2>/dev/null || true && \
    rm -rf /build/deps/numpy/tests /build/deps/numpy/doc 2>/dev/null || true

# Stage 2: Ultra-minimal runtime
FROM gcr.io/distroless/python3-debian11

WORKDIR /app

# Copy Python packages
COPY --from=builder /build/deps /usr/local/lib/python3.11/site-packages

# Copy application code
COPY bot.py .
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app:/usr/local/lib/python3.11/site-packages
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Distroless images don't have shell, so use exec form
CMD ["python", "bot.py"]
