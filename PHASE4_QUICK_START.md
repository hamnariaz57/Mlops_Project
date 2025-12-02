# Phase IV: Quick Start Guide - Monitoring is Running! ✅

## 🎉 Setup Complete!

All monitoring services are now running and ready to use!

---

## 📊 Service Access URLs

### 1. **FastAPI Prediction Service**
- **URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Metrics Endpoint**: http://localhost:8000/metrics
- **API Documentation**: http://localhost:8000/docs
- **Status**: ✅ Running and Healthy

### 2. **Prometheus (Metrics Collection)**
- **URL**: http://localhost:9090
- **Status**: ✅ Running
- **What to do here**:
  - View collected metrics
  - Query metrics using PromQL
  - Check targets (Status → Targets)
  - Explore metrics at: http://localhost:9090/graph

### 3. **Grafana (Visualization & Dashboards)**
- **URL**: http://localhost:3000
- **Username**: `admin`
- **Password**: `admin`
- **Status**: ✅ Running
- **What to do here**:
  - View monitoring dashboard
  - Configure alerts
  - Explore metrics visualization

---

## 🚀 Quick Actions

### Test the API

```powershell
# Make a prediction
$body = @{ history = @(0.85, 0.86, 0.87) } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json"
```

### View Metrics

```powershell
# Check metrics endpoint
Invoke-WebRequest -Uri "http://localhost:8000/metrics" | Select-Object -ExpandProperty Content
```

### Check Service Status

```powershell
docker-compose -f docker-compose.monitoring.yml ps
```

---

## 📈 Web-Based Setup Instructions

### Step 1: Access Grafana Dashboard

1. **Open your web browser** and go to: **http://localhost:3000**

2. **Login**:
   - Username: `admin`
   - Password: `admin`
   - Click "Log in"

3. **Access the Dashboard**:
   - Click on **"Dashboards"** in the left menu (📊 icon)
   - Look for **"MLOps Exchange Rate API - Monitoring Dashboard"**
   - Click to open it

4. **What you'll see**:
   - Real-time metrics visualization
   - Request rates, latency, data drift ratio
   - Time series charts
   - Status code distributions

### Step 2: Verify Prometheus is Scraping

1. **Open Prometheus**: http://localhost:9090

2. **Check Targets**:
   - Click **"Status"** → **"Targets"** in the top menu
   - Verify `fastapi-service` shows as **UP** (green)
   - If it shows DOWN, wait a few seconds and refresh

3. **Query Metrics**:
   - Go to **"Graph"** tab
   - Try this query: `rate(http_requests_total[5m])`
   - Click **"Execute"**
   - You should see metrics data

### Step 3: Configure Grafana Alerts (Optional)

1. **In Grafana**, go to **"Alerting"** → **"Alert rules"**

2. **Create High Latency Alert**:
   - Click **"New alert rule"**
   - **Name**: "High Inference Latency"
   - **Query A**: 
     ```
     histogram_quantile(0.95, rate(inference_latency_seconds_bucket[5m])) * 1000
     ```
   - **Condition**: `WHEN last() OF A IS ABOVE 500`
   - **For**: `5m`
   - **Summary**: "Inference latency exceeds 500ms"
   - Click **"Save"**

3. **Create Data Drift Alert**:
   - Click **"New alert rule"**
   - **Name**: "Data Drift Spike"
   - **Query A**:
     ```
     rate(data_drift_requests_total[5m]) / rate(prediction_requests_total[5m])
     ```
   - **Condition**: `WHEN last() OF A IS ABOVE 0.3`
   - **For**: `5m`
   - **Summary**: "Data drift ratio spike detected"
   - Click **"Save"**

4. **Add Notification Channel** (Optional - for Slack/Email):
   - Go to **"Alerting"** → **"Notification channels"**
   - Click **"New channel"**
   - Choose channel type (Slack, Email, etc.)
   - Configure and save
   - Add to your alert rules

### Step 4: Generate Some Traffic (To See Metrics)

1. **Make multiple API calls** to generate metrics:

```powershell
# Run this multiple times to generate traffic
for ($i=1; $i -le 10; $i++) {
    $body = @{ history = @(0.85, 0.86, 0.87) } | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json"
    Start-Sleep -Seconds 1
}
```

2. **Watch the dashboard update** in Grafana (auto-refreshes every 10 seconds)

---

## 🔍 What to Check

### ✅ Verify Everything is Working

1. **FastAPI Health**: http://localhost:8000/health
   - Should return: `{"status":"healthy","model_loaded":true}`

2. **Metrics Endpoint**: http://localhost:8000/metrics
   - Should show Prometheus metrics including:
     - `http_requests_total`
     - `inference_latency_seconds_bucket`
     - `data_drift_requests_total`
     - `prediction_requests_total`

3. **Prometheus Targets**: http://localhost:9090/targets
   - `fastapi-service` should be **UP**

4. **Grafana Dashboard**: http://localhost:3000
   - Dashboard should load and show metrics

---

## 📝 Useful Commands

### View Logs
```powershell
# FastAPI logs
docker logs exchange-rate-api -f

# Prometheus logs
docker logs prometheus -f

# Grafana logs
docker logs grafana -f

# All services
docker-compose -f docker-compose.monitoring.yml logs -f
```

### Restart Services
```powershell
# Restart all
docker-compose -f docker-compose.monitoring.yml restart

# Restart specific service
docker-compose -f docker-compose.monitoring.yml restart model-api
```

### Stop Services
```powershell
docker-compose -f docker-compose.monitoring.yml down
```

### Start Services
```powershell
docker-compose -f docker-compose.monitoring.yml up -d
```

---

## 🎯 Key Metrics Explained

### Service Metrics
- **`http_requests_total`**: Total HTTP requests by endpoint/status
- **`inference_latency_seconds`**: Prediction request latency (histogram)

### Data Drift Metrics
- **`data_drift_requests_total`**: Count of requests with OOD features
- **`data_drift_ratio`**: Ratio of drift requests (calculated in Grafana)
- **`prediction_requests_total`**: Total prediction requests

---

## 🐛 Troubleshooting

### Services Not Starting
```powershell
# Check Docker is running
docker info

# Check logs
docker-compose -f docker-compose.monitoring.yml logs
```

### Metrics Not Appearing
1. Check Prometheus targets: http://localhost:9090/targets
2. Verify FastAPI is running: http://localhost:8000/health
3. Check network connectivity between containers

### Dashboard Not Loading
1. Check Grafana logs: `docker logs grafana`
2. Manually import dashboard via Grafana UI (Import → Upload JSON)

---

## ✅ Phase IV Complete!

Your monitoring stack is fully operational:
- ✅ Prometheus collecting metrics
- ✅ Grafana visualizing data
- ✅ FastAPI exposing metrics
- ✅ Data drift detection active
- ✅ All services healthy

**Next Steps**: Access the web interfaces and configure alerts as needed!

---

**For detailed documentation, see**: `MONITORING_SETUP.md`

