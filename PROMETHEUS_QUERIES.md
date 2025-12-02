# Prometheus Queries Guide

## 🔍 What to Search in Prometheus

Access Prometheus at: **http://localhost:9090**

Go to the **"Graph"** tab to run queries.

---

## 📊 Essential Queries to Try

### 1. **Request Rate (Requests per Second)**
```
rate(http_requests_total[5m])
```
Shows the rate of HTTP requests per second over the last 5 minutes.

### 2. **Request Rate by Endpoint**
```
sum(rate(http_requests_total[5m])) by (endpoint)
```
Shows request rate broken down by endpoint (/, /health, /predict).

### 3. **Total Request Count**
```
sum(http_requests_total)
```
Shows total number of HTTP requests since service started.

### 4. **Inference Latency - p95 (95th Percentile)**
```
histogram_quantile(0.95, rate(inference_latency_seconds_bucket[5m])) * 1000
```
Shows 95th percentile latency in milliseconds. This is what you should alert on if > 500ms.

### 5. **Inference Latency - p50 (Median)**
```
histogram_quantile(0.50, rate(inference_latency_seconds_bucket[5m])) * 1000
```
Shows median latency in milliseconds.

### 6. **Inference Latency - p99 (99th Percentile)**
```
histogram_quantile(0.99, rate(inference_latency_seconds_bucket[5m])) * 1000
```
Shows 99th percentile latency in milliseconds.

### 7. **Data Drift Ratio**
```
rate(data_drift_requests_total[5m]) / rate(prediction_requests_total[5m])
```
Shows the ratio of requests with out-of-distribution features. Alert if > 0.3 (30%).

### 8. **Data Drift Requests Rate**
```
rate(data_drift_requests_total[5m])
```
Shows the rate of data drift detections per second.

### 9. **Total Prediction Requests**
```
sum(prediction_requests_total)
```
Shows total number of prediction requests.

### 10. **Error Rate**
```
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```
Shows the ratio of 5xx errors to total requests.

### 11. **Request Count by Status Code**
```
sum(rate(http_requests_total[5m])) by (status)
```
Shows request rate broken down by HTTP status code (200, 400, 500, etc.).

### 12. **Latency Distribution (Histogram)**
```
rate(inference_latency_seconds_bucket[5m])
```
Shows the distribution of latencies across different buckets.

---

## 🎯 Most Important Queries for Monitoring

### **For Performance Monitoring:**
```
# p95 Latency (Alert threshold: > 500ms)
histogram_quantile(0.95, rate(inference_latency_seconds_bucket[5m])) * 1000
```

### **For Data Drift Monitoring:**
```
# Drift Ratio (Alert threshold: > 0.3 or 30%)
rate(data_drift_requests_total[5m]) / rate(prediction_requests_total[5m])
```

### **For Service Health:**
```
# Request Rate
sum(rate(http_requests_total[5m]))
```

---

## 📝 How to Use Prometheus

1. **Open Prometheus**: http://localhost:9090
2. **Click "Graph"** tab
3. **Type a query** in the search box
4. **Click "Execute"** or press Enter
5. **View results**:
   - **Graph** tab: See time series visualization
   - **Console** tab: See current values
6. **Change time range**: Use the time selector (top right)

---

## 🔍 Check if Metrics are Being Collected

1. Go to **Status → Targets**
2. Verify `fastapi-service` shows **UP** (green)
3. If DOWN, check:
   - FastAPI is running: http://localhost:8000/health
   - Metrics endpoint: http://localhost:8000/metrics

---

## 💡 Tips

- Use `[5m]` for 5-minute windows (good for rate calculations)
- Use `* 1000` to convert seconds to milliseconds for latency
- Use `rate()` for counters to get per-second rates
- Use `histogram_quantile()` for percentile calculations

