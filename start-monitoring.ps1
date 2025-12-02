# Start Monitoring Stack Script (PowerShell)
# This script starts Prometheus, Grafana, and the FastAPI service

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting MLOps Monitoring Stack" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Error: Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Check if models directory exists
if (-not (Test-Path "models")) {
    Write-Host "⚠️  Warning: models/ directory not found." -ForegroundColor Yellow
    Write-Host "   Creating directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "models" | Out-Null
}

# Check if training_stats.json exists
if (-not (Test-Path "models/training_stats.json")) {
    Write-Host "⚠️  Warning: models/training_stats.json not found." -ForegroundColor Yellow
    Write-Host "   Data drift detection will be disabled." -ForegroundColor Yellow
    Write-Host "   Run 'python train_model.py' to generate training statistics." -ForegroundColor Yellow
    Write-Host ""
}

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Green
docker-compose -f docker-compose.monitoring.yml up -d

Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check service health
Write-Host ""
Write-Host "📊 Checking service status..." -ForegroundColor Cyan
docker-compose -f docker-compose.monitoring.yml ps

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Monitoring Stack Started!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the services:" -ForegroundColor White
Write-Host "  📈 FastAPI Service:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  📊 Prometheus:        http://localhost:9090" -ForegroundColor Cyan
Write-Host "  📉 Grafana:           http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Grafana credentials:" -ForegroundColor White
Write-Host "  Username: admin" -ForegroundColor Yellow
Write-Host "  Password: admin" -ForegroundColor Yellow
Write-Host ""
Write-Host "View logs:" -ForegroundColor White
Write-Host "  docker-compose -f docker-compose.monitoring.yml logs -f" -ForegroundColor Gray
Write-Host ""
Write-Host "Stop services:" -ForegroundColor White
Write-Host "  docker-compose -f docker-compose.monitoring.yml down" -ForegroundColor Gray
Write-Host ""

