#!/bin/bash
# Build and Deploy Script for Model Service
# This script fetches the best model from MLflow and builds the Docker image

set -e  # Exit on error

# Configuration
DOCKER_IMAGE_NAME="exchange-rate-model"
DOCKER_USERNAME="${DOCKER_USERNAME:-your-username}"  # Set your Docker Hub username
VERSION="${1:-v1.0.0}"  # Version tag, default v1.0.0

echo "=========================================="
echo "Building and Deploying Model Service"
echo "=========================================="

# Step 1: Fetch best model from MLflow
echo "Step 1: Fetching best model from MLflow..."
python fetch_model.py > model_info.txt

RUN_ID=$(grep "MLFLOW_RUN_ID=" model_info.txt | cut -d'=' -f2)
MODEL_PATH=$(grep "MODEL_PATH=" model_info.txt | cut -d'=' -f2)

if [ -z "$RUN_ID" ]; then
    echo "Error: Failed to fetch model run ID"
    exit 1
fi

echo "✓ Model fetched from run: $RUN_ID"
echo "✓ Model path: $MODEL_PATH"

# Step 2: Build Docker image
echo ""
echo "Step 2: Building Docker image..."
docker build \
    -f Dockerfile.model \
    --build-arg MLFLOW_RUN_ID="$RUN_ID" \
    --build-arg MODEL_PATH="/app/models/rf_model.pkl" \
    -t "$DOCKER_USERNAME/$DOCKER_IMAGE_NAME:$VERSION" \
    -t "$DOCKER_USERNAME/$DOCKER_IMAGE_NAME:latest" \
    .

echo "✓ Docker image built successfully"

# Step 3: Push to Docker Hub (optional)
read -p "Push image to Docker Hub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Step 3: Pushing to Docker Hub..."
    docker push "$DOCKER_USERNAME/$DOCKER_IMAGE_NAME:$VERSION"
    docker push "$DOCKER_USERNAME/$DOCKER_IMAGE_NAME:latest"
    echo "✓ Image pushed successfully"
else
    echo "Skipping push to Docker Hub"
fi

echo ""
echo "=========================================="
echo "Build Complete!"
echo "=========================================="
echo "Image: $DOCKER_USERNAME/$DOCKER_IMAGE_NAME:$VERSION"
echo "To run: docker run -p 8000:8000 $DOCKER_USERNAME/$DOCKER_IMAGE_NAME:$VERSION"

