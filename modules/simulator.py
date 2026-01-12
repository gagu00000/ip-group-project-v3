"""
Simulator Module for UAE Pulse Dashboard (FINAL v3 - ROI Debug + Better Cost Model)

Key improvements:
- Auto-detect baseline window length (data_days) from sales date column if present
- Less aggressive promo cost model (prevents ROI always being clipped to -100)
- Adds debug fields in outputs so user can diagnose baseline and ROI drivers
- Keeps app compatibility: outputs/comparison/warnings keys remain
- Includes recommend_campaign() with fallback (best available even if ROI negative)
"""

from __future__ import annotations
import pandas as pd
import numpy as np


class Simulator:
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

    # ---------------- Column helpers ----------------
    def _find_column(self, df: pd.DataFrame, possible_names: list[str]) -> str | None:
        if df is None or not hasattr(df, "columns"):
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
        return self._find_column(df, ["order_time", "order_ts", "order_date", "date", "timestamp", "created_at", "sale_date", "transaction_date"])

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

    # ---------------- Internal: auto baseline days ----------------
    def _infer_data_days(self, sales_df: pd.DataFrame, fallback: int = 30) -> int:
        """Infer number of days covered by sales_df using its date column."""
        try:
            date_col = self._get_date_column(sales_df)
            if not date_col:
                return int(max(1, fallback))
            s = pd.to_datetime(sales_df[date_col], errors="coerce").dropna()
            if len(s) == 0:
                return int(max(1, fallback))
            days = int((s.max() - s.min()).days + 1)
            return int(max(1, days))
        except Exception:
            return int(max(1, fallback))

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
        data_days=30,  # used only if we cannot infer from dates
    ) -> dict:
        """
        Forward simulation: given discount/margin/days/budget -> expected results.

        Important changes vs earlier versions:
        - data_days auto-inferred from sales date column when available
        - promo_cost model is softer to avoid universally negative ROI
        """
        try:
            if sales_df is None or len(sales_df) == 0:
                return {"outputs": None, "comparison": None, "warnings": ["No sales data provided"]}

            # Infer baseline window from data if possible
            inferred_days = self._infer_data_days(sales_df, fallback=data_days)
            data_days = int(max(1, inferred_days))
            campaign_days = int(max(1, campaign_days))

            merged = sales_df.copy()

            # --- Merge stores to get city/channel for filtering ---
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

            # --- Merge products for cost + category ---
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
                merged["_cost"] = np.nan
            if "category" not in merged.columns:
                merged["category"] = "Unknown"

            # --- Numeric columns ---
            price_col = self._get_price_column(merged)
            qty_col = self._get_qty_column(merged)
            order_col = self._get_order_column(merged)

            merged["_qty"] = pd.to_numeric(merged[qty_col], errors="coerce").fillna(0) if qty_col else 1
            merged["_price"] = pd.to_numeric(merged[price_col], errors="coerce").fillna(0) if price_col else 0
            merged["_cost"] = pd.to_numeric(merged["_cost"], errors="coerce")

            # Cost missing diagnostics
            cost_missing_pct = float(merged["_cost"].isna().mean() * 100) if "_cost" in merged.columns else 100.0
            merged["_cost"] = merged["_cost"].fillna(0)

            # --- Apply targeting filters ---
            if city != "All" and city_col and city_col in merged.columns:
                merged = merged[merged[city_col] == city]
            if channel != "All" and channel_col and channel_col in merged.columns:
                merged = merged[merged[channel_col] == channel]
            if category != "All" and "category" in merged.columns:
                merged = merged[merged["category"] == category]

            if len(merged) == 0:
                return {"outputs": None, "comparison": None, "warnings": ["No data matches filters"]}

            # --- Compute baseline revenue/profit from data ---
            merged["revenue"] = merged["_qty"] * merged["_price"]
            merged["profit"] = merged["_qty"] * (merged["_price"] - merged["_cost"])

            baseline_revenue = merged["revenue"].sum() / data_days * campaign_days
            baseline_profit = merged["profit"].sum() / data_days * campaign_days
            baseline_units = merged["_qty"].sum() / data_days * campaign_days
            baseline_orders = (merged[order_col].nunique() / data_days * campaign_days) if (order_col and order_col in merged.columns) else (len(merged) / data_days * campaign_days)

            # --- Elasticity ---
            elasticity = self.category_elasticity.get(category, self.default_elasticity) if category != "All" else self.default_elasticity

            # --- Demand lift ---
            demand_lift_pct = float(np.clip(float(discount_pct) * float(elasticity), -50, 400))
            expected_units = baseline_units * (1 + demand_lift_pct / 100)

            avg_price = float(merged["_price"].mean()) if len(merged) else 0.0
            avg_cost = float(merged["_cost"].mean()) if len(merged) else 0.0

            # --- Margin floor enforcement ---
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

            # --- Financials ---
            expected_revenue = expected_units * discounted_price
            cogs = expected_units * avg_cost
            expected_gross_profit = expected_revenue - cogs

            # PROMO COST MODEL (UPDATED):
            # - scale spend by campaign length (short campaigns don't spend full budget)
            # - cap promo spend at 1% of revenue (instead of 5%) to prevent universal negative ROI
            budget_scaled = float(promo_budget) * (campaign_days / 30.0)
            promo_cost = min(budget_scaled, float(expected_revenue) * 0.01)

            incremental_units = max(0.0, expected_units - baseline_units)
            fulfillment_cost = incremental_units * 1.5

            expected_net_profit = expected_gross_profit - promo_cost - fulfillment_cost

            # ROI (no hard clamp while debugging; you can clamp later in UI)
            total_investment = promo_cost + fulfillment_cost
            incremental_profit = expected_net_profit - baseline_profit

            if total_investment > 0:
                roi_pct = incremental_profit / total_investment * 100
            else:
                roi_pct = 0 if incremental_profit <= 0 else 100

            warnings = []
            if cost_missing_pct > 20:
                warnings.append(f"Cost missing for {cost_missing_pct:.1f}% of rows (products↔sales SKU mapping may be weak).")
            if margin_capped:
                warnings.append(f"Discount capped to {effective_discount:.1f}% to maintain {margin_floor}% margin floor")
            if expected_margin_pct < margin_floor:
                warnings.append(f"Margin ({expected_margin_pct:.1f}%) below floor ({margin_floor}%)")
            if roi_pct < 0:
                warnings.append(f"Negative ROI ({roi_pct:.1f}%)")

            outputs = {
                # main outputs
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

                # debug outputs (so you can tell me what's wrong)
                "baseline_revenue_used": float(baseline_revenue),
                "baseline_profit_used": float(baseline_profit),
                "incremental_profit": float(incremental_profit),
                "total_investment": float(total_investment),
                "avg_price": float(avg_price),
                "avg_cost": float(avg_cost),
                "base_margin_pct": float(base_margin_pct),
                "data_days_inferred": int(data_days),
                "cost_missing_pct": float(cost_missing_pct),
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
    # Reverse Optimizer
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
        Two-pass optimizer:
        - pass1: require positive ROI (if enabled)
        - pass2: fallback to best available even if ROI is negative
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
                        score = roi if objective == "roi" else net_profit

                        if require_positive and roi <= 0:
                            continue

                        row = {
                            "discount_pct": float(d),
                            "margin_floor": float(mf),
                            "campaign_days": int(days),
                            "discount_effective": float(out.get("discount_pct_effective", d)),
                            "expected_revenue": float(out.get("expected_revenue", 0)),
                            "expected_net_profit": float(net_profit),
                            "expected_margin_pct": float(out.get("expected_margin_pct", 0)),
                            "roi_pct": float(roi),
                            "promo_cost": float(out.get("promo_cost", 0)),
                            "baseline_revenue": float(comp.get("baseline_revenue", 0)),
                            "baseline_profit": float(comp.get("baseline_profit", 0)),
                            "data_days_inferred": int(out.get("data_days_inferred", data_days)),
                            "cost_missing_pct": float(out.get("cost_missing_pct", 0)),
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

        # Pass 1: positive ROI only
        best, df = run(require_positive=require_positive_roi)
        if best is not None:
            return {"best": best, "candidates": df, "warnings": best.get("warnings", [])}

        # Pass 2: fallback
        best2, df2 = run(require_positive=False)
        if best2 is None:
            return {
                "best": None,
                "candidates": df2,
                "warnings": ["No valid simulation results. Filters may remove all rows or required columns are missing."],
            }

        warnings = ["No positive ROI found. Showing best available (may still be negative)."] + best2.get("warnings", [])
        return {"best": best2, "candidates": df2, "warnings": warnings}
