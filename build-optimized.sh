#!/bin/bash

# Advanced Docker build optimization script
# This script uses multiple techniques to minimize image size

set -e

IMAGE_NAME="pronoun-proofer"
DOCKERFILE="Dockerfile"

echo "Building optimized Docker image..."

# Strategy 1: Use BuildKit for advanced optimization
export DOCKER_BUILDKIT=1

echo "Step 1: Building multi-stage image with BuildKit..."
docker build \
    --platform linux/amd64 \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --target final \
    -t ${IMAGE_NAME}:latest \
    -f ${DOCKERFILE} \
    .

# Strategy 2: Create a squashed version (if supported)
echo "Step 2: Attempting to squash layers..."
docker build \
    --platform linux/amd64 \
    --squash \
    -t ${IMAGE_NAME}:squashed \
    -f ${DOCKERFILE} \
    . 2>/dev/null || echo "Squash not supported, continuing..."

# Strategy 3: Export and reimport to remove unused layers
echo "Step 3: Export/import optimization..."
docker save ${IMAGE_NAME}:latest | docker load

# Strategy 4: Show size comparison
echo "Image size analysis:"
docker images | grep ${IMAGE_NAME}

echo "Build complete! Use the smallest image for deployment."
echo "Railway will use ${IMAGE_NAME}:latest by default"
