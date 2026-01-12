"""
Simulator Module for UAE Pulse Dashboard (REVAMPED)
Campaign simulation and KPI calculations

Revamp focus:
- More "what-if simulator" logic similar to user's other project:
  category -> brand -> sku selection (optional)
  city/channel scope targeting
  scenario object returned
- Budget + margin floor constraints enforced
- Output structure remains compatible with app: {outputs, comparison, warnings}
"""

import pandas as pd
import numpy as np


class Simulator:
    """Campaign simulator with KPI calculations."""

    def __init__(self):
        """Initialize simulator with default elasticity values."""
        self.category_elasticity = {
            'Electronics': 2.5,
            'Fashion': 3.0,
            'Grocery': 2.0,
            'Beauty': 2.8,
            'Home': 2.2,
            'Sports': 2.6
        }
        self.default_elasticity = 2.5

        # Optional: brand/audience/promo-type multipliers (kept neutral by default)
        self.promo_type_multiplier = {
            "Percentage Off": 1.00,
            "BOGO": 1.10,
            "Bundle Deal": 1.05,
            "Flash Sale": 1.15,
            "Clearance": 1.20,
            "Member Exclusive": 0.95,
        }

    # ---------------------------------------------------------------------
    # Column finders (keep your robust behavior)
    # ---------------------------------------------------------------------
    def _find_column(self, df, possible_names):
        for name in possible_names:
            if name in df.columns:
                return name
        return None

    def _get_sku_column(self, df):
        return self._find_column(df, ['sku', 'SKU', 'sku_id', 'SKU_ID', 'product_id', 'ProductID', 'product_sku', 'item_id'])

    def _get_cost_column(self, df):
        return self._find_column(df, ['unit_cost_aed', 'cost_aed', 'cost', 'unit_cost', 'cost_price', 'purchase_price', 'buying_price'])

    def _get_price_column(self, df):
        return self._find_column(df, ['selling_price_aed', 'selling_price', 'price', 'unit_price', 'sale_price', 'base_price_aed'])

    def _get_qty_column(self, df):
        return self._find_column(df, ['qty', 'quantity', 'units', 'qty_sold', 'units_sold'])

    def _get_date_column(self, df):
        return self._find_column(df, ['order_ts', 'order_date', 'date', 'timestamp', 'created_at', 'sale_date', 'transaction_date', 'order_time'])

    def _get_order_column(self, df):
        return self._find_column(df, ['order_id', 'OrderID', 'transaction_id', 'invoice_id'])

    def _get_store_column(self, df):
        return self._find_column(df, ['store_id', 'StoreID', 'store', 'location_id'])

    def _get_category_column(self, df):
        return self._find_column(df, ['category', 'Category', 'product_category', 'cat'])

    def _get_city_column(self, df):
        return self._find_column(df, ['city', 'City', 'location', 'store_city'])

    def _get_channel_column(self, df):
        return self._find_column(df, ['channel', 'Channel', 'sales_channel', 'store_channel'])

    def _get_brand_column(self, df):
        return self._find_column(df, ['brand', 'Brand', 'brand_name'])

    # ---------------------------------------------------------------------
    # Existing KPI methods (kept as-is from your original, with tiny safety)
    # ---------------------------------------------------------------------
    def calculate_overall_kpis(self, sales_df, products_df):
        kpis = {}
        try:
            sku_col_sales = self._get_sku_column(sales_df)
            sku_col_products = self._get_sku_column(products_df)
            cost_col = self._get_cost_column(products_df)
            price_col = self._get_price_column(sales_df)
            qty_col = self._get_qty_column(sales_df)
            order_col = self._get_order_column(sales_df)

            merged = sales_df.copy()

            if sku_col_sales and sku_col_products and cost_col:
                products_subset = products_df[[sku_col_products, cost_col]].copy()
                products_subset.columns = ['_sku', '_cost']
                merged['_sku'] = merged[sku_col_sales]
                merged = merged.merge(products_subset, on='_sku', how='left')
                merged['_cost'] = merged['_cost'].fillna(0)
            else:
                merged['_cost'] = 0

            merged['_qty'] = pd.to_numeric(merged[qty_col], errors='coerce').fillna(0) if qty_col else 1
            merged['_price'] = pd.to_numeric(merged[price_col], errors='coerce').fillna(0) if price_col else 0
            merged['_cost'] = pd.to_numeric(merged['_cost'], errors='coerce').fillna(0)

            merged['revenue'] = merged['_qty'] * merged['_price']
            merged['profit'] = merged['_qty'] * (merged['_price'] - merged['_cost'])

            kpis['total_revenue'] = float(merged['revenue'].sum())
            kpis['total_profit'] = float(merged['profit'].sum())

            if order_col:
                kpis['total_orders'] = int(merged[order_col].nunique())
            else:
                kpis['total_orders'] = int(len(merged))

            kpis['total_units'] = float(merged['_qty'].sum())
            kpis['avg_order_value'] = kpis['total_revenue'] / kpis['total_orders'] if kpis['total_orders'] > 0 else 0
            kpis['profit_margin_pct'] = (kpis['total_profit'] / kpis['total_revenue'] * 100) if kpis['total_revenue'] > 0 else 0

            return_col = self._find_column(sales_df, ['return_flag', 'is_returned', 'returned', 'is_return'])
            if return_col:
                returned = pd.to_numeric(sales_df[return_col], errors='coerce').fillna(0)
                kpis['return_rate_pct'] = float(returned.mean() * 100)
            else:
                kpis['return_rate_pct'] = 0

            if 'payment_status' in merged.columns:
                refund_mask = merged['payment_status'].astype(str).str.lower().str.contains('refund', na=False)
                kpis['refund_amount'] = float(merged.loc[refund_mask, 'revenue'].sum())
            else:
                kpis['refund_amount'] = 0

            merged['cogs'] = merged['_qty'] * merged['_cost']
            kpis['total_cogs'] = float(merged['cogs'].sum())
            kpis['net_revenue'] = kpis['total_revenue'] - kpis['refund_amount']

            discount_col = self._find_column(merged, ['discount_pct', 'discount', 'discount_percent'])
            if discount_col and discount_col in merged.columns:
                merged['_discount_pct'] = pd.to_numeric(merged[discount_col], errors='coerce').fillna(0)
                kpis['avg_discount_pct'] = float(merged['_discount_pct'].mean())
                kpis['total_discount'] = float((merged['revenue'] * merged['_discount_pct'] / 100).sum())
            else:
                kpis['avg_discount_pct'] = 0
                kpis['total_discount'] = 0

        except Exception as e:
            print(f"Error in calculate_overall_kpis: {e}")
            kpis = {
                'total_revenue': 0,
                'total_profit': 0,
                'total_orders': 0,
                'total_units': 0,
                'avg_order_value': 0,
                'profit_margin_pct': 0,
                'return_rate_pct': 0,
                'avg_discount_pct': 0,
                'refund_amount': 0,
                'total_cogs': 0,
                'net_revenue': 0,
                'total_discount': 0
            }

        return kpis

    def calculate_kpis_by_dimension(self, sales_df, stores_df, products_df, dimension):
        try:
            merged = sales_df.copy()

            sku_col_sales = self._get_sku_column(sales_df)
            sku_col_products = self._get_sku_column(products_df)
            store_col_sales = self._get_store_column(sales_df)
            store_col_stores = self._get_store_column(stores_df)
            cost_col = self._get_cost_column(products_df)
            price_col = self._get_price_column(sales_df)
            qty_col = self._get_qty_column(sales_df)
            order_col = self._get_order_column(sales_df)
            category_col = self._get_category_column(products_df)
            city_col = self._get_city_column(stores_df)
            channel_col = self._get_channel_column(stores_df)

            if store_col_sales and store_col_stores:
                stores_cols = [store_col_stores]
                if city_col:
                    stores_cols.append(city_col)
                if channel_col:
                    stores_cols.append(channel_col)

                stores_subset = stores_df[stores_cols].copy()
                stores_subset.columns = ['_store'] + [f'_{c}' for c in stores_cols[1:]]
                merged['_store'] = merged[store_col_sales]
                merged = merged.merge(stores_subset, on='_store', how='left')

                if city_col:
                    merged['city'] = merged[f'_{city_col}']
                if channel_col:
                    merged['channel'] = merged[f'_{channel_col}']

            if sku_col_sales and sku_col_products:
                products_cols = [sku_col_products]
                if cost_col:
                    products_cols.append(cost_col)
                if category_col:
                    products_cols.append(category_col)

                products_subset = products_df[products_cols].copy()
                new_cols = ['_sku']
                if cost_col:
                    new_cols.append('_cost')
                if category_col:
                    new_cols.append('category')
                products_subset.columns = new_cols

                merged['_sku'] = merged[sku_col_sales]
                merged = merged.merge(products_subset, on='_sku', how='left')

            if '_cost' not in merged.columns:
                merged['_cost'] = 0
            if 'category' not in merged.columns:
                merged['category'] = 'Unknown'
            if 'city' not in merged.columns:
                merged['city'] = 'Unknown'
            if 'channel' not in merged.columns:
                merged['channel'] = 'Unknown'

            merged['_qty'] = pd.to_numeric(merged[qty_col], errors='coerce').fillna(0) if qty_col else 1
            merged['_price'] = pd.to_numeric(merged[price_col], errors='coerce').fillna(0) if price_col else 0
            merged['_cost'] = pd.to_numeric(merged['_cost'], errors='coerce').fillna(0)

            merged['revenue'] = merged['_qty'] * merged['_price']
            merged['profit'] = merged['_qty'] * (merged['_price'] - merged['_cost'])

            merged['_order_id'] = merged[order_col] if order_col else range(len(merged))

            grouped = merged.groupby(dimension).agg({
                'revenue': 'sum',
                'profit': 'sum',
                '_order_id': 'nunique',
                '_qty': 'sum'
            }).reset_index()

            grouped.columns = [dimension, 'revenue', 'profit', 'orders', 'units']
            grouped['avg_order_value'] = grouped['revenue'] / grouped['orders']
            grouped['profit_margin_pct'] = (grouped['profit'] / grouped['revenue'] * 100).fillna(0)
            grouped = grouped.sort_values('revenue', ascending=False)

            return grouped

        except Exception as e:
            print(f"Error in calculate_kpis_by_dimension: {e}")
            return pd.DataFrame()

    def calculate_daily_trends(self, sales_df, products_df):
        try:
            merged = sales_df.copy()

            sku_col_sales = self._get_sku_column(sales_df)
            sku_col_products = self._get_sku_column(products_df)
            cost_col = self._get_cost_column(products_df)
            price_col = self._get_price_column(sales_df)
            qty_col = self._get_qty_column(sales_df)
            date_col = self._get_date_column(sales_df)
            order_col = self._get_order_column(sales_df)

            if sku_col_sales and sku_col_products and cost_col:
                products_subset = products_df[[sku_col_products, cost_col]].copy()
                products_subset.columns = ['_sku', '_cost']
                merged['_sku'] = merged[sku_col_sales]
                merged = merged.merge(products_subset, on='_sku', how='left')
                merged['_cost'] = merged['_cost'].fillna(0)
            else:
                merged['_cost'] = 0

            merged['_qty'] = pd.to_numeric(merged[qty_col], errors='coerce').fillna(0) if qty_col else 1
            merged['_price'] = pd.to_numeric(merged[price_col], errors='coerce').fillna(0) if price_col else 0
            merged['_cost'] = pd.to_numeric(merged['_cost'], errors='coerce').fillna(0)

            merged['revenue'] = merged['_qty'] * merged['_price']
            merged['profit'] = merged['_qty'] * (merged['_price'] - merged['_cost'])

            if date_col:
                merged['date'] = pd.to_datetime(merged[date_col], errors='coerce').dt.date
            else:
                merged['date'] = pd.date_range(end=pd.Timestamp.today(), periods=len(merged), freq='h').date

            merged = merged.dropna(subset=['date'])
            if len(merged) == 0:
                return pd.DataFrame(columns=['date', 'revenue', 'profit', 'orders', 'units'])

            daily = merged.groupby('date').agg({
                'revenue': 'sum',
                'profit': 'sum',
                '_qty': 'sum'
            }).reset_index()

            if order_col:
                orders_per_day = merged.groupby('date')[order_col].nunique().reset_index()
                orders_per_day.columns = ['date', 'orders']
                daily = daily.merge(orders_per_day, on='date', how='left')
                daily.columns = ['date', 'revenue', 'profit', 'units', 'orders']
            else:
                daily['orders'] = daily['_qty']
                daily.columns = ['date', 'revenue', 'profit', 'units', 'orders']

            daily = daily.sort_values('date')
            return daily

        except Exception as e:
            print(f"Error in calculate_daily_trends: {e}")
            return pd.DataFrame(columns=['date', 'revenue', 'profit', 'orders', 'units'])

    def calculate_stockout_risk(self, inventory_df):
        try:
            stock_col = self._find_column(inventory_df, ['stock_on_hand', 'stock', 'quantity', 'qty', 'inventory'])
            reorder_col = self._find_column(inventory_df, ['reorder_point', 'reorder_level', 'min_stock'])

            if stock_col:
                inventory_df['_stock'] = pd.to_numeric(inventory_df[stock_col], errors='coerce').fillna(0)
            else:
                inventory_df['_stock'] = 0

            if reorder_col:
                inventory_df['_reorder'] = pd.to_numeric(inventory_df[reorder_col], errors='coerce').fillna(10)
            else:
                inventory_df['_reorder'] = 10

            total_items = len(inventory_df)
            zero_stock = int((inventory_df['_stock'] == 0).sum())
            low_stock = int((inventory_df['_stock'] <= inventory_df['_reorder']).sum())

            return {
                'total_items': int(total_items),
                'zero_stock': int(zero_stock),
                'low_stock': int(low_stock),
                'stockout_risk_pct': (low_stock / total_items * 100) if total_items > 0 else 0
            }
        except Exception as e:
            print(f"Error in calculate_stockout_risk: {e}")
            return {'total_items': 0, 'zero_stock': 0, 'low_stock': 0, 'stockout_risk_pct': 0}

    # ---------------------------------------------------------------------
    # Helpers for the revamped simulate_campaign()
    # ---------------------------------------------------------------------
    def _attach_store_dims(self, sales_df, stores_df):
        merged = sales_df.copy()
        store_col_sales = self._get_store_column(sales_df)
        store_col_stores = self._get_store_column(stores_df) if stores_df is not None else None
        city_col = self._get_city_column(stores_df) if stores_df is not None else None
        channel_col = self._get_channel_column(stores_df) if stores_df is not None else None

        if stores_df is not None and store_col_sales and store_col_stores:
            cols = [store_col_stores]
            if city_col:
                cols.append(city_col)
            if channel_col:
                cols.append(channel_col)
            ssub = stores_df[cols].copy()
            ssub.columns = ['_store'] + cols[1:]
            merged['_store'] = merged[store_col_sales]
            merged = merged.merge(ssub, on='_store', how='left')

        return merged, city_col, channel_col

    def _attach_product_dims(self, sales_df, products_df):
        merged = sales_df.copy()
        sku_col_sales = self._get_sku_column(sales_df)
        sku_col_products = self._get_sku_column(products_df) if products_df is not None else None
        cost_col = self._get_cost_column(products_df) if products_df is not None else None
        category_col = self._get_category_column(products_df) if products_df is not None else None
        brand_col = self._get_brand_column(products_df) if products_df is not None else None

        if products_df is not None and sku_col_sales and sku_col_products:
            cols = [sku_col_products]
            if cost_col:
                cols.append(cost_col)
            if category_col:
                cols.append(category_col)
            if brand_col:
                cols.append(brand_col)

            psub = products_df[cols].copy()
            renamed = ['_sku']
            if cost_col:
                renamed.append('_cost')
            if category_col:
                renamed.append('category')
            if brand_col:
                renamed.append('brand')
            psub.columns = renamed

            merged['_sku'] = merged[sku_col_sales]
            merged = merged.merge(psub, on='_sku', how='left')

        # Defaults
        if '_cost' not in merged.columns:
            merged['_cost'] = 0
        if 'category' not in merged.columns:
            merged['category'] = 'Unknown'
        if 'brand' not in merged.columns:
            merged['brand'] = 'Unknown'

        return merged, sku_col_sales

    def _compute_revenue_profit_cols(self, df, price_col, qty_col):
        out = df.copy()
        out['_qty'] = pd.to_numeric(out[qty_col], errors='coerce').fillna(0) if qty_col else 1
        out['_price'] = pd.to_numeric(out[price_col], errors='coerce').fillna(0) if price_col else 0
        out['_cost'] = pd.to_numeric(out['_cost'], errors='coerce').fillna(0)

        out['revenue'] = out['_qty'] * out['_price']
        out['profit'] = out['_qty'] * (out['_price'] - out['_cost'])
        return out

    # ---------------------------------------------------------------------
    # REVAMPED: simulate_campaign
    # ---------------------------------------------------------------------
    def simulate_campaign(
        self,
        sales_df,
        stores_df,
        products_df,
        discount_pct=10,
        promo_budget=10000,
        margin_floor=15,
        city='All',
        channel='All',
        category='All',
        campaign_days=7,
        # new optional params to mimic your other simulator style
        brand='All',
        sku='All',
        promo_type="Percentage Off",
        data_days=30
    ):
        """
        Simulate a promotional campaign.

        This is a revamp that supports:
        - category -> brand -> sku scoping (optional)
        - city/channel targeting (existing)
        - margin floor enforcement (discount is capped if it breaches floor)
        - promo budget constraint (promo spend <= promo_budget, with safety cap)
        - returns scenario object for UI explanation
        """
        try:
            if sales_df is None or len(sales_df) == 0:
                return {'outputs': None, 'comparison': None, 'warnings': ['No sales data provided']}

            merged = sales_df.copy()

            # Attach stores + products
            merged, city_col, channel_col = self._attach_store_dims(merged, stores_df)
            merged, sku_col_sales = self._attach_product_dims(merged, products_df)

            # Identify core columns
            price_col = self._get_price_column(merged)
            qty_col = self._get_qty_column(merged)
            order_col = self._get_order_column(merged)

            # Normalize city/channel columns if merged used original names
            # (In _attach_store_dims we kept original names from stores_df)
            # For filtering, we must use city_col/channel_col if present.
            if city_col is None:
                # maybe already exists as 'city' (cleaned data)
                if 'city' in merged.columns:
                    city_col = 'city'
            if channel_col is None:
                if 'channel' in merged.columns:
                    channel_col = 'channel'

            # Compute revenue/profit base columns
            merged = self._compute_revenue_profit_cols(merged, price_col, qty_col)

            # -------------------------------
            # Apply targeting filters (scope)
            # -------------------------------
            # City/channel
            if city != 'All' and city_col and city_col in merged.columns:
                merged = merged[merged[city_col] == city]
            if channel != 'All' and channel_col and channel_col in merged.columns:
                merged = merged[merged[channel_col] == channel]

            # Category/brand/sku (your "other project" chain)
            if category != 'All' and 'category' in merged.columns:
                merged = merged[merged['category'] == category]

            if brand != 'All' and brand != 'All Brands' and 'brand' in merged.columns:
                merged = merged[merged['brand'] == brand]

            if sku != 'All' and sku != 'All SKUs in Category':
                # sku might match _sku or original sku column depending on UI
                if '_sku' in merged.columns:
                    merged = merged[merged['_sku'].astype(str) == str(sku)]
                elif sku_col_sales and sku_col_sales in merged.columns:
                    merged = merged[merged[sku_col_sales].astype(str) == str(sku)]

            if len(merged) == 0:
                return {'outputs': None, 'comparison': None, 'warnings': ['No data matches filters']}

            # -------------------------------
            # Baseline for the chosen scope
            # -------------------------------
            baseline_revenue = merged['revenue'].sum() / data_days * campaign_days
            baseline_profit = merged['profit'].sum() / data_days * campaign_days

            if order_col and order_col in merged.columns:
                baseline_orders = merged[order_col].nunique() / data_days * campaign_days
            else:
                baseline_orders = len(merged) / data_days * campaign_days

            baseline_units = merged['_qty'].sum() / data_days * campaign_days

            # -------------------------------
            # Demand lift model
            # -------------------------------
            # Elasticity based on category if selected, otherwise default.
            # If category is All but filtered data has a dominant category, use that.
            if category != 'All':
                elasticity = self.category_elasticity.get(category, self.default_elasticity)
            else:
                elasticity = self.default_elasticity

            # Promo-type multiplier (optional)
            promo_mult = self.promo_type_multiplier.get(promo_type, 1.0)

            # Core lift: discount * elasticity
            demand_lift_pct = discount_pct * elasticity * promo_mult

            # clamp lift to avoid absurd numbers
            demand_lift_pct = float(np.clip(demand_lift_pct, -50, 400))

            expected_units = baseline_units * (1 + demand_lift_pct / 100)

            avg_price = float(merged['_price'].replace([np.inf, -np.inf], np.nan).dropna().mean()) if len(merged) else 0.0
            avg_cost = float(merged['_cost'].replace([np.inf, -np.inf], np.nan).dropna().mean()) if len(merged) else 0.0

            # -------------------------------
            # Margin floor enforcement
            # -------------------------------
            base_margin_pct = ((avg_price - avg_cost) / avg_price * 100) if avg_price > 0 else 0

            effective_discount = float(discount_pct)
            margin_capped = False

            discounted_price = avg_price * (1 - effective_discount / 100)
            expected_margin_pct = ((discounted_price - avg_cost) / discounted_price * 100) if discounted_price > 0 else 0

            # If discount breaches floor and baseline margin was above floor, cap discount
            if expected_margin_pct < margin_floor and base_margin_pct > margin_floor and avg_price > 0:
                # min price needed to satisfy margin floor
                min_price = avg_cost / (1 - margin_floor / 100) if margin_floor < 100 else avg_cost
                max_discount = ((avg_price - min_price) / avg_price * 100)
                max_discount = float(np.clip(max_discount, 0, 95))
                effective_discount = min(effective_discount, max_discount)
                margin_capped = True

                # recompute lift + units using effective_discount
                demand_lift_pct = effective_discount * elasticity * promo_mult
                demand_lift_pct = float(np.clip(demand_lift_pct, -50, 400))
                expected_units = baseline_units * (1 + demand_lift_pct / 100)

                discounted_price = avg_price * (1 - effective_discount / 100)
                expected_margin_pct = ((discounted_price - avg_cost) / discounted_price * 100) if discounted_price > 0 else 0

            # -------------------------------
            # Revenue + costs
            # -------------------------------
            expected_revenue = expected_units * discounted_price
            cogs = expected_units * avg_cost
            expected_gross_profit = expected_revenue - cogs

            # Promo cost model:
            # - cannot exceed promo_budget
            # - also cap at 5% of expected revenue (safety)
            promo_cost = min(float(promo_budget), float(expected_revenue) * 0.05)

            # Fulfillment cost only on incremental units
            incremental_units = max(0.0, expected_units - baseline_units)
            fulfillment_cost = incremental_units * 1.5

            expected_net_profit = expected_gross_profit - promo_cost - fulfillment_cost

            # ROI based on incremental net profit / investment
            total_investment = promo_cost + fulfillment_cost
            incremental_profit = expected_net_profit - baseline_profit
            roi_pct = (incremental_profit / total_investment * 100) if total_investment > 0 else (0 if incremental_profit <= 0 else 100)
            roi_pct = float(np.clip(roi_pct, -100, 500))

            # -------------------------------
            # Warnings (business logic)
            # -------------------------------
            warnings = []
            if margin_capped:
                warnings.append(f"Discount capped to {effective_discount:.1f}% to maintain {margin_floor}% margin floor")
            if expected_margin_pct < margin_floor:
                warnings.append(f"Margin ({expected_margin_pct:.1f}%) below floor ({margin_floor}%) - campaign not recommended")
            if roi_pct < 0:
                warnings.append(f"Negative ROI ({roi_pct:.1f}%) - campaign will lose money")
            if 0 <= roi_pct < 50:
                warnings.append(f"Low ROI ({roi_pct:.1f}%) - consider reducing discount or budget")
            if discount_pct > 30:
                warnings.append("High discount may erode brand value")

            # Extra budget warning: if promo_budget is tiny vs required spend cap
            if promo_budget < expected_revenue * 0.01:
                warnings.append("Promo budget is very low vs expected revenue; lift assumptions may be optimistic")

            # -------------------------------
            # Scenario object for UI explanation
            # -------------------------------
            scenario = {
                "city": city,
                "channel": channel,
                "category": category,
                "brand": brand,
                "sku": sku,
                "promo_type": promo_type,
                "discount_pct_requested": float(discount_pct),
                "discount_pct_effective": float(effective_discount),
                "campaign_days": int(campaign_days),
                "margin_floor_pct": float(margin_floor),
                "promo_budget": float(promo_budget),
                "elasticity": float(elasticity),
                "promo_type_multiplier": float(promo_mult),
                "data_days_assumed": int(data_days),
            }

            outputs = {
                'expected_revenue': float(expected_revenue),
                'expected_orders': int(baseline_orders * (1 + demand_lift_pct / 100)),
                'expected_units': float(expected_units),
                'expected_net_profit': float(expected_net_profit),
                'expected_margin_pct': float(expected_margin_pct),
                'demand_lift_pct': float(demand_lift_pct),
                'roi_pct': float(roi_pct),
                'promo_cost': float(promo_cost),
                'fulfillment_cost': float(fulfillment_cost),
                # additional helpful fields for “data and information”
                'expected_gross_profit': float(expected_gross_profit),
                'avg_selling_price': float(avg_price),
                'avg_unit_cost': float(avg_cost),
                'incremental_units': float(incremental_units),
            }

            comparison = {
                'baseline_revenue': float(baseline_revenue),
                'baseline_profit': float(baseline_profit),
                'baseline_orders': int(baseline_orders),
                'revenue_change_pct': ((expected_revenue - baseline_revenue) / baseline_revenue * 100) if baseline_revenue > 0 else 0,
                'profit_change_pct': ((expected_net_profit - baseline_profit) / abs(baseline_profit) * 100) if baseline_profit != 0 else 0,
                'order_change_pct': float(demand_lift_pct),
            }

            return {'outputs': outputs, 'comparison': comparison, 'warnings': warnings, 'scenario': scenario}

        except Exception as e:
            print(f"Error in simulate_campaign: {e}")
            return {'outputs': None, 'comparison': None, 'warnings': [f'Error: {str(e)}']}
