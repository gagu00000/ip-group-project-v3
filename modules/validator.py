"""
File Validator Module - UAE Pulse Simulator
Validates uploaded files match expected schema for each file type.
"""

import pandas as pd


class FileValidator:
    """Validates uploaded files against expected schemas."""
    
    # Required columns for each file type (with variations)
    SCHEMAS = {
        'products': {
            'required': [
                ['sku', 'product_id', 'productid', 'SKU'],
                ['category'],
                ['base_price_aed', 'base_price', 'price'],
            ],
            'optional': ['unit_cost_aed', 'unit_cost', 'brand', 'launch_flag', 'tax_rate'],
            'unique_identifiers': ['sku', 'product_id', 'category', 'brand', 'launch_flag', 'base_price_aed']
        },
        'stores': {
            'required': [
                ['store_id', 'storeid'],
                ['city'],
                ['channel']
            ],
            'optional': ['fulfillment_type', 'store_name'],
            'unique_identifiers': ['store_id', 'city', 'channel', 'fulfillment_type']
        },
        'sales': {
            'required': [
                ['order_id', 'orderid', 'transaction_id'],
                ['sku', 'product_id', 'productid'],
                ['store_id', 'storeid'],
                ['qty', 'quantity', 'units'],
                ['selling_price_aed', 'selling_price', 'price', 'amount']
            ],
            'optional': ['order_time', 'discount_pct', 'payment_status', 'return_flag'],
            'unique_identifiers': ['order_id', 'qty', 'selling_price_aed', 'payment_status', 'discount_pct', 'return_flag']
        },
        'inventory': {
            'required': [
                ['sku', 'product_id', 'productid'],
                ['store_id', 'storeid'],
                ['stock_on_hand', 'stock', 'inventory', 'on_hand']
            ],
            'optional': ['snapshot_date', 'reorder_point', 'lead_time_days'],
            'unique_identifiers': ['stock_on_hand', 'stock', 'reorder_point', 'lead_time_days', 'snapshot_date']
        }
    }
    
    @classmethod
    def validate_file(cls, df, expected_type):
        """
        Validate if uploaded file matches expected type.
        """
        if df is None or df.empty:
            return {
                'valid': False,
                'message': '❌ File is empty or could not be read.',
                'missing_columns': [],
                'detected_type': None
            }
        
        # Normalize column names
        df_columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # Check if file matches expected type
        expected_schema = cls.SCHEMAS.get(expected_type)
        if not expected_schema:
            return {
                'valid': False,
                'message': f'❌ Unknown file type: {expected_type}',
                'missing_columns': [],
                'detected_type': None
            }
        
        # Check required columns for expected type
        missing_required = []
        matched_required = 0
        for col_variants in expected_schema['required']:
            col_variants_lower = [c.lower() for c in col_variants]
            if any(col in df_columns for col in col_variants_lower):
                matched_required += 1
            else:
                missing_required.append(col_variants[0])
        
        # If all required columns present, file is valid
        if not missing_required:
            return {
                'valid': True,
                'message': f'✅ Valid {expected_type} file detected.',
                'missing_columns': [],
                'detected_type': expected_type
            }
        
        # File doesn't match expected type - try to detect actual type
        detected_type = cls._detect_file_type(df_columns)
        
        if detected_type and detected_type != expected_type:
            return {
                'valid': False,
                'message': f'❌ Wrong file! This looks like a **{detected_type.upper()}** file, not {expected_type.upper()}.',
                'missing_columns': missing_required,
                'detected_type': detected_type
            }
        else:
            return {
                'valid': False,
                'message': f'❌ Unrecognized file! This doesn\'t look like a valid {expected_type.upper()} file.',
                'missing_columns': missing_required,
                'detected_type': None,
                'uploaded_columns': list(df_columns)[:10]
            }
    
    @classmethod
    def _detect_file_type(cls, df_columns):
        """Detect the actual file type based on columns - STRICT matching."""
        scores = {}
        required_counts = {}
        
        for file_type, schema in cls.SCHEMAS.items():
            score = 0
            required_matched = 0
            total_required = len(schema['required'])
            
            # Check required columns (most important)
            for col_variants in schema['required']:
                col_variants_lower = [c.lower() for c in col_variants]
                if any(col in df_columns for col in col_variants_lower):
                    score += 3
                    required_matched += 1
            
            # Check unique identifiers (secondary)
            for identifier in schema.get('unique_identifiers', []):
                if identifier.lower() in df_columns:
                    score += 1
            
            scores[file_type] = score
            required_counts[file_type] = (required_matched, total_required)
        
        # Only return a match if at least 60% of required columns are present
        if scores:
            best_match = max(scores, key=scores.get)
            matched, total = required_counts[best_match]
            match_percentage = (matched / total * 100) if total > 0 else 0
            
            if match_percentage >= 60 and scores[best_match] >= 6:
                return best_match
        
        return None
    
    @classmethod
    def get_expected_columns(cls, file_type):
        """Get list of expected columns for a file type."""
        schema = cls.SCHEMAS.get(file_type, {})
        required = [cols[0] for cols in schema.get('required', [])]
        optional = schema.get('optional', [])
        return {
            'required': required,
            'optional': optional
        }
