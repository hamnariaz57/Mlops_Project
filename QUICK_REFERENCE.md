# 🎯 MLOps Phase 1 - Quick Reference Card

## 📊 Project at a Glance

**Problem**: Exchange Rate Prediction (Time-Series)  
**Data Source**: https://api.exchangerate-api.com/v4/latest/USD  
**Base Currency**: USD → ~160 target currencies  
**Schedule**: Daily at 00:00 UTC (configurable)  

---

## 🏗️ Pipeline Flow (5 Tasks)

```
┌─────────────────┐
│  1. EXTRACT     │ ← Fetch from API + timestamp
│     DATA        │   data/raw/exchange_rates_raw_*.csv
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. QUALITY     │ ← Check nulls, schema, min currencies
│     CHECK ⚠️    │   FAILS if thresholds breached
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. TRANSFORM   │ ← Lag, rolling, time features
│   & ENGINEER    │   data/processed/exchange_rates.csv
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. PROFILING   │ ← Generate HTML report
│     REPORT      │   reports/data_profile_*.html
│                 │   → Log to MLflow
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. DVC         │ ← Version data
│   VERSIONING    │   dvc add → push → git commit
└─────────────────┘
```

---

## 🚀 Essential Commands

### Start Everything
```powershell
docker-compose build
docker-compose up -d
```

### Access UIs
- **Airflow**: http://localhost:8080 (admin/admin)
- **MLflow**: http://localhost:5000

### Trigger DAG
```powershell
docker-compose exec airflow-scheduler airflow dags trigger exchange_rate_mlops_pipeline_phase1
```

### View Logs
```powershell
docker-compose logs -f airflow-scheduler
```

### Stop Everything
```powershell
docker-compose down
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `dags/exchange_rate_dag.py` | Complete ETL pipeline (400+ lines) |
| `requirements.txt` | All Python dependencies |
| `docker-compose.yaml` | 5 services: Airflow, PostgreSQL, MLflow |
| `Dockerfile` | Custom Airflow image with git + packages |
| `.env` | DagHub credentials (create from .env.example) |
| `.dvc/config` | DVC remote storage configuration |

---

## 🎯 Quality Gates

| Check | Threshold | Action if Fails |
|-------|-----------|-----------------|
| Null values | < 1% | ❌ Stop DAG |
| Min currencies | ≥ 10 | ❌ Stop DAG |
| Schema validation | Required columns | ❌ Stop DAG |
| Data types | Numeric for rates | ❌ Stop DAG |

---

## 🔢 Features Created

### Time-Based
- `day_of_week`, `day_of_month`, `month`, `quarter`, `year`, `hour`

### For Major Currencies (EUR, GBP, JPY, CAD, AUD)
- **Lag**: `EUR_lag1`, `EUR_lag7`
- **Rolling Mean**: `EUR_rolling_mean_7`, `EUR_rolling_mean_30`
- **Volatility**: `EUR_rolling_std_7`, `EUR_rolling_std_30`
- **Rate of Change**: `EUR_pct_change_1d`, `EUR_pct_change_7d`

**Total Features**: ~200+ after feature engineering

---

## 📊 Expected Outputs

After successful run:

```
data/
├── raw/
│   └── exchange_rates_raw_20251130_143025.csv
└── processed/
    ├── exchange_rates.csv          ← Actual data (DVC tracked)
    └── exchange_rates.csv.dvc      ← Metadata (in Git)

reports/
└── data_profile_20251130_143025.html

MLflow: Run logged with metrics + profiling report artifact
DVC: Data pushed to DagHub S3
Git: .dvc file committed
```

---

## 🐛 Top 3 Issues & Fixes

### 1. Import Errors
```powershell
docker-compose build  # Uses Dockerfile with packages
docker-compose up -d
```

### 2. DVC Authentication
```powershell
dvc remote modify storage --local auth basic
dvc remote modify storage --local user hamnariaz57
dvc remote modify storage --local password YOUR_TOKEN
```

### 3. DAG Not Showing
```powershell
docker-compose logs -f airflow-scheduler
# Check for syntax errors in DAG file
```

---

## ✅ Phase 1 Checklist

- [x] Live API data extraction with timestamps
- [x] Mandatory quality gate (fails DAG on breach)
- [x] Feature engineering (lag, rolling, time-based)
- [x] Pandas Profiling report generation
- [x] MLflow artifact logging (DagHub)
- [x] DVC data versioning
- [x] DagHub S3 remote storage
- [x] Apache Airflow orchestration
- [x] Docker Compose multi-service setup
- [x] Complete documentation

---

## 📈 Metrics Tracked

**MLflow Parameters**:
- timestamp, num_rows, num_features, base_currency

**MLflow Metrics**:
- null_percentage, num_currencies

**MLflow Artifacts**:
- Pandas Profiling HTML report

---

## 🔄 Daily Workflow

```
00:00 UTC  →  Airflow triggers DAG automatically
  ↓
Fetch latest exchange rates from API
  ↓
Validate data quality (fail-fast if issues)
  ↓
Engineer time-series features
  ↓
Generate profiling report → Log to MLflow
  ↓
Version with DVC → Push to DagHub S3
  ↓
Commit .dvc metadata to Git
  ↓
Done! 🎉
```

---

## 🎓 Skills Demonstrated

1. **Airflow** - Building production ETL DAGs
2. **Docker** - Multi-container orchestration
3. **DVC** - Data versioning & remote storage
4. **MLflow** - Experiment tracking & artifacts
5. **Data Quality** - Mandatory validation gates
6. **Feature Engineering** - Time-series specific
7. **MLOps Best Practices** - Automation, monitoring, versioning

---

## 📞 Quick Help

**Problem**: Services won't start  
**Fix**: `docker-compose down -v; docker-compose build; docker-compose up -d`

**Problem**: DAG import errors  
**Fix**: Check `docker-compose logs airflow-scheduler` for details

**Problem**: DVC push fails  
**Fix**: Configure credentials with `dvc remote modify`

**Problem**: Quality check always fails  
**Fix**: Adjust thresholds in DAG file or check API response

---

## 🎯 Success Criteria

✅ All 5 tasks turn green in Airflow UI  
✅ Files created in data/raw, data/processed, reports  
✅ MLflow shows run with artifacts  
✅ DVC status shows "up to date"  
✅ Runs automatically every day  

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `PHASE1_COMPLETE.md` | Full project overview |
| `SETUP_GUIDE.md` | Step-by-step setup |
| `PHASE1_SUMMARY.md` | Implementation details |
| `TROUBLESHOOTING.md` | Common issues & solutions |
| `QUICK_REFERENCE.md` | This file |

---

**Status**: ✅ Phase 1 COMPLETE  
**Date**: November 30, 2025  
**Deadline**: ✅ On time!  

---

