# PowerShell Deployment Script for Windows
# This script builds and verifies the Docker container

param(
    [string]$ImageName = "exchange-rate-model:latest",
    [string]$Version = "v1.0.0",
    [string]$DockerUsername = "your-username"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Building and Deploying Model Service" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Step 1: Fetch best model
Write-Host "`nStep 1: Fetching best model from MLflow..." -ForegroundColor Yellow
python fetch_model.py | Out-File -FilePath model_info.txt -Encoding utf8

$modelInfo = Get-Content model_info.txt
$runId = ($modelInfo | Select-String "MLFLOW_RUN_ID=").ToString().Split('=')[1]
$modelPath = ($modelInfo | Select-String "MODEL_PATH=").ToString().Split('=')[1]

if ([string]::IsNullOrEmpty($runId)) {
    Write-Host "Error: Failed to fetch model run ID" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Model fetched from run: $runId" -ForegroundColor Green
Write-Host "✓ Model path: $modelPath" -ForegroundColor Green

# Step 2: Build Docker image
Write-Host "`nStep 2: Building Docker image..." -ForegroundColor Yellow
docker build `
    -f Dockerfile.model `
    --build-arg MLFLOW_RUN_ID="$runId" `
    --build-arg MODEL_PATH="/app/models/rf_model.pkl" `
    -t "$DockerUsername/$ImageName`:$Version" `
    -t "$DockerUsername/$ImageName`:latest" `
    .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker build failed" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker image built successfully" -ForegroundColor Green

# Step 3: Verify deployment
Write-Host "`nStep 3: Verifying deployment..." -ForegroundColor Yellow

# Clean up existing container
docker stop exchange-rate-test 2>$null
docker rm exchange-rate-test 2>$null

# Run container
Write-Host "  Starting container..." -ForegroundColor Gray
docker run -d `
    --name exchange-rate-test `
    -p 8000:8000 `
    -e MLFLOW_TRACKING_URI="$env:MLFLOW_TRACKING_URI" `
    -e DAGSHUB_USERNAME="$env:DAGSHUB_USERNAME" `
    -e DAGSHUB_TOKEN="$env:DAGSHUB_TOKEN" `
    "$DockerUsername/$ImageName`:latest" | Out-Null

Start-Sleep -Seconds 10

# Health check
$maxRetries = 30
$retryCount = 0
$healthCheckPassed = $false

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Health check passed" -ForegroundColor Green
            $healthCheckPassed = $true
            break
        }
    } catch {
        $retryCount++
        Write-Host "  Waiting... ($retryCount/$maxRetries)" -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $healthCheckPassed) {
    Write-Host "✗ Health check failed" -ForegroundColor Red
    docker logs exchange-rate-test
    docker stop exchange-rate-test
    docker rm exchange-rate-test
    exit 1
}

# Test prediction
Write-Host "  Testing prediction endpoint..." -ForegroundColor Gray
try {
    $body = @{
        history = @(0.85, 0.86, 0.87)
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8000/predict" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body

    Write-Host "✓ Prediction endpoint working" -ForegroundColor Green
    Write-Host "  Response: $($response | ConvertTo-Json)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Prediction endpoint failed: $_" -ForegroundColor Red
    docker logs exchange-rate-test
    docker stop exchange-rate-test
    docker rm exchange-rate-test
    exit 1
}

# Cleanup
Write-Host "`nCleaning up test container..." -ForegroundColor Yellow
docker stop exchange-rate-test
docker rm exchange-rate-test

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✓ Deployment verification complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Image: $DockerUsername/$ImageName`:$Version" -ForegroundColor Yellow
Write-Host "To run: docker run -d -p 8000:8000 $DockerUsername/$ImageName`:latest" -ForegroundColor Yellow

