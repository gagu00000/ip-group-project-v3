"""
Simulator Module for UAE Pulse Dashboard (FINAL - Import Safe)

Features:
- Robust column detection (works with varied schemas)
- KPI calculations (overall, by dimension, daily trends, stockout risk)
- Forward campaign simulation: simulate_campaign()
- Reverse optimizer: recommend_campaign()
  (user inputs budget + city, simulator recommends discount/margin_floor/days)

Design goals:
- No import-time side effects
- Defensive against missing columns
- Always returns results (fallback even if ROI is negative)
"""

from __future__ import annotations

import pandas as pd
import numpy as np


class Simulator:
    """Campaign simulator with KPI calculations and a recommendation optimizer."""

    def __init__(self):
        self.category_elasticity = {
            "Electronics": 2.5,
            "Fashion": 3.0,
            "Grocery": 2.0,
            "Beauty": 2.8,
            "Home": 2.2,
            "Sports": 2.6,
        }
        self.default_elasticity = 2.5

    # ------------------------------------------------------------------
    # Column helpers
    # ------------------------------------------------------------------
    def _find_column(self, df: pd.DataFrame, possible_names: list[str]) -> str | None:
        if df is None or len(getattr(df, "columns", [])) == 0:
            return None
        for name in possible_names:
            if name in df.columns:
                return name
        return None

    def _get_sku_column(self, df):
        return self._find_column(df, ["sku", "SKU", "sku_id", "SKU_ID", "product_id", "ProductID", "product_sku", "item_id"])

    def _get_cost_column(self, df):
        return self._find_column(df, ["unit_cost_aed", "cost_aed", "cost", "unit_cost", "cost_price", "purchase_price", "buying_price"])

    def _get_price_column(self, df):
        return self._find_column(df, ["selling_price_aed", "selling_price", "price", "unit_price", "sale_price", "base_price_aed"])

    def _get_qty_column(self, df):
        return self._find_column(df, ["qty", "quantity", "units", "qty_sold", "units_sold"])

    def _get_date_column(self, df):
        return self._find_column(df, ["order_ts", "order_date", "date", "timestamp", "created_at", "sale_date", "transaction_date", "order_time"])

    def _get_order_column(self, df):
        return self._find_column(df, ["order_id", "OrderID", "transaction_id", "invoice_id"])

    def _get_store_column(self, df):
        return self._find_column(df, ["store_id", "StoreID", "store", "location_id"])

    def _get_category_column(self, df):
        return self._find_column(df, ["category", "Category", "product_category", "cat"])

    def _get_city_column(self, df):
        return self._find_column(df, ["city", "City", "location", "store_city"])

    def _get_channel_column(self, df):
        return self._find_column(df, ["channel", "Channel", "sales_channel", "store_channel"])

    # ------------------------------------------------------------------
    # KPI Calculations
    # ------------------------------------------------------------------
    def calculate_overall_kpis(self, sales_df: pd.DataFrame, products_df: pd.DataFrame) -> dict:
        """Calculate overall KPIs from sales data."""
        try:
            if sales_df is None or len(sales_df) == 0:
                return {
                    "total_revenue": 0, "total_profit": 0, "total_orders": 0, "total_units": 0,
                    "avg_order_value": 0, "profit_margin_pct": 0, "return_rate_pct": 0,
                    "avg_discount_pct": 0, "refund_amount": 0, "total_cogs": 0, "net_revenue": 0, "total_discount": 0
                }

            sku_col_sales = self._get_sku_column(sales_df)
            sku_col_products = self._get_sku_column(products_df)
            cost_col = self._get_cost_column(products_df)
            price_col = self._get_price_column(sales_df)
            qty_col = self._get_qty_column(sales_df)
            order_col = self._get_order_column(sales_df)

            merged = sales_df.copy()

            # Merge product cost
            if products_df is not None and sku_col_sales and sku_col_products and cost_col:
                psub = products_df[[sku_col_products, cost_col]].copy()
                psub.columns = ["_sku", "_cost"]
                merged["_sku"] = merged[sku_col_sales]
                merged = merged.merge(psub, on="_sku", how="left")
                merged["_cost"] = merged["_cost"].fillna(0)
            else:
                merged["_cost"] = 0

            merged["_qty"] = pd.to_numeric(merged[qty_col], errors="coerce").fillna(0) if qty_col else 1
            merged["_price"] = pd.to_numeric(merged[price_col], errors="coerce").fillna(0) if price_col else 0
            merged["_cost"] = pd.to_numeric(merged["_cost"], errors="coerce").fillna(0)

            merged["revenue"] = merged["_qty"] * merged["_price"]
            merged["profit"] = merged["_qty"] * (merged["_price"] - merged["_cost"])
            merged["cogs"] = merged["_qty"] * merged["_cost"]

            total_revenue = float(merged["revenue"].sum())
            total_profit = float(merged["profit"].sum())
            total_cogs = float(merged["cogs"].sum())

            if order_col:
                total_orders = int(merged[order_col].nunique())
            else:
                total_orders = int(len(merged))

            total_units = float(merged["_qty"].sum())
            avg_order_value = total_revenue / total_orders if total_orders else 0
            margin_pct = (total_profit / total_revenue * 100) if total_revenue else 0

            # Return rate
            return_col = self._find_column(sales_df, ["return_flag", "is_returned", "returned", "is_return"])
            if return_col:
                returned = pd.to_numeric(sales_df[return_col], errors="coerce").fillna(0)
                return_rate_pct = float(returned.mean() * 100)
            else:
                return_rate_pct = 0.0

            # Refund amount (simple heuristic)
            if "payment_status" in merged.columns:
                refund_mask = merged["payment_status"].astype(str).str.lower().str.contains("refund", na=False)
                refund_amount = float(merged.loc[refund_mask, "revenue"].sum())
            else:
                refund_amount = 0.0

            net_revenue = total_revenue - refund_amount

            # Discount
            discount_col = self._find_column(merged, ["discount_pct", "discount", "discount_percent"])
            if discount_col and discount_col in merged.columns:
                merged["_discount_pct"] = pd.to_numeric(merged[discount_col], errors="coerce").fillna(0)
                avg_discount_pct = float(merged["_discount_pct"].mean())
                total_discount = float((merged["revenue"] * merged["_discount_pct"] / 100).sum())
            else:
                avg_discount_pct = 0.0
                total_discount = 0.0

            return {
                "total_revenue": total_revenue,
                "total_profit": total_profit,
                "total_orders": total_orders,
                "total_units": total_units,
                "avg_order_value": avg_order_value,
                "profit_margin_pct": margin_pct,
                "return_rate_pct": return_rate_pct,
                "avg_discount_pct": avg_discount_pct,
                "refund_amount": refund_amount,
                "total_cogs": total_cogs,
                "net_revenue": net_revenue,
                "total_discount": total_discount,
            }

        except Exception as e:
            print(f"Error in calculate_overall_kpis: {e}")
            return {
                "total_revenue": 0, "total_profit": 0, "total_orders": 0, "total_units": 0,
                "avg_order_value": 0, "profit_margin_pct": 0, "return_rate_pct": 0,
                "avg_discount_pct": 0, "refund_amount": 0, "total_cogs": 0, "net_revenue": 0, "total_discount": 0
            }

    def calculate_kpis_by_dimension(self, sales_df, stores_df, products_df, dimension: str) -> pd.DataFrame:
        """Calculate KPIs grouped by a dimension (city, channel, category)."""
        try:
            if sales_df is None or len(sales_df) == 0:
                return pd.DataFrame()

            merged = sales_df.copy()

            # Resolve columns
            sku_sales = self._get_sku_column(sales_df)
            sku_prod = self._get_sku_column(products_df)
            store_sales = self._get_store_column(sales_df)
            store_stores = self._get_store_column(stores_df)
            cost_col = self._get_cost_column(products_df)
            price_col = self._get_price_column(sales_df)
            qty_col = self._get_qty_column(sales_df)
            order_col = self._get_order_column(sales_df)
            category_col = self._get_category_column(products_df)
            city_col = self._get_city_column(stores_df)
            channel_col = self._get_channel_column(stores_df)

            # Merge stores
            if stores_df is not None and store_sales and store_stores:
                cols = [store_stores]
                if city_col:
                    cols.append(city_col)
                if channel_col:
                    cols.append(channel_col)
                ssub = stores_df[cols].copy()
                ssub.columns = ["_store"] + [f"_{c}" for c in cols[1:]]
                merged["_store"] = merged[store_sales]
                merged = merged.merge(ssub, on="_store", how="left")
                if city_col:
                    merged["city"] = merged[f"_{city_col}"]
                if channel_col:
                    merged["channel"] = merged[f"_{channel_col}"]

            # Merge products
            if products_df is not None and sku_sales and sku_prod:
                cols = [sku_prod]
                if cost_col:
                    cols.append(cost_col)
                if category_col:
                    cols.append(category_col)
                psub = products_df[cols].copy()
                new_cols = ["_sku"]
                if cost_col:
                    new_cols.append("_cost")
                if category_col:
                    new_cols.append("category")
                psub.columns = new_cols
                merged["_sku"] = merged[sku_sales]
                merged = merged.merge(psub, on="_sku", how="left")

            if "_cost" not in merged.columns:
                merged["_cost"] = 0
            if "category" not in merged.columns:
                merged["category"] = "Unknown"
            if "city" not in merged.columns:
                merged["city"] = "Unknown"
            if "channel" not in merged.columns:
                merged["channel"] = "Unknown"

            merged["_qty"] = pd.to_numeric(merged[qty_col], errors="coerce").fillna(0) if qty_col else 1
            merged["_price"] = pd.to_numeric(merged[price_col], errors="coerce").fillna(0) if price_col else 0
            merged["_cost"] = pd.to_numeric(merged["_cost"], errors="coerce").fillna(0)

            merged["revenue"] = merged["_qty"] * merged["_price"]
            merged["profit"] = merged["_qty"] * (merged["_price"] - merged["_cost"])

            merged["_order_id"] = merged[order_col] if (order_col and order_col in merged.columns) else range(len(merged))

            grouped = merged.groupby(dimension).agg(
                revenue=("revenue", "sum"),
                profit=("profit", "sum"),
                orders=("_order_id", "nunique"),
                units=("_qty", "sum"),
            ).reset_index()

            grouped["avg_order_value"] = grouped["revenue"] / grouped["orders"]
            grouped["profit_margin_pct"] = (grouped["profit"] / grouped["revenue"] * 100).replace([np.inf, -np.inf], np.nan).fillna(0)

            return grouped.sort_values("revenue", ascending=False)

        except Exception as e:
            print(f"Error in calculate_kpis_by_dimension: {e}")
            return pd.DataFrame()

    def calculate_daily_trends(self, sales_df, products_df) -> pd.DataFrame:
        """Calculate daily performance trends."""
        try:
            if sales_df is None or len(sales_df) == 0:
                return pd.DataFrame(columns=["date", "revenue", "profit", "orders", "units"])

            merged = sales_df.copy()

            sku_sales = self._get_sku_column(sales_df)
            sku_prod = self._get_sku_column(products_df)
            cost_col = self._get_cost_column(products_df)
            price_col = self._get_price_column(sales_df)
            qty_col = self._get_qty_column(sales_df)
            date_col = self._get_date_column(sales_df)
            order_col = self._get_order_column(sales_df)

            if products_df is not None and sku_sales and sku_prod and cost_col:
                psub = products_df[[sku_prod, cost_col]].copy()
                psub.columns = ["_sku", "_cost"]
                merged["_sku"] = merged[sku_sales]
                merged = merged.merge(psub, on="_sku", how="left")
                merged["_cost"] = merged["_cost"].fillna(0)
            else:
                merged["_cost"] = 0

            merged["_qty"] = pd.to_numeric(merged[qty_col], errors="coerce").fillna(0) if qty_col else 1
            merged["_price"] = pd.to_numeric(merged[price_col], errors="coerce").fillna(0) if price_col else 0
            merged["_cost"] = pd.to_numeric(merged["_cost"], errors="coerce").fillna(0)

            merged["revenue"] = merged["_qty"] * merged["_price"]
            merged["profit"] = merged["_qty"] * (merged["_price"] - merged["_cost"])

            if date_col:
                merged["date"] = pd.to_datetime(merged[date_col], errors="coerce").dt.date
            else:
                merged["date"] = pd.date_range(end=pd.Timestamp.today(), periods=len(merged), freq="h").date

            merged = merged.dropna(subset=["date"])
            if len(merged) == 0:
                return pd.DataFrame(columns=["date", "revenue", "profit", "orders", "units"])

            daily = merged.groupby("date").agg(
                revenue=("revenue", "sum"),
                profit=("profit", "sum"),
                units=("_qty", "sum"),
            ).reset_index()

            if order_col and order_col in merged.columns:
                orders = merged.groupby("date")[order_col].nunique().reset_index()
                orders.columns = ["date", "orders"]
                daily = daily.merge(orders, on="date", how="left")
            else:
                daily["orders"] = daily["units"]

            return daily.sort_values("date")

        except Exception as e:
            print(f"Error in calculate_daily_trends: {e}")
            return pd.DataFrame(columns=["date", "revenue", "profit", "orders", "units"])

    def calculate_stockout_risk(self, inventory_df) -> dict:
        """Calculate stockout risk metrics."""
        try:
            if inventory_df is None or len(inventory_df) == 0:
                return {"total_items": 0, "zero_stock": 0, "low_stock": 0, "stockout_risk_pct": 0}

            stock_col = self._find_column(inventory_df, ["stock_on_hand", "stock", "quantity", "qty", "inventory"])
            reorder_col = self._find_column(inventory_df, ["reorder_point", "reorder_level", "min_stock"])

            df = inventory_df.copy()
            df["_stock"] = pd.to_numeric(df[stock_col], errors="coerce").fillna(0) if stock_col else 0
            df["_reorder"] = pd.to_numeric(df[reorder_col], errors="coerce").fillna(10) if reorder_col else 10

            total_items = int(len(df))
            zero_stock = int((df["_stock"] == 0).sum())
            low_stock = int((df["_stock"] <= df["_reorder"]).sum())

            return {
                "total_items": total_items,
                "zero_stock": zero_stock,
                "low_stock": low_stock,
                "stockout_risk_pct": (low_stock / total_items * 100) if total_items else 0,
            }

        except Exception as e:
            print(f"Error in calculate_stockout_risk: {e}")
            return {"total_items": 0, "zero_stock": 0, "low_stock": 0, "stockout_risk_pct": 0}

    # ------------------------------------------------------------------
    # Forward Simulation
    # ------------------------------------------------------------------
    def simulate_campaign(
        self,
        sales_df,
        stores_df,
        products_df,
        discount_pct=10,
        promo_budget=10000,
        margin_floor=15,
        city="All",
        channel="All",
        category="All",
        campaign_days=7,
        data_days=30,
    ) -> dict:
        """
        Forward simulation:
        Inputs: discount, margin floor, days, budget, targeting
        Output: expected KPIs + ROI
        """
        try:
            if sales_df is None or len(sales_df) == 0:
                return {"outputs": None, "comparison": None, "warnings": ["No sales data provided"]}

            merged = sales_df.copy()

            # --- Merge stores for city/channel filtering ---
            store_sales = self._get_store_column(sales_df)
            store_stores = self._get_store_column(stores_df) if stores_df is not None else None
            city_col = self._get_city_column(stores_df) if stores_df is not None else None
            channel_col = self._get_channel_column(stores_df) if stores_df is not None else None

            if stores_df is not None and store_sales and store_stores:
                cols = [store_stores]
                if city_col:
                    cols.append(city_col)
                if channel_col:
                    cols.append(channel_col)
                ssub = stores_df[cols].copy()
                ssub.columns = ["_store"] + cols[1:]
                merged["_store"] = merged[store_sales]
                merged = merged.merge(ssub, on="_store", how="left")

            # --- Merge products for cost + category filtering ---
            sku_sales = self._get_sku_column(sales_df)
            sku_prod = self._get_sku_column(products_df) if products_df is not None else None
            cost_col = self._get_cost_column(products_df) if products_df is not None else None
            cat_col = self._get_category_column(products_df) if products_df is not None else None

            if products_df is not None and sku_sales and sku_prod:
                cols = [sku_prod]
                if cost_col:
                    cols.append(cost_col)
                if cat_col:
                    cols.append(cat_col)
                psub = products_df[cols].copy()
                new_cols = ["_sku"]
                if cost_col:
                    new_cols.append("_cost")
                if cat_col:
                    new_cols.append("category")
                psub.columns = new_cols
                merged["_sku"] = merged[sku_sales]
                merged = merged.merge(psub, on="_sku", how="left")

            if "_cost" not in merged.columns:
                merged["_cost"] = 0
            if "category" not in merged.columns:
                merged["category"] = "Unknown"

            # --- Core numeric columns ---
            price_col = self._get_price_column(merged)
            qty_col = self._get_qty_column(merged)
            order_col = self._get_order_column(merged)

            merged["_qty"] = pd.to_numeric(merged[qty_col], errors="coerce").fillna(0) if qty_col else 1
            merged["_price"] = pd.to_numeric(merged[price_col], errors="coerce").fillna(0) if price_col else 0
            merged["_cost"] = pd.to_numeric(merged["_cost"], errors="coerce").fillna(0)

            # --- Apply targeting filters ---
            if city != "All" and city_col and city_col in merged.columns:
                merged = merged[merged[city_col] == city]
            if channel != "All" and channel_col and channel_col in merged.columns:
                merged = merged[merged[channel_col] == channel]
            if category != "All" and "category" in merged.columns:
                merged = merged[merged["category"] == category]

            if len(merged) == 0:
                return {"outputs": None, "comparison": None, "warnings": ["No data matches filters"]}

            merged["revenue"] = merged["_qty"] * merged["_price"]
            merged["profit"] = merged["_qty"] * (merged["_price"] - merged["_cost"])

            # --- Baseline scaling ---
            data_days = max(1, int(data_days))
            campaign_days = max(1, int(campaign_days))

            baseline_revenue = merged["revenue"].sum() / data_days * campaign_days
            baseline_profit = merged["profit"].sum() / data_days * campaign_days
            baseline_units = merged["_qty"].sum() / data_days * campaign_days

            if order_col and order_col in merged.columns:
                baseline_orders = merged[order_col].nunique() / data_days * campaign_days
            else:
                baseline_orders = len(merged) / data_days * campaign_days

            # --- Elasticity + lift ---
            elasticity = self.category_elasticity.get(category, self.default_elasticity) if category != "All" else self.default_elasticity
            demand_lift_pct = float(np.clip(float(discount_pct) * float(elasticity), -50, 400))
            expected_units = baseline_units * (1 + demand_lift_pct / 100)

            avg_price = float(merged["_price"].mean()) if len(merged) else 0.0
            avg_cost = float(merged["_cost"].mean()) if len(merged) else 0.0

            # --- Margin floor enforcement (cap discount if needed) ---
            base_margin_pct = ((avg_price - avg_cost) / avg_price * 100) if avg_price > 0 else 0.0

            effective_discount = float(discount_pct)
            discounted_price = avg_price * (1 - effective_discount / 100)
            expected_margin_pct = ((discounted_price - avg_cost) / discounted_price * 100) if discounted_price > 0 else 0.0

            margin_capped = False
            if expected_margin_pct < margin_floor and base_margin_pct > margin_floor and avg_price > 0:
                min_price = avg_cost / (1 - margin_floor / 100) if margin_floor < 100 else avg_cost
                max_discount = ((avg_price - min_price) / avg_price * 100) if avg_price > 0 else 0
                max_discount = float(np.clip(max_discount, 0, 95))
                effective_discount = min(float(discount_pct), max_discount)
                margin_capped = True

                demand_lift_pct = float(np.clip(effective_discount * elasticity, -50, 400))
                expected_units = baseline_units * (1 + demand_lift_pct / 100)

                discounted_price = avg_price * (1 - effective_discount / 100)
                expected_margin_pct = ((discounted_price - avg_cost) / discounted_price * 100) if discounted_price > 0 else 0.0

            # --- Revenue/Profit ---
            expected_revenue = expected_units * discounted_price
            cogs = expected_units * avg_cost
            expected_gross_profit = expected_revenue - cogs

            # Promo cost model (budget-limited, plus 5% of revenue safety cap)
            promo_cost = min(float(promo_budget), float(expected_revenue) * 0.05)

            # Fulfillment cost on incremental units
            incremental_units = max(0.0, expected_units - baseline_units)
            fulfillment_cost = incremental_units * 1.5

            expected_net_profit = expected_gross_profit - promo_cost - fulfillment_cost

            # ROI
            total_investment = promo_cost + fulfillment_cost
            incremental_profit = expected_net_profit - baseline_profit

            if total_investment > 0:
                roi_pct = incremental_profit / total_investment * 100
            else:
                roi_pct = 0 if incremental_profit <= 0 else 100
            roi_pct = float(np.clip(roi_pct, -100, 500))

            # Warnings
            warnings = []
            if margin_capped:
                warnings.append(f"Discount capped to {effective_discount:.1f}% to maintain {margin_floor}% margin floor")
            if expected_margin_pct < margin_floor:
                warnings.append(f"Margin ({expected_margin_pct:.1f}%) below floor ({margin_floor}%)")
            if roi_pct < 0:
                warnings.append(f"Negative ROI ({roi_pct:.1f}%)")

            outputs = {
                "expected_revenue": float(expected_revenue),
                "expected_orders": int(baseline_orders * (1 + demand_lift_pct / 100)),
                "expected_units": float(expected_units),
                "expected_net_profit": float(expected_net_profit),
                "expected_margin_pct": float(expected_margin_pct),
                "demand_lift_pct": float(demand_lift_pct),
                "roi_pct": float(roi_pct),
                "promo_cost": float(promo_cost),
                "fulfillment_cost": float(fulfillment_cost),
                "discount_pct_effective": float(effective_discount),
            }

            comparison = {
                "baseline_revenue": float(baseline_revenue),
                "baseline_profit": float(baseline_profit),
                "baseline_orders": int(baseline_orders),
                "revenue_change_pct": ((expected_revenue - baseline_revenue) / baseline_revenue * 100) if baseline_revenue > 0 else 0,
                "profit_change_pct": ((expected_net_profit - baseline_profit) / abs(baseline_profit) * 100) if baseline_profit != 0 else 0,
            }

            return {"outputs": outputs, "comparison": comparison, "warnings": warnings}

        except Exception as e:
            print(f"Error in simulate_campaign: {e}")
            return {"outputs": None, "comparison": None, "warnings": [f"Error: {str(e)}"]}

    # ------------------------------------------------------------------
    # Reverse Optimizer (your requested logic)
    # ------------------------------------------------------------------
    def recommend_campaign(
        self,
        sales_df,
        stores_df,
        products_df,
        promo_budget,
        city="All",
        channel="All",
        category="All",
        discount_grid=(5, 10, 15, 20, 25, 30, 35),
        margin_floor_grid=(5, 10, 15, 20),
        days_grid=(3, 5, 7, 10, 14),
        data_days=30,
        objective="roi",  # "roi" or "net_profit"
        require_positive_roi=True,
    ) -> dict:
        """
        Reverse simulator:
        Inputs: budget + targeting
        Output: best discount/margin_floor/days

        Two-pass logic:
        - Pass 1: require positive ROI (if enabled)
        - Pass 2: fallback to best available even if ROI <= 0
        """

        def run(require_positive: bool):
            candidates = []
            best = None

            for d in discount_grid:
                for mf in margin_floor_grid:
                    for days in days_grid:
                        res = self.simulate_campaign(
                            sales_df=sales_df,
                            stores_df=stores_df,
                            products_df=products_df,
                            discount_pct=d,
                            promo_budget=promo_budget,
                            margin_floor=mf,
                            city=city,
                            channel=channel,
                            category=category,
                            campaign_days=days,
                            data_days=data_days,
                        )

                        out = res.get("outputs")
                        comp = res.get("comparison")
                        if not out or not comp:
                            continue

                        roi = float(out.get("roi_pct", -999))
                        net_profit = float(out.get("expected_net_profit", -1e18))

                        if require_positive and roi <= 0:
                            continue

                        score = roi if objective == "roi" else net_profit

                        row = {
                            "discount_pct": float(d),
                            "margin_floor": float(mf),
                            "campaign_days": int(days),
                            "discount_effective": float(out.get("discount_pct_effective", d)),
                            "expected_revenue": float(out.get("expected_revenue", 0)),
                            "expected_net_profit": float(net_profit),
                            "expected_margin_pct": float(out.get("expected_margin_pct", 0)),
                            "roi_pct": float(roi),
                            "baseline_revenue": float(comp.get("baseline_revenue", 0)),
                            "baseline_profit": float(comp.get("baseline_profit", 0)),
                            "score": float(score),
                            "warnings": res.get("warnings", []),
                        }
                        candidates.append(row)

                        if best is None or row["score"] > best["score"]:
                            best = row

            df = pd.DataFrame(candidates)
            if len(df) > 0:
                df = df.sort_values("score", ascending=False)

            return best, df

        # Pass 1
        best, df = run(require_positive=require_positive_roi)
        if best is not None:
            return {"best": best, "candidates": df, "warnings": best.get("warnings", [])}

        # Pass 2 fallback
        best2, df2 = run(require_positive=False)
        if best2 is None:
            return {
                "best": None,
                "candidates": df2,
                "warnings": ["No valid simulation results. Filters may remove all rows or required columns are missing."],
            }

        warnings = ["No positive ROI found. Showing best available (may still be negative)."] + best2.get("warnings", [])
        return {"best": best2, "candidates": df2, "warnings": warnings}
