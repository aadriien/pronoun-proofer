# ULTRA-AGGRESSIVE Docker optimization
# This approach uses extreme compression and minimal base images

# Stage 1: Build in minimal Alpine environment
FROM alpine:3.18 as builder

# Install Python and build tools
RUN apk add --no-cache \
    python3=~3.11 \
    python3-dev \
    py3-pip \
    gcc \
    musl-dev \
    linux-headers \
    upx \
    && ln -sf python3 /usr/bin/python

WORKDIR /build

# Install dependencies with aggressive optimization
COPY requirements.txt .
RUN pip3 install --no-cache-dir --target=/deps -r requirements.txt && \
    # Remove ALL unnecessary files in single pass
    find /deps \( \
        -name "*.pyc" -o \
        -name "*.pyo" -o \
        -name "__pycache__" -o \
        -name "test*" -o \
        -name "*test*" -o \
        -name "docs" -o \
        -name "examples" -o \
        -name "*.md" -o \
        -name "*.rst" -o \
        -name "*.txt" -o \
        -name "LICENSE*" -o \
        -name "*.dist-info" -o \
        -name "*.egg-info" \
    \) -exec rm -rf {} + 2>/dev/null || true && \
    # Strip and compress ALL binaries
    find /deps -name "*.so*" -exec strip {} \; 2>/dev/null || true && \
    find /deps -name "*.so*" -size +500k -exec upx --best --lzma {} \; 2>/dev/null || true && \
    # Remove torch extras
    rm -rf /deps/torch/{include,share,test} /deps/torch/lib/*.a 2>/dev/null || true

# Copy application code
COPY bot.py /build/
COPY src/ /build/src/

# Stage 2: Create absolute minimal runtime
FROM gcr.io/distroless/python3-debian11:nonroot

WORKDIR /app

# Copy optimized dependencies and code
COPY --from=builder /deps /usr/local/lib/python3.11/site-packages
COPY --from=builder /build/bot.py .
COPY --from=builder /build/src ./src

# Extreme optimization environment
ENV PYTHONPATH=/app:/usr/local/lib/python3.11/site-packages \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=2 \
    PYTHONHASHSEED=0 \
    MALLOC_ARENA_MAX=1

# Use nonroot user from distroless for security
USER nonroot:nonroot

CMD ["python", "bot.py"]
