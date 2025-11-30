# 🚀 MLOps Real-Time Predictive System (RPS) - Exchange Rate Prediction

[![MLOps Phase 1](https://img.shields.io/badge/Phase%201-Complete-brightgreen)]()
[![Apache Airflow](https://img.shields.io/badge/Orchestration-Airflow-017CEE)]()
[![MLflow](https://img.shields.io/badge/Tracking-MLflow-0194E2)]()
[![DVC](https://img.shields.io/badge/Versioning-DVC-945DD6)]()

> **Academic Project**: MLOps Case Study - Building a Real-Time Predictive System with automated data pipelines, quality gates, and continuous monitoring.

---

## 📋 **Overview**

This project implements a **production-grade MLOps Phase 1 pipeline** for exchange rate prediction using time-series data. It demonstrates end-to-end MLOps practices including:

- ✅ **Automated Data Ingestion** from live APIs
- ✅ **Mandatory Data Quality Gates** (fail-fast validation)
- ✅ **Time-Series Feature Engineering** (lag, rolling, volatility)
- ✅ **Data Versioning** with DVC & DagHub S3
- ✅ **Experiment Tracking** with MLflow
- ✅ **Workflow Orchestration** with Apache Airflow

**Problem**: Predict exchange rates using ~160 currency pairs updated daily  
**Data Source**: [Exchange Rate API](https://api.exchangerate-api.com) (live, no API key required)  
**Deadline**: November 30, 2025 ✅ **COMPLETE**

---

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│              Apache Airflow Orchestration                    │
│                    (Daily Schedule)                          │
└─────────────────────────────────────────────────────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    ▼                      ▼                      ▼
┌────────┐          ┌───────────┐          ┌──────────┐
│  API   │   →      │  Quality  │    →     │ Feature  │
│ Fetch  │          │  Checks   │          │Engineer  │
└────────┘          └───────────┘          └──────────┘
                          │
                    ❌ FAIL GATE
                          │
    ┌─────────────────────┼─────────────────────┐
    ▼                     ▼                     ▼
┌─────────┐         ┌──────────┐         ┌──────────┐
│ Pandas  │   →     │  MLflow  │    →    │   DVC    │
│Profiling│         │Artifacts │         │Versioning│
└─────────┘         └──────────┘         └──────────┘
                                               │
                                               ▼
                                    ┌─────────────────┐
                                    │  DagHub S3      │
                                    │Remote Storage   │
                                    └─────────────────┘
```

---

## 🚀 **Quick Start (5 minutes)**

### **Prerequisites**
- Docker & Docker Compose
- Git
- DagHub account (free) for remote storage

### **1. Clone & Configure**
```powershell
git clone https://github.com/hamnariaz57/Mlops_Project.git
cd Mlops_Project

# Create environment file
cp .env.example .env
# Edit .env and add your DAGSHUB_TOKEN
```

### **2. Build & Start**
```powershell
docker-compose build
docker-compose up -d

# Wait ~2 minutes for initialization
docker-compose ps
```

### **3. Access & Run**
1. **Airflow UI**: http://localhost:8080 (login: `admin`/`admin`)
2. Find DAG: `exchange_rate_mlops_pipeline_phase1`
3. Toggle **ON** and click **Trigger DAG**
4. **MLflow UI**: http://localhost:5000

---

## 📁 **Project Structure**

```
Mlops_Project/
├── dags/
│   └── exchange_rate_dag.py      # Complete ETL pipeline (5 tasks)
├── data/
│   ├── raw/                       # Timestamped API responses
│   └── processed/                 # Engineered features (DVC tracked)
├── reports/                       # Pandas Profiling HTML reports
├── docker-compose.yaml            # Multi-service orchestration
├── Dockerfile                     # Custom Airflow image
├── requirements.txt               # Python dependencies
├── .dvc/                          # DVC configuration
│   └── config                     # DagHub S3 remote
└── docs/
    ├── PHASE1_COMPLETE.md         # Full project overview
    ├── SETUP_GUIDE.md             # Detailed setup instructions
    ├── TROUBLESHOOTING.md         # Common issues & solutions
    ├── QUICK_REFERENCE.md         # Command cheat sheet
    └── PHASE1_SUMMARY.md          # Implementation summary
```

---

## 🎯 **Phase 1 Implementation**

### **✅ Completed Requirements**

| Component | Implementation | Status |
|-----------|----------------|--------|
| **API Extraction** | Fetches 160+ currencies daily from live API | ✅ |
| **Timestamp Raw Data** | Saves with `YYYYMMDD_HHMMSS` format | ✅ |
| **Quality Gate** | Fails pipeline if data quality thresholds breached | ✅ |
| **Feature Engineering** | Lag, rolling means, volatility, time-based | ✅ |
| **Pandas Profiling** | Automated HTML report generation | ✅ |
| **MLflow Logging** | Experiment tracking + artifact storage | ✅ |
| **DVC Versioning** | Automated data versioning & remote push | ✅ |
| **DagHub Storage** | S3-compatible remote storage | ✅ |
| **Airflow Orchestration** | Daily scheduled DAG execution | ✅ |

---

## 📊 **Pipeline Details**

### **Task 1: Data Extraction** ⬇️
- **API**: `https://api.exchangerate-api.com/v4/latest/USD`
- **Output**: `data/raw/exchange_rates_raw_YYYYMMDD_HHMMSS.csv`
- **Includes**: Timestamp, base currency, ~160 exchange rates

### **Task 2: Quality Check (MANDATORY GATE)** ⚠️
**Fails DAG if**:
- Null values > 1%
- < 10 currencies present
- Schema validation fails
- Non-numeric currency values

### **Task 3: Feature Engineering** 🔧
**Creates**:
- **Time features**: day_of_week, month, quarter, hour
- **Lag features**: 1-day, 7-day historical values
- **Rolling means**: 7-day, 30-day averages
- **Volatility**: Rolling standard deviation
- **Rate of change**: Daily and weekly percentage changes

**Output**: `data/processed/exchange_rates.csv` (~200+ features)

### **Task 4: Profiling Report** 📊
- **Tool**: ydata-profiling (Pandas Profiling)
- **Output**: `reports/data_profile_TIMESTAMP.html`
- **Logged to**: MLflow as artifact

### **Task 5: DVC Versioning** 📦
- **Commands**: `dvc add` → `dvc push` → `git commit`
- **Remote**: DagHub S3 bucket
- **Tracked**: `.dvc` metadata files in Git

---

## 🔧 **Technology Stack**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Orchestration** | Apache Airflow 2.7.1 | Workflow scheduling & management |
| **Tracking** | MLflow 2.9.2 | Experiment logging & artifacts |
| **Versioning** | DVC 3.32.1 | Data version control |
| **Storage** | DagHub S3 | Remote data storage |
| **Database** | PostgreSQL 13 | Airflow metadata |
| **Containerization** | Docker Compose | Multi-service deployment |
| **Language** | Python 3.9+ | Data processing & ML |

---

## 📈 **Key Features**

### **Robustness** 💪
- Fail-fast quality gates
- Automatic retry on task failure (2 retries)
- Comprehensive logging at every step
- Error handling with detailed messages

### **Scalability** 🚀
- Daily automated execution
- Historical data accumulation
- Configurable schedule (hourly/weekly)
- Efficient storage with DVC

### **Observability** 👁️
- MLflow experiment tracking
- Pandas Profiling data insights
- Airflow task-level monitoring
- Complete data lineage tracking

---

## 📚 **Documentation**

| File | Purpose |
|------|---------|
| [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) | Comprehensive project overview & architecture |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Step-by-step setup & execution instructions |
| [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md) | Detailed implementation summary |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues & solutions |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Command cheat sheet |

---

## 🛠️ **Essential Commands**

```powershell
# Build and start services
docker-compose build
docker-compose up -d

# View logs
docker-compose logs -f airflow-scheduler

# Trigger DAG manually
docker-compose exec airflow-scheduler airflow dags trigger exchange_rate_mlops_pipeline_phase1

# Stop services
docker-compose down

# Complete reset
docker-compose down -v
docker system prune -a
```

---

## 🐛 **Troubleshooting**

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

**Quick fixes**:
- **Import errors**: `docker-compose build` (uses Dockerfile with packages)
- **DVC auth fails**: Configure with `dvc remote modify storage --local auth basic`
- **DAG not showing**: Check `docker-compose logs airflow-scheduler` for errors

---

## 🎓 **What This Project Demonstrates**

1. **Production MLOps Practices**
   - Automated pipelines
   - Data quality validation
   - Version control for data & code
   - Experiment tracking

2. **Time-Series ML Engineering**
   - Feature engineering for forecasting
   - Lag and rolling window features
   - Handling concept drift (foundation for Phase 2)

3. **Infrastructure as Code**
   - Docker containerization
   - Multi-service orchestration
   - Reproducible environments

4. **Best Practices**
   - Fail-fast quality gates
   - Comprehensive logging
   - Documentation-first approach
   - Modular, maintainable code

---

## 📊 **Expected Outputs**

After first successful run:

```
data/raw/exchange_rates_raw_20251130_143025.csv          ← Raw API data
data/processed/exchange_rates.csv                        ← Engineered features
data/processed/exchange_rates.csv.dvc                    ← DVC metadata (Git)
reports/data_profile_20251130_143025.html               ← Profiling report
MLflow: Run with parameters, metrics, artifacts         ← Experiment tracking
DagHub: Data versioned in S3 bucket                     ← Remote storage
```

---

## 🚀 **Next Steps (Phases 2-5)**

- **Phase 2**: Model training & hyperparameter tuning
- **Phase 3**: Model serving via REST API
- **Phase 4**: Concept drift detection & auto-retraining
- **Phase 5**: Monitoring dashboard & alerting

---

## 👤 **Author**

**Hamna Riaz**  
- GitHub: [@hamnariaz57](https://github.com/hamnariaz57)
- DagHub: [hamnariaz57](https://dagshub.com/hamnariaz57)
- Project: [Mlops_Project](https://github.com/hamnariaz57/Mlops_Project)

---

## 📜 **License**

Educational project for MLOps case study. See course requirements for usage terms.

---

## 🙏 **Acknowledgments**

- **Exchange Rate API**: Free live exchange rate data
- **Apache Airflow**: Workflow orchestration framework
- **MLflow**: Experiment tracking platform
- **DVC**: Data version control tool
- **DagHub**: MLOps platform for collaboration

---

## ✅ **Status**

**Phase 1**: ✅ **COMPLETE** (November 30, 2025)  
**All Requirements**: ✅ **IMPLEMENTED**  
**Documentation**: ✅ **COMPREHENSIVE**  
**Ready for**: ✅ **EVALUATION**

---

## 📞 **Support**

For issues:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review Airflow logs: `docker-compose logs -f airflow-scheduler`
3. Verify `.env` configuration
4. See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed steps

---

**🎉 Phase 1 Implementation Complete! Ready for submission.**
