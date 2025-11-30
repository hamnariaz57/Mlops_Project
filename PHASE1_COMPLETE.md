# 🚀 MLOps Phase 1: Real-Time Predictive System (RPS)
## Exchange Rate Prediction Pipeline

[![MLOps](https://img.shields.io/badge/MLOps-Phase%201-blue)](https://github.com/hamnariaz57/Mlops_Project)
[![Airflow](https://img.shields.io/badge/Apache-Airflow-017CEE?logo=apache-airflow)](https://airflow.apache.org/)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2?logo=mlflow)](https://mlflow.org/)
[![DVC](https://img.shields.io/badge/DVC-Data%20Versioning-945DD6?logo=dvc)](https://dvc.org/)

---

## 📋 **Project Overview**

This project implements a **complete MLOps Phase 1 pipeline** for a Real-Time Exchange Rate Predictive System. It demonstrates production-grade practices including:

- ✅ **Automated Data Ingestion** from live APIs
- ✅ **Mandatory Data Quality Gates** (fail-fast approach)
- ✅ **Feature Engineering** for time-series data
- ✅ **Data Versioning** with DVC
- ✅ **Experiment Tracking** with MLflow (DagHub)
- ✅ **Orchestration** with Apache Airflow

---

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Apache Airflow DAG (Daily)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 1: EXTRACTION                                              │
│  ├─ Fetch data from Exchange Rate API                           │
│  ├─ Save raw data with timestamp                                │
│  └─ Store in: data/raw/exchange_rates_raw_YYYYMMDD_HHMMSS.csv  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 2: QUALITY CHECK (MANDATORY GATE) ⚠️                      │
│  ├─ Check null values < 1%                                       │
│  ├─ Validate schema                                              │
│  ├─ Verify minimum currency count                               │
│  └─ FAIL pipeline if checks fail                                │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 3: TRANSFORMATION & FEATURE ENGINEERING                    │
│  ├─ Time-based features (day, month, quarter, hour)             │
│  ├─ Lag features (1-day, 7-day)                                 │
│  ├─ Rolling means (7-day, 30-day)                               │
│  ├─ Volatility measures (rolling std)                           │
│  ├─ Percentage changes (1-day, 7-day)                           │
│  └─ Save to: data/processed/exchange_rates.csv                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 4: PANDAS PROFILING REPORT                                │
│  ├─ Generate comprehensive data quality report                  │
│  ├─ Save as HTML: reports/data_profile_TIMESTAMP.html          │
│  └─ Log to MLflow (DagHub) as artifact                         │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 5: DATA VERSIONING (DVC)                                  │
│  ├─ dvc add data/processed/exchange_rates.csv                   │
│  ├─ dvc push (to DagHub S3 remote storage)                      │
│  ├─ git commit .dvc files                                        │
│  └─ Complete data lineage tracking                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 **Project Structure**

```
Mlops_Project/
├── dags/
│   └── exchange_rate_dag.py          # Complete Airflow DAG (Phase 1)
│
├── data/
│   ├── raw/                           # Raw API responses (timestamped)
│   │   └── exchange_rates_raw_*.csv
│   └── processed/                     # Processed & engineered features
│       ├── exchange_rates.csv         # Main dataset (DVC tracked)
│       └── exchange_rates.csv.dvc     # DVC metadata
│
├── reports/                           # Data quality reports
│   └── data_profile_*.html
│
├── docker-compose.yaml                # Airflow + PostgreSQL + MLflow
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .dvc/                              # DVC configuration
│   └── config                         # Remote storage config (DagHub)
│
├── README.md                          # This file
└── PHASE1_IMPLEMENTATION_GUIDE.md     # Detailed setup guide
```

---

## 🎯 **Phase 1 Requirements Implementation**

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| **1.1: API Data Extraction** | ✅ | `extract_exchange_rate_data()` - Fetches from exchangerate-api.com |
| **1.2: Timestamp & Save Raw** | ✅ | Saves with `YYYYMMDD_HHMMSS` format |
| **2.1: Data Quality Gate** | ✅ | `data_quality_check()` - Fails DAG if thresholds breached |
| **2.2: Transformation** | ✅ | `transform_and_engineer_features()` - Lag, rolling, time features |
| **2.3: Pandas Profiling** | ✅ | `generate_profiling_report()` - HTML report + MLflow artifact |
| **3.1: DVC Versioning** | ✅ | `version_data_with_dvc()` - Automated versioning |
| **3.2: Remote Storage** | ✅ | DagHub S3 bucket configured |
| **Airflow Orchestration** | ✅ | Daily schedule with proper task dependencies |

---

## 🚀 **Quick Start Guide**

### **Prerequisites**

- Docker & Docker Compose installed
- Python 3.9+ (for local development)
- Git installed
- DagHub account (for MLflow & DVC remote)

### **Step 1: Clone & Setup**

```bash
# Clone repository
git clone https://github.com/hamnariaz57/Mlops_Project.git
cd Mlops_Project

# Create environment file
cp .env.example .env
# Edit .env and add your DAGSHUB_TOKEN
```

### **Step 2: Install Python Dependencies (Optional - for local testing)**

```bash
pip install -r requirements.txt
```

### **Step 3: Configure DVC Remote (Already configured)**

```bash
# Verify DVC remote
dvc remote list
# Output: storage  s3://hamnariaz57@dagshub.com/repo-buckets/s3/hamnariaz57
```

### **Step 4: Start Airflow**

```bash
# Start all services (Airflow + PostgreSQL + MLflow)
docker-compose up -d

# Wait for services to be healthy (~2 minutes)
docker-compose ps
```

### **Step 5: Access Airflow UI**

1. Open browser: **http://localhost:8080**
2. Login:
   - Username: `admin`
   - Password: `admin`
3. Enable the DAG: `exchange_rate_mlops_pipeline_phase1`
4. Trigger manually or wait for daily schedule

### **Step 6: Access MLflow UI**

1. Open browser: **http://localhost:5000**
2. View experiment runs, metrics, and artifacts

---

## 📊 **What the Pipeline Does**

### **Data Extraction**
```python
# Fetches from: https://api.exchangerate-api.com/v4/latest/USD
# Returns: ~160 currency exchange rates
# Saved as: data/raw/exchange_rates_raw_20251130_143025.csv
```

### **Quality Checks**
- ❌ **Fails if** > 1% null values
- ❌ **Fails if** < 10 currencies returned
- ❌ **Fails if** schema invalid
- ❌ **Fails if** non-numeric currency values

### **Feature Engineering**

| Feature Type | Examples |
|--------------|----------|
| **Time Features** | `day_of_week`, `month`, `quarter`, `hour` |
| **Lag Features** | `EUR_lag1`, `EUR_lag7` |
| **Rolling Means** | `EUR_rolling_mean_7`, `EUR_rolling_mean_30` |
| **Volatility** | `EUR_rolling_std_7`, `EUR_rolling_std_30` |
| **Rate of Change** | `EUR_pct_change_1d`, `EUR_pct_change_7d` |

### **Outputs**

1. **Processed Dataset**: `data/processed/exchange_rates.csv` (DVC tracked)
2. **Profiling Report**: `reports/data_profile_TIMESTAMP.html`
3. **MLflow Run**: Logged to DagHub with metrics & artifacts
4. **DVC Metadata**: `.dvc` files committed to Git

---

## 🔧 **Configuration**

### **Airflow DAG Configuration**

```python
# In: dags/exchange_rate_dag.py

# Schedule
schedule_interval="@daily"  # Runs every day at midnight

# Data Quality Thresholds
NULL_THRESHOLD = 0.01  # 1% max null values
MIN_REQUIRED_CURRENCIES = 10

# API
API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
```

### **Environment Variables**

```bash
# .env file

DAGSHUB_USERNAME=hamnariaz57
DAGSHUB_TOKEN=your_token_here
MLFLOW_TRACKING_URI=https://dagshub.com/hamnariaz57/Mlops_Project.mlflow
```

---

## 📈 **Monitoring & Logs**

### **Airflow Logs**
```bash
# View scheduler logs
docker-compose logs -f airflow-scheduler

# View webserver logs
docker-compose logs -f airflow-webserver
```

### **Task Logs**
- Access via Airflow UI → DAG → Task → Logs
- Detailed output for each task (extraction, quality check, etc.)

### **MLflow Tracking**
- View runs at: **http://localhost:5000**
- Or on DagHub: **https://dagshub.com/hamnariaz57/Mlops_Project**

---

## 🐛 **Troubleshooting**

### **Issue: Airflow containers not starting**
```bash
# Check logs
docker-compose logs postgres
docker-compose logs airflow-init

# Reset and restart
docker-compose down -v
docker-compose up -d
```

### **Issue: DVC push fails**
```bash
# Verify DagHub credentials
dvc remote list
dvc remote modify storage --local auth basic
dvc remote modify storage --local user hamnariaz57
dvc remote modify storage --local password YOUR_TOKEN

# Test connection
dvc push -r storage
```

### **Issue: MLflow not logging**
```bash
# Check MLflow service
docker-compose ps mlflow

# Verify environment variables in docker-compose
echo $DAGSHUB_TOKEN
```

---

## 📝 **Next Steps (Phase 2)**

Phase 1 establishes the **data pipeline**. Next phases will include:

- ✅ **Phase 2**: Model training & hyperparameter tuning
- ✅ **Phase 3**: Model serving (REST API)
- ✅ **Phase 4**: Concept drift detection & retraining
- ✅ **Phase 5**: Monitoring dashboard

---

## 🤝 **Contributing**

This is an academic project. For questions or improvements:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📜 **License**

This project is for educational purposes as part of an MLOps case study.

---

## 👤 **Author**

**Hamna Riaz**
- GitHub: [@hamnariaz57](https://github.com/hamnariaz57)
- DagHub: [hamnariaz57](https://dagshub.com/hamnariaz57)

---

## 🙏 **Acknowledgments**

- **Exchange Rate API**: [exchangerate-api.com](https://exchangerate-api.com)
- **Apache Airflow**: Workflow orchestration
- **MLflow**: Experiment tracking
- **DVC**: Data version control
- **DagHub**: Remote storage & MLflow hosting

---

## 📞 **Support**

If you encounter issues:

1. Check Airflow logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Ensure DagHub token is valid
4. Review task logs in Airflow UI

---

**Project Deadline**: November 30, 2025  
**Status**: ✅ Phase 1 Complete

---

