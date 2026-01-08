# ============================================================================
# UAE Pulse Simulator + Data Rescue Dashboard
# Utility Functions
# ============================================================================

import pandas as pd
import numpy as np

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    # Valid values for validation
    'valid_cities': ['Dubai', 'Abu Dhabi', 'Sharjah'],
    'valid_channels': ['App', 'Web', 'Marketplace'],
    'valid_fulfillment_types': ['Own', '3PL'],
    'valid_categories': ['Electronics', 'Fashion', 'Grocery', 'Beauty', 'Home', 'Sports'],
    'valid_payment_statuses': ['Paid', 'Failed', 'Refunded'],
    'valid_launch_flags': ['New', 'Regular'],
    
    # City name mapping (dirty → clean)
    'city_mapping': {
        'dubai': 'Dubai', 'DUBAI': 'Dubai', 'Dubayy': 'Dubai', 
        'DXB': 'Dubai', 'dxb': 'Dubai',
        'abu dhabi': 'Abu Dhabi', 'ABU DHABI': 'Abu Dhabi', 
        'Abu-Dhabi': 'Abu Dhabi', 'AbuDhabi': 'Abu Dhabi',
        'abudhabi': 'Abu Dhabi', 'AUH': 'Abu Dhabi', 'auh': 'Abu Dhabi',
        'sharjah': 'Sharjah', 'SHARJAH': 'Sharjah', 
        'SHJ': 'Sharjah', 'Shj': 'Sharjah', 'shj': 'Sharjah'
    },
    
    # Boolean mappings
    'true_values': ['True', 'TRUE', 'true', 'Yes', 'YES', 'yes', '1', 'T', 'Y', 't', 'y'],
    'false_values': ['False', 'FALSE', 'false', 'No', 'NO', 'no', '0', 'F', 'N', 'f', 'n'],
    
    # Null representations
    'null_representations': ['N/A', 'n/a', 'NA', 'na', 'null', 'NULL', 'None', 'none', 
                             '-', '--', '', ' ', 'NaN', 'nan', 'NAN'],
    
    # Thresholds
    'qty_max_normal': 20,
    'price_outlier_multiplier': 5,
    'stock_max_normal': 5000
}

# ============================================================================
# SIMULATOR CONFIGURATION
# ============================================================================

SIMULATOR_CONFIG = {
    'discount_impact': {
        'base_lift_per_percent': 0.02,
        'diminishing_factor': 0.95,
        'max_lift': 0.50
    },
    
    'channel_multipliers': {
        'App': 1.2,
        'Web': 1.0,
        'Marketplace': 0.9
    },
    
    'city_weights': {
        'Dubai': 0.50,
        'Abu Dhabi': 0.35,
        'Sharjah': 0.15
    },
    
    'category_elasticity': {
        'Electronics': 1.3,
        'Fashion': 1.2,
        'Beauty': 1.1,
        'Sports': 1.0,
        'Home': 0.9,
        'Grocery': 0.7
    },
    
    'promo_cost_per_order': 2.0,
    'fulfillment_cost_pct': 0.05
}

# ============================================================================
# CHART THEME (High Contrast for Projector)
# ============================================================================

CHART_THEME = {
    'template': 'plotly_dark',
    'color_sequence': ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#06b6d4', '#84cc16'],
    'background_color': 'rgba(30, 30, 63, 0.8)',
    'paper_color': 'rgba(15, 15, 26, 0.9)',
    'font_color': '#e0e0e0',
    'grid_color': 'rgba(74, 74, 138, 0.3)'
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_currency(value):
    """Format number as AED currency."""
    return f"AED {value:,.2f}"

def format_number(value):
    """Format number with commas."""
    return f"{value:,.0f}"

def format_percentage(value):
    """Format number as percentage."""
    return f"{value:.1f}%"

def calculate_percentage_change(old_value, new_value):
    """Calculate percentage change between two values."""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def style_plotly_chart(fig):
    """Apply consistent styling to plotly charts."""
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=CHART_THEME['paper_color'],
        plot_bgcolor=CHART_THEME['background_color'],
        font=dict(color=CHART_THEME['font_color'], size=12),
        title_font=dict(size=18, color='#a78bfa'),
        legend=dict(
            bgcolor='rgba(30, 30, 63, 0.8)',
            bordercolor='#4a4a8a',
            borderwidth=1
        ),
        xaxis=dict(gridcolor=CHART_THEME['grid_color'], zerolinecolor='#4a4a8a'),
        yaxis=dict(gridcolor=CHART_THEME['grid_color'], zerolinecolor='#4a4a8a')
    )
    return fig

def load_sample_data():
    """Load sample data from data folder."""
    try:
        products = pd.read_csv('data/products.csv')
        stores = pd.read_csv('data/stores.csv')
        sales = pd.read_csv('data/sales_raw.csv')
        inventory = pd.read_csv('data/inventory_snapshot.csv')
        return products, stores, sales, inventory
    except Exception as e:
        return None, None, None, None

def get_data_summary(df, name):
    """Get summary statistics for a dataframe."""
    return {
        'name': name,
        'rows': len(df),
        'columns': len(df.columns),
        'null_count': df.isnull().sum().sum(),
        'duplicate_count': df.duplicated().sum(),
        'memory_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
    }
