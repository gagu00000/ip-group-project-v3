"""
Simulator Module for UAE Pulse Dashboard
Campaign simulation and KPI calculations
FIXED VERSION - Realistic ROI Calculation
"""

import pandas as pd
import numpy as np


class Simulator:
    """Campaign simulator with KPI calculations."""
    
    def __init__(self):
        """Initialize simulator with default elasticity values."""
        # More conservative elasticity (realistic for UAE market)
        self.category_elasticity = {
            'Electronics': 1.5,
            'Fashion': 1.8,
            'Grocery': 1.2,
            'Beauty': 1.6,
            'Home': 1.4,
            'Sports': 1.5
        }
        self.default_elasticity = 1.5
    
    def _find_column(self, df, possible_names):
        """Find a column from a list of possible names."""
        if df is None:
            return None
        for name in possible_names:
            if name in df.columns:
                return name
        return None
    
    def _get_sku_column(self, df):
        return self._find_column(df, ['sku', 'SKU', 'product_id', 'ProductID', 'product_sku', 'item_id'])
    
    def _get_cost_column(self, df):
        return self._find_column(df, ['unit_cost_aed', 'cost_aed', 'cost', 'unit_cost', 'cost_price', 'purchase_price'])
    
    def _get_price_column(self, df):
        return self._find_column(df, ['selling_price_aed', 'selling_price', 'price', 'unit_price', 'sale_price'])
    
    def _get_qty_column(self, df):
        return self._find_column(df, ['qty', 'quantity', 'units', 'qty_sold', 'units_sold'])
    
    def _get_date_column(self, df):
        return self._find_column(df, ['order_ts', 'order_time', 'order_date', 'date', 'timestamp', 'created_at'])
    
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
    
    def _get_data_days(self, sales_df):
        """Calculate actual number of days in data."""
        date_col = self._get_date_column(sales_df)
        if date_col and date_col in sales_df.columns:
            try:
                dates = pd.to_datetime(sales_df[date_col], errors='coerce').dropna()
                if len(dates) > 0:
                    days = (dates.max() - dates.min()).days + 1
                    return max(1, days)
            except Exception:
                pass
        return 30
    
    def calculate_overall_kpis(self, sales_df, products_df):
        """Calculate overall KPIs from sales data."""
        kpis = {
            'total_revenue': 0,
            'total_profit': 0,
            'total_orders': 0,
            'total_units': 0,
            'avg_order_value': 0,
            'profit_margin_pct': 0,
            'return_rate_pct': 0,
            'refund_amount': 0,
            'total_cogs': 0,
            'net_revenue': 0,
            'avg_discount_pct': 0,
            'total_discount': 0
        }
        
        if sales_df is None or len(sales_df) == 0:
            return kpis
        
        try:
            sku_col_sales = self._get_sku_column(sales_df)
            sku_col_products = self._get_sku_column(products_df) if products_df is not None else None
            cost_col = self._get_cost_column(products_df) if products_df is not None else None
            price_col = self._get_price_column(sales_df)
            qty_col = self._get_qty_column(sales_df)
            order_col = self._get_order_column(sales_df)
            
            merged = sales_df.copy()
            
            if sku_col_sales and sku_col_products and cost_col and products_df is not None:
                products_subset = products_df[[sku_col_products, cost_col]].copy()
                products_subset.columns = ['_sku', '_cost']
                merged['_sku'] = merged[sku_col_sales]
                merged = merged.merge(products_subset, on='_sku', how='left')
                merged['_cost'] = merged['_cost'].fillna(0)
            else:
                merged['_cost'] = 0
            
            if qty_col:
                merged['_qty'] = pd.to_numeric(merged[qty_col], errors='coerce').fillna(0)
            else:
                merged['_qty'] = 1
            
            if price_col:
                merged['_price'] = pd.to_numeric(merged[price_col], errors='coerce').fillna(0)
            else:
                merged['_price'] = 0
            
            merged['_cost'] = pd.to_numeric(merged['_cost'], errors='coerce').fillna(0)
            
            # Use 40% COGS ratio if no cost data (60% gross margin)
            if merged['_cost'].sum() == 0:
                merged['_cost'] = merged['_price'] * 0.40
            
            merged['revenue'] = merged['_qty'] * merged['_price']
            merged['profit'] = merged['_qty'] * (merged['_price'] - merged['_cost'])
            
            kpis['total_revenue'] = float(merged['revenue'].sum())
            kpis['total_profit'] = float(merged['profit'].sum())
            
            if order_col and order_col in merged.columns:
                kpis['total_orders'] = int(merged[order_col].nunique())
            else:
                kpis['total_orders'] = len(merged)
            
            kpis['total_units'] = float(merged['_qty'].sum())
            kpis['avg_order_value'] = kpis['total_revenue'] / kpis['total_orders'] if kpis['total_orders'] > 0 else 0
            kpis['profit_margin_pct'] = (kpis['total_profit'] / kpis['total_revenue'] * 100) if kpis['total_revenue'] > 0 else 0
            
            merged['cogs'] = merged['_qty'] * merged['_cost']
            kpis['total_cogs'] = float(merged['cogs'].sum())
            kpis['net_revenue'] = kpis['total_revenue']
            
        except Exception as e:
            print(f"Error in calculate_overall_kpis: {e}")
        
        return kpis
    
    def calculate_kpis_by_dimension(self, sales_df, stores_df, products_df, dimension):
        """Calculate KPIs grouped by a dimension (city, channel, category)."""
        if sales_df is None or len(sales_df) == 0:
            return pd.DataFrame()
        
        try:
            merged = sales_df.copy()
            
            sku_col_sales = self._get_sku_column(sales_df)
            sku_col_products = self._get_sku_column(products_df) if products_df is not None else None
            store_col_sales = self._get_store_column(sales_df)
            store_col_stores = self._get_store_column(stores_df) if stores_df is not None else None
            cost_col = self._get_cost_column(products_df) if products_df is not None else None
            price_col = self._get_price_column(sales_df)
            qty_col = self._get_qty_column(sales_df)
            order_col = self._get_order_column(sales_df)
            category_col = self._get_category_column(products_df) if products_df is not None else None
            city_col = self._get_city_column(stores_df) if stores_df is not None else None
            channel_col = self._get_channel_column(stores_df) if stores_df is not None else None
            
            if store_col_sales and store_col_stores and stores_df is not None:
                stores_cols = [store_col_stores]
                if city_col:
                    stores_cols.append(city_col)
                if channel_col:
                    stores_cols.append(channel_col)
                
                stores_subset = stores_df[stores_cols].copy()
                new_names = ['_store']
                if city_col:
                    new_names.append('city')
                if channel_col:
                    new_names.append('channel')
                stores_subset.columns = new_names
                
                merged['_store'] = merged[store_col_sales]
                merged = merged.merge(stores_subset, on='_store', how='left')
            
            if sku_col_sales and sku_col_products and products_df is not None:
                products_cols = [sku_col_products]
                if cost_col:
                    products_cols.append(cost_col)
                if category_col:
                    products_cols.append(category_col)
                
                products_subset = products_df[products_cols].copy()
                new_names = ['_sku']
                if cost_col:
                    new_names.append('_cost')
                if category_col:
                    new_names.append('category')
                products_subset.columns = new_names
                
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
            
            if qty_col:
                merged['_qty'] = pd.to_numeric(merged[qty_col], errors='coerce').fillna(0)
            else:
                merged['_qty'] = 1
            
            if price_col:
                merged['_price'] = pd.to_numeric(merged[price_col], errors='coerce').fillna(0)
            else:
                merged['_price'] = 0
            
            merged['_cost'] = pd.to_numeric(merged['_cost'], errors='coerce').fillna(0)
            
            if merged['_cost'].sum() == 0:
                merged['_cost'] = merged['_price'] * 0.40
            
            merged['revenue'] = merged['_qty'] * merged['_price']
            merged['profit'] = merged['_qty'] * (merged['_price'] - merged['_cost'])
            
            if order_col and order_col in merged.columns:
                merged['_order_id'] = merged[order_col]
            else:
                merged['_order_id'] = range(len(merged))
            
            if dimension not in merged.columns:
                return pd.DataFrame()
            
            grouped = merged.groupby(dimension).agg({
                'revenue': 'sum',
                'profit': 'sum',
                '_order_id': 'nunique',
                '_qty': 'sum'
            }).reset_index()
            
            grouped.columns = [dimension, 'revenue', 'profit', 'orders', 'units']
            grouped['avg_order_value'] = grouped['revenue'] / grouped['orders']
            grouped['margin_pct'] = (grouped['profit'] / grouped['revenue'] * 100).fillna(0)
            grouped = grouped.sort_values('revenue', ascending=False)
            
            return grouped
            
        except Exception as e:
            print(f"Error in calculate_kpis_by_dimension: {e}")
            return pd.DataFrame()
    
    def calculate_daily_trends(self, sales_df, products_df):
        """Calculate daily performance trends."""
        if sales_df is None or len(sales_df) == 0:
            return pd.DataFrame(columns=['date', 'revenue', 'profit', 'orders', 'units'])
        
        try:
            merged = sales_df.copy()
            
            sku_col_sales = self._get_sku_column(sales_df)
            sku_col_products = self._get_sku_column(products_df) if products_df is not None else None
            cost_col = self._get_cost_column(products_df) if products_df is not None else None
            price_col = self._get_price_column(sales_df)
            qty_col = self._get_qty_column(sales_df)
            date_col = self._get_date_column(sales_df)
            order_col = self._get_order_column(sales_df)
            
            if sku_col_sales and sku_col_products and cost_col and products_df is not None:
                products_subset = products_df[[sku_col_products, cost_col]].copy()
                products_subset.columns = ['_sku', '_cost']
                merged['_sku'] = merged[sku_col_sales]
                merged = merged.merge(products_subset, on='_sku', how='left')
                merged['_cost'] = merged['_cost'].fillna(0)
            else:
                merged['_cost'] = 0
            
            if qty_col:
                merged['_qty'] = pd.to_numeric(merged[qty_col], errors='coerce').fillna(0)
            else:
                merged['_qty'] = 1
            
            if price_col:
                merged['_price'] = pd.to_numeric(merged[price_col], errors='coerce').fillna(0)
            else:
                merged['_price'] = 0
            
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
            
            if order_col and order_col in merged.columns:
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
        """Calculate stockout risk metrics."""
        result = {
            'total_items': 0,
            'zero_stock': 0,
            'low_stock': 0,
            'stockout_risk_pct': 0
        }
        
        if inventory_df is None or len(inventory_df) == 0:
            return result
        
        try:
            stock_col = self._find_column(inventory_df, ['stock_on_hand', 'stock', 'quantity', 'qty', 'inventory'])
            reorder_col = self._find_column(inventory_df, ['reorder_point', 'reorder_level', 'min_stock'])
            
            df = inventory_df.copy()
            
            if stock_col:
                df['_stock'] = pd.to_numeric(df[stock_col], errors='coerce').fillna(0)
            else:
                df['_stock'] = 0
            
            if reorder_col:
                df['_reorder'] = pd.to_numeric(df[reorder_col], errors='coerce').fillna(10)
            else:
                df['_reorder'] = 10
            
            result['total_items'] = len(df)
            result['zero_stock'] = len(df[df['_stock'] == 0])
            result['low_stock'] = len(df[df['_stock'] <= df['_reorder']])
            result['stockout_risk_pct'] = (result['low_stock'] / result['total_items'] * 100) if result['total_items'] > 0 else 0
            
        except Exception as e:
            print(f"Error in calculate_stockout_risk: {e}")
        
        return result
    
    def simulate_campaign(self, sales_df, stores_df, products_df,
                          discount_pct=10, promo_budget=10000, margin_floor=15,
                          city='All', channel='All', category='All', campaign_days=7):
        """
        Simulate a promotional campaign with REALISTIC ROI calculation.
        
        Key insight: ROI should measure the VALUE generated, not just incremental profit.
        A successful campaign generates enough gross profit to cover its costs.
        """
        
        result = {
            'outputs': None,
            'comparison': None,
            'warnings': []
        }
        
        if sales_df is None or len(sales_df) == 0:
            result['warnings'].append('No sales data available')
            return result
        
        try:
            merged = sales_df.copy()
            
            # Find columns
            sku_col_sales = self._get_sku_column(sales_df)
            sku_col_products = self._get_sku_column(products_df) if products_df is not None else None
            store_col_sales = self._get_store_column(sales_df)
            store_col_stores = self._get_store_column(stores_df) if stores_df is not None else None
            cost_col = self._get_cost_column(products_df) if products_df is not None else None
            price_col = self._get_price_column(sales_df)
            qty_col = self._get_qty_column(sales_df)
            order_col = self._get_order_column(sales_df)
            category_col = self._get_category_column(products_df) if products_df is not None else None
            city_col = self._get_city_column(stores_df) if stores_df is not None else None
            channel_col = self._get_channel_column(stores_df) if stores_df is not None else None
            
            # Merge with stores
            if store_col_sales and store_col_stores and stores_df is not None:
                stores_cols = [store_col_stores]
                if city_col:
                    stores_cols.append(city_col)
                if channel_col:
                    stores_cols.append(channel_col)
                
                stores_subset = stores_df[stores_cols].copy()
                stores_subset.columns = ['_store'] + stores_cols[1:]
                merged['_store'] = merged[store_col_sales]
                merged = merged.merge(stores_subset, on='_store', how='left')
            
            # Merge with products
            if sku_col_sales and sku_col_products and products_df is not None:
                products_cols = [sku_col_products]
                if cost_col:
                    products_cols.append(cost_col)
                if category_col:
                    products_cols.append(category_col)
                
                products_subset = products_df[products_cols].copy()
                new_names = ['_sku']
                if cost_col:
                    new_names.append('_cost')
                if category_col:
                    new_names.append('category')
                products_subset.columns = new_names
                
                merged['_sku'] = merged[sku_col_sales]
                merged = merged.merge(products_subset, on='_sku', how='left')
            
            # Set defaults
            if '_cost' not in merged.columns:
                merged['_cost'] = 0
            if 'category' not in merged.columns:
                merged['category'] = 'Unknown'
            
            # Get qty and price
            if qty_col:
                merged['_qty'] = pd.to_numeric(merged[qty_col], errors='coerce').fillna(0)
            else:
                merged['_qty'] = 1
            
            if price_col:
                merged['_price'] = pd.to_numeric(merged[price_col], errors='coerce').fillna(0)
            else:
                merged['_price'] = 0
            
            merged['_cost'] = pd.to_numeric(merged['_cost'], errors='coerce').fillna(0)
            
            # IMPORTANT: Use realistic COGS ratio (40% COGS = 60% gross margin)
            # This is typical for retail in UAE
            if merged['_cost'].sum() == 0 or merged['_cost'].mean() == 0:
                merged['_cost'] = merged['_price'] * 0.40
            
            # Filter by targeting
            if city != 'All' and city_col and city_col in merged.columns:
                merged = merged[merged[city_col] == city]
            if channel != 'All' and channel_col and channel_col in merged.columns:
                merged = merged[merged[channel_col] == channel]
            if category != 'All' and 'category' in merged.columns:
                merged = merged[merged['category'] == category]
            
            if len(merged) == 0:
                result['warnings'].append('No data matches filters')
                return result
            
            # Calculate revenue and profit
            merged['revenue'] = merged['_qty'] * merged['_price']
            merged['cogs'] = merged['_qty'] * merged['_cost']
            merged['profit'] = merged['revenue'] - merged['cogs']
            
            # Get data days
            data_days = self._get_data_days(sales_df)
            
            # ================================================================
            # BASELINE CALCULATIONS
            # ================================================================
            total_revenue = merged['revenue'].sum()
            total_cogs = merged['cogs'].sum()
            total_profit = merged['profit'].sum()
            total_units = merged['_qty'].sum()
            
            if order_col and order_col in merged.columns:
                total_orders = merged[order_col].nunique()
            else:
                total_orders = len(merged)
            
            # Daily averages
            daily_revenue = total_revenue / data_days
            daily_profit = total_profit / data_days
            daily_orders = total_orders / data_days
            daily_units = total_units / data_days
            daily_cogs = total_cogs / data_days
            
            # Baseline for campaign period
            baseline_revenue = daily_revenue * campaign_days
            baseline_profit = daily_profit * campaign_days
            baseline_orders = daily_orders * campaign_days
            baseline_units = daily_units * campaign_days
            baseline_cogs = daily_cogs * campaign_days
            
            # Average prices
            avg_price = merged['_price'].mean()
            avg_cost = merged['_cost'].mean()
            baseline_margin_pct = ((avg_price - avg_cost) / avg_price * 100) if avg_price > 0 else 60
            
            # ================================================================
            # CAMPAIGN EFFECT CALCULATION
            # ================================================================
            
            # Get elasticity for category
            if category != 'All' and category in self.category_elasticity:
                elasticity = self.category_elasticity[category]
            else:
                elasticity = self.default_elasticity
            
            # Volume increase from discount
            # More conservative: each 1% discount → elasticity% more volume
            demand_lift_pct = discount_pct * elasticity
            volume_multiplier = 1 + (demand_lift_pct / 100)
            
            # Price after discount
            discounted_price = avg_price * (1 - discount_pct / 100)
            
            # New margin after discount
            new_margin_per_unit = discounted_price - avg_cost
            new_margin_pct = (new_margin_per_unit / discounted_price * 100) if discounted_price > 0 else 0
            
            # ================================================================
            # EXPECTED OUTCOMES
            # ================================================================
            
            expected_units = baseline_units * volume_multiplier
            expected_orders = int(baseline_orders * volume_multiplier)
            expected_revenue = expected_units * discounted_price
            expected_cogs = expected_units * avg_cost
            expected_gross_profit = expected_revenue - expected_cogs
            
            # Net profit after marketing spend
            # Assume we spend 100% of budget on the campaign
            marketing_spend = promo_budget
            expected_net_profit = expected_gross_profit - marketing_spend
            
            # Final margin
            expected_margin_pct = (expected_gross_profit / expected_revenue * 100) if expected_revenue > 0 else 0
            
            # ================================================================
            # ROI CALCULATION - MULTIPLE METHODS
            # ================================================================
            
            # Method 1: Marketing ROI (Revenue generated per dollar spent)
            # ROMI = (Revenue - Marketing Cost) / Marketing Cost
            if marketing_spend > 0:
                romi = ((expected_revenue - marketing_spend) / marketing_spend) * 100
            else:
                romi = 0
            
            # Method 2: Profit ROI (Profit generated vs spend)
            # This is more meaningful - did we make money?
            if marketing_spend > 0:
                profit_roi = (expected_gross_profit / marketing_spend) * 100
            else:
                profit_roi = 0
            
            # Method 3: Incremental ROI (Extra profit vs spend)
            incremental_profit = expected_gross_profit - baseline_profit
            if marketing_spend > 0:
                incremental_roi = (incremental_profit / marketing_spend) * 100
            else:
                incremental_roi = 0
            
            # Method 4: Net ROI (Net profit vs spend) - Most conservative
            if marketing_spend > 0:
                net_roi = (expected_net_profit / marketing_spend) * 100
            else:
                net_roi = 0
            
            # ================================================================
            # CHOOSE THE BEST ROI FOR DISPLAY
            # ================================================================
            
            # Use Profit ROI as primary metric (most intuitive)
            # "For every AED 1 spent, we generate X AED in gross profit"
            display_roi = profit_roi
            
            # If gross profit > spend, campaign is profitable
            # ROI of 100% means we generated AED 1 profit per AED 1 spent
            # ROI of 200% means we generated AED 2 profit per AED 1 spent
            
            # ================================================================
            # WARNINGS
            # ================================================================
            warnings = []
            
            if expected_margin_pct < margin_floor:
                warnings.append(f"⚠️ Margin ({expected_margin_pct:.1f}%) below floor ({margin_floor}%)")
            
            if expected_gross_profit < marketing_spend:
                warnings.append(f"⚠️ Gross profit (AED {expected_gross_profit:,.0f}) < budget (AED {marketing_spend:,.0f})")
            
            if incremental_profit < 0:
                warnings.append(f"⚠️ Campaign reduces profit by AED {abs(incremental_profit):,.0f}")
            
            if discount_pct > 30:
                warnings.append("⚠️ High discount (>30%) may erode brand value")
            
            if new_margin_pct < 20:
                warnings.append(f"⚠️ Post-discount margin very low ({new_margin_pct:.1f}%)")
            
            # ================================================================
            # COMPILE RESULTS
            # ================================================================
            
            result['outputs'] = {
                'expected_revenue': expected_revenue,
                'expected_orders': expected_orders,
                'expected_units': expected_units,
                'expected_gross_profit': expected_gross_profit,
                'expected_net_profit': expected_net_profit,
                'expected_margin_pct': expected_margin_pct,
                'demand_lift_pct': demand_lift_pct,
                'roi_pct': display_roi,
                'incremental_roi_pct': incremental_roi,
                'net_roi_pct': net_roi,
                'romi_pct': romi,
                'promo_cost': marketing_spend,
                'volume_multiplier': volume_multiplier,
                'incremental_profit': incremental_profit,
                'new_margin_pct': new_margin_pct
            }
            
            result['comparison'] = {
                'baseline_revenue': baseline_revenue,
                'baseline_profit': baseline_profit,
                'baseline_orders': int(baseline_orders),
                'baseline_cogs': baseline_cogs,
                'baseline_margin_pct': baseline_margin_pct,
                'revenue_change_pct': ((expected_revenue - baseline_revenue) / baseline_revenue * 100) if baseline_revenue > 0 else 0,
                'profit_change_pct': ((expected_gross_profit - baseline_profit) / baseline_profit * 100) if baseline_profit > 0 else 0,
                'order_change_pct': demand_lift_pct
            }
            
            result['warnings'] = warnings
            
        except Exception as e:
            print(f"Error in simulate_campaign: {e}")
            import traceback
            traceback.print_exc()
            result['warnings'].append(f'Error: {str(e)}')
        
        return result
