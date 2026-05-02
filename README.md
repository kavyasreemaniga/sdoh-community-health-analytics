# SDOH Community Health Analytics Platform

A production-grade data engineering portfolio project demonstrating end-to-end pipeline development for **Social Drivers of Health (SDOH)** program analytics in community health settings.

---

## 📋 Project Overview

This platform integrates synthetic clinical data (Epic FHIR via Synthea), SDOH screening results (PRAPARE framework), and community program referrals to track intervention effectiveness and health equity outcomes across patient populations.

**Built to demonstrate:** Healthcare data engineering skills for community health and population health analytics roles.

---

## 🏗️ Architecture

┌─────────────────────────────────────────────────────┐
│  Phase 1: Data Generation                           │
│  Synthea FHIR → Python Scripts → CSV Files          │
└─────────────────────────┬───────────────────────────┘
│
┌─────────────────────────▼───────────────────────────┐
│  Phase 2: Database & Ingestion                      │
│  Python Pipeline → PostgreSQL (Bronze Schema)       │
└─────────────────────────┬───────────────────────────┘
│
┌─────────────────────────▼───────────────────────────┐
│  Phase 3: dbt Transformations                       │
│  Bronze → Staging (Silver) → Marts (Gold)           │
└─────────────────────────┬───────────────────────────┘
│
┌─────────────────────────▼───────────────────────────┐
│  Phase 4: Dashboards                                │
│  Tableau Public - 3 Interactive Dashboards          │
└─────────────────────────────────────────────────────┘
---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Generation | Synthea FHIR Generator, Python (Pandas, Faker) |
| Database | PostgreSQL 15 |
| Transformation | dbt (data build tool) |
| Orchestration | Apache Airflow (planned) |
| Analytics | Tableau Public (planned) |
| Languages | Python 3.12, SQL |
| Version Control | Git / GitHub |

---

## 📊 Dataset Summary

| Dataset | Rows | Description |
|---------|------|-------------|
| Patients | 1,134 | Synthea FHIR synthetic patients (Colorado) |
| SDOH Screenings | 1,725 | PRAPARE framework screenings |
| Community Referrals | 1,520 | Program interventions & outcomes |

**Key Metrics:**
- 🔴 High-Risk Patients: 150 (8.7%)
- 🟡 Moderate-Risk: 527 (30.5%)
- 🟢 Low-Risk: 1,048 (60.8%)
- ✅ Referral Completion Rate: 69.0%
- ⏱️ Average Days to Service: 49.5 days

---

## 🏥 Healthcare Domain Coverage

- **Epic FHIR Integration** - Synthea generates Epic-compatible FHIR R4 data
- **PRAPARE Framework** - 9-domain SDOH screening standard used by FQHCs
- **ICD-10 Z-codes** - Social determinants coded per clinical standards
- **HIPAA Compliance** - Synthetic data only, no real PHI
- **Health Equity** - Demographic analysis of disparities in access and outcomes

---

## 📁 Project Structure

sdoh-community-health-analytics/
├── src/
│   ├── data_generation/
│   │   ├── generate_sdoh_screenings.py    # PRAPARE screening generator
│   │   └── generate_community_referrals.py # Referral data generator
│   ├── database/
│   │   ├── create_schemas.sql             # Bronze/Staging/Marts schema
│   │   └── fix_schema.sql                 # Schema updates
│   ├── ingestion/
│   │   ├── load_patients.py               # Patient data loader
│   │   ├── load_sdoh_screenings.py        # Screening data loader
│   │   ├── load_community_referrals.py    # Referral data loader
│   │   └── load_all_data.py               # Master load script
│   └── utils/
│       └── db_connection.py               # Database connection utility
├── dbt_sdoh_analytics/
│   ├── models/
│   │   ├── staging/
│   │   │   └── bronze/
│   │   │       ├── sources.yml            # Bronze source definitions
│   │   │       ├── stg_patients.sql       # Patient staging model
│   │   │       ├── stg_sdoh_screenings.sql # Screening staging model
│   │   │       └── stg_community_referrals.sql # Referral staging model
│   │   └── marts/
│   │       ├── core/
│   │       │   └── fct_patient_sdoh_summary.sql  # Patient fact table
│   │       └── program_performance/
│   │           ├── rpt_program_performance.sql    # Program metrics
│   │           └── rpt_health_equity_dashboard.sql # Equity metrics
│   ├── macros/
│   │   └── get_custom_schema.sql          # Custom schema macro
│   ├── dbt_project.yml                    # dbt project config
│   └── README.md                          # dbt documentation
├── docs/
│   └── DASHBOARDS.md                      # Dashboard documentation
├── data/
│   └── DATA_SUMMARY.md                    # Dataset documentation
├── requirements.txt
├── .gitignore
└── README.md
---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 15
- Java 11+ (for Synthea)
- dbt-postgres

### 1. Clone Repository

```bash
git clone https://github.com/kavyasreemaniga/sdoh-community-health-analytics.git
cd sdoh-community-health-analytics
```

### 2. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Database

```bash
# Create PostgreSQL database
psql postgres
CREATE DATABASE sdoh_analytics;
CREATE USER sdoh_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE sdoh_analytics TO sdoh_user;
\q

# Create schemas
psql -U sdoh_user -d sdoh_analytics -h localhost -f src/database/create_schemas.sql
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 5. Generate Synthetic Data

```bash
# Install and run Synthea (requires Java 11+)
git clone https://github.com/synthetichealth/synthea.git tools/synthea
cd tools/synthea && ./gradlew build
./run_synthea -p 1000 Colorado
cd ../..

# Copy generated data
cp tools/synthea/output/csv/* data/raw/csv/

# Generate SDOH screenings
python src/data_generation/generate_sdoh_screenings.py

# Generate community referrals
python src/data_generation/generate_community_referrals.py
```

### 6. Load Data into PostgreSQL

```bash
python src/ingestion/load_all_data.py
```

### 7. Run dbt Transformations

```bash
cd dbt_sdoh_analytics
dbt deps
dbt run
dbt test
dbt docs generate && dbt docs serve
```

---

## 🧪 dbt Models

### Staging Layer (Bronze → Silver)

| Model | Type | Description |
|-------|------|-------------|
| `stg_patients` | View | Cleaned patient demographics, age calculations, standardized fields |
| `stg_sdoh_screenings` | View | Standardized PRAPARE screenings with risk scoring |
| `stg_community_referrals` | View | Enriched referral data with service categorization |

### Marts Layer (Silver → Gold)

| Model | Type | Description |
|-------|------|-------------|
| `fct_patient_sdoh_summary` | Table | One row per patient - latest SDOH status + referral metrics |
| `rpt_program_performance` | Table | Monthly program metrics by service type |
| `rpt_health_equity_dashboard` | Table | Demographic disparities in access and outcomes |

---

## 📈 Key Analytics

### SDOH Risk Scoring (0-10 Scale)

| Domain | Max Points | Trigger |
|--------|-----------|---------|
| Housing | 3 | Homeless = 3, Unstable = 2 |
| Food Security | 2 | Hunger Vital Sign score |
| Transportation | 1 | Any barriers = 1 |
| Utilities | 1 | Assistance needed = 1 |
| Employment | 2 | Unemployed = 2 |
| Social Isolation | 2 | Score ≥ 3 = 2 |
| Financial Strain | 2 | Severe = 2, Moderate = 1 |

**Risk Categories:**
- 🟢 Low Risk: 0-3
- 🟡 Moderate Risk: 4-6
- 🔴 High Risk: 7-10

---

## 🔬 Data Quality

All dbt models include automated tests:
- ✅ Unique primary keys
- ✅ Not null constraints
- ✅ Referential integrity (foreign keys)
- ✅ Accepted values (risk categories, referral status)
- ✅ Row count verification

---

## 🗺️ Roadmap

- [x] Phase 1: Synthetic data generation (Synthea + PRAPARE)
- [x] Phase 2: PostgreSQL database + Python ingestion pipeline
- [x] Phase 3: dbt transformation layer (staging + marts)
- [ ] Phase 4: Tableau Public dashboards 
- [ ] Phase 5: Apache Airflow orchestration
- [ ] Phase 6: ML risk prediction model
- [ ] Phase 7: CI/CD with GitHub Actions

---

## 👩‍💻 Author

**Kavya Sree Maniga**
- 📧 kavyasreede@gmail.com
- 💼 [LinkedIn](https://linkedin.com/in/kavyasreede)
- 🐙 [GitHub](https://github.com/kavyasreemaniga)

---

## 📄 License

MIT License - Educational/Portfolio Use Only

> ⚠️ **Note:** All patient data is synthetic and generated using Synthea. No real patient information is used in this project.
