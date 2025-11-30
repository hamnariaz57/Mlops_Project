# MLOps Phase 1 - Troubleshooting Guide

## 🔍 Common Issues and Solutions

### 1. Docker Build Fails

**Error**: `failed to solve: failed to fetch ...`

**Solutions**:
```powershell
# Clear Docker cache and rebuild
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
```

---

### 2. Airflow Webserver Won't Start

**Error**: `airflow-webserver exited with code 1`

**Check logs**:
```powershell
docker-compose logs airflow-webserver
```

**Solutions**:
```powershell
# Reset everything
docker-compose down -v
docker volume rm mlops_project_postgres-db
docker-compose up -d
```

---

### 3. Import Errors in DAG

**Error**: `ModuleNotFoundError: No module named 'ydata_profiling'`

**Cause**: Packages not installed in Airflow container

**Solution A** (Recommended - using Dockerfile):
```powershell
# Already done - just rebuild
docker-compose build
docker-compose up -d
```

**Solution B** (Quick fix):
```powershell
# Install in running containers
docker-compose exec airflow-scheduler pip install -r /opt/airflow/requirements.txt
docker-compose exec airflow-webserver pip install -r /opt/airflow/requirements.txt
docker-compose restart airflow-scheduler airflow-webserver
```

---

### 4. DVC Push Authentication Fails

**Error**: `ERROR: failed to push data to the cloud - Authentication failed`

**Solution**:
```powershell
# Configure DVC with DagHub credentials
dvc remote modify storage --local auth basic
dvc remote modify storage --local user hamnariaz57
dvc remote modify storage --local password YOUR_DAGSHUB_TOKEN_HERE

# Test connection
dvc push -v
```

**Inside Docker container**:
```powershell
docker-compose exec airflow-scheduler bash
cd /opt/airflow
dvc remote modify storage --local auth basic
dvc remote modify storage --local user hamnariaz57
dvc remote modify storage --local password YOUR_TOKEN
exit
```

---

### 5. MLflow Not Logging

**Error**: `Warning: Could not log to MLflow`

**Check**:
1. MLflow service is running:
```powershell
docker-compose ps mlflow
```

2. Environment variables are set:
```powershell
# Edit .env file
DAGSHUB_USERNAME=hamnariaz57
DAGSHUB_TOKEN=your_actual_token_here
```

3. Restart services:
```powershell
docker-compose down
docker-compose up -d
```

---

### 6. DAG Not Appearing in Airflow UI

**Cause**: Syntax error in DAG file

**Check**:
```powershell
# View scheduler logs
docker-compose logs -f airflow-scheduler

# Test DAG import
docker-compose exec airflow-scheduler bash
python -c "from dags.exchange_rate_dag import *"
```

---

### 7. Quality Check Keeps Failing

**Error**: `QUALITY CHECK FAILED: Null values exceed threshold`

**Debug**:
```powershell
# Check raw data
docker-compose exec airflow-scheduler bash
cd /opt/airflow/data/raw
ls -lh
cat exchange_rates_raw_*.csv | head -20
```

**Adjust thresholds** (if needed) in `dags/exchange_rate_dag.py`:
```python
NULL_THRESHOLD = 0.05  # Increase to 5%
MIN_REQUIRED_CURRENCIES = 5  # Reduce minimum
```

---

### 8. Data Directory Not Accessible

**Error**: `FileNotFoundError: [Errno 2] No such file or directory`

**Solution**:
Ensure volumes are mounted correctly in `docker-compose.yaml`:
```yaml
volumes:
  - ./data:/opt/airflow/data
  - ./reports:/opt/airflow/reports
```

**Create directories**:
```powershell
mkdir -p data/raw, data/processed, reports
```

---

### 9. Git Not Found in Airflow Container

**Error**: `git: command not found`

**Cause**: Using base Airflow image instead of custom Dockerfile

**Solution**:
Ensure `docker-compose.yaml` uses `build: .` instead of `image: apache/airflow:2.7.1`:
```yaml
airflow-scheduler:
  build: .  # ← Should be this, not 'image:'
```

Then rebuild:
```powershell
docker-compose build
docker-compose up -d
```

---

### 10. Pandas Profiling Takes Too Long

**Issue**: Report generation timeout

**Solution**:
In `dags/exchange_rate_dag.py`, use minimal mode:
```python
profile = ProfileReport(
    df,
    minimal=True,  # ← Faster generation
    explorative=False  # ← Less detailed
)
```

---

## 🛠️ Useful Debug Commands

### Check All Services
```powershell
docker-compose ps
```

### View Logs
```powershell
# All services
docker-compose logs

# Specific service
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver
docker-compose logs -f postgres
docker-compose logs -f mlflow
```

### Access Container Shell
```powershell
# Scheduler
docker-compose exec airflow-scheduler bash

# Webserver
docker-compose exec airflow-webserver bash
```

### Test DAG Manually
```powershell
docker-compose exec airflow-scheduler bash
cd /opt/airflow
python -c "
from dags.exchange_rate_dag import *
from datetime import datetime
context = {'task_instance': type('obj', (object,), {'xcom_push': lambda *args: None, 'xcom_pull': lambda *args: None})}
extract_exchange_rate_data(**context)
"
```

### Check Airflow Configuration
```powershell
docker-compose exec airflow-scheduler airflow config list
```

### List DAGs
```powershell
docker-compose exec airflow-scheduler airflow dags list
```

### Trigger DAG
```powershell
docker-compose exec airflow-scheduler airflow dags trigger exchange_rate_mlops_pipeline_phase1
```

### Check Task Instances
```powershell
docker-compose exec airflow-scheduler airflow tasks list exchange_rate_mlops_pipeline_phase1
```

---

## 🔄 Complete Reset (Nuclear Option)

If everything is broken:

```powershell
# Stop and remove everything
docker-compose down -v

# Remove all Docker volumes
docker volume prune -f

# Remove all unused images
docker system prune -a -f

# Rebuild from scratch
docker-compose build --no-cache

# Start fresh
docker-compose up -d

# Wait for initialization
Start-Sleep -Seconds 120

# Check status
docker-compose ps
```

---

## 📊 Verifying Everything Works

### 1. Check Services Running
```powershell
docker-compose ps
# All should show "healthy" or "running"
```

### 2. Check Airflow UI
- Go to http://localhost:8080
- Login: admin / admin
- DAG should appear: `exchange_rate_mlops_pipeline_phase1`

### 3. Check MLflow UI
- Go to http://localhost:5000
- Should show experiments page

### 4. Run Test DAG
```powershell
docker-compose exec airflow-scheduler airflow dags trigger exchange_rate_mlops_pipeline_phase1
```

### 5. Monitor Execution
```powershell
docker-compose logs -f airflow-scheduler
```

### 6. Verify Outputs
```powershell
# Check files created
ls data/raw/
ls data/processed/
ls reports/
```

---

## 📞 Still Stuck?

1. **Check Airflow logs** first - most errors show here
2. **Verify .env file** has correct DagHub token
3. **Ensure Docker has enough resources** (4GB+ RAM)
4. **Check file permissions** on mounted volumes
5. **Try the complete reset** steps above

---

## 🎯 Expected Behavior

### First Run:
- Takes 5-10 minutes
- All tasks should turn green
- Files created in data/raw, data/processed, reports
- MLflow run logged

### Subsequent Runs:
- Faster (3-5 minutes)
- More features calculated (with history)
- DVC versions increment

---

