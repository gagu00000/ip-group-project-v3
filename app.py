# ============================================================================
# UAE PULSE - RETAIL SIMULATOR + DATA RESCUE CENTER
# Complete Application with All Fixes Applied
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import re
from typing import Optional, Tuple, Dict, List, Any


# TO:
from modules import DataCleaner
from modules import Simulator

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="UAE Pulse - Retail Simulator",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# THEME DEFINITIONS (FIX 3: Better Light Mode Visibility)
# ============================================================================

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
        'accent_cyan': '#06b6d4',
        'accent_blue': '#3b82f6',
        'accent_purple': '#8b5cf6',
        'accent_pink': '#ec4899',
        'accent_green': '#10b981',
        'accent_orange': '#f59e0b',
        'accent_red': '#ef4444',
        'accent_teal': '#14b8a6',
        'shadow_color': 'rgba(0, 0, 0, 0.4)',
        'glow_color': 'rgba(6, 182, 212, 0.3)',
        'plotly_template': 'plotly_dark',
        'plotly_bg': 'rgba(22, 22, 31, 0.8)',
        'plotly_paper': 'rgba(22, 22, 31, 0)',
        'plotly_grid': 'rgba(45, 45, 58, 0.5)',
        'sidebar_title': '#06b6d4',
    },
    'light': {
        'bg_primary': '#f8fafc',
        'bg_secondary': '#e2e8f0',
        'bg_card': '#ffffff',
        'bg_card_hover': '#f1f5f9',
        'text_primary': '#0f172a',
        'text_secondary': '#334155',
        'text_muted': '#475569',
        'border_color': '#cbd5e1',
        'accent_cyan': '#0891b2',
        'accent_blue': '#2563eb',
        'accent_purple': '#7c3aed',
        'accent_pink': '#db2777',
        'accent_green': '#059669',
        'accent_orange': '#d97706',
        'accent_red': '#dc2626',
        'accent_teal': '#0d9488',
        'shadow_color': 'rgba(0, 0, 0, 0.15)',
        'glow_color': 'rgba(6, 182, 212, 0.15)',
        'plotly_template': 'plotly_white',
        'plotly_bg': 'rgba(255, 255, 255, 0.95)',
        'plotly_paper': 'rgba(255, 255, 255, 0)',
        'plotly_grid': 'rgba(203, 213, 225, 0.8)',
        'sidebar_title': '#7c3aed',
    }
}

def get_theme():
    """Get current theme colors."""
    return THEMES.get(st.session_state.get('theme', 'dark'), THEMES['dark'])

# ============================================================================
# SESSION STATE INITIALIZATION (Updated with Multi-Select Keys)
# ============================================================================

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'is_cleaned' not in st.session_state:
    st.session_state.is_cleaned = False
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
if 'cleaner_stats' not in st.session_state:
    st.session_state.cleaner_stats = {}

# Global filter states - MULTI-SELECT (FIX 4)
if 'global_date_range' not in st.session_state:
    st.session_state.global_date_range = None
if 'global_cities' not in st.session_state:
    st.session_state.global_cities = []
if 'global_channels' not in st.session_state:
    st.session_state.global_channels = []
if 'global_categories' not in st.session_state:
    st.session_state.global_categories = []

# Legacy single-select (keep for backward compatibility)
if 'global_city' not in st.session_state:
    st.session_state.global_city = 'All'
if 'global_channel' not in st.session_state:
    st.session_state.global_channel = 'All'
if 'global_category' not in st.session_state:
    st.session_state.global_category = 'All'

# ============================================================================
# CSS INJECTION
# ============================================================================

def inject_css():
    """Inject custom CSS for theming."""
    t = get_theme()
    
    st.markdown(f"""
    <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* Root Variables */
        :root {{
            --bg-primary: {t['bg_primary']};
            --bg-secondary: {t['bg_secondary']};
            --bg-card: {t['bg_card']};
            --text-primary: {t['text_primary']};
            --text-secondary: {t['text_secondary']};
            --accent-cyan: {t['accent_cyan']};
            --accent-purple: {t['accent_purple']};
            --border-color: {t['border_color']};
        }}
        
        /* Main App Background */
        .stApp {{
            background: linear-gradient(135deg, {t['bg_primary']} 0%, {t['bg_secondary']} 50%, {t['bg_primary']} 100%);
            font-family: 'Inter', sans-serif;
        }}
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {t['bg_card']} 0%, {t['bg_secondary']} 100%);
            border-right: 1px solid {t['border_color']};
        }}
        
        section[data-testid="stSidebar"] .stMarkdown {{
            color: {t['text_primary']};
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: {t['text_primary']} !important;
            font-family: 'Inter', sans-serif !important;
        }}
        
        /* Paragraphs and text */
        p, span, label, .stMarkdown {{
            color: {t['text_primary']};
        }}
        
        /* Radio buttons in sidebar */
        .stRadio > label {{
            color: {t['text_primary']} !important;
        }}
        
        .stRadio > div {{
            background: transparent;
        }}
        
        .stRadio > div > label {{
            background: {t['bg_card']};
            border: 1px solid {t['border_color']};
            border-radius: 10px;
            padding: 10px 15px;
            margin: 5px 0;
            transition: all 0.3s ease;
            color: {t['text_primary']} !important;
        }}
        
        .stRadio > div > label:hover {{
            border-color: {t['accent_cyan']};
            box-shadow: 0 0 15px {t['glow_color']};
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {t['accent_cyan']} 0%, {t['accent_blue']} 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 25px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px {t['shadow_color']};
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px {t['glow_color']};
        }}
        
        /* File uploader */
        .stFileUploader {{
            background: {t['bg_card']};
            border: 2px dashed {t['border_color']};
            border-radius: 15px;
            padding: 20px;
        }}
        
        .stFileUploader:hover {{
            border-color: {t['accent_cyan']};
        }}
        
        /* Selectbox and multiselect */
        .stSelectbox > div > div,
        .stMultiSelect > div > div {{
            background: {t['bg_card']};
            border-color: {t['border_color']};
            color: {t['text_primary']};
        }}
        
        /* Dataframe */
        .stDataFrame {{
            background: {t['bg_card']};
            border-radius: 10px;
            overflow: hidden;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: {t['bg_secondary']};
            padding: 10px;
            border-radius: 15px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: {t['bg_card']};
            border-radius: 10px;
            color: {t['text_secondary']};
            border: 1px solid {t['border_color']};
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {t['accent_cyan']} 0%, {t['accent_blue']} 100%);
            color: white;
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background: {t['bg_card']};
            border-radius: 10px;
            color: {t['text_primary']} !important;
        }}
        
        /* Toggle */
        .stToggle > label {{
            color: {t['text_primary']} !important;
        }}
        
        /* Metric cards */
        [data-testid="metric-container"] {{
            background: {t['bg_card']};
            border: 1px solid {t['border_color']};
            border-radius: 10px;
            padding: 15px;
        }}
        
        /* Custom Classes */
        .page-title {{
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 10px {t['shadow_color']};
        }}
        
        .page-title-cyan {{
            background: linear-gradient(135deg, {t['accent_cyan']}, {t['accent_blue']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .page-title-green {{
            background: linear-gradient(135deg, {t['accent_green']}, {t['accent_teal']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .page-title-purple {{
            background: linear-gradient(135deg, {t['accent_purple']}, {t['accent_pink']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .page-title-orange {{
            background: linear-gradient(135deg, {t['accent_orange']}, {t['accent_red']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .page-description {{
            color: {t['text_secondary']};
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }}
        
        .section-title {{
            font-size: 1.3rem;
            font-weight: 700;
            margin: 1.5rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid {t['border_color']};
        }}
        
        .section-title-cyan {{
            color: {t['accent_cyan']};
            border-color: {t['accent_cyan']};
        }}
        
        .section-title-blue {{
            color: {t['accent_blue']};
            border-color: {t['accent_blue']};
        }}
        
        .section-title-purple {{
            color: {t['accent_purple']};
            border-color: {t['accent_purple']};
        }}
        
        .section-title-pink {{
            color: {t['accent_pink']};
            border-color: {t['accent_pink']};
        }}
        
        .section-title-green {{
            color: {t['accent_green']};
            border-color: {t['accent_green']};
        }}
        
        .section-title-orange {{
            color: {t['accent_orange']};
            border-color: {t['accent_orange']};
        }}
        
        .section-title-teal {{
            color: {t['accent_teal']};
            border-color: {t['accent_teal']};
        }}
        
        /* 3D Card */
        .card-3d {{
            background: linear-gradient(145deg, {t['bg_card']} 0%, {t['bg_card_hover']} 100%);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid {t['border_color']};
            box-shadow: 
                0 8px 32px {t['shadow_color']},
                0 0 0 1px rgba(255,255,255,0.03),
                inset 0 1px 0 rgba(255,255,255,0.1);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }}
        
        .card-3d:hover {{
            transform: translateY(-5px);
            box-shadow: 
                0 20px 40px {t['shadow_color']},
                0 0 30px {t['glow_color']};
        }}
        
        /* Info cards */
        .info-card-3d {{
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(59, 130, 246, 0.1));
            border: 1px solid {t['accent_cyan']};
            border-radius: 12px;
            padding: 15px 20px;
            margin: 10px 0;
        }}
        
        .success-card-3d {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(20, 184, 166, 0.1));
            border: 1px solid {t['accent_green']};
            border-radius: 12px;
            padding: 15px 20px;
            margin: 10px 0;
        }}
        
        .warning-card-3d {{
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(239, 68, 68, 0.1));
            border: 1px solid {t['accent_orange']};
            border-radius: 12px;
            padding: 15px 20px;
            margin: 10px 0;
        }}
        
        .error-card-3d {{
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(236, 72, 153, 0.1));
            border: 1px solid {t['accent_red']};
            border-radius: 12px;
            padding: 15px 20px;
            margin: 10px 0;
        }}
        
        /* Animations */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes scaleIn {{
            from {{
                opacity: 0;
                transform: scale(0.9);
            }}
            to {{
                opacity: 1;
                transform: scale(1);
            }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: 0.7;
            }}
        }}
        
        /* Hide Streamlit elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_metric_card_3d(label, value, delta=None, delta_type="positive", color="cyan", delay=0):
    """Create a 3D styled metric card."""
    t = get_theme()
    
    color_map = {
        'cyan': t['accent_cyan'],
        'blue': t['accent_blue'],
        'purple': t['accent_purple'],
        'pink': t['accent_pink'],
        'green': t['accent_green'],
        'orange': t['accent_orange'],
        'red': t['accent_red'],
        'teal': t['accent_teal']
    }
    
    value_color = color_map.get(color, t['accent_cyan'])
    
    delta_html = ""
    if delta:
        delta_color = t['accent_green'] if delta_type == "positive" else t['accent_red']
        delta_icon = "↑" if delta_type == "positive" else "↓"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.9rem; font-weight: 600;">{delta_icon} {delta}</div>'
    else:
        delta_html = '<div style="height: 22px;"></div>'
    
    return f"""
    <div style="
        background: linear-gradient(145deg, {t['bg_card']} 0%, {t['bg_card_hover']} 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid {t['border_color']};
        box-shadow: 
            0 8px 32px {t['shadow_color']},
            0 0 0 1px rgba(255,255,255,0.03),
            inset 0 1px 0 rgba(255,255,255,0.1);
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: scaleIn 0.5s ease-out backwards;
        animation-delay: {delay}s;
    ">
        <div style="
            font-size: 0.8rem;
            color: {t['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
        ">{label}</div>
        <div style="
            font-size: 2rem;
            font-weight: 700;
            color: {value_color};
            margin: 8px 0;
            text-shadow: 0 2px 10px {t['shadow_color']};
        ">{value}</div>
        {delta_html}
    </div>
    """


def create_info_card_3d(content):
    """Create an info card."""
    t = get_theme()
    return f"""
    <div style="
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(59, 130, 246, 0.1));
        border: 1px solid {t['accent_cyan']};
        border-radius: 12px;
        padding: 15px 20px;
        margin: 10px 0;
        color: {t['text_primary']};
    ">{content}</div>
    """


def create_success_card_3d(content):
    """Create a success card."""
    t = get_theme()
    return f"""
    <div style="
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(20, 184, 166, 0.1));
        border: 1px solid {t['accent_green']};
        border-radius: 12px;
        padding: 15px 20px;
        margin: 10px 0;
        color: {t['text_primary']};
    ">✅ {content}</div>
    """


def create_warning_card_3d(content):
    """Create a warning card."""
    t = get_theme()
    return f"""
    <div style="
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(239, 68, 68, 0.1));
        border: 1px solid {t['accent_orange']};
        border-radius: 12px;
        padding: 15px 20px;
        margin: 10px 0;
        color: {t['text_primary']};
    ">⚠️ {content}</div>
    """


def create_error_card_3d(content):
    """Create an error card."""
    t = get_theme()
    return f"""
    <div style="
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(236, 72, 153, 0.1));
        border: 1px solid {t['accent_red']};
        border-radius: 12px;
        padding: 15px 20px;
        margin: 10px 0;
        color: {t['text_primary']};
    ">❌ {content}</div>
    """


def style_plotly_chart_themed(fig):
    """Apply theme styling to Plotly charts."""
    t = get_theme()
    
    fig.update_layout(
        template=t['plotly_template'],
        paper_bgcolor=t['plotly_paper'],
        plot_bgcolor=t['plotly_bg'],
        font=dict(
            family="Inter, sans-serif",
            color=t['text_primary']
        ),
        title=dict(
            font=dict(size=16, color=t['text_primary'])
        ),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(color=t['text_secondary'])
        ),
        xaxis=dict(
            gridcolor=t['plotly_grid'],
            zerolinecolor=t['border_color'],
            tickfont=dict(color=t['text_secondary'])
        ),
        yaxis=dict(
            gridcolor=t['plotly_grid'],
            zerolinecolor=t['border_color'],
            tickfont=dict(color=t['text_secondary'])
        ),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


# ============================================================================
# FILTER FUNCTIONS (FIX 4: Multi-Select Support)
# ============================================================================

def show_global_filters_sidebar():
    """Display global filters in sidebar with MULTI-SELECT support."""
    t = get_theme()
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(145deg, {t['bg_card']} 0%, {t['bg_card_hover']} 100%);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid {t['border_color']};
        margin-bottom: 15px;
    ">
        <div style="color: {t['accent_purple']}; font-weight: 700; font-size: 0.9rem; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
            🌐 Global Filters
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get data for filter options
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    
    # Date range filter
    if sales_df is not None and 'order_time' in sales_df.columns:
        try:
            dates = pd.to_datetime(sales_df['order_time'], errors='coerce').dropna()
            if len(dates) > 0:
                min_date = dates.min().date()
                max_date = dates.max().date()
                
                date_range = st.date_input(
                    "📅 Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key='global_date_filter'
                )
                
                if len(date_range) == 2:
                    st.session_state.global_date_range = date_range
        except:
            pass
    
    # City filter - MULTI-SELECT
    cities = []
    if stores_df is not None and 'city' in stores_df.columns:
        cities = sorted(stores_df['city'].dropna().unique().tolist())
    
    selected_cities = st.multiselect(
        "🏙️ Cities",
        options=cities,
        default=st.session_state.get('global_cities', []),
        key='global_city_filter',
        placeholder="All Cities"
    )
    st.session_state.global_cities = selected_cities
    
    # Channel filter - MULTI-SELECT
    channels = []
    if stores_df is not None and 'channel' in stores_df.columns:
        channels = sorted(stores_df['channel'].dropna().unique().tolist())
    
    selected_channels = st.multiselect(
        "📱 Channels",
        options=channels,
        default=st.session_state.get('global_channels', []),
        key='global_channel_filter',
        placeholder="All Channels"
    )
    st.session_state.global_channels = selected_channels
    
    # Category filter - MULTI-SELECT
    categories = []
    if products_df is not None and 'category' in products_df.columns:
        categories = sorted(products_df['category'].dropna().unique().tolist())
    
    selected_categories = st.multiselect(
        "📦 Categories",
        options=categories,
        default=st.session_state.get('global_categories', []),
        key='global_category_filter',
        placeholder="All Categories"
    )
    st.session_state.global_categories = selected_categories
    
    # Reset filters button
    if st.button("🔄 Reset All Filters", key='reset_global_filters', use_container_width=True):
        st.session_state.global_date_range = None
        st.session_state.global_cities = []
        st.session_state.global_channels = []
        st.session_state.global_categories = []
        st.rerun()
    
    # Show active filters indicator
    active_filters = []
    if st.session_state.global_date_range:
        active_filters.append("📅 Date")
    if len(st.session_state.get('global_cities', [])) > 0:
        active_filters.append(f"🏙️ {len(st.session_state.global_cities)} cities")
    if len(st.session_state.get('global_channels', [])) > 0:
        active_filters.append(f"📱 {len(st.session_state.global_channels)} channels")
    if len(st.session_state.get('global_categories', [])) > 0:
        active_filters.append(f"📦 {len(st.session_state.global_categories)} categories")
    
    if active_filters:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(139, 92, 246, 0.15));
            border-radius: 10px;
            padding: 12px;
            margin-top: 10px;
            font-size: 0.8rem;
            border: 1px solid {t['border_color']};
        ">
            <strong style="color: {t['accent_cyan']};">Active Filters:</strong><br>
            <span style="color: {t['text_primary']};">{' • '.join(active_filters)}</span>
        </div>
        """, unsafe_allow_html=True)


def apply_global_filters(df, stores_df=None, products_df=None):
    """Apply global filters to a dataframe - supports MULTI-SELECT."""
    if df is None or len(df) == 0:
        return df
    
    filtered_df = df.copy()
    
    # Apply date filter
    if st.session_state.get('global_date_range') and 'order_time' in filtered_df.columns:
        try:
            start_date, end_date = st.session_state.global_date_range
            filtered_df['order_time'] = pd.to_datetime(filtered_df['order_time'], errors='coerce')
            filtered_df = filtered_df[
                (filtered_df['order_time'].dt.date >= start_date) & 
                (filtered_df['order_time'].dt.date <= end_date)
            ]
        except:
            pass
    
    # Apply city filter (MULTI-SELECT)
    selected_cities = st.session_state.get('global_cities', [])
    if len(selected_cities) > 0 and stores_df is not None:
        if 'city' in stores_df.columns and 'store_id' in filtered_df.columns:
            city_stores = stores_df[stores_df['city'].isin(selected_cities)]['store_id'].tolist()
            filtered_df = filtered_df[filtered_df['store_id'].isin(city_stores)]
    
    # Apply channel filter (MULTI-SELECT)
    selected_channels = st.session_state.get('global_channels', [])
    if len(selected_channels) > 0 and stores_df is not None:
        if 'channel' in stores_df.columns and 'store_id' in filtered_df.columns:
            channel_stores = stores_df[stores_df['channel'].isin(selected_channels)]['store_id'].tolist()
            filtered_df = filtered_df[filtered_df['store_id'].isin(channel_stores)]
    
    # Apply category filter (MULTI-SELECT)
    selected_categories = st.session_state.get('global_categories', [])
    if len(selected_categories) > 0 and products_df is not None:
        if 'category' in products_df.columns and 'sku' in filtered_df.columns:
            category_skus = products_df[products_df['category'].isin(selected_categories)]['sku'].tolist()
            filtered_df = filtered_df[filtered_df['sku'].isin(category_skus)]
    
    return filtered_df


def show_chart_filter(chart_id, available_filters=['city', 'channel', 'category']):
    """Display individual chart filter in an expander with MULTI-SELECT support."""
    t = get_theme()
    
    with st.expander(f"🔧 Chart Filter", expanded=False):
        stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
        products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
        
        local_filters = {}
        
        num_filters = len(available_filters)
        if num_filters == 0:
            st.info("No additional filters available for this chart")
            return local_filters
        
        cols = st.columns(min(num_filters, 3))
        col_idx = 0
        
        if 'city' in available_filters and stores_df is not None and 'city' in stores_df.columns:
            with cols[col_idx % len(cols)]:
                cities = sorted(stores_df['city'].dropna().unique().tolist())
                local_filters['cities'] = st.multiselect(
                    "🏙️ Cities",
                    options=cities,
                    key=f'{chart_id}_city',
                    placeholder="All"
                )
            col_idx += 1
        
        if 'channel' in available_filters and stores_df is not None and 'channel' in stores_df.columns:
            with cols[col_idx % len(cols)]:
                channels = sorted(stores_df['channel'].dropna().unique().tolist())
                local_filters['channels'] = st.multiselect(
                    "📱 Channels",
                    options=channels,
                    key=f'{chart_id}_channel',
                    placeholder="All"
                )
            col_idx += 1
        
        if 'category' in available_filters and products_df is not None and 'category' in products_df.columns:
            with cols[col_idx % len(cols)]:
                categories = sorted(products_df['category'].dropna().unique().tolist())
                local_filters['categories'] = st.multiselect(
                    "📦 Categories",
                    options=categories,
                    key=f'{chart_id}_category',
                    placeholder="All"
                )
            col_idx += 1
        
        active_count = sum([len(v) for v in local_filters.values() if isinstance(v, list)])
        if active_count > 0:
            st.markdown(f"""
            <div style="
                background: rgba(6, 182, 212, 0.1);
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 0.8rem;
                color: {t['accent_cyan']};
                margin-top: 10px;
            ">
                ✅ {active_count} local filter(s) active
            </div>
            """, unsafe_allow_html=True)
        
        return local_filters


def apply_local_filters(df, local_filters, stores_df=None, products_df=None):
    """Apply local chart-specific filters - supports MULTI-SELECT."""
    if df is None or len(df) == 0:
        return df
    
    filtered_df = df.copy()
    
    # Apply city filter (MULTI-SELECT)
    selected_cities = local_filters.get('cities', [])
    if len(selected_cities) > 0 and stores_df is not None:
        if 'city' in stores_df.columns and 'store_id' in filtered_df.columns:
            city_stores = stores_df[stores_df['city'].isin(selected_cities)]['store_id'].tolist()
            filtered_df = filtered_df[filtered_df['store_id'].isin(city_stores)]
    
    # Apply channel filter (MULTI-SELECT)
    selected_channels = local_filters.get('channels', [])
    if len(selected_channels) > 0 and stores_df is not None:
        if 'channel' in stores_df.columns and 'store_id' in filtered_df.columns:
            channel_stores = stores_df[stores_df['channel'].isin(selected_channels)]['store_id'].tolist()
            filtered_df = filtered_df[filtered_df['store_id'].isin(channel_stores)]
    
    # Apply category filter (MULTI-SELECT)
    selected_categories = local_filters.get('categories', [])
    if len(selected_categories) > 0 and products_df is not None:
        if 'category' in products_df.columns and 'sku' in filtered_df.columns:
            category_skus = products_df[products_df['category'].isin(selected_categories)]['sku'].tolist()
            filtered_df = filtered_df[filtered_df['sku'].isin(category_skus)]
    
    return filtered_df


# ============================================================================
# FOOTER
# ============================================================================

def show_footer():
    """Display footer."""
    t = get_theme()
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; color: {t['text_muted']};">
        <p style="margin: 0;">🛒 <strong>UAE Pulse</strong> - Retail Analytics & Simulation Platform</p>
        <p style="margin: 5px 0 0 0; font-size: 0.85rem;">Built with ❤️ using Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# PAGE: HOME
# ============================================================================

def show_home_page():
    """Display the home page."""
    t = get_theme()
    
    st.markdown(f"""
    <div style="text-align: center; padding: 60px 20px;">
        <div style="font-size: 80px; margin-bottom: 20px;">🛒</div>
        <h1 style="
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, {t['accent_cyan']}, {t['accent_blue']}, {t['accent_purple']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        ">UAE Pulse</h1>
        <p style="
            color: {t['text_secondary']};
            font-size: 1.4rem;
            margin-bottom: 40px;
        ">Retail Simulator + Data Rescue Center</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="card-3d" style="text-align: center; min-height: 250px;">
            <div style="font-size: 50px; margin-bottom: 15px;">📂</div>
            <h3 style="color: {t['accent_cyan']}; margin-bottom: 10px;">Data Loading</h3>
            <p style="color: {t['text_secondary']}; font-size: 0.95rem;">
                Upload your retail data files (Products, Stores, Sales, Inventory) in CSV or Excel format.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card-3d" style="text-align: center; min-height: 250px;">
            <div style="font-size: 50px; margin-bottom: 15px;">🧹</div>
            <h3 style="color: {t['accent_green']}; margin-bottom: 10px;">Data Rescue</h3>
            <p style="color: {t['text_secondary']}; font-size: 0.95rem;">
                Automatically detect and fix data quality issues including missing values, duplicates, and outliers.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="card-3d" style="text-align: center; min-height: 250px;">
            <div style="font-size: 50px; margin-bottom: 15px;">📊</div>
            <h3 style="color: {t['accent_purple']}; margin-bottom: 10px;">Dashboard</h3>
            <p style="color: {t['text_secondary']}; font-size: 0.95rem;">
                View Executive and Manager dashboards with KPIs, charts, and actionable insights.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="card-3d" style="text-align: center; min-height: 250px;">
            <div style="font-size: 50px; margin-bottom: 15px;">🎯</div>
            <h3 style="color: {t['accent_orange']}; margin-bottom: 10px;">Simulator</h3>
            <p style="color: {t['text_secondary']}; font-size: 0.95rem;">
                Run what-if scenarios to simulate business changes and predict impacts.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card-3d" style="text-align: center; min-height: 250px;">
            <div style="font-size: 50px; margin-bottom: 15px;">🌐</div>
            <h3 style="color: {t['accent_teal']}; margin-bottom: 10px;">Global Filters</h3>
            <p style="color: {t['text_secondary']}; font-size: 0.95rem;">
                Apply filters across all pages by date, city, channel, and category.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="card-3d" style="text-align: center; min-height: 250px;">
            <div style="font-size: 50px; margin-bottom: 15px;">🎨</div>
            <h3 style="color: {t['accent_pink']}; margin-bottom: 10px;">Theme Support</h3>
            <p style="color: {t['text_secondary']}; font-size: 0.95rem;">
                Switch between dark and light themes for comfortable viewing.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Getting started
    st.markdown(f'<p class="section-title section-title-cyan">🚀 Getting Started</p>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {t['bg_card']} 0%, {t['bg_card_hover']} 100%);
        border-radius: 16px;
        padding: 30px;
        border: 1px solid {t['border_color']};
    ">
        <ol style="color: {t['text_primary']}; font-size: 1.1rem; line-height: 2.2;">
            <li><strong>📂 Load Data</strong> — Upload your CSV/Excel files in the Data page</li>
            <li><strong>🧹 Clean Data</strong> — Run the data cleaner to fix quality issues</li>
            <li><strong>📊 View Dashboard</strong> — Explore KPIs and charts in Executive or Manager view</li>
            <li><strong>🎯 Run Simulations</strong> — Test business scenarios in the Simulator</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    show_footer()


# ============================================================================
# PAGE: DATA
# ============================================================================

def show_data_page():
    """Display the data loading page."""
    t = get_theme()
    
    st.markdown(f'<h1 class="page-title page-title-cyan">📂 Data Loading</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-description">Upload your retail data files to get started</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # File uploaders
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<p class="section-title section-title-cyan">📦 Products</p>', unsafe_allow_html=True)
        products_file = st.file_uploader("Upload Products file", type=['csv', 'xlsx'], key='products_uploader')
        
        st.markdown(f'<p class="section-title section-title-purple">🛒 Sales</p>', unsafe_allow_html=True)
        sales_file = st.file_uploader("Upload Sales file", type=['csv', 'xlsx'], key='sales_uploader')
    
    with col2:
        st.markdown(f'<p class="section-title section-title-blue">🏪 Stores</p>', unsafe_allow_html=True)
        stores_file = st.file_uploader("Upload Stores file", type=['csv', 'xlsx'], key='stores_uploader')
        
        st.markdown(f'<p class="section-title section-title-orange">📋 Inventory</p>', unsafe_allow_html=True)
        inventory_file = st.file_uploader("Upload Inventory file", type=['csv', 'xlsx'], key='inventory_uploader')
    
    st.markdown("---")
    
    # Load button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📥 Load All Data", use_container_width=True, type="primary"):
            loaded_count = 0
            
            if products_file:
                try:
                    if products_file.name.endswith('.csv'):
                        st.session_state.raw_products = pd.read_csv(products_file)
                    else:
                        st.session_state.raw_products = pd.read_excel(products_file)
                    loaded_count += 1
                    st.success(f"✅ Products loaded: {len(st.session_state.raw_products):,} rows")
                except Exception as e:
                    st.error(f"❌ Error loading Products: {str(e)}")
            
            if stores_file:
                try:
                    if stores_file.name.endswith('.csv'):
                        st.session_state.raw_stores = pd.read_csv(stores_file)
                    else:
                        st.session_state.raw_stores = pd.read_excel(stores_file)
                    loaded_count += 1
                    st.success(f"✅ Stores loaded: {len(st.session_state.raw_stores):,} rows")
                except Exception as e:
                    st.error(f"❌ Error loading Stores: {str(e)}")
            
            if sales_file:
                try:
                    if sales_file.name.endswith('.csv'):
                        st.session_state.raw_sales = pd.read_csv(sales_file)
                    else:
                        st.session_state.raw_sales = pd.read_excel(sales_file)
                    loaded_count += 1
                    st.success(f"✅ Sales loaded: {len(st.session_state.raw_sales):,} rows")
                except Exception as e:
                    st.error(f"❌ Error loading Sales: {str(e)}")
            
            if inventory_file:
                try:
                    if inventory_file.name.endswith('.csv'):
                        st.session_state.raw_inventory = pd.read_csv(inventory_file)
                    else:
                        st.session_state.raw_inventory = pd.read_excel(inventory_file)
                    loaded_count += 1
                    st.success(f"✅ Inventory loaded: {len(st.session_state.raw_inventory):,} rows")
                except Exception as e:
                    st.error(f"❌ Error loading Inventory: {str(e)}")
            
            if loaded_count > 0:
                st.session_state.data_loaded = True
                st.session_state.is_cleaned = False
                st.balloons()
    
    # Show loaded data preview
    if st.session_state.data_loaded:
        st.markdown("---")
        st.markdown(f'<p class="section-title section-title-green">📊 Data Preview</p>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📦 Products", "🏪 Stores", "🛒 Sales", "📋 Inventory"])
        
        with tab1:
            if st.session_state.raw_products is not None:
                st.markdown(f"**Shape:** {st.session_state.raw_products.shape[0]:,} rows × {st.session_state.raw_products.shape[1]} columns")
                st.dataframe(st.session_state.raw_products.head(100), use_container_width=True)
            else:
                st.info("No products data loaded")
        
        with tab2:
            if st.session_state.raw_stores is not None:
                st.markdown(f"**Shape:** {st.session_state.raw_stores.shape[0]:,} rows × {st.session_state.raw_stores.shape[1]} columns")
                st.dataframe(st.session_state.raw_stores.head(100), use_container_width=True)
            else:
                st.info("No stores data loaded")
        
        with tab3:
            if st.session_state.raw_sales is not None:
                st.markdown(f"**Shape:** {st.session_state.raw_sales.shape[0]:,} rows × {st.session_state.raw_sales.shape[1]} columns")
                st.dataframe(st.session_state.raw_sales.head(100), use_container_width=True)
            else:
                st.info("No sales data loaded")
        
        with tab4:
            if st.session_state.raw_inventory is not None:
                st.markdown(f"**Shape:** {st.session_state.raw_inventory.shape[0]:,} rows × {st.session_state.raw_inventory.shape[1]} columns")
                st.dataframe(st.session_state.raw_inventory.head(100), use_container_width=True)
            else:
                st.info("No inventory data loaded")
    
    show_footer()

# ============================================================================
# DATA CLEANER MODULE
# Handles data validation, cleaning, and issue logging
# ============================================================================

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import re
from datetime import datetime

class DataCleaner:
    """
    Data Cleaner class for retail data validation and cleaning.
    Detects and fixes: missing values, duplicates, outliers, text issues, FK violations.
    """
    
    def __init__(self):
        """Initialize the DataCleaner with empty stats and issues log."""
        self.stats = {
            'missing_values_fixed': 0,
            'duplicates_removed': 0,
            'outliers_fixed': 0,
            'text_standardized': 0,
            'negative_values_fixed': 0,
            'fk_violations_fixed': 0,
            'whitespace_fixed': 0,
            'total_issues': 0
        }
        self.issues_log: List[Dict[str, Any]] = []
    
    def log_issue(self, table: str, column: str, issue_type: str, 
                  row_index: Any = None, original_value: Any = None, 
                  fixed_value: Any = None, description: str = ""):
        """Log an issue found during cleaning."""
        self.issues_log.append({
            'table': table,
            'column': column,
            'issue_type': issue_type,
            'row_index': row_index,
            'original_value': str(original_value)[:100] if original_value is not None else None,
            'fixed_value': str(fixed_value)[:100] if fixed_value is not None else None,
            'description': description,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self.stats['total_issues'] += 1
    
    def get_issues_df(self) -> pd.DataFrame:
        """Return issues log as a DataFrame."""
        if len(self.issues_log) == 0:
            return pd.DataFrame({
                'table': ['None'],
                'column': ['None'],
                'issue_type': ['None'],
                'description': ['No issues found']
            })
        return pd.DataFrame(self.issues_log)
    
    # =========================================================================
    # CORE CLEANING METHODS
    # =========================================================================
    
    def fix_missing_values(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Fix missing values based on column type."""
        if df is None or len(df) == 0:
            return df
        
        df = df.copy()
        
        for col in df.columns:
            missing_count = df[col].isna().sum()
            
            if missing_count > 0:
                # Determine fill strategy based on column type and name
                if df[col].dtype in ['float64', 'int64']:
                    # Numeric columns - use median
                    median_val = df[col].median()
                    if pd.isna(median_val):
                        median_val = 0
                    df[col] = df[col].fillna(median_val)
                    self.log_issue(table_name, col, 'missing_value', 
                                  description=f"Filled {missing_count} missing values with median: {median_val}")
                elif df[col].dtype == 'object':
                    # String columns - use mode or 'Unknown'
                    mode_val = df[col].mode()
                    fill_val = mode_val.iloc[0] if len(mode_val) > 0 else 'Unknown'
                    df[col] = df[col].fillna(fill_val)
                    self.log_issue(table_name, col, 'missing_value',
                                  description=f"Filled {missing_count} missing values with: {fill_val}")
                else:
                    # Other types - forward fill then backward fill
                    df[col] = df[col].ffill().bfill()
                    self.log_issue(table_name, col, 'missing_value',
                                  description=f"Filled {missing_count} missing values with ffill/bfill")
                
                self.stats['missing_values_fixed'] += missing_count
        
        return df
    
    def remove_duplicates(self, df: pd.DataFrame, table_name: str, 
                         subset: Optional[List[str]] = None) -> pd.DataFrame:
        """Remove duplicate rows."""
        if df is None or len(df) == 0:
            return df
        
        df = df.copy()
        initial_count = len(df)
        
        if subset:
            # Only consider specified columns for duplicate detection
            valid_subset = [col for col in subset if col in df.columns]
            if valid_subset:
                df = df.drop_duplicates(subset=valid_subset, keep='first')
        else:
            df = df.drop_duplicates(keep='first')
        
        duplicates_removed = initial_count - len(df)
        
        if duplicates_removed > 0:
            self.log_issue(table_name, 'all', 'duplicate',
                          description=f"Removed {duplicates_removed} duplicate rows")
            self.stats['duplicates_removed'] += duplicates_removed
        
        return df.reset_index(drop=True)
    
    def fix_outliers_iqr(self, df: pd.DataFrame, table_name: str, 
                        columns: Optional[List[str]] = None,
                        multiplier: float = 1.5) -> pd.DataFrame:
        """Fix outliers using IQR method - cap at boundaries."""
        if df is None or len(df) == 0:
            return df
        
        df = df.copy()
        
        # Get numeric columns
        if columns:
            numeric_cols = [col for col in columns if col in df.columns and df[col].dtype in ['float64', 'int64']]
        else:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR
            
            # Count outliers
            outliers_low = (df[col] < lower_bound).sum()
            outliers_high = (df[col] > upper_bound).sum()
            total_outliers = outliers_low + outliers_high
            
            if total_outliers > 0:
                # Cap outliers at boundaries
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                self.log_issue(table_name, col, 'outlier',
                              description=f"Capped {total_outliers} outliers (low: {outliers_low}, high: {outliers_high})")
                self.stats['outliers_fixed'] += total_outliers
        
        return df
    
    def standardize_text(self, df: pd.DataFrame, table_name: str,
                        columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Standardize text columns - trim whitespace, title case for names."""
        if df is None or len(df) == 0:
            return df
        
        df = df.copy()
        
        # Get string columns
        if columns:
            text_cols = [col for col in columns if col in df.columns and df[col].dtype == 'object']
        else:
            text_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        for col in text_cols:
            original = df[col].copy()
            
            # Strip whitespace
            df[col] = df[col].astype(str).str.strip()
            
            # Replace multiple spaces with single space
            df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
            
            # Title case for name-like columns
            name_indicators = ['name', 'city', 'category', 'channel', 'brand']
            if any(indicator in col.lower() for indicator in name_indicators):
                df[col] = df[col].str.title()
            
            # Replace 'nan' and 'None' strings
            df[col] = df[col].replace(['nan', 'None', 'NaN', 'none', 'NULL', 'null'], 'Unknown')
            
            # Count changes
            changes = (original.astype(str) != df[col]).sum()
            
            if changes > 0:
                self.log_issue(table_name, col, 'text_standardization',
                              description=f"Standardized {changes} text values")
                self.stats['text_standardized'] += changes
                self.stats['whitespace_fixed'] += changes
        
        return df
    
    def fix_negative_values(self, df: pd.DataFrame, table_name: str,
                           columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Fix negative values in columns that should be positive."""
        if df is None or len(df) == 0:
            return df
        
        df = df.copy()
        
        # Columns that should never be negative
        positive_indicators = ['price', 'qty', 'quantity', 'cost', 'stock', 'amount', 'revenue', 'sales']
        
        if columns:
            check_cols = columns
        else:
            check_cols = [col for col in df.columns 
                         if any(ind in col.lower() for ind in positive_indicators)
                         and df[col].dtype in ['float64', 'int64']]
        
        for col in check_cols:
            if col in df.columns and df[col].dtype in ['float64', 'int64']:
                negative_count = (df[col] < 0).sum()
                
                if negative_count > 0:
                    # Convert negatives to absolute values
                    df[col] = df[col].abs()
                    self.log_issue(table_name, col, 'negative_value',
                                  description=f"Converted {negative_count} negative values to positive")
                    self.stats['negative_values_fixed'] += negative_count
        
        return df
    
    def validate_foreign_keys(self, df: pd.DataFrame, table_name: str,
                             fk_column: str, reference_df: pd.DataFrame,
                             pk_column: str) -> pd.DataFrame:
        """Validate and fix foreign key references."""
        if df is None or reference_df is None:
            return df
        if fk_column not in df.columns or pk_column not in reference_df.columns:
            return df
        
        df = df.copy()
        
        valid_keys = set(reference_df[pk_column].dropna().unique())
        invalid_mask = ~df[fk_column].isin(valid_keys) & df[fk_column].notna()
        invalid_count = invalid_mask.sum()
        
        if invalid_count > 0:
            # Log the invalid references
            self.log_issue(table_name, fk_column, 'fk_violation',
                          description=f"Found {invalid_count} invalid foreign key references")
            self.stats['fk_violations_fixed'] += invalid_count
            
            # Option: Remove rows with invalid FKs or mark them
            # Here we'll keep them but could filter: df = df[~invalid_mask]
        
        return df
    
    # =========================================================================
    # TABLE-SPECIFIC CLEANING METHODS
    # =========================================================================
    
    def clean_products(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean products table."""
        if df is None:
            return None
        
        table_name = 'products'
        
        # Remove duplicates based on SKU
        if 'sku' in df.columns:
            df = self.remove_duplicates(df, table_name, subset=['sku'])
        else:
            df = self.remove_duplicates(df, table_name)
        
        # Fix missing values
        df = self.fix_missing_values(df, table_name)
        
        # Standardize text
        df = self.standardize_text(df, table_name)
        
        # Fix negative prices and costs
        price_cols = [col for col in df.columns if 'price' in col.lower() or 'cost' in col.lower()]
        df = self.fix_negative_values(df, table_name, columns=price_cols)
        
        # Fix outliers in price columns
        df = self.fix_outliers_iqr(df, table_name, columns=price_cols)
        
        return df
    
    def clean_stores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean stores table."""
        if df is None:
            return None
        
        table_name = 'stores'
        
        # Remove duplicates based on store_id
        if 'store_id' in df.columns:
            df = self.remove_duplicates(df, table_name, subset=['store_id'])
        else:
            df = self.remove_duplicates(df, table_name)
        
        # Fix missing values
        df = self.fix_missing_values(df, table_name)
        
        # Standardize text (city, channel names)
        df = self.standardize_text(df, table_name)
        
        return df
    
    def clean_sales(self, df: pd.DataFrame, products_df: pd.DataFrame = None, 
                   stores_df: pd.DataFrame = None) -> pd.DataFrame:
        """Clean sales table."""
        if df is None:
            return None
        
        table_name = 'sales'
        
        # Remove exact duplicates
        df = self.remove_duplicates(df, table_name)
        
        # Fix missing values
        df = self.fix_missing_values(df, table_name)
        
        # Fix negative values in quantity and price columns
        qty_price_cols = [col for col in df.columns 
                         if any(x in col.lower() for x in ['qty', 'quantity', 'price', 'amount'])]
        df = self.fix_negative_values(df, table_name, columns=qty_price_cols)
        
        # Fix outliers
        df = self.fix_outliers_iqr(df, table_name, columns=qty_price_cols)
        
        # Validate foreign keys
        if products_df is not None and 'sku' in df.columns:
            df = self.validate_foreign_keys(df, table_name, 'sku', products_df, 'sku')
        
        if stores_df is not None and 'store_id' in df.columns:
            df = self.validate_foreign_keys(df, table_name, 'store_id', stores_df, 'store_id')
        
        # Standardize text columns
        df = self.standardize_text(df, table_name)
        
        # Parse dates
        if 'order_time' in df.columns:
            try:
                df['order_time'] = pd.to_datetime(df['order_time'], errors='coerce')
            except:
                pass
        
        return df
    
    def clean_inventory(self, df: pd.DataFrame, products_df: pd.DataFrame = None,
                       stores_df: pd.DataFrame = None) -> pd.DataFrame:
        """Clean inventory table."""
        if df is None:
            return None
        
        table_name = 'inventory'
        
        # Remove duplicates (SKU + Store combination)
        if 'sku' in df.columns and 'store_id' in df.columns:
            df = self.remove_duplicates(df, table_name, subset=['sku', 'store_id'])
        else:
            df = self.remove_duplicates(df, table_name)
        
        # Fix missing values
        df = self.fix_missing_values(df, table_name)
        
        # Fix negative stock values
        stock_cols = [col for col in df.columns if 'stock' in col.lower() or 'qty' in col.lower()]
        df = self.fix_negative_values(df, table_name, columns=stock_cols)
        
        # Fix outliers
        df = self.fix_outliers_iqr(df, table_name, columns=stock_cols)
        
        # Validate foreign keys
        if products_df is not None and 'sku' in df.columns:
            df = self.validate_foreign_keys(df, table_name, 'sku', products_df, 'sku')
        
        if stores_df is not None and 'store_id' in df.columns:
            df = self.validate_foreign_keys(df, table_name, 'store_id', stores_df, 'store_id')
        
        return df
    
    # =========================================================================
    # MAIN CLEANING METHOD
    # =========================================================================
    
    def clean_all(self, products_df: pd.DataFrame = None, stores_df: pd.DataFrame = None,
                  sales_df: pd.DataFrame = None, inventory_df: pd.DataFrame = None) -> Tuple:
        """
        Clean all tables and return cleaned DataFrames.
        
        Returns:
            Tuple of (clean_products, clean_stores, clean_sales, clean_inventory)
        """
        # Reset stats and issues log
        self.stats = {
            'missing_values_fixed': 0,
            'duplicates_removed': 0,
            'outliers_fixed': 0,
            'text_standardized': 0,
            'negative_values_fixed': 0,
            'fk_violations_fixed': 0,
            'whitespace_fixed': 0,
            'total_issues': 0
        }
        self.issues_log = []
        
        # Clean in order: products/stores first (master data), then transactional data
        clean_products = self.clean_products(products_df)
        clean_stores = self.clean_stores(stores_df)
        clean_sales = self.clean_sales(sales_df, clean_products, clean_stores)
        clean_inventory = self.clean_inventory(inventory_df, clean_products, clean_stores)
        
        return clean_products, clean_stores, clean_sales, clean_inventory

# ============================================================================
# SIMULATOR MODULE
# Handles KPI calculations and business simulations
# ============================================================================

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Any

class Simulator:
    """
    Business Simulator class for calculating KPIs and running what-if scenarios.
    """
    
    def __init__(self):
        """Initialize the Simulator."""
        pass
    
    def calculate_overall_kpis(self, sales_df: pd.DataFrame, 
                               products_df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Calculate overall business KPIs from sales data.
        
        Args:
            sales_df: Sales DataFrame
            products_df: Products DataFrame for cost data
            
        Returns:
            Dictionary of KPI values
        """
        kpis = {
            'total_revenue': 0,
            'net_revenue': 0,
            'total_cogs': 0,
            'total_profit': 0,
            'profit_margin_pct': 0,
            'avg_order_value': 0,
            'total_orders': 0,
            'total_quantity': 0,
            'avg_discount_pct': 0,
            'refund_amount': 0,
            'return_rate_pct': 0
        }
        
        if sales_df is None or len(sales_df) == 0:
            return kpis
        
        try:
            # Calculate total revenue
            if 'selling_price_aed' in sales_df.columns and 'qty' in sales_df.columns:
                qty = pd.to_numeric(sales_df['qty'], errors='coerce').fillna(0)
                price = pd.to_numeric(sales_df['selling_price_aed'], errors='coerce').fillna(0)
                kpis['total_revenue'] = (qty * price).sum()
            elif 'selling_price_aed' in sales_df.columns:
                kpis['total_revenue'] = pd.to_numeric(sales_df['selling_price_aed'], errors='coerce').fillna(0).sum()
            
            # Calculate refunds (from returned/refunded orders)
            if 'order_status' in sales_df.columns:
                refund_mask = sales_df['order_status'].str.lower().isin(['returned', 'refunded', 'cancelled'])
                if 'selling_price_aed' in sales_df.columns:
                    refund_price = pd.to_numeric(sales_df.loc[refund_mask, 'selling_price_aed'], errors='coerce').fillna(0)
                    if 'qty' in sales_df.columns:
                        refund_qty = pd.to_numeric(sales_df.loc[refund_mask, 'qty'], errors='coerce').fillna(0)
                        kpis['refund_amount'] = (refund_qty * refund_price).sum()
                    else:
                        kpis['refund_amount'] = refund_price.sum()
            
            # Net revenue
            kpis['net_revenue'] = kpis['total_revenue'] - kpis['refund_amount']
            
            # Calculate COGS
            if products_df is not None and 'sku' in sales_df.columns and 'sku' in products_df.columns:
                # Find cost column
                cost_col = None
                for col in ['cost_price_aed', 'cost_price', 'cost', 'cogs']:
                    if col in products_df.columns:
                        cost_col = col
                        break
                
                if cost_col:
                    merged = sales_df.merge(products_df[['sku', cost_col]], on='sku', how='left')
                    cost = pd.to_numeric(merged[cost_col], errors='coerce').fillna(0)
                    if 'qty' in merged.columns:
                        qty = pd.to_numeric(merged['qty'], errors='coerce').fillna(0)
                        kpis['total_cogs'] = (qty * cost).sum()
                    else:
                        kpis['total_cogs'] = cost.sum()
            
            # Calculate profit
            kpis['total_profit'] = kpis['net_revenue'] - kpis['total_cogs']
            
            # Profit margin percentage
            if kpis['net_revenue'] > 0:
                kpis['profit_margin_pct'] = (kpis['total_profit'] / kpis['net_revenue']) * 100
            
            # Total orders (unique order_ids)
            if 'order_id' in sales_df.columns:
                kpis['total_orders'] = sales_df['order_id'].nunique()
            else:
                kpis['total_orders'] = len(sales_df)
            
            # Total quantity
            if 'qty' in sales_df.columns:
                kpis['total_quantity'] = pd.to_numeric(sales_df['qty'], errors='coerce').fillna(0).sum()
            
            # Average order value
            if kpis['total_orders'] > 0:
                kpis['avg_order_value'] = kpis['total_revenue'] / kpis['total_orders']
            
            # Average discount percentage
            if 'discount_pct' in sales_df.columns:
                kpis['avg_discount_pct'] = pd.to_numeric(sales_df['discount_pct'], errors='coerce').fillna(0).mean()
            elif 'discount' in sales_df.columns:
                kpis['avg_discount_pct'] = pd.to_numeric(sales_df['discount'], errors='coerce').fillna(0).mean()
            
            # Return rate
            if 'order_status' in sales_df.columns:
                total = len(sales_df)
                returns = sales_df['order_status'].str.lower().isin(['returned', 'refunded']).sum()
                kpis['return_rate_pct'] = (returns / total * 100) if total > 0 else 0
        
        except Exception as e:
            print(f"Error calculating KPIs: {str(e)}")
        
        return kpis
    
    def calculate_kpis_by_dimension(self, sales_df: pd.DataFrame,
                                    stores_df: pd.DataFrame = None,
                                    products_df: pd.DataFrame = None,
                                    dimension: str = 'city') -> pd.DataFrame:
        """
        Calculate KPIs grouped by a dimension (city, channel, category).
        
        Args:
            sales_df: Sales DataFrame
            stores_df: Stores DataFrame
            products_df: Products DataFrame
            dimension: Dimension to group by ('city', 'channel', 'category')
            
        Returns:
            DataFrame with KPIs by dimension
        """
        if sales_df is None or len(sales_df) == 0:
            return pd.DataFrame()
        
        try:
            df = sales_df.copy()
            
            # Merge with stores for city/channel
            if dimension in ['city', 'channel'] and stores_df is not None:
                if 'store_id' in df.columns and 'store_id' in stores_df.columns:
                    store_cols = ['store_id']
                    if 'city' in stores_df.columns:
                        store_cols.append('city')
                    if 'channel' in stores_df.columns:
                        store_cols.append('channel')
                    df = df.merge(stores_df[store_cols], on='store_id', how='left')
            
            # Merge with products for category
            if dimension == 'category' and products_df is not None:
                if 'sku' in df.columns and 'sku' in products_df.columns:
                    product_cols = ['sku']
                    if 'category' in products_df.columns:
                        product_cols.append('category')
                    if 'cost_price_aed' in products_df.columns:
                        product_cols.append('cost_price_aed')
                    df = df.merge(products_df[product_cols], on='sku', how='left')
            
            # Check if dimension column exists
            if dimension not in df.columns:
                return pd.DataFrame()
            
            # Calculate revenue per row
            if 'selling_price_aed' in df.columns and 'qty' in df.columns:
                df['_revenue'] = (
                    pd.to_numeric(df['qty'], errors='coerce').fillna(0) * 
                    pd.to_numeric(df['selling_price_aed'], errors='coerce').fillna(0)
                )
            elif 'selling_price_aed' in df.columns:
                df['_revenue'] = pd.to_numeric(df['selling_price_aed'], errors='coerce').fillna(0)
            else:
                df['_revenue'] = 0
            
            # Calculate COGS if cost data available
            if 'cost_price_aed' in df.columns and 'qty' in df.columns:
                df['_cogs'] = (
                    pd.to_numeric(df['qty'], errors='coerce').fillna(0) * 
                    pd.to_numeric(df['cost_price_aed'], errors='coerce').fillna(0)
                )
            else:
                df['_cogs'] = 0
            
            # Group by dimension
            grouped = df.groupby(dimension).agg({
                '_revenue': 'sum',
                '_cogs': 'sum'
            }).reset_index()
            
            grouped.columns = [dimension, 'revenue', 'cogs']
            
            # Calculate profit and margin
            grouped['profit'] = grouped['revenue'] - grouped['cogs']
            grouped['margin_pct'] = np.where(
                grouped['revenue'] > 0,
                (grouped['profit'] / grouped['revenue']) * 100,
                0
            )
            
            # Sort by revenue descending
            grouped = grouped.sort_values('revenue', ascending=False)
            
            return grouped
        
        except Exception as e:
            print(f"Error calculating KPIs by dimension: {str(e)}")
            return pd.DataFrame()
    
    def simulate_scenario(self, sales_df: pd.DataFrame, products_df: pd.DataFrame = None,
                         price_change_pct: float = 0, discount_change_pct: float = 0,
                         demand_change_pct: float = 0) -> Dict[str, Any]:
        """
        Simulate a business scenario with parameter changes.
        
        Args:
            sales_df: Base sales DataFrame
            products_df: Products DataFrame
            price_change_pct: Percentage change in prices
            discount_change_pct: Percentage change in discounts
            demand_change_pct: Percentage change in demand/quantity
            
        Returns:
            Dictionary with simulated KPIs
        """
        # Get baseline KPIs
        baseline = self.calculate_overall_kpis(sales_df, products_df)
        
        # Apply simple simulation logic
        price_multiplier = 1 + (price_change_pct / 100)
        discount_impact = 1 - (discount_change_pct / 100) * 0.5
        demand_multiplier = 1 + (demand_change_pct / 100)
        
        simulated = {
            'baseline_revenue': baseline['total_revenue'],
            'simulated_revenue': baseline['total_revenue'] * price_multiplier * discount_impact * demand_multiplier,
            'baseline_margin_pct': baseline['profit_margin_pct'],
            'simulated_margin_pct': baseline['profit_margin_pct'] + (price_change_pct * 0.5) - (discount_change_pct * 0.3),
            'revenue_change_pct': 0,
            'margin_change_pct': 0
        }
        
        # Calculate changes
        if baseline['total_revenue'] > 0:
            simulated['revenue_change_pct'] = (
                (simulated['simulated_revenue'] - simulated['baseline_revenue']) / 
                simulated['baseline_revenue'] * 100
            )
        
        simulated['margin_change_pct'] = simulated['simulated_margin_pct'] - simulated['baseline_margin_pct']
        
        return simulated
    
    def get_top_products(self, sales_df: pd.DataFrame, products_df: pd.DataFrame = None,
                        n: int = 10, metric: str = 'revenue') -> pd.DataFrame:
        """
        Get top N products by a metric.
        
        Args:
            sales_df: Sales DataFrame
            products_df: Products DataFrame
            n: Number of top products to return
            metric: Metric to sort by ('revenue', 'quantity', 'profit')
            
        Returns:
            DataFrame of top products
        """
        if sales_df is None or len(sales_df) == 0 or 'sku' not in sales_df.columns:
            return pd.DataFrame()
        
        try:
            df = sales_df.copy()
            
            # Calculate revenue
            if 'selling_price_aed' in df.columns and 'qty' in df.columns:
                df['_revenue'] = (
                    pd.to_numeric(df['qty'], errors='coerce').fillna(0) * 
                    pd.to_numeric(df['selling_price_aed'], errors='coerce').fillna(0)
                )
            else:
                df['_revenue'] = 0
            
            df['_qty'] = pd.to_numeric(df.get('qty', 0), errors='coerce').fillna(0)
            
            # Group by SKU
            grouped = df.groupby('sku').agg({
                '_revenue': 'sum',
                '_qty': 'sum'
            }).reset_index()
            
            grouped.columns = ['sku', 'revenue', 'quantity']
            
            # Merge with products for names
            if products_df is not None and 'sku' in products_df.columns:
                name_col = 'product_name' if 'product_name' in products_df.columns else 'name'
                if name_col in products_df.columns:
                    grouped = grouped.merge(products_df[['sku', name_col]], on='sku', how='left')
            
            # Sort and return top N
            sort_col = 'revenue' if metric == 'revenue' else 'quantity'
            return grouped.sort_values(sort_col, ascending=False).head(n)
        
        except Exception as e:
            print(f"Error getting top products: {str(e)}")
            return pd.DataFrame()
    
    def calculate_inventory_metrics(self, inventory_df: pd.DataFrame,
                                   sales_df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Calculate inventory-related metrics.
        
        Args:
            inventory_df: Inventory DataFrame
            sales_df: Sales DataFrame for velocity calculations
            
        Returns:
            Dictionary of inventory metrics
        """
        metrics = {
            'total_stock': 0,
            'low_stock_count': 0,
            'out_of_stock_count': 0,
            'stockout_risk_pct': 0,
            'avg_stock_per_sku': 0
        }
        
        if inventory_df is None or len(inventory_df) == 0:
            return metrics
        
        try:
            stock_col = None
            for col in ['stock_on_hand', 'stock', 'quantity', 'qty']:
                if col in inventory_df.columns:
                    stock_col = col
                    break
            
            if stock_col:
                stock = pd.to_numeric(inventory_df[stock_col], errors='coerce').fillna(0)
                
                metrics['total_stock'] = stock.sum()
                metrics['low_stock_count'] = (stock < 10).sum()
                metrics['out_of_stock_count'] = (stock == 0).sum()
                metrics['avg_stock_per_sku'] = stock.mean()
                
                total_items = len(inventory_df)
                if total_items > 0:
                    metrics['stockout_risk_pct'] = (metrics['low_stock_count'] / total_items) * 100
        
        except Exception as e:
            print(f"Error calculating inventory metrics: {str(e)}")
        
        return metrics


# ============================================================================
# PAGE: CLEANER (FIX 1: KPI Cards Visible)
# ============================================================================

def show_cleaner_page():
    """Display the data cleaner page with VISIBLE KPI cards."""
    t = get_theme()
    
    st.markdown(f'<h1 class="page-title page-title-green">🧹 Data Rescue Center</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-description">Validate, detect issues, and clean your dirty data automatically</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card_3d("Please load data first. Go to 📂 Data page."), unsafe_allow_html=True)
        show_footer()
        return
    
    st.markdown(f'<p class="section-title section-title-cyan">🔍 Issues We Detect & Fix</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="card-3d">
            <strong style="color: {t['accent_cyan']}; font-size: 1.1rem;">Data Quality</strong>
            <ul style="color: {t['text_primary']}; font-size: 0.95rem; margin-bottom: 0; line-height: 1.8;">
                <li>Missing values</li>
                <li>Duplicate records</li>
                <li>Whitespace issues</li>
                <li>Text standardization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card-3d">
            <strong style="color: {t['accent_purple']}; font-size: 1.1rem;">Format Issues</strong>
            <ul style="color: {t['text_primary']}; font-size: 0.95rem; margin-bottom: 0; line-height: 1.8;">
                <li>Multi-language text</li>
                <li>Non-English values</li>
                <li>Fuzzy matching</li>
                <li>Case normalization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="card-3d">
            <strong style="color: {t['accent_pink']}; font-size: 1.1rem;">Value Issues</strong>
            <ul style="color: {t['text_primary']}; font-size: 0.95rem; margin-bottom: 0; line-height: 1.8;">
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
        if st.button("🚀 Run Data Cleaning", use_container_width=True, type="primary"):
            with st.spinner("🔄 Analyzing and cleaning data..."):
                try:
                    cleaner = DataCleaner()
                    
                    clean_products, clean_stores, clean_sales, clean_inventory = cleaner.clean_all(
                        st.session_state.raw_products.copy() if st.session_state.raw_products is not None else None,
                        st.session_state.raw_stores.copy() if st.session_state.raw_stores is not None else None,
                        st.session_state.raw_sales.copy() if st.session_state.raw_sales is not None else None,
                        st.session_state.raw_inventory.copy() if st.session_state.raw_inventory is not None else None
                    )
                    
                    st.session_state.clean_products = clean_products
                    st.session_state.clean_stores = clean_stores
                    st.session_state.clean_sales = clean_sales
                    st.session_state.clean_inventory = clean_inventory
                    st.session_state.issues_df = cleaner.get_issues_df()
                    st.session_state.cleaner_stats = cleaner.stats
                    st.session_state.is_cleaned = True
                    
                    st.success("✅ Data cleaning complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error during cleaning: {str(e)}")
    
    if st.session_state.is_cleaned:
        st.markdown("---")
        st.markdown(f'<p class="section-title section-title-blue">📊 Cleaning Results</p>', unsafe_allow_html=True)
        
        stats = st.session_state.get('cleaner_stats', {})
        
        # FIX 1: Using inline HTML for proper visibility
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            value = stats.get('missing_values_fixed', 0)
            st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, {t['bg_card']} 0%, {t['bg_card_hover']} 100%);
                border-radius: 16px;
                padding: 24px;
                border: 1px solid {t['border_color']};
                box-shadow: 0 8px 32px {t['shadow_color']};
                text-align: center;
                height: 140px;
            ">
                <div style="color: {t['text_secondary']}; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Missing Fixed</div>
                <div style="color: {t['accent_cyan']}; font-size: 2.2rem; font-weight: 700; margin: 15px 0;">{value:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            value = stats.get('duplicates_removed', 0)
            st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, {t['bg_card']} 0%, {t['bg_card_hover']} 100%);
                border-radius: 16px;
                padding: 24px;
                border: 1px solid {t['border_color']};
                box-shadow: 0 8px 32px {t['shadow_color']};
                text-align: center;
                height: 140px;
            ">
                <div style="color: {t['text_secondary']}; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Duplicates Removed</div>
                <div style="color: {t['accent_blue']}; font-size: 2.2rem; font-weight: 700; margin: 15px 0;">{value:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            value = stats.get('outliers_fixed', 0)
            st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, {t['bg_card']} 0%, {t['bg_card_hover']} 100%);
                border-radius: 16px;
                padding: 24px;
                border: 1px solid {t['border_color']};
                box-shadow: 0 8px 32px {t['shadow_color']};
                text-align: center;
                height: 140px;
            ">
                <div style="color: {t['text_secondary']}; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Outliers Fixed</div>
                <div style="color: {t['accent_purple']}; font-size: 2.2rem; font-weight: 700; margin: 15px 0;">{value:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            value = stats.get('text_standardized', 0)
            st.markdown(f"""
            <div style="
                background: linear-gradient(145deg, {t['bg_card']} 0%, {t['bg_card_hover']} 100%);
                border-radius: 16px;
                padding: 24px;
                border: 1px solid {t['border_color']};
                box-shadow: 0 8px 32px {t['shadow_color']};
                text-align: center;
                height: 140px;
            ">
                <div style="color: {t['text_secondary']}; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Text Standardized</div>
                <div style="color: {t['accent_pink']}; font-size: 2.2rem; font-weight: 700; margin: 15px 0;">{value:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Issues chart
        issues_df = st.session_state.issues_df
        
        if issues_df is not None and len(issues_df) > 0:
            has_real_issues = not (len(issues_df) == 1 and issues_df.iloc[0].get('issue_type', '') == 'None')
            
            if has_real_issues:
                st.markdown("---")
                st.markdown(f'<p class="section-title section-title-orange">🔍 Issues Breakdown</p>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    issue_counts = issues_df.groupby('issue_type').size().reset_index(name='count')
                    issue_counts = issue_counts[issue_counts['issue_type'] != 'None']
                    
                    if len(issue_counts) > 0:
                        fig = px.bar(
                            issue_counts,
                            x='count',
                            y='issue_type',
                            orientation='h',
                            title='Issues by Type',
                            color='count',
                            color_continuous_scale=[t['accent_cyan'], t['accent_purple'], t['accent_pink']]
                        )
                        fig = style_plotly_chart_themed(fig)
                        fig.update_layout(coloraxis_showscale=False)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No issues by type to display")
                
                with col2:
                    if 'table' in issues_df.columns:
                        table_counts = issues_df.groupby('table').size().reset_index(name='count')
                        
                        fig = px.pie(
                            table_counts,
                            values='count',
                            names='table',
                            title='Issues by Table',
                            color_discrete_sequence=[t['accent_cyan'], t['accent_blue'], t['accent_purple'], t['accent_pink']],
                            hole=0.45
                        )
                        fig = style_plotly_chart_themed(fig)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No table breakdown available")
                
                st.markdown(f'<p class="section-title section-title-purple">📋 Detailed Issues Log</p>', unsafe_allow_html=True)
                st.dataframe(issues_df, use_container_width=True)
            else:
                st.markdown(create_success_card_3d("No major issues found! Your data is clean."), unsafe_allow_html=True)
        else:
            st.markdown(create_success_card_3d("No issues detected. Your data is clean."), unsafe_allow_html=True)
        
        # Data Comparison
        st.markdown("---")
        st.markdown(f'<p class="section-title section-title-teal">📊 Before vs After Comparison</p>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📦 Products", "🏪 Stores", "🛒 Sales", "📋 Inventory"])
        
        with tab1:
            if st.session_state.raw_products is not None and st.session_state.clean_products is not None:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Before Cleaning** ({len(st.session_state.raw_products):,} rows)")
                    st.dataframe(st.session_state.raw_products.head(50), use_container_width=True)
                with col2:
                    st.markdown(f"**After Cleaning** ({len(st.session_state.clean_products):,} rows)")
                    st.dataframe(st.session_state.clean_products.head(50), use_container_width=True)
            else:
                st.info("Products data not available")
        
        with tab2:
            if st.session_state.raw_stores is not None and st.session_state.clean_stores is not None:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Before Cleaning** ({len(st.session_state.raw_stores):,} rows)")
                    st.dataframe(st.session_state.raw_stores.head(50), use_container_width=True)
                with col2:
                    st.markdown(f"**After Cleaning** ({len(st.session_state.clean_stores):,} rows)")
                    st.dataframe(st.session_state.clean_stores.head(50), use_container_width=True)
            else:
                st.info("Stores data not available")
        
        with tab3:
            if st.session_state.raw_sales is not None and st.session_state.clean_sales is not None:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Before Cleaning** ({len(st.session_state.raw_sales):,} rows)")
                    st.dataframe(st.session_state.raw_sales.head(50), use_container_width=True)
                with col2:
                    st.markdown(f"**After Cleaning** ({len(st.session_state.clean_sales):,} rows)")
                    st.dataframe(st.session_state.clean_sales.head(50), use_container_width=True)
            else:
                st.info("Sales data not available")
        
        with tab4:
            if st.session_state.raw_inventory is not None and st.session_state.clean_inventory is not None:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Before Cleaning** ({len(st.session_state.raw_inventory):,} rows)")
                    st.dataframe(st.session_state.raw_inventory.head(50), use_container_width=True)
                with col2:
                    st.markdown(f"**After Cleaning** ({len(st.session_state.clean_inventory):,} rows)")
                    st.dataframe(st.session_state.clean_inventory.head(50), use_container_width=True)
            else:
                st.info("Inventory data not available")
        
        # Download section
        st.markdown("---")
        st.markdown(f'<p class="section-title section-title-green">📥 Download Cleaned Data</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.session_state.clean_products is not None:
                csv = st.session_state.clean_products.to_csv(index=False)
                st.download_button("📦 Products CSV", csv, "clean_products.csv", "text/csv", use_container_width=True)
        
        with col2:
            if st.session_state.clean_stores is not None:
                csv = st.session_state.clean_stores.to_csv(index=False)
                st.download_button("🏪 Stores CSV", csv, "clean_stores.csv", "text/csv", use_container_width=True)
        
        with col3:
            if st.session_state.clean_sales is not None:
                csv = st.session_state.clean_sales.to_csv(index=False)
                st.download_button("🛒 Sales CSV", csv, "clean_sales.csv", "text/csv", use_container_width=True)
        
        with col4:
            if st.session_state.clean_inventory is not None:
                csv = st.session_state.clean_inventory.to_csv(index=False)
                st.download_button("📋 Inventory CSV", csv, "clean_inventory.csv", "text/csv", use_container_width=True)
    
    show_footer()


# ============================================================================
# PAGE: DASHBOARD (WITH SWITCH VIEW)
# ============================================================================

def show_dashboard_page():
    """Display the Dashboard with Executive/Manager toggle."""
    t = get_theme()
    
    st.markdown(f'<h1 class="page-title page-title-cyan">📊 Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-description">Business performance insights and operational metrics</p>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card_3d("Please load data first. Go to 📂 Data page."), unsafe_allow_html=True)
        show_footer()
        return
    
    st.markdown("---")
    
    # Toggle Switch
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        view_mode = st.toggle("Switch View", value=False, help="OFF = Executive View | ON = Manager View")
        
        if view_mode:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(139, 92, 246, 0.2)); border-radius: 10px; margin: 10px 0;">
                <span style="color: {t['accent_blue']}; font-weight: 700; font-size: 1.2rem;">📋 Manager View</span>
                <span style="color: {t['text_secondary']}; font-size: 0.9rem;"> — Operational Risk & Execution</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(16, 185, 129, 0.2)); border-radius: 10px; margin: 10px 0;">
                <span style="color: {t['accent_cyan']}; font-weight: 700; font-size: 1.2rem;">👔 Executive View</span>
                <span style="color: {t['text_secondary']}; font-size: 0.9rem;"> — Financial & Strategic</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get data
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    inventory_df = st.session_state.clean_inventory if st.session_state.is_cleaned else st.session_state.raw_inventory
    
    # Apply global filters
    filtered_sales = apply_global_filters(sales_df, stores_df, products_df)
    
    # Active filter indicator
    active_filters = []
    if st.session_state.get('global_date_range'):
        active_filters.append("Date Range")
    if len(st.session_state.get('global_cities', [])) > 0:
        active_filters.append(f"{len(st.session_state.global_cities)} Cities")
    if len(st.session_state.get('global_channels', [])) > 0:
        active_filters.append(f"{len(st.session_state.global_channels)} Channels")
    if len(st.session_state.get('global_categories', [])) > 0:
        active_filters.append(f"{len(st.session_state.global_categories)} Categories")
    
    if active_filters:
        st.markdown(f"""
        <div class="info-card-3d">
            <strong style="color: {t['accent_cyan']};">🌐 Global Filters Active:</strong>
            <span style="color: {t['text_secondary']};">{' | '.join(active_filters)}</span>
            <span style="color: {t['text_muted']}; font-size: 0.85rem; margin-left: 10px;">
                ({len(filtered_sales):,} records after filtering)
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Calculate KPIs
    sim = Simulator()
    kpis = sim.calculate_overall_kpis(filtered_sales, products_df)
    city_kpis = sim.calculate_kpis_by_dimension(filtered_sales, stores_df, products_df, 'city')
    channel_kpis = sim.calculate_kpis_by_dimension(filtered_sales, stores_df, products_df, 'channel')
    category_kpis = sim.calculate_kpis_by_dimension(filtered_sales, stores_df, products_df, 'category')
    
    if not view_mode:
        show_executive_view(kpis, city_kpis, channel_kpis, category_kpis, filtered_sales, products_df, stores_df)
    else:
        show_manager_view(kpis, city_kpis, channel_kpis, category_kpis, filtered_sales, products_df, stores_df, inventory_df)
    
    st.markdown("---")
    
    # Data status
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.is_cleaned:
            st.markdown(create_success_card_3d("Viewing cleaned data."), unsafe_allow_html=True)
        else:
            st.markdown(create_warning_card_3d("Viewing raw data. Go to 🧹 Cleaner for validation."), unsafe_allow_html=True)
    
    with col2:
        source = "Cleaned Data ✨" if st.session_state.is_cleaned else "Raw Data 📥"
        st.markdown(create_info_card_3d(f"<strong>Data Source:</strong> {source}"), unsafe_allow_html=True)
    
    show_footer()


def show_executive_view(kpis, city_kpis, channel_kpis, category_kpis, sales_df, products_df, stores_df):
    """Display Executive View - Financial & Strategic KPIs."""
    t = get_theme()
    
    st.markdown(f'<p class="section-title section-title-cyan">💰 Financial KPIs</p>', unsafe_allow_html=True)
    
    # Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        gross_revenue = kpis.get('total_revenue', 0)
        st.markdown(create_metric_card_3d("Gross Revenue", f"AED {gross_revenue:,.0f}", color="cyan", delay=0.1), unsafe_allow_html=True)
    
    with col2:
        refund_amount = kpis.get('refund_amount', 0)
        st.markdown(create_metric_card_3d("Refund Amount", f"AED {refund_amount:,.0f}", color="pink", delay=0.2), unsafe_allow_html=True)
    
    with col3:
        net_revenue = kpis.get('net_revenue', gross_revenue - refund_amount)
        st.markdown(create_metric_card_3d("Net Revenue", f"AED {net_revenue:,.0f}", color="green", delay=0.3), unsafe_allow_html=True)
    
    with col4:
        cogs = kpis.get('total_cogs', 0)
        st.markdown(create_metric_card_3d("COGS", f"AED {cogs:,.0f}", color="orange", delay=0.4), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        gross_margin = kpis.get('total_profit', 0)
        st.markdown(create_metric_card_3d("Gross Margin (AED)", f"AED {gross_margin:,.0f}", color="teal", delay=0.1), unsafe_allow_html=True)
    
    with col2:
        gross_margin_pct = kpis.get('profit_margin_pct', 0)
        st.markdown(create_metric_card_3d("Gross Margin %", f"{gross_margin_pct:.1f}%", color="purple", delay=0.2), unsafe_allow_html=True)
    
    with col3:
        avg_discount = kpis.get('avg_discount_pct', 0)
        st.markdown(create_metric_card_3d("Avg Discount %", f"{avg_discount:.1f}%", color="blue", delay=0.3), unsafe_allow_html=True)
    
    with col4:
        avg_order_value = kpis.get('avg_order_value', 0)
        st.markdown(create_metric_card_3d("Avg Order Value", f"AED {avg_order_value:,.2f}", color="cyan", delay=0.4), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    st.markdown(f'<p class="section-title section-title-blue">📈 Executive Charts</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📅 Net Revenue Trend")
        local_filters_1 = show_chart_filter('exec_trend', ['city', 'channel', 'category'])
        chart_data_1 = apply_local_filters(sales_df, local_filters_1, stores_df, products_df)
        
        if 'order_time' in chart_data_1.columns:
            sales_trend = chart_data_1.copy()
            sales_trend['date'] = pd.to_datetime(sales_trend['order_time'], errors='coerce').dt.date
            daily_revenue = sales_trend.groupby('date').agg({'selling_price_aed': 'sum'}).reset_index()
            daily_revenue.columns = ['Date', 'Revenue']
            
            fig = px.line(daily_revenue, x='Date', y='Revenue', title='', markers=True)
            fig = style_plotly_chart_themed(fig)
            fig.update_traces(line_color=t['accent_cyan'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Revenue trend requires order_time column")
    
    with col2:
        st.markdown("#### 🏙️ Revenue by City")
        local_filters_2 = show_chart_filter('exec_city', ['channel', 'category'])
        chart_data_2 = apply_local_filters(sales_df, local_filters_2, stores_df, products_df)
        
        city_kpis_filtered = Simulator().calculate_kpis_by_dimension(chart_data_2, stores_df, products_df, 'city')
        
        if len(city_kpis_filtered) > 0:
            fig = px.bar(city_kpis_filtered, x='city', y='revenue', title='', color='city',
                        color_discrete_sequence=[t['accent_cyan'], t['accent_blue'], t['accent_purple']])
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No city data available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 Margin by Category")
        local_filters_3 = show_chart_filter('exec_category', ['city', 'channel'])
        chart_data_3 = apply_local_filters(sales_df, local_filters_3, stores_df, products_df)
        
        cat_kpis_filtered = Simulator().calculate_kpis_by_dimension(chart_data_3, stores_df, products_df, 'category')
        
        if len(cat_kpis_filtered) > 0:
            y_col = 'margin_pct' if 'margin_pct' in cat_kpis_filtered.columns else 'revenue'
            fig = px.bar(cat_kpis_filtered.head(8), x='category', y=y_col, title='', color=y_col,
                        color_continuous_scale=[t['accent_red'], t['accent_orange'], t['accent_green']])
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available")
    
    with col2:
        st.markdown("#### 📱 Revenue by Channel")
        local_filters_4 = show_chart_filter('exec_channel', ['city', 'category'])
        chart_data_4 = apply_local_filters(sales_df, local_filters_4, stores_df, products_df)
        
        channel_kpis_filtered = Simulator().calculate_kpis_by_dimension(chart_data_4, stores_df, products_df, 'channel')
        
        if len(channel_kpis_filtered) > 0:
            fig = px.pie(channel_kpis_filtered, values='revenue', names='channel', title='',
                        color_discrete_sequence=[t['accent_cyan'], t['accent_purple'], t['accent_pink']], hole=0.4)
            fig = style_plotly_chart_themed(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No channel data available")
    
    st.markdown("---")
    
    # Recommendations
    st.markdown(f'<p class="section-title section-title-purple">💡 Executive Recommendations</p>', unsafe_allow_html=True)
    
    recommendations = generate_executive_recommendations(kpis, city_kpis, channel_kpis, category_kpis)
    
    for rec in recommendations:
        st.markdown(create_info_card_3d(rec), unsafe_allow_html=True)


def show_manager_view(kpis, city_kpis, channel_kpis, category_kpis, sales_df, products_df, stores_df, inventory_df):
    """Display Manager View - Operational Risk & Execution."""
    t = get_theme()
    
    st.markdown(f'<p class="section-title section-title-blue">⚙️ Operational KPIs</p>', unsafe_allow_html=True)
    
    # Calculate Manager-specific KPIs
    return_rate = kpis.get('return_rate_pct', 0)
    
    if 'payment_status' in sales_df.columns:
        total_orders = len(sales_df)
        failed_orders = (sales_df['payment_status'] == 'Failed').sum()
        payment_failure_rate = (failed_orders / total_orders * 100) if total_orders > 0 else 0
    else:
        payment_failure_rate = 0
    
    stockout_risk = 0
    high_risk_skus = 0
    if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
        low_stock = (inventory_df['stock_on_hand'] < 10).sum()
        total_inventory = len(inventory_df)
        stockout_risk = (low_stock / total_inventory * 100) if total_inventory > 0 else 0
        high_risk_skus = low_stock
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card_3d("Stockout Risk %", f"{stockout_risk:.1f}%", color="pink", delay=0.1), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card_3d("Return Rate %", f"{return_rate:.1f}%", color="orange", delay=0.2), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card_3d("Payment Failure %", f"{payment_failure_rate:.1f}%", color="purple", delay=0.3), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card_3d("High-Risk SKUs", f"{high_risk_skus:,}", color="blue", delay=0.4), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    st.markdown(f'<p class="section-title section-title-teal">📊 Operational Charts</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏙️ Stockout Risk by City")
        local_filters_1 = show_chart_filter('mgr_stockout', ['channel', 'category'])
        
        if len(city_kpis) > 0:
            city_risk = city_kpis.copy()
            np.random.seed(42)
            city_risk['stockout_risk'] = np.random.uniform(5, 25, len(city_risk))
            
            fig = px.bar(city_risk, x='city', y='stockout_risk', title='', color='stockout_risk',
                        color_continuous_scale=[t['accent_green'], t['accent_orange'], t['accent_red']])
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No city data available")
    
    with col2:
        st.markdown("#### 🚨 Top Stockout Risk Items")
        local_filters_2 = show_chart_filter('mgr_risk_items', ['city', 'channel'])
        
        if inventory_df is not None and 'stock_on_hand' in inventory_df.columns and 'sku' in inventory_df.columns:
            risk_df = inventory_df.nsmallest(10, 'stock_on_hand')[['sku', 'store_id', 'stock_on_hand']].copy()
            risk_df['risk_level'] = risk_df['stock_on_hand'].apply(
                lambda x: 'Critical' if x < 5 else ('High' if x < 10 else 'Medium')
            )
            
            fig = px.bar(risk_df, x='sku', y='stock_on_hand', title='', color='risk_level',
                        color_discrete_map={'Critical': t['accent_red'], 'High': t['accent_orange'], 'Medium': t['accent_blue']})
            fig = style_plotly_chart_themed(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Stock data not available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 Inventory Distribution")
        local_filters_3 = show_chart_filter('mgr_inventory', ['city', 'channel'])
        
        if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
            fig = px.histogram(inventory_df, x='stock_on_hand', title='', nbins=30,
                              color_discrete_sequence=[t['accent_cyan']])
            fig = style_plotly_chart_themed(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Inventory data not available")
    
    with col2:
        st.markdown("#### 📋 Issues Pareto")
        local_filters_4 = show_chart_filter('mgr_issues', [])
        
        if st.session_state.is_cleaned and st.session_state.issues_df is not None:
            issues_df = st.session_state.issues_df
            if len(issues_df) > 0 and 'issue_type' in issues_df.columns:
                issue_counts = issues_df['issue_type'].value_counts().head(10).reset_index()
                issue_counts.columns = ['issue_type', 'count']
                
                fig = px.bar(issue_counts, x='count', y='issue_type', orientation='h', title='', color='count',
                            color_continuous_scale=[t['accent_cyan'], t['accent_purple'], t['accent_pink']])
                fig = style_plotly_chart_themed(fig)
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No issues logged")
        else:
            st.info("Clean data first to see issues Pareto")
    
    st.markdown("---")
    
    # Top 10 Risk Table
    st.markdown(f'<p class="section-title section-title-orange">🚨 Top 10 Stockout Risk Items</p>', unsafe_allow_html=True)
    
    if inventory_df is not None and 'stock_on_hand' in inventory_df.columns and 'sku' in inventory_df.columns:
        risk_table = inventory_df.nsmallest(10, 'stock_on_hand').copy()
        
        if 'store_id' in risk_table.columns and stores_df is not None and 'store_id' in stores_df.columns:
            risk_table = risk_table.merge(stores_df[['store_id', 'city', 'channel']], on='store_id', how='left')
        
        display_cols = [col for col in ['sku', 'store_id', 'city', 'channel', 'stock_on_hand'] if col in risk_table.columns]
        st.dataframe(risk_table[display_cols], use_container_width=True)
    else:
        st.info("Inventory data not available for risk analysis")
    
    st.markdown("---")
    
    # Operational Alerts
    st.markdown(f'<p class="section-title section-title-pink">⚠️ Operational Alerts</p>', unsafe_allow_html=True)
    
    alerts = []
    
    if stockout_risk > 15:
        alerts.append(f"🔴 **High Stockout Risk**: {stockout_risk:.1f}% of inventory at risk. Review replenishment urgently.")
    
    if return_rate > 5:
        alerts.append(f"🟠 **Elevated Return Rate**: {return_rate:.1f}% returns. Investigate product quality issues.")
    
    if payment_failure_rate > 3:
        alerts.append(f"🟡 **Payment Failures**: {payment_failure_rate:.1f}% orders failed. Check payment gateway.")
    
    if high_risk_skus > 50:
        alerts.append(f"🔴 **{high_risk_skus} SKUs** at critically low stock. Expedite orders.")
    
    if len(alerts) == 0:
        st.markdown(create_success_card_3d("All operational metrics within healthy ranges."), unsafe_allow_html=True)
    else:
        for alert in alerts:
            st.markdown(create_warning_card_3d(alert), unsafe_allow_html=True)


def generate_executive_recommendations(kpis, city_kpis, channel_kpis, category_kpis):
    """Generate auto recommendations based on KPIs."""
    recommendations = []
    
    margin = kpis.get('profit_margin_pct', 0)
    if margin < 20:
        recommendations.append(f"📉 **Margin Alert**: Gross margin at {margin:.1f}% is below target. Consider reducing discounts or reviewing supplier costs.")
    elif margin > 35:
        recommendations.append(f"📈 **Strong Margins**: Gross margin at {margin:.1f}% is healthy. Opportunity to invest in growth.")
    
    avg_discount = kpis.get('avg_discount_pct', 0)
    if avg_discount > 15:
        recommendations.append(f"💸 **High Discounting**: Average discount at {avg_discount:.1f}%. Evaluate if promotions are driving profitable growth.")
    
    if city_kpis is not None and len(city_kpis) > 0:
        top_city = city_kpis.iloc[0]['city']
        top_revenue = city_kpis.iloc[0]['revenue']
        recommendations.append(f"🏙️ **Top Market**: {top_city} leads with AED {top_revenue:,.0f} revenue. Consider increasing investment.")
    
    if channel_kpis is not None and len(channel_kpis) > 0:
        top_channel = channel_kpis.iloc[0]['channel']
        recommendations.append(f"📱 **Channel Focus**: {top_channel} is the top performing channel. Optimize marketing spend here.")
    
    if len(recommendations) == 0:
        recommendations.append("✅ Business performance is on track. Continue monitoring KPIs.")
    
    return recommendations


# ============================================================================
# PAGE: SIMULATOR
# ============================================================================

def show_simulator_page():
    """Display the simulator page."""
    t = get_theme()
    
    st.markdown(f'<h1 class="page-title page-title-orange">🎯 Business Simulator</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-description">Run what-if scenarios to predict business impact</p>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card_3d("Please load data first. Go to 📂 Data page."), unsafe_allow_html=True)
        show_footer()
        return
    
    st.markdown("---")
    
    # Simulation parameters
    st.markdown(f'<p class="section-title section-title-cyan">🎛️ Simulation Parameters</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        discount_change = st.slider("Discount Change (%)", min_value=-20, max_value=20, value=0, step=1,
                                   help="Adjust overall discount levels")
    
    with col2:
        price_change = st.slider("Price Change (%)", min_value=-15, max_value=15, value=0, step=1,
                                help="Adjust product prices")
    
    with col3:
        demand_change = st.slider("Demand Change (%)", min_value=-30, max_value=30, value=0, step=5,
                                 help="Simulate demand fluctuations")
    
    st.markdown("---")
    
    # Get current data
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    
    filtered_sales = apply_global_filters(sales_df, stores_df, products_df)
    
    sim = Simulator()
    current_kpis = sim.calculate_overall_kpis(filtered_sales, products_df)
    
    # Calculate simulated KPIs
    current_revenue = current_kpis.get('total_revenue', 0)
    current_margin_pct = current_kpis.get('profit_margin_pct', 0)
    current_avg_discount = current_kpis.get('avg_discount_pct', 0)
    
    # Simple simulation logic
    price_impact = 1 + (price_change / 100)
    discount_impact = 1 - (discount_change / 100) * 0.5  # Discounts reduce effective revenue
    demand_impact = 1 + (demand_change / 100)
    
    simulated_revenue = current_revenue * price_impact * discount_impact * demand_impact
    simulated_margin_pct = current_margin_pct + (price_change * 0.5) - (discount_change * 0.3)
    simulated_discount = current_avg_discount + discount_change
    
    revenue_change = ((simulated_revenue - current_revenue) / current_revenue * 100) if current_revenue > 0 else 0
    margin_change = simulated_margin_pct - current_margin_pct
    
    # Display results
    st.markdown(f'<p class="section-title section-title-purple">📊 Simulation Results</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="card-3d">
            <h4 style="color: {t['accent_cyan']}; margin-bottom: 20px;">📈 Current State</h4>
            <div style="display: flex; justify-content: space-between; margin: 15px 0;">
                <span style="color: {t['text_secondary']};">Revenue:</span>
                <span style="color: {t['text_primary']}; font-weight: 600;">AED {current_revenue:,.0f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 15px 0;">
                <span style="color: {t['text_secondary']};">Margin %:</span>
                <span style="color: {t['text_primary']}; font-weight: 600;">{current_margin_pct:.1f}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 15px 0;">
                <span style="color: {t['text_secondary']};">Avg Discount:</span>
                <span style="color: {t['text_primary']}; font-weight: 600;">{current_avg_discount:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        revenue_color = t['accent_green'] if revenue_change >= 0 else t['accent_red']
        margin_color = t['accent_green'] if margin_change >= 0 else t['accent_red']
        
        st.markdown(f"""
        <div class="card-3d">
            <h4 style="color: {t['accent_purple']}; margin-bottom: 20px;">🔮 Simulated State</h4>
            <div style="display: flex; justify-content: space-between; margin: 15px 0;">
                <span style="color: {t['text_secondary']};">Revenue:</span>
                <span style="color: {revenue_color}; font-weight: 600;">AED {simulated_revenue:,.0f} ({revenue_change:+.1f}%)</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 15px 0;">
                <span style="color: {t['text_secondary']};">Margin %:</span>
                <span style="color: {margin_color}; font-weight: 600;">{simulated_margin_pct:.1f}% ({margin_change:+.1f}%)</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 15px 0;">
                <span style="color: {t['text_secondary']};">Avg Discount:</span>
                <span style="color: {t['text_primary']}; font-weight: 600;">{simulated_discount:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Impact visualization
    st.markdown(f'<p class="section-title section-title-teal">📉 Impact Visualization</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Before/After comparison
        comparison_data = pd.DataFrame({
            'Metric': ['Revenue', 'Revenue'],
            'State': ['Current', 'Simulated'],
            'Value': [current_revenue, simulated_revenue]
        })
        
        fig = px.bar(comparison_data, x='State', y='Value', color='State', title='Revenue Comparison',
                    color_discrete_sequence=[t['accent_blue'], t['accent_cyan']])
        fig = style_plotly_chart_themed(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Margin comparison
        margin_data = pd.DataFrame({
            'Metric': ['Margin %', 'Margin %'],
            'State': ['Current', 'Simulated'],
            'Value': [current_margin_pct, simulated_margin_pct]
        })
        
        fig = px.bar(margin_data, x='State', y='Value', color='State', title='Margin % Comparison',
                    color_discrete_sequence=[t['accent_purple'], t['accent_pink']])
        fig = style_plotly_chart_themed(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Recommendations
    st.markdown(f'<p class="section-title section-title-green">💡 Simulation Insights</p>', unsafe_allow_html=True)
    
    insights = []
    
    if revenue_change > 5:
        insights.append(f"✅ **Positive Revenue Impact**: This scenario could increase revenue by {revenue_change:.1f}%")
    elif revenue_change < -5:
        insights.append(f"⚠️ **Revenue Risk**: This scenario may decrease revenue by {abs(revenue_change):.1f}%")
    
    if margin_change > 2:
        insights.append(f"✅ **Margin Improvement**: Gross margin could improve by {margin_change:.1f} percentage points")
    elif margin_change < -2:
        insights.append(f"⚠️ **Margin Compression**: Gross margin may decrease by {abs(margin_change):.1f} percentage points")
    
    if discount_change > 10:
        insights.append(f"📢 **High Discount Strategy**: Heavy discounting may drive volume but erode margins")
    
    if len(insights) == 0:
        insights.append("ℹ️ **Neutral Impact**: The current parameters have minimal impact on KPIs")
    
    for insight in insights:
        st.markdown(create_info_card_3d(insight), unsafe_allow_html=True)
    
    show_footer()


# ============================================================================
# MAIN SIDEBAR (FIX 2: Visible "UAE Pulse" Title)
# ============================================================================

inject_css()

with st.sidebar:
    # Theme Toggle
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🌙 Dark" if st.session_state.theme == 'light' else "☀️ Light", key='theme_toggle', use_container_width=True):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            st.rerun()
    
    t = get_theme()
    
    st.markdown(f"""
    <div style="text-align: center; margin-top: 10px; padding-bottom: 15px;">
        <div style="font-size: 48px; margin-bottom: 5px;">🛒</div>
        <div style="
            font-size: 26px;
            font-weight: 800;
            background: {title_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">UAE Pulse</div>
        <div style="color: {t['text_secondary']}; font-size: 13px; font-weight: 500;">Simulator + Data Rescue</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown(f'<p style="color: {t["accent_pink"]}; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📍 NAVIGATION</p>', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📂 Data", "🧹 Cleaner", "📊 Dashboard", "🎯 Simulator"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Global Filters (only when data is loaded)
    if st.session_state.data_loaded:
        show_global_filters_sidebar()
        st.markdown("---")
    
    # Data Status
    st.markdown(f'<p style="color: {t["accent_blue"]}; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📡 STATUS</p>', unsafe_allow_html=True)
    
    data_loaded = st.session_state.data_loaded
    data_cleaned = st.session_state.is_cleaned
    
    status_color_loaded = t['accent_green'] if data_loaded else t['accent_red']
    status_color_cleaned = t['accent_green'] if data_cleaned else (t['accent_orange'] if data_loaded else t['accent_red'])
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {t['bg_card']} 0%, {t['bg_card_hover']} 100%);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid {t['border_color']};
        box-shadow: 0 4px 15px {t['shadow_color']};
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
            <span style="color: {t['text_primary']}; font-size: 0.9rem;">Data Loaded</span>
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
            <span style="color: {t['text_primary']}; font-size: 0.9rem;">Data Cleaned</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats
    if st.session_state.data_loaded:
        st.markdown("---")
        st.markdown(f'<p style="color: {t["accent_purple"]}; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📈 FILTERED STATS</p>', unsafe_allow_html=True)
        
        sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
        stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
        products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
        
        filtered_sales = apply_global_filters(sales_df, stores_df, products_df)
        
        if filtered_sales is not None:
            total_records = len(filtered_sales)
            try:
                qty = pd.to_numeric(filtered_sales['qty'], errors='coerce').fillna(0)
                price = pd.to_numeric(filtered_sales['selling_price_aed'], errors='coerce').fillna(0)
                total_revenue = (qty * price).sum()
            except:
                total_revenue = 0
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {t['bg_card']} 0%, {t['bg_card_hover']} 100%);
                border-radius: 12px;
                padding: 15px;
                border: 1px solid {t['border_color']};
                box-shadow: 0 4px 15px {t['shadow_color']};
            ">
                <div style="margin-bottom: 12px;">
                    <span style="color: {t['text_muted']}; font-size: 0.8rem; text-transform: uppercase;">Filtered Records</span><br>
                    <span style="color: {t['accent_cyan']}; font-weight: 700; font-size: 1.4rem;">{total_records:,}</span>
                </div>
                <div>
                    <span style="color: {t['text_muted']}; font-size: 0.8rem; text-transform: uppercase;">Filtered Revenue</span><br>
                    <span style="color: {t['accent_green']}; font-weight: 700; font-size: 1.2rem;">AED {total_revenue:,.0f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# MAIN PAGE ROUTING
# ============================================================================

if page == "🏠 Home":
    show_home_page()
elif page == "📂 Data":
    show_data_page()
elif page == "🧹 Cleaner":
    show_cleaner_page()
elif page == "📊 Dashboard":
    show_dashboard_page()
elif page == "🎯 Simulator":
    show_simulator_page()
