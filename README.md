# 🛒 UAE Pulse Simulator + Data Rescue Dashboard

A comprehensive Streamlit dashboard for UAE e-commerce data analysis, cleaning, and campaign simulation.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📋 Overview

This dashboard provides:

- **📂 Data Management**: Upload and preview e-commerce data files
- **🧹 Data Rescue**: Detect and fix 15+ types of dirty data issues
- **🎯 Campaign Simulator**: Run what-if scenarios for promotional campaigns
- **📊 Analytics**: Visualize KPIs, trends, and performance metrics

---

## ✨ Features

### Data Cleaning (15+ Issue Types)
| Issue Type | Description |
|------------|-------------|
| Missing Values | NULL/NaN in required fields |
| Null Representations | Strings like 'N/A', 'null', '-' |
| Duplicates | Duplicate order_ids, product_ids |
| Invalid Timestamps | Corrupted/unparseable dates |
| Mixed Date Formats | Inconsistent date formats |
| Whitespace | Leading/trailing spaces |
| Mixed Case | Inconsistent capitalization |
| Invalid Values | Values not in valid list |
| Outliers | Extreme quantities/prices |
| Negative Values | Negative stock/quantities |
| FK Violations | Invalid foreign key references |
| Boolean Strings | 'Yes'/'No' instead of True/False |

### Campaign Simulator
- **Demand Lift Calculation**: Based on discount %, category elasticity, channel efficiency
- **ROI Forecasting**: Expected revenue, profit, and margin
- **What-If Scenarios**: Test different campaign parameters
- **Warning System**: Alerts for low margin, negative ROI

### Analytics Dashboard
- Revenue trends over time
- Performance by city, channel, category
- Inventory health and stockout risk
- KPI cards with key metrics

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/UAE-Pulse-Simulator-Data-Rescue-Dashboard.git
cd UAE-Pulse-Simulator-Data-Rescue-Dashboard
