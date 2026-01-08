"""
Simulator Module for UAE Pulse Dashboard
Campaign simulation and KPI calculations
"""

import pandas as pd
import numpy as np


class Simulator:
    """Campaign simulator with KPI calculations."""
    
    def __init__(self):
        """Initialize simulator with default elasticity values."""
        self.category_elasticity = {
            'Electronics': 1.8,
            'Fashion': 2.0,
            'Grocery': 1.2,
            'Beauty': 1.6,
            'Home': 1.4,
            'Sports': 1.7
        }
        self.default_elasticity = 1.5
    
    def _find_column(self, df, possible_names):
        """Find a column from a list of possible names."""
        for name in possible_names:
            if name in df.columns:
                return name
        return None
    
    def _get_sku_column(self, df):
        """Find SKU column."""
        return self._find_column(df, ['sku', 'SKU', 'product_id', 'ProductID', 'product_sku', 'item_id'])
    
    def _get_cost_column(self, df):
        """Find cost column."""
        return self._find_column(df, ['cost_aed', 'cost', 'unit_cost', 'cost_price', 'purchase_price', 'buying_price'])
    
    def _get_price_column(self, df):
        """Find selling price column."""
        return self._find_column(df, ['selling_price_aed', 'selling_price', 'price', 'unit_price', 'sale_price'])
    
    def _get_qty_column(self, df):
        """Find quantity column."""
        return self._find_column(df, ['qty', 'quantity', 'units', 'qty_sold', 'units_sold'])
    
    def _get_date_column(self, df):
        """Find date column."""
        return self._find_column(df, ['order_ts', 'order_date', 'date', 'timestamp', 'created_at', 'sale_date', 'transaction_date'])
    
    def _get_order_column(self, df):
        """Find order ID column."""
        return self._find_column(df, ['order_id', 'OrderID', 'transaction_id', 'invoice_id'])
    
    def _get_store_column(self, df):
        """Find store ID column."""
        return self._find_column(df, ['store_id', 'StoreID', 'store', 'location_id'])
    
    def _get_category_column(self, df):
        """Find category column."""
        return self._find_column(df, ['category', 'Category', 'product_category', 'cat'])
    
    def _get_city_column(self, df):
        """Find city column."""
        return self._find_column(df, ['city', 'City', 'location', 'store_city'])
    
    def _get_channel_column(self, df):
        """Find channel column."""
        return self._find_column(df, ['channel', 'Channel', 'sales_channel', 'store_channel'])
    
    def calculate_overall_kpis(self, sales_df, products_df):
        """Calculate overall KPIs from sales data."""
        kpis = {}
        
        try:
            # Find column names
            sku_col_sales = self._get_sku_column(sales_df)
            sku_col_products = self._get_sku_column(products_df)
            cost_col = self._get_cost_column(products_df)
            price_col = self._get_price_column(sales_df)
            qty_col = self._get_qty_column(sales_df)
            order_col = self._get_order_column(sales_df)
            
            # Create working copy
            merged = sales_df.copy()
            
            # Merge with products if possible
            if sku_col_sales and sku_col_products and cost_col:
                products_subset = products_df[[sku_col_products, cost_col]].copy()
                products_subset.columns = ['_sku', '_cost']
                merged['_sku'] = merged[sku_col_sales]
                merged = merged.merge(products_subset, on='_sku', how='left')
                merged['_cost'] = merged['_cost'].fillna(0)
            else:
                merged['_cost'] = 0
            
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
            
            # Calculate
            merged['revenue'] = merged['_qty'] * merged['_price']
            merged['profit'] = merged['_qty'] * (merged['_price'] - merged['_cost'])
            
            kpis['total_revenue'] = float(merged['revenue'].sum())
            kpis['total_profit'] = float(merged['profit'].sum())
            
            if order_col:
                kpis['total_orders'] = int(merged[order_col].nunique())
            else:
                kpis['total_orders'] = len(merged)
            
            kpis['total_units'] = float(merged['_qty'].sum())
            kpis['avg_order_value'] = kpis['total_revenue'] / kpis['total_orders'] if kpis['total_orders'] > 0 else 0
            kpis['profit_margin_pct'] = (kpis['total_profit'] / kpis['total_revenue'] * 100) if kpis['total_revenue'] > 0 else 0
            
            # Return rate
            if 'is_returned' in sales_df.columns:
                returned = pd.to_numeric(sales_df['is_returned'], errors='coerce').fillna(0)
                kpis['return_rate_pct'] = float(returned.mean() * 100)
            else:
                kpis['return_rate_pct'] = 0
            
            # Discount
            discount_col = self._find_column(sales_df, ['discount_pct', 'discount', 'discount_percent'])
            if discount_col:
                discount = pd.to_numeric(sales_df[discount_col], errors='coerce').fillna(0)
                kpis['avg_discount_pct'] = float(discount.mean())
            else:
                kpis['avg_discount_pct'] = 0
                
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
                'avg_discount_pct': 0
            }
        
        return kpis
    
    def calculate_kpis_by_dimension(self, sales_df, stores_df, products_df, dimension):
        """Calculate KPIs grouped by a dimension (city, channel, category)."""
        try:
            merged = sales_df.copy()
            
            # Find columns
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
            
            # Merge with stores
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
            
            # Merge with products
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
            
            # Set defaults
            if '_cost' not in merged.columns:
                merged['_cost'] = 0
            if 'category' not in merged.columns:
                merged['category'] = 'Unknown'
            if 'city' not in merged.columns:
                merged['city'] = 'Unknown'
            if 'channel' not in merged.columns:
                merged['channel'] = 'Unknown'
            
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
            
            merged['revenue'] = merged['_qty'] * merged['_price']
            merged['profit'] = merged['_qty'] * (merged['_price'] - merged['_cost'])
            
            # Set order_id for counting
            if order_col:
                merged['_order_id'] = merged[order_col]
            else:
                merged['_order_id'] = range(len(merged))
            
            # Group by dimension
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
        """Calculate daily performance trends."""
        try:
            merged = sales_df.copy()
            
            # Find columns
            sku_col_sales = self._get_sku_column(sales_df)
            sku_col_products = self._get_sku_column(products_df)
            cost_col = self._get_cost_column(products_df)
            price_col = self._get_price_column(sales_df)
            qty_col = self._get_qty_column(sales_df)
            date_col = self._get_date_column(sales_df)
            order_col = self._get_order_column(sales_df)
            
            # Merge with products for cost
            if sku_col_sales and sku_col_products and cost_col:
                products_subset = products_df[[sku_col_products, cost_col]].copy()
                products_subset.columns = ['_sku', '_cost']
                merged['_sku'] = merged[sku_col_sales]
                merged = merged.merge(products_subset, on='_sku', how='left')
                merged['_cost'] = merged['_cost'].fillna(0)
            else:
                merged['_cost'] = 0
            
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
            
            merged['revenue'] = merged['_qty'] * merged['_price']
            merged['profit'] = merged['_qty'] * (merged['_price'] - merged['_cost'])
            
            # Parse date
            if date_col:
                merged['date'] = pd.to_datetime(merged[date_col], errors='coerce').dt.date
            else:
                # No date column found - create dummy dates
                merged['date'] = pd.date_range(end=pd.Timestamp.today(), periods=len(merged), freq='H').date
            
            merged = merged.dropna(subset=['date'])
            
            if len(merged) == 0:
                return pd.DataFrame(columns=['date', 'revenue', 'profit', 'orders', 'units'])
            
            # Group by date
            daily = merged.groupby('date').agg({
                'revenue': 'sum',
                'profit': 'sum',
                '_qty': 'sum'
            }).reset_index()
            
            # Count orders
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
        """Calculate stockout risk metrics."""
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
            zero_stock = len(inventory_df[inventory_df['_stock'] == 0])
            low_stock = len(inventory_df[inventory_df['_stock'] <= inventory_df['_reorder']])
            
            return {
                'total_items': total_items,
                'zero_stock': zero_stock,
                'low_stock': low_stock,
                'stockout_risk_pct': (low_stock / total_items * 100) if total_items > 0 else 0
            }
        except Exception as e:
            print(f"Error in calculate_stockout_risk: {e}")
            return {
                'total_items': 0,
                'zero_stock': 0,
                'low_stock': 0,
                'stockout_risk_pct': 0
            }
    
    def simulate_campaign(self, sales_df, stores_df, products_df,
                          discount_pct=10, promo_budget=10000, margin_floor=15,
                          city='All', channel='All', category='All', campaign_days=7):
        """Simulate a promotional campaign."""
        try:
            merged = sales_df.copy()
            
            # Find columns
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
            
            # Merge with stores
            if store_col_sales and store_col_stores:
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
            if sku_col_sales and sku_col_products:
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
            if city_col and city_col not in merged.columns:
                merged[city_col] = 'Unknown'
            if channel_col and channel_col not in merged.columns:
                merged[channel_col] = 'Unknown'
            
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
            
            # Filter by targeting
            if city != 'All' and city_col and city_col in merged.columns:
                merged = merged[merged[city_col] == city]
            if channel != 'All' and channel_col and channel_col in merged.columns:
                merged = merged[merged[channel_col] == channel]
            if category != 'All' and 'category' in merged.columns:
                merged = merged[merged['category'] == category]
            
            if len(merged) == 0:
                return {'outputs': None, 'comparison': None, 'warnings': ['No data matches filters']}
            
            merged['revenue'] = merged['_qty'] * merged['_price']
            merged['profit'] = merged['_qty'] * (merged['_price'] - merged['_cost'])
            
            data_days = 30
            baseline_revenue = merged['revenue'].sum() / data_days * campaign_days
            baseline_profit = merged['profit'].sum() / data_days * campaign_days
            
            if order_col and order_col in merged.columns:
                baseline_orders = merged[order_col].nunique() / data_days * campaign_days
            else:
                baseline_orders = len(merged) / data_days * campaign_days
            
            baseline_units = merged['_qty'].sum() / data_days * campaign_days
            
            elasticity = self.category_elasticity.get(category, self.default_elasticity) if category != 'All' else self.default_elasticity
            
            demand_lift_pct = discount_pct * elasticity
            
            expected_units = baseline_units * (1 + demand_lift_pct / 100)
            avg_price = merged['_price'].mean()
            avg_cost = merged['_cost'].mean()
            
            discounted_price = avg_price * (1 - discount_pct / 100)
            expected_revenue = expected_units * discounted_price
            
            promo_cost = min(promo_budget, expected_revenue * 0.1)
            fulfillment_cost = expected_units * 2
            cogs = expected_units * avg_cost
            
            expected_gross_profit = expected_revenue - cogs
            expected_net_profit = expected_gross_profit - promo_cost - fulfillment_cost
            expected_margin_pct = (expected_net_profit / expected_revenue * 100) if expected_revenue > 0 else 0
            
            total_investment = promo_cost + fulfillment_cost
            roi_pct = ((expected_net_profit - baseline_profit) / total_investment * 100) if total_investment > 0 else 0
            
            warnings = []
            if expected_margin_pct < margin_floor:
                warnings.append(f"Margin ({expected_margin_pct:.1f}%) below floor ({margin_floor}%)")
            if roi_pct < 0:
                warnings.append(f"Negative ROI ({roi_pct:.1f}%)")
            if discount_pct > 30:
                warnings.append("High discount may erode brand value")
            
            outputs = {
                'expected_revenue': expected_revenue,
                'expected_orders': int(baseline_orders * (1 + demand_lift_pct / 100)),
                'expected_units': expected_units,
                'expected_net_profit': expected_net_profit,
                'expected_margin_pct': expected_margin_pct,
                'demand_lift_pct': demand_lift_pct,
                'roi_pct': roi_pct,
                'promo_cost': promo_cost,
                'fulfillment_cost': fulfillment_cost
            }
            
            comparison = {
                'baseline_revenue': baseline_revenue,
                'baseline_profit': baseline_profit,
                'baseline_orders': int(baseline_orders),
                'revenue_change_pct': ((expected_revenue - baseline_revenue) / baseline_revenue * 100) if baseline_revenue > 0 else 0,
                'profit_change_pct': ((expected_net_profit - baseline_profit) / abs(baseline_profit) * 100) if baseline_profit != 0 else 0,
                'order_change_pct': demand_lift_pct
            }
            
            return {'outputs': outputs, 'comparison': comparison, 'warnings': warnings}
            
        except Exception as e:
            print(f"Error in simulate_campaign: {e}")
            return {'outputs': None, 'comparison': None, 'warnings': [f'Error: {str(e)}']}
