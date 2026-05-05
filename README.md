# 🔍 DataQuality Pro
> Automated Data Quality Audit & Monitoring System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dataquality-pro.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Live Demo
**[► Try the live app → dataquality-pro.streamlit.app](https://dataquality-pro.streamlit.app)**

Upload any CSV or Excel file and get a full quality 
audit report in seconds — no setup required.

---

## ✨ What it does

DataQuality Pro audits any dataset across 5 dimensions
and returns an actionable quality score with recommendations.

| Dimension | What it checks |
|-----------|---------------|
| ✅ Completeness | Missing values per column |
| ✅ Uniqueness | Duplicate row detection |
| ✅ Outliers | IQR-based anomaly detection |
| ✅ Consistency | Value range validation |
| ✅ Data Types | Column type classification |

**Output:** 0–100 quality score · A–F grade · 
Plain-English recommendations

---

## 🛠 Tech Stack

| Layer | Tools |
|-------|-------|
| Core engine | Python · pandas · numpy |
| Web interface | Streamlit · Plotly |
| Database support | PostgreSQL · SQLAlchemy |
| Analysis notebook | Jupyter · seaborn · matplotlib |
| Deployment | Streamlit Community Cloud |

---

## 📥 Supported Input Sources

- 📁 **CSV & Excel** — upload any file directly
- 🗄️ **PostgreSQL** — connect and query live databases
- 🌐 **REST API** — fetch and audit any JSON endpoint

---

## ⚡ Quick Start (run locally)

git clone https://github.com/abduljelil3349/dataquality-pro
cd dataquality-pro
pip install -r requirements.txt
streamlit run app/streamlit_app.py

---

## 📁 Project Structure

dataquality-pro/
├── core/
│   ├── __init__.py          # Package initialiser
│   ├── loader.py            # Multi-source data loader
│   ├── quality_checks.py    # Quality engine
│   └── reporter.py          # Report exporter
├── app/
│   └── streamlit_app.py     # Web interface
├── notebooks/
│   └── DataQuality_Pro_Full_Analysis.ipynb
├── sample_data/
│   └── titanic.csv
├── outputs/                 # Generated reports
├── requirements.txt
└── README.md

---

## 📊 Sample Output

**Titanic Dataset Audit Results:**
- Overall Score: 96.8/100 — Grade A
- Completeness: 91.9/100 (Cabin 77.1% missing)
- Uniqueness: 100/100 (zero duplicates)
- Outliers detected in: Age, Fare, SibSp, Parch

---

## 👤 Author

**Abduljelil Olalekan**
Data Analyst & Research Data Specialist
7+ years experience @ IITA

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/abduljelil)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/abduljelil3349)