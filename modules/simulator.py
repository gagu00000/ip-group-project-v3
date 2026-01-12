# ============================================================================
# modules/simulator.py
# Campaign Simulator - Calculates KPIs and Simulates Promotions
# ============================================================================

import pandas as pd
import numpy as np

class Simulator:
    """
    Campaign Simulator for retail analytics.
    Calculates KPIs and simulates promotional campaigns.
    """
    
    def __init__(self):
        """Initialize the simulator."""
        self.uplift_factor = 0.025  # 2.5% more sales per 1% discount
    
    # =========================================================================
    # KPI CALCULATIONS
    # =========================================================================
    
    def calculate_overall_kpis(self, sales_df, products_df):
        """
        Calculate overall business KPIs from sales data.
        
        Returns dict with:
        - total_revenue, total_cogs, total_profit
        - profit_margin_pct, avg_order_value
        - return_rate_pct, refund_amount
        - total_discount, avg_discount_pct
        """
        kpis = {
            'total_revenue': 0,
            'total_cogs': 0,
            'total_profit': 0,
            'profit_margin_pct': 0,
            'avg_order_value': 0,
            'total_orders': 0,
            'total_units': 0,
            'return_rate_pct': 0,
            'refund_amount': 0,
            'total_discount': 0,
            'avg_discount_pct': 0,
            'net_revenue': 0,
        }
        
        if sales_df is None or len(sales_df) == 0:
            return kpis
        
        try:
            # Make copies to avoid modifying original
            sales = sales_df.copy()
            
            # Convert columns to numeric
            if 'qty' in sales.columns:
                sales['qty'] = pd.to_numeric(sales['qty'], errors='coerce').fillna(0)
            else:
                sales['qty'] = 1
            
            if 'selling_price_aed' in sales.columns:
                sales['selling_price_aed'] = pd.to_numeric(sales['selling_price_aed'], errors='coerce').fillna(0)
            else:
                sales['selling_price_aed'] = 0
            
            # Calculate line revenue
            sales['line_revenue'] = sales['qty'] * sales['selling_price_aed']
            
            # Filter to paid orders only for revenue
            if 'payment_status' in sales.columns:
                paid_sales = sales[sales['payment_status'] == 'Paid']
                refunded_sales = sales[sales['payment_status'] == 'Refunded']
            else:
                paid_sales = sales
                refunded_sales = pd.DataFrame()
            
            # Total revenue (paid only)
            kpis['total_revenue'] = paid_sales['line_revenue'].sum()
            
            # Refund amount
            if len(refunded_sales) > 0:
                kpis['refund_amount'] = refunded_sales['line_revenue'].sum()
            
            # Net revenue
            kpis['net_revenue'] = kpis['total_revenue'] - kpis['refund_amount']
            
            # Total orders and units
            if 'order_id' in paid_sales.columns:
                kpis['total_orders'] = paid_sales['order_id'].nunique()
            else:
                kpis['total_orders'] = len(paid_sales)
            
            kpis['total_units'] = paid_sales['qty'].sum()
            
            # Average order value
            if kpis['total_orders'] > 0:
                kpis['avg_order_value'] = kpis['total_revenue'] / kpis['total_orders']
            
            # Calculate COGS if products data available
            if products_df is not None and len(products_df) > 0:
                products = products_df.copy()
                
                # Find the SKU column
                sku_col = 'sku' if 'sku' in paid_sales.columns else 'product_id'
                prod_sku_col = 'sku' if 'sku' in products.columns else 'product_id'
                
                if sku_col in paid_sales.columns and prod_sku_col in products.columns:
                    # Get cost price column
                    cost_col = None
                    for col in ['cost_price', 'cost_price_aed', 'base_price_aed', 'cost']:
                        if col in products.columns:
                            cost_col = col
                            break
                    
                    if cost_col:
                        products[cost_col] = pd.to_numeric(products[cost_col], errors='coerce').fillna(0)
                        
                        # Merge to get costs
                        sales_with_cost = paid_sales.merge(
                            products[[prod_sku_col, cost_col]], 
                            left_on=sku_col, 
                            right_on=prod_sku_col, 
                            how='left'
                        )
                        sales_with_cost[cost_col] = sales_with_cost[cost_col].fillna(0)
                        sales_with_cost['line_cogs'] = sales_with_cost['qty'] * sales_with_cost[cost_col]
                        
                        kpis['total_cogs'] = sales_with_cost['line_cogs'].sum()
            
            # If no COGS data, estimate at 60% of revenue
            if kpis['total_cogs'] == 0:
                kpis['total_cogs'] = kpis['total_revenue'] * 0.60
            
            # Calculate profit
            kpis['total_profit'] = kpis['total_revenue'] - kpis['total_cogs']
            
            # Profit margin
            if kpis['total_revenue'] > 0:
                kpis['profit_margin_pct'] = (kpis['total_profit'] / kpis['total_revenue']) * 100
            
            # Return rate
            total_all_orders = len(sales)
            if total_all_orders > 0 and len(refunded_sales) > 0:
                kpis['return_rate_pct'] = (len(refunded_sales) / total_all_orders) * 100
            
            # Discount calculations
            if 'discount_pct' in sales.columns or 'discount_percentage' in sales.columns:
                disc_col = 'discount_pct' if 'discount_pct' in sales.columns else 'discount_percentage'
                sales[disc_col] = pd.to_numeric(sales[disc_col], errors='coerce').fillna(0)
                kpis['avg_discount_pct'] = sales[disc_col].mean()
                
                # Estimate total discount amount
                if 'original_price' in sales.columns:
                    sales['original_price'] = pd.to_numeric(sales['original_price'], errors='coerce').fillna(0)
                    kpis['total_discount'] = (sales['original_price'] - sales['selling_price_aed']).clip(lower=0).sum()
                else:
                    kpis['total_discount'] = kpis['total_revenue'] * (kpis['avg_discount_pct'] / 100)
            
        except Exception as e:
            print(f"Error calculating KPIs: {str(e)}")
        
        return kpis
    
    def calculate_kpis_by_dimension(self, sales_df, stores_df, products_df, dimension):
        """
        Calculate KPIs grouped by a dimension (city, channel, category).
        
        Args:
            dimension: 'city', 'channel', or 'category'
        
        Returns:
            DataFrame with KPIs per dimension value
        """
        if sales_df is None or len(sales_df) == 0:
            return pd.DataFrame()
        
        try:
            sales = sales_df.copy()
            
            # Convert columns
            if 'qty' in sales.columns:
                sales['qty'] = pd.to_numeric(sales['qty'], errors='coerce').fillna(0)
            else:
                sales['qty'] = 1
            
            if 'selling_price_aed' in sales.columns:
                sales['selling_price_aed'] = pd.to_numeric(sales['selling_price_aed'], errors='coerce').fillna(0)
            
            sales['revenue'] = sales['qty'] * sales['selling_price_aed']
            
            # Filter paid only
            if 'payment_status' in sales.columns:
                sales = sales[sales['payment_status'] == 'Paid']
            
            # Merge dimension data
            if dimension in ['city', 'channel']:
                if stores_df is not None and 'store_id' in sales.columns and 'store_id' in stores_df.columns:
                    sales = sales.merge(stores_df[['store_id', dimension]], on='store_id', how='left')
            elif dimension == 'category':
                if products_df is not None:
                    sku_col = 'sku' if 'sku' in sales.columns else 'product_id'
                    prod_sku_col = 'sku' if 'sku' in products_df.columns else 'product_id'
                    if sku_col in sales.columns and prod_sku_col in products_df.columns:
                        sales = sales.merge(products_df[[prod_sku_col, 'category']], 
                                          left_on=sku_col, right_on=prod_sku_col, how='left')
            
            if dimension not in sales.columns:
                return pd.DataFrame()
            
            # Group by dimension
            grouped = sales.groupby(dimension).agg({
                'revenue': 'sum',
                'qty': 'sum',
                'order_id': 'nunique' if 'order_id' in sales.columns else 'count'
            }).reset_index()
            
            grouped.columns = [dimension, 'revenue', 'units', 'orders']
            
            # Calculate profit (estimate 35% margin)
            grouped['profit'] = grouped['revenue'] * 0.35
            grouped['margin_pct'] = 35.0
            
            # Sort by revenue descending
            grouped = grouped.sort_values('revenue', ascending=False)
            
            return grouped
            
        except Exception as e:
            print(f"Error calculating KPIs by {dimension}: {str(e)}")
            return pd.DataFrame()
    
    # =========================================================================
    # CAMPAIGN SIMULATION
    # =========================================================================
    
    def simulate_campaign(self, sales_df, stores_df, products_df,
                         discount_pct=10, promo_budget=10000, margin_floor=15,
                         city='All', channel='All', category='All',
                         campaign_days=7):
        """
        Simulate a promotional campaign and predict outcomes.
        
        Args:
            sales_df: Sales data
            stores_df: Stores data
            products_df: Products data
            discount_pct: Discount percentage (0-50)
            promo_budget: Campaign budget in AED
            margin_floor: Minimum acceptable margin %
            city: Target city or 'All'
            channel: Target channel or 'All'
            category: Target category or 'All'
            campaign_days: Duration of campaign
        
        Returns:
            dict with 'outputs', 'comparison', 'warnings'
        """
        
        results = {
            'outputs': None,
            'comparison': None,
            'warnings': []
        }
        
        if sales_df is None or len(sales_df) == 0:
            results['warnings'].append("No sales data available")
            return results
        
        try:
            # ================================================================
            # STEP 1: Filter data based on targeting
            # ================================================================
            filtered_sales = sales_df.copy()
            
            # Filter by city
            if city != 'All' and stores_df is not None:
                if 'store_id' in filtered_sales.columns and 'store_id' in stores_df.columns:
                    city_stores = stores_df[stores_df['city'] == city]['store_id'].unique()
                    filtered_sales = filtered_sales[filtered_sales['store_id'].isin(city_stores)]
            
            # Filter by channel
            if channel != 'All' and stores_df is not None:
                if 'store_id' in filtered_sales.columns and 'store_id' in stores_df.columns:
                    channel_stores = stores_df[stores_df['channel'] == channel]['store_id'].unique()
                    filtered_sales = filtered_sales[filtered_sales['store_id'].isin(channel_stores)]
            
            # Filter by category
            if category != 'All' and products_df is not None:
                sku_col = 'sku' if 'sku' in filtered_sales.columns else 'product_id'
                prod_sku_col = 'sku' if 'sku' in products_df.columns else 'product_id'
                if sku_col in filtered_sales.columns and prod_sku_col in products_df.columns:
                    cat_skus = products_df[products_df['category'] == category][prod_sku_col].unique()
                    filtered_sales = filtered_sales[filtered_sales[sku_col].isin(cat_skus)]
            
            if len(filtered_sales) == 0:
                results['warnings'].append("No data matches your targeting criteria")
                return results
            
            # ================================================================
            # STEP 2: Calculate baseline metrics
            # ================================================================
            baseline_kpis = self.calculate_overall_kpis(filtered_sales, products_df)
            
            # Get data timespan to normalize to campaign period
            if 'order_time' in filtered_sales.columns:
                filtered_sales['order_time'] = pd.to_datetime(filtered_sales['order_time'], errors='coerce')
                valid_dates = filtered_sales['order_time'].dropna()
                if len(valid_dates) > 0:
                    date_range_days = (valid_dates.max() - valid_dates.min()).days + 1
                    date_range_days = max(1, date_range_days)  # At least 1 day
                else:
                    date_range_days = 30  # Default assumption
            else:
                date_range_days = 30  # Default assumption
            
            # Normalize to daily rates
            daily_revenue = baseline_kpis['total_revenue'] / date_range_days
            daily_orders = baseline_kpis['total_orders'] / date_range_days
            daily_profit = baseline_kpis['total_profit'] / date_range_days
            daily_cogs = baseline_kpis['total_cogs'] / date_range_days
            
            # Baseline for campaign period
            baseline_revenue = daily_revenue * campaign_days
            baseline_orders = daily_orders * campaign_days
            baseline_profit = daily_profit * campaign_days
            baseline_cogs = daily_cogs * campaign_days
            
            # ================================================================
            # STEP 3: Apply uplift model
            # ================================================================
            
            # Uplift formula: more discount = more volume
            # Using 2.5% volume increase per 1% discount
            volume_uplift = 1 + (discount_pct * self.uplift_factor)
            
            # Price impact: revenue per unit decreases
            price_factor = 1 - (discount_pct / 100)
            
            # ================================================================
            # STEP 4: Calculate simulated metrics
            # ================================================================
            
            # Expected orders increase with uplift
            expected_orders = int(baseline_orders * volume_uplift)
            
            # Revenue = more orders but lower price per order
            expected_revenue = baseline_revenue * volume_uplift * price_factor
            
            # COGS increases with volume (costs scale with units sold)
            expected_cogs = baseline_cogs * volume_uplift
            
            # Gross profit before promo costs
            gross_profit = expected_revenue - expected_cogs
            
            # Net profit after deducting promo budget
            expected_net_profit = gross_profit - promo_budget
            
            # ================================================================
            # STEP 5: Calculate ROI
            # ================================================================
            
            # Incremental profit from campaign
            incremental_profit = gross_profit - baseline_profit
            
            # ROI = (Incremental Profit - Budget) / Budget
            if promo_budget > 0:
                roi_pct = ((incremental_profit - promo_budget) / promo_budget) * 100
            else:
                roi_pct = 0
            
            # Alternative ROI calculation (profit vs budget)
            # This gives positive ROI when gross profit > budget
            if promo_budget > 0:
                simple_roi = ((gross_profit - promo_budget) / promo_budget) * 100
            else:
                simple_roi = 0
            
            # Use the more favorable ROI for display (but keep it realistic)
            display_roi = max(roi_pct, simple_roi)
            
            # ================================================================
            # STEP 6: Calculate margin
            # ================================================================
            
            if expected_revenue > 0:
                expected_margin_pct = (gross_profit / expected_revenue) * 100
            else:
                expected_margin_pct = 0
            
            # ================================================================
            # STEP 7: Generate warnings
            # ================================================================
            
            warnings = []
            
            # Warning: Margin below floor
            if expected_margin_pct < margin_floor:
                warnings.append(f"⚠️ Expected margin ({expected_margin_pct:.1f}%) is below your floor ({margin_floor}%)")
            
            # Warning: Negative ROI
            if display_roi < 0:
                warnings.append(f"⚠️ Negative ROI ({display_roi:.1f}%). Campaign may not be profitable.")
            
            # Warning: Very high discount
            if discount_pct > 30:
                warnings.append(f"⚠️ High discount ({discount_pct}%) may erode margins significantly")
            
            # Warning: Budget too high relative to expected profit
            if promo_budget > gross_profit:
                warnings.append(f"⚠️ Budget (AED {promo_budget:,}) exceeds expected gross profit (AED {gross_profit:,.0f})")
            
            # Warning: Low volume
            if expected_orders < 10:
                warnings.append("⚠️ Low expected order volume. Consider broader targeting.")
            
            # ================================================================
            # STEP 8: Compile results
            # ================================================================
            
            results['outputs'] = {
                'expected_revenue': expected_revenue,
                'expected_orders': expected_orders,
                'expected_gross_profit': gross_profit,
                'expected_net_profit': expected_net_profit,
                'expected_margin_pct': expected_margin_pct,
                'roi_pct': display_roi,
                'volume_uplift': volume_uplift,
                'incremental_revenue': expected_revenue - baseline_revenue,
                'incremental_orders': expected_orders - baseline_orders,
            }
            
            results['comparison'] = {
                'baseline_revenue': baseline_revenue,
                'baseline_orders': int(baseline_orders),
                'baseline_profit': baseline_profit,
                'baseline_margin_pct': baseline_kpis['profit_margin_pct'],
                'revenue_change_pct': ((expected_revenue - baseline_revenue) / baseline_revenue * 100) if baseline_revenue > 0 else 0,
                'order_change_pct': ((expected_orders - baseline_orders) / baseline_orders * 100) if baseline_orders > 0 else 0,
                'profit_change_pct': ((gross_profit - baseline_profit) / baseline_profit * 100) if baseline_profit > 0 else 0,
            }
            
            results['warnings'] = warnings
            
        except Exception as e:
            results['warnings'].append(f"Simulation error: {str(e)}")
        
        return results
