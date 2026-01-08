# ============================================================================
# UAE Promo Pulse Simulator + Data Rescue Dashboard
# PREMIUM ENHANCED VERSION v3.0 - Advanced EDA & Theme Toggle
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io

# Import custom modules
from modules.cleaner import DataCleaner
from modules.simulator import Simulator
from modules.utils import (
    CONFIG, SIMULATOR_CONFIG, CHART_THEME, 
    style_plotly_chart, load_sample_data, get_data_summary
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="UAE Promo Pulse Simulator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# THEME MANAGEMENT
# ============================================================================

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Theme colors
THEMES = {
    'dark': {
        'bg_primary': '#0a0a0f',
        'bg_secondary': '#12121a',
        'bg_card': '#16161f',
        'bg_card_hover': '#1e1e2d',
        'text_primary': '#f1f5f9',
        'text_secondary': '#94a3b8',
        'text_muted': '#64748b',
        'border_color': '#2d2d3a',
        'gradient_1': 'rgba(6, 182, 212, 0.08)',
        'gradient_2': 'rgba(139, 92, 246, 0.08)',
        'gradient_3': 'rgba(236, 72, 153, 0.05)',
    },
    'light': {
        'bg_primary': '#ffffff',
        'bg_secondary': '#f8fafc',
        'bg_card': '#ffffff',
        'bg_card_hover': '#f1f5f9',
        'text_primary': '#0f172a',
        'text_secondary': '#475569',
        'text_muted': '#64748b',
        'border_color': '#e2e8f0',
        'gradient_1': 'rgba(6, 182, 212, 0.05)',
        'gradient_2': 'rgba(139, 92, 246, 0.05)',
        'gradient_3': 'rgba(236, 72, 153, 0.03)',
    }
}

current_theme = THEMES[st.session_state.theme]

# ============================================================================
# PREMIUM CSS WITH THEME SUPPORT
# ============================================================================

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    :root {{
        --bg-primary: {current_theme['bg_primary']};
        --bg-secondary: {current_theme['bg_secondary']};
        --bg-card: {current_theme['bg_card']};
        --bg-card-hover: {current_theme['bg_card_hover']};
        --text-primary: {current_theme['text_primary']};
        --text-secondary: {current_theme['text_secondary']};
        --text-muted: {current_theme['text_muted']};
        --border-color: {current_theme['border_color']};
        
        --accent-cyan: #06b6d4;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-pink: #ec4899;
        --accent-green: #10b981;
        --accent-orange: #f59e0b;
        --accent-red: #ef4444;
        --accent-teal: #14b8a6;
        
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, {'0.1' if st.session_state.theme == 'light' else '0.3'});
        --shadow-md: 0 4px 16px rgba(0, 0, 0, {'0.12' if st.session_state.theme == 'light' else '0.4'});
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, {'0.15' if st.session_state.theme == 'light' else '0.5'});
    }}
    
    /* ANIMATIONS */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ box-shadow: 0 0 20px rgba(6, 182, 212, 0.3); }}
        50% {{ box-shadow: 0 0 40px rgba(6, 182, 212, 0.6); }}
    }}
    
    @keyframes shimmer {{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}
    
    /* HIDE DEFAULTS */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* MAIN BACKGROUND */
    .stApp {{
        background: var(--bg-primary);
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
        transition: background 0.3s ease;
    }}
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {{
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
        transition: background 0.3s ease;
    }}
    
    /* THEME TOGGLE BUTTON */
    .theme-toggle {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
        border: none;
        border-radius: 50%;
        width: 56px;
        height: 56px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: var(--shadow-lg);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    
    .theme-toggle:hover {{
        transform: scale(1.1) rotate(15deg);
        box-shadow: 0 12px 48px rgba(6, 182, 212, 0.5);
    }}
    
    /* PREMIUM CONTAINER */
    .premium-container {{
        background: var(--bg-card);
        border-radius: 20px;
        padding: 32px;
        margin: 24px 0;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
    }}
    
    .premium-container:hover {{
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }}
    
    /* HERO SECTION */
    .hero-premium {{
        background: linear-gradient(135deg, 
            {current_theme['gradient_1']} 0%, 
            {current_theme['gradient_2']} 50%, 
            {current_theme['gradient_3']} 100%);
        border-radius: 28px;
        padding: 64px 48px;
        margin-bottom: 48px;
        border: 2px solid var(--border-color);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.8s ease-out;
    }}
    
    .hero-premium::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.1) 0%, transparent 50%);
        animation: float 8s ease-in-out infinite;
    }}
    
    .hero-title-premium {{
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 40%, #8b5cf6 70%, #ec4899 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 24px;
        position: relative;
        z-index: 1;
        line-height: 1.1;
        letter-spacing: -2px;
    }}
    
    /* METRIC CARDS - PREMIUM */
    .metric-card-premium {{
        background: var(--bg-card);
        border-radius: 20px;
        padding: 28px 24px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card-premium::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple));
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    
    .metric-card-premium:hover {{
        transform: translateY(-8px) scale(1.02);
        border-color: var(--accent-cyan);
        box-shadow: var(--shadow-lg);
    }}
    
    .metric-card-premium:hover::before {{
        opacity: 1;
    }}
    
    .metric-label-premium {{
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
        margin-bottom: 8px;
    }}
    
    .metric-value-premium {{
        font-size: 2.25rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        margin: 12px 0;
    }}
    
    .metric-delta {{
        font-size: 0.9rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    
    /* PAGE TITLES */
    .page-title-premium {{
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 16px;
        line-height: 1.1;
        letter-spacing: -1.5px;
        color: var(--text-primary);
    }}
    
    .section-title-premium {{
        font-size: 2rem;
        font-weight: 700;
        margin: 32px 0 20px 0;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    
    .section-title-premium::after {{
        content: '';
        flex: 1;
        height: 2px;
        background: linear-gradient(90deg, var(--border-color), transparent);
    }}
    
    /* FILTER CONTAINER */
    .filter-container {{
        background: var(--bg-card);
        border-radius: 16px;
        padding: 24px;
        margin: 24px 0;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }}
    
    /* CHART CONTAINER */
    .chart-container {{
        background: var(--bg-card);
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }}
    
    .chart-container:hover {{
        box-shadow: var(--shadow-md);
    }}
    
    /* INSIGHT CARDS */
    .insight-premium {{
        background: linear-gradient(135deg, 
            rgba(139, 92, 246, {'0.08' if st.session_state.theme == 'dark' else '0.05'}) 0%, 
            rgba(236, 72, 153, {'0.08' if st.session_state.theme == 'dark' else '0.05'}) 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        margin: 16px 0;
        transition: all 0.3s ease;
    }}
    
    .insight-premium:hover {{
        transform: translateX(8px);
        border-color: var(--accent-purple);
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.2);
    }}
    
    .insight-title-premium {{
        color: var(--accent-purple);
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    .insight-text-premium {{
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.7;
    }}
    
    /* RECOMMENDATION BOX */
    .recommendation-premium {{
        background: linear-gradient(135deg, 
            rgba(16, 185, 129, {'0.12' if st.session_state.theme == 'dark' else '0.08'}) 0%, 
            rgba(6, 182, 212, {'0.12' if st.session_state.theme == 'dark' else '0.08'}) 100%);
        border-radius: 20px;
        padding: 32px;
        border: 2px solid rgba(16, 185, 129, 0.3);
        margin: 24px 0;
        position: relative;
        overflow: hidden;
    }}
    
    .recommendation-premium::before {{
        content: '💡';
        position: absolute;
        top: 24px;
        right: 24px;
        font-size: 3rem;
        opacity: 0.3;
    }}
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        background: transparent;
        border-bottom: 2px solid var(--border-color);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: var(--bg-card);
        border-radius: 12px 12px 0 0;
        color: var(--text-secondary);
        padding: 14px 28px;
        border: 1px solid var(--border-color);
        border-bottom: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: var(--bg-card-hover);
        border-color: var(--accent-cyan);
        transform: translateY(-3px);
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
    }}
    
    /* BUTTONS */
    .stButton > button {{
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 16px 36px;
        font-weight: 700;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.3);
        letter-spacing: 0.5px;
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
        box-shadow: 0 12px 36px rgba(59, 130, 246, 0.5);
        transform: translateY(-3px);
    }}
    
    /* ALERTS */
    .alert-info {{
        background: linear-gradient(135deg, 
            rgba(6, 182, 212, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 0%, 
            rgba(59, 130, 246, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 100%);
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid var(--accent-cyan);
        margin: 16px 0;
        color: var(--text-primary);
    }}
    
    .alert-success {{
        background: linear-gradient(135deg, 
            rgba(16, 185, 129, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 0%, 
            rgba(20, 184, 166, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 100%);
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid var(--accent-green);
        margin: 16px 0;
        color: var(--text-primary);
    }}
    
    .alert-warning {{
        background: linear-gradient(135deg, 
            rgba(245, 158, 11, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 0%, 
            rgba(251, 146, 60, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 100%);
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid var(--accent-orange);
        margin: 16px 0;
        color: var(--text-primary);
    }}
    
    /* DATAFRAME */
    .stDataFrame {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border-color);
    }}
    
    /* DIVIDER */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 40px 0;
    }}
    
    /* FOOTER */
    .footer-premium {{
        background: var(--bg-secondary);
        padding: 48px;
        text-align: center;
        border-top: 1px solid var(--border-color);
        margin-top: 80px;
        border-radius: 28px 28px 0 0;
        position: relative;
    }}
    
    .footer-premium::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple), var(--accent-pink));
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_metric_card_premium(label, value, delta=None, delta_type="positive", color="cyan"):
    """Create premium metric card."""
    colors = {
        'cyan': '#06b6d4', 'blue': '#3b82f6', 'purple': '#8b5cf6',
        'pink': '#ec4899', 'green': '#10b981', 'orange': '#f59e0b',
        'teal': '#14b8a6', 'red': '#ef4444'
    }
    accent = colors.get(color, '#06b6d4')
    
    delta_html = ""
    if delta:
        delta_color = "#10b981" if delta_type == "positive" else "#ef4444"
        delta_icon = "↑" if delta_type == "positive" else "↓"
        delta_html = f'<div class="metric-delta" style="color: {delta_color};">{delta_icon} {delta}</div>'
    else:
        delta_html = '<div style="height: 28px;"></div>'
    
    return f"""
    <div class="metric-card-premium">
        <div class="metric-label-premium">{label}</div>
        <div class="metric-value-premium" style="color: {accent};">{value}</div>
        {delta_html}
    </div>
    """

def create_insight_card_premium(title, text):
    """Create premium insight card."""
    return f"""
    <div class="insight-premium">
        <div class="insight-title-premium">💡 {title}</div>
        <div class="insight-text-premium">{text}</div>
    </div>
    """

def create_recommendation_premium(title, items):
    """Create premium recommendation box."""
    items_html = "<br>".join([f"• {item}" for item in items])
    return f"""
    <div class="recommendation-premium">
        <div style="color: #10b981; font-size: 1.4rem; font-weight: 800; margin-bottom: 16px;">📋 {title}</div>
        <div style="color: var(--text-secondary); font-size: 1.05rem; line-height: 1.9;">{items_html}</div>
    </div>
    """

def show_footer():
    """Premium footer."""
    st.markdown("""
    <div class="footer-premium">
        <div style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 12px;">
            🚀 UAE Promo Pulse Simulator - Premium Analytics Platform
        </div>
        <div style="color: var(--text-muted); font-size: 1rem; margin-bottom: 16px;">
            Advanced Data Rescue & Campaign Simulation
        </div>
        <div style="
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
            font-size: 1.15rem;
        ">Kartik Joshi • Gagandeep Singh • Samuel Alex • Prem Kukreja</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# ADVANCED EDA FUNCTIONS
# ============================================================================

def create_customer_cohort_analysis(sales_df):
    """EDA Insight 1: Customer Cohort Retention Analysis."""
    if 'order_time' not in sales_df.columns or 'order_id' not in sales_df.columns:
        return None
    
    sales_copy = sales_df.copy()
    sales_copy['order_time'] = pd.to_datetime(sales_copy['order_time'], errors='coerce')
    sales_copy['order_month'] = sales_copy['order_time'].dt.to_period('M')
    
    # Simulate customer_id if not present
    if 'customer_id' not in sales_copy.columns:
        sales_copy['customer_id'] = sales_copy['order_id'].apply(lambda x: hash(str(x)) % 10000)
    
    # First purchase month
    first_purchase = sales_copy.groupby('customer_id')['order_month'].min().reset_index()
    first_purchase.columns = ['customer_id', 'cohort_month']
    
    sales_copy = sales_copy.merge(first_purchase, on='customer_id')
    sales_copy['months_since_first'] = (sales_copy['order_month'] - sales_copy['cohort_month']).apply(lambda x: x.n)
    
    # Cohort table
    cohort_data = sales_copy.groupby(['cohort_month', 'months_since_first'])['customer_id'].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index='cohort_month', columns='months_since_first', values='customer_id')
    
    # Calculate retention rates
    cohort_size = cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.divide(cohort_size, axis=0) * 100
    
    return retention

def create_rfm_segmentation(sales_df):
    """EDA Insight 2: RFM (Recency, Frequency, Monetary) Customer Segmentation."""
    if 'order_time' not in sales_df.columns:
        return None
    
    sales_copy = sales_df.copy()
    sales_copy['order_time'] = pd.to_datetime(sales_copy['order_time'], errors='coerce')
    
    # Simulate customer_id
    if 'customer_id' not in sales_copy.columns:
        sales_copy['customer_id'] = sales_copy['order_id'].apply(lambda x: hash(str(x)) % 10000)
    
    # Calculate revenue per order
    if 'selling_price_aed' in sales_copy.columns and 'qty' in sales_copy.columns:
        sales_copy['revenue'] = pd.to_numeric(sales_copy['selling_price_aed'], errors='coerce') * pd.to_numeric(sales_copy['qty'], errors='coerce')
    else:
        return None
    
    snapshot_date = sales_copy['order_time'].max() + timedelta(days=1)
    
    rfm = sales_copy.groupby('customer_id').agg({
        'order_time': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'count',
        'revenue': 'sum'
    }).reset_index()
    
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # Score RFM
    rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
    
    # Segment customers
    def segment_customer(row):
        if row['r_score'] >= 4 and row['f_score'] >= 4:
            return 'Champions'
        elif row['r_score'] >= 3 and row['f_score'] >= 3:
            return 'Loyal Customers'
        elif row['r_score'] >= 4 and row['f_score'] <= 2:
            return 'Promising'
        elif row['r_score'] <= 2 and row['f_score'] >= 3:
            return 'At Risk'
        elif row['r_score'] <= 2 and row['f_score'] <= 2:
            return 'Hibernating'
        else:
            return 'Need Attention'
    
    rfm['segment'] = rfm.apply(segment_customer, axis=1)
    
    return rfm

def create_price_elasticity_analysis(sales_df, products_df):
    """EDA Insight 3: Price Elasticity & Discount Effectiveness Analysis."""
    if 'discount_pct' not in sales_df.columns or 'selling_price_aed' not in sales_df.columns:
        return None
    
    sales_copy = sales_df.copy()
    sales_copy['discount_pct'] = pd.to_numeric(sales_copy['discount_pct'], errors='coerce').fillna(0)
    sales_copy['selling_price_aed'] = pd.to_numeric(sales_copy['selling_price_aed'], errors='coerce')
    sales_copy['qty'] = pd.to_numeric(sales_copy['qty'], errors='coerce')
    
    # Bin discounts
    sales_copy['discount_bin'] = pd.cut(sales_copy['discount_pct'], 
                                         bins=[-1, 0, 5, 10, 15, 20, 100],
                                         labels=['No Discount', '1-5%', '6-10%', '11-15%', '16-20%', '20%+'])
    
    # Aggregate by discount bin
    elasticity = sales_copy.groupby('discount_bin').agg({
        'qty': 'sum',
        'selling_price_aed': 'mean',
        'order_id': 'count'
    }).reset_index()
    
    elasticity.columns = ['discount_bin', 'total_qty', 'avg_price', 'num_orders']
    elasticity['avg_qty_per_order'] = elasticity['total_qty'] / elasticity['num_orders']
    
    return elasticity

# ============================================================================

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if 'raw_products' not in st.session_state:
    st.session_state.raw_products = None
if 'raw_stores' not in st.session_state:
    st.session_state.raw_stores = None
if 'raw_sales' not in st.session_state:
    st.session_state.raw_sales = None
if 'raw_inventory' not in st.session_state:
    st.session_state.raw_inventory = None
if 'clean_products' not in st.session_state:
    st.session_state.clean_products = None
if 'clean_stores' not in st.session_state:
    st.session_state.clean_stores = None
if 'clean_sales' not in st.session_state:
    st.session_state.clean_sales = None
if 'clean_inventory' not in st.session_state:
    st.session_state.clean_inventory = None
if 'issues_df' not in st.session_state:
    st.session_state.issues_df = None
if 'is_cleaned' not in st.session_state:
    st.session_state.is_cleaned = False
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'sim_results' not in st.session_state:
    st.session_state.sim_results = None

# ============================================================================
# SIDEBAR WITH THEME TOGGLE
# ============================================================================

with st.sidebar:
    # Theme Toggle Button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div style="text-align: center; margin-top: -20px; padding-bottom: 15px;">
            <div style="font-size: 48px; margin-bottom: 5px;">🛒</div>
            <div style="
                font-size: 26px;
                font-weight: 800;
                background: linear-gradient(135deg, #06b6d4, #3b82f6, #8b5cf6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">Promo Pulse</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
        if st.button(theme_icon, key='theme_toggle'):
            toggle_theme()
            st.rerun()
    
    st.markdown("---")
    
    # Navigation
    st.markdown('<p style="color: #ec4899; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📍 NAVIGATION</p>', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📂 Data Upload", "🧹 Data Rescue", "🎯 Simulator", "📊 Dashboard", "🔬 Advanced EDA"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Data Status
    st.markdown('<p style="color: #3b82f6; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📡 STATUS</p>', unsafe_allow_html=True)
    
    data_loaded = st.session_state.data_loaded
    data_cleaned = st.session_state.is_cleaned
    
    status_color_loaded = "#10b981" if data_loaded else "#ef4444"
    status_color_cleaned = "#10b981" if data_cleaned else "#f59e0b" if data_loaded else "#ef4444"
    
    st.markdown(f"""
    <div class="premium-container" style="padding: 16px;">
        <div style="display: flex; align-items: center; margin: 8px 0;">
            <div style="
                width: 12px; 
                height: 12px; 
                border-radius: 50%; 
                background: {status_color_loaded}; 
                margin-right: 12px;
                box-shadow: 0 0 10px {status_color_loaded};
            "></div>
            <span style="color: var(--text-primary); font-size: 0.9rem;">Data Loaded</span>
        </div>
        <div style="display: flex; align-items: center; margin: 8px 0;">
            <div style="
                width: 12px; 
                height: 12px; 
                border-radius: 50%; 
                background: {status_color_cleaned}; 
                margin-right: 12px;
                box-shadow: 0 0 10px {status_color_cleaned};
            "></div>
            <span style="color: var(--text-primary); font-size: 0.9rem;">Data Cleaned</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE: HOME
# ============================================================================

def show_home_page():
    """Premium home page."""
    st.markdown("""
    <div class="hero-premium">
        <div style="text-align: center; position: relative; z-index: 1;">
            <div style="margin-bottom: 24px;">
                <span style="
                    display: inline-block;
                    padding: 12px 28px;
                    background: linear-gradient(135deg, #06b6d4, #3b82f6);
                    border-radius: 50px;
                    color: white;
                    font-size: 1rem;
                    font-weight: 700;
                    margin-right: 12px;
                ">✨ Premium Analytics</span>
                <span style="
                    display: inline-block;
                    padding: 12px 28px;
                    background: linear-gradient(135deg, #8b5cf6, #ec4899);
                    border-radius: 50px;
                    color: white;
                    font-size: 1rem;
                    font-weight: 700;
                ">🚀 v3.0</span>
            </div>
            <div class="hero-title-premium">Promo Pulse Simulator</div>
            <p style="color: var(--text-secondary); font-size: 1.3rem; margin: 0; line-height: 1.6;">
                Advanced Data Intelligence + Campaign Simulation Platform<br>
                <span style="color: var(--accent-cyan); font-weight: 600;">UAE Omnichannel Retail Analytics</span>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        # Feature Cards
        st.markdown('<div class="section-title-premium">✨ Platform Capabilities</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        features = [
            ("📂", "Data Upload", "Multi-format data ingestion with instant validation", "cyan"),
            ("🧹", "Data Rescue", "AI-powered quality detection & auto-fix engine", "blue"),
            ("🎯", "Smart Simulation", "What-if scenarios with constraint intelligence", "purple"),
            ("📊", "Advanced Analytics", "Executive & operational dashboards with ML insights", "pink")
        ]
        
        for col, (icon, title, desc, color) in zip([col1, col2, col3, col4], features):
            with col:
                st.markdown(f"""
                <div class="premium-container" style="height: 240px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;">
                    <div style="font-size: 56px; margin-bottom: 16px;">{icon}</div>
                    <div style="color: var(--accent-{color}); font-size: 1.15rem; font-weight: 700; margin-bottom: 12px;">{title}</div>
                    <div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.6;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Getting Started
        st.markdown('<div class="section-title-premium">🚀 Quick Start</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="alert-info">
            <strong style="font-size: 1.1rem;">👈 Navigate to Data Upload</strong><br>
            Load your e-commerce data files or use our sample dataset to explore the platform's full capabilities.
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Data loaded view
        st.markdown('<div class="section-title-premium">📊 Data Overview</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        counts = [
            ("Products", len(st.session_state.raw_products) if st.session_state.raw_products is not None else 0, "cyan"),
            ("Stores", len(st.session_state.raw_stores) if st.session_state.raw_stores is not None else 0, "blue"),
            ("Sales Records", len(st.session_state.raw_sales) if st.session_state.raw_sales is not None else 0, "purple"),
            ("Inventory", len(st.session_state.raw_inventory) if st.session_state.raw_inventory is not None else 0, "pink")
        ]
        
        for col, (label, count, color) in zip([col1, col2, col3, col4], counts):
            with col:
                st.markdown(create_metric_card_premium(label, f"{count:,}", color=color), unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.session_state.is_cleaned:
            st.markdown('<div class="alert-success">✅ <strong>Data Ready:</strong> Your data has been cleaned and validated. Ready for advanced analytics!</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-warning">⚠️ <strong>Action Required:</strong> Navigate to Data Rescue to validate and clean your data.</div>', unsafe_allow_html=True)
    
    show_footer()

# ============================================================================
# PAGE: ADVANCED EDA
# ============================================================================

def show_advanced_eda_page():
    """Advanced EDA page with 3 new insights."""
    st.markdown('<h1 class="page-title-premium" style="color: var(--accent-purple);">🔬 Advanced Exploratory Data Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: var(--text-secondary); font-size: 1.1rem;">Deep-dive analytics with cohort analysis, customer segmentation, and price elasticity insights</p>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.markdown('<div class="alert-warning">⚠️ Please load data first to access advanced analytics.</div>', unsafe_allow_html=True)
        show_footer()
        return
    
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    
    st.markdown("---")
    
    # TAB 1: Cohort Analysis
    st.markdown('<div class="section-title-premium">📅 Customer Cohort Retention Analysis</div>', unsafe_allow_html=True)
    
    with st.expander("ℹ️ What is Cohort Analysis?", expanded=False):
        st.markdown("""
        <div class="alert-info">
            Cohort analysis tracks customer behavior over time by grouping customers based on their first purchase month.
            This reveals retention patterns and helps identify when customers churn, enabling targeted re-engagement campaigns.
        </div>
        """, unsafe_allow_html=True)
    
    cohort_data = create_customer_cohort_analysis(sales_df)
    
    if cohort_data is not None and len(cohort_data) > 0:
        # Heatmap
        fig = px.imshow(
            cohort_data.values,
            labels=dict(x="Months Since First Purchase", y="Cohort Month", color="Retention %"),
            x=[f"Month {i}" for i in range(cohort_data.shape[1])],
            y=[str(m) for m in cohort_data.index],
            color_continuous_scale='RdYlGn',
            aspect="auto"
        )
        fig.update_layout(
            title="Customer Retention Heatmap by Cohort",
            height=500,
            template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Insights
        avg_retention_month1 = cohort_data.iloc[:, 1].mean() if cohort_data.shape[1] > 1 else 0
        avg_retention_month3 = cohort_data.iloc[:, 3].mean() if cohort_data.shape[1] > 3 else 0
        
        st.markdown(create_insight_card_premium(
            "Retention Insight",
            f"Average 1-month retention is {avg_retention_month1:.1f}%. By month 3, retention drops to {avg_retention_month3:.1f}%. Consider implementing a 30-day engagement campaign to improve early retention."
        ), unsafe_allow_html=True)
    else:
        st.info("Insufficient data for cohort analysis. Need multiple months of customer purchase history.")
    
    st.markdown("---")
    
    # TAB 2: RFM Segmentation
    st.markdown('<div class="section-title-premium">👥 RFM Customer Segmentation</div>', unsafe_allow_html=True)
    
    with st.expander("ℹ️ What is RFM Analysis?", expanded=False):
        st.markdown("""
        <div class="alert-info">
            RFM stands for Recency, Frequency, Monetary value. It segments customers based on:<br>
            • <strong>Recency:</strong> How recently they purchased<br>
            • <strong>Frequency:</strong> How often they purchase<br>
            • <strong>Monetary:</strong> How much they spend<br>
            This enables personalized marketing strategies for each segment.
        </div>
        """, unsafe_allow_html=True)
    
    rfm_data = create_rfm_segmentation(sales_df)
    
    if rfm_data is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            # Segment distribution
            segment_counts = rfm_data['segment'].value_counts().reset_index()
            segment_counts.columns = ['Segment', 'Count']
            
            fig = px.bar(
                segment_counts,
                x='Segment',
                y='Count',
                title='Customer Segment Distribution',
                color='Segment',
                color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b']
            )
            fig.update_layout(
                showlegend=False,
                template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Segment value
            segment_value = rfm_data.groupby('segment')['monetary'].sum().reset_index()
            segment_value.columns = ['Segment', 'Total Value']
            
            fig = px.pie(
                segment_value,
                values='Total Value',
                names='Segment',
                title='Revenue Contribution by Segment',
                color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b'],
                hole=0.4
            )
            fig.update_layout(template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        
        # Strategic recommendations
        champions_pct = (rfm_data[rfm_data['segment'] == 'Champions'].shape[0] / len(rfm_data) * 100) if len(rfm_data) > 0 else 0
        at_risk_pct = (rfm_data[rfm_data['segment'] == 'At Risk'].shape[0] / len(rfm_data) * 100) if len(rfm_data) > 0 else 0
        
        recommendations = [
            f"Champions represent {champions_pct:.1f}% of customers - prioritize VIP programs and exclusive offers",
            f"{at_risk_pct:.1f}% customers are 'At Risk' - implement win-back campaigns with personalized incentives",
            "Activate 'Hibernating' customers with re-engagement emails featuring best-seller recommendations"
        ]
        
        st.markdown(create_recommendation_premium("RFM-Based Marketing Strategy", recommendations), unsafe_allow_html=True)
    else:
        st.info("Unable to calculate RFM segments. Check data availability.")
    
    st.markdown("---")
    
    # TAB 3: Price Elasticity
    st.markdown('<div class="section-title-premium">💰 Price Elasticity & Discount Effectiveness</div>', unsafe_allow_html=True)
    
    with st.expander("ℹ️ What is Price Elasticity?", expanded=False):
        st.markdown("""
        <div class="alert-info">
            Price elasticity measures how demand responds to price changes (discounts).
            This analysis reveals the optimal discount levels that maximize volume without eroding profitability.
            Key insight: identify the "sweet spot" where discount ROI is highest.
        </div>
        """, unsafe_allow_html=True)
    
    elasticity_data = create_price_elasticity_analysis(sales_df, products_df)
    
    if elasticity_data is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                elasticity_data,
                x='discount_bin',
                y='total_qty',
                title='Total Quantity Sold by Discount Level',
                color='total_qty',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(
                elasticity_data,
                x='discount_bin',
                y='avg_qty_per_order',
                title='Average Quantity per Order by Discount',
                markers=True,
                line_shape='spline'
            )
            fig.update_traces(line=dict(color='#06b6d4', width=3), marker=dict(size=10))
            fig.update_layout(template='plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        
        # Find optimal discount
        optimal_idx = elasticity_data['avg_qty_per_order'].idxmax()
        optimal_discount = elasticity_data.iloc[optimal_idx]['discount_bin']
        optimal_qty = elasticity_data.iloc[optimal_idx]['avg_qty_per_order']
        
        st.markdown(create_insight_card_premium(
            "Optimal Discount Strategy",
            f"The {optimal_discount} discount range shows the highest average quantity per order ({optimal_qty:.2f} units). This is your optimal discount sweet spot that balances volume lift with margin preservation."
        ), unsafe_allow_html=True)
    else:
        st.info("Unable to calculate price elasticity. Check discount and price data.")
    
    show_footer()

# ============================================================================
# MAIN ROUTER
# ============================================================================

if page == "🏠 Home":
    show_home_page()
elif page == "🔬 Advanced EDA":
    show_advanced_eda_page()
else:
    # For other pages, show placeholder (you'd integrate your existing pages here)
    st.markdown(f'<h1 class="page-title-premium">🚧 {page}</h1>', unsafe_allow_html=True)
    st.markdown('<div class="alert-info">This page is being migrated to the new premium theme. Check back soon!</div>', unsafe_allow_html=True)
    show_footer()

# ============================================================================
# UAE Promo Pulse Simulator + Data Rescue Dashboard
# PREMIUM ENHANCED VERSION v3.0 - Advanced EDA & Theme Toggle
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io

# Import custom modules
from modules.cleaner import DataCleaner
from modules.simulator import Simulator
from modules.utils import (
    CONFIG, SIMULATOR_CONFIG, CHART_THEME, 
    style_plotly_chart, load_sample_data, get_data_summary
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="UAE Promo Pulse Simulator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# THEME MANAGEMENT
# ============================================================================

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Theme colors
THEMES = {
    'dark': {
        'bg_primary': '#0a0a0f',
        'bg_secondary': '#12121a',
        'bg_card': '#16161f',
        'bg_card_hover': '#1e1e2d',
        'text_primary': '#f1f5f9',
        'text_secondary': '#94a3b8',
        'text_muted': '#64748b',
        'border_color': '#2d2d3a',
        'gradient_1': 'rgba(6, 182, 212, 0.08)',
        'gradient_2': 'rgba(139, 92, 246, 0.08)',
        'gradient_3': 'rgba(236, 72, 153, 0.05)',
    },
    'light': {
        'bg_primary': '#ffffff',
        'bg_secondary': '#f8fafc',
        'bg_card': '#ffffff',
        'bg_card_hover': '#f1f5f9',
        'text_primary': '#0f172a',
        'text_secondary': '#475569',
        'text_muted': '#64748b',
        'border_color': '#e2e8f0',
        'gradient_1': 'rgba(6, 182, 212, 0.05)',
        'gradient_2': 'rgba(139, 92, 246, 0.05)',
        'gradient_3': 'rgba(236, 72, 153, 0.03)',
    }
}

current_theme = THEMES[st.session_state.theme]

# ============================================================================
# PREMIUM CSS WITH THEME SUPPORT
# ============================================================================

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    :root {{
        --bg-primary: {current_theme['bg_primary']};
        --bg-secondary: {current_theme['bg_secondary']};
        --bg-card: {current_theme['bg_card']};
        --bg-card-hover: {current_theme['bg_card_hover']};
        --text-primary: {current_theme['text_primary']};
        --text-secondary: {current_theme['text_secondary']};
        --text-muted: {current_theme['text_muted']};
        --border-color: {current_theme['border_color']};
        
        --accent-cyan: #06b6d4;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-pink: #ec4899;
        --accent-green: #10b981;
        --accent-orange: #f59e0b;
        --accent-red: #ef4444;
        --accent-teal: #14b8a6;
        
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, {'0.1' if st.session_state.theme == 'light' else '0.3'});
        --shadow-md: 0 4px 16px rgba(0, 0, 0, {'0.12' if st.session_state.theme == 'light' else '0.4'});
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, {'0.15' if st.session_state.theme == 'light' else '0.5'});
    }}
    
    /* ANIMATIONS */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ box-shadow: 0 0 20px rgba(6, 182, 212, 0.3); }}
        50% {{ box-shadow: 0 0 40px rgba(6, 182, 212, 0.6); }}
    }}
    
    @keyframes shimmer {{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}
    
    /* HIDE DEFAULTS */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* MAIN BACKGROUND */
    .stApp {{
        background: var(--bg-primary);
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
        transition: background 0.3s ease;
    }}
    
    /* SIDEBAR */
    [data-testid="stSidebar"] {{
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
        transition: background 0.3s ease;
    }}
    
    /* THEME TOGGLE BUTTON */
    .theme-toggle {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
        border: none;
        border-radius: 50%;
        width: 56px;
        height: 56px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: var(--shadow-lg);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    
    .theme-toggle:hover {{
        transform: scale(1.1) rotate(15deg);
        box-shadow: 0 12px 48px rgba(6, 182, 212, 0.5);
    }}
    
    /* PREMIUM CONTAINER */
    .premium-container {{
        background: var(--bg-card);
        border-radius: 20px;
        padding: 32px;
        margin: 24px 0;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
    }}
    
    .premium-container:hover {{
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }}
    
    /* HERO SECTION */
    .hero-premium {{
        background: linear-gradient(135deg, 
            {current_theme['gradient_1']} 0%, 
            {current_theme['gradient_2']} 50%, 
            {current_theme['gradient_3']} 100%);
        border-radius: 28px;
        padding: 64px 48px;
        margin-bottom: 48px;
        border: 2px solid var(--border-color);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.8s ease-out;
    }}
    
    .hero-premium::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.1) 0%, transparent 50%);
        animation: float 8s ease-in-out infinite;
    }}
    
    .hero-title-premium {{
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 40%, #8b5cf6 70%, #ec4899 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 24px;
        position: relative;
        z-index: 1;
        line-height: 1.1;
        letter-spacing: -2px;
    }}
    
    /* METRIC CARDS - PREMIUM */
    .metric-card-premium {{
        background: var(--bg-card);
        border-radius: 20px;
        padding: 28px 24px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card-premium::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple));
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    
    .metric-card-premium:hover {{
        transform: translateY(-8px) scale(1.02);
        border-color: var(--accent-cyan);
        box-shadow: var(--shadow-lg);
    }}
    
    .metric-card-premium:hover::before {{
        opacity: 1;
    }}
    
    .metric-label-premium {{
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
        margin-bottom: 8px;
    }}
    
    .metric-value-premium {{
        font-size: 2.25rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        margin: 12px 0;
    }}
    
    .metric-delta {{
        font-size: 0.9rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    
    /* PAGE TITLES */
    .page-title-premium {{
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 16px;
        line-height: 1.1;
        letter-spacing: -1.5px;
        color: var(--text-primary);
    }}
    
    .section-title-premium {{
        font-size: 2rem;
        font-weight: 700;
        margin: 32px 0 20px 0;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    
    .section-title-premium::after {{
        content: '';
        flex: 1;
        height: 2px;
        background: linear-gradient(90deg, var(--border-color), transparent);
    }}
    
    /* FILTER CONTAINER */
    .filter-container {{
        background: var(--bg-card);
        border-radius: 16px;
        padding: 24px;
        margin: 24px 0;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }}
    
    /* CHART CONTAINER */
    .chart-container {{
        background: var(--bg-card);
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }}
    
    .chart-container:hover {{
        box-shadow: var(--shadow-md);
    }}
    
    /* INSIGHT CARDS */
    .insight-premium {{
        background: linear-gradient(135deg, 
            rgba(139, 92, 246, {'0.08' if st.session_state.theme == 'dark' else '0.05'}) 0%, 
            rgba(236, 72, 153, {'0.08' if st.session_state.theme == 'dark' else '0.05'}) 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        margin: 16px 0;
        transition: all 0.3s ease;
    }}
    
    .insight-premium:hover {{
        transform: translateX(8px);
        border-color: var(--accent-purple);
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.2);
    }}
    
    .insight-title-premium {{
        color: var(--accent-purple);
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    .insight-text-premium {{
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.7;
    }}
    
    /* RECOMMENDATION BOX */
    .recommendation-premium {{
        background: linear-gradient(135deg, 
            rgba(16, 185, 129, {'0.12' if st.session_state.theme == 'dark' else '0.08'}) 0%, 
            rgba(6, 182, 212, {'0.12' if st.session_state.theme == 'dark' else '0.08'}) 100%);
        border-radius: 20px;
        padding: 32px;
        border: 2px solid rgba(16, 185, 129, 0.3);
        margin: 24px 0;
        position: relative;
        overflow: hidden;
    }}
    
    .recommendation-premium::before {{
        content: '💡';
        position: absolute;
        top: 24px;
        right: 24px;
        font-size: 3rem;
        opacity: 0.3;
    }}
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        background: transparent;
        border-bottom: 2px solid var(--border-color);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: var(--bg-card);
        border-radius: 12px 12px 0 0;
        color: var(--text-secondary);
        padding: 14px 28px;
        border: 1px solid var(--border-color);
        border-bottom: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: var(--bg-card-hover);
        border-color: var(--accent-cyan);
        transform: translateY(-3px);
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
    }}
    
    /* BUTTONS */
    .stButton > button {{
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 16px 36px;
        font-weight: 700;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.3);
        letter-spacing: 0.5px;
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
        box-shadow: 0 12px 36px rgba(59, 130, 246, 0.5);
        transform: translateY(-3px);
    }}
    
    /* ALERTS */
    .alert-info {{
        background: linear-gradient(135deg, 
            rgba(6, 182, 212, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 0%, 
            rgba(59, 130, 246, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 100%);
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid var(--accent-cyan);
        margin: 16px 0;
        color: var(--text-primary);
    }}
    
    .alert-success {{
        background: linear-gradient(135deg, 
            rgba(16, 185, 129, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 0%, 
            rgba(20, 184, 166, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 100%);
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid var(--accent-green);
        margin: 16px 0;
        color: var(--text-primary);
    }}
    
    .alert-warning {{
        background: linear-gradient(135deg, 
            rgba(245, 158, 11, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 0%, 
            rgba(251, 146, 60, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 100%);
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid var(--accent-orange);
        margin: 16px 0;
        color: var(--text-primary);
    }}
    
    /* DATAFRAME */
    .stDataFrame {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--border-color);
    }}
    
    /* DIVIDER */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 40px 0;
    }}
    
    /* FOOTER */
    .footer-premium {{
        background: var(--bg-secondary);
        padding: 48px;
        text-align: center;
        border-top: 1px solid var(--border-color);
        margin-top: 80px;
        border-radius: 28px 28px 0 0;
        position: relative;
    }}
    
    .footer-premium::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple), var(--accent-pink));
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_metric_card_premium(label, value, delta=None, delta_type="positive", color="cyan"):
    """Create premium metric card."""
    colors = {
        'cyan': '#06b6d4', 'blue': '#3b82f6', 'purple': '#8b5cf6',
        'pink': '#ec4899', 'green': '#10b981', 'orange': '#f59e0b',
        'teal': '#14b8a6', 'red': '#ef4444'
    }
    accent = colors.get(color, '#06b6d4')
    
    delta_html = ""
    if delta:
        delta_color = "#10b981" if delta_type == "positive" else "#ef4444"
        delta_icon = "↑" if delta_type == "positive" else "↓"
        delta_html = f'<div class="metric-delta" style="color: {delta_color};">{delta_icon} {delta}</div>'
    else:
        delta_html = '<div style="height: 28px;"></div>'
    
    return f"""
    <div class="metric-card-premium">
        <div class="metric-label-premium">{label}</div>
        <div class="metric-value-premium" style="color: {accent};">{value}</div>
        {delta_html}
    </div>
    """

def create_insight_card_premium(title, text):
    """Create premium insight card."""
    return f"""
    <div class="insight-premium">
        <div class="insight-title-premium">💡 {title}</div>
        <div class="insight-text-premium">{text}</div>
    </div>
    """

def create_recommendation_premium(title, items):
    """Create premium recommendation box."""
    items_html = "<br>".join([f"• {item}" for item in items])
    return f"""
    <div class="recommendation-premium">
        <div style="color: #10b981; font-size: 1.4rem; font-weight: 800; margin-bottom: 16px;">📋 {title}</div>
        <div style="color: var(--text-secondary); font-size: 1.05rem; line-height: 1.9;">{items_html}</div>
    </div>
    """

def show_footer():
    """Premium footer."""
    st.markdown("""
    <div class="footer-premium">
        <div style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 12px;">
            🚀 UAE Promo Pulse Simulator - Premium Analytics Platform
        </div>
        <div style="color: var(--text-muted); font-size: 1rem; margin-bottom: 16px;">
            Advanced Data Rescue & Campaign Simulation
        </div>
        <div style="
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
            font-size: 1.15rem;
        ">Kartik Joshi • Gagandeep Singh • Samuel Alex • Prem Kukreja</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# ADVANCED EDA FUNCTIONS
# ============================================================================

def create_customer_cohort_analysis(sales_df):
    """EDA Insight 1: Customer Cohort Retention Analysis."""
    if 'order_time' not in sales_df.columns or 'order_id' not in sales_df.columns:
        return None
    
    sales_copy = sales_df.copy()
    sales_copy['order_time'] = pd.to_datetime(sales_copy['order_time'], errors='coerce')
    sales_copy['order_month'] = sales_copy['order_time'].dt.to_period('M')
    
    # Simulate customer_id if not present
    if 'customer_id' not in sales_copy.columns:
        sales_copy['customer_id'] = sales_copy['order_id'].apply(lambda x: hash(str(x)) % 10000)
    
    # First purchase month
    first_purchase = sales_copy.groupby('customer_id')['order_month'].min().reset_index()
    first_purchase.columns = ['customer_id', 'cohort_month']
    
    sales_copy = sales_copy.merge(first_purchase, on='customer_id')
    sales_copy['months_since_first'] = (sales_copy['order_month'] - sales_copy['cohort_month']).apply(lambda x: x.n)
    
    # Cohort table
    cohort_data = sales_copy.groupby(['cohort_month', 'months_since_first'])['customer_id'].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index='cohort_month', columns='months_since_first', values='customer_id')
    
    # Calculate retention rates
    cohort_size = cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.divide(cohort_size, axis=0) * 100
    
    return retention

def create_rfm_segmentation(sales_df):
    """EDA Insight 2: RFM (Recency, Frequency, Monetary) Customer Segmentation."""
    if 'order_time' not in sales_df.columns:
        return None
    
    sales_copy = sales_df.copy()
    sales_copy['order_time'] = pd.to_datetime(sales_copy['order_time'], errors='coerce')
    
    # Simulate customer_id
    if 'customer_id' not in sales_copy.columns:
        sales_copy['customer_id'] = sales_copy['order_id'].apply(lambda x: hash(str(x)) % 10000)
    
    # Calculate revenue per order
    if 'selling_price_aed' in sales_copy.columns and 'qty' in sales_copy.columns:
        sales_copy['revenue'] = pd.to_numeric(sales_copy['selling_price_aed'], errors='coerce') * pd.to_numeric(sales_copy['qty'], errors='coerce')
    else:
        return None
    
    snapshot_date = sales_copy['order_time'].max() + timedelta(days=1)
    
    rfm = sales_copy.groupby('customer_id').agg({
        'order_time': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'count',
        'revenue': 'sum'
    }).reset_index()
    
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # Score RFM
    rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
    
    # Segment customers
    def segment_customer(row):
        if row['r_score'] >= 4 and row['f_score'] >= 4:
            return 'Champions'
        elif row['r_score'] >= 3 and row['f_score'] >= 3:
            return 'Loyal Customers'
        elif row['r_score'] >= 4 and row['f_score'] <= 2:
            return 'Promising'
        elif row['r_score'] <= 2 and row['f_score'] >= 3:
            return 'At Risk'
        elif row['r_score'] <= 2 and row['f_score'] <= 2:
            return 'Hibernating'
        else:
            return 'Need Attention'
    
    rfm['segment'] = rfm.apply(segment_customer, axis=1)
    
    return rfm

def create_price_elasticity_analysis(sales_df, products_df):
    """EDA Insight 3: Price Elasticity & Discount Effectiveness Analysis."""
    if 'discount_pct' not in sales_df.columns or 'selling_price_aed' not in sales_df.columns:
        return None
    
    sales_copy = sales_df.copy()
    sales_copy['discount_pct'] = pd.to_numeric(sales_copy['discount_pct'], errors='coerce').fillna(0)
    sales_copy['selling_price_aed'] = pd.to_numeric(sales_copy['selling_price_aed'], errors='coerce')
    sales_copy['qty'] = pd.to_numeric(sales_copy['qty'], errors='coerce')
    
    # Bin discounts
    sales_copy['discount_bin'] = pd.cut(sales_copy['discount_pct'], 
                                         bins=[-1, 0, 5, 10, 15, 20, 100],
                                         labels=['No Discount', '1-5%', '6-10%', '11-15%', '16-20%', '20%+'])
    
    # Aggregate by discount bin
    elasticity = sales_copy.groupby('discount_bin').agg({
        'qty': 'sum',
        'selling_price_aed': 'mean',
        'order_id': 'count'
    }).reset_index()
    
    elasticity.columns = ['discount_bin', 'total_qty', 'avg_price', 'num_orders']
    elasticity['avg_qty_per_order'] = elasticity['total_qty'] / elasticity['num_orders']
    
    return elasticity

# ============================================================================
