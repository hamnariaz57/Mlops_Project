# Monitoring and Observability Setup Guide

This guide explains how to set up and use Prometheus and Grafana for monitoring your MLOps Exchange Rate Prediction API.

## Overview

The monitoring stack consists of:
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and alerting
- **FastAPI Service**: Exposes metrics via `/metrics` endpoint

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- Trained model and training statistics available in `models/` directory
- Docker image built: `your-username/exchange-rate-model:latest`

### 2. Start Monitoring Stack

```bash
# Start all services (Prometheus, Grafana, and API)
docker-compose -f docker-compose.monitoring.yml up -d

# Check service status
docker-compose -f docker-compose.monitoring.yml ps

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f
```

### 3. Access Services

- **FastAPI Service**: http://localhost:8000
  - Health: http://localhost:8000/health
  - Metrics: http://localhost:8000/metrics
  - API Docs: http://localhost:8000/docs

- **Prometheus**: http://localhost:9090
  - Query metrics, view targets, check configuration

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin` (change in production!)
  - Dashboard: Automatically loaded at startup

## Metrics Collected

### Service Metrics

1. **HTTP Request Count** (`http_requests_total`)
   - Total number of HTTP requests by method, endpoint, and status code
   - Labels: `method`, `endpoint`, `status`

2. **Inference Latency** (`inference_latency_seconds`)
   - Histogram of prediction request latency
   - Buckets: 1ms, 5ms, 10ms, 50ms, 100ms, 500ms, 1s, 5s

### Model/Data Drift Metrics

3. **Data Drift Requests** (`data_drift_requests_total`)
   - Counter of requests with out-of-distribution feature values
   - Incremented when features are outside training distribution

4. **Data Drift Ratio** (`data_drift_ratio`)
   - Gauge showing current ratio of drift requests to total requests
   - Calculated as: `drift_requests / total_requests`

5. **Total Prediction Requests** (`prediction_requests_total`)
   - Counter of all prediction requests

## Data Drift Detection

The system detects data drift by comparing incoming feature values against training data statistics:

- **Training Statistics**: Stored in `models/training_stats.json`
- **Detection Method**: 
  - Checks if values are outside training min/max range
  - Checks if values are > 3 standard deviations from training mean
- **Statistics Required**: min, max, mean, std for each feature (lag_1, lag_2, lag_3)

### Generating Training Statistics

Training statistics are automatically generated when you run `train_model.py`:

```bash
python train_model.py
```

This creates `models/training_stats.json` with feature statistics.

## Grafana Dashboard

The dashboard includes:

1. **Key Metrics Panels**:
   - Total HTTP Requests (rate)
   - Inference Latency (p95)
   - Data Drift Ratio
   - Total Prediction Requests

2. **Time Series Panels**:
   - Inference Latency Over Time (p50, p95, p99)
   - HTTP Request Rate by Endpoint
   - Data Drift Detection Over Time

3. **Distribution Panels**:
   - HTTP Status Codes Distribution (pie chart)
   - Latency Distribution (histogram)

### Accessing the Dashboard

1. Open Grafana: http://localhost:3000
2. Login with admin/admin
3. Navigate to **Dashboards** → **MLOps Exchange Rate API - Monitoring Dashboard**

## Alerting Configuration

### Setting Up Alerts in Grafana UI

1. **Navigate to Alerting**:
   - Go to **Alerting** → **Alert rules** in Grafana

2. **Create Alert for High Latency**:
   - Click **New alert rule**
   - **Name**: "High Inference Latency"
   - **Query**: 
     ```promql
     histogram_quantile(0.95, rate(inference_latency_seconds_bucket[5m])) * 1000
     ```
   - **Condition**: `WHEN last() OF A IS ABOVE 500`
   - **For**: `5m`
   - **Annotations**:
     - Summary: "Inference latency exceeds 500ms"
     - Description: "p95 latency is {{ $values.A }}ms"

3. **Create Alert for Data Drift**:
   - Click **New alert rule**
   - **Name**: "Data Drift Spike"
   - **Query**:
     ```promql
     rate(data_drift_requests_total[5m]) / rate(prediction_requests_total[5m])
     ```
   - **Condition**: `WHEN last() OF A IS ABOVE 0.3`
   - **For**: `5m`
   - **Annotations**:
     - Summary: "Data drift ratio spike detected"
     - Description: "Drift ratio is {{ $values.A }}"

### Alert Notification Channels

To send alerts to Slack or other channels:

1. **Configure Notification Channel**:
   - Go to **Alerting** → **Notification channels**
   - Click **New channel**
   - Choose channel type (Slack, Email, etc.)
   - Configure credentials

2. **Add to Alert Rule**:
   - When creating/editing alert rule
   - Add notification channel in **Notifications** section

### Example: Slack Integration

1. Create Slack webhook URL
2. In Grafana: **Alerting** → **Notification channels** → **New channel**
3. Type: **Slack**
4. Webhook URL: `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`
5. Save and add to alert rules

## Prometheus Queries

Useful PromQL queries for monitoring:

### Request Rate
```promql
sum(rate(http_requests_total[5m])) by (endpoint)
```

### Latency Percentiles
```promql
# p50
histogram_quantile(0.50, rate(inference_latency_seconds_bucket[5m])) * 1000

# p95
histogram_quantile(0.95, rate(inference_latency_seconds_bucket[5m])) * 1000

# p99
histogram_quantile(0.99, rate(inference_latency_seconds_bucket[5m])) * 1000
```

### Data Drift Ratio
```promql
rate(data_drift_requests_total[5m]) / rate(prediction_requests_total[5m])
```

### Error Rate
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

## Testing the Setup

### 1. Test API Endpoint

```bash
# Health check
curl http://localhost:8000/health

# Make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"history": [0.85, 0.86, 0.87]}'
```

### 2. Check Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

You should see Prometheus metrics including:
- `http_requests_total`
- `inference_latency_seconds_bucket`
- `data_drift_requests_total`
- `prediction_requests_total`

### 3. Verify Prometheus Scraping

1. Open Prometheus: http://localhost:9090
2. Go to **Status** → **Targets**
3. Check that `fastapi-service` target is **UP**

### 4. Verify Grafana Dashboard

1. Open Grafana: http://localhost:3000
2. Check dashboard shows metrics
3. Make some API requests and watch metrics update

## Troubleshooting

### Metrics Not Appearing

1. **Check API is running**:
   ```bash
   docker logs exchange-rate-api
   ```

2. **Check Prometheus targets**:
   - http://localhost:9090/targets
   - Ensure `fastapi-service` is UP

3. **Check network connectivity**:
   ```bash
   docker exec prometheus wget -qO- http://model-api:8000/metrics
   ```

### Training Statistics Not Found

If you see warnings about missing training statistics:

1. **Generate statistics**:
   ```bash
   python train_model.py
   ```

2. **Copy to models directory**:
   ```bash
   cp training_stats.json models/
   ```

3. **Restart API**:
   ```bash
   docker-compose -f docker-compose.monitoring.yml restart model-api
   ```

### Grafana Dashboard Not Loading

1. **Check dashboard file exists**:
   ```bash
   ls -la grafana/dashboards/mlops-monitoring.json
   ```

2. **Check Grafana logs**:
   ```bash
   docker logs grafana
   ```

3. **Manually import dashboard**:
   - Go to Grafana → **Dashboards** → **Import**
   - Upload `grafana/dashboards/mlops-monitoring.json`

## Production Considerations

### Security

1. **Change Grafana default password**:
   - Update in `docker-compose.monitoring.yml`
   - Or set via environment variable

2. **Use secrets management**:
   - Store credentials in Docker secrets or environment files
   - Don't commit sensitive data

3. **Network security**:
   - Use internal networks for service communication
   - Expose only necessary ports

### Performance

1. **Retention policy**:
   - Adjust `storage.tsdb.retention.time` in Prometheus config
   - Default: 30 days

2. **Scrape intervals**:
   - Balance between real-time monitoring and resource usage
   - Current: 10s for API, 15s for Prometheus

3. **Resource limits**:
   - Add resource limits to Docker Compose services
   - Monitor resource usage

### High Availability

For production, consider:
- Prometheus federation for scaling
- Grafana high availability setup
- Alertmanager for alert routing
- Persistent volumes for data retention

## Files Structure

```
Mlops_Project/
├── service.py                          # FastAPI service with metrics
├── train_model.py                      # Generates training_stats.json
├── docker-compose.monitoring.yml       # Monitoring stack
├── prometheus/
│   └── prometheus.yml                  # Prometheus configuration
└── grafana/
    ├── provisioning/
    │   ├── datasources/
    │   │   └── prometheus.yml          # Prometheus datasource
    │   └── dashboards/
    │       └── dashboard.yml           # Dashboard provisioning
    ├── dashboards/
    │   └── mlops-monitoring.json       # Dashboard definition
    └── alerts/
        └── alert-rules.json            # Alert definitions (reference)
```

## Next Steps

1. **Customize alerts** for your specific thresholds
2. **Add more metrics** as needed (model accuracy, feature importance, etc.)
3. **Set up notification channels** (Slack, PagerDuty, etc.)
4. **Create additional dashboards** for different stakeholders
5. **Implement log aggregation** (e.g., ELK stack) for comprehensive observability

## Support

For issues or questions:
1. Check logs: `docker-compose -f docker-compose.monitoring.yml logs`
2. Verify configuration files
3. Test individual services independently
4. Review Prometheus and Grafana documentation

