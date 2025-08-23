# Advanced multi-stage build with aggressive layer optimization
# Strategy: Build everything, compress, then copy compressed result

# Stage 1: Dependency installation and aggressive compression
FROM python:3.11.5-slim as deps-builder

WORKDIR /build

# Install build tools and compression utilities
RUN apt-get update && apt-get install -y \
    gcc g++ \
    upx-ucl \
    binutils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies in one massive RUN command to minimize layers
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --target=/deps -r requirements.txt && \
    # PHASE 1: Remove obvious bloat
    find /deps -name "*.pyc" -delete && \
    find /deps -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /deps -name "*.pyo" -delete && \
    find /deps -name "*.pyd" -delete && \
    # PHASE 2: Remove development/testing artifacts
    find /deps -name "test*" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /deps -name "*test*" -name "*.py" -delete 2>/dev/null || true && \
    find /deps -name "docs" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /deps -name "doc" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /deps -name "examples" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /deps -name "example" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /deps -name "*.md" -delete && \
    find /deps -name "*.rst" -delete && \
    find /deps -name "*.txt" -delete && \
    find /deps -name "LICENSE*" -delete && \
    find /deps -name "COPYING*" -delete && \
    find /deps -name "CHANGELOG*" -delete && \
    find /deps -name "NEWS*" -delete && \
    # PHASE 3: Aggressive binary stripping and compression
    find /deps -name "*.so" -exec strip --strip-unneeded {} \; 2>/dev/null || true && \
    find /deps -name "*.so.*" -exec strip --strip-unneeded {} \; 2>/dev/null || true && \
    # PHASE 4: Remove package metadata (saves significant space)
    rm -rf /deps/*.dist-info /deps/*.egg-info 2>/dev/null || true && \
    # PHASE 5: Remove specific heavy components
    rm -rf /deps/torch/include /deps/torch/share /deps/torch/test 2>/dev/null || true && \
    rm -rf /deps/numpy/tests /deps/numpy/doc 2>/dev/null || true && \
    rm -rf /deps/spacy/tests 2>/dev/null || true && \
    # PHASE 6: Compress binaries with UPX (can save 40-60% on binaries)
    find /deps -name "*.so" -size +1M -exec upx --best --lzma {} \; 2>/dev/null || true && \
    # PHASE 7: Create compressed tarball of entire deps
    tar -czf /build/deps.tar.gz -C /deps . && \
    rm -rf /deps

# Stage 2: Decompress in Alpine (has tar), then copy to distroless
FROM alpine:3.18 as decompressor
RUN apk add --no-cache tar gzip
COPY --from=deps-builder /build/deps.tar.gz /tmp/
RUN mkdir -p /final-deps && \
    tar -xzf /tmp/deps.tar.gz -C /final-deps/ && \
    rm /tmp/deps.tar.gz

# Stage 3: Ultra-minimal runtime
FROM gcr.io/distroless/python3-debian11

WORKDIR /app

# Copy decompressed dependencies
COPY --from=decompressor /final-deps /usr/local/lib/python3.11/site-packages

# Copy application code (minimal)
COPY bot.py .
COPY src/ ./src/

# Optimize environment for maximum performance and minimal overhead
ENV PYTHONPATH=/app:/usr/local/lib/python3.11/site-packages \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONOPTIMIZE=2 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1

CMD ["python", "bot.py"]
