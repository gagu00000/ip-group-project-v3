# ============================================================================
# UAE Pulse Simulator + Data Rescue Dashboard
# Main Streamlit Application - PREMIUM v4.0
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Import custom modules
from modules.cleaner import DataCleaner
from modules.simulator import Simulator
from modules.utils import (
    CONFIG, SIMULATOR_CONFIG, CHART_THEME, 
    style_plotly_chart, load_sample_data, get_data_summary
)

# ============================================================================
# IMPORT PREMIUM CSS LOADER
# ============================================================================
from styles import (
    load_premium_css,
    get_theme_colors,
    create_metric_card,
    create_insight_card,
    create_alert,
    create_section_title,
    create_page_title,
    create_recommendation_box,
    create_footer,
    create_status_dot
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="UAE Pulse Simulator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)



# ============================================================================
# THEME STATE MANAGEMENT
# ============================================================================

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# ============================================================================
# LOAD PREMIUM CSS (This replaces your entire 500+ line CSS block!)
# ============================================================================

load_premium_css(theme=st.session_state.theme, include_orbs=True)

# Get theme colors for Plotly charts
theme_colors = get_theme_colors(st.session_state.theme)

# ============================================================================
# CUSTOM HELPER FUNCTIONS (Keep these for backward compatibility)
# ============================================================================

def create_feature_card(icon, title, description, color="cyan"):
    """Create a styled feature card with border effect and hover."""
    colors = {
        "cyan": "#06b6d4",
        "blue": "#3b82f6",
        "purple": "#8b5cf6",
        "pink": "#ec4899",
        "green": "#10b981",
        "orange": "#f59e0b",
        "teal": "#14b8a6",
    }
    primary = colors.get(color, colors["cyan"])
    
    return f"""
    <div class="premium-container feature-card" style="height: 220px; text-align: center; padding: 30px 20px;">
        <div style="font-size: 48px; margin-bottom: 16px; animation: float 3s ease-in-out infinite;">{icon}</div>
        <div style="color: {primary}; font-size: 1.15rem; font-weight: 700; margin-bottom: 10px;">{title}</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">{description}</div>
    </div>
    """

def create_info_card(content):
    """Create an info card."""
    return f'<div class="alert-info">{content}</div>'

def create_success_card(content):
    """Create a success card."""
    return f'<div class="alert-success">{content}</div>'

def create_warning_card(content):
    """Create a warning card."""
    return f'<div class="alert-warning">{content}</div>'

def create_error_card(content):
    """Create an error card."""
    return f'<div class="alert-error">{content}</div>'

def show_footer():
    """Display the footer with team names."""
    st.markdown(create_footer(
        "🚀 UAE Pulse Simulator + Data Rescue Dashboard",
        "Built with ❤️ by",
        "Kartik Joshi • Gagandeep Singh • Samuel Alex • Prem Kukreja"
    ), unsafe_allow_html=True)

def generate_insights(kpis, city_kpis=None, channel_kpis=None, cat_kpis=None):
    """Generate business insights based on KPIs."""
    insights = []
    
    if kpis.get('total_revenue', 0) > 0:
        aov = kpis.get('avg_order_value', 0)
        if aov > 500:
            insights.append(("High-Value Customers", f"Average order value is AED {aov:,.0f}, indicating premium customer segment."))
        elif aov < 200:
            insights.append(("Growth Opportunity", f"Average order value is AED {aov:,.0f}. Bundle offers could increase basket size."))
    
    margin = kpis.get('profit_margin_pct', 0)
    if margin > 25:
        insights.append(("Strong Margins", f"Profit margin at {margin:.1f}% is healthy."))
    elif margin < 15:
        insights.append(("Margin Alert", f"Profit margin at {margin:.1f}% is below benchmark."))
    
    return insights[:3]

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

# ============================================================================
# SIDEBAR NAVIGATION (Updated with theme toggle)
# ============================================================================

with st.sidebar:
    # Logo and Title
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <div style="text-align: center; margin-top: -20px; padding-bottom: 15px;">
            <div style="font-size: 48px; margin-bottom: 5px; animation: float 3s ease-in-out infinite;">🛒</div>
            <div class="gradient-text" style="font-size: 26px; font-weight: 800;">UAE Pulse</div>
            <div style="color: var(--text-muted); font-size: 13px;">Simulator + Data Rescue</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Theme toggle button
        theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
        if st.button(theme_icon, key='theme_toggle', help="Toggle Theme"):
            toggle_theme()
            st.rerun()
    
    st.markdown("---")
    
    # Navigation
    st.markdown('<p style="color: var(--accent-pink); font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📍 NAVIGATION</p>', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📂 Data", "🧹 Cleaner", "👔 Executive", "📋 Manager", "🎯 Simulator", "📊 Analytics"],
        label_visibility="collapsed"
        key="main_navigation"
    )
    
    st.markdown("---")
    
    # Data Status with breathing dots
    st.markdown('<p style="color: var(--accent-blue); font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📡 STATUS</p>', unsafe_allow_html=True)
    
    data_loaded = st.session_state.data_loaded
    data_cleaned = st.session_state.is_cleaned
    
    status_class_loaded = "green" if data_loaded else "red"
    status_class_cleaned = "green" if data_cleaned else ("orange" if data_loaded else "red")
    
    st.markdown(f"""
    <div class="premium-container" style="padding: 16px;">
        <div style="display: flex; align-items: center; margin: 10px 0;">
            <div class="status-dot {status_class_loaded}" style="margin-right: 12px;"></div>
            <span style="color: var(--text-primary); font-size: 0.9rem;">Data Loaded</span>
        </div>
        <div style="display: flex; align-items: center; margin: 10px 0;">
            <div class="status-dot {status_class_cleaned}" style="margin-right: 12px;"></div>
            <span style="color: var(--text-primary); font-size: 0.9rem;">Data Cleaned</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats (rest of your sidebar code...)
    if st.session_state.data_loaded:
        st.markdown("---")
        st.markdown('<p style="color: var(--accent-purple); font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📈 QUICK STATS</p>', unsafe_allow_html=True)
        
        sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
        if sales_df is not None:
            total_records = len(sales_df)
            try:
                qty = pd.to_numeric(sales_df['qty'], errors='coerce').fillna(0)
                price = pd.to_numeric(sales_df['selling_price_aed'], errors='coerce').fillna(0)
                total_revenue = (qty * price).sum()
            except:
                total_revenue = 0
            
            st.markdown(f"""
            <div class="premium-container" style="padding: 15px;">
                <div style="margin-bottom: 12px;">
                    <span style="color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase;">RECORDS</span><br>
                    <span style="color: var(--accent-cyan); font-weight: 700; font-size: 1.4rem;">{total_records:,}</span>
                </div>
                <div>
                    <span style="color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase;">REVENUE</span><br>
                    <span style="color: var(--accent-green); font-weight: 700; font-size: 1.2rem;">AED {total_revenue:,.0f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS FOR UI
# ============================================================================

def create_metric_card(label, value, delta=None, delta_type="positive", color="cyan"):
    """Create a styled metric card with EXACT uniform size."""
    delta_html = ""
    if delta:
        delta_class = "metric-delta-positive" if delta_type == "positive" else "metric-delta-negative"
        delta_icon = "↑" if delta_type == "positive" else "↓"
        delta_html = f'<div class="{delta_class}">{delta_icon} {delta}</div>'
    else:
        delta_html = '<div style="height: 22px;"></div>'  # Spacer for uniform height
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value metric-value-{color}">{value}</div>
        {delta_html}
    </div>
    """
def create_feature_card(icon, title, description, color="cyan"):
    """Create a styled feature card with border effect and hover."""
    colors = {
        "cyan": "#06b6d4",
        "blue": "#3b82f6",
        "purple": "#8b5cf6",
        "pink": "#ec4899",
        "green": "#10b981",
        "orange": "#f59e0b",
        "teal": "#14b8a6",
    }
    primary = colors.get(color, colors["cyan"])
    
    return f"""
    <style>
        .feature-card-{color} {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
            border-radius: 16px;
            padding: 30px 20px;
            text-align: center;
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-left: 4px solid {primary};
            height: 220px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .feature-card-{color}:hover {{
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4), 0 0 30px {primary}44;
            border-color: {primary};
        }}
    </style>
    <div class="feature-card-{color}">
        <div style="font-size: 42px; margin-bottom: 12px;">{icon}</div>
        <div style="color: {primary}; font-size: 1.1rem; font-weight: 700; margin-bottom: 8px;">{title}</div>
        <div style="color: #94a3b8; font-size: 0.85rem; line-height: 1.5;">{description}</div>
    </div>
    """
    
    return f"""
    <div style="
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border-radius: 16px;
        padding: 30px 24px;
        text-align: center;
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-left: 4px solid {primary};
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    "
    onmouseover="
        this.style.transform='translateY(-5px)';
        this.style.boxShadow='0 20px 40px rgba(0,0,0,0.3), 0 0 30px {primary}33';
        this.style.borderLeftColor='{secondary}';
    "
    onmouseout="
        this.style.transform='translateY(0)';
        this.style.boxShadow='none';
        this.style.borderLeftColor='{primary}';
    ">
        <div style="
            font-size: 48px;
            margin-bottom: 16px;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
        ">{icon}</div>
        <div style="
            color: {primary};
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        ">{title}</div>
        <div style="
            color: #94a3b8;
            font-size: 0.9rem;
            line-height: 1.5;
        ">{description}</div>
    </div>
    """

def create_info_card(content):
    """Create an info card."""
    return f'<div class="info-card">{content}</div>'

def create_success_card(content):
    """Create a success card."""
    return f'<div class="success-card">✅ {content}</div>'

def create_warning_card(content):
    """Create a warning card."""
    return f'<div class="warning-card">⚠️ {content}</div>'

def create_error_card(content):
    """Create an error card."""
    return f'<div class="error-card">❌ {content}</div>'

def create_insight_card(title, insight_text):
    """Create a business insight card."""
    return f"""
    <div class="insight-card">
        <div class="insight-title">💡 {title}</div>
        <div class="insight-text">{insight_text}</div>
    </div>
    """

def show_footer():
    """Display the footer with team names."""
    st.markdown("""
    <div class="footer">
        <div class="footer-title">🚀 UAE Pulse Simulator + Data Rescue Dashboard</div>
        <div class="footer-subtitle">Built with ❤️ by</div>
        <div class="footer-names">Kartik Joshi • Gagandeep Singh • Samuel Alex • Prem Kukreja</div>
    </div>
    """, unsafe_allow_html=True)

def generate_insights(kpis, city_kpis=None, channel_kpis=None, cat_kpis=None):
    """Generate business insights based on KPIs."""
    insights = []
    
    # Revenue insight
    if kpis.get('total_revenue', 0) > 0:
        aov = kpis.get('avg_order_value', 0)
        if aov > 500:
            insights.append(("High-Value Customers", f"Average order value is AED {aov:,.0f}, indicating premium customer segment. Consider upselling strategies."))
        elif aov < 200:
            insights.append(("Growth Opportunity", f"Average order value is AED {aov:,.0f}. Bundle offers could increase basket size by 15-25%."))
    
    # Margin insight
    margin = kpis.get('profit_margin_pct', 0)
    if margin > 25:
        insights.append(("Strong Margins", f"Profit margin at {margin:.1f}% is healthy. Room for strategic discounts without hurting profitability."))
    elif margin < 15:
        insights.append(("Margin Alert", f"Profit margin at {margin:.1f}% is below industry benchmark. Review pricing strategy and costs."))
    
    # Return rate insight
    return_rate = kpis.get('return_rate_pct', 0)
    if return_rate > 10:
        insights.append(("High Returns", f"Return rate of {return_rate:.1f}% is above normal. Investigate product quality or description accuracy."))
    elif return_rate < 3:
        insights.append(("Excellent Quality", f"Low return rate of {return_rate:.1f}% indicates high customer satisfaction."))
    
    # City insight
    if city_kpis is not None and len(city_kpis) > 0:
        top_city = city_kpis.iloc[0]['city'] if 'city' in city_kpis.columns else None
        if top_city:
            top_revenue = city_kpis.iloc[0]['revenue']
            total_revenue = city_kpis['revenue'].sum()
            pct = (top_revenue / total_revenue * 100) if total_revenue > 0 else 0
            insights.append(("Market Concentration", f"{top_city} contributes {pct:.0f}% of total revenue. {'Diversify to reduce risk.' if pct > 50 else 'Healthy market distribution.'}"))
    
    return insights[:3]  # Return top 3 insights

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

    # ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

with st.sidebar:
    # Logo and Title
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <div style="text-align: center; margin-top: -20px; padding-bottom: 15px;">
            <div style="font-size: 48px; margin-bottom: 5px; animation: float 3s ease-in-out infinite;">🛒</div>
            <div class="gradient-text" style="font-size: 26px; font-weight: 800;">UAE Pulse</div>
            <div style="color: var(--text-muted); font-size: 13px;">Simulator + Data Rescue</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Theme toggle button
        theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
        if st.button(theme_icon, key='theme_toggle', help="Toggle Theme"):
            toggle_theme()
            st.rerun()
    
    st.markdown("---")
    
    # Navigation
    st.markdown('<p style="color: var(--accent-pink); font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📍 NAVIGATION</p>', unsafe_allow_html=True)
    
    # 👇 ADD key="main_navigation" HERE
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📂 Data", "🧹 Cleaner", "👔 Executive", "📋 Manager", "🎯 Simulator", "📊 Analytics"],
        label_visibility="collapsed",
        key="main_navigation"  # ✅ THIS FIXES THE ERROR
    )
    
    st.markdown("---")
    
    # Data Status
    st.markdown('<p style="color: var(--accent-blue); font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📡 STATUS</p>', unsafe_allow_html=True)
    
    data_loaded = st.session_state.get('data_loaded', False)
    data_cleaned = st.session_state.get('is_cleaned', False)
    
    status_class_loaded = "green" if data_loaded else "red"
    status_class_cleaned = "green" if data_cleaned else ("orange" if data_loaded else "red")
    
    st.markdown(f"""
    <div class="premium-container" style="padding: 16px;">
        <div style="display: flex; align-items: center; margin: 10px 0;">
            <div class="status-dot {status_class_loaded}" style="margin-right: 12px;"></div>
            <span style="color: var(--text-primary); font-size: 0.9rem;">Data Loaded</span>
        </div>
        <div style="display: flex; align-items: center; margin: 10px 0;">
            <div class="status-dot {status_class_cleaned}" style="margin-right: 12px;"></div>
            <span style="color: var(--text-primary); font-size: 0.9rem;">Data Cleaned</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown('<p style="color: #ec4899; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📍 NAVIGATION</p>', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📂 Data", "🧹 Cleaner", "👔 Executive", "📋 Manager", "🎯 Simulator", "📊 Analytics"],
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
    <div style="
        background: linear-gradient(135deg, #16161f 0%, #1a1a24 100%);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #2d2d3a;
    ">
        <div style="display: flex; align-items: center; margin: 8px 0;">
            <div style="
                width: 12px; 
                height: 12px; 
                border-radius: 50%; 
                background: {status_color_loaded}; 
                margin-right: 12px;
                box-shadow: 0 0 10px {status_color_loaded};
            "></div>
            <span style="color: #e0e0e0; font-size: 0.9rem;">Data Loaded</span>
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
            <span style="color: #e0e0e0; font-size: 0.9rem;">Data Cleaned</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats
    if st.session_state.data_loaded:
        st.markdown("---")
        st.markdown('<p style="color: #8b5cf6; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📈 QUICK STATS</p>', unsafe_allow_html=True)
        
        sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
        if sales_df is not None:
            total_records = len(sales_df)
            try:
                qty = pd.to_numeric(sales_df['qty'], errors='coerce').fillna(0)
                price = pd.to_numeric(sales_df['selling_price_aed'], errors='coerce').fillna(0)
                total_revenue = (qty * price).sum()
            except:
                total_revenue = 0
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #16161f 0%, #1a1a24 100%);
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #2d2d3a;
            ">
                <div style="margin-bottom: 12px;">
                    <span style="color: #64748b; font-size: 0.8rem; text-transform: uppercase;">RECORDS</span><br>
                    <span style="color: #06b6d4; font-weight: 700; font-size: 1.4rem;">{total_records:,}</span>
                </div>
                <div>
                    <span style="color: #64748b; font-size: 0.8rem; text-transform: uppercase;">REVENUE</span><br>
                    <span style="color: #10b981; font-weight: 700; font-size: 1.2rem;">AED {total_revenue:,.0f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def validate_file_columns(df, file_type):
    """Validate that uploaded file has required columns for its type."""
    
    required_columns = {
        'products': {
            'must_have': ['sku'],
            'should_have': ['product_name', 'category', 'cost', 'price'],
            'alternate_names': {
                'sku': ['sku', 'SKU', 'product_id', 'ProductID', 'product_sku'],
                'product_name': ['product_name', 'name', 'product', 'ProductName'],
                'category': ['category', 'Category', 'product_category', 'cat'],
                'cost': ['cost', 'cost_aed', 'Cost', 'unit_cost'],
                'price': ['price', 'selling_price', 'selling_price_aed', 'Price', 'unit_price']
            }
        },
        'stores': {
            'must_have': ['store_id'],
            'should_have': ['city', 'channel'],
            'alternate_names': {
                'store_id': ['store_id', 'StoreID', 'store', 'Store'],
                'city': ['city', 'City', 'location', 'store_city'],
                'channel': ['channel', 'Channel', 'sales_channel', 'store_channel']
            }
        },
        'sales': {
            'must_have': ['sku', 'store_id'],
            'should_have': ['date', 'qty', 'revenue'],
            'alternate_names': {
                'sku': ['sku', 'SKU', 'product_id', 'ProductID'],
                'store_id': ['store_id', 'StoreID', 'store', 'Store'],
                'date': ['date', 'Date', 'transaction_date', 'sale_date', 'order_date'],
                'qty': ['qty', 'quantity', 'Qty', 'Quantity', 'units'],
                'revenue': ['revenue', 'Revenue', 'sales', 'total', 'amount']
            }
        },
        'inventory': {
            'must_have': ['sku', 'store_id'],
            'should_have': ['stock_on_hand'],
            'alternate_names': {
                'sku': ['sku', 'SKU', 'product_id', 'ProductID'],
                'store_id': ['store_id', 'StoreID', 'store', 'Store'],
                'stock_on_hand': ['stock_on_hand', 'stock', 'inventory', 'qty', 'quantity', 'on_hand']
            }
        }
    }
    
    if file_type not in required_columns:
        return True, "Unknown file type", []
    
    config = required_columns[file_type]
    df_columns = [col.lower().strip() for col in df.columns]
    df_columns_original = list(df.columns)
    
    missing_must_have = []
    found_columns = []
    
    # Check must-have columns
    for col in config['must_have']:
        alternates = config['alternate_names'].get(col, [col])
        found = False
        for alt in alternates:
            if alt.lower() in df_columns:
                found = True
                found_columns.append(alt)
                break
        if not found:
            missing_must_have.append(col)
    
    # Check should-have columns (for better confidence)
    should_have_found = 0
    for col in config['should_have']:
        alternates = config['alternate_names'].get(col, [col])
        for alt in alternates:
            if alt.lower() in df_columns:
                should_have_found += 1
                found_columns.append(alt)
                break
    
    # Validation result
    if len(missing_must_have) > 0:
        return False, f"Missing required columns: {', '.join(missing_must_have)}", found_columns
    
    # Check if at least some expected columns exist
    total_expected = len(config['must_have']) + len(config['should_have'])
    total_found = len(config['must_have']) - len(missing_must_have) + should_have_found
    confidence = total_found / total_expected * 100
    
    if confidence < 40:
        return False, f"This doesn't look like a {file_type} file. Only {confidence:.0f}% columns match.", found_columns
    
    return True, f"Valid {file_type} file ({confidence:.0f}% confidence)", found_columns
    
# ============================================================================
# PAGE: HOME
# ============================================================================

# ============================================================================
# PAGE: HOME (FIXED - BIG TITLE, BETTER LAYOUT)
# ============================================================================

def show_home_page():
    """Display the home page - always static, never changes."""
    
    # ===== HERO SECTION =====
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(139, 92, 246, 0.15) 50%, rgba(236, 72, 153, 0.15) 100%);
        border-radius: 24px;
        padding: 50px;
        margin-bottom: 40px;
        border: 1px solid rgba(6, 182, 212, 0.3);
        text-align: center;
    ">
        <div style="margin-bottom: 20px;">
            <span style="
                display: inline-block;
                padding: 10px 24px;
                background: linear-gradient(135deg, #06b6d4, #3b82f6);
                border-radius: 50px;
                color: white;
                font-size: 0.95rem;
                font-weight: 600;
                margin-right: 12px;
            ">✨ UAE E-Commerce Analytics</span>
            <span style="
                display: inline-block;
                padding: 10px 24px;
                background: linear-gradient(135deg, #8b5cf6, #ec4899);
                border-radius: 50px;
                color: white;
                font-size: 0.95rem;
                font-weight: 600;
            ">🚀 v2.0</span>
        </div>
        <div style="
            font-size: 64px;
            font-weight: 800;
            background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 20px 0;
            line-height: 1.2;
        ">UAE Pulse Simulator</div>
        <p style="color: #94a3b8; font-size: 1.15rem; margin: 0; line-height: 1.6;">
            Transform your e-commerce data into actionable insights.<br>
            Clean dirty data, simulate promotional campaigns, and visualize performance metrics.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== FEATURE CARDS =====
    st.markdown('<p class="section-title section-title-purple">✨ Powerful Features</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_feature_card(
            "📂", "Data Upload", 
            "Upload and preview your e-commerce CSV files with instant validation",
            "cyan"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_feature_card(
            "🧹", "Data Rescue", 
            "Detect & auto-fix 15+ types of data quality issues",
            "blue"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_feature_card(
            "🎯", "Simulator", 
            "Run what-if scenarios and forecast campaign ROI",
            "purple"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_feature_card(
            "📊", "Analytics", 
            "Interactive dashboards with real-time KPI tracking",
            "pink"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== CAPABILITIES SECTION =====
    st.markdown('<p class="section-title section-title-teal">🔥 What You Can Do</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #06b6d4; margin-top: 0; font-size: 1.1rem;">🧹 Data Cleaning Capabilities</h4>
            <ul style="color: #94a3b8; margin-bottom: 0; font-size: 0.95rem; line-height: 1.8;">
                <li>Missing value detection & imputation</li>
                <li>Duplicate record removal</li>
                <li>Outlier detection & capping</li>
                <li>Format standardization</li>
                <li>Foreign key validation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card" style="border-left-color: #8b5cf6;">
            <h4 style="color: #8b5cf6; margin-top: 0; font-size: 1.1rem;">🎯 Simulation Features</h4>
            <ul style="color: #94a3b8; margin-bottom: 0; font-size: 0.95rem; line-height: 1.8;">
                <li>Discount impact modeling</li>
                <li>Category elasticity analysis</li>
                <li>Channel performance comparison</li>
                <li>ROI & margin forecasting</li>
                <li>Risk warning system</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== QUICK START GUIDE =====
    st.markdown('<p class="section-title section-title-blue">🚀 Quick Start Guide</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 48px; margin-bottom: 10px;">1️⃣</div>
            <div style="color: #06b6d4; font-weight: 600; margin-bottom: 5px;">Load Data</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">Go to 📂 Data page and upload your files or load sample data</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 48px; margin-bottom: 10px;">2️⃣</div>
            <div style="color: #3b82f6; font-weight: 600; margin-bottom: 5px;">Clean Data</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">Go to 🧹 Cleaner to detect and fix data issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 48px; margin-bottom: 10px;">3️⃣</div>
            <div style="color: #8b5cf6; font-weight: 600; margin-bottom: 5px;">View Insights</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">Check 👔 Executive or 📋 Manager views for KPIs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 48px; margin-bottom: 10px;">4️⃣</div>
            <div style="color: #ec4899; font-weight: 600; margin-bottom: 5px;">Simulate</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">Go to 🎯 Simulator to run what-if campaigns</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== DATA STATUS =====
    if st.session_state.data_loaded:
        st.markdown(create_success_card("✅ Data is loaded! Go to 👔 Executive View to see your KPIs."), unsafe_allow_html=True)
    else:
        st.markdown(create_info_card("💡 Start by loading data. Go to 📂 Data page."), unsafe_allow_html=True)
    
    show_footer()
    
def show_executive_page():
    """Display the Executive View - high-level KPIs and insights."""
    
    st.markdown('<h1 class="page-title page-title-cyan">👔 Executive View</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">High-level business performance at a glance</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card("Please load data first. Go to 📂 Data page."), unsafe_allow_html=True)
        show_footer()
        return
    
    # Get the appropriate data
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    
    # Initialize simulator for KPI calculations
    sim = Simulator()
    
    # Calculate KPIs
    kpis = sim.calculate_overall_kpis(sales_df, products_df)
    
    # ===== KPI CARDS ROW 1 =====
    st.markdown('<p class="section-title section-title-cyan">📈 Key Performance Indicators</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "Total Revenue", 
            f"AED {kpis['total_revenue']:,.0f}",
            color="cyan"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Total Orders", 
            f"{kpis['total_orders']:,}",
            color="blue"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Avg Order Value", 
            f"AED {kpis['avg_order_value']:,.2f}",
            color="purple"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "Profit Margin", 
            f"{kpis['profit_margin_pct']:.1f}%",
            color="green"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ===== KPI CARDS ROW 2 =====
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "Total Profit", 
            f"AED {kpis['total_profit']:,.0f}",
            color="teal"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Total Units", 
            f"{kpis['total_units']:,.0f}",
            color="orange"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Return Rate", 
            f"{kpis['return_rate_pct']:.1f}%",
            color="pink"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "Avg Discount", 
            f"{kpis['avg_discount_pct']:.1f}%",
            color="blue"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== CHARTS =====
    st.markdown('<p class="section-title section-title-blue">📊 Revenue Overview</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    city_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'city')
    channel_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'channel')
    
    with col1:
        if len(city_kpis) > 0:
            fig = px.pie(
                city_kpis, 
                values='revenue', 
                names='city',
                title='Revenue by City',
                color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b'],
                hole=0.45
            )
            fig = style_plotly_chart(fig)
            fig.update_traces(textposition='outside', textinfo='percent+label', textfont_size=12)
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        if len(channel_kpis) > 0:
            fig = px.bar(
                channel_kpis,
                x='channel',
                y='revenue',
                title='Revenue by Channel',
                color='channel',
                color_discrete_sequence=['#10b981', '#f59e0b', '#ec4899']
            )
            fig = style_plotly_chart(fig)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # ===== BUSINESS INSIGHTS =====
    st.markdown('<p class="section-title section-title-purple">💡 Key Business Insights</p>', unsafe_allow_html=True)
    
    insights = generate_insights(kpis, city_kpis, channel_kpis)
    
    for title, text in insights:
        st.markdown(create_insight_card(title, text), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== STATUS =====
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.is_cleaned:
            st.markdown(create_success_card("✅ Data has been cleaned and validated."), unsafe_allow_html=True)
        else:
            st.markdown(create_warning_card("⚠️ Data not yet cleaned. Go to 🧹 Cleaner to validate."), unsafe_allow_html=True)
    
    with col2:
        source = "Cleaned Data ✨" if st.session_state.is_cleaned else "Raw Data 📥"
        st.markdown(create_info_card(f"<strong>Data Source:</strong> {source}"), unsafe_allow_html=True)
    
    show_footer()
    
def show_manager_page():
    """Display the Manager View - detailed operational metrics."""
    
    st.markdown('<h1 class="page-title page-title-blue">📋 Manager View</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Detailed operational metrics and performance breakdown</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card("Please load data first. Go to 📂 Data page."), unsafe_allow_html=True)
        show_footer()
        return
    
    # Get the appropriate data
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    inventory_df = st.session_state.clean_inventory if st.session_state.is_cleaned else st.session_state.raw_inventory
    
    # Initialize simulator for KPI calculations
    sim = Simulator()
    
    # Calculate KPIs
    kpis = sim.calculate_overall_kpis(sales_df, products_df)
    city_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'city')
    channel_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'channel')
    category_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'category')
    
    # ===== DATA SUMMARY =====
    st.markdown('<p class="section-title section-title-cyan">📊 Data Summary</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "Products", 
            f"{len(products_df):,}",
            color="cyan"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Stores", 
            f"{len(stores_df):,}",
            color="blue"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Sales Records", 
            f"{len(sales_df):,}",
            color="purple"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "Inventory Items", 
            f"{len(inventory_df):,}",
            color="pink"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== PERFORMANCE BY CITY =====
    st.markdown('<p class="section-title section-title-teal">🏙️ Performance by City</p>', unsafe_allow_html=True)
    
    if len(city_kpis) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                city_kpis,
                x='city',
                y='revenue',
                title='Revenue by City',
                color='revenue',
                color_continuous_scale=['#06b6d4', '#3b82f6', '#8b5cf6']
            )
            fig = style_plotly_chart(fig)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            fig = px.bar(
                city_kpis,
                x='city',
                y='orders',
                title='Orders by City',
                color='orders',
                color_continuous_scale=['#10b981', '#f59e0b', '#ec4899']
            )
            fig = style_plotly_chart(fig)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, width='stretch')
        
        # City table
        st.markdown("**📋 City Performance Table**")
        display_city = city_kpis.copy()
        display_city['revenue'] = display_city['revenue'].apply(lambda x: f"AED {x:,.0f}")
        display_city['orders'] = display_city['orders'].apply(lambda x: f"{x:,}")
        st.dataframe(display_city, width='stretch')
    
    st.markdown("---")
    
    # ===== PERFORMANCE BY CHANNEL =====
    st.markdown('<p class="section-title section-title-purple">📺 Performance by Channel</p>', unsafe_allow_html=True)
    
    if len(channel_kpis) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                channel_kpis,
                values='revenue',
                names='channel',
                title='Revenue Share by Channel',
                color_discrete_sequence=['#06b6d4', '#8b5cf6', '#ec4899'],
                hole=0.4
            )
            fig = style_plotly_chart(fig)
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            fig = px.pie(
                channel_kpis,
                values='orders',
                names='channel',
                title='Orders Share by Channel',
                color_discrete_sequence=['#10b981', '#f59e0b', '#3b82f6'],
                hole=0.4
            )
            fig = style_plotly_chart(fig)
            st.plotly_chart(fig, width='stretch')
        
        # Channel table
        st.markdown("**📋 Channel Performance Table**")
        display_channel = channel_kpis.copy()
        display_channel['revenue'] = display_channel['revenue'].apply(lambda x: f"AED {x:,.0f}")
        display_channel['orders'] = display_channel['orders'].apply(lambda x: f"{x:,}")
        st.dataframe(display_channel, width='stretch')
    
    st.markdown("---")
    
    # ===== PERFORMANCE BY CATEGORY =====
    st.markdown('<p class="section-title section-title-orange">📦 Performance by Category</p>', unsafe_allow_html=True)
    
    if len(category_kpis) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                category_kpis.head(10),
                x='revenue',
                y='category',
                orientation='h',
                title='Top 10 Categories by Revenue',
                color='revenue',
                color_continuous_scale=['#06b6d4', '#3b82f6', '#8b5cf6']
            )
            fig = style_plotly_chart(fig)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            fig = px.bar(
                category_kpis.head(10),
                x='orders',
                y='category',
                orientation='h',
                title='Top 10 Categories by Orders',
                color='orders',
                color_continuous_scale=['#10b981', '#f59e0b', '#ec4899']
            )
            fig = style_plotly_chart(fig)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, width='stretch')
        
        # Category table
        st.markdown("**📋 Category Performance Table**")
        display_cat = category_kpis.copy()
        display_cat['revenue'] = display_cat['revenue'].apply(lambda x: f"AED {x:,.0f}")
        display_cat['orders'] = display_cat['orders'].apply(lambda x: f"{x:,}")
        st.dataframe(display_cat, width='stretch')
    
    st.markdown("---")
    
    # ===== OPERATIONAL ALERTS =====
    st.markdown('<p class="section-title section-title-pink">⚠️ Operational Alerts</p>', unsafe_allow_html=True)
    
    alerts = []
    
    # Check profit margin
    if kpis['profit_margin_pct'] < 20:
        alerts.append(("Low Profit Margin", f"Profit margin is {kpis['profit_margin_pct']:.1f}%. Consider reviewing pricing strategy.", "warning"))
    
    # Check return rate
    if kpis['return_rate_pct'] > 5:
        alerts.append(("High Return Rate", f"Return rate is {kpis['return_rate_pct']:.1f}%. Investigate product quality issues.", "warning"))
    
    # Check discount
    if kpis['avg_discount_pct'] > 15:
        alerts.append(("High Discounting", f"Average discount is {kpis['avg_discount_pct']:.1f}%. Monitor impact on margins.", "warning"))
    
    if len(alerts) == 0:
        st.markdown(create_success_card("✅ No operational alerts. All metrics are within healthy ranges."), unsafe_allow_html=True)
    else:
        for title, message, alert_type in alerts:
            if alert_type == "warning":
                st.markdown(create_warning_card(f"**{title}:** {message}"), unsafe_allow_html=True)
            else:
                st.markdown(create_info_card(f"**{title}:** {message}"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== DATA STATUS =====
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.is_cleaned:
            st.markdown(create_success_card("✅ Viewing cleaned data."), unsafe_allow_html=True)
        else:
            st.markdown(create_warning_card("⚠️ Viewing raw data. Clean data for better accuracy."), unsafe_allow_html=True)
    
    with col2:
        source = "Cleaned Data ✨" if st.session_state.is_cleaned else "Raw Data 📥"
        st.markdown(create_info_card(f"<strong>Data Source:</strong> {source}"), unsafe_allow_html=True)
    
    show_footer()
# ============================================================================
# PAGE: DATA (FIXED - BIGGER TITLES)
# ============================================================================

def show_data_page():
    """Display the data management page."""
    
    # BIG PAGE TITLE
    st.markdown('<h1 class="page-title page-title-cyan">📂 Data Management</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Upload, view, and manage your e-commerce data files</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Upload section
    st.markdown('<p class="section-title section-title-blue">📤 Upload Data Files</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        products_file = st.file_uploader("📦 Products CSV", type=['csv'], key='products_upload')
        sales_file = st.file_uploader("🛒 Sales CSV", type=['csv'], key='sales_upload')
    
    with col2:
        stores_file = st.file_uploader("🏪 Stores CSV", type=['csv'], key='stores_upload')
        inventory_file = st.file_uploader("📋 Inventory CSV", type=['csv'], key='inventory_upload')
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📥 Load Uploaded Files", width='stretch'):
            try:
                if products_file:
                    st.session_state.raw_products = pd.read_csv(products_file)
                if stores_file:
                    st.session_state.raw_stores = pd.read_csv(stores_file)
                if sales_file:
                    st.session_state.raw_sales = pd.read_csv(sales_file)
                if inventory_file:
                    st.session_state.raw_inventory = pd.read_csv(inventory_file)
                
                st.session_state.data_loaded = True
                st.session_state.is_cleaned = False
                st.success("✅ Files uploaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    
    # Or load sample data
    st.markdown('<p class="section-title section-title-purple">📦 Or Use Sample Data</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📥 Load Sample Data", width='stretch', key='sample_data_btn'):
            try:
                st.session_state.raw_products = pd.read_csv('data/products.csv')
                st.session_state.raw_stores = pd.read_csv('data/stores.csv')
                st.session_state.raw_sales = pd.read_csv('data/sales_raw.csv')
                st.session_state.raw_inventory = pd.read_csv('data/inventory_snapshot.csv')
                st.session_state.data_loaded = True
                st.session_state.is_cleaned = False
                st.success("✅ Sample data loaded!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Preview data
    if st.session_state.data_loaded:
        st.markdown("---")
        st.markdown('<p class="section-title section-title-teal">👀 Data Preview</p>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📦 Products", "🏪 Stores", "🛒 Sales", "📋 Inventory"])
        
        with tab1:
            if st.session_state.raw_products is not None:
                df = st.session_state.raw_products
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(create_metric_card("Rows", f"{len(df):,}", color="cyan"), unsafe_allow_html=True)
                with col2:
                    st.markdown(create_metric_card("Columns", f"{len(df.columns)}", color="blue"), unsafe_allow_html=True)
                with col3:
                    null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
                    st.markdown(create_metric_card("Null %", f"{null_pct:.1f}%", color="orange"), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df.head(100), width='stretch')
        
        with tab2:
            if st.session_state.raw_stores is not None:
                df = st.session_state.raw_stores
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(create_metric_card("Rows", f"{len(df):,}", color="cyan"), unsafe_allow_html=True)
                with col2:
                    st.markdown(create_metric_card("Columns", f"{len(df.columns)}", color="blue"), unsafe_allow_html=True)
                with col3:
                    null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
                    st.markdown(create_metric_card("Null %", f"{null_pct:.1f}%", color="orange"), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df.head(100), width='stretch')
        
        with tab3:
            if st.session_state.raw_sales is not None:
                df = st.session_state.raw_sales
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(create_metric_card("Rows", f"{len(df):,}", color="cyan"), unsafe_allow_html=True)
                with col2:
                    st.markdown(create_metric_card("Columns", f"{len(df.columns)}", color="blue"), unsafe_allow_html=True)
                with col3:
                    null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
                    st.markdown(create_metric_card("Null %", f"{null_pct:.1f}%", color="orange"), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df.head(100), width='stretch')
        
        with tab4:
            if st.session_state.raw_inventory is not None:
                df = st.session_state.raw_inventory
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(create_metric_card("Rows", f"{len(df):,}", color="cyan"), unsafe_allow_html=True)
                with col2:
                    st.markdown(create_metric_card("Columns", f"{len(df.columns)}", color="blue"), unsafe_allow_html=True)
                with col3:
                    null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
                    st.markdown(create_metric_card("Null %", f"{null_pct:.1f}%", color="orange"), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df.head(100), width='stretch')
        
        # Data Quality Insight
        st.markdown("---")
        st.markdown('<p class="section-title section-title-purple">💡 Data Quality Insight</p>', unsafe_allow_html=True)
        
        total_nulls = 0
        total_cells = 0
        for df in [st.session_state.raw_products, st.session_state.raw_stores, st.session_state.raw_sales, st.session_state.raw_inventory]:
            if df is not None:
                total_nulls += df.isnull().sum().sum()
                total_cells += len(df) * len(df.columns)
        
        overall_null_pct = (total_nulls / total_cells * 100) if total_cells > 0 else 0
        
        if overall_null_pct > 5:
            st.markdown(create_insight_card("Data Quality Alert", f"Overall null rate is {overall_null_pct:.1f}%. Recommend running Data Cleaner to fix missing values and improve data quality."), unsafe_allow_html=True)
        elif overall_null_pct > 0:
            st.markdown(create_insight_card("Minor Issues Detected", f"Overall null rate is {overall_null_pct:.1f}%. Data Cleaner can help fix these small issues."), unsafe_allow_html=True)
        else:
            st.markdown(create_insight_card("Excellent Data Quality", "No missing values detected in your datasets! Data looks clean."), unsafe_allow_html=True)
    
    show_footer()

# ============================================================================
# PAGE: CLEANER (FIXED - BIGGER TITLES)
# ============================================================================

def show_cleaner_page():
    """Display the data cleaner page."""
    
    st.markdown('<h1 class="page-title page-title-green">🧹 Data Rescue Center</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Validate, detect issues, and clean your dirty data automatically</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card("Please load data first. Go to 📂 Data page."), unsafe_allow_html=True)
        show_footer()
        return
    
    st.markdown('<p class="section-title section-title-cyan">🔍 Issues We Detect & Fix</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <strong style="color: #06b6d4; font-size: 1.1rem;">Data Quality</strong>
            <ul style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0; line-height: 1.8;">
                <li>Missing values</li>
                <li>Duplicate records</li>
                <li>Whitespace issues</li>
                <li>Text standardization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card" style="border-left-color: #8b5cf6;">
            <strong style="color: #8b5cf6; font-size: 1.1rem;">Format Issues</strong>
            <ul style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0; line-height: 1.8;">
                <li>Multi-language text</li>
                <li>Non-English values</li>
                <li>Fuzzy matching</li>
                <li>Case normalization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card" style="border-left-color: #ec4899;">
            <strong style="color: #ec4899; font-size: 1.1rem;">Value Issues</strong>
            <ul style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0; line-height: 1.8;">
                <li>Negative values</li>
                <li>Outliers (IQR)</li>
                <li>FK violations</li>
                <li>Invalid references</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run Data Cleaning", width='stretch', type="primary"):
            with st.spinner("🔄 Analyzing and cleaning data... This may take a moment."):
                try:
                    cleaner = DataCleaner()
                    
                    clean_products, clean_stores, clean_sales, clean_inventory = cleaner.clean_all(
                        st.session_state.raw_products.copy(),
                        st.session_state.raw_stores.copy(),
                        st.session_state.raw_sales.copy(),
                        st.session_state.raw_inventory.copy()
                    )
                    
                    st.session_state.clean_products = clean_products
                    st.session_state.clean_stores = clean_stores
                    st.session_state.clean_sales = clean_sales
                    st.session_state.clean_inventory = clean_inventory
                    st.session_state.issues_df = cleaner.get_issues_df()
                    st.session_state.cleaner_stats = cleaner.stats
                    st.session_state.cleaning_report = cleaner.cleaning_report
                    st.session_state.is_cleaned = True
                    
                    st.success("✅ Data cleaning complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error during cleaning: {str(e)}")
    
    if st.session_state.is_cleaned:
        st.markdown("---")
        st.markdown('<p class="section-title section-title-blue">📊 Cleaning Results</p>', unsafe_allow_html=True)
        
        stats = st.session_state.cleaner_stats
        report = st.session_state.cleaning_report
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'products' in report:
                before = report['products'].get('original_rows', 0)
                after = report['products'].get('final_rows', 0)
                fixed = report['products'].get('missing_fixed', 0) + report['products'].get('duplicates_removed', 0)
                delta = f"{fixed} fixed" if fixed > 0 else "Clean"
                delta_type = "positive"
            else:
                after = len(st.session_state.clean_products)
                delta = "Processed"
                delta_type = "positive"
            st.markdown(create_metric_card("Products", f"{after:,}", delta, delta_type, "cyan"), unsafe_allow_html=True)
        
        with col2:
            if 'stores' in report:
                before = report['stores'].get('original_rows', 0)
                after = report['stores'].get('final_rows', 0)
                fixed = report['stores'].get('missing_fixed', 0) + report['stores'].get('duplicates_removed', 0)
                delta = f"{fixed} fixed" if fixed > 0 else "Clean"
                delta_type = "positive"
            else:
                after = len(st.session_state.clean_stores)
                delta = "Processed"
                delta_type = "positive"
            st.markdown(create_metric_card("Stores", f"{after:,}", delta, delta_type, "blue"), unsafe_allow_html=True)
        
        with col3:
            if 'sales' in report:
                before = report['sales'].get('original_rows', 0)
                after = report['sales'].get('final_rows', 0)
                fixed = report['sales'].get('missing_fixed', 0) + report['sales'].get('duplicates_removed', 0)
                delta = f"{fixed} fixed" if fixed > 0 else "Clean"
                delta_type = "positive"
            else:
                after = len(st.session_state.clean_sales)
                delta = "Processed"
                delta_type = "positive"
            st.markdown(create_metric_card("Sales", f"{after:,}", delta, delta_type, "purple"), unsafe_allow_html=True)
        
        with col4:
            if 'inventory' in report:
                before = report['inventory'].get('original_rows', 0)
                after = report['inventory'].get('final_rows', 0)
                fixed = report['inventory'].get('missing_fixed', 0) + report['inventory'].get('duplicates_removed', 0)
                delta = f"{fixed} fixed" if fixed > 0 else "Clean"
                delta_type = "positive"
            else:
                after = len(st.session_state.clean_inventory)
                delta = "Processed"
                delta_type = "positive"
            st.markdown(create_metric_card("Inventory", f"{after:,}", delta, delta_type, "pink"), unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<p class="section-title section-title-teal">📈 Cleaning Summary</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card("Missing Fixed", f"{stats.get('missing_values_fixed', 0):,}", color="cyan"), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_metric_card("Duplicates Removed", f"{stats.get('duplicates_removed', 0):,}", color="blue"), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_metric_card("Outliers Fixed", f"{stats.get('outliers_fixed', 0):,}", color="purple"), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_metric_card("Text Standardized", f"{stats.get('text_standardized', 0):,}", color="pink"), unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<p class="section-title section-title-orange">🔍 Issues Detected & Fixed</p>', unsafe_allow_html=True)
        
        issues_df = st.session_state.issues_df
        
        if len(issues_df) > 0 and not (len(issues_df) == 1 and issues_df.iloc[0]['Issue Type'] == 'None'):
            total_fixed = stats.get('total_issues_fixed', 0)
            st.markdown(create_success_card(f"Total {total_fixed} issues detected and fixed automatically!"), unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                issue_counts = issues_df.groupby('Issue Type')['Count'].sum().reset_index()
                issue_counts.columns = ['Issue Type', 'Count']
                
                fig = px.bar(
                    issue_counts,
                    x='Count',
                    y='Issue Type',
                    orientation='h',
                    title='Issues by Type',
                    color='Count',
                    color_continuous_scale=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899']
                )
                fig = style_plotly_chart(fig)
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                table_counts = issues_df.groupby('DataFrame')['Count'].sum().reset_index()
                table_counts.columns = ['Table', 'Count']
                
                fig = px.pie(
                    table_counts,
                    values='Count',
                    names='Table',
                    title='Issues by Table',
                    color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899'],
                    hole=0.45
                )
                fig = style_plotly_chart(fig)
                st.plotly_chart(fig, width='stretch')
            
            st.markdown('<p class="section-title section-title-purple">💡 Cleaning Insight</p>', unsafe_allow_html=True)
            
            top_issue = issue_counts.loc[issue_counts['Count'].idxmax(), 'Issue Type']
            top_count = issue_counts['Count'].max()
            st.markdown(create_insight_card("Most Common Issue", f"'{top_issue}' was the most frequent issue with {top_count} occurrences. All instances have been automatically fixed."), unsafe_allow_html=True)
            
            st.markdown('<p class="section-title section-title-blue">📋 Detailed Issues Log</p>', unsafe_allow_html=True)
            st.dataframe(issues_df, width='stretch')
            
            csv = issues_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Issues Log (CSV)",
                data=csv,
                file_name="data_issues_log.csv",
                mime="text/csv"
            )
        else:
            st.markdown(create_success_card("No major issues found! Your data is already clean."), unsafe_allow_html=True)
        
        if 'foreign_key_issues' in report:
            fk = report['foreign_key_issues']
            if fk.get('invalid_skus', 0) > 0 or fk.get('invalid_stores', 0) > 0:
                st.markdown("---")
                st.markdown('<p class="section-title section-title-orange">⚠️ Foreign Key Warnings</p>', unsafe_allow_html=True)
                
                if fk.get('invalid_skus', 0) > 0:
                    st.warning(f"⚠️ {fk['invalid_skus']} sales records have SKUs not found in products table")
                if fk.get('invalid_stores', 0) > 0:
                    st.warning(f"⚠️ {fk['invalid_stores']} sales records have store IDs not found in stores table")
    
    show_footer()

# ============================================================================
# PAGE: SIMULATOR (FIXED - BIGGER TITLES)
# ============================================================================

def show_simulator_page():
    """Display the campaign simulator page."""
    
    st.markdown('<h1 class="page-title page-title-purple">🎯 Campaign Simulator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Run what-if scenarios and forecast campaign outcomes</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.warning("⚠️ Please load data first. Go to 📂 Data page.")
        show_footer()
        return
    
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    
    st.markdown('<p class="section-title section-title-cyan">⚙️ Campaign Parameters</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p style="color: #06b6d4; font-weight: 600; margin-bottom: 10px;">💰 Pricing</p>', unsafe_allow_html=True)
        discount_pct = st.slider("Discount %", 0, 50, 15)
        promo_budget = st.number_input("Promo Budget (AED)", 1000, 500000, 25000, step=5000)
    
    with col2:
        st.markdown('<p style="color: #8b5cf6; font-weight: 600; margin-bottom: 10px;">📊 Constraints</p>', unsafe_allow_html=True)
        margin_floor = st.slider("Margin Floor %", 0, 50, 15)
        campaign_days = st.slider("Campaign Days", 1, 30, 7)
    
    with col3:
        st.markdown('<p style="color: #ec4899; font-weight: 600; margin-bottom: 10px;">🎯 Targeting</p>', unsafe_allow_html=True)
        
        cities = ['All']
        channels = ['All']
        categories = ['All']
        
        if stores_df is not None and 'city' in stores_df.columns:
            cities += stores_df['city'].dropna().unique().tolist()
        if stores_df is not None and 'channel' in stores_df.columns:
            channels += stores_df['channel'].dropna().unique().tolist()
        if products_df is not None and 'category' in products_df.columns:
            categories += products_df['category'].dropna().unique().tolist()
        
        city = st.selectbox("Target City", cities)
        channel = st.selectbox("Target Channel", channels)
        category = st.selectbox("Target Category", categories)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        run_simulation = st.button("🚀 Run Simulation", width='stretch', type="primary")
    
    if run_simulation:
        with st.spinner("🔄 Running simulation..."):
            try:
                sim = Simulator()
                
                results = sim.simulate_campaign(
                    sales_df, stores_df, products_df,
                    discount_pct=discount_pct,
                    promo_budget=promo_budget,
                    margin_floor=margin_floor,
                    city=city,
                    channel=channel,
                    category=category,
                    campaign_days=campaign_days
                )
                
                st.session_state.sim_results = results
                
            except Exception as e:
                st.error(f"❌ Simulation error: {str(e)}")
    
    if 'sim_results' in st.session_state and st.session_state.sim_results:
        results = st.session_state.sim_results
        outputs = results.get('outputs')
        comparison = results.get('comparison')
        warnings = results.get('warnings', [])
        
        if outputs:
            st.markdown("---")
            st.markdown('<p class="section-title section-title-teal">📊 Simulation Results</p>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                delta = f"{comparison['revenue_change_pct']:+.1f}%"
                delta_type = "positive" if comparison['revenue_change_pct'] > 0 else "negative"
                st.markdown(create_metric_card("Expected Revenue", f"AED {outputs['expected_revenue']:,.0f}", delta, delta_type, "cyan"), unsafe_allow_html=True)
            
            with col2:
                delta = f"{comparison['order_change_pct']:+.1f}%"
                delta_type = "positive" if comparison['order_change_pct'] > 0 else "negative"
                st.markdown(create_metric_card("Expected Orders", f"{outputs['expected_orders']:,}", delta, delta_type, "blue"), unsafe_allow_html=True)
            
            with col3:
                delta = f"{comparison['profit_change_pct']:+.1f}%"
                delta_type = "positive" if comparison['profit_change_pct'] > 0 else "negative"
                st.markdown(create_metric_card("Net Profit", f"AED {outputs['expected_net_profit']:,.0f}", delta, delta_type, "green"), unsafe_allow_html=True)
            
            with col4:
                color = "green" if outputs['roi_pct'] > 0 else "pink"
                st.markdown(create_metric_card("ROI", f"{outputs['roi_pct']:.1f}%", color=color), unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(create_metric_card("Demand Lift", f"+{outputs['demand_lift_pct']:.1f}%", color="purple"), unsafe_allow_html=True)
            
            with col2:
                color = "green" if outputs['expected_margin_pct'] >= margin_floor else "orange"
                st.markdown(create_metric_card("Margin", f"{outputs['expected_margin_pct']:.1f}%", color=color), unsafe_allow_html=True)
            
            with col3:
                st.markdown(create_metric_card("Promo Cost", f"AED {outputs['promo_cost']:,.0f}", color="orange"), unsafe_allow_html=True)
            
            with col4:
                st.markdown(create_metric_card("Fulfillment", f"AED {outputs['fulfillment_cost']:,.0f}", color="blue"), unsafe_allow_html=True)
            
            if warnings:
                st.markdown("---")
                st.markdown('<p class="section-title section-title-orange">⚠️ Risk Alerts</p>', unsafe_allow_html=True)
                for warning in warnings:
                    st.warning(warning)
            else:
                st.markdown("---")
                st.success("✅ All metrics within acceptable range. Campaign looks healthy!")
            
            st.markdown("---")
            st.markdown('<p class="section-title section-title-blue">📈 Baseline vs Campaign</p>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                comp_data = pd.DataFrame({
                    'Metric': ['Revenue', 'Profit'],
                    'Baseline': [comparison['baseline_revenue'], comparison['baseline_profit']],
                    'Campaign': [outputs['expected_revenue'], outputs['expected_net_profit']]
                })
                
                fig = go.Figure()
                fig.add_trace(go.Bar(name='Baseline', x=comp_data['Metric'], y=comp_data['Baseline'], marker_color='#3b82f6'))
                fig.add_trace(go.Bar(name='Campaign', x=comp_data['Metric'], y=comp_data['Campaign'], marker_color='#06b6d4'))
                fig = style_plotly_chart(fig)
                fig.update_layout(barmode='group', title='Revenue & Profit Comparison')
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                orders_data = pd.DataFrame({
                    'Type': ['Baseline', 'Campaign'],
                    'Orders': [comparison['baseline_orders'], outputs['expected_orders']]
                })
                
                fig = px.bar(
                    orders_data,
                    x='Type',
                    y='Orders',
                    title='Orders Comparison',
                    color='Type',
                    color_discrete_sequence=['#8b5cf6', '#ec4899']
                )
                fig = style_plotly_chart(fig)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, width='stretch')
        
        elif warnings:
            for warning in warnings:
                st.warning(warning)
    
    show_footer()

# ============================================================================
# PAGE: ANALYTICS (FIXED - BIGGER TITLES + TAB HOVER)
# ============================================================================

def show_analytics_page():
    """Display the analytics page."""
    
    st.markdown('<h1 class="page-title page-title-pink">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Deep dive into your e-commerce performance metrics</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.warning("⚠️ Please load data first. Go to 📂 Data page.")
        show_footer()
        return
    
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    inventory_df = st.session_state.clean_inventory if st.session_state.is_cleaned else st.session_state.raw_inventory
    
    sim = Simulator()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🏙️ By City", "📦 By Category", "📋 Inventory"])
    
    with tab1:
        st.markdown('<p class="section-title section-title-cyan">📈 Daily Performance Trends</p>', unsafe_allow_html=True)
        
        try:
            daily_trends = sim.calculate_daily_trends(sales_df, products_df)
            
            if daily_trends is None or len(daily_trends) == 0:
                st.warning("⚠️ No trend data available. This could be due to missing date column in sales data.")
            else:
                fig = px.area(
                    daily_trends,
                    x='date',
                    y='revenue',
                    title='Daily Revenue Trend',
                    color_discrete_sequence=['#06b6d4']
                )
                fig = style_plotly_chart(fig)
                fig.update_traces(line=dict(width=3), fillcolor='rgba(6, 182, 212, 0.2)')
                st.plotly_chart(fig, width='stretch')
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.line(
                        daily_trends,
                        x='date',
                        y='orders',
                        title='Daily Orders',
                        color_discrete_sequence=['#3b82f6']
                    )
                    fig = style_plotly_chart(fig)
                    fig.update_traces(line=dict(width=3))
                    st.plotly_chart(fig, width='stretch')
                
                with col2:
                    fig = px.line(
                        daily_trends,
                        x='date',
                        y='profit',
                        title='Daily Profit',
                        color_discrete_sequence=['#10b981']
                    )
                    fig = style_plotly_chart(fig)
                    fig.update_traces(line=dict(width=3))
                    st.plotly_chart(fig, width='stretch')
                
                st.markdown('<p class="section-title section-title-purple">💡 Trend Insight</p>', unsafe_allow_html=True)
                avg_revenue = daily_trends['revenue'].mean()
                max_revenue = daily_trends['revenue'].max()
                max_date = daily_trends.loc[daily_trends['revenue'].idxmax(), 'date']
                date_str = max_date.strftime('%b %d, %Y') if hasattr(max_date, 'strftime') else str(max_date)
                st.markdown(create_insight_card("Peak Performance Day", f"Best day was {date_str} with AED {max_revenue:,.0f} revenue ({((max_revenue/avg_revenue)-1)*100:.0f}% above average)."), unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"❌ Error loading trends: {str(e)}")
    
    with tab2:
        st.markdown('<p class="section-title section-title-blue">🏙️ Performance by City</p>', unsafe_allow_html=True)
        
        try:
            city_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'city')
            
            if city_kpis is None or len(city_kpis) == 0:
                st.warning("⚠️ No city data available.")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(
                        city_kpis,
                        x='city',
                        y='revenue',
                        title='Revenue by City',
                        color='city',
                        color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6']
                    )
                    fig = style_plotly_chart(fig)
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, width='stretch')
                
                with col2:
                    fig = px.bar(
                        city_kpis,
                        x='city',
                        y='profit_margin_pct',
                        title='Profit Margin by City',
                        color='city',
                        color_discrete_sequence=['#10b981', '#14b8a6', '#06b6d4']
                    )
                    fig = style_plotly_chart(fig)
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, width='stretch')
                
                st.markdown('<p class="section-title section-title-teal">📋 City Performance Table</p>', unsafe_allow_html=True)
                st.dataframe(city_kpis, width='stretch')
                
                st.markdown('<p class="section-title section-title-purple">💡 City Insight</p>', unsafe_allow_html=True)
                top_city = city_kpis.iloc[0]
                total_rev = city_kpis['revenue'].sum()
                top_pct = (top_city['revenue'] / total_rev * 100) if total_rev > 0 else 0
                st.markdown(create_insight_card("Market Leader", f"{top_city['city']} leads with {top_pct:.0f}% of revenue (AED {top_city['revenue']:,.0f})."), unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"❌ Error loading city data: {str(e)}")
    
    with tab3:
        st.markdown('<p class="section-title section-title-purple">📦 Performance by Category</p>', unsafe_allow_html=True)
        
        try:
            cat_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'category')
            
            if cat_kpis is None or len(cat_kpis) == 0:
                st.warning("⚠️ No category data available.")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(
                        cat_kpis,
                        values='revenue',
                        names='category',
                        title='Revenue Share by Category',
                        color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'],
                        hole=0.45
                    )
                    fig = style_plotly_chart(fig)
                    st.plotly_chart(fig, width='stretch')
                
                with col2:
                    fig = px.bar(
                        cat_kpis,
                        x='category',
                        y='profit',
                        title='Profit by Category',
                        color='profit',
                        color_continuous_scale=['#3b82f6', '#8b5cf6', '#ec4899']
                    )
                    fig = style_plotly_chart(fig)
                    fig.update_layout(coloraxis_showscale=False)
                    st.plotly_chart(fig, width='stretch')
                
                st.markdown('<p class="section-title section-title-teal">📋 Category Performance Table</p>', unsafe_allow_html=True)
                st.dataframe(cat_kpis, width='stretch')
                
                st.markdown('<p class="section-title section-title-purple">💡 Category Insight</p>', unsafe_allow_html=True)
                top_cat = cat_kpis.iloc[0]
                st.markdown(create_insight_card("Top Category", f"{top_cat['category']} leads with AED {top_cat['revenue']:,.0f} revenue and {top_cat['profit_margin_pct']:.1f}% margin."), unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"❌ Error loading category data: {str(e)}")
    
    with tab4:
        st.markdown('<p class="section-title section-title-orange">📋 Inventory Health</p>', unsafe_allow_html=True)
        
        try:
            stockout = sim.calculate_stockout_risk(inventory_df)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(create_metric_card("Total SKUs", f"{stockout['total_items']:,}", color="cyan"), unsafe_allow_html=True)
            
            with col2:
                color = "orange" if stockout['stockout_risk_pct'] > 10 else "green"
                st.markdown(create_metric_card("Stockout Risk", f"{stockout['stockout_risk_pct']:.1f}%", color=color), unsafe_allow_html=True)
            
            with col3:
                color = "pink" if stockout['zero_stock'] > 0 else "green"
                st.markdown(create_metric_card("Zero Stock", f"{stockout['zero_stock']:,}", color=color), unsafe_allow_html=True)
            
            st.markdown("---")
            
            if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.histogram(
                        inventory_df,
                        x='stock_on_hand',
                        nbins=50,
                        title='Stock Level Distribution',
                        color_discrete_sequence=['#8b5cf6']
                    )
                    fig = style_plotly_chart(fig)
                    st.plotly_chart(fig, width='stretch')
                
                with col2:
                    inventory_copy = inventory_df.copy()
                    inventory_copy['stock_on_hand'] = pd.to_numeric(inventory_copy['stock_on_hand'], errors='coerce').fillna(0)
                    
                    if 'reorder_point' in inventory_copy.columns:
                        inventory_copy['reorder_point'] = pd.to_numeric(inventory_copy['reorder_point'], errors='coerce').fillna(10)
                    else:
                        inventory_copy['reorder_point'] = 10
                    
                    inventory_copy['status'] = inventory_copy.apply(
                        lambda x: 'Critical' if x['stock_on_hand'] == 0 
                        else ('Low' if x['stock_on_hand'] <= x['reorder_point'] else 'Healthy'),
                        axis=1
                    )
                    status_counts = inventory_copy['status'].value_counts().reset_index()
                    status_counts.columns = ['Status', 'Count']
                    
                    fig = px.pie(
                        status_counts,
                        values='Count',
                        names='Status',
                        title='Inventory Status',
                        color='Status',
                        color_discrete_map={'Healthy': '#10b981', 'Low': '#f59e0b', 'Critical': '#ef4444'},
                        hole=0.45
                    )
                    fig = style_plotly_chart(fig)
                    st.plotly_chart(fig, width='stretch')
                
                st.markdown('<p class="section-title section-title-purple">💡 Inventory Insight</p>', unsafe_allow_html=True)
                if stockout['zero_stock'] > 0:
                    st.markdown(create_insight_card("Critical Stock Alert", f"{stockout['zero_stock']} items are out of stock! Immediate reorder required."), unsafe_allow_html=True)
                elif stockout['stockout_risk_pct'] > 15:
                    st.markdown(create_insight_card("Reorder Recommended", f"{stockout['stockout_risk_pct']:.0f}% of inventory is below reorder point."), unsafe_allow_html=True)
                else:
                    st.markdown(create_insight_card("Healthy Inventory", "Inventory levels are well-maintained."), unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"❌ Error loading inventory data: {str(e)}")
    
    show_footer()

# ============================================================================
# MAIN ROUTING
# ============================================================================

if page == "🏠 Home":
    show_home_page()
elif page == "📂 Data":
    show_data_page()
elif page == "🧹 Cleaner":
    show_cleaner_page()
elif page == "👔 Executive":
    show_executive_page()
elif page == "📋 Manager":
    show_manager_page()
elif page == "🎯 Simulator":
    show_simulator_page()
elif page == "📊 Analytics":
    show_analytics_page()
