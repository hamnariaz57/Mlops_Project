# Deployment Guide

This guide covers containerization and deployment of the Exchange Rate Forecast Model Service.

## Overview

The model service is containerized using Docker and can be deployed via:
1. **Local Docker Build** - Build and run locally
2. **Docker Hub** - Push to registry and pull for deployment
3. **GitHub Actions CD** - Automated CI/CD pipeline

## Prerequisites

- Docker installed and running
- MLflow credentials configured (DAGSHUB_USERNAME, DAGSHUB_TOKEN)
- At least one trained model in MLflow Model Registry

## Quick Start

### Option 1: Local Build and Run (Windows PowerShell)

```powershell
# 1. Fetch best model and build Docker image
.\deploy.ps1 -DockerUsername "your-dockerhub-username" -Version "v1.0.0"

# 2. Run the container
docker run -d -p 8000:8000 `
    -e DAGSHUB_USERNAME="your-username" `
    -e DAGSHUB_TOKEN="your-token" `
    your-dockerhub-username/exchange-rate-model:latest
```

### Option 2: Local Build and Run (Linux/Mac)

```bash
# 1. Make scripts executable
chmod +x build_and_deploy.sh verify_deployment.sh

# 2. Build and deploy
./build_and_deploy.sh

# 3. Run the container
docker run -d -p 8000:8000 \
    -e DAGSHUB_USERNAME="your-username" \
    -e DAGSHUB_TOKEN="your-token" \
    your-username/exchange-rate-model:latest
```

### Option 3: Manual Build

```bash
# 1. Fetch best model
python fetch_model.py

# 2. Build Docker image
docker build -f Dockerfile.model \
    --build-arg MLFLOW_RUN_ID="<run-id-from-fetch>" \
    -t exchange-rate-model:latest .

# 3. Run container
docker run -d -p 8000:8000 \
    -e DAGSHUB_USERNAME="your-username" \
    -e DAGSHUB_TOKEN="your-token" \
    exchange-rate-model:latest
```

## Verification

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "model_loaded": true}
```

### Test Prediction

```bash
curl -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"history": [0.85, 0.86, 0.87]}'
```

Expected response:
```json
{"prediction": 0.88}
```

### Automated Verification

```bash
# Linux/Mac
./verify_deployment.sh exchange-rate-model:latest

# Windows PowerShell
# Use deploy.ps1 which includes verification
```

## Continuous Delivery (CD) Pipeline

### GitHub Actions Setup

1. **Add Secrets to GitHub Repository:**
   - Go to Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `DOCKER_USERNAME` - Your Docker Hub username
     - `DOCKER_PASSWORD` - Your Docker Hub password/token
     - `MLFLOW_TRACKING_URI` - MLflow tracking URI
     - `DAGSHUB_USERNAME` - DagHub username
     - `DAGSHUB_TOKEN` - DagHub token

2. **Trigger CD Pipeline:**
   - Push to `master` or `main` branch
   - Or manually trigger via GitHub Actions UI

3. **Pipeline Steps:**
   - Fetches best model from MLflow
   - Builds Docker image
   - Tags image with version and latest
   - Pushes to Docker Hub
   - Verifies deployment

### CD Pipeline Output

After successful run, you'll have:
- Image: `docker.io/<username>/exchange-rate-model:latest`
- Image: `docker.io/<username>/exchange-rate-model:v1.0.0`
- Image: `docker.io/<username>/exchange-rate-model:<commit-sha>`

## Deployment to Production

### Docker Run

```bash
docker run -d \
    --name exchange-rate-api \
    -p 8000:8000 \
    -e DAGSHUB_USERNAME="your-username" \
    -e DAGSHUB_TOKEN="your-token" \
    -e MLFLOW_TRACKING_URI="https://dagshub.com/hamnariaz57/Mlops_Project.mlflow" \
    --restart unless-stopped \
    your-username/exchange-rate-model:latest
```

### Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'
services:
  model-api:
    image: your-username/exchange-rate-model:latest
    ports:
      - "8000:8000"
    environment:
      - DAGSHUB_USERNAME=${DAGSHUB_USERNAME}
      - DAGSHUB_TOKEN=${DAGSHUB_TOKEN}
      - MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## API Endpoints

### GET `/`
Health check and service info.

**Response:**
```json
{
  "message": "Exchange Rate Forecast API Running",
  "status": "healthy",
  "model_loaded": true
}
```

### GET `/health`
Health check endpoint for Docker/Kubernetes.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### POST `/predict`
Predict exchange rate based on historical values.

**Request:**
```json
{
  "history": [0.85, 0.86, 0.87]
}
```

**Response:**
```json
{
  "prediction": 0.88
}
```

## Troubleshooting

### Model Not Loading

1. Check environment variables:
   ```bash
   docker exec <container> env | grep MLFLOW
   ```

2. Check logs:
   ```bash
   docker logs <container>
   ```

3. Verify model exists in MLflow:
   ```bash
   python fetch_model.py
   ```

### Container Won't Start

1. Check Docker logs:
   ```bash
   docker logs <container>
   ```

2. Verify port is available:
   ```bash
   netstat -an | grep 8000
   ```

3. Check health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```

### CD Pipeline Fails

1. Check GitHub Actions logs
2. Verify all secrets are set correctly
3. Ensure MLflow has at least one trained model
4. Check Docker Hub credentials

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MLFLOW_TRACKING_URI` | MLflow tracking server URI | `https://dagshub.com/hamnariaz57/Mlops_Project.mlflow` |
| `DAGSHUB_USERNAME` | DagHub username | - |
| `DAGSHUB_TOKEN` | DagHub access token | - |
| `MODEL_PATH` | Path to model file in container | `/app/models/rf_model.pkl` |
| `MLFLOW_RUN_ID` | Specific MLflow run ID (optional) | - |

## Versioning

Images are tagged with:
- `latest` - Always points to most recent build
- `v1.0.0` - Semantic version
- `<commit-sha>` - Git commit SHA for traceability

## Security Notes

- Never commit `.env` files with secrets
- Use Docker secrets or environment variables for credentials
- Regularly update base images for security patches
- Use specific version tags in production (not `latest`)

