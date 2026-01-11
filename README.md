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

🧠 Critical Thinking Responses
1. Which cleaning rules could change business decisions the most, and why?
Answer:

The three most impactful cleaning rules are:

Payment Status Filtering ("Paid" only)

Impact: This rule has the HIGHEST business impact. If we include "Pending" or "Refunded" orders in revenue calculations, we would overstate actual cash flow by potentially 10-30%.
Decision affected: A CEO might approve expansion budgets based on inflated revenue, only to face cash flow problems when pending orders don't convert.
Risk: Conversely, being too strict (excluding legitimate pending orders that will convert) understates pipeline revenue.
Negative/Zero Price Handling

Impact: Negative prices often represent returns, adjustments, or data entry errors. Setting them to 0 or absolute values fundamentally changes margin calculations.
Decision affected: A pricing manager might see artificially high margins if returns are zeroed out instead of subtracted, leading to aggressive pricing that erodes profitability.
Why it matters: A single bulk return of -50,000 AED treated as 0 versus -50,000 could swing a category from "profitable" to "loss-making."
Duplicate Order Handling

Impact: System glitches or data integration issues can create duplicate records. Keeping ALL duplicates inflates revenue; removing ALL might delete legitimate repeat purchases.
Decision affected: Inventory planning relies on accurate demand signals. 2x inflated demand = 2x overstock = capital waste.
My approach: I chose conservative cleaning (filter Paid only, cap negatives at 0) because understating revenue is safer than overstating for cash flow planning. For a growth-focused company, I might be more liberal with pending orders.

2. What uplift assumptions did you choose, and how could they be wrong?
Answer:

###Assumptions Made:

### Assumptions Made:
| Assumption | Value Used |
|------------|-------------|
| Baseline conversion rate | 2% of visitors |
| Promo uplift multiplier | 1.5x - 2.5x based on discount depth |
| Cannibalization rate | 20% of promo sales |
| Margin preservation threshold | 15% minimum margin |


How These Could Be Wrong:

   1.Uplift multiplier is category-dependent:
   *Elastic categories (fashion, electronics): True uplift might be 3-4x
   *Inelastic categories (groceries, essentials): Might only see 1.2x
   *My assumption of uniform 1.5-2.5x ignores this, potentially over-valuing grocery promos and under-valuing fashion promos.
   
   2.Cannibalization rate varies by timing:
    *End-of-month promos: Lower cannibalization (customers wait for payday)
    *Random mid-week promos: Higher cannibalization (planned purchasers just get discount)
    *My flat 20% could be 40% for poorly-timed promos.

   3.No consideration of halo effects:
    *A 50% off TV might drive traffic that buys full-price accessories
    *My ROI calculation ignores this, understating true promo value by potentially 20-30%.

   4.Assumption that historical uplift predicts future:
   *First-time promos have novelty effect (higher uplift)
   *Repeated promos train customers to wait (lower uplift over time)


3. **If budget is fixed, how do you choose between margin floor vs stockout risk?
Answer:**

This is a classic trade-off problem. Here's my framework:

Decision Matrix:

Scenario	Prioritize Margin Floor	Prioritize Stockout Prevention
High-margin products	✅ Protect margins	❌ Stockouts hurt less
High-velocity products	❌ Volume matters more	✅ Every stockout = lost sale
Seasonal products	✅ Can't discount way out	✅ Must be in-stock for peak
Competitive products	❌ Must match prices	✅ OOS sends customers to rivals

My Chosen Approach:
Given fixed budget, I would use a tiered strategy:

diff
Copy code
Tier 1 (60% of budget): Prevent stockouts on TOP 20% revenue products
- These products drive traffic and have highest opportunity cost
- A stockout on a hero SKU can lose the entire basket

Tier 2 (30% of budget): Maintain margin floor on MEDIUM performers
- These are margin contributors, not traffic drivers
- Discount them and you just give away money

Tier 3 (10% of budget): Let TAIL products fluctuate
- Long-tail SKUs have low volume anyway
- Use them for clearance when needed
Quantitative Justification:

Stockout cost = (Daily sales rate) × (Days OOS) × (Margin per unit) × (1 + Customer loss factor)
Margin erosion cost = (Units sold) × (Discount given) × (Could-have-been margin)
For a $50 product with 50% margin selling 10/day:

3-day stockout = 10 × 3 × $25 × 1.3 = $975 lost
10% unnecessary discount on 30 units = 30 × $5 = $150 lost
Conclusion: For most retail scenarios, stockout prevention wins for high-velocity items because the cost multiplier (customer loss, competitive switching) amplifies losses beyond the immediate sale.

4. **What did you exclude to finish in 2 hours (scope control)?
Answer**

Explicitly Excluded Features:

Feature	Why Excluded	Time Estimate	Future Priority
User authentication	Not critical for demo	2+ hours	Medium
Data write-back to sheets	Read-only is sufficient	3+ hours	High
Predictive forecasting	Requires ML pipeline	4+ hours	High
Email alert system	Infrastructure needed	2+ hours	Medium
Multi-currency support	Assumed single market (AED)	1 hour	Low
Custom date range picker	Used automatic date detection	45 min	Medium
PDF report export	Focused on interactive view	1.5 hours	High
Benchmark comparisons	No industry data available	2+ hours	Low
A/B test analysis	No experimental data structure	3+ hours	Medium
Supplier lead time integration	Out of scope for sales dashboard	2+ hours	High

Technical Debt Accepted:
*Hardcoded Google Sheet names - Should be configurable
*No caching layer - Data reloads on every interaction
*Limited error messages - Generic "data not available" vs specific errors
*No unit tests - Relied on manual testing
*Single-threaded data loading - Could parallelize sheet reads

Scope Control Decisions:

*Chose Plotly over custom D3.js - Faster development, good enough visuals
*Used Streamlit's native layout - Not custom CSS grid
*Skipped mobile optimization - Desktop-first for analyst use case
*No dark mode persistence - Resets on refresh (would need cookies/session)

**⚠️ Limitations & Future Work**
Current Limitations
No real-time streaming (batch refresh only)
Limited to Google Sheets data source
No user-level access control
Charts may slow with >100K rows

Planned Improvements
 Add BigQuery connector for large datasets
 Implement Redis caching layer
 Build automated anomaly detection
 Create mobile-responsive views
 Add Slack/Teams alert integration

 
👤 Author
Gagandeep Singh 
Kartik Joshi 
Samuel Alex 
Prem Kukreja

Course: [MAIB]
Date: January 2026
Time Spent: ~2 hours (core development)
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Streamlit team for the amazing framework
Plotly for interactive visualizations
Google Sheets API for data connectivity
Course instructors for the challenge prompt

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/UAE-Pulse-Simulator-Data-Rescue-Dashboard.git
cd UAE-Pulse-Simulator-Data-Rescue-Dashboard
