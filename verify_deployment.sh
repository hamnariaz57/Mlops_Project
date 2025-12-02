#!/bin/bash
# Deployment Verification Script
# This script verifies that the containerized service works correctly

set -e

IMAGE_NAME="${1:-exchange-rate-model:latest}"
CONTAINER_NAME="exchange-rate-test"
PORT=8000

echo "=========================================="
echo "Deployment Verification"
echo "=========================================="

# Clean up any existing container
echo "Cleaning up existing containers..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Step 1: Run the container
echo ""
echo "Step 1: Starting container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:8000 \
    -e MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-https://dagshub.com/hamnariaz57/Mlops_Project.mlflow}" \
    -e DAGSHUB_USERNAME="${DAGSHUB_USERNAME:-MuhammadAwaisRafique}" \
    -e DAGSHUB_TOKEN="${DAGSHUB_TOKEN}" \
    $IMAGE_NAME

echo "✓ Container started"

# Step 2: Wait for service to be ready
echo ""
echo "Step 2: Waiting for service to be ready..."
sleep 10

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
        echo "✓ Service is ready"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Waiting... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "✗ Service failed to start"
    docker logs $CONTAINER_NAME
    docker stop $CONTAINER_NAME
    exit 1
fi

# Step 3: Health check
echo ""
echo "Step 3: Running health check..."
HEALTH_RESPONSE=$(curl -s http://localhost:$PORT/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✓ Health check passed"
    echo "  Response: $HEALTH_RESPONSE"
else
    echo "✗ Health check failed"
    echo "  Response: $HEALTH_RESPONSE"
    docker logs $CONTAINER_NAME
    docker stop $CONTAINER_NAME
    exit 1
fi

# Step 4: Test prediction endpoint
echo ""
echo "Step 4: Testing prediction endpoint..."
PREDICTION_RESPONSE=$(curl -s -X POST http://localhost:$PORT/predict \
    -H "Content-Type: application/json" \
    -d '{"history": [0.85, 0.86, 0.87]}')

if echo "$PREDICTION_RESPONSE" | grep -q "prediction"; then
    echo "✓ Prediction endpoint working"
    echo "  Response: $PREDICTION_RESPONSE"
else
    echo "✗ Prediction endpoint failed"
    echo "  Response: $PREDICTION_RESPONSE"
    docker logs $CONTAINER_NAME
    docker stop $CONTAINER_NAME
    exit 1
fi

# Step 5: Test root endpoint
echo ""
echo "Step 5: Testing root endpoint..."
ROOT_RESPONSE=$(curl -s http://localhost:$PORT/)
if echo "$ROOT_RESPONSE" | grep -q "Running"; then
    echo "✓ Root endpoint working"
    echo "  Response: $ROOT_RESPONSE"
else
    echo "✗ Root endpoint failed"
    echo "  Response: $ROOT_RESPONSE"
fi

# Cleanup
echo ""
echo "Step 6: Cleaning up..."
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME

echo ""
echo "=========================================="
echo "✓ All verification tests passed!"
echo "=========================================="
echo "The containerized service is working correctly."
echo "You can deploy it using:"
echo "  docker run -d -p 8000:8000 $IMAGE_NAME"

