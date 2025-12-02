#!/bin/bash

# Start Monitoring Stack Script
# This script starts Prometheus, Grafana, and the FastAPI service

echo "=========================================="
echo "Starting MLOps Monitoring Stack"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if models directory exists
if [ ! -d "models" ]; then
    echo "⚠️  Warning: models/ directory not found."
    echo "   Creating directory..."
    mkdir -p models
fi

# Check if training_stats.json exists
if [ ! -f "models/training_stats.json" ]; then
    echo "⚠️  Warning: models/training_stats.json not found."
    echo "   Data drift detection will be disabled."
    echo "   Run 'python train_model.py' to generate training statistics."
    echo ""
fi

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.monitoring.yml up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check service health
echo ""
echo "📊 Checking service status..."
docker-compose -f docker-compose.monitoring.yml ps

echo ""
echo "=========================================="
echo "✅ Monitoring Stack Started!"
echo "=========================================="
echo ""
echo "Access the services:"
echo "  📈 FastAPI Service:  http://localhost:8000"
echo "  📊 Prometheus:        http://localhost:9090"
echo "  📉 Grafana:           http://localhost:3000"
echo ""
echo "Grafana credentials:"
echo "  Username: admin"
echo "  Password: admin"
echo ""
echo "View logs:"
echo "  docker-compose -f docker-compose.monitoring.yml logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose -f docker-compose.monitoring.yml down"
echo ""

