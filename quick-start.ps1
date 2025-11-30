# Quick Start Commands for MLOps Phase 1
# Windows PowerShell

# ============================================
# FIRST TIME SETUP (Run once)
# ============================================

# 1. Create environment file from template
Copy-Item .env.example .env
Write-Host "✓ Created .env file - Please edit and add your DAGSHUB_TOKEN" -ForegroundColor Green

# 2. Build custom Airflow Docker image with dependencies
Write-Host "`n🔨 Building custom Airflow image..." -ForegroundColor Cyan
docker-compose build

# 3. Start all services (Airflow, PostgreSQL, MLflow)
Write-Host "`n🚀 Starting all services..." -ForegroundColor Cyan
docker-compose up -d

# 4. Wait for initialization
Write-Host "`n⏳ Waiting for services to initialize (2 minutes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 120

# 5. Check service status
Write-Host "`n📊 Checking service status..." -ForegroundColor Cyan
docker-compose ps

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`nAccess points:" -ForegroundColor Cyan
Write-Host "  - Airflow UI: http://localhost:8080 (admin/admin)" -ForegroundColor White
Write-Host "  - MLflow UI:  http://localhost:5000" -ForegroundColor White

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:8080" -ForegroundColor White
Write-Host "  2. Login with admin/admin" -ForegroundColor White
Write-Host "  3. Find DAG: exchange_rate_mlops_pipeline_phase1" -ForegroundColor White
Write-Host "  4. Toggle it ON and trigger manually" -ForegroundColor White

# ============================================
# REGULAR USAGE COMMANDS
# ============================================

# Start services (after first setup)
# docker-compose up -d

# Stop services
# docker-compose down

# View logs
# docker-compose logs -f airflow-scheduler

# Trigger DAG manually
# docker-compose exec airflow-scheduler airflow dags trigger exchange_rate_mlops_pipeline_phase1

# Check DAG status
# docker-compose exec airflow-scheduler airflow dags list

# Access scheduler shell
# docker-compose exec airflow-scheduler bash
