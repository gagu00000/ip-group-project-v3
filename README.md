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

**Question 1: Which cleaning rules could change business decisions the most, and why?**

The three cleaning rules that have the biggest impact on business decisions are:

First, filtering by payment status (keeping only "Paid" orders). This rule has the highest business impact. If we include orders that are still pending or have been refunded in our revenue calculations, we would overstate how much money we actually have. This could be off by 10-30%. Imagine a CEO approving a big expansion budget based on inflated revenue numbers, only to run into cash flow problems later when those pending orders never convert to actual payments. On the flip side, being too strict and excluding legitimate pending orders that will eventually convert means we understate our expected revenue.

Second, handling negative or zero prices. Negative prices usually represent returns, adjustments, or simple data entry mistakes. When we set these to zero or convert them to positive numbers, it fundamentally changes our margin calculations. A pricing manager might see artificially high profit margins if we zero out returns instead of subtracting them properly. This could lead to aggressive pricing decisions that actually hurt profitability. For example, if there's a bulk return worth -50,000 AED and we treat it as 0 instead of -50,000, it could make a category look profitable when it's actually losing money.

Third, handling duplicate orders. Sometimes system glitches or data integration problems create duplicate records in our data. If we keep all duplicates, we inflate our revenue numbers. But if we remove too aggressively, we might delete legitimate repeat purchases from the same customer. This matters a lot for inventory planning because if our demand signal is doubled due to duplicates, we'll order twice as much inventory as we need, wasting money on overstock.

For this project, we chose conservative cleaning rules. We filter to only Paid orders and cap negative values at zero. We believe understating revenue is safer than overstating it when it comes to cash flow planning. A company that is focused on aggressive growth might choose to be more liberal with including pending orders.

**Question 2: What uplift assumptions did you choose, and how could they be wrong?**

For calculating promotion effectiveness, we made these assumptions:

We assumed a baseline conversion rate of 2% of visitors, which is a typical industry average for retail. For the promotion uplift multiplier, we used 1.5x for small discounts under 20%, going up to 2.5x for deep discounts over 40%. We assumed a cannibalization rate of 20%, meaning 20% of people who bought during the promo would have bought anyway at full price. We also set a margin preservation threshold of 15%, meaning any promo that drops margin below 15% is considered unprofitable.

Here's how these assumptions could be wrong:

The uplift multiplier is not the same for every product category. Elastic categories like fashion and electronics might see 3-4x uplift from a good discount because customers are very price sensitive. Inelastic categories like groceries and everyday essentials might only see 1.2x uplift because people buy them regardless of price. Our assumption of a uniform 1.5-2.5x multiplier ignores this difference, which could mean we are overvaluing grocery promotions and undervaluing fashion promotions.

The cannibalization rate changes based on when you run the promotion. If you run a promo at the end of the month when people have just been paid, cannibalization is lower because customers weren't planning to buy yet. If you run a random mid-week promo, cannibalization is higher because people who were already planning to buy just get a discount they didn't need. Our flat 20% assumption could actually be 40% for poorly timed promotions.

We also didn't consider halo effects. When you offer 50% off on a TV, you might drive traffic into the store that ends up buying full-price accessories like cables and mounts. Our ROI calculation completely ignores this additional revenue, which means we are probably understating the true value of promotions by 20-30%.

Finally, we assumed that past promotion performance predicts future performance. But first-time promotions have a novelty effect and tend to perform better. When you repeat the same promotion over and over, customers learn to wait for it, which reduces uplift over time.

If we had more time, we would segment our uplift calculations by category, time of year, and how frequently we've run similar promotions before.

**Question 3: If budget is fixed, how do you choose between margin floor vs stockout risk?**

This is a classic trade-off where you can't have everything. Here's how we think about it:

Protecting margin floor means you refuse to discount below a certain level to preserve profitability. Preventing stockouts means you invest in keeping products in stock even if it costs more.

Our approach is a tiered strategy:

For the top 20% of products by revenue, we would spend 60% of the budget preventing stockouts. These products drive traffic to the store and have the highest opportunity cost when they're unavailable. If a customer comes looking for a hero product and it's out of stock, they might leave without buying anything else. You lose the entire basket, not just that one item.

For medium-performing products, we would spend 30% of the budget maintaining the margin floor. These products contribute to profits but don't drive traffic on their own. If you discount them too much, you're just giving away money without attracting new customers.

For the long tail of slow-moving products, we would only spend 10% of the budget. These items have low volume anyway, so neither stockouts nor margin erosion matters as much. You can use them for clearance when needed.

Here's a simple example to show why stockout prevention usually wins for high-velocity items:

Consider a product that costs $50, has a 50% margin ($25 profit), and sells 10 units per day. If you're out of stock for 3 days, you lose 30 potential sales. That's $750 in lost profit. But it's actually worse because some of those customers will go to a competitor and might not come back. If you add a 30% customer loss factor, you're really losing about $975.

Now compare that to giving an unnecessary 10% discount on 30 units. You lose $5 per unit, which is only $150 total.

The stockout costs way more. This is why for most retail situations, especially for popular fast-selling items, preventing stockouts should be the priority over protecting margins.

**Question 4: What did you exclude to finish in 2 hours (scope control)?**

To complete this project in 2 hours, we had to make some tough decisions about what to leave out.

Features we excluded:

We did not build user authentication because it wasn't critical for a demo and would have taken at least 2 more hours. We skipped the ability to write data back to Google Sheets since read-only functionality was enough for an analytics dashboard. Predictive forecasting would have required setting up a machine learning pipeline which would take 4+ hours. An email alert system needs additional infrastructure that was out of scope. We assumed a single currency (AED) instead of building multi-currency support. We used automatic date detection instead of building a custom date range picker. We focused on interactive viewing instead of PDF report export. We didn't include industry benchmark comparisons because we had no benchmark data available. A/B test analysis wasn't possible without experimental data in the right structure. Supplier lead time integration was out of scope for a sales-focused dashboard.

Technical shortcuts we accepted:

We hardcoded the Google Sheet names instead of making them configurable. There's no caching layer, so data reloads every time you interact with the dashboard. Error messages are generic like "data not available" instead of specific helpful messages. We didn't write any unit tests and relied on manual testing. Data loading happens one sheet at a time instead of loading multiple sheets in parallel.

Other scope decisions:

We chose Plotly instead of building custom D3.js visualizations because it's faster to develop and looks good enough. We used Streamlit's built-in layout system instead of custom CSS grids. We focused on desktop users and skipped mobile optimization since analysts typically use laptops. The dark mode setting resets when you refresh the page because saving it would require cookies or session storage.

If we had 2 more hours, we would add:

Data caching with automatic refresh every few minutes, which would take about 30 minutes. Download buttons to export each chart as CSV would take another 30 minutes. A global date range filter that affects all tabs would take about 45 minutes. Better error logging for debugging in production would take about 15 minutes.

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
