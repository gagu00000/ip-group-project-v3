
"""
Data Cleaner Module - UAE Pulse Simulator
Handles validation, cleaning, and issue logging for all datasets.

DROP Logic:
- stores.city NOT IN [Dubai, Abu Dhabi, Sharjah]
- stores.channel NOT IN [App, Web, Marketplace]
- stores.fulfillment_type NOT IN [Own, 3PL]
- products.launch_flag NOT IN [New, Regular]
- sales.payment_status NOT IN [Paid, Failed, Refunded]
- sales.timestamp unparseable/corrupted

FIX Logic:
- sales.return_flag invalid → False
- sales.qty outlier → cap at 95th percentile
- sales.selling_price outlier → cap at 95th percentile
- products.unit_cost > base_price → impute
- products.unit_cost missing → impute median
- sales.discount_pct missing → 0
- inventory.stock_on_hand negative → 0
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os


class DataCleaner:
    """Clean and validate all datasets with comprehensive issue logging."""
    
    # Valid values for strict validation
    VALID_CITIES = ["Dubai", "Abu Dhabi", "Sharjah"]
    VALID_CHANNELS = ["App", "Web", "Marketplace"]
    VALID_FULFILLMENT = ["Own", "3PL"]
    VALID_LAUNCH_FLAG = ["New", "Regular"]
    VALID_PAYMENT_STATUS = ["Paid", "Failed", "Refunded"]
    
    def __init__(self):
        """Initialize the cleaner."""
        self.issues = []
        self.stats = {
            'total_issues_fixed': 0,
            'missing_values_fixed': 0,
            'duplicates_removed': 0,
            'outliers_fixed': 0,
            'invalid_dropped': 0,
            'text_standardized': 0
        }
        self.cleaning_report = {}
        self.text_mappings = self._load_text_mappings()
    
    def _load_text_mappings(self):
        """Load text mappings from config file."""
        mappings_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'text_mappings.json')
        try:
            if os.path.exists(mappings_path):
                with open(mappings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load text mappings: {e}")
        
        # Default mappings if file not found
        return {
            "cities": {},
            "channels": {},
            "categories": {},
            "standard_values": {
                "cities": ["Dubai", "Abu Dhabi", "Sharjah"],
                "channels": ["App", "Web", "Marketplace"]
            }
        }
    
    def _log_issue(self, table, record_id, issue_type, issue_detail, action_taken):
        """Log an issue with standardized format."""
        self.issues.append({
            'table': table,
            'record_identifier': record_id,
            'issue_type': issue_type,
            'issue_detail': issue_detail,
            'action_taken': action_taken
        })
        self.stats['total_issues_fixed'] += 1
    
    def _map_text_value(self, value, mappings, field_type):
        """Map a text value to its standardized form."""
        if pd.isna(value) or value is None:
            return value
        
        value_str = str(value).strip()
        
        # Direct mapping lookup
        if value_str in mappings:
            self.stats['text_standardized'] += 1
            return mappings[value_str]
        
        # Case-insensitive lookup
        value_lower = value_str.lower()
        for key, mapped_value in mappings.items():
            if key.lower() == value_lower:
                self.stats['text_standardized'] += 1
                return mapped_value
        
        # Title case for standard values
        value_title = value_str.title()
        standard_values = self.text_mappings.get('standard_values', {}).get(field_type + 's', [])
        if value_title in standard_values:
            self.stats['text_standardized'] += 1
            return value_title
        
        return value_str
    
    def clean_all(self, products_df, stores_df, sales_df, inventory_df):
        """Clean all dataframes and return cleaned versions."""
        self.issues = []
        self.stats = {
            'total_issues_fixed': 0,
            'missing_values_fixed': 0,
            'duplicates_removed': 0,
            'outliers_fixed': 0,
            'invalid_dropped': 0,
            'text_standardized': 0
        }
        self.cleaning_report = {}
        
        # Clean in order (stores/products first, then sales/inventory)
        clean_products = self._clean_products(products_df.copy())
        clean_stores = self._clean_stores(stores_df.copy())
        clean_sales = self._clean_sales(sales_df.copy(), clean_products, clean_stores)
        clean_inventory = self._clean_inventory(inventory_df.copy(), clean_products, clean_stores)
        
        # Final foreign key validation
        clean_sales = self._validate_foreign_keys_sales(clean_sales, clean_products, clean_stores)
        clean_inventory = self._validate_foreign_keys_inventory(clean_inventory, clean_products, clean_stores)
        
        return clean_products, clean_stores, clean_sales, clean_inventory
    
    def _clean_products(self, df):
        """Clean products dataframe."""
        original_count = len(df)
        
        # Standardize column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Handle product_id/sku column
        id_cols = ['product_id', 'productid', 'sku', 'SKU']
        for col in id_cols:
            if col.lower() in [c.lower() for c in df.columns]:
                actual_col = [c for c in df.columns if c.lower() == col.lower()][0]
                if actual_col != 'sku':
                    df = df.rename(columns={actual_col: 'sku'})
                break
        
        # Clean text columns
        text_cols = ['category', 'brand', 'product_name', 'launch_flag']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Map category variations
        if 'category' in df.columns:
            category_mappings = self.text_mappings.get('categories', {})
            df['category'] = df['category'].apply(lambda x: self._map_text_value(x, category_mappings, 'category'))
        
        # Validate launch_flag - DROP if invalid
        if 'launch_flag' in df.columns:
            # First try to map common variations
            launch_mappings = {
                'new': 'New', 'NEW': 'New', 'N': 'New', 'n': 'New',
                'regular': 'Regular', 'REGULAR': 'Regular', 'R': 'Regular', 'r': 'Regular',
                'Reg': 'Regular', 'reg': 'Regular'
            }
            df['launch_flag'] = df['launch_flag'].apply(
                lambda x: launch_mappings.get(str(x).strip(), str(x).strip().title()) if pd.notna(x) else 'Regular'
            )
            
            # Drop invalid launch_flag
            invalid_mask = ~df['launch_flag'].isin(self.VALID_LAUNCH_FLAG)
            invalid_count = invalid_mask.sum()
            
            if invalid_count > 0:
                invalid_values = df.loc[invalid_mask, 'launch_flag'].unique()
                for val in invalid_values:
                    val_count = (df['launch_flag'] == val).sum()
                    self._log_issue('products', f'launch_flag={val}', 'INVALID_LAUNCH_FLAG',
                                  f"launch_flag '{val}' not in {self.VALID_LAUNCH_FLAG}",
                                  f'Dropped {val_count} rows')
                
                df = df[~invalid_mask].copy()
                self.stats['invalid_dropped'] += invalid_count
        
        # Handle missing unit_cost_aed - IMPUTE
        cost_cols = ['unit_cost_aed', 'unit_cost', 'cost', 'cost_aed']
        cost_col = None
        for col in cost_cols:
            if col in df.columns:
                cost_col = col
                break
        
        price_cols = ['base_price_aed', 'base_price', 'price', 'price_aed', 'selling_price', 'selling_price_aed']
        price_col = None
        for col in price_cols:
            if col in df.columns:
                price_col = col
                break
        
        if cost_col:
            # Fix missing cost
            missing_cost = df[cost_col].isna().sum()
            if missing_cost > 0:
                if price_col and price_col in df.columns:
                    # Impute as 60% of price
                    median_ratio = 0.6
                    df.loc[df[cost_col].isna(), cost_col] = df.loc[df[cost_col].isna(), price_col] * median_ratio
                else:
                    # Impute with median
                    median_cost = df[cost_col].median()
                    df[cost_col] = df[cost_col].fillna(median_cost)
                
                self._log_issue('products', f'{missing_cost} rows', 'MISSING_UNIT_COST',
                              f'{missing_cost} products missing unit_cost_aed',
                              'Imputed based on price or median')
                self.stats['missing_values_fixed'] += missing_cost
            
            # Fix unit_cost > base_price
            if price_col and price_col in df.columns:
                invalid_cost_mask = df[cost_col] > df[price_col]
                invalid_cost_count = invalid_cost_mask.sum()
                if invalid_cost_count > 0:
                    # Set cost to 60% of price
                    df.loc[invalid_cost_mask, cost_col] = df.loc[invalid_cost_mask, price_col] * 0.6
                    self._log_issue('products', f'{invalid_cost_count} rows', 'COST_EXCEEDS_PRICE',
                                  f'{invalid_cost_count} products have unit_cost > base_price',
                                  'Set cost to 60% of price')
                    self.stats['outliers_fixed'] += invalid_cost_count
        
        # Remove duplicates
        if 'sku' in df.columns:
            before_dedup = len(df)
            df = df.drop_duplicates(subset=['sku'], keep='first')
            dups_removed = before_dedup - len(df)
            if dups_removed > 0:
                self.stats['duplicates_removed'] += dups_removed
                self._log_issue('products', f'{dups_removed} rows', 'DUPLICATE_SKU',
                              f'{dups_removed} duplicate SKUs found', 'Kept first occurrence')
        
        # Report
        self.cleaning_report['products'] = {
            'original_rows': original_count,
            'final_rows': len(df),
            'dropped_rows': original_count - len(df)
        }
        
        return df
    
    def _clean_stores(self, df):
        """Clean stores dataframe."""
        original_count = len(df)
        
        # Standardize column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Handle store_id column
        id_cols = ['store_id', 'storeid', 'store']
        for col in id_cols:
            if col in df.columns and 'store_id' not in df.columns:
                df = df.rename(columns={col: 'store_id'})
                break
        
        # Clean text columns
        text_cols = ['city', 'channel', 'store_name', 'fulfillment_type']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # ===== CITY VALIDATION - DROP IF INVALID =====
        if 'city' in df.columns:
            # Map variations first
            city_mappings = self.text_mappings.get('cities', {})
            df['city'] = df['city'].apply(lambda x: self._map_text_value(x, city_mappings, 'city'))
            
            # Drop invalid cities
            invalid_mask = ~df['city'].isin(self.VALID_CITIES)
            invalid_count = invalid_mask.sum()
            
            if invalid_count > 0:
                invalid_values = df.loc[invalid_mask, 'city'].unique()
                for val in invalid_values:
                    val_count = (df['city'] == val).sum()
                    self._log_issue('stores', f'city={val}', 'INVALID_CITY',
                                  f"City '{val}' not in {self.VALID_CITIES}",
                                  f'Dropped {val_count} rows')
                
                df = df[~invalid_mask].copy()
                self.stats['invalid_dropped'] += invalid_count
        
        # ===== CHANNEL VALIDATION - DROP IF INVALID =====
        if 'channel' in df.columns:
            # Map variations first
            channel_mappings = self.text_mappings.get('channels', {})
            df['channel'] = df['channel'].apply(lambda x: self._map_text_value(x, channel_mappings, 'channel'))
            
            # Drop invalid channels
            invalid_mask = ~df['channel'].isin(self.VALID_CHANNELS)
            invalid_count = invalid_mask.sum()
            
            if invalid_count > 0:
                invalid_values = df.loc[invalid_mask, 'channel'].unique()
                for val in invalid_values:
                    val_count = (df['channel'] == val).sum()
                    self._log_issue('stores', f'channel={val}', 'INVALID_CHANNEL',
                                  f"Channel '{val}' not in {self.VALID_CHANNELS}",
                                  f'Dropped {val_count} rows')
                
                df = df[~invalid_mask].copy()
                self.stats['invalid_dropped'] += invalid_count
        
        # ===== FULFILLMENT_TYPE VALIDATION - DROP IF INVALID =====
        if 'fulfillment_type' in df.columns:
            # Map variations first
            fulfillment_mappings = {
                'own': 'Own', 'OWN': 'Own', 'self': 'Own', 'Self': 'Own',
                '3pl': '3PL', '3PL': '3PL', 'third party': '3PL', 'Third Party': '3PL',
                'thirdparty': '3PL', '3rd party': '3PL', '3rd Party': '3PL'
            }
            df['fulfillment_type'] = df['fulfillment_type'].apply(
                lambda x: fulfillment_mappings.get(str(x).strip(), str(x).strip()) if pd.notna(x) else x
            )
            
            # Drop invalid fulfillment_type
            invalid_mask = ~df['fulfillment_type'].isin(self.VALID_FULFILLMENT)
            invalid_count = invalid_mask.sum()
            
            if invalid_count > 0:
                invalid_values = df.loc[invalid_mask, 'fulfillment_type'].unique()
                for val in invalid_values:
                    val_count = (df['fulfillment_type'] == val).sum()
                    self._log_issue('stores', f'fulfillment_type={val}', 'INVALID_FULFILLMENT_TYPE',
                                  f"fulfillment_type '{val}' not in {self.VALID_FULFILLMENT}",
                                  f'Dropped {val_count} rows')
                
                df = df[~invalid_mask].copy()
                self.stats['invalid_dropped'] += invalid_count
        
        # Remove duplicates
        if 'store_id' in df.columns:
            before_dedup = len(df)
            df = df.drop_duplicates(subset=['store_id'], keep='first')
            dups_removed = before_dedup - len(df)
            if dups_removed > 0:
                self.stats['duplicates_removed'] += dups_removed
                self._log_issue('stores', f'{dups_removed} rows', 'DUPLICATE_STORE_ID',
                              f'{dups_removed} duplicate store_ids found', 'Kept first occurrence')
        
        # Report
        self.cleaning_report['stores'] = {
            'original_rows': original_count,
            'final_rows': len(df),
            'dropped_rows': original_count - len(df)
        }
        
        return df
    
    def _clean_sales(self, df, products_df, stores_df):
        """Clean sales dataframe."""
        original_count = len(df)
        
        # Standardize column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Handle column name variations
        column_mappings = {
            'order_id': ['order_id', 'orderid', 'transaction_id', 'txn_id'],
            'sku': ['sku', 'product_id', 'productid', 'SKU'],
            'store_id': ['store_id', 'storeid', 'store'],
            'qty': ['qty', 'quantity', 'units'],
            'order_time': ['order_time', 'order_date', 'date', 'timestamp', 'transaction_date'],
            'selling_price_aed': ['selling_price_aed', 'selling_price', 'price', 'amount'],
            'discount_pct': ['discount_pct', 'discount', 'discount_percent'],
            'payment_status': ['payment_status', 'status', 'payment'],
            'return_flag': ['return_flag', 'returned', 'is_returned']
        }
        
        for standard_name, variations in column_mappings.items():
            for var in variations:
                if var in df.columns and standard_name not in df.columns:
                    df = df.rename(columns={var: standard_name})
                    break
        
        # ===== TIMESTAMP VALIDATION - DROP IF CORRUPTED =====
        if 'order_time' in df.columns:
            original_timestamps = len(df)
            
            def parse_timestamp(x):
                if pd.isna(x):
                    return pd.NaT
                try:
                    return pd.to_datetime(x, format='mixed')
                except:
                    return pd.NaT
            
            df['order_time'] = df['order_time'].apply(parse_timestamp)
            
            # Drop NaT (unparseable timestamps)
            invalid_timestamps = df['order_time'].isna().sum()
            if invalid_timestamps > 0:
                self._log_issue('sales', f'{invalid_timestamps} rows', 'INVALID_TIMESTAMP',
                              f'{invalid_timestamps} orders have corrupted/unparseable timestamps',
                              'Dropped rows')
                df = df[df['order_time'].notna()].copy()
                self.stats['invalid_dropped'] += invalid_timestamps
            
            # Drop dates outside valid range (2020-2030)
            if len(df) > 0:
                out_of_range = ((df['order_time'].dt.year < 2020) | (df['order_time'].dt.year > 2030)).sum()
                if out_of_range > 0:
                    self._log_issue('sales', f'{out_of_range} rows', 'OUT_OF_RANGE_DATE',
                                  f'{out_of_range} orders have dates outside valid range (2020-2030)',
                                  'Dropped rows')
                    df = df[(df['order_time'].dt.year >= 2020) & (df['order_time'].dt.year <= 2030)].copy()
                    self.stats['invalid_dropped'] += out_of_range
        
        # ===== PAYMENT_STATUS VALIDATION - DROP IF INVALID =====
        if 'payment_status' in df.columns:
            # Map variations first
            status_mappings = {
                'paid': 'Paid', 'PAID': 'Paid', 'P': 'Paid', 'p': 'Paid', 'completed': 'Paid',
                'failed': 'Failed', 'FAILED': 'Failed', 'F': 'Failed', 'f': 'Failed', 'failure': 'Failed',
                'refunded': 'Refunded', 'REFUNDED': 'Refunded', 'R': 'Refunded', 'r': 'Refunded', 'refund': 'Refunded'
            }
            df['payment_status'] = df['payment_status'].apply(
                lambda x: status_mappings.get(str(x).strip(), str(x).strip().title()) if pd.notna(x) else x
            )
            
            # Drop invalid payment_status
            invalid_mask = ~df['payment_status'].isin(self.VALID_PAYMENT_STATUS)
            invalid_count = invalid_mask.sum()
            
            if invalid_count > 0:
                invalid_values = df.loc[invalid_mask, 'payment_status'].unique()
                for val in invalid_values:
                    val_count = (df['payment_status'] == val).sum()
                    self._log_issue('sales', f'payment_status={val}', 'INVALID_PAYMENT_STATUS',
                                  f"payment_status '{val}' not in {self.VALID_PAYMENT_STATUS}",
                                  f'Dropped {val_count} rows')
                
                df = df[~invalid_mask].copy()
                self.stats['invalid_dropped'] += invalid_count
        
        # ===== RETURN_FLAG VALIDATION - FIX (not drop) =====
        if 'return_flag' in df.columns:
            def parse_return_flag(x):
                if pd.isna(x):
                    return False
                if isinstance(x, bool):
                    return x
                x_str = str(x).strip().lower()
                if x_str in ['true', '1', 'yes', 'y', 't']:
                    return True
                return False
            
            original_invalid = df['return_flag'].apply(lambda x: str(x).strip().lower() not in ['true', 'false', '1', '0', 'yes', 'no', 'y', 'n', 't', 'f', 'nan', 'none', '']).sum()
            df['return_flag'] = df['return_flag'].apply(parse_return_flag)
            
            if original_invalid > 0:
                self._log_issue('sales', f'{original_invalid} rows', 'INVALID_RETURN_FLAG',
                              f'{original_invalid} orders have invalid return_flag',
                              'Set to False')
                self.stats['missing_values_fixed'] += original_invalid
        
        # ===== MISSING DISCOUNT_PCT - FIX (set to 0) =====
        if 'discount_pct' in df.columns:
            missing_discount = df['discount_pct'].isna().sum()
            if missing_discount > 0:
                df['discount_pct'] = df['discount_pct'].fillna(0)
                self._log_issue('sales', f'{missing_discount} rows', 'MISSING_DISCOUNT',
                              f'{missing_discount} orders missing discount_pct',
                              'Set to 0')
                self.stats['missing_values_fixed'] += missing_discount
        
        # ===== QTY OUTLIERS - CAP (not drop) =====
        if 'qty' in df.columns:
            df['qty'] = pd.to_numeric(df['qty'], errors='coerce')
            
            # Fix negative qty
            neg_qty = (df['qty'] < 0).sum()
            if neg_qty > 0:
                df.loc[df['qty'] < 0, 'qty'] = 1
                self._log_issue('sales', f'{neg_qty} rows', 'NEGATIVE_QTY',
                              f'{neg_qty} orders have negative qty',
                              'Set to 1')
                self.stats['outliers_fixed'] += neg_qty
            
            # Cap high qty outliers at 95th percentile
            qty_95 = df['qty'].quantile(0.95)
            high_qty = (df['qty'] > qty_95 * 3).sum()  # 3x the 95th percentile
            if high_qty > 0:
                cap_value = qty_95 * 2
                df.loc[df['qty'] > qty_95 * 3, 'qty'] = cap_value
                self._log_issue('sales', f'{high_qty} rows', 'OUTLIER_QTY',
                              f'{high_qty} orders have extreme qty values',
                              f'Capped at {cap_value:.0f}')
                self.stats['outliers_fixed'] += high_qty
        
        # ===== PRICE OUTLIERS - CAP (not drop) =====
        if 'selling_price_aed' in df.columns:
            df['selling_price_aed'] = pd.to_numeric(df['selling_price_aed'], errors='coerce')
            
            # Fix negative price
            neg_price = (df['selling_price_aed'] < 0).sum()
            if neg_price > 0:
                median_price = df['selling_price_aed'].median()
                df.loc[df['selling_price_aed'] < 0, 'selling_price_aed'] = median_price
                self._log_issue('sales', f'{neg_price} rows', 'NEGATIVE_PRICE',
                              f'{neg_price} orders have negative price',
                              'Set to median')
                self.stats['outliers_fixed'] += neg_price
            
            # Cap high price outliers
            price_95 = df['selling_price_aed'].quantile(0.95)
            high_price = (df['selling_price_aed'] > price_95 * 5).sum()
            if high_price > 0:
                cap_value = price_95 * 3
                df.loc[df['selling_price_aed'] > price_95 * 5, 'selling_price_aed'] = cap_value
                self._log_issue('sales', f'{high_price} rows', 'OUTLIER_PRICE',
                              f'{high_price} orders have extreme price values',
                              f'Capped at {cap_value:.0f}')
                self.stats['outliers_fixed'] += high_price
        
        # ===== DUPLICATE ORDER_ID - KEEP LATEST =====
        if 'order_id' in df.columns:
            before_dedup = len(df)
            if 'order_time' in df.columns:
                df = df.sort_values('order_time', ascending=False)
            df = df.drop_duplicates(subset=['order_id'], keep='first')
            dups_removed = before_dedup - len(df)
            if dups_removed > 0:
                self.stats['duplicates_removed'] += dups_removed
                self._log_issue('sales', f'{dups_removed} rows', 'DUPLICATE_ORDER_ID',
                              f'{dups_removed} duplicate order_ids found',
                              'Kept latest by timestamp')
        
        # Report
        self.cleaning_report['sales'] = {
            'original_rows': original_count,
            'final_rows': len(df),
            'dropped_rows': original_count - len(df)
        }
        
        return df
    
    def _clean_inventory(self, df, products_df, stores_df):
        """Clean inventory dataframe."""
        original_count = len(df)
        
        # Standardize column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Handle column name variations
        column_mappings = {
            'sku': ['sku', 'product_id', 'productid', 'SKU'],
            'store_id': ['store_id', 'storeid', 'store'],
            'stock_on_hand': ['stock_on_hand', 'stock', 'inventory', 'qty', 'quantity', 'on_hand'],
            'snapshot_date': ['snapshot_date', 'date', 'as_of_date']
        }
        
        for standard_name, variations in column_mappings.items():
            for var in variations:
                if var in df.columns and standard_name not in df.columns:
                    df = df.rename(columns={var: standard_name})
                    break
        
        # ===== NEGATIVE STOCK - FIX (set to 0) =====
        if 'stock_on_hand' in df.columns:
            df['stock_on_hand'] = pd.to_numeric(df['stock_on_hand'], errors='coerce')
            
            neg_stock = (df['stock_on_hand'] < 0).sum()
            if neg_stock > 0:
                df.loc[df['stock_on_hand'] < 0, 'stock_on_hand'] = 0
                self._log_issue('inventory', f'{neg_stock} rows', 'NEGATIVE_STOCK',
                              f'{neg_stock} inventory records have negative stock',
                              'Set to 0')
                self.stats['outliers_fixed'] += neg_stock
            
            # Cap extreme stock values (like 9999)
            stock_95 = df['stock_on_hand'].quantile(0.95)
            extreme_stock = (df['stock_on_hand'] > stock_95 * 5).sum()
            if extreme_stock > 0:
                cap_value = stock_95 * 3
                df.loc[df['stock_on_hand'] > stock_95 * 5, 'stock_on_hand'] = cap_value
                self._log_issue('inventory', f'{extreme_stock} rows', 'EXTREME_STOCK',
                              f'{extreme_stock} inventory records have extreme stock values',
                              f'Capped at {cap_value:.0f}')
                self.stats['outliers_fixed'] += extreme_stock
        
        # Handle missing values
        if 'reorder_point' in df.columns:
            missing = df['reorder_point'].isna().sum()
            if missing > 0:
                df['reorder_point'] = df['reorder_point'].fillna(10)
                self._log_issue('inventory', f'{missing} rows', 'MISSING_REORDER_POINT',
                              f'{missing} records missing reorder_point',
                              'Set to 10')
                self.stats['missing_values_fixed'] += missing
        
        if 'lead_time_days' in df.columns:
            missing = df['lead_time_days'].isna().sum()
            if missing > 0:
                df['lead_time_days'] = df['lead_time_days'].fillna(3)
                self._log_issue('inventory', f'{missing} rows', 'MISSING_LEAD_TIME',
                              f'{missing} records missing lead_time_days',
                              'Set to 3')
                self.stats['missing_values_fixed'] += missing
        
        # Remove duplicates
        key_cols = ['sku', 'store_id', 'snapshot_date']
        key_cols_present = [col for col in key_cols if col in df.columns]
        if len(key_cols_present) >= 2:
            before_dedup = len(df)
            df = df.drop_duplicates(subset=key_cols_present, keep='last')
            dups_removed = before_dedup - len(df)
            if dups_removed > 0:
                self.stats['duplicates_removed'] += dups_removed
                self._log_issue('inventory', f'{dups_removed} rows', 'DUPLICATE_INVENTORY',
                              f'{dups_removed} duplicate inventory records',
                              'Kept latest')
        
        # Report
        self.cleaning_report['inventory'] = {
            'original_rows': original_count,
            'final_rows': len(df),
            'dropped_rows': original_count - len(df)
        }
        
        return df
    
    def _validate_foreign_keys_sales(self, sales_df, products_df, stores_df):
        """Validate and drop sales with invalid foreign keys."""
        original_count = len(sales_df)
        
        # Check SKU exists in products
        if 'sku' in sales_df.columns and 'sku' in products_df.columns:
            valid_skus = set(products_df['sku'].unique())
            invalid_sku_mask = ~sales_df['sku'].isin(valid_skus)
            invalid_sku_count = invalid_sku_mask.sum()
            
            if invalid_sku_count > 0:
                self._log_issue('sales', f'{invalid_sku_count} rows', 'INVALID_SKU_FK',
                              f'{invalid_sku_count} sales reference non-existent SKUs',
                              'Dropped rows')
                sales_df = sales_df[~invalid_sku_mask].copy()
                self.stats['invalid_dropped'] += invalid_sku_count
        
        # Check store_id exists in stores
        if 'store_id' in sales_df.columns and 'store_id' in stores_df.columns:
            valid_stores = set(stores_df['store_id'].unique())
            invalid_store_mask = ~sales_df['store_id'].isin(valid_stores)
            invalid_store_count = invalid_store_mask.sum()
            
            if invalid_store_count > 0:
                self._log_issue('sales', f'{invalid_store_count} rows', 'INVALID_STORE_FK',
                              f'{invalid_store_count} sales reference non-existent stores',
                              'Dropped rows')
                sales_df = sales_df[~invalid_store_mask].copy()
                self.stats['invalid_dropped'] += invalid_store_count
        
        # Update report
        self.cleaning_report['sales']['final_rows'] = len(sales_df)
        self.cleaning_report['sales']['dropped_rows'] = original_count - len(sales_df) + self.cleaning_report['sales'].get('dropped_rows', 0)
        
        self.cleaning_report['foreign_key_issues'] = {
            'invalid_skus': invalid_sku_count if 'invalid_sku_count' in dir() else 0,
            'invalid_stores': invalid_store_count if 'invalid_store_count' in dir() else 0
        }
        
        return sales_df
    
    def _validate_foreign_keys_inventory(self, inventory_df, products_df, stores_df):
        """Validate and drop inventory with invalid foreign keys."""
        original_count = len(inventory_df)
        
        # Check SKU exists in products
        if 'sku' in inventory_df.columns and 'sku' in products_df.columns:
            valid_skus = set(products_df['sku'].unique())
            invalid_sku_mask = ~inventory_df['sku'].isin(valid_skus)
            invalid_sku_count = invalid_sku_mask.sum()
            
            if invalid_sku_count > 0:
                self._log_issue('inventory', f'{invalid_sku_count} rows', 'INVALID_SKU_FK',
                              f'{invalid_sku_count} inventory records reference non-existent SKUs',
                              'Dropped rows')
                inventory_df = inventory_df[~invalid_sku_mask].copy()
                self.stats['invalid_dropped'] += invalid_sku_count
        
        # Check store_id exists in stores
        if 'store_id' in inventory_df.columns and 'store_id' in stores_df.columns:
            valid_stores = set(stores_df['store_id'].unique())
            invalid_store_mask = ~inventory_df['store_id'].isin(valid_stores)
            invalid_store_count = invalid_store_mask.sum()
            
            if invalid_store_count > 0:
                self._log_issue('inventory', f'{invalid_store_count} rows', 'INVALID_STORE_FK',
                              f'{invalid_store_count} inventory records reference non-existent stores',
                              'Dropped rows')
                inventory_df = inventory_df[~invalid_store_mask].copy()
                self.stats['invalid_dropped'] += invalid_store_count
        
        # Update report
        self.cleaning_report['inventory']['final_rows'] = len(inventory_df)
        self.cleaning_report['inventory']['dropped_rows'] = original_count - len(inventory_df) + self.cleaning_report['inventory'].get('dropped_rows', 0)
        
        return inventory_df
    
    def get_issues_df(self):
        """Return issues as a DataFrame in required format."""
        if not self.issues:
            return pd.DataFrame({
                'record_identifier': ['None'],
                'issue_type': ['None'],
                'issue_detail': ['No issues found'],
                'action_taken': ['None']
            })
        
        return pd.DataFrame(self.issues)
    
    def get_issues_summary(self):
        """Return summary of issues by type."""
        if not self.issues:
            return {}
        
        df = pd.DataFrame(self.issues)
        return df.groupby('issue_type').size().to_dict()
