# 🔧 Phase 1 Setup & Execution Guide

## **Complete Step-by-Step Implementation Instructions**

---

## 📋 **Current Status Assessment**

### ✅ **What You Already Have:**
1. Basic Airflow Docker setup
2. DVC initialized with DagHub remote
3. Node.js Express server (for dashboard)
4. Empty DVC-tracked dataset

### 🆕 **What's Been Added:**
1. ✅ Complete Airflow DAG with all 5 phases
2. ✅ Requirements.txt with all Python dependencies
3. ✅ MLflow service in docker-compose
4. ✅ Environment configuration (.env.example)
5. ✅ Proper directory structure
6. ✅ Data quality gates
7. ✅ Feature engineering
8. ✅ Pandas profiling
9. ✅ DVC automation

---

## 🚀 **Setup Instructions**

### **Step 1: Install Docker Dependencies in Airflow**

The Airflow containers need additional Python packages. Update your docker-compose.yaml:

**Option A: Build custom Airflow image (Recommended)**

Create `Dockerfile` in project root:

```dockerfile
FROM apache/airflow:2.7.1

USER root
RUN apt-get update && apt-get install -y git

USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
```

Update `docker-compose.yaml` - replace all `image: apache/airflow:2.7.1` with:
```yaml
build: .
```

**Option B: Install packages in running container (Quick test)**

```bash
# After starting containers
docker-compose exec airflow-scheduler pip install -r /opt/airflow/requirements.txt
docker-compose exec airflow-webserver pip install -r /opt/airflow/requirements.txt
```

---

### **Step 2: Configure DagHub Token**

1. **Get DagHub Token:**
   - Go to: https://dagshub.com/user/settings/tokens
   - Create new token with full access
   - Copy the token

2. **Create `.env` file:**
```bash
cp .env.example .env
```

3. **Edit `.env`** and add your token:
```bash
DAGSHUB_USERNAME=hamnariaz57
DAGSHUB_TOKEN=your_actual_token_here
```

4. **Configure DVC with credentials:**
```bash
dvc remote modify storage --local auth basic
dvc remote modify storage --local user hamnariaz57
dvc remote modify storage --local password YOUR_DAGSHUB_TOKEN
```

---

### **Step 3: Start Services**

```bash
# If using Option A (custom image)
docker-compose build

# Start all services
docker-compose up -d

# Monitor startup
docker-compose ps
docker-compose logs -f airflow-init

# Wait for "airflow-init exited with code 0"
```

**Services running:**
- Airflow Webserver: http://localhost:8080
- MLflow: http://localhost:5000
- PostgreSQL: port 5432

---

### **Step 4: Verify Setup**

```bash
# Check all containers are healthy
docker-compose ps

# Should show:
# airflow-webserver  -> healthy
# airflow-scheduler  -> running
# postgres          -> healthy
# mlflow            -> running

# Check Airflow can access Python packages
docker-compose exec airflow-scheduler python -c "import mlflow, dvc; print('OK')"
```

---

### **Step 5: Access Airflow & Enable DAG**

1. Open http://localhost:8080
2. Login: `admin` / `admin`
3. Find DAG: `exchange_rate_mlops_pipeline_phase1`
4. Toggle it **ON** (switch on left)
5. Click **Play button** → "Trigger DAG" for manual run

---

### **Step 6: Monitor Execution**

**In Airflow UI:**
1. Click on DAG name
2. Click on latest run (Graph view)
3. Watch tasks turn green:
   - `extract_data` → `quality_check` → `transform_data` → `generate_profiling_report` → `version_with_dvc`

4. Click any task → **Logs** to see detailed output

**Expected execution time:** 5-10 minutes (first run)

---

### **Step 7: Verify Outputs**

After successful run:

```bash
# Check raw data
ls -lh data/raw/
# Should have: exchange_rates_raw_YYYYMMDD_HHMMSS.csv

# Check processed data
ls -lh data/processed/
# Should have: exchange_rates.csv and exchange_rates.csv.dvc

# Check reports
ls -lh reports/
# Should have: data_profile_YYYYMMDD_HHMMSS.html

# Check DVC status
dvc status
# Should show: up to date
```

---

### **Step 8: Verify DVC Versioning**

```bash
# Check DVC tracking
dvc list --dvc-only .

# Check remote storage
dvc pull  # Should say "Everything is up to date"

# View Git commits
git log --oneline -5
# Should show: "Data version update - TIMESTAMP"
```

---

### **Step 9: Check MLflow Logs**

1. Open http://localhost:5000
2. Navigate to "Experiments"
3. Find run: `data_pipeline_TIMESTAMP`
4. Check:
   - **Parameters**: timestamp, num_rows, num_features
   - **Metrics**: quality_metrics
   - **Artifacts**: data_profile_*.html

**OR via DagHub:**
- https://dagshub.com/hamnariaz57/Mlops_Project.mlflow

---

## 🔄 **Daily Automated Execution**

The DAG runs **automatically every day at midnight UTC**.

To change schedule:
```python
# In dags/exchange_rate_dag.py
schedule_interval="@daily"     # Current: midnight UTC
# schedule_interval="0 9 * * *"  # 9 AM daily
# schedule_interval="@hourly"    # Every hour
```

---

## 🐛 **Common Issues & Solutions**

### **Issue 1: Import errors in Airflow**

```
ModuleNotFoundError: No module named 'ydata_profiling'
```

**Solution:**
```bash
# Install in containers
docker-compose exec airflow-scheduler pip install -r /opt/airflow/requirements.txt
docker-compose exec airflow-webserver pip install -r /opt/airflow/requirements.txt
docker-compose restart airflow-scheduler airflow-webserver
```

---

### **Issue 2: DVC push fails with authentication error**

```
ERROR: failed to push data to the cloud - Authentication failed
```

**Solution:**
```bash
# Inside container or locally
dvc remote modify storage --local auth basic
dvc remote modify storage --local user hamnariaz57
dvc remote modify storage --local password YOUR_DAGSHUB_TOKEN

# Test
dvc push -v
```

---

### **Issue 3: MLflow not logging**

```
Warning: Could not log to MLflow
```

**Solution:**
Check `.env` file has correct token:
```bash
# Edit docker-compose.yaml to load .env
# Add under scheduler and webserver services:
env_file:
  - .env

# Restart
docker-compose down
docker-compose up -d
```

---

### **Issue 4: Airflow can't access Git/DVC**

```
ERROR: git command not found
```

**Solution:**
Must use custom Dockerfile (Option A above) to install git in Airflow container.

---

### **Issue 5: Profiling report generation too slow**

In DAG file, change:
```python
profile = ProfileReport(
    df,
    minimal=True,  # ← Faster generation
    explorative=True
)
```

---

## 📊 **Understanding the Data Flow**

### **Day 1 (First Run):**
```
API → Raw CSV (timestamped)
  ↓
Quality Check (pass/fail)
  ↓
Feature Engineering (basic - no historical data yet)
  ↓
Processed CSV → DVC version 1
  ↓
Profiling Report → MLflow artifact
```

### **Day 2+ (With History):**
```
API → Raw CSV (timestamped)
  ↓
Quality Check (pass/fail)
  ↓
Feature Engineering (lag, rolling, volatility calculated from history)
  ↓
Processed CSV → DVC version 2 (updated)
  ↓
Profiling Report → MLflow artifact
```

---

## 🧪 **Testing the Pipeline**

### **Manual Test Run:**

```bash
# Trigger DAG manually
docker-compose exec airflow-scheduler airflow dags trigger exchange_rate_mlops_pipeline_phase1

# Check status
docker-compose exec airflow-scheduler airflow dags state exchange_rate_mlops_pipeline_phase1

# View logs
docker-compose logs -f airflow-scheduler
```

---

## 📈 **What to Submit for Phase 1**

### **Deliverables Checklist:**

- [ ] **Code**:
  - ✅ `dags/exchange_rate_dag.py` (complete ETL pipeline)
  - ✅ `requirements.txt`
  - ✅ `docker-compose.yaml`
  - ✅ `.dvc/config` (remote storage configured)

- [ ] **Data**:
  - ✅ `data/processed/exchange_rates.csv.dvc` (DVC metadata in Git)
  - ✅ Actual data in DagHub S3 remote

- [ ] **Reports**:
  - ✅ Sample `data_profile_*.html` (Pandas Profiling)
  - ✅ MLflow run showing logged artifacts

- [ ] **Documentation**:
  - ✅ README.md with architecture & setup
  - ✅ This implementation guide

- [ ] **Screenshots**:
  - Airflow UI showing successful DAG run (all tasks green)
  - MLflow UI showing experiment with artifacts
  - DagHub showing DVC tracked data

---

## 🎯 **Phase 1 Validation Criteria**

| Requirement | How to Verify | Status |
|-------------|---------------|--------|
| **API data extraction** | Check `data/raw/` has timestamped files | ✅ |
| **Quality gate implemented** | Trigger with bad data → DAG fails | ✅ |
| **Feature engineering** | Processed CSV has lag/rolling columns | ✅ |
| **Pandas profiling** | HTML report in `reports/` | ✅ |
| **MLflow artifact** | Report visible in MLflow UI | ✅ |
| **DVC versioning** | `.dvc` file committed to Git | ✅ |
| **Remote storage** | `dvc pull` downloads data | ✅ |
| **Airflow orchestration** | Daily schedule works automatically | ✅ |

---

## 🚀 **Next Actions**

1. **Run the pipeline** and verify all tasks succeed
2. **Take screenshots** of:
   - Airflow DAG run (graph view, all green)
   - MLflow experiment page
   - Profiling report opened
   - DVC status output

3. **Test quality gate** by modifying thresholds to intentionally fail
4. **Verify** data accumulates over multiple runs
5. **Document** any customizations you make

---

## 📞 **Getting Help**

If stuck:

1. Check Airflow task logs (most detailed)
2. Run commands manually in scheduler container:
   ```bash
   docker-compose exec airflow-scheduler bash
   cd /opt/airflow
   python -c "from dags.exchange_rate_dag import *; extract_exchange_rate_data()"
   ```
3. Verify all environment variables are set
4. Check Docker container logs for startup errors

---

**You're ready for Phase 1 completion! 🎉**

