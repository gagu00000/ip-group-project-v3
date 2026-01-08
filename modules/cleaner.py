# ============================================================================
# UAE Pulse Simulator + Data Rescue Dashboard
# Data Cleaner Module
# ============================================================================

import pandas as pd
import numpy as np
from .utils import CONFIG

# ============================================================================
# DATA CLEANER CLASS
# ============================================================================

class DataCleaner:
    """
    Data validation and cleaning class.
    Detects 15+ types of dirty data issues and fixes them.
    """
    
    def __init__(self):
        """Initialize the cleaner with configuration."""
        self.config = CONFIG
        self.issues = []
        self.stats = {
            'products': {'before': 0, 'after': 0, 'issues': 0},
            'stores': {'before': 0, 'after': 0, 'issues': 0},
            'sales': {'before': 0, 'after': 0, 'issues': 0},
            'inventory': {'before': 0, 'after': 0, 'issues': 0}
        }
    
    def log_issue(self, record_id, table, column, issue_type, issue_detail, 
                  original_value, action_taken, new_value=None):
        """Log a single issue to the issues list."""
        self.issues.append({
            'record_identifier': str(record_id),
            'table': table,
            'column': column,
            'issue_type': issue_type,
            'issue_detail': issue_detail,
            'original_value': str(original_value),
            'action_taken': action_taken,
            'new_value': str(new_value) if new_value is not None else ''
        })
    
    def get_issues_df(self):
        """Return issues as DataFrame."""
        return pd.DataFrame(self.issues)
    
    def get_issues_summary(self):
        """Get summary of issues by type."""
        if len(self.issues) == 0:
            return {}
        df = pd.DataFrame(self.issues)
        return df['issue_type'].value_counts().to_dict()
    
    # ========================================================================
    # VALIDATION FUNCTIONS (Detect Issues)
    # ========================================================================
    
    def detect_nulls(self, df, column):
        """Detect NULL/NaN values in a column."""
        null_mask = df[column].isna()
        return df[null_mask].index.tolist()
    
    def detect_null_representations(self, df, column):
        """Detect string representations of null: 'N/A', 'null', '-', etc."""
        if df[column].dtype != 'object':
            return []
        null_reprs = self.config['null_representations']
        mask = df[column].isin(null_reprs)
        return df[mask].index.tolist()
    
    def detect_duplicates(self, df, column):
        """Detect duplicate values in a column."""
        duplicate_mask = df[column].duplicated(keep='first')
        return df[duplicate_mask].index.tolist()
    
    def detect_invalid_values(self, df, column, valid_list):
        """Detect values not in the valid list."""
        invalid_mask = ~df[column].isin(valid_list) & df[column].notna()
        return [(idx, df.loc[idx, column]) for idx in df[invalid_mask].index]
    
    def detect_whitespace(self, df, column):
        """Detect leading/trailing whitespace in string column."""
        if df[column].dtype != 'object':
            return []
        
        def has_whitespace(val):
            if pd.isna(val):
                return False
            return str(val) != str(val).strip()
        
        mask = df[column].apply(has_whitespace)
        return df[mask].index.tolist()
    
    def detect_negative_values(self, df, column):
        """Detect negative values where they shouldn't exist."""
        if not pd.api.types.is_numeric_dtype(df[column]):
            return []
        mask = df[column] < 0
        return [(idx, df.loc[idx, column]) for idx in df[mask].index]
    
    def detect_outliers(self, df, column, max_normal=None, multiplier=None):
        """Detect outlier values using threshold or multiplier method."""
        if not pd.api.types.is_numeric_dtype(df[column]):
            return []
        
        if max_normal is not None:
            mask = df[column] > max_normal
        elif multiplier is not None:
            median_val = df[column].median()
            threshold = median_val * multiplier
            mask = df[column] > threshold
        else:
            return []
        
        return [(idx, df.loc[idx, column]) for idx in df[mask].index]
    
    # ========================================================================
    # CLEANING FUNCTIONS (Fix Issues)
    # ========================================================================
    
    def clean_whitespace(self, df, column, table_name):
        """Strip leading/trailing whitespace from string column."""
        if df[column].dtype != 'object':
            return 0
        
        count = 0
        for idx, val in df[column].items():
            if pd.isna(val):
                continue
            stripped = str(val).strip()
            if str(val) != stripped:
                self.log_issue(idx, table_name, column, 'WHITESPACE',
                              'Leading/trailing whitespace', f'"{val}"',
                              'Stripped whitespace', stripped)
                df.loc[idx, column] = stripped
                count += 1
        return count
    
    def clean_with_mapping(self, df, column, mapping_dict, table_name):
        """Fix invalid values using a mapping dictionary."""
        count = 0
        for idx, val in df[column].items():
            if pd.isna(val):
                continue
            val_stripped = str(val).strip()
            if val_stripped in mapping_dict:
                new_val = mapping_dict[val_stripped]
                self.log_issue(idx, table_name, column, 'INVALID_VALUE',
                              'Non-standard value mapped', val,
                              'Mapped to standard value', new_val)
                df.loc[idx, column] = new_val
                count += 1
        return count
    
    def clean_nulls_with_value(self, df, column, fill_value, table_name):
        """Replace NULL/NaN values with a specified value."""
        null_mask = df[column].isna()
        null_count = null_mask.sum()
        
        if null_count > 0:
            for idx in df[null_mask].index:
                self.log_issue(idx, table_name, column, 'MISSING_VALUE',
                              f'Null value in {column}', 'NULL',
                              f'Imputed with {fill_value}', fill_value)
            df.loc[null_mask, column] = fill_value
        return null_count
    
    def clean_nulls_with_median(self, df, column, table_name):
        """Replace NULL/NaN values with column median."""
        null_mask = df[column].isna()
        null_count = null_mask.sum()
        
        if null_count > 0:
            median_val = df[column].median()
            for idx in df[null_mask].index:
                self.log_issue(idx, table_name, column, 'MISSING_VALUE',
                              f'Null value in {column}', 'NULL',
                              f'Imputed with median ({median_val:.2f})', median_val)
            df.loc[null_mask, column] = median_val
        return null_count
    
    def clean_duplicates(self, df, column, table_name):
        """Remove duplicate rows based on column (keep first)."""
        duplicate_mask = df[column].duplicated(keep='first')
        duplicate_count = duplicate_mask.sum()
        
        if duplicate_count > 0:
            for idx in df[duplicate_mask].index:
                self.log_issue(idx, table_name, column, 'DUPLICATE_VALUE',
                              f'Duplicate {column}', df.loc[idx, column],
                              'Row removed (kept first occurrence)', '')
            df = df[~duplicate_mask].reset_index(drop=True)
        return df, duplicate_count
    
    def clean_negative_values(self, df, column, table_name):
        """Floor negative values at 0."""
        if not pd.api.types.is_numeric_dtype(df[column]):
            return 0
        
        mask = df[column] < 0
        count = mask.sum()
        
        if count > 0:
            for idx in df[mask].index:
                self.log_issue(idx, table_name, column, 'NEGATIVE_VALUE',
                              'Negative value not allowed', df.loc[idx, column],
                              'Floored to 0', 0)
            df.loc[mask, column] = 0
        return count
    
    def clean_outliers_cap(self, df, column, max_value, table_name):
        """Cap outlier values at maximum threshold."""
        if not pd.api.types.is_numeric_dtype(df[column]):
            return 0
        
        mask = df[column] > max_value
        count = mask.sum()
        
        if count > 0:
            for idx in df[mask].index:
                self.log_issue(idx, table_name, column, 'OUTLIER_VALUE',
                              f'Value exceeds threshold {max_value}', df.loc[idx, column],
                              f'Capped at {max_value}', max_value)
            df.loc[mask, column] = max_value
        return count
    
    def clean_mixed_case(self, df, column, valid_values, table_name):
        """Standardize case of values to match valid values list."""
        if df[column].dtype != 'object':
            return 0
        
        valid_lower_map = {v.lower(): v for v in valid_values}
        count = 0
        
        for idx, val in df[column].items():
            if pd.isna(val):
                continue
            val_str = str(val).strip()
            val_lower = val_str.lower()
            if val_lower in valid_lower_map and val_str != valid_lower_map[val_lower]:
                correct_val = valid_lower_map[val_lower]
                self.log_issue(idx, table_name, column, 'MIXED_CASE',
                              'Inconsistent case', val,
                              'Standardized case', correct_val)
                df.loc[idx, column] = correct_val
                count += 1
        return count
    
    def clean_boolean_strings(self, df, column, table_name):
        """Convert string boolean representations to actual booleans."""
        true_vals = self.config['true_values']
        false_vals = self.config['false_values']
        count = 0
        
        for idx, val in df[column].items():
            if pd.isna(val):
                continue
            if isinstance(val, str):
                if val in true_vals:
                    self.log_issue(idx, table_name, column, 'BOOLEAN_AS_STRING',
                                  'Boolean stored as string', val,
                                  'Converted to boolean', True)
                    df.loc[idx, column] = True
                    count += 1
                elif val in false_vals:
                    self.log_issue(idx, table_name, column, 'BOOLEAN_AS_STRING',
                                  'Boolean stored as string', val,
                                  'Converted to boolean', False)
                    df.loc[idx, column] = False
                    count += 1
        return count
    
    def clean_fk_violations(self, df, column, valid_keys, table_name):
        """Remove rows with invalid foreign key references."""
        invalid_mask = ~df[column].isin(valid_keys) & df[column].notna()
        invalid_count = invalid_mask.sum()
        
        if invalid_count > 0:
            for idx in df[invalid_mask].index:
                self.log_issue(idx, table_name, column, 'FK_VIOLATION',
                              f'Invalid reference not in parent table', df.loc[idx, column],
                              'Row removed', '')
            df = df[~invalid_mask].reset_index(drop=True)
        return df, invalid_count
    
    def clean_invalid_timestamps(self, df, column, table_name):
        """Remove rows with invalid timestamps."""
        invalid_indices = []
        
        for idx, val in df[column].items():
            if pd.isna(val):
                continue
            try:
                pd.to_datetime(val)
            except:
                invalid_indices.append(idx)
                self.log_issue(idx, table_name, column, 'INVALID_TIMESTAMP',
                              'Cannot parse timestamp', val,
                              'Row removed', '')
        
        if len(invalid_indices) > 0:
            df = df.drop(invalid_indices).reset_index(drop=True)
        return df, len(invalid_indices)
    
    # ========================================================================
    # TABLE-LEVEL CLEANING FUNCTIONS
    # ========================================================================
    
    def clean_products(self, df):
        """Clean the products table."""
        self.stats['products']['before'] = len(df)
        df = df.copy()
        
        # Clean whitespace
        for col in ['brand', 'category', 'launch_flag']:
            if col in df.columns:
                self.clean_whitespace(df, col, 'products')
        
        # Clean missing unit_cost_aed with category median
        if 'unit_cost_aed' in df.columns and df['unit_cost_aed'].isna().sum() > 0:
            for idx in df[df['unit_cost_aed'].isna()].index:
                category = df.loc[idx, 'category']
                category_costs = df[(df['category'] == category) & (df['unit_cost_aed'].notna())]['unit_cost_aed']
                
                if len(category_costs) > 0:
                    median_cost = category_costs.median()
                else:
                    median_cost = df.loc[idx, 'base_price_aed'] * 0.5 if 'base_price_aed' in df.columns else 50
                
                self.log_issue(df.loc[idx, 'product_id'] if 'product_id' in df.columns else idx,
                              'products', 'unit_cost_aed', 'MISSING_VALUE',
                              f'Missing unit cost for {category} product', 'NULL',
                              'Imputed with category median', round(median_cost, 2))
                df.loc[idx, 'unit_cost_aed'] = round(median_cost, 2)
        
        # Remove duplicates
        if 'product_id' in df.columns:
            df, _ = self.clean_duplicates(df, 'product_id', 'products')
        
        self.stats['products']['after'] = len(df)
        self.stats['products']['issues'] = len([i for i in self.issues if i['table'] == 'products'])
        return df
    
    def clean_stores(self, df):
        """Clean the stores table."""
        self.stats['stores']['before'] = len(df)
        df = df.copy()
        
        # Clean whitespace
        for col in ['city', 'channel', 'fulfillment_type']:
            if col in df.columns:
                self.clean_whitespace(df, col, 'stores')
        
        # Clean city names using mapping
        if 'city' in df.columns:
            self.clean_with_mapping(df, 'city', self.config['city_mapping'], 'stores')
        
        # Clean mixed case in channel and fulfillment_type
        if 'channel' in df.columns:
            self.clean_mixed_case(df, 'channel', self.config['valid_channels'], 'stores')
        if 'fulfillment_type' in df.columns:
            self.clean_mixed_case(df, 'fulfillment_type', self.config['valid_fulfillment_types'], 'stores')
        
        # Remove duplicates
        if 'store_id' in df.columns:
            df, _ = self.clean_duplicates(df, 'store_id', 'stores')
        
        self.stats['stores']['after'] = len(df)
        self.stats['stores']['issues'] = len([i for i in self.issues if i['table'] == 'stores'])
        return df
    
    def clean_sales(self, df, valid_product_ids=None, valid_store_ids=None):
        """Clean the sales table."""
        self.stats['sales']['before'] = len(df)
        df = df.copy()
        
        # Remove duplicate order_ids
        if 'order_id' in df.columns:
            df, _ = self.clean_duplicates(df, 'order_id', 'sales')
        
        # Clean invalid timestamps
        if 'order_time' in df.columns:
            df, _ = self.clean_invalid_timestamps(df, 'order_time', 'sales')
            # Standardize date format
            df['order_time'] = pd.to_datetime(df['order_time'], errors='coerce')
            df = df.dropna(subset=['order_time'])
            df['order_time'] = df['order_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Clean discount_pct
        if 'discount_pct' in df.columns:
            # Convert null representations
            null_reprs = self.config['null_representations']
            for idx, val in df['discount_pct'].items():
                if pd.notna(val) and str(val).strip() in null_reprs:
                    self.log_issue(idx, 'sales', 'discount_pct', 'NULL_REPRESENTATION',
                                  'String null representation', val,
                                  'Replaced with 0', 0)
                    df.loc[idx, 'discount_pct'] = np.nan
            
            # Fill missing with 0
            self.clean_nulls_with_value(df, 'discount_pct', 0, 'sales')
            df['discount_pct'] = pd.to_numeric(df['discount_pct'], errors='coerce').fillna(0)
        
        # Clean outlier quantities
        if 'qty' in df.columns:
            self.clean_outliers_cap(df, 'qty', self.config['qty_max_normal'], 'sales')
        
        # Clean outlier prices
        if 'selling_price_aed' in df.columns:
            median_price = df['selling_price_aed'].median()
            threshold = median_price * self.config['price_outlier_multiplier']
            self.clean_outliers_cap(df, 'selling_price_aed', threshold, 'sales')
        
        # Clean payment_status case
        if 'payment_status' in df.columns:
            self.clean_mixed_case(df, 'payment_status', self.config['valid_payment_statuses'], 'sales')
        
        # Clean return_flag boolean strings
        if 'return_flag' in df.columns:
            self.clean_boolean_strings(df, 'return_flag', 'sales')
            # Ensure all values are boolean
            df['return_flag'] = df['return_flag'].apply(
                lambda x: True if x in [True, 'True', 'true', 1] else False if pd.notna(x) else False
            )
        
        # Clean FK violations
        if valid_product_ids is not None and 'product_id' in df.columns:
            df, _ = self.clean_fk_violations(df, 'product_id', valid_product_ids, 'sales')
        if valid_store_ids is not None and 'store_id' in df.columns:
            df, _ = self.clean_fk_violations(df, 'store_id', valid_store_ids, 'sales')
        
        self.stats['sales']['after'] = len(df)
        self.stats['sales']['issues'] = len([i for i in self.issues if i['table'] == 'sales'])
        return df
    
    def clean_inventory(self, df, valid_product_ids=None, valid_store_ids=None):
        """Clean the inventory table."""
        self.stats['inventory']['before'] = len(df)
        df = df.copy()
        
        # Clean negative stock
        if 'stock_on_hand' in df.columns:
            self.clean_negative_values(df, 'stock_on_hand', 'inventory')
        
        # Clean extreme stock
        if 'stock_on_hand' in df.columns:
            self.clean_outliers_cap(df, 'stock_on_hand', self.config['stock_max_normal'], 'inventory')
        
        # Clean FK violations
        if valid_product_ids is not None and 'product_id' in df.columns:
            df, _ = self.clean_fk_violations(df, 'product_id', valid_product_ids, 'inventory')
        if valid_store_ids is not None and 'store_id' in df.columns:
            df, _ = self.clean_fk_violations(df, 'store_id', valid_store_ids, 'inventory')
        
        # Standardize date format
        if 'snapshot_date' in df.columns:
            df['snapshot_date'] = pd.to_datetime(df['snapshot_date'], errors='coerce').dt.strftime('%Y-%m-%d')
        
        self.stats['inventory']['after'] = len(df)
        self.stats['inventory']['issues'] = len([i for i in self.issues if i['table'] == 'inventory'])
        return df
    
    def clean_all(self, products_df, stores_df, sales_df, inventory_df):
        """Clean all tables and return cleaned versions."""
        # Reset issues list
        self.issues = []
        
        # Clean in order (products & stores first for FK validation)
        clean_products = self.clean_products(products_df)
        clean_stores = self.clean_stores(stores_df)
        
        # Get valid IDs for FK validation
        valid_product_ids = set(clean_products['product_id'].tolist()) if 'product_id' in clean_products.columns else None
        valid_store_ids = set(clean_stores['store_id'].tolist()) if 'store_id' in clean_stores.columns else None
        
        # Clean sales and inventory
        clean_sales = self.clean_sales(sales_df, valid_product_ids, valid_store_ids)
        clean_inventory = self.clean_inventory(inventory_df, valid_product_ids, valid_store_ids)
        
        return clean_products, clean_stores, clean_sales, clean_inventory
