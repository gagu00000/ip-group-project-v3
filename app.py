# ============================================================================
# UAE PULSE - RETAIL SIMULATOR + DATA RESCUE CENTER
# Complete Application with All Project Requirements
# Version 2.1 - Fixed
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
# THEME DEFINITIONS
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
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'theme': 'dark',
        'data_loaded': False,
        'is_cleaned': False,
        'raw_products': None,
        'raw_stores': None,
        'raw_sales': None,
        'raw_inventory': None,
        'clean_products': None,
        'clean_stores': None,
        'clean_sales': None,
        'clean_inventory': None,
        'issues_df': None,
        'cleaner_stats': {},
        # Global filters - Multi-select
        'global_date_range': None,
        'global_cities': [],
        'global_channels': [],
        'global_categories': [],
        'global_brands': [],  # NEW: 5th filter
        'global_fulfillment': [],  # NEW: 6th filter option
        # Simulation state
        'last_simulation': None,
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

init_session_state()

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


def format_currency(value):
    """Format value as AED currency."""
    if value >= 1_000_000:
        return f"AED {value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"AED {value/1_000:.1f}K"
    else:
        return f"AED {value:,.0f}"


# ============================================================================
# FILTER FUNCTIONS (WITH 5TH FILTER - BRAND)
# ============================================================================

def show_global_filters_sidebar():
    """Display global filters in sidebar with MULTI-SELECT support including Brand."""
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
    
    # =========================================================================
    # NEW: 5th FILTER - BRAND
    # =========================================================================
    brands = []
    if products_df is not None and 'brand' in products_df.columns:
        brands = sorted(products_df['brand'].dropna().unique().tolist())
    
    selected_brands = st.multiselect(
        "🏷️ Brands",
        options=brands,
        default=st.session_state.get('global_brands', []),
        key='global_brand_filter',
        placeholder="All Brands"
    )
    st.session_state.global_brands = selected_brands
    
    # =========================================================================
    # OPTIONAL 6th FILTER - FULFILLMENT TYPE
    # =========================================================================
    fulfillment_types = []
    if stores_df is not None and 'fulfillment_type' in stores_df.columns:
        fulfillment_types = sorted(stores_df['fulfillment_type'].dropna().unique().tolist())
    
    if len(fulfillment_types) > 0:
        selected_fulfillment = st.multiselect(
            "🚚 Fulfillment",
            options=fulfillment_types,
            default=st.session_state.get('global_fulfillment', []),
            key='global_fulfillment_filter',
            placeholder="All Types"
        )
        st.session_state.global_fulfillment = selected_fulfillment
    
    # Reset filters button
    if st.button("🔄 Reset All Filters", key='reset_global_filters', use_container_width=True):
        st.session_state.global_date_range = None
        st.session_state.global_cities = []
        st.session_state.global_channels = []
        st.session_state.global_categories = []
        st.session_state.global_brands = []
        st.session_state.global_fulfillment = []
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
    if len(st.session_state.get('global_brands', [])) > 0:
        active_filters.append(f"🏷️ {len(st.session_state.global_brands)} brands")
    if len(st.session_state.get('global_fulfillment', [])) > 0:
        active_filters.append(f"🚚 {len(st.session_state.global_fulfillment)} fulfillment")
    
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
    """Apply global filters to a dataframe - supports MULTI-SELECT including Brand."""
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
        if 'category' in products_df.columns:
            sku_col = 'sku' if 'sku' in filtered_df.columns else 'product_id'
            prod_sku_col = 'sku' if 'sku' in products_df.columns else 'product_id'
            if sku_col in filtered_df.columns and prod_sku_col in products_df.columns:
                category_skus = products_df[products_df['category'].isin(selected_categories)][prod_sku_col].tolist()
                filtered_df = filtered_df[filtered_df[sku_col].isin(category_skus)]
    
    # Apply brand filter (MULTI-SELECT) - NEW!
    selected_brands = st.session_state.get('global_brands', [])
    if len(selected_brands) > 0 and products_df is not None:
        if 'brand' in products_df.columns:
            sku_col = 'sku' if 'sku' in filtered_df.columns else 'product_id'
            prod_sku_col = 'sku' if 'sku' in products_df.columns else 'product_id'
            if sku_col in filtered_df.columns and prod_sku_col in products_df.columns:
                brand_skus = products_df[products_df['brand'].isin(selected_brands)][prod_sku_col].tolist()
                filtered_df = filtered_df[filtered_df[sku_col].isin(brand_skus)]
    
    # Apply fulfillment filter (MULTI-SELECT)
    selected_fulfillment = st.session_state.get('global_fulfillment', [])
    if len(selected_fulfillment) > 0 and stores_df is not None:
        if 'fulfillment_type' in stores_df.columns and 'store_id' in filtered_df.columns:
            fulfillment_stores = stores_df[stores_df['fulfillment_type'].isin(selected_fulfillment)]['store_id'].tolist()
            filtered_df = filtered_df[filtered_df['store_id'].isin(fulfillment_stores)]
    
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
        
        cols = st.columns(min(num_filters, 4))
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
        
        if 'brand' in available_filters and products_df is not None and 'brand' in products_df.columns:
            with cols[col_idx % len(cols)]:
                brands = sorted(products_df['brand'].dropna().unique().tolist())
                local_filters['brands'] = st.multiselect(
                    "🏷️ Brands",
                    options=brands,
                    key=f'{chart_id}_brand',
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
        if 'category' in products_df.columns:
            sku_col = 'sku' if 'sku' in filtered_df.columns else 'product_id'
            prod_sku_col = 'sku' if 'sku' in products_df.columns else 'product_id'
            if sku_col in filtered_df.columns and prod_sku_col in products_df.columns:
                category_skus = products_df[products_df['category'].isin(selected_categories)][prod_sku_col].tolist()
                filtered_df = filtered_df[filtered_df[sku_col].isin(category_skus)]
    
    # Apply brand filter (MULTI-SELECT)
    selected_brands = local_filters.get('brands', [])
    if len(selected_brands) > 0 and products_df is not None:
        if 'brand' in products_df.columns:
            sku_col = 'sku' if 'sku' in filtered_df.columns else 'product_id'
            prod_sku_col = 'sku' if 'sku' in products_df.columns else 'product_id'
            if sku_col in filtered_df.columns and prod_sku_col in products_df.columns:
                brand_skus = products_df[products_df['brand'].isin(selected_brands)][prod_sku_col].tolist()
                filtered_df = filtered_df[filtered_df[sku_col].isin(brand_skus)]
    
    return filtered_df


# ============================================================================
# DATA CLEANER MODULE
# ============================================================================

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
            'invalid_timestamps_fixed': 0,
            'total_issues': 0
        }
        self.issues_log: List[Dict[str, Any]] = []
    
    def log_issue(self, table: str, column: str, issue_type: str, 
                  row_index: Any = None, original_value: Any = None, 
                  fixed_value: Any = None, action_taken: str = "", description: str = ""):
        """Log an issue found during cleaning."""
        self.issues_log.append({
            'table': table,
            'column': column,
            'issue_type': issue_type,
            'row_index': row_index,
            'original_value': str(original_value)[:100] if original_value is not None else None,
            'fixed_value': str(fixed_value)[:100] if fixed_value is not None else None,
            'action_taken': action_taken if action_taken else 'Fixed',
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
                'action_taken': ['None'],
                'description': ['No issues found']
            })
        return pd.DataFrame(self.issues_log)
    
    def fix_missing_values(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Fix missing values based on column type."""
        if df is None or len(df) == 0:
            return df
        
        df = df.copy()
        
        for col in df.columns:
            missing_count = df[col].isna().sum()
            
            if missing_count > 0:
                if df[col].dtype in ['float64', 'int64']:
                    median_val = df[col].median()
                    if pd.isna(median_val):
                        median_val = 0
                    df[col] = df[col].fillna(median_val)
                    self.log_issue(table_name, col, 'missing_value', 
                                  action_taken='Imputed with median',
                                  description=f"Filled {missing_count} missing values with median: {median_val:.2f}")
                elif df[col].dtype == 'object':
                    mode_val = df[col].mode()
                    fill_val = mode_val.iloc[0] if len(mode_val) > 0 else 'Unknown'
                    df[col] = df[col].fillna(fill_val)
                    self.log_issue(table_name, col, 'missing_value',
                                  action_taken='Imputed with mode',
                                  description=f"Filled {missing_count} missing values with: {fill_val}")
                else:
                    df[col] = df[col].ffill().bfill()
                    self.log_issue(table_name, col, 'missing_value',
                                  action_taken='Forward/backward fill',
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
            valid_subset = [col for col in subset if col in df.columns]
            if valid_subset:
                df = df.drop_duplicates(subset=valid_subset, keep='first')
        else:
            df = df.drop_duplicates(keep='first')
        
        duplicates_removed = initial_count - len(df)
        
        if duplicates_removed > 0:
            self.log_issue(table_name, 'all', 'duplicate',
                          action_taken='Dropped duplicates',
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
            
            outliers_low = (df[col] < lower_bound).sum()
            outliers_high = (df[col] > upper_bound).sum()
            total_outliers = outliers_low + outliers_high
            
            if total_outliers > 0:
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                self.log_issue(table_name, col, 'outlier',
                              action_taken='Capped at IQR bounds',
                              description=f"Capped {total_outliers} outliers (low: {outliers_low}, high: {outliers_high})")
                self.stats['outliers_fixed'] += total_outliers
        
        return df
    
    def standardize_text(self, df: pd.DataFrame, table_name: str,
                        columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Standardize text columns - trim whitespace, title case for names."""
        if df is None or len(df) == 0:
            return df
        
        df = df.copy()
        
        if columns:
            text_cols = [col for col in columns if col in df.columns and df[col].dtype == 'object']
        else:
            text_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        for col in text_cols:
            original = df[col].copy()
            
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
            
            name_indicators = ['name', 'city', 'category', 'channel', 'brand']
            if any(indicator in col.lower() for indicator in name_indicators):
                df[col] = df[col].str.title()
            
            df[col] = df[col].replace(['nan', 'None', 'NaN', 'none', 'NULL', 'null'], 'Unknown')
            
            changes = (original.astype(str) != df[col]).sum()
            
            if changes > 0:
                self.log_issue(table_name, col, 'text_standardization',
                              action_taken='Standardized text',
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
                    df[col] = df[col].abs()
                    self.log_issue(table_name, col, 'negative_value',
                                  action_taken='Converted to absolute',
                                  description=f"Converted {negative_count} negative values to positive")
                    self.stats['negative_values_fixed'] += negative_count
        
        return df
    
    def fix_timestamps(self, df: pd.DataFrame, table_name: str, 
                      column: str = 'order_time') -> pd.DataFrame:
        """Fix invalid timestamps."""
        if df is None or len(df) == 0 or column not in df.columns:
            return df
        
        df = df.copy()
        
        original = df[column].copy()
        df[column] = pd.to_datetime(df[column], errors='coerce')
        
        invalid_count = df[column].isna().sum() - original.isna().sum()
        
        if invalid_count > 0:
            median_date = df[column].dropna().median()
            df[column] = df[column].fillna(median_date)
            
            self.log_issue(table_name, column, 'invalid_timestamp',
                          action_taken='Parsed and imputed',
                          description=f"Fixed {invalid_count} invalid timestamps")
            self.stats['invalid_timestamps_fixed'] += invalid_count
        
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
            self.log_issue(table_name, fk_column, 'fk_violation',
                          action_taken='Flagged invalid references',
                          description=f"Found {invalid_count} invalid foreign key references")
            self.stats['fk_violations_fixed'] += invalid_count
        
        return df
    
    def clean_products(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean products table."""
        if df is None:
            return None
        
        table_name = 'products'
        
        sku_col = 'sku' if 'sku' in df.columns else 'product_id'
        if sku_col in df.columns:
            df = self.remove_duplicates(df, table_name, subset=[sku_col])
        else:
            df = self.remove_duplicates(df, table_name)
        
        df = self.fix_missing_values(df, table_name)
        df = self.standardize_text(df, table_name)
        
        price_cols = [col for col in df.columns if 'price' in col.lower() or 'cost' in col.lower()]
        df = self.fix_negative_values(df, table_name, columns=price_cols)
        df = self.fix_outliers_iqr(df, table_name, columns=price_cols)
        
        return df
    
    def clean_stores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean stores table."""
        if df is None:
            return None
        
        table_name = 'stores'
        
        if 'store_id' in df.columns:
            df = self.remove_duplicates(df, table_name, subset=['store_id'])
        else:
            df = self.remove_duplicates(df, table_name)
        
        df = self.fix_missing_values(df, table_name)
        df = self.standardize_text(df, table_name)
        
        return df
    
    def clean_sales(self, df: pd.DataFrame, products_df: pd.DataFrame = None, 
                   stores_df: pd.DataFrame = None) -> pd.DataFrame:
        """Clean sales table."""
        if df is None:
            return None
        
        table_name = 'sales'
        
        df = self.remove_duplicates(df, table_name)
        df = self.fix_missing_values(df, table_name)
        
        if 'order_time' in df.columns:
            df = self.fix_timestamps(df, table_name, 'order_time')
        
        qty_price_cols = [col for col in df.columns 
                         if any(x in col.lower() for x in ['qty', 'quantity', 'price', 'amount'])]
        df = self.fix_negative_values(df, table_name, columns=qty_price_cols)
        df = self.fix_outliers_iqr(df, table_name, columns=qty_price_cols)
        
        sku_col = 'sku' if 'sku' in df.columns else 'product_id'
        prod_sku_col = 'sku' if products_df is not None and 'sku' in products_df.columns else 'product_id'
        if products_df is not None and sku_col in df.columns:
            df = self.validate_foreign_keys(df, table_name, sku_col, products_df, prod_sku_col)
        
        if stores_df is not None and 'store_id' in df.columns:
            df = self.validate_foreign_keys(df, table_name, 'store_id', stores_df, 'store_id')
        
        df = self.standardize_text(df, table_name)
        
        return df
    
    def clean_inventory(self, df: pd.DataFrame, products_df: pd.DataFrame = None,
                       stores_df: pd.DataFrame = None) -> pd.DataFrame:
        """Clean inventory table."""
        if df is None:
            return None
        
        table_name = 'inventory'
        
        sku_col = 'sku' if 'sku' in df.columns else 'product_id'
        if sku_col in df.columns and 'store_id' in df.columns:
            df = self.remove_duplicates(df, table_name, subset=[sku_col, 'store_id'])
        else:
            df = self.remove_duplicates(df, table_name)
        
        df = self.fix_missing_values(df, table_name)
        
        stock_cols = [col for col in df.columns if 'stock' in col.lower() or 'qty' in col.lower()]
        df = self.fix_negative_values(df, table_name, columns=stock_cols)
        df = self.fix_outliers_iqr(df, table_name, columns=stock_cols)
        
        prod_sku_col = 'sku' if products_df is not None and 'sku' in products_df.columns else 'product_id'
        if products_df is not None and sku_col in df.columns:
            df = self.validate_foreign_keys(df, table_name, sku_col, products_df, prod_sku_col)
        
        if stores_df is not None and 'store_id' in df.columns:
            df = self.validate_foreign_keys(df, table_name, 'store_id', stores_df, 'store_id')
        
        return df
    
    def clean_all(self, products_df: pd.DataFrame = None, stores_df: pd.DataFrame = None,
                  sales_df: pd.DataFrame = None, inventory_df: pd.DataFrame = None) -> Tuple:
        """Clean all tables and return cleaned DataFrames."""
        self.stats = {
            'missing_values_fixed': 0,
            'duplicates_removed': 0,
            'outliers_fixed': 0,
            'text_standardized': 0,
            'negative_values_fixed': 0,
            'fk_violations_fixed': 0,
            'whitespace_fixed': 0,
            'invalid_timestamps_fixed': 0,
            'total_issues': 0
        }
        self.issues_log = []
        
        clean_products = self.clean_products(products_df)
        clean_stores = self.clean_stores(stores_df)
        clean_sales = self.clean_sales(sales_df, clean_products, clean_stores)
        clean_inventory = self.clean_inventory(inventory_df, clean_products, clean_stores)
        
        return clean_products, clean_stores, clean_sales, clean_inventory


# ============================================================================
# SIMULATOR MODULE (ENHANCED WITH ALL REQUIREMENTS)
# ============================================================================

class Simulator:
    """
    Business Simulator class for calculating KPIs and running what-if scenarios.
    Includes constraint enforcement and demand uplift logic.
    """
    
    # Demand uplift factors by channel and category
    CHANNEL_UPLIFT = {
        'Marketplace': 1.4,  # Marketplace reacts more to discounts
        'App': 1.2,
        'Web': 1.0
    }
    
    CATEGORY_UPLIFT = {
        'Electronics': 1.5,  # Electronics reacts more to discounts
        'Fashion': 1.3,
        'Home': 1.1,
        'Grocery': 0.9,  # Grocery less elastic
        'Beauty': 1.2
    }
    
    def __init__(self):
        """Initialize the Simulator."""
        pass
    
    def calculate_overall_kpis(self, sales_df: pd.DataFrame, 
                               products_df: pd.DataFrame = None) -> Dict[str, Any]:
        """Calculate overall business KPIs from sales data."""
        kpis = {
            'total_revenue': 0,
            'gross_revenue': 0,
            'net_revenue': 0,
            'total_cogs': 0,
            'total_profit': 0,
            'gross_margin_aed': 0,
            'profit_margin_pct': 0,
            'gross_margin_pct': 0,
            'avg_order_value': 0,
            'total_orders': 0,
            'total_quantity': 0,
            'avg_discount_pct': 0,
            'refund_amount': 0,
            'return_rate_pct': 0,
            'promo_spend': 0,
            'profit_proxy': 0,
            'budget_utilization_pct': 0
        }
        
        if sales_df is None or len(sales_df) == 0:
            return kpis
        
        try:
            # Calculate gross revenue
            if 'selling_price_aed' in sales_df.columns and 'qty' in sales_df.columns:
                qty = pd.to_numeric(sales_df['qty'], errors='coerce').fillna(0)
                price = pd.to_numeric(sales_df['selling_price_aed'], errors='coerce').fillna(0)
                kpis['gross_revenue'] = (qty * price).sum()
                kpis['total_revenue'] = kpis['gross_revenue']
            elif 'selling_price_aed' in sales_df.columns:
                kpis['gross_revenue'] = pd.to_numeric(sales_df['selling_price_aed'], errors='coerce').fillna(0).sum()
                kpis['total_revenue'] = kpis['gross_revenue']
            
            # Calculate refunds
            refund_mask = None
            if 'order_status' in sales_df.columns:
                refund_mask = sales_df['order_status'].astype(str).str.lower().isin(['returned', 'refunded', 'cancelled'])
            elif 'payment_status' in sales_df.columns:
                refund_mask = sales_df['payment_status'].astype(str).str.lower().isin(['refunded', 'cancelled'])
            
            if refund_mask is not None and refund_mask.any():
                if 'selling_price_aed' in sales_df.columns:
                    refund_price = pd.to_numeric(sales_df.loc[refund_mask, 'selling_price_aed'], errors='coerce').fillna(0)
                    if 'qty' in sales_df.columns:
                        refund_qty = pd.to_numeric(sales_df.loc[refund_mask, 'qty'], errors='coerce').fillna(0)
                        kpis['refund_amount'] = (refund_qty * refund_price).sum()
                    else:
                        kpis['refund_amount'] = refund_price.sum()
            
            # Net revenue
            kpis['net_revenue'] = kpis['gross_revenue'] - kpis['refund_amount']
            
            # Calculate COGS
            if products_df is not None:
                sku_col = 'sku' if 'sku' in sales_df.columns else 'product_id'
                prod_sku_col = 'sku' if 'sku' in products_df.columns else 'product_id'
                
                cost_col = None
                for col in ['cost_price_aed', 'unit_cost_aed', 'cost_price', 'cost', 'cogs']:
                    if col in products_df.columns:
                        cost_col = col
                        break
                
                if cost_col and sku_col in sales_df.columns and prod_sku_col in products_df.columns:
                    merged = sales_df.merge(products_df[[prod_sku_col, cost_col]], 
                                           left_on=sku_col, right_on=prod_sku_col, how='left')
                    cost = pd.to_numeric(merged[cost_col], errors='coerce').fillna(0)
                    if 'qty' in merged.columns:
                        qty = pd.to_numeric(merged['qty'], errors='coerce').fillna(0)
                        kpis['total_cogs'] = (qty * cost).sum()
                    else:
                        kpis['total_cogs'] = cost.sum()
            
            # Calculate profit and margins
            kpis['total_profit'] = kpis['net_revenue'] - kpis['total_cogs']
            kpis['gross_margin_aed'] = kpis['total_profit']
            
            if kpis['net_revenue'] > 0:
                kpis['profit_margin_pct'] = (kpis['total_profit'] / kpis['net_revenue']) * 100
                kpis['gross_margin_pct'] = kpis['profit_margin_pct']
            
            # Total orders
            if 'order_id' in sales_df.columns:
                kpis['total_orders'] = sales_df['order_id'].nunique()
            else:
                kpis['total_orders'] = len(sales_df)
            
            # Total quantity
            if 'qty' in sales_df.columns:
                kpis['total_quantity'] = pd.to_numeric(sales_df['qty'], errors='coerce').fillna(0).sum()
            
            # Average order value
            if kpis['total_orders'] > 0:
                kpis['avg_order_value'] = kpis['gross_revenue'] / kpis['total_orders']
            
            # Average discount percentage
            if 'discount_pct' in sales_df.columns:
                kpis['avg_discount_pct'] = pd.to_numeric(sales_df['discount_pct'], errors='coerce').fillna(0).mean()
            elif 'discount' in sales_df.columns:
                kpis['avg_discount_pct'] = pd.to_numeric(sales_df['discount'], errors='coerce').fillna(0).mean()
            
            # Return rate
            if refund_mask is not None:
                total = len(sales_df)
                returns = refund_mask.sum()
                kpis['return_rate_pct'] = (returns / total * 100) if total > 0 else 0
            
            # Promo spend (estimated as discount * revenue)
            kpis['promo_spend'] = kpis['gross_revenue'] * (kpis['avg_discount_pct'] / 100)
            
            # Profit proxy
            kpis['profit_proxy'] = kpis['total_profit']
        
        except Exception as e:
            print(f"Error calculating KPIs: {str(e)}")
        
        return kpis
    
    def calculate_kpis_by_dimension(self, sales_df: pd.DataFrame,
                                    stores_df: pd.DataFrame = None,
                                    products_df: pd.DataFrame = None,
                                    dimension: str = 'city') -> pd.DataFrame:
        """Calculate KPIs grouped by a dimension (city, channel, category)."""
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
                sku_col = 'sku' if 'sku' in df.columns else 'product_id'
                prod_sku_col = 'sku' if 'sku' in products_df.columns else 'product_id'
                
                if sku_col in df.columns and prod_sku_col in products_df.columns:
                    product_cols = [prod_sku_col]
                    if 'category' in products_df.columns:
                        product_cols.append('category')
                    
                    cost_col = None
                    for col in ['cost_price_aed', 'unit_cost_aed', 'cost_price', 'cost']:
                        if col in products_df.columns:
                            cost_col = col
                            break
                    if cost_col:
                        product_cols.append(cost_col)
                    
                    df = df.merge(products_df[product_cols], left_on=sku_col, right_on=prod_sku_col, how='left')
            
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
            cost_col = None
            for col in ['cost_price_aed', 'unit_cost_aed', 'cost_price', 'cost']:
                if col in df.columns:
                    cost_col = col
                    break
            
            if cost_col and 'qty' in df.columns:
                df['_cogs'] = (
                    pd.to_numeric(df['qty'], errors='coerce').fillna(0) * 
                    pd.to_numeric(df[cost_col], errors='coerce').fillna(0)
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
            
            grouped = grouped.sort_values('revenue', ascending=False)
            
            return grouped
        
        except Exception as e:
            print(f"Error calculating KPIs by dimension: {str(e)}")
            return pd.DataFrame()
    
    def calculate_demand_uplift(self, base_demand: float, discount_pct: float, 
                               channel: str = None, category: str = None) -> float:
        """
        Calculate demand uplift based on discount and elasticity factors.
        This is rule-based, not ML.
        """
        # Base elasticity: 1% discount = 0.5% demand increase
        base_elasticity = 0.5
        
        # Get channel multiplier
        channel_mult = self.CHANNEL_UPLIFT.get(channel, 1.0) if channel else 1.0
        
        # Get category multiplier
        category_mult = self.CATEGORY_UPLIFT.get(category, 1.0) if category else 1.0
        
        # Calculate uplift
        uplift_pct = discount_pct * base_elasticity * channel_mult * category_mult
        
        # Apply uplift to base demand
        new_demand = base_demand * (1 + uplift_pct / 100)
        
        return new_demand
    
    def simulate_scenario(self, sales_df: pd.DataFrame, products_df: pd.DataFrame = None,
                         stores_df: pd.DataFrame = None, inventory_df: pd.DataFrame = None,
                         discount_pct: float = 0, promo_budget: float = 500000,
                         margin_floor: float = 15, simulation_days: int = 14) -> Dict[str, Any]:
        """
        Run a complete what-if simulation with constraint enforcement.
        """
        # Get baseline KPIs
        baseline = self.calculate_overall_kpis(sales_df, products_df)
        
        # Calculate baseline daily metrics
        if sales_df is not None and 'order_time' in sales_df.columns:
            try:
                sales_df['order_time'] = pd.to_datetime(sales_df['order_time'], errors='coerce')
                date_range = (sales_df['order_time'].max() - sales_df['order_time'].min()).days
                if date_range > 0:
                    daily_revenue = baseline['gross_revenue'] / date_range
                    daily_demand = baseline['total_quantity'] / date_range if baseline['total_quantity'] > 0 else 0
                else:
                    daily_revenue = baseline['gross_revenue']
                    daily_demand = baseline['total_quantity']
            except:
                daily_revenue = baseline['gross_revenue'] / 30  # Assume 30 days
                daily_demand = baseline['total_quantity'] / 30
        else:
            daily_revenue = baseline['gross_revenue'] / 30
            daily_demand = baseline['total_quantity'] / 30
        
        # Calculate demand uplift
        avg_uplift = 1 + (discount_pct * 0.005 * 1.2)  # Simplified average uplift
        simulated_daily_demand = daily_demand * avg_uplift
        simulated_total_demand = simulated_daily_demand * simulation_days
        
        # Calculate simulated revenue
        avg_price = baseline['gross_revenue'] / baseline['total_quantity'] if baseline['total_quantity'] > 0 else 0
        simulated_revenue = simulated_total_demand * avg_price * (1 - discount_pct / 100)
        
        # Calculate promo spend
        promo_spend = simulated_total_demand * avg_price * (discount_pct / 100)
        
        # Calculate simulated COGS
        avg_cost_ratio = baseline['total_cogs'] / baseline['gross_revenue'] if baseline['gross_revenue'] > 0 else 0.6
        simulated_cogs = simulated_revenue * avg_cost_ratio
        
        # Calculate simulated profit
        simulated_profit = simulated_revenue - simulated_cogs - promo_spend
        simulated_margin_pct = (simulated_profit / simulated_revenue * 100) if simulated_revenue > 0 else 0
        
        # Budget utilization
        budget_utilization = (promo_spend / promo_budget * 100) if promo_budget > 0 else 0
        
        # Check stock constraint
        stock_violation = False
        stock_shortage = 0
        top_stockout_items = []
        
        if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
            total_stock = pd.to_numeric(inventory_df['stock_on_hand'], errors='coerce').fillna(0).sum()
            if simulated_total_demand > total_stock:
                stock_violation = True
                stock_shortage = simulated_total_demand - total_stock
                
                # Get top 10 items at risk
                sku_col = 'sku' if 'sku' in inventory_df.columns else 'product_id'
                if sku_col in inventory_df.columns:
                    top_stockout_items = inventory_df.nsmallest(10, 'stock_on_hand')[[sku_col, 'stock_on_hand']].to_dict('records')
        
        # Check constraints
        constraints = {
            'budget_ok': promo_spend <= promo_budget,
            'margin_ok': simulated_margin_pct >= margin_floor,
            'stock_ok': not stock_violation,
            'all_ok': True
        }
        constraints['all_ok'] = constraints['budget_ok'] and constraints['margin_ok'] and constraints['stock_ok']
        
        # Build results
        results = {
            # Baseline
            'baseline_revenue': baseline['gross_revenue'],
            'baseline_margin_pct': baseline['profit_margin_pct'],
            'baseline_daily_demand': daily_demand,
            
            # Simulated
            'simulated_revenue': simulated_revenue,
            'simulated_profit': simulated_profit,
            'simulated_margin_pct': simulated_margin_pct,
            'simulated_demand': simulated_total_demand,
            
            # Promo metrics
            'promo_spend': promo_spend,
            'budget_utilization_pct': budget_utilization,
            'profit_proxy': simulated_profit,
            
            # Changes
            'revenue_change_pct': ((simulated_revenue - baseline['gross_revenue']) / baseline['gross_revenue'] * 100) if baseline['gross_revenue'] > 0 else 0,
            'margin_change_pct': simulated_margin_pct - baseline['profit_margin_pct'],
            'demand_uplift_pct': (avg_uplift - 1) * 100,
            
            # Constraints
            'constraints': constraints,
            'stock_shortage': stock_shortage,
            'top_stockout_items': top_stockout_items,
            
            # Parameters used
            'discount_pct': discount_pct,
            'promo_budget': promo_budget,
            'margin_floor': margin_floor,
            'simulation_days': simulation_days
        }
        
        return results
    
    def get_top_products(self, sales_df: pd.DataFrame, products_df: pd.DataFrame = None,
                        n: int = 10, metric: str = 'revenue') -> pd.DataFrame:
        """Get top N products by a metric."""
        if sales_df is None or len(sales_df) == 0:
            return pd.DataFrame()
        
        sku_col = 'sku' if 'sku' in sales_df.columns else 'product_id'
        if sku_col not in sales_df.columns:
            return pd.DataFrame()
        
        try:
            df = sales_df.copy()
            
            if 'selling_price_aed' in df.columns and 'qty' in df.columns:
                df['_revenue'] = (
                    pd.to_numeric(df['qty'], errors='coerce').fillna(0) * 
                    pd.to_numeric(df['selling_price_aed'], errors='coerce').fillna(0)
                )
            else:
                df['_revenue'] = 0
            
            df['_qty'] = pd.to_numeric(df.get('qty', 0), errors='coerce').fillna(0)
            
            grouped = df.groupby(sku_col).agg({
                '_revenue': 'sum',
                '_qty': 'sum'
            }).reset_index()
            
            grouped.columns = [sku_col, 'revenue', 'quantity']
            
            if products_df is not None:
                prod_sku_col = 'sku' if 'sku' in products_df.columns else 'product_id'
                name_col = 'product_name' if 'product_name' in products_df.columns else 'name'
                if name_col in products_df.columns and prod_sku_col in products_df.columns:
                    grouped = grouped.merge(products_df[[prod_sku_col, name_col]], 
                                           left_on=sku_col, right_on=prod_sku_col, how='left')
            
            sort_col = 'revenue' if metric == 'revenue' else 'quantity'
            return grouped.sort_values(sort_col, ascending=False).head(n)
        
        except Exception as e:
            print(f"Error getting top products: {str(e)}")
            return pd.DataFrame()
    
    def calculate_inventory_metrics(self, inventory_df: pd.DataFrame,
                                   sales_df: pd.DataFrame = None) -> Dict[str, Any]:
        """Calculate inventory-related metrics."""
        metrics = {
            'total_stock': 0,
            'low_stock_count': 0,
            'out_of_stock_count': 0,
            'stockout_risk_pct': 0,
            'avg_stock_per_sku': 0,
            'high_risk_skus': 0
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
                metrics['high_risk_skus'] = metrics['low_stock_count']
                metrics['avg_stock_per_sku'] = stock.mean()
                
                total_items = len(inventory_df)
                if total_items > 0:
                    metrics['stockout_risk_pct'] = (metrics['low_stock_count'] / total_items) * 100
        
        except Exception as e:
            print(f"Error calculating inventory metrics: {str(e)}")
        
        return metrics


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
        <p style="margin: 5px 0 0 0; font-size: 0.85rem;">Built with ❤️ using Streamlit | Data Rescue + Promo Pulse Simulator</p>
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
        ">Promo Pulse Simulator + Data Rescue Center</p>
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
                Supports faculty dataset testing with column mapping.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card-3d" style="text-align: center; min-height: 250px;">
            <div style="font-size: 50px; margin-bottom: 15px;">🧹</div>
            <h3 style="color: {t['accent_green']}; margin-bottom: 10px;">Data Rescue</h3>
            <p style="color: {t['text_secondary']}; font-size: 0.95rem;">
                Automatically detect and fix data quality issues: missing values, duplicates, 
                outliers, invalid timestamps, and FK violations.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="card-3d" style="text-align: center; min-height: 250px;">
            <div style="font-size: 50px; margin-bottom: 15px;">📊</div>
            <h3 style="color: {t['accent_purple']}; margin-bottom: 10px;">Dashboard</h3>
            <p style="color: {t['text_secondary']}; font-size: 0.95rem;">
                Toggle between Executive View (financial KPIs) and Manager View 
                (operational metrics) with 14+ KPIs.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="card-3d" style="text-align: center; min-height: 250px;">
            <div style="font-size: 50px; margin-bottom: 15px;">🎯</div>
            <h3 style="color: {t['accent_orange']}; margin-bottom: 10px;">Promo Simulator</h3>
            <p style="color: {t['text_secondary']}; font-size: 0.95rem;">
                Run what-if scenarios with budget caps, margin floors, and stock constraints.
                Rule-based demand uplift by channel and category.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card-3d" style="text-align: center; min-height: 250px;">
            <div style="font-size: 50px; margin-bottom: 15px;">🌐</div>
            <h3 style="color: {t['accent_teal']}; margin-bottom: 10px;">6 Global Filters</h3>
            <p style="color: {t['text_secondary']}; font-size: 0.95rem;">
                Filter by Date Range, City, Channel, Category, Brand, and Fulfillment Type.
                Multi-select support for all filters.
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
                Beautiful 3D cards and gradient styling.
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
            <li><strong>📂 Load Data</strong> — Upload your CSV/Excel files (Products, Stores, Sales, Inventory)</li>
            <li><strong>🧹 Clean Data</strong> — Run the data cleaner to fix quality issues and generate issues log</li>
            <li><strong>📊 View Dashboard</strong> — Toggle between Executive and Manager views with 14+ KPIs</li>
            <li><strong>🎯 Run Simulations</strong> — Test promo scenarios with budget, margin, and stock constraints</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Project requirements checklist
    st.markdown("---")
    st.markdown(f'<p class="section-title section-title-purple">✅ Project Requirements Coverage</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="card-3d">
            <h4 style="color: {t['accent_green']}; margin-bottom: 15px;">Phase 1: Data Rescue ✅</h4>
            <ul style="color: {t['text_primary']}; line-height: 1.8;">
                <li>✅ Validation rules (timestamps, FKs, ranges)</li>
                <li>✅ Issues log with action_taken column</li>
                <li>✅ Duplicate detection & removal</li>
                <li>✅ Missing value imputation</li>
                <li>✅ Outlier detection (IQR method)</li>
                <li>✅ Text standardization</li>
                <li>✅ Download cleaned data</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card-3d">
            <h4 style="color: {t['accent_orange']}; margin-bottom: 15px;">Phase 2: Promo Simulator ✅</h4>
            <ul style="color: {t['text_primary']}; line-height: 1.8;">
                <li>✅ 14 KPIs (Finance + Operations)</li>
                <li>✅ Promo Budget input + utilization</li>
                <li>✅ Margin Floor constraint</li>
                <li>✅ Stock constraint + violations</li>
                <li>✅ Simulation window (7/14 days)</li>
                <li>✅ Rule-based demand uplift</li>
                <li>✅ Scenario comparison charts</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    show_footer()


# ============================================================================
# PAGE: DATA (WITH COLUMN MAPPING FOR FACULTY TESTING)
# ============================================================================

def show_data_page():
    """Display the data loading page with column mapping support."""
    t = get_theme()
    
    st.markdown(f'<h1 class="page-title page-title-cyan">📂 Data Loading</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-description">Upload your retail data files to get started. Supports faculty dataset testing.</p>', unsafe_allow_html=True)
    
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
    
    # Column Mapping Section (for faculty testing)
    if st.session_state.data_loaded:
        st.markdown("---")
        st.markdown(f'<p class="section-title section-title-teal">🔄 Column Mapping (Faculty Testing)</p>', unsafe_allow_html=True)
        
        with st.expander("📋 Map Columns to Expected Schema", expanded=False):
            st.markdown("""
            If your uploaded files have different column names, map them to the expected schema below.
            This is useful when the faculty provides a new dataset during presentation.
            """)
            
            tab1, tab2, tab3, tab4 = st.tabs(["Products", "Stores", "Sales", "Inventory"])
            
            with tab1:
                if st.session_state.raw_products is not None:
                    st.markdown("**Expected columns:** sku/product_id, category, brand, base_price_aed, cost_price_aed")
                    cols = list(st.session_state.raw_products.columns)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        sku_map = st.selectbox("SKU/Product ID column:", ['(auto-detect)'] + cols, key='prod_sku_map')
                        category_map = st.selectbox("Category column:", ['(auto-detect)'] + cols, key='prod_cat_map')
                        brand_map = st.selectbox("Brand column:", ['(auto-detect)'] + cols, key='prod_brand_map')
                    with col2:
                        price_map = st.selectbox("Base Price column:", ['(auto-detect)'] + cols, key='prod_price_map')
                        cost_map = st.selectbox("Cost Price column:", ['(auto-detect)'] + cols, key='prod_cost_map')
                    
                    if st.button("Apply Product Mapping", key='apply_prod_map'):
                        df = st.session_state.raw_products.copy()
                        rename_map = {}
                        if sku_map != '(auto-detect)':
                            rename_map[sku_map] = 'sku'
                        if category_map != '(auto-detect)':
                            rename_map[category_map] = 'category'
                        if brand_map != '(auto-detect)':
                            rename_map[brand_map] = 'brand'
                        if price_map != '(auto-detect)':
                            rename_map[price_map] = 'base_price_aed'
                        if cost_map != '(auto-detect)':
                            rename_map[cost_map] = 'cost_price_aed'
                        
                        if rename_map:
                            df = df.rename(columns=rename_map)
                            st.session_state.raw_products = df
                            st.success("✅ Product columns mapped successfully!")
                            st.rerun()
            
            with tab2:
                if st.session_state.raw_stores is not None:
                    st.markdown("**Expected columns:** store_id, city, channel, fulfillment_type")
                    cols = list(st.session_state.raw_stores.columns)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        store_id_map = st.selectbox("Store ID column:", ['(auto-detect)'] + cols, key='store_id_map')
                        city_map = st.selectbox("City column:", ['(auto-detect)'] + cols, key='store_city_map')
                    with col2:
                        channel_map = st.selectbox("Channel column:", ['(auto-detect)'] + cols, key='store_channel_map')
                        fulfillment_map = st.selectbox("Fulfillment Type column:", ['(auto-detect)'] + cols, key='store_fulfillment_map')
                    
                    if st.button("Apply Store Mapping", key='apply_store_map'):
                        df = st.session_state.raw_stores.copy()
                        rename_map = {}
                        if store_id_map != '(auto-detect)':
                            rename_map[store_id_map] = 'store_id'
                        if city_map != '(auto-detect)':
                            rename_map[city_map] = 'city'
                        if channel_map != '(auto-detect)':
                            rename_map[channel_map] = 'channel'
                        if fulfillment_map != '(auto-detect)':
                            rename_map[fulfillment_map] = 'fulfillment_type'
                        
                        if rename_map:
                            df = df.rename(columns=rename_map)
                            st.session_state.raw_stores = df
                            st.success("✅ Store columns mapped successfully!")
                            st.rerun()
            
            with tab3:
                if st.session_state.raw_sales is not None:
                    st.markdown("**Expected columns:** order_id, order_time, sku/product_id, store_id, qty, selling_price_aed, discount_pct, payment_status")
                    cols = list(st.session_state.raw_sales.columns)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        order_id_map = st.selectbox("Order ID column:", ['(auto-detect)'] + cols, key='sales_order_map')
                        order_time_map = st.selectbox("Order Time column:", ['(auto-detect)'] + cols, key='sales_time_map')
                        sku_map = st.selectbox("SKU/Product ID column:", ['(auto-detect)'] + cols, key='sales_sku_map')
                    with col2:
                        store_map = st.selectbox("Store ID column:", ['(auto-detect)'] + cols, key='sales_store_map')
                        qty_map = st.selectbox("Quantity column:", ['(auto-detect)'] + cols, key='sales_qty_map')
                        price_map = st.selectbox("Selling Price column:", ['(auto-detect)'] + cols, key='sales_price_map')
                    with col3:
                        discount_map = st.selectbox("Discount % column:", ['(auto-detect)'] + cols, key='sales_discount_map')
                        payment_map = st.selectbox("Payment Status column:", ['(auto-detect)'] + cols, key='sales_payment_map')
                    
                    if st.button("Apply Sales Mapping", key='apply_sales_map'):
                        df = st.session_state.raw_sales.copy()
                        rename_map = {}
                        if order_id_map != '(auto-detect)':
                            rename_map[order_id_map] = 'order_id'
                        if order_time_map != '(auto-detect)':
                            rename_map[order_time_map] = 'order_time'
                        if sku_map != '(auto-detect)':
                            rename_map[sku_map] = 'sku'
                        if store_map != '(auto-detect)':
                            rename_map[store_map] = 'store_id'
                        if qty_map != '(auto-detect)':
                            rename_map[qty_map] = 'qty'
                        if price_map != '(auto-detect)':
                            rename_map[price_map] = 'selling_price_aed'
                        if discount_map != '(auto-detect)':
                            rename_map[discount_map] = 'discount_pct'
                        if payment_map != '(auto-detect)':
                            rename_map[payment_map] = 'payment_status'
                        
                        if rename_map:
                            df = df.rename(columns=rename_map)
                            st.session_state.raw_sales = df
                            st.success("✅ Sales columns mapped successfully!")
                            st.rerun()
            
            with tab4:
                if st.session_state.raw_inventory is not None:
                    st.markdown("**Expected columns:** sku/product_id, store_id, stock_on_hand, reorder_point")
                    cols = list(st.session_state.raw_inventory.columns)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        sku_map = st.selectbox("SKU/Product ID column:", ['(auto-detect)'] + cols, key='inv_sku_map')
                        store_map = st.selectbox("Store ID column:", ['(auto-detect)'] + cols, key='inv_store_map')
                    with col2:
                        stock_map = st.selectbox("Stock on Hand column:", ['(auto-detect)'] + cols, key='inv_stock_map')
                        reorder_map = st.selectbox("Reorder Point column:", ['(auto-detect)'] + cols, key='inv_reorder_map')
                    
                    if st.button("Apply Inventory Mapping", key='apply_inv_map'):
                        df = st.session_state.raw_inventory.copy()
                        rename_map = {}
                        if sku_map != '(auto-detect)':
                            rename_map[sku_map] = 'sku'
                        if store_map != '(auto-detect)':
                            rename_map[store_map] = 'store_id'
                        if stock_map != '(auto-detect)':
                            rename_map[stock_map] = 'stock_on_hand'
                        if reorder_map != '(auto-detect)':
                            rename_map[reorder_map] = 'reorder_point'
                        
                        if rename_map:
                            df = df.rename(columns=rename_map)
                            st.session_state.raw_inventory = df
                            st.success("✅ Inventory columns mapped successfully!")
                            st.rerun()
    
    # Show loaded data preview
    if st.session_state.data_loaded:
        st.markdown("---")
        st.markdown(f'<p class="section-title section-title-green">📊 Data Preview</p>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📦 Products", "🏪 Stores", "🛒 Sales", "📋 Inventory"])
        
        with tab1:
            if st.session_state.raw_products is not None:
                st.markdown(f"**Shape:** {st.session_state.raw_products.shape[0]:,} rows × {st.session_state.raw_products.shape[1]} columns")
                st.markdown(f"**Columns:** {', '.join(st.session_state.raw_products.columns.tolist())}")
                st.dataframe(st.session_state.raw_products.head(100), use_container_width=True)
            else:
                st.info("No products data loaded")
        
        with tab2:
            if st.session_state.raw_stores is not None:
                st.markdown(f"**Shape:** {st.session_state.raw_stores.shape[0]:,} rows × {st.session_state.raw_stores.shape[1]} columns")
                st.markdown(f"**Columns:** {', '.join(st.session_state.raw_stores.columns.tolist())}")
                st.dataframe(st.session_state.raw_stores.head(100), use_container_width=True)
            else:
                st.info("No stores data loaded")
        
        with tab3:
            if st.session_state.raw_sales is not None:
                st.markdown(f"**Shape:** {st.session_state.raw_sales.shape[0]:,} rows × {st.session_state.raw_sales.shape[1]} columns")
                st.markdown(f"**Columns:** {', '.join(st.session_state.raw_sales.columns.tolist())}")
                st.dataframe(st.session_state.raw_sales.head(100), use_container_width=True)
            else:
                st.info("No sales data loaded")
        
        with tab4:
            if st.session_state.raw_inventory is not None:
                st.markdown(f"**Shape:** {st.session_state.raw_inventory.shape[0]:,} rows × {st.session_state.raw_inventory.shape[1]} columns")
                st.markdown(f"**Columns:** {', '.join(st.session_state.raw_inventory.columns.tolist())}")
                st.dataframe(st.session_state.raw_inventory.head(100), use_container_width=True)
            else:
                st.info("No inventory data loaded")
    
    show_footer()


# ============================================================================
# PAGE: CLEANER
# ============================================================================

def show_cleaner_page():
    """Display the data cleaner page."""
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
                <li>Invalid timestamps</li>
                <li>Whitespace issues</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card-3d">
            <strong style="color: {t['accent_purple']}; font-size: 1.1rem;">Format Issues</strong>
            <ul style="color: {t['text_primary']}; font-size: 0.95rem; margin-bottom: 0; line-height: 1.8;">
                <li>Text standardization</li>
                <li>City name variants</li>
                <li>Case normalization</li>
                <li>Multi-language text</li>
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
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            value = stats.get('missing_values_fixed', 0)
            st.markdown(create_metric_card_3d("Missing Fixed", f"{value:,}", color="cyan"), unsafe_allow_html=True)
        
        with col2:
            value = stats.get('duplicates_removed', 0)
            st.markdown(create_metric_card_3d("Duplicates Removed", f"{value:,}", color="blue"), unsafe_allow_html=True)
        
        with col3:
            value = stats.get('outliers_fixed', 0)
            st.markdown(create_metric_card_3d("Outliers Fixed", f"{value:,}", color="purple"), unsafe_allow_html=True)
        
        with col4:
            value = stats.get('text_standardized', 0)
            st.markdown(create_metric_card_3d("Text Standardized", f"{value:,}", color="pink"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Row 2
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            value = stats.get('negative_values_fixed', 0)
            st.markdown(create_metric_card_3d("Negatives Fixed", f"{value:,}", color="orange"), unsafe_allow_html=True)
        
        with col2:
            value = stats.get('invalid_timestamps_fixed', 0)
            st.markdown(create_metric_card_3d("Timestamps Fixed", f"{value:,}", color="teal"), unsafe_allow_html=True)
        
        with col3:
            value = stats.get('fk_violations_fixed', 0)
            st.markdown(create_metric_card_3d("FK Violations", f"{value:,}", color="red"), unsafe_allow_html=True)
        
        with col4:
            value = stats.get('total_issues', 0)
            st.markdown(create_metric_card_3d("Total Issues", f"{value:,}", color="green"), unsafe_allow_html=True)
        
        # Issues breakdown
        issues_df = st.session_state.issues_df
        
        if issues_df is not None and len(issues_df) > 0:
            has_real_issues = not (len(issues_df) == 1 and issues_df.iloc[0].get('issue_type', '') == 'None')
            
            if has_real_issues:
                st.markdown("---")
                st.markdown(f'<p class="section-title section-title-orange">🔍 Issues Breakdown (Pareto)</p>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    issue_counts = issues_df.groupby('issue_type').size().reset_index(name='count')
                    issue_counts = issue_counts[issue_counts['issue_type'] != 'None']
                    issue_counts = issue_counts.sort_values('count', ascending=False)
                    
                    if len(issue_counts) > 0:
                        # Add cumulative percentage for Pareto
                        total = issue_counts['count'].sum()
                        issue_counts['cumulative_pct'] = (issue_counts['count'].cumsum() / total * 100)
                        
                        # Create Pareto chart
                        fig = go.Figure()
                        
                        # Bars
                        fig.add_trace(go.Bar(
                            x=issue_counts['issue_type'],
                            y=issue_counts['count'],
                            name='Count',
                            marker_color=t['accent_cyan']
                        ))
                        
                        # Line
                        fig.add_trace(go.Scatter(
                            x=issue_counts['issue_type'],
                            y=issue_counts['cumulative_pct'],
                            name='Cumulative %',
                            yaxis='y2',
                            mode='lines+markers',
                            line=dict(color=t['accent_pink'], width=3),
                            marker=dict(size=8)
                        ))
                        
                        fig.update_layout(
                            title='Issues Pareto Chart',
                            yaxis=dict(title='Count'),
                            yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0, 105])
                        )
                        fig = style_plotly_chart_themed(fig)
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
                
                # Download issues log
                issues_csv = issues_df.to_csv(index=False)
                st.download_button(
                    "📥 Download Issues Log (CSV)",
                    issues_csv,
                    "issues.csv",
                    "text/csv",
                    use_container_width=True
                )
            else:
                st.markdown(create_success_card_3d("No major issues found! Your data is clean."), unsafe_allow_html=True)
        
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
# PAGE: DASHBOARD
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
    filtered_inventory = apply_global_filters(inventory_df, stores_df, products_df) if inventory_df is not None else None
    
    # Filter products and stores based on what's in filtered sales
    filtered_products = products_df
    filtered_stores = stores_df
    
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
    if len(st.session_state.get('global_brands', [])) > 0:
        active_filters.append(f"{len(st.session_state.global_brands)} Brands")
    
    if active_filters:
        st.markdown(f"""
        <div class="info-card-3d" style="background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(59, 130, 246, 0.1)); border: 1px solid {t['accent_cyan']}; border-radius: 12px; padding: 15px 20px;">
            <strong style="color: {t['accent_cyan']};">🌐 Global Filters Active:</strong>
            <span style="color: {t['text_secondary']};">{' | '.join(active_filters)}</span>
            <span style="color: {t['text_muted']}; font-size: 0.85rem; margin-left: 10px;">
                ({len(filtered_sales):,} records after filtering)
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Calculate KPIs using filtered data
    sim = Simulator()
    kpis = sim.calculate_overall_kpis(filtered_sales, filtered_products)
    city_kpis = sim.calculate_kpis_by_dimension(filtered_sales, filtered_stores, filtered_products, 'city')
    channel_kpis = sim.calculate_kpis_by_dimension(filtered_sales, filtered_stores, filtered_products, 'channel')
    category_kpis = sim.calculate_kpis_by_dimension(filtered_sales, filtered_stores, filtered_products, 'category')
    
    if not view_mode:
        show_executive_view(kpis, city_kpis, channel_kpis, category_kpis, filtered_sales, filtered_products, filtered_stores)
    else:
        show_manager_view(kpis, city_kpis, channel_kpis, category_kpis, filtered_sales, filtered_products, filtered_stores, filtered_inventory)
    
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
    
    # Row 1: Revenue KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        gross_revenue = kpis.get('gross_revenue', 0)
        st.markdown(create_metric_card_3d("Gross Revenue", format_currency(gross_revenue), color="cyan", delay=0.1), unsafe_allow_html=True)
    
    with col2:
        refund_amount = kpis.get('refund_amount', 0)
        st.markdown(create_metric_card_3d("Refund Amount", format_currency(refund_amount), color="pink", delay=0.2), unsafe_allow_html=True)
    
    with col3:
        net_revenue = kpis.get('net_revenue', 0)
        st.markdown(create_metric_card_3d("Net Revenue", format_currency(net_revenue), color="green", delay=0.3), unsafe_allow_html=True)
    
    with col4:
        cogs = kpis.get('total_cogs', 0)
        st.markdown(create_metric_card_3d("COGS", format_currency(cogs), color="orange", delay=0.4), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 2: Margin and Discount KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        gross_margin = kpis.get('gross_margin_aed', 0)
        st.markdown(create_metric_card_3d("Gross Margin (AED)", format_currency(gross_margin), color="teal", delay=0.1), unsafe_allow_html=True)
    
    with col2:
        gross_margin_pct = kpis.get('gross_margin_pct', 0)
        st.markdown(create_metric_card_3d("Gross Margin %", f"{gross_margin_pct:.1f}%", color="purple", delay=0.2), unsafe_allow_html=True)
    
    with col3:
        avg_discount = kpis.get('avg_discount_pct', 0)
        st.markdown(create_metric_card_3d("Avg Discount %", f"{avg_discount:.1f}%", color="blue", delay=0.3), unsafe_allow_html=True)
    
    with col4:
        avg_order_value = kpis.get('avg_order_value', 0)
        st.markdown(create_metric_card_3d("Avg Order Value", format_currency(avg_order_value), color="cyan", delay=0.4), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    st.markdown(f'<p class="section-title section-title-blue">📈 Executive Charts</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📅 Net Revenue Trend")
        local_filters_1 = show_chart_filter('exec_trend', ['city', 'channel', 'category', 'brand'])
        chart_data_1 = apply_local_filters(sales_df, local_filters_1, stores_df, products_df)
        
        if chart_data_1 is not None and 'order_time' in chart_data_1.columns and len(chart_data_1) > 0:
            sales_trend = chart_data_1.copy()
            sales_trend['order_time'] = pd.to_datetime(sales_trend['order_time'], errors='coerce')
            sales_trend['date'] = sales_trend['order_time'].dt.date
            
            if 'selling_price_aed' in sales_trend.columns and 'qty' in sales_trend.columns:
                sales_trend['revenue'] = (
                    pd.to_numeric(sales_trend['qty'], errors='coerce').fillna(0) *
                    pd.to_numeric(sales_trend['selling_price_aed'], errors='coerce').fillna(0)
                )
            elif 'selling_price_aed' in sales_trend.columns:
                sales_trend['revenue'] = pd.to_numeric(sales_trend['selling_price_aed'], errors='coerce').fillna(0)
            else:
                sales_trend['revenue'] = 0
            
            daily_revenue = sales_trend.groupby('date')['revenue'].sum().reset_index()
            daily_revenue.columns = ['Date', 'Revenue']
            
            fig = px.area(daily_revenue, x='Date', y='Revenue', title='')
            fig = style_plotly_chart_themed(fig)
            fig.update_traces(fill='tozeroy', line_color=t['accent_cyan'], fillcolor=f"rgba(6, 182, 212, 0.3)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Revenue trend requires order_time column")
    
    with col2:
        st.markdown("#### 🏙️ Revenue by City/Channel (Sunburst)")
        local_filters_2 = show_chart_filter('exec_sunburst', ['category', 'brand'])
        chart_data_2 = apply_local_filters(sales_df, local_filters_2, stores_df, products_df)
        
        if chart_data_2 is not None and len(chart_data_2) > 0 and stores_df is not None:
            merged = chart_data_2.merge(stores_df[['store_id', 'city', 'channel']], on='store_id', how='left')
            
            if 'selling_price_aed' in merged.columns and 'qty' in merged.columns:
                merged['revenue'] = (
                    pd.to_numeric(merged['qty'], errors='coerce').fillna(0) *
                    pd.to_numeric(merged['selling_price_aed'], errors='coerce').fillna(0)
                )
            else:
                merged['revenue'] = 0
            
            sunburst_data = merged.groupby(['city', 'channel'])['revenue'].sum().reset_index()
            
            if len(sunburst_data) > 0:
                fig = px.sunburst(
                    sunburst_data,
                    path=['city', 'channel'],
                    values='revenue',
                    title='',
                    color='revenue',
                    color_continuous_scale=[t['accent_cyan'], t['accent_blue'], t['accent_purple']]
                )
                fig = style_plotly_chart_themed(fig)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data for sunburst chart")
        else:
            st.info("City/Channel data not available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📦 Margin % by Category")
        local_filters_3 = show_chart_filter('exec_category', ['city', 'channel', 'brand'])
        chart_data_3 = apply_local_filters(sales_df, local_filters_3, stores_df, products_df)
        
        cat_kpis_filtered = Simulator().calculate_kpis_by_dimension(chart_data_3, stores_df, products_df, 'category')
        
        if len(cat_kpis_filtered) > 0:
            fig = px.bar(
                cat_kpis_filtered.head(8), 
                x='margin_pct', 
                y='category', 
                orientation='h',
                title='', 
                color='margin_pct',
                color_continuous_scale=[t['accent_red'], t['accent_orange'], t['accent_green']]
            )
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(coloraxis_showscale=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available")
    
    with col2:
        st.markdown("#### 📱 Revenue by Channel")
        local_filters_4 = show_chart_filter('exec_channel', ['city', 'category', 'brand'])
        chart_data_4 = apply_local_filters(sales_df, local_filters_4, stores_df, products_df)
        
        channel_kpis_filtered = Simulator().calculate_kpis_by_dimension(chart_data_4, stores_df, products_df, 'channel')
        
        if len(channel_kpis_filtered) > 0:
            fig = px.pie(
                channel_kpis_filtered, 
                values='revenue', 
                names='channel', 
                title='',
                color_discrete_sequence=[t['accent_cyan'], t['accent_purple'], t['accent_pink']], 
                hole=0.4
            )
            fig = style_plotly_chart_themed(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No channel data available")
    
    st.markdown("---")
    
    # Profit Bridge (Waterfall Chart)
    st.markdown(f'<p class="section-title section-title-teal">🌊 Profit Bridge (Waterfall)</p>', unsafe_allow_html=True)
    
    gross_rev = kpis.get('gross_revenue', 0)
    refunds = kpis.get('refund_amount', 0)
    cogs = kpis.get('total_cogs', 0)
    profit = kpis.get('total_profit', 0)
    
    fig = go.Figure(go.Waterfall(
        name="Profit Bridge",
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=["Gross Revenue", "Refunds", "COGS", "Net Profit"],
        y=[gross_rev, -refunds, -cogs, profit],
        connector={"line": {"color": t['border_color']}},
        decreasing={"marker": {"color": t['accent_red']}},
        increasing={"marker": {"color": t['accent_green']}},
        totals={"marker": {"color": t['accent_cyan']}}
    ))
    fig = style_plotly_chart_themed(fig)
    fig.update_layout(title="", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
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
    
    payment_failure_rate = 0
    if sales_df is not None and 'payment_status' in sales_df.columns:
        total_orders = len(sales_df)
        failed_orders = (sales_df['payment_status'].astype(str).str.lower() == 'failed').sum()
        payment_failure_rate = (failed_orders / total_orders * 100) if total_orders > 0 else 0
    
    stockout_risk = 0
    high_risk_skus = 0
    if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
        stock = pd.to_numeric(inventory_df['stock_on_hand'], errors='coerce').fillna(0)
        low_stock = (stock < 10).sum()
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
    
    # Gauge Chart for Stockout Risk
    st.markdown(f'<p class="section-title section-title-pink">🎯 Stockout Risk Gauge</p>', unsafe_allow_html=True)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=stockout_risk,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Stockout Risk %", 'font': {'size': 20, 'color': t['text_primary']}},
        delta={'reference': 15, 'increasing': {'color': t['accent_red']}, 'decreasing': {'color': t['accent_green']}},
        gauge={
            'axis': {'range': [0, 50], 'tickwidth': 1, 'tickcolor': t['text_secondary']},
            'bar': {'color': t['accent_pink']},
            'bgcolor': t['bg_card'],
            'borderwidth': 2,
            'bordercolor': t['border_color'],
            'steps': [
                {'range': [0, 10], 'color': t['accent_green']},
                {'range': [10, 25], 'color': t['accent_orange']},
                {'range': [25, 50], 'color': t['accent_red']}
            ],
            'threshold': {
                'line': {'color': t['accent_red'], 'width': 4},
                'thickness': 0.75,
                'value': 30
            }
        }
    ))
    fig = style_plotly_chart_themed(fig)
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Charts
    st.markdown(f'<p class="section-title section-title-teal">📊 Operational Charts</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏙️ Stockout Risk by City/Channel")
        local_filters_1 = show_chart_filter('mgr_stockout', ['category', 'brand'])
        
        if inventory_df is not None and stores_df is not None and 'stock_on_hand' in inventory_df.columns:
            inv_with_store = inventory_df.merge(stores_df[['store_id', 'city', 'channel']], on='store_id', how='left')
            inv_with_store['stock_on_hand'] = pd.to_numeric(inv_with_store['stock_on_hand'], errors='coerce').fillna(0)
            inv_with_store['is_low_stock'] = inv_with_store['stock_on_hand'] < 10
            
            city_risk = inv_with_store.groupby('city').agg({
                'is_low_stock': 'mean'
            }).reset_index()
            city_risk.columns = ['city', 'stockout_risk']
            city_risk['stockout_risk'] = city_risk['stockout_risk'] * 100
            
            if len(city_risk) > 0:
                fig = px.bar(
                    city_risk, 
                    x='stockout_risk', 
                    y='city', 
                    orientation='h',
                    title='', 
                    color='stockout_risk',
                    color_continuous_scale=[t['accent_green'], t['accent_orange'], t['accent_red']]
                )
                fig = style_plotly_chart_themed(fig)
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No city risk data available")
        else:
            st.info("Inventory or store data not available")
    
    with col2:
        st.markdown("#### 📦 Demand vs Stock by Category")
        local_filters_2 = show_chart_filter('mgr_demand_stock', ['city', 'channel'])
        
        if sales_df is not None and inventory_df is not None and products_df is not None:
            sku_col = 'sku' if 'sku' in sales_df.columns else 'product_id'
            prod_sku_col = 'sku' if 'sku' in products_df.columns else 'product_id'
            
            if sku_col in sales_df.columns and prod_sku_col in products_df.columns and 'category' in products_df.columns:
                # Calculate demand by category
                sales_with_cat = sales_df.merge(products_df[[prod_sku_col, 'category']], left_on=sku_col, right_on=prod_sku_col, how='left')
                if 'qty' in sales_with_cat.columns:
                    demand_by_cat = sales_with_cat.groupby('category')['qty'].sum().reset_index()
                    demand_by_cat.columns = ['category', 'demand']
                else:
                    demand_by_cat = pd.DataFrame(columns=['category', 'demand'])
                
                # Calculate stock by category
                inv_sku_col = 'sku' if 'sku' in inventory_df.columns else 'product_id'
                if inv_sku_col in inventory_df.columns:
                    inv_with_cat = inventory_df.merge(products_df[[prod_sku_col, 'category']], left_on=inv_sku_col, right_on=prod_sku_col, how='left')
                    if 'stock_on_hand' in inv_with_cat.columns:
                        stock_by_cat = inv_with_cat.groupby('category')['stock_on_hand'].sum().reset_index()
                        stock_by_cat.columns = ['category', 'stock']
                    else:
                        stock_by_cat = pd.DataFrame(columns=['category', 'stock'])
                else:
                    stock_by_cat = pd.DataFrame(columns=['category', 'stock'])
                
                if len(demand_by_cat) > 0 and len(stock_by_cat) > 0:
                    merged = demand_by_cat.merge(stock_by_cat, on='category', how='outer').fillna(0)
                    merged = merged.head(8)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(name='Demand', x=merged['category'], y=merged['demand'], marker_color=t['accent_cyan']))
                    fig.add_trace(go.Bar(name='Stock', x=merged['category'], y=merged['stock'], marker_color=t['accent_purple']))
                    fig.update_layout(barmode='group', title='')
                    fig = style_plotly_chart_themed(fig)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for demand vs stock chart")
            else:
                st.info("Required columns not found")
        else:
            st.info("Sales, inventory, or product data not available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚨 Top 10 Stockout Risk Items")
        local_filters_3 = show_chart_filter('mgr_risk_items', ['city', 'channel', 'category'])
        
        if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
            sku_col = 'sku' if 'sku' in inventory_df.columns else 'product_id'
            if sku_col in inventory_df.columns:
                risk_df = inventory_df.nsmallest(10, 'stock_on_hand')[[sku_col, 'store_id', 'stock_on_hand']].copy()
                risk_df['risk_level'] = risk_df['stock_on_hand'].apply(
                    lambda x: 'Critical' if x < 5 else ('High' if x < 10 else 'Medium')
                )
                
                fig = px.bar(
                    risk_df, 
                    x=sku_col, 
                    y='stock_on_hand', 
                    title='', 
                    color='risk_level',
                    color_discrete_map={'Critical': t['accent_red'], 'High': t['accent_orange'], 'Medium': t['accent_blue']}
                )
                fig = style_plotly_chart_themed(fig)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("SKU column not found")
        else:
            st.info("Stock data not available")
    
    with col2:
        st.markdown("#### 📋 Issues Pareto")
        local_filters_4 = show_chart_filter('mgr_issues', [])
        
        if st.session_state.is_cleaned and st.session_state.issues_df is not None:
            issues_df = st.session_state.issues_df
            if len(issues_df) > 0 and 'issue_type' in issues_df.columns:
                issue_counts = issues_df['issue_type'].value_counts().head(10).reset_index()
                issue_counts.columns = ['issue_type', 'count']
                issue_counts = issue_counts[issue_counts['issue_type'] != 'None']
                
                if len(issue_counts) > 0:
                    # Add cumulative for Pareto
                    total = issue_counts['count'].sum()
                    issue_counts['cumulative_pct'] = (issue_counts['count'].cumsum() / total * 100)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=issue_counts['issue_type'],
                        y=issue_counts['count'],
                        name='Count',
                        marker_color=t['accent_cyan']
                    ))
                    fig.add_trace(go.Scatter(
                        x=issue_counts['issue_type'],
                        y=issue_counts['cumulative_pct'],
                        name='Cumulative %',
                        yaxis='y2',
                        mode='lines+markers',
                        line=dict(color=t['accent_pink'], width=3)
                    ))
                    fig.update_layout(
                        yaxis2=dict(overlaying='y', side='right', range=[0, 105]),
                        title=''
                    )
                    fig = style_plotly_chart_themed(fig)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No issues to display")
            else:
                st.info("No issues logged")
        else:
            st.info("Clean data first to see issues Pareto")
    
    st.markdown("---")
    
    # Top 10 Risk Table
    st.markdown(f'<p class="section-title section-title-orange">🚨 Top 10 Stockout Risk Items (Sortable Table)</p>', unsafe_allow_html=True)
    
    if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
        sku_col = 'sku' if 'sku' in inventory_df.columns else 'product_id'
        if sku_col in inventory_df.columns:
            risk_table = inventory_df.nsmallest(10, 'stock_on_hand').copy()
            
            if 'store_id' in risk_table.columns and stores_df is not None and 'store_id' in stores_df.columns:
                store_cols = ['store_id']
                if 'city' in stores_df.columns:
                    store_cols.append('city')
                if 'channel' in stores_df.columns:
                    store_cols.append('channel')
                risk_table = risk_table.merge(stores_df[store_cols], on='store_id', how='left')
            
            risk_table['Risk Level'] = risk_table['stock_on_hand'].apply(
                lambda x: '🔴 Critical' if x < 5 else ('🟠 High' if x < 10 else '🟡 Medium')
            )
            
            display_cols = [col for col in [sku_col, 'store_id', 'city', 'channel', 'stock_on_hand', 'Risk Level'] if col in risk_table.columns]
            st.dataframe(risk_table[display_cols], use_container_width=True)
        else:
            st.info("SKU column not found")
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
    
    margin = kpis.get('gross_margin_pct', 0)
    if margin < 20:
        recommendations.append(f"📉 **Margin Alert**: Gross margin at {margin:.1f}% is below target (20%). Consider reducing discounts or reviewing supplier costs.")
    elif margin > 35:
        recommendations.append(f"📈 **Strong Margins**: Gross margin at {margin:.1f}% is healthy. Opportunity to invest in growth initiatives.")
    else:
        recommendations.append(f"✅ **Healthy Margins**: Gross margin at {margin:.1f}% is within target range.")
    
    avg_discount = kpis.get('avg_discount_pct', 0)
    if avg_discount > 15:
        recommendations.append(f"💸 **High Discounting**: Average discount at {avg_discount:.1f}%. Evaluate if promotions are driving profitable growth or eroding margins.")
    
    if city_kpis is not None and len(city_kpis) > 0:
        top_city = city_kpis.iloc[0]['city']
        top_revenue = city_kpis.iloc[0]['revenue']
        recommendations.append(f"🏙️ **Top Market**: {top_city} leads with {format_currency(top_revenue)} revenue. Consider increasing investment in this market.")
    
    if channel_kpis is not None and len(channel_kpis) > 0:
        top_channel = channel_kpis.iloc[0]['channel']
        recommendations.append(f"📱 **Channel Focus**: {top_channel} is the top performing channel. Optimize marketing spend and inventory allocation here.")
    
    if category_kpis is not None and len(category_kpis) > 0:
        if 'margin_pct' in category_kpis.columns:
            best_margin_cat = category_kpis.loc[category_kpis['margin_pct'].idxmax()]
            recommendations.append(f"📦 **Best Margin Category**: {best_margin_cat['category']} has {best_margin_cat['margin_pct']:.1f}% margin. Push promotions here for profitable growth.")
    
    return recommendations


# ============================================================================
# PAGE: SIMULATOR (COMPLETE WITH ALL REQUIREMENTS)
# ============================================================================

def show_simulator_page():
    """Display the simulator page with all required inputs and constraints."""
    t = get_theme()
    
    st.markdown(f'<h1 class="page-title page-title-orange">🎯 Promo Pulse Simulator</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-description">Run what-if scenarios with budget, margin, and stock constraints</p>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card_3d("Please load data first. Go to 📂 Data page."), unsafe_allow_html=True)
        show_footer()
        return
    
    st.markdown("---")
    
    # Get current data
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    inventory_df = st.session_state.clean_inventory if st.session_state.is_cleaned else st.session_state.raw_inventory
    
    filtered_sales = apply_global_filters(sales_df, stores_df, products_df)
    
    # =========================================================================
    # SIMULATION PARAMETERS (ALL REQUIRED INPUTS)
    # =========================================================================
    
    st.markdown(f'<p class="section-title section-title-cyan">🎛️ Simulation Parameters</p>', unsafe_allow_html=True)
    
    # Row 1: Core simulation inputs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        discount_pct = st.slider(
            "💸 Discount %",
            min_value=0,
            max_value=50,
            value=10,
            step=5,
            help="Promotional discount percentage to simulate"
        )
    
    with col2:
        promo_budget = st.number_input(
            "💰 Promo Budget (AED)",
            min_value=0,
            max_value=10000000,
            value=500000,
            step=50000,
            help="Maximum promotional spend allowed"
        )
    
    with col3:
        margin_floor = st.slider(
            "📊 Margin Floor %",
            min_value=0,
            max_value=50,
            value=15,
            step=1,
            help="Minimum acceptable gross margin percentage"
        )
    
    # Row 2: Additional parameters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        simulation_days = st.radio(
            "📅 Simulation Window",
            options=[7, 14],
            index=1,
            horizontal=True,
            help="Number of days to simulate"
        )
    
    with col2:
        # Optional: City focus
        city_options = ['All']
        if stores_df is not None and 'city' in stores_df.columns:
            city_options += sorted(stores_df['city'].dropna().unique().tolist())
        sim_city = st.selectbox("🏙️ City Focus", options=city_options, help="Focus simulation on specific city")
    
    with col3:
        # Optional: Category focus
        category_options = ['All']
        if products_df is not None and 'category' in products_df.columns:
            category_options += sorted(products_df['category'].dropna().unique().tolist())
        sim_category = st.selectbox("📦 Category Focus", options=category_options, help="Focus simulation on specific category")
    
    st.markdown("---")
    
    # Run Simulation Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        run_simulation = st.button("🚀 Run Simulation", use_container_width=True, type="primary")
    
    if run_simulation:
        with st.spinner("🔄 Running simulation..."):
            sim = Simulator()
            
            # Run simulation
            results = sim.simulate_scenario(
                sales_df=filtered_sales,
                products_df=products_df,
                stores_df=stores_df,
                inventory_df=inventory_df,
                discount_pct=discount_pct,
                promo_budget=promo_budget,
                margin_floor=margin_floor,
                simulation_days=simulation_days
            )
            
            st.session_state.last_simulation = results
    
    # Display results if available
    if st.session_state.get('last_simulation'):
        results = st.session_state.last_simulation
        
        st.markdown("---")
        st.markdown(f'<p class="section-title section-title-purple">📊 Simulation Results</p>', unsafe_allow_html=True)
        
        # KPI Cards Row 1
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card_3d(
                "Simulated Revenue",
                format_currency(results['simulated_revenue']),
                delta=f"{results['revenue_change_pct']:+.1f}%",
                delta_type="positive" if results['revenue_change_pct'] >= 0 else "negative",
                color="cyan"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_metric_card_3d(
                "Promo Spend",
                format_currency(results['promo_spend']),
                color="orange"
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_metric_card_3d(
                "Profit Proxy",
                format_currency(results['profit_proxy']),
                color="green"
            ), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_metric_card_3d(
                "Budget Utilization",
                f"{results['budget_utilization_pct']:.1f}%",
                color="purple"
            ), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # KPI Cards Row 2
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card_3d(
                "Simulated Margin %",
                f"{results['simulated_margin_pct']:.1f}%",
                delta=f"{results['margin_change_pct']:+.1f}%",
                delta_type="positive" if results['margin_change_pct'] >= 0 else "negative",
                color="teal"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_metric_card_3d(
                "Demand Uplift",
                f"{results['demand_uplift_pct']:.1f}%",
                color="blue"
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_metric_card_3d(
                "Simulated Demand",
                f"{results['simulated_demand']:,.0f} units",
                color="pink"
            ), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_metric_card_3d(
                "Simulation Days",
                f"{results['simulation_days']} days",
                color="cyan"
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # =====================================================================
        # CONSTRAINT CHECKS (REQUIRED)
        # =====================================================================
        
        st.markdown(f'<p class="section-title section-title-orange">⚠️ Constraint Validation</p>', unsafe_allow_html=True)
        
        constraints = results['constraints']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if constraints['budget_ok']:
                st.markdown(create_success_card_3d(
                    f"**Budget Constraint**: {format_currency(results['promo_spend'])} ≤ {format_currency(promo_budget)}"
                ), unsafe_allow_html=True)
            else:
                st.markdown(create_error_card_3d(
                    f"**Budget Exceeded**: {format_currency(results['promo_spend'])} > {format_currency(promo_budget)}"
                ), unsafe_allow_html=True)
        
        with col2:
            if constraints['margin_ok']:
                st.markdown(create_success_card_3d(
                    f"**Margin Floor**: {results['simulated_margin_pct']:.1f}% ≥ {margin_floor}%"
                ), unsafe_allow_html=True)
            else:
                st.markdown(create_error_card_3d(
                    f"**Margin Below Floor**: {results['simulated_margin_pct']:.1f}% < {margin_floor}%"
                ), unsafe_allow_html=True)
        
        with col3:
            if constraints['stock_ok']:
                st.markdown(create_success_card_3d(
                    f"**Stock Constraint**: Demand within available inventory"
                ), unsafe_allow_html=True)
            else:
                st.markdown(create_error_card_3d(
                    f"**Stock Shortage**: {results['stock_shortage']:,.0f} units short"
                ), unsafe_allow_html=True)
        
        # Show top stockout items if constraint violated
        if not constraints['stock_ok'] and results.get('top_stockout_items'):
            st.markdown("---")
            st.markdown(f'<p class="section-title section-title-red">🚨 Top 10 Stockout Risk Items (Contributors)</p>', unsafe_allow_html=True)
            
            stockout_df = pd.DataFrame(results['top_stockout_items'])
            st.dataframe(stockout_df, use_container_width=True)
        
        st.markdown("---")
        
        # =====================================================================
        # SCENARIO COMPARISON CHARTS
        # =====================================================================
        
        st.markdown(f'<p class="section-title section-title-teal">📈 Scenario Impact Visualization</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Before/After Revenue Comparison
            comparison_data = pd.DataFrame({
                'Metric': ['Revenue', 'Revenue'],
                'State': ['Baseline', 'Simulated'],
                'Value': [results['baseline_revenue'], results['simulated_revenue']]
            })
            
            fig = px.bar(
                comparison_data, 
                x='State', 
                y='Value', 
                color='State', 
                title='Revenue: Baseline vs Simulated',
                color_discrete_sequence=[t['accent_blue'], t['accent_cyan']]
            )
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Margin Comparison
            margin_data = pd.DataFrame({
                'Metric': ['Margin %', 'Margin %'],
                'State': ['Baseline', 'Simulated'],
                'Value': [results['baseline_margin_pct'], results['simulated_margin_pct']]
            })
            
            fig = px.bar(
                margin_data, 
                x='State', 
                y='Value', 
                color='State', 
                title='Margin %: Baseline vs Simulated',
                color_discrete_sequence=[t['accent_purple'], t['accent_pink']]
            )
            
            # Add margin floor line
            fig.add_hline(
                y=margin_floor, 
                line_dash="dash", 
                line_color=t['accent_red'],
                annotation_text=f"Margin Floor: {margin_floor}%"
            )
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Scenario Impact Chart (Profit vs Discount) - Multi-scenario
        st.markdown("#### 📊 Scenario Impact: Profit Proxy vs Discount Level")
        
        # Simulate multiple discount levels
        sim = Simulator()
        scenario_results = []
        
        for disc in [0, 5, 10, 15, 20, 25, 30]:
            sim_result = sim.simulate_scenario(
                sales_df=filtered_sales,
                products_df=products_df,
                stores_df=stores_df,
                inventory_df=inventory_df,
                discount_pct=disc,
                promo_budget=promo_budget,
                margin_floor=margin_floor,
                simulation_days=simulation_days
            )
            scenario_results.append({
                'Discount %': disc,
                'Profit Proxy': sim_result['profit_proxy'],
                'Margin %': sim_result['simulated_margin_pct'],
                'Revenue': sim_result['simulated_revenue'],
                'Constraint OK': '✅' if sim_result['constraints']['all_ok'] else '❌'
            })
        
        scenario_df = pd.DataFrame(scenario_results)
        
        fig = go.Figure()
        
        # Profit line
        fig.add_trace(go.Scatter(
            x=scenario_df['Discount %'],
            y=scenario_df['Profit Proxy'],
            name='Profit Proxy',
            mode='lines+markers',
            line=dict(color=t['accent_green'], width=3),
            marker=dict(size=10)
        ))
        
        # Revenue line
        fig.add_trace(go.Scatter(
            x=scenario_df['Discount %'],
            y=scenario_df['Revenue'],
            name='Revenue',
            mode='lines+markers',
            line=dict(color=t['accent_cyan'], width=3),
            marker=dict(size=10),
            yaxis='y2'
        ))
        
        # Highlight current scenario
        fig.add_vline(
            x=discount_pct, 
            line_dash="dash", 
            line_color=t['accent_pink'],
            annotation_text=f"Current: {discount_pct}%"
        )
        
        fig.update_layout(
            title='Profit Proxy & Revenue vs Discount Level',
            xaxis_title='Discount %',
            yaxis=dict(title='Profit Proxy (AED)', side='left'),
            yaxis2=dict(title='Revenue (AED)', side='right', overlaying='y')
        )
        fig = style_plotly_chart_themed(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        # Scenario comparison table
        st.markdown("#### 📋 Scenario Comparison Table")
        st.dataframe(scenario_df, use_container_width=True)
        
        st.markdown("---")
        
        # =====================================================================
        # DEMAND UPLIFT LOGIC EXPLANATION
        # =====================================================================
        
        st.markdown(f'<p class="section-title section-title-blue">📖 Demand Uplift Logic (Rule-Based)</p>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="card-3d">
            <h4 style="color: {t['accent_cyan']}; margin-bottom: 15px;">How Demand Uplift is Calculated</h4>
            <p style="color: {t['text_primary']}; line-height: 1.8;">
                This simulator uses a <strong>rule-based</strong> approach (no ML/DL) with the following logic:
            </p>
            <ul style="color: {t['text_primary']}; line-height: 2;">
                <li><strong>Base Elasticity:</strong> 1% discount → 0.5% demand increase</li>
                <li><strong>Channel Multipliers:</strong> Marketplace (1.4x), App (1.2x), Web (1.0x)</li>
                <li><strong>Category Multipliers:</strong> Electronics (1.5x), Fashion (1.3x), Beauty (1.2x), Home (1.1x), Grocery (0.9x)</li>
            </ul>
            <p style="color: {t['text_secondary']}; font-style: italic; margin-top: 15px;">
                Example: A 10% discount on Electronics via Marketplace would yield: 10 × 0.5 × 1.5 × 1.4 = 10.5% demand uplift
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Insights
        st.markdown(f'<p class="section-title section-title-green">💡 Simulation Insights</p>', unsafe_allow_html=True)
        
        insights = []
        
        if constraints['all_ok']:
            insights.append(f"✅ **All Constraints Met**: This scenario is viable for implementation.")
        else:
            if not constraints['budget_ok']:
                insights.append(f"❌ **Budget Exceeded**: Reduce discount or scope to stay within budget.")
            if not constraints['margin_ok']:
                insights.append(f"❌ **Margin Too Low**: This discount level erodes margins below acceptable floor.")
            if not constraints['stock_ok']:
                insights.append(f"❌ **Stock Insufficient**: Expected demand exceeds inventory. Consider replenishment or limiting scope.")
        
        if results['revenue_change_pct'] > 5:
            insights.append(f"📈 **Positive Revenue Impact**: This scenario could increase revenue by {results['revenue_change_pct']:.1f}%")
        elif results['revenue_change_pct'] < -5:
            insights.append(f"📉 **Revenue Risk**: This scenario may decrease revenue by {abs(results['revenue_change_pct']):.1f}%")
        
        if results['profit_proxy'] > results['baseline_revenue'] * 0.15:
            insights.append(f"💰 **Strong Profit Potential**: Profit proxy of {format_currency(results['profit_proxy'])} is healthy.")
        
        for insight in insights:
            st.markdown(create_info_card_3d(insight), unsafe_allow_html=True)
    
    else:
        st.info("👆 Configure parameters and click 'Run Simulation' to see results")
    
    show_footer()


# ============================================================================
# MAIN SIDEBAR
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
    
    # Title color: White for dark theme, Black for light theme
    title_color = "#FFFFFF" if st.session_state.theme == 'dark' else "#000000"
    
    st.markdown(f"""
    <div style="text-align: center; margin-top: 10px; padding-bottom: 15px;">
        <div style="font-size: 48px; margin-bottom: 5px;">🛒</div>
        <div style="
            font-size: 26px;
            font-weight: 800;
            color: {title_color};
        ">UAE Pulse</div>
        <div style="color: {t['text_secondary']}; font-size: 13px; font-weight: 500;">Promo Simulator + Data Rescue</div>
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
        st.markdown(f'<p style="color: {t["accent_purple"]}; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📈 QUICK STATS</p>', unsafe_allow_html=True)
        
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
                    <span style="color: {t['accent_green']}; font-weight: 700; font-size: 1.2rem;">{format_currency(total_revenue)}</span>
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
