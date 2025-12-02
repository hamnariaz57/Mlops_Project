# Grafana Alerts Setup Guide - Step by Step

## 🚨 How to Configure Grafana Alerts

Access Grafana at: **http://localhost:3000** (admin/admin)

---

## 📋 Step-by-Step: Create High Latency Alert

### Step 1: Navigate to Alerting
1. Open Grafana: http://localhost:3000
2. Login with: `admin` / `admin`
3. Click **"Alerting"** in the left menu (bell icon 🔔)
4. Click **"Alert rules"** in the submenu

### Step 2: Create New Alert Rule
1. Click **"New alert rule"** button (top right)

### Step 3: Configure Alert Details
1. **Name**: `High Inference Latency`
2. **Folder**: Leave default or create "MLOps Alerts"
3. **Evaluation group**: `mlops-evaluation` (or default)

### Step 4: Set Up Query
1. In the **"Query"** section:
   - **Data source**: Select `Prometheus`
   - **Query A**: Paste this:
     ```
     histogram_quantile(0.95, rate(inference_latency_seconds_bucket[5m])) * 1000
     ```
   - **Legend**: `p95 Latency (ms)`
   - **Format**: `Time series`

### Step 5: Set Condition
1. Scroll to **"Condition"** section
2. **When**: `last()`
3. **Of**: `A`
4. **Is above**: `500`
5. This means: Alert when p95 latency is above 500ms

### Step 6: Set Evaluation
1. **Evaluate every**: `1m` (check every minute)
2. **For**: `5m` (must be above threshold for 5 minutes before alerting)

### Step 7: Add Annotations
1. Scroll to **"Annotations"** section
2. **Summary**: `Inference latency exceeds 500ms threshold`
3. **Description**: 
   ```
   The p95 inference latency is {{ $values.A }}ms, which exceeds the 500ms threshold.
   This may indicate performance degradation.
   Service: Exchange Rate Prediction API
   ```

### Step 8: Add Labels
1. Scroll to **"Labels"** section
2. Click **"Add label"**
   - **Name**: `severity`
   - **Value**: `warning`
3. Click **"Add label"** again
   - **Name**: `team`
   - **Value**: `mlops`

### Step 9: Save Alert
1. Click **"Save"** button (top right)
2. Alert rule is now active!

---

## 📋 Step-by-Step: Create Data Drift Alert

### Step 1: Create Another Alert Rule
1. Go to **Alerting → Alert rules**
2. Click **"New alert rule"**

### Step 2: Configure Alert Details
1. **Name**: `Data Drift Spike`
2. **Folder**: Same as before

### Step 3: Set Up Query
1. **Data source**: `Prometheus`
2. **Query A**: Paste this:
   ```
   rate(data_drift_requests_total[5m]) / rate(prediction_requests_total[5m])
   ```
3. **Legend**: `Drift Ratio`
4. **Format**: `Time series`

### Step 4: Set Condition
1. **When**: `last()`
2. **Of**: `A`
3. **Is above**: `0.3` (30% drift ratio)
4. This means: Alert when more than 30% of requests have data drift

### Step 5: Set Evaluation
1. **Evaluate every**: `1m`
2. **For**: `5m` (must be above threshold for 5 minutes)

### Step 6: Add Annotations
1. **Summary**: `Data drift ratio spike detected`
2. **Description**:
   ```
   The data drift ratio is {{ $values.A }}, indicating a significant increase 
   in out-of-distribution feature values. Model performance may be degraded.
   Service: Exchange Rate Prediction API
   ```

### Step 7: Add Labels
1. **severity**: `critical`
2. **team**: `mlops`

### Step 8: Save Alert
1. Click **"Save"**

---

## 🔔 Step-by-Step: Configure Notification Channel (Optional)

### For Slack Integration:

1. **Get Slack Webhook URL**:
   - Go to https://api.slack.com/apps
   - Create a new app or use existing
   - Go to "Incoming Webhooks"
   - Activate and create webhook
   - Copy webhook URL

2. **In Grafana**:
   - Go to **Alerting → Notification channels**
   - Click **"New channel"**
   - **Name**: `Slack - MLOps Team`
   - **Type**: `Slack`
   - **Webhook URL**: Paste your Slack webhook URL
   - **Channel**: `#mlops-alerts` (or your channel)
   - Click **"Test"** to verify
   - Click **"Save"**

3. **Add to Alert Rules**:
   - Edit your alert rules
   - Scroll to **"Notifications"** section
   - Select your Slack channel
   - Save

### For Email Integration:

1. **In Grafana**:
   - Go to **Alerting → Notification channels**
   - Click **"New channel"**
   - **Name**: `Email - MLOps Team`
   - **Type**: `Email`
   - **Addresses**: `your-email@example.com`
   - Click **"Save"**

2. **Add to Alert Rules**:
   - Edit alert rules
   - Add email channel to notifications
   - Save

---

## 🧪 How to Test/Trigger Alerts

### Method 1: Generate High Latency (Test Latency Alert)

Make many slow requests to trigger latency:

```powershell
# Generate traffic to test latency alert
for ($i=1; $i -le 50; $i++) {
    $body = @{ history = @(0.85, 0.86, 0.87) } | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json"
    Start-Sleep -Milliseconds 100
}
```

### Method 2: Generate Data Drift (Test Drift Alert)

Send requests with extreme values to trigger drift:

```powershell
# Send extreme values that will trigger data drift
for ($i=1; $i -le 20; $i++) {
    $body = @{ history = @(10.0, 20.0, 30.0) } | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json"
    Start-Sleep -Seconds 1
}
```

### Method 3: Check Alert Status

1. **In Grafana**:
   - Go to **Alerting → Alert rules**
   - You'll see alert states:
     - **🟢 OK**: Normal
     - **🟡 Pending**: Condition met but waiting for "For" duration
     - **🔴 Firing**: Alert is active

2. **View Alert History**:
   - Click on an alert rule
   - See "State history" tab
   - View when alerts fired

---

## ✅ Verify Alerts Are Working

### Check Alert Rules:
1. Go to **Alerting → Alert rules**
2. You should see your alerts listed
3. Status should show current state

### Check Alert Instances:
1. Go to **Alerting → Alert instances**
2. See active/firing alerts
3. View alert details

### Test Alert:
1. Generate traffic using methods above
2. Wait 5+ minutes (alert "For" duration)
3. Check if alert fires
4. Verify notifications (if configured)

---

## 📊 View Alerts in Dashboard

You can also add alert indicators to your dashboard:

1. **Edit Dashboard**: Go to your monitoring dashboard
2. **Add Panel**: Click "Add panel"
3. **Query**: Use your alert query
4. **Visualization**: Choose "Stat" or "Gauge"
5. **Alert Thresholds**: Set color thresholds
   - Green: < 500ms
   - Yellow: 500-1000ms
   - Red: > 1000ms

---

## 🔧 Troubleshooting

### Alerts Not Firing:
1. **Check query works**: Test query in Prometheus first
2. **Check time range**: Make sure data exists for the time period
3. **Check condition**: Verify threshold is correct
4. **Check evaluation**: Ensure "For" duration allows time to evaluate

### Alerts Firing Too Often:
1. **Increase "For" duration**: Make it wait longer (e.g., 10m)
2. **Adjust threshold**: Make threshold higher
3. **Add hysteresis**: Use different thresholds for alerting vs resolving

### No Data in Queries:
1. **Check Prometheus targets**: http://localhost:9090/targets
2. **Check metrics endpoint**: http://localhost:8000/metrics
3. **Generate traffic**: Make some API calls to generate metrics

---

## 📝 Quick Reference

### Alert 1: High Latency
- **Query**: `histogram_quantile(0.95, rate(inference_latency_seconds_bucket[5m])) * 1000`
- **Condition**: `> 500` (ms)
- **For**: `5m`

### Alert 2: Data Drift
- **Query**: `rate(data_drift_requests_total[5m]) / rate(prediction_requests_total[5m])`
- **Condition**: `> 0.3` (30%)
- **For**: `5m`

---

## 🎯 Next Steps

1. ✅ Create both alert rules
2. ✅ Test alerts by generating traffic
3. ✅ Configure notification channels (optional)
4. ✅ Monitor alert history
5. ✅ Adjust thresholds as needed

Your alerts are now configured and ready to monitor your ML service! 🚀

