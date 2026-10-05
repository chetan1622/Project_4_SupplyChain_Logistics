# Supply Chain & Logistics Analytics

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python) ![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql) ![Pandas](https://img.shields.io/badge/Pandas-1.5+-green?logo=pandas) ![Matplotlib](https://img.shields.io/badge/Matplotlib-3.6+-red) ![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

> **End-to-end supply chain analytics pipeline** processing 60,000+ multi-table records to identify ₹1.9Cr freight cost savings, vendor risk segments, and stockout patterns across 20 Indian warehouses.

---

## 🎯 Problem Statement

Modern supply chains suffer from **invisible inefficiencies**: companies overspend on air freight when road/rail would suffice, fail to detect underperforming vendors until it's too late, and carry dead stock that silently drains working capital. Without data-driven visibility, procurement teams rely on gut instinct — leading to stockouts, cost overruns, and missed SLAs.

This project builds an **end-to-end analytics pipeline** that transforms raw supply chain transactions into actionable intelligence across 5 critical business domains.

---

## 📊 Dataset Overview

| Table | Rows | Key Columns | Purpose |
|-------|------|-------------|---------|
| `products.csv` | 500 | product_id, category, unit_price_inr, weight_kg | Product master |
| `suppliers.csv` | 200 | supplier_id, gstin, on_time_delivery_rate, quality_rating | Vendor master |
| `warehouses.csv` | 20 | warehouse_id, region, capacity_units, utilization_pct | Warehouse master |
| `orders.csv` | 50,000 | order_id, delay_days, freight_mode, freight_cost_inr | Transaction data |
| `inventory.csv` | 10,000 | snapshot_date, closing_stock, stockout_flag, days_of_inventory | Stock snapshots |

**Time Period**: January 2023 – September 2024 | **Geography**: 15 Indian cities, 5 regions

---

## 🔑 Key Insights

- 📦 **₹1.87Cr annual freight savings** identified by switching 30% of Air shipments to Road (₹89.3/kg → ₹12.4/kg)
- 🏭 **4 warehouses flagged as OVERLOADED** (>85% utilization) — Mumbai Central and Delhi North at 91%+
- ⚠️ **34 SKUs classified as HIGH RISK** for stockout — all from Pharma and Electronics categories
- 🚚 **22% of suppliers** fall in the At-Risk/Critical tier — accounting for ₹4.2Cr of annual procurement spend
- 💤 **18.4% of SKUs are dead stock** (turnover < 2x) — holding cost of ₹67L annually in tied-up capital

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.9+ | Core pipeline & analytics |
| Pandas | 1.5+ | Data manipulation |
| NumPy | 1.23+ | Numerical computations |
| Matplotlib + Seaborn | 3.6+ | Dashboards & visualization |
| MySQL | 8.0 | Business queries |
| Faker | 15.0+ | Synthetic data generation |

---

## 📁 Project Structure

```
Project_4_SupplyChain_Logistics/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                        ← Generated raw CSVs (5 tables)
│   └── processed/                  ← Cleaned & enriched CSVs
├── src/
│   ├── 01_data_generation.py       ← Synthetic data generator (60K+ records)
│   ├── 02_data_cleaning.py         ← Data cleaning & feature engineering
│   ├── 03_analytics_engine.py      ← 5 analytics modules
│   └── 04_visualization.py         ← 8-panel executive dashboard
├── sql/
│   └── business_problems.sql       ← 10 MySQL business queries
└── reports/
    ├── supply_chain_dashboard.png  ← Executive dashboard (300 DPI)
    └── analytics_summary.txt       ← Printed analysis results
```

---

## 🚀 How to Run

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/Project_4_SupplyChain_Logistics.git
cd Project_4_SupplyChain_Logistics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate synthetic data (creates 60K+ records)
python src/01_data_generation.py

# 4. Clean and validate data
python src/02_data_cleaning.py

# 5. Run analytics engine
python src/03_analytics_engine.py

# 6. Generate dashboard
python src/04_visualization.py

# 7. Open MySQL Workbench, run SQL queries
#    File → sql/business_problems.sql
```

---

## 📈 Dashboard Preview

See `reports/supply_chain_dashboard.png` — 8-panel dashboard covering:
- Supplier On-Time Delivery Rankings
- Monthly Order Volume Trend
- Freight Mode Distribution
- Freight Cost Optimization Opportunity
- Warehouse Utilization Heatmap
- Dead Stock Analysis
- Delivery Performance by Mode
- Stockout Events Timeline

---

## 💼 Resume Bullet Points

> Copy-paste these directly into your resume:

- Built end-to-end **supply chain analytics pipeline** on 60,000+ multi-table records using Python & MySQL, identifying **₹1.87Cr annual freight savings** through Air-to-Road mode-shift analysis
- Developed **vendor performance scoring model** evaluating 200 suppliers across on-time delivery, quality, and order value KPIs — classified 22% as At-Risk, enabling targeted procurement action
- Engineered **demand-supply gap analysis** detecting 34 HIGH RISK SKUs prone to stockout, reducing potential revenue loss through proactive reorder-point recalibration
- Designed **8-panel executive operations dashboard** (Matplotlib/Seaborn) visualizing warehouse utilization heatmaps, freight cost benchmarks, and monthly inventory KPIs for supply chain leadership

---

## 🗄️ SQL Business Problems

| # | Problem | Business Impact |
|---|---------|----------------|
| 1 | Overall supply chain KPI health check | Leadership dashboard |
| 2 | Top 10 suppliers by on-time delivery | Preferred supplier agreements |
| 3 | Monthly demand vs supply gap | Procurement planning |
| 4 | Freight cost by mode + optimization | ₹1.87Cr cost saving |
| 5 | Warehouse capacity utilization ranking | Expansion decisions |
| 6 | Dead stock identification + holding cost | Working capital recovery |
| 7 | Delay root cause: mode × region | SLA improvement |
| 8 | Vendor risk classification (CASE WHEN) | Procurement policy |
| 9 | Seasonal demand patterns by category | Pre-festival stocking |
| 10 | Rolling 3-month freight cost trend (Window Functions) | Cost forecasting |

---

## 📌 Author

**Chetan** | Data Analyst  
📧 chetan.g.patil1622@gmail.com 

---
*Project built as part of Data Analyst Portfolio — Oct 2024*
