
# ============================================================================
# UAE Pulse Simulator + Data Rescue Dashboard
# Main Streamlit Application - RESTORED v2.0 + FIXES
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from modules.validator import FileValidator

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
    page_title="UAE Pulse Simulator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ENHANCED CSS - ALL FIXES APPLIED
# ============================================================================

st.markdown("""
<style>
    /* ===== IMPORTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* ===== CSS VARIABLES ===== */
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-card: #16161f;
        --bg-card-hover: #1e1e2d;
        
        --accent-cyan: #06b6d4;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-pink: #ec4899;
        --accent-green: #10b981;
        --accent-orange: #f59e0b;
        --accent-red: #ef4444;
        --accent-teal: #14b8a6;
        
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        
        --border-color: #2d2d3a;
    }
    
    /* ===== ANIMATIONS ===== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 20px rgba(6, 182, 212, 0.3); }
        50% { box-shadow: 0 0 40px rgba(6, 182, 212, 0.6); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* ===== HIDE STREAMLIT DEFAULTS ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ===== ENHANCED MAIN BACKGROUND ===== */
    .stApp {
        background: 
            radial-gradient(ellipse at top left, rgba(6, 182, 212, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at top right, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at bottom left, rgba(236, 72, 153, 0.05) 0%, transparent 50%),
            radial-gradient(ellipse at bottom right, rgba(59, 130, 246, 0.05) 0%, transparent 50%),
            linear-gradient(180deg, #0a0a0f 0%, #0d0d14 25%, #0f0f18 50%, #0d0d14 75%, #0a0a0f 100%);
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
    }
    
    /* ===== SIDEBAR STYLING ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d14 0%, #0f0f18 50%, #0a0a0f 100%);
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 2px;
        height: 100%;
        background: linear-gradient(180deg, var(--accent-cyan), var(--accent-purple), var(--accent-pink));
        opacity: 0.6;
    }
    
    /* ===== FIX: HEADINGS - NO BOX ===== */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        background: none !important;
        -webkit-background-clip: unset !important;
        background-clip: unset !important;
    }
    
    /* ===== HERO SECTION ===== */
    .hero-container {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.12) 0%, rgba(139, 92, 246, 0.12) 50%, rgba(236, 72, 153, 0.12) 100%);
        border-radius: 24px;
        padding: 60px 50px;
        margin-bottom: 40px;
        border: 1px solid rgba(6, 182, 212, 0.3);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 50%);
        animation: float 6s ease-in-out infinite;
    }
    
    /* ===== FIX: HERO TITLE - MUCH BIGGER ===== */
    .hero-title {
        font-size: 4rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #ffffff 0%, #06b6d4 40%, #8b5cf6 70%, #ec4899 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 20px;
        position: relative;
        z-index: 1;
        line-height: 1.2;
        animation: gradientShift 4s ease infinite;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: var(--text-secondary);
        margin-bottom: 30px;
        position: relative;
        z-index: 1;
        line-height: 1.6;
    }
    
    .hero-badge {
        display: inline-block;
        padding: 10px 24px;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
        border-radius: 50px;
        color: white;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 20px;
        animation: pulse 2s infinite;
    }
    
    /* ===== FIX: PAGE TITLES - BIGGER FOR PROJECTOR ===== */
    .page-title {
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
        line-height: 1.2;
    }
    
    .page-title-cyan { color: #06b6d4 !important; }
    .page-title-blue { color: #3b82f6 !important; }
    .page-title-purple { color: #8b5cf6 !important; }
    .page-title-pink { color: #ec4899 !important; }
    .page-title-green { color: #10b981 !important; }
    .page-title-teal { color: #14b8a6 !important; }
    .page-title-orange { color: #f59e0b !important; }
    
    .page-description {
        color: var(--text-secondary);
        font-size: 1.15rem;
        margin-bottom: 25px;
    }
    
    /* ===== SECTION TITLES - BIGGER ===== */
    .section-title {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        margin-bottom: 20px !important;
    }
    
    .section-title-cyan { color: #06b6d4 !important; }
    .section-title-blue { color: #3b82f6 !important; }
    .section-title-purple { color: #8b5cf6 !important; }
    .section-title-pink { color: #ec4899 !important; }
    .section-title-green { color: #10b981 !important; }
    .section-title-teal { color: #14b8a6 !important; }
    .section-title-orange { color: #f59e0b !important; }
    
    /* ===== FIX: METRIC CARDS - EXACT UNIFORM SIZE ===== */
    .metric-card {
        background: linear-gradient(145deg, #16161f 0%, #1a1a24 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        height: 140px !important;
        min-height: 140px !important;
        max-height: 140px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
        box-sizing: border-box;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        border-color: var(--accent-cyan);
        box-shadow: 0 12px 40px rgba(6, 182, 212, 0.2);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 8px 0;
    }
    
    .metric-value-cyan { color: #06b6d4; }
    .metric-value-blue { color: #3b82f6; }
    .metric-value-purple { color: #8b5cf6; }
    .metric-value-pink { color: #ec4899; }
    .metric-value-green { color: #10b981; }
    .metric-value-orange { color: #f59e0b; }
    .metric-value-teal { color: #14b8a6; }
    
    .metric-delta-positive {
        color: var(--accent-green);
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    .metric-delta-negative {
        color: var(--accent-red);
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* ===== FIX: FEATURE CARDS - EXACT UNIFORM SIZE ===== */
    .feature-card {
        background: linear-gradient(145deg, #16161f 0%, #1a1a24 100%);
        border-radius: 20px;
        padding: 35px 25px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        height: 220px !important;
        min-height: 220px !important;
        max-height: 220px !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-sizing: border-box;
    }
    
    .feature-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-12px) scale(1.02);
        border-color: transparent;
        box-shadow: 0 20px 50px rgba(6, 182, 212, 0.15);
    }
    
    .feature-card:hover::after {
        opacity: 1;
    }
    
    .feature-card-cyan:hover { box-shadow: 0 20px 50px rgba(6, 182, 212, 0.2); border-color: var(--accent-cyan); }
    .feature-card-blue:hover { box-shadow: 0 20px 50px rgba(59, 130, 246, 0.2); border-color: var(--accent-blue); }
    .feature-card-purple:hover { box-shadow: 0 20px 50px rgba(139, 92, 246, 0.2); border-color: var(--accent-purple); }
    .feature-card-pink:hover { box-shadow: 0 20px 50px rgba(236, 72, 153, 0.2); border-color: var(--accent-pink); }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 20px;
        animation: float 3s ease-in-out infinite;
    }
    
    .feature-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 10px;
    }
    
    .feature-title-cyan { color: var(--accent-cyan); }
    .feature-title-blue { color: var(--accent-blue); }
    .feature-title-purple { color: var(--accent-purple); }
    .feature-title-pink { color: var(--accent-pink); }
    
    .feature-desc {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* ===== INFO/SUCCESS/WARNING/ERROR CARDS ===== */
    .info-card {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
        border-radius: 12px;
        padding: 20px 25px;
        border-left: 4px solid var(--accent-cyan);
        margin: 15px 0;
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateX(8px);
        box-shadow: 0 4px 20px rgba(6, 182, 212, 0.15);
    }
    
    .success-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(20, 184, 166, 0.1) 100%);
        border-radius: 12px;
        padding: 20px 25px;
        border-left: 4px solid var(--accent-green);
        margin: 15px 0;
        color: #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .success-card:hover {
        transform: translateX(8px);
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.15);
    }
    
    .warning-card {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 146, 60, 0.1) 100%);
        border-radius: 12px;
        padding: 20px 25px;
        border-left: 4px solid var(--accent-orange);
        margin: 15px 0;
        color: #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .warning-card:hover {
        transform: translateX(8px);
        box-shadow: 0 4px 20px rgba(245, 158, 11, 0.15);
    }
    
    .error-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
        border-radius: 12px;
        padding: 20px 25px;
        border-left: 4px solid var(--accent-red);
        margin: 15px 0;
        color: #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .error-card:hover {
        transform: translateX(8px);
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.15);
    }
    
    /* ===== INSIGHT CARD ===== */
    .insight-card {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.12) 0%, rgba(236, 72, 153, 0.12) 100%);
        border-radius: 12px;
        padding: 20px 25px;
        border: 1px solid rgba(139, 92, 246, 0.3);
        margin: 15px 0;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        transform: translateX(8px);
        border-color: #8b5cf6;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.2);
    }
    
    .insight-title {
        color: #a78bfa;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 10px;
    }
    
    .insight-text {
        color: #e2e8f0;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* ===== FIX: SUB-TABS - WITH HOVER EFFECT ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(145deg, #16161f 0%, #1a1a24 100%);
        border-radius: 12px;
        color: var(--text-secondary);
        padding: 12px 24px;
        border: 1px solid var(--border-color);
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    /* HOVER EFFECT FOR SUB-TABS */
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(145deg, #1a1a24 0%, #1e1e2d 100%);
        border-color: var(--accent-cyan);
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.15);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);
    }
    
    .stTabs [aria-selected="true"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(6, 182, 212, 0.5);
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 32px;
        font-weight: 600;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.4);
        transform: translateY(-3px);
    }
    
    /* ===== FOOTER ===== */
    .footer {
        background: linear-gradient(135deg, #0f0f18 0%, #12121a 100%);
        padding: 35px;
        text-align: center;
        border-top: 1px solid var(--border-color);
        margin-top: 60px;
        border-radius: 20px 20px 0 0;
        position: relative;
        overflow: hidden;
    }
    
    .footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple), var(--accent-pink));
    }
    
    .footer-title {
        color: var(--text-primary);
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 10px;
    }
    
    .footer-subtitle {
        color: var(--text-muted);
        font-size: 0.95rem;
        margin-bottom: 12px;
    }
    
    .footer-names {
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    /* ===== DIVIDER ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 30px 0;
    }
    
    /* ===== SLIDER ===== */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue)) !important;
    }
    
    /* ===== SELECTBOX ===== */
    .stSelectbox > div > div {
        background-color: var(--bg-card);
        border-color: var(--border-color);
        border-radius: 10px;
    }
    
</style>
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
def format_currency(value):
    """Format large currency values for display.
    Examples:
        1,500 → AED 1.5K
        28,469,655 → AED 28.5M
        1,200,000,000 → AED 1.2B
    """
    if value is None:
        return "AED 0"
    
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 1_000_000_000:  # Billions
        return f"{sign}AED {abs_value / 1_000_000_000:.1f}B"
    elif abs_value >= 1_000_000:  # Millions
        return f"{sign}AED {abs_value / 1_000_000:.1f}M"
    elif abs_value >= 1_000:  # Thousands
        return f"{sign}AED {abs_value / 1_000:.1f}K"
    else:
        return f"{sign}AED {abs_value:,.0f}"
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
def get_theme_colors():
    """Return theme colors for consistent styling."""
    return {
        'chart_bg': 'rgba(0,0,0,0)',
        'chart_text': '#e2e8f0',
        'chart_grid': '#334155',
        'cyan': '#06b6d4',
        'purple': '#8b5cf6',
        'pink': '#ec4899',
        'green': '#10b981',
        'orange': '#f59e0b',
        'red': '#ef4444',
        'blue': '#3b82f6',
        'teal': '#14b8a6'
    }


def style_plotly_chart_themed(fig, height=400):
    """Apply consistent theme styling to Plotly charts."""
    colors = get_theme_colors()
    fig.update_layout(
        paper_bgcolor=colors['chart_bg'],
        plot_bgcolor=colors['chart_bg'],
        font=dict(color=colors['chart_text'], family='Inter, sans-serif'),
        height=height,
        margin=dict(l=20, r=20, t=60, b=40)
    )
    fig.update_xaxes(gridcolor=colors['chart_grid'])
    fig.update_yaxes(gridcolor=colors['chart_grid'])
    return fig

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
        insights.append(("Excellent Quality", f"Low return rate of {return_rate:.1f}% indicates high customer satisfaction_taken."))
    
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
    # Title with NO empty space
    st.markdown("""
    <div style="text-align: center; margin-top: -20px; padding-bottom: 15px;">
        <div style="font-size: 48px; margin-bottom: 5px;">🛒</div>
        <div style="
            font-size: 26px;
            font-weight: 800;
            background: linear-gradient(135deg, #06b6d4, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">UAE Pulse</div>
        <div style="color: #94a3b8; font-size: 13px;">Simulator + Data Rescue</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown('<p style="color: #ec4899; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📍 NAVIGATION</p>', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📂 Data", "🧹 Cleaner", "📊 Dashboard", "🎯 Simulator"],
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
    
    # Footer
    st.markdown("---")
    st.markdown('<p style="color: #3b82f6; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">🔬 TECH</p>', unsafe_allow_html=True)
    st.markdown("""
    <div style="color: #64748b; font-size: 11px; line-height: 1.6;">
        Python • Pandas • Plotly • Streamlit
    </div>
    """, unsafe_allow_html=True)
    
   # ===== DOWNLOAD CLEANED FILES =====
    if st.session_state.data_loaded and st.session_state.is_cleaned:
        st.markdown("---")
        st.markdown('<p style="color: #10b981; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📥 DOWNLOAD CLEANED FILES</p>', unsafe_allow_html=True)
        
        import io
        import zipfile
        
        # Create ZIP file with all cleaned CSVs
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            if st.session_state.clean_products is not None:
                zip_file.writestr("cleaned_products.csv", st.session_state.clean_products.to_csv(index=False))
            if st.session_state.clean_stores is not None:
                zip_file.writestr("cleaned_stores.csv", st.session_state.clean_stores.to_csv(index=False))
            if st.session_state.clean_sales is not None:
                zip_file.writestr("cleaned_sales.csv", st.session_state.clean_sales.to_csv(index=False))
            if st.session_state.clean_inventory is not None:
                zip_file.writestr("cleaned_inventory.csv", st.session_state.clean_inventory.to_csv(index=False))
        
        zip_buffer.seek(0)
        
        st.download_button(
            label="📦 Download All Cleaned Files (ZIP)",
            data=zip_buffer,
            file_name="cleaned_data.zip",
            mime="application/zip"
        )
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
            
            formatted_revenue = format_currency(total_revenue)
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #16161f 0%, #1a1a24 100%);
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #2d2d3a;
            ">
                <div style="margin-bottom: 12px;">
                    <span style="color: #64748b; font-size: 0.8rem; text-transform: uppercase;">records</span><br>
                    <span style="color: #06b6d4; font-weight: 700; font-size: 1.4rem;">{total_records:,}</span>
                </div>
                <div>
                    <span style="color: #64748b; font-size: 0.8rem; text-transform: uppercase;">REVENUE</span><br>
                    <span style="color: #10b981; font-weight: 700; font-size: 1.2rem;">{formatted_revenue}</span>
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
                'date': ['date', 'Date', 'transaction_taken_date', 'sale_date', 'order_date'],
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
            Transform your e-commerce data into action_takenable insights.<br>
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
                <li>Duplicate record_identifier removal</li>
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
    
def show_dashboard_page():
# Custom CSS for large tab buttons
    st.markdown("""
    <style>
    div[data-testid="stButton"] button {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        padding: 30px 20px !important;
        min-height: 140px !important;
        white-space: pre-wrap !important;
        text-align: center !important;
        line-height: 2.2 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.3), rgba(59, 130, 246, 0.3)) !important;
        border: 2px solid #06b6d4 !important;
        color: #ffffff !important;
    }
    div[data-testid="stButton"] button[kind="secondary"] {
        background: rgba(100, 116, 139, 0.15) !important;
        border: 1px solid #475569 !important;
        color: #94a3b8 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="page-title page-title-cyan">📊 Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Business performance insights and operational metrics</p>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card("Please load data first. Go to 📂 Data page."), unsafe_allow_html=True)
        show_footer()
        return
    
    # Get raw or cleaned data
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    inventory_df = st.session_state.clean_inventory if st.session_state.is_cleaned else st.session_state.raw_inventory
    
    if sales_df is None:
        st.markdown(create_warning_card("No sales data available."), unsafe_allow_html=True)
        show_footer()
        return
    
    st.markdown("---")
    
    # ===== GLOBAL FILTERS SECTION =====
    st.markdown('<p class="section-title section-title-blue">🎛️ Global Filters</p>', unsafe_allow_html=True)
    st.caption("💡 Leave empty to include all")
    
    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)
    
    # Date Range Filter
    with filter_col1:
        date_range = None
        if 'order_time' in sales_df.columns:
            try:
                sales_df['order_time'] = pd.to_datetime(sales_df['order_time'], errors='coerce')
                valid_dates = sales_df['order_time'].dropna()
                if len(valid_dates) > 0:
                    min_date = valid_dates.min().date()
                    max_date = valid_dates.max().date()
                    date_range = st.date_input(
                        "📅 Date Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        key="global_date_filter"
                    )
            except:
                st.caption("Date filter unavailable")
    
    # City Filter
    with filter_col2:
        all_cities = []
        selected_cities = []
        if stores_df is not None and 'city' in stores_df.columns:
            all_cities = sorted(stores_df['city'].dropna().unique().tolist())
            
            selected_cities = st.multiselect(
                "🏙️ City",
                options=all_cities,
                default=[],
                placeholder="All Cities",
                key="global_city_filter"
            )
            
            if len(selected_cities) == 0:
                selected_cities = all_cities
    
    # Channel Filter
    with filter_col3:
        all_channels = []
        selected_channels = []
        if stores_df is not None and 'channel' in stores_df.columns:
            all_channels = sorted(stores_df['channel'].dropna().unique().tolist())
            
            selected_channels = st.multiselect(
                "📱 Channel",
                options=all_channels,
                default=[],
                placeholder="All Channels",
                key="global_channel_filter"
            )
            
            if len(selected_channels) == 0:
                selected_channels = all_channels
    
    # Category Filter
    with filter_col4:
        all_categories = []
        selected_categories = []
        if products_df is not None and 'category' in products_df.columns:
            all_categories = sorted(products_df['category'].dropna().unique().tolist())
            
            selected_categories = st.multiselect(
                "📦 Category",
                options=all_categories,
                default=[],
                placeholder="All Categories",
                key="global_category_filter"
            )
            
            if len(selected_categories) == 0:
                selected_categories = all_categories
                # Brand Filter
    with filter_col5:
        all_brands = []
        selected_brands = []
        if products_df is not None and 'brand' in products_df.columns:
            all_brands = sorted(products_df['brand'].dropna().unique().tolist())
            
            selected_brands = st.multiselect(
                "🏷️ Brand",
                options=all_brands,
                default=[],
                placeholder="All Brands",
                key="global_brand_filter"
            )
            
            if len(selected_brands) == 0:
                selected_brands = all_brands
        else:
            selected_brands = []
    
# ===== APPLY FILTERS =====
    filtered_sales = sales_df.copy()
    filtered_stores = stores_df.copy() if stores_df is not None else None
    filtered_products = products_df.copy() if products_df is not None else None
    filtered_inventory = inventory_df.copy() if inventory_df is not None else None
    
    # Apply date filter
    if date_range and len(date_range) == 2 and 'order_time' in filtered_sales.columns:
        start_date, end_date = date_range
        filtered_sales = filtered_sales[
            (filtered_sales['order_time'].dt.date >= start_date) &
            (filtered_sales['order_time'].dt.date <= end_date)
        ]
    
    # Apply city/channel filter via stores
    if filtered_stores is not None:
        if selected_cities:
            filtered_stores = filtered_stores[filtered_stores['city'].isin(selected_cities)]
        if selected_channels:
            filtered_stores = filtered_stores[filtered_stores['channel'].isin(selected_channels)]
        
        # Filter sales by valid stores
        if 'store_id' in filtered_sales.columns and 'store_id' in filtered_stores.columns:
            valid_store_ids = filtered_stores['store_id'].unique()
            filtered_sales = filtered_sales[filtered_sales['store_id'].isin(valid_store_ids)]
    
    # Apply category filter via products
    if filtered_products is not None and selected_categories:
        filtered_products = filtered_products[filtered_products['category'].isin(selected_categories)]
    
    # Apply brand filter via products
    if filtered_products is not None and selected_brands and 'brand' in filtered_products.columns:
        filtered_products = filtered_products[filtered_products['brand'].isin(selected_brands)]
    
    # Filter sales by valid products (after category AND brand filters)
    if filtered_products is not None:
        if 'sku' in filtered_sales.columns and 'sku' in filtered_products.columns:
            valid_skus = filtered_products['sku'].unique()
            filtered_sales = filtered_sales[filtered_sales['sku'].isin(valid_skus)]
    
    # Filter inventory by valid stores and products
    if filtered_inventory is not None:
        if filtered_stores is not None and 'store_id' in filtered_inventory.columns:
            valid_store_ids = filtered_stores['store_id'].unique()
            filtered_inventory = filtered_inventory[filtered_inventory['store_id'].isin(valid_store_ids)]
        if filtered_products is not None and 'sku' in filtered_inventory.columns:
            valid_skus = filtered_products['sku'].unique()
            filtered_inventory = filtered_inventory[filtered_inventory['sku'].isin(valid_skus)]
    
    # Show filter results
    original_count = len(sales_df)
    filtered_count = len(filtered_sales)
    filter_pct = (filtered_count / original_count * 100) if original_count > 0 else 0
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(59, 130, 246, 0.1)); 
                padding: 10px 20px; border-radius: 10px; margin: 10px 0;">
        <span style="color: #06b6d4; font-weight: 600;">📊 Showing {filtered_count:,} of {original_count:,} records ({filter_pct:.1f}%)</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---") 
    
# ===== TOGGLE SWITCH =====
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        padding: 25px 50px !important;
        border-radius: 12px !important;
        min-height: 80px !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.3), rgba(59, 130, 246, 0.3)) !important;
        border: 2px solid #06b6d4 !important;
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.3) !important;
    }
    .stTabs [aria-selected="false"] {
        background: rgba(100, 116, 139, 0.15) !important;
        border: 1px solid #475569 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    tab_exec, tab_mgr = st.tabs([
        "👔 Executive View — Financial & Strategic",
        "📋 Manager View — Operational Risk & Execution"
    ])
    
    st.markdown("---")
    
    # Initialize simulator for KPI calculations
    sim = Simulator()
    
    # Calculate KPIs using FILTERED data
    kpis = sim.calculate_overall_kpis(filtered_sales, filtered_products)
    city_kpis = sim.calculate_kpis_by_dimension(filtered_sales, filtered_stores, filtered_products, 'city')
    channel_kpis = sim.calculate_kpis_by_dimension(filtered_sales, filtered_stores, filtered_products, 'channel')
    category_kpis = sim.calculate_kpis_by_dimension(filtered_sales, filtered_stores, filtered_products, 'category')
    
    with tab_exec:
        show_executive_view(kpis, city_kpis, channel_kpis, category_kpis, filtered_sales, filtered_products, filtered_stores, filtered_inventory)
    
    with tab_mgr:
        show_manager_view(kpis, city_kpis, channel_kpis, category_kpis, filtered_sales, filtered_products, filtered_stores, filtered_inventory)
    
    st.markdown("---")
    
    # Data Status
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.is_cleaned:
            st.markdown(create_success_card("✅ Viewing cleaned data."), unsafe_allow_html=True)
        else:
            st.markdown(create_warning_card("⚠️ Viewing raw data. Go to 🧹 Cleaner for validation."), unsafe_allow_html=True)
    
    with col2:
        source = "Cleaned Data ✨" if st.session_state.is_cleaned else "Raw Data 📥"
        st.markdown(create_info_card(f"<strong>Data Source:</strong> {source}"), unsafe_allow_html=True)
    
    show_footer()


def show_executive_view(kpis, city_kpis, channel_kpis, category_kpis, sales_df, products_df, stores_df, filtered_inventory=None):
    """Display Executive View - Financial & Strategic KPIs."""
    
    # ===== KPI CARDS (Executive) =====
    st.markdown('<p class="section-title section-title-cyan">💰 Financial KPIs</p>', unsafe_allow_html=True)
    
    # Row 1: Revenue metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        gross_revenue = kpis.get('total_revenue', 0)
        st.markdown(create_metric_card(
            "Gross Revenue",
            format_currency(gross_revenue),
            color="cyan"
        ), unsafe_allow_html=True)
    
    with col2:
        refund_amount = kpis.get('refund_amount', 0)
        st.markdown(create_metric_card(
            "Refund Amount",
            format_currency(refund_amount),
            color="pink"
        ), unsafe_allow_html=True)
    
    with col3:
        net_revenue = kpis.get('net_revenue', gross_revenue - refund_amount)
        st.markdown(create_metric_card(
            "Net Revenue",
            format_currency(net_revenue),
            color="green"
        ), unsafe_allow_html=True)
    
    with col4:
        cogs = kpis.get('total_cogs', 0)
        st.markdown(create_metric_card(
            "COGS",
            format_currency(cogs),
            color="orange"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 2: Margin metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        gross_margin = kpis.get('total_profit', 0)
        st.markdown(create_metric_card(
            "Gross Margin (AED)",
            format_currency(gross_margin),
            color="teal"
        ), unsafe_allow_html=True)
    
    with col2:
        gross_margin_pct = kpis.get('profit_margin_pct', 0)
        st.markdown(create_metric_card(
            "Gross Margin %",
            f"{gross_margin_pct:.1f}%",
            color="purple"
        ), unsafe_allow_html=True)
    
    with col3:
        avg_discount = kpis.get('avg_discount_pct', 0)
        st.markdown(create_metric_card(
            "Avg Discount %",
            f"{avg_discount:.1f}%",
            color="blue"
        ), unsafe_allow_html=True)
    
    with col4:
        # Calculate Budget Utilization
        total_discount_amount = kpis.get('total_discount', gross_revenue * avg_discount / 100)
        assumed_budget = gross_revenue * 0.15  # Assume 15% of revenue as promo budget
        budget_utilization = (total_discount_amount / assumed_budget * 100) if assumed_budget > 0 else 0
        
        st.markdown(create_metric_card(
            "Budget Utilization",
            f"{budget_utilization:.1f}%",
            color="orange"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    # ===== EXECUTIVE RECOMMENDATION BOX =====
    st.markdown('<p class="section-title section-title-purple">🎯 Executive Recommendations</p>', unsafe_allow_html=True)
    
    # Generate dynamic recommendations based on KPIs
    recommendations = []
    
    # Check Gross Margin %
    gross_margin_pct = kpis.get('profit_margin_pct', 0)
    if gross_margin_pct < 20:
        recommendations.append({
            'priority': '🔴 Critical',
            'area': 'Profitability',
            'insight': f'Gross margin is {gross_margin_pct:.1f}% (below 20% threshold)',
            'action': 'Review pricing strategy and negotiate better supplier costs immediately'
        })
    elif gross_margin_pct < 30:
        recommendations.append({
            'priority': '🟠 High',
            'area': 'Profitability',
            'insight': f'Gross margin is {gross_margin_pct:.1f}% (below 30% target)',
            'action': 'Consider reducing discounts or optimizing product mix'
        })
    else:
        recommendations.append({
            'priority': '🟢 Good',
            'area': 'Profitability',
            'insight': f'Gross margin is healthy at {gross_margin_pct:.1f}%',
            'action': 'Maintain current pricing strategy'
        })
    
    # Check Average Discount
    avg_discount = kpis.get('avg_discount_pct', 0)
    if avg_discount > 15:
        recommendations.append({
            'priority': '🔴 Critical',
            'area': 'Discounting',
            'insight': f'Average discount is {avg_discount:.1f}% (very high)',
            'action': 'Reduce blanket discounts; implement targeted promotions instead'
        })
    elif avg_discount > 10:
        recommendations.append({
            'priority': '🟠 High',
            'area': 'Discounting',
            'insight': f'Average discount is {avg_discount:.1f}% (above optimal)',
            'action': 'Review discount approval process and set category-wise caps'
        })
    
    # Check Refund Rate
    gross_revenue = kpis.get('total_revenue', 0)
    refund_amount = kpis.get('refund_amount', 0)
    refund_rate = (refund_amount / gross_revenue * 100) if gross_revenue > 0 else 0
    if refund_rate > 5:
        recommendations.append({
            'priority': '🔴 Critical',
            'area': 'Returns',
            'insight': f'Refund rate is {refund_rate:.1f}% (above 5% threshold)',
            'action': 'Investigate product quality issues and improve product descriptions'
        })
    elif refund_rate > 3:
        recommendations.append({
            'priority': '🟠 High',
            'area': 'Returns',
            'insight': f'Refund rate is {refund_rate:.1f}% (needs attention)',
            'action': 'Analyze top returned products and address root causes'
        })
    
    # Check Average Order Value
    avg_order_value = kpis.get('avg_order_value', 0)
    if avg_order_value < 100:
        recommendations.append({
            'priority': '🟠 High',
            'area': 'Revenue',
            'insight': f'Average order value is AED {avg_order_value:.0f} (low)',
            'action': 'Implement cross-selling and bundle offers to increase basket size'
        })
    
    # Check inventory stockout risk if available
    if filtered_inventory is not None and 'stock_on_hand' in filtered_inventory.columns:
        zero_stock_count = (filtered_inventory['stock_on_hand'] == 0).sum()
        total_items = len(filtered_inventory)
        stockout_pct = (zero_stock_count / total_items * 100) if total_items > 0 else 0
        
        if stockout_pct > 10:
            recommendations.append({
                'priority': '🔴 Critical',
                'area': 'Inventory',
                'insight': f'{stockout_pct:.1f}% of SKU-store combinations have zero stock',
                'action': 'Urgent replenishment needed; review demand forecasting process'
            })
        elif stockout_pct > 5:
            recommendations.append({
                'priority': '🟠 High',
                'area': 'Inventory',
                'insight': f'{stockout_pct:.1f}% of items at stockout risk',
                'action': 'Prioritize replenishment for fast-moving SKUs'
            })
    
    # Display recommendations
    if recommendations:
        for rec in recommendations:
            priority_color = {
                '🔴 Critical': 'rgba(239, 68, 68, 0.15)',
                '🟠 High': 'rgba(245, 158, 11, 0.15)',
                '🟢 Good': 'rgba(16, 185, 129, 0.15)'
            }.get(rec['priority'], 'rgba(100, 100, 100, 0.15)')
            
            border_color = {
                '🔴 Critical': '#ef4444',
                '🟠 High': '#f59e0b',
                '🟢 Good': '#10b981'
            }.get(rec['priority'], '#666')
            
            st.markdown(f"""
            <div style="background: {priority_color}; 
                        border-left: 4px solid {border_color}; 
                        padding: 15px 20px; 
                        border-radius: 8px; 
                        margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: #e2e8f0;">{rec['priority']} - {rec['area']}</span>
                </div>
                <div style="color: #cbd5e1; margin-bottom: 8px;">
                    <strong>Insight:</strong> {rec['insight']}
                </div>
                <div style="color: #67e8f9;">
                    <strong>Action:</strong> {rec['action']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.15); 
                    border-left: 4px solid #10b981; 
                    padding: 15px 20px; 
                    border-radius: 8px;">
            <span style="font-weight: 600; color: #10b981;">✅ All metrics within healthy ranges!</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== CHART 1: WATERFALL - Profit Bridge (Full Width) =====
    st.markdown('<p class="section-title section-title-blue">📊 Profit Bridge Analysis</p>', unsafe_allow_html=True)
    
    # Calculate waterfall values
    gross_rev = kpis.get('total_revenue', 0)
    refunds = kpis.get('refund_amount', 0)
    discounts = kpis.get('total_discount', gross_rev * kpis.get('avg_discount_pct', 0) / 100)
    cogs_val = kpis.get('total_cogs', 0)
    net_profit = gross_rev - refunds - discounts - cogs_val
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="Profit Bridge",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["Gross Revenue", "Refunds", "Discounts", "COGS", "Net Profit"],
        y=[gross_rev, -refunds, -discounts, -cogs_val, net_profit],
        connector={"line": {"color": "#475569"}},
        decreasing={"marker": {"color": "#ef4444"}},
        increasing={"marker": {"color": "#10b981"}},
        totals={"marker": {"color": "#06b6d4"}},
        text=[format_currency(gross_rev), format_currency(-refunds), format_currency(-discounts), 
              format_currency(-cogs_val), format_currency(net_profit)],
        textposition="outside"
    ))
    
    fig_waterfall.update_layout(
        title="",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0'),
        height=400,
        showlegend=False
    )
    fig_waterfall.update_xaxes(gridcolor='#334155')
    fig_waterfall.update_yaxes(gridcolor='#334155')
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    st.caption("📌 How Net Profit is built: Gross Revenue minus Refunds, Discounts, and COGS.")
    
    st.markdown("---")
    
    # ===== CHART 2 & 3: Area Chart + Bar Chart (Side by Side) =====
    st.markdown('<p class="section-title section-title-green">📈 Revenue & Margin Analysis</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CHART 2: Area Chart - Revenue Trend
        if sales_df is not None and 'order_time' in sales_df.columns:
            # Local filter for time grouping
            time_group = st.selectbox(
                "Group by",
                ["Monthly", "Weekly", "Daily"],
                index=0,
                key="revenue_trend_time_group"
            )
            
            sales_trend = sales_df.copy()
            sales_trend['order_time'] = pd.to_datetime(sales_trend['order_time'], errors='coerce')
            
            # Drop rows with invalid dates
            sales_trend = sales_trend.dropna(subset=['order_time'])
            
            if len(sales_trend) > 0:
                # Create time column based on selection
                if time_group == "Daily":
                    sales_trend['time_period'] = sales_trend['order_time'].dt.strftime('%d %b %Y')
                    sales_trend['time_sort'] = sales_trend['order_time'].dt.date
                elif time_group == "Weekly":
                    sales_trend['time_period'] = sales_trend['order_time'].dt.to_period('W').apply(lambda x: x.start_time.strftime('%d %b %Y'))
                    sales_trend['time_sort'] = sales_trend['order_time'].dt.to_period('W').apply(lambda x: x.start_time)
                else:  # Monthly
                    sales_trend['time_period'] = sales_trend['order_time'].dt.strftime('%b %Y')
                    sales_trend['time_sort'] = sales_trend['order_time'].dt.to_period('M')
                
                # Calculate correct revenue (qty * price)
                if 'qty' in sales_trend.columns and 'selling_price_aed' in sales_trend.columns:
                    sales_trend['revenue'] = sales_trend['qty'] * sales_trend['selling_price_aed']
                elif 'selling_price_aed' in sales_trend.columns:
                    sales_trend['revenue'] = sales_trend['selling_price_aed']
                else:
                    sales_trend['revenue'] = 0
                
                # Filter paid only
                if 'payment_status' in sales_trend.columns:
                    sales_trend = sales_trend[sales_trend['payment_status'] == 'Paid']
                
                # Group by time period
                trend_revenue = sales_trend.groupby(['time_sort', 'time_period']).agg({'revenue': 'sum'}).reset_index()
                trend_revenue = trend_revenue.sort_values('time_sort')
                
                fig_area = go.Figure()
                fig_area.add_trace(go.Scatter(
                    x=trend_revenue['time_period'],
                    y=trend_revenue['revenue'],
                    fill='tozeroy',
                    mode='lines+markers',
                    line=dict(color='#06b6d4', width=2),
                    fillcolor='rgba(6, 182, 212, 0.3)',
                    marker=dict(size=6),
                    name='Revenue'
                ))
                
                fig_area.update_layout(
                    title=f"{time_group} Revenue Trend",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=350,
                    xaxis_title=time_group,
                    yaxis_title="Revenue (AED)",
                    xaxis=dict(type='category')
                )
                fig_area.update_xaxes(gridcolor='#334155')
                fig_area.update_yaxes(gridcolor='#334155')
                
                st.plotly_chart(fig_area, use_container_width=True)
                st.caption(f"📌 {time_group} revenue pattern to identify seasonality and plan promotions.")
            else:
                st.info("No valid dates in data range")
        else:
            st.info("Revenue trend requires order_time column")
    
    with col2:
        # CHART 3: Bar Chart - Margin % by Category
        if category_kpis is not None and len(category_kpis) > 0:
            # Local filters
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                top_n_margin = st.selectbox(
                    "Show Top",
                    [5, 8, 10, "All"],
                    index=1,
                    key="margin_top_n"
                )
            with filter_col2:
                sort_margin = st.selectbox(
                    "Sort by",
                    ["Margin %", "Revenue"],
                    index=0,
                    key="margin_sort"
                )
            
            cat_data = category_kpis.copy()
            
            # Calculate margin_pct if not present
            if 'margin_pct' not in cat_data.columns:
                if 'profit' in cat_data.columns and 'revenue' in cat_data.columns:
                    cat_data['margin_pct'] = (cat_data['profit'] / cat_data['revenue'] * 100).fillna(0)
                else:
                    cat_data['margin_pct'] = 0
            
            # Apply Top N filter
            if top_n_margin != "All":
                cat_data = cat_data.nlargest(int(top_n_margin), 'revenue')
            
            # Apply sorting
            if sort_margin == "Margin %":
                cat_data = cat_data.sort_values('margin_pct', ascending=True)
            else:
                cat_data = cat_data.sort_values('revenue', ascending=True)
            
            colors = ['#ef4444' if x < 20 else '#f59e0b' if x < 30 else '#10b981' for x in cat_data['margin_pct']]
            
            fig_margin = go.Figure(go.Bar(
                x=cat_data['margin_pct'],
                y=cat_data['category'],
                orientation='h',
                marker_color=colors,
                text=[f"{x:.1f}%" for x in cat_data['margin_pct']],
                textposition='outside'
            ))
            
            fig_margin.update_layout(
                title="Gross Margin % by Category",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=350,
                xaxis_title="Margin %",
                yaxis_title=""
            )
            fig_margin.update_xaxes(gridcolor='#334155')
            fig_margin.update_yaxes(gridcolor='#334155')
            
            st.plotly_chart(fig_margin, use_container_width=True)
            st.caption("📌 Which product categories deliver the highest profit margins. Red < 20%, Yellow < 30%, Green ≥ 30%.")
        else:
            st.info("Category data not available")
    
    st.markdown("---")
    
    # ===== CHART 4 & 5: Sunburst + Discount Impact (Side by Side) =====
    st.markdown('<p class="section-title section-title-purple">🎯 Revenue Mix & Discount Impact</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CHART 4: Sunburst - Revenue Mix (City → Channel → Category)
        if sales_df is not None and stores_df is not None and products_df is not None:
            try:
                sunburst_df = sales_df.copy()
                
                # Merge store data
                if 'store_id' in sunburst_df.columns and 'store_id' in stores_df.columns:
                    sunburst_df = sunburst_df.merge(
                        stores_df[['store_id', 'city', 'channel']], 
                        on='store_id', 
                        how='left'
                    )
                
                # Merge product data
                if 'sku' in sunburst_df.columns and 'sku' in products_df.columns:
                    sunburst_df = sunburst_df.merge(
                        products_df[['sku', 'category']], 
                        on='sku', 
                        how='left'
                    )
                elif 'product_id' in sunburst_df.columns and 'product_id' in products_df.columns:
                    sunburst_df = sunburst_df.merge(
                        products_df[['product_id', 'category']], 
                        on='product_id', 
                        how='left'
                    )
                
                # Check if all required columns exist
                if all(col in sunburst_df.columns for col in ['city', 'channel', 'category', 'selling_price_aed']):
                    # Calculate revenue
                    if 'qty' in sunburst_df.columns:
                        sunburst_df['revenue'] = sunburst_df['qty'] * sunburst_df['selling_price_aed']
                    else:
                        sunburst_df['revenue'] = sunburst_df['selling_price_aed']
                    
                    # Filter paid orders only
                    if 'payment_status' in sunburst_df.columns:
                        sunburst_df = sunburst_df[sunburst_df['payment_status'] == 'Paid']
                    
                    # Aggregate data
                    sunburst_agg = sunburst_df.groupby(['city', 'channel', 'category']).agg({
                        'revenue': 'sum'
                    }).reset_index()
                    sunburst_agg.columns = ['City', 'Channel', 'Category', 'Revenue']
                    
                    # Get top 30 combinations for cleaner visualization
                    sunburst_agg = sunburst_agg.nlargest(30, 'Revenue')
                    
                    if len(sunburst_agg) > 0:
                        # Create Sunburst chart
                        fig_sunburst = px.sunburst(
                            sunburst_agg,
                            path=['City', 'Channel', 'Category'],
                            values='Revenue',
                            color='City',
                            color_discrete_sequence=['#06b6d4', '#10b981', '#3b82f6', '#8b5cf6', '#f59e0b']
                        )
                        
                        fig_sunburst = style_plotly_chart_themed(fig_sunburst, height=400)
                        fig_sunburst.update_layout(
                            title="Revenue Mix: City → Channel → Category",
                            coloraxis_showscale=False
                        )
                        fig_sunburst.update_traces(
                            textinfo='label+percent parent',
                            insidetextorientation='radial'
                        )
                        
                        st.plotly_chart(fig_sunburst, use_container_width=True)
                        st.caption("📌 Click to drill down: City → Channel → Category revenue contribution.")
                    else:
                        st.info("No revenue data available for sunburst chart")
                else:
                    # Fallback: Pie chart by channel
                    if 'channel' in sunburst_df.columns and 'selling_price_aed' in sunburst_df.columns:
                        if 'qty' in sunburst_df.columns:
                            sunburst_df['revenue'] = sunburst_df['qty'] * sunburst_df['selling_price_aed']
                        else:
                            sunburst_df['revenue'] = sunburst_df['selling_price_aed']
                        
                        channel_rev = sunburst_df.groupby('channel')['revenue'].sum().reset_index()
                        
                        fig_fallback = px.pie(
                            channel_rev, 
                            values='revenue', 
                            names='channel', 
                            title='Revenue by Channel',
                            color_discrete_sequence=['#06b6d4', '#8b5cf6', '#ec4899'],
                            hole=0.4
                        )
                        fig_fallback = style_plotly_chart_themed(fig_fallback, height=400)
                        
                        st.plotly_chart(fig_fallback, use_container_width=True)
                        st.caption("📌 Revenue distribution by sales channel.")
                    else:
                        st.info("Revenue mix data not available")
            except Exception as e:
                st.info("Unable to create revenue mix chart")
        else:
            st.info("Sales, stores, or products data not available")
    
    with col2:
        # CHART 5: Combo Chart - Discount % vs Profit (Scenario Impact)
        st.markdown("**Discount Impact Analysis**")
        
        # Local filter for margin floor
        margin_floor = st.slider(
            "Margin Floor %",
            min_value=10,
            max_value=40,
            value=20,
            step=5,
            key="discount_margin_floor"
        )
        
        # Simulate profit at different discount levels
        base_revenue = kpis.get('total_revenue', 0)
        base_cogs = kpis.get('total_cogs', 0)
        
        discount_levels = [0, 5, 10, 15, 20, 25, 30]
        profits = []
        margins = []
        
        for disc in discount_levels:
            # Simple simulation: higher discount = higher volume but lower margin
            volume_uplift = 1 + (disc * 0.02)  # 2% volume increase per 1% discount
            simulated_revenue = base_revenue * volume_uplift * (1 - disc/100)
            simulated_cogs = base_cogs * volume_uplift
            profit = simulated_revenue - simulated_cogs
            margin = (profit / simulated_revenue * 100) if simulated_revenue > 0 else 0
            profits.append(profit)
            margins.append(margin)
        
        fig_combo = go.Figure()
        
        # Bars for profit - color based on margin vs margin floor
        bar_colors = ['#10b981' if m >= margin_floor else '#ef4444' for m in margins]
        fig_combo.add_trace(go.Bar(
            x=discount_levels,
            y=profits,
            name='Profit',
            marker_color=bar_colors,
            text=[format_currency(p) for p in profits],
            textposition='outside'
        ))
        
        # Line for margin floor
        fig_combo.add_hline(
            y=base_revenue * margin_floor / 100,
            line_dash="dash",
            line_color="#f59e0b",
            annotation_text=f"Margin Floor ({margin_floor}%)",
            annotation_position="top right"
        )
        
        fig_combo.update_layout(
            title="Profit at Different Discount Levels",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=400,
            xaxis_title="Discount %",
            yaxis_title="Profit (AED)",
            showlegend=False
        )
        fig_combo.update_xaxes(gridcolor='#334155')
        fig_combo.update_yaxes(gridcolor='#334155')
        
        st.plotly_chart(fig_combo, use_container_width=True)
        st.caption("📌 Shows profit at different discount levels. Green = above margin floor, Red = below margin floor.")
    
    st.markdown("---")
    
    # ===== RECOMMENDATION BOX =====
    st.markdown('<p class="section-title section-title-purple">💡 Executive Recommendations</p>', unsafe_allow_html=True)
    
    # Auto-generate recommendations based on KPIs
    recommendations = []
    
    gross_margin_pct = kpis.get('profit_margin_pct', 0)
    avg_discount = kpis.get('avg_discount_pct', 0)
    net_revenue = kpis.get('net_revenue', 0)
    
    # Margin recommendation
    if gross_margin_pct >= 30:
        recommendations.append(f"✅ **Healthy Margin**: Gross margin at {gross_margin_pct:.1f}% is strong. Room for promotional activity.")
    elif gross_margin_pct >= 20:
        recommendations.append(f"⚠️ **Moderate Margin**: Gross margin at {gross_margin_pct:.1f}%. Monitor discount levels carefully.")
    else:
        recommendations.append(f"🔴 **Low Margin Alert**: Gross margin at {gross_margin_pct:.1f}% is below healthy threshold. Reduce discounts or optimize COGS.")
    
    # Discount recommendation
    if avg_discount > 15:
        recommendations.append(f"⚠️ **High Discounting**: Average discount at {avg_discount:.1f}%. Consider reducing to protect margins.")
    elif avg_discount < 5:
        recommendations.append(f"💡 **Low Discount Opportunity**: Average discount at {avg_discount:.1f}%. Consider targeted promotions to drive volume.")
    
    # Top city recommendation
    if city_kpis is not None and len(city_kpis) > 0:
        top_city = city_kpis.nlargest(1, 'revenue')['city'].values[0]
        recommendations.append(f"🏆 **Top Market**: {top_city} leads in revenue. Consider increasing inventory allocation.")
    
    # Top channel recommendation
    if channel_kpis is not None and len(channel_kpis) > 0:
        top_channel = channel_kpis.nlargest(1, 'revenue')['channel'].values[0]
        recommendations.append(f"📱 **Best Channel**: {top_channel} generates highest revenue. Prioritize marketing spend here.")
    
    for rec in recommendations:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1)); 
                    border-left: 4px solid #8b5cf6; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
            <p style="color: #e2e8f0; margin: 0; font-size: 1rem;">{rec}</p>
        </div>
        """, unsafe_allow_html=True)


def show_manager_view(kpis, city_kpis, channel_kpis, category_kpis, sales_df, products_df, stores_df, inventory_df):
    """Display Manager View - Operational Risk & Execution."""
    
    # ===== KPI CARDS (Manager) =====
    st.markdown('<p class="section-title section-title-blue">⚙️ Operational KPIs</p>', unsafe_allow_html=True)
    
    # Calculate Manager-specific KPIs
    return_rate = kpis.get('return_rate_pct', 0)
    
    # Payment failure rate
    if sales_df is not None and 'payment_status' in sales_df.columns:
        total_orders = len(sales_df)
        failed_orders = (sales_df['payment_status'] == 'Failed').sum()
        payment_failure_rate = (failed_orders / total_orders * 100) if total_orders > 0 else 0
    else:
        payment_failure_rate = 0
    
   # Stockout risk - Smart calculation
    stockout_risk = 0
    high_risk_skus = 0
    if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
        total_inventory = len(inventory_df)
        
        # Use reorder_point if available, otherwise use fixed threshold
        if 'reorder_point' in inventory_df.columns:
            # Compare stock against reorder point
            inventory_df['_stock'] = pd.to_numeric(inventory_df['stock_on_hand'], errors='coerce').fillna(0)
            inventory_df['_reorder'] = pd.to_numeric(inventory_df['reorder_point'], errors='coerce').fillna(10)
            low_stock = (inventory_df['_stock'] <= inventory_df['_reorder']).sum()
        else:
            # Fallback: Use 10% of average stock or minimum 10 units
            avg_stock = inventory_df['stock_on_hand'].mean()
            threshold = max(10, avg_stock * 0.1)
            low_stock = (inventory_df['stock_on_hand'] < threshold).sum()
        
        stockout_risk = (low_stock / total_inventory * 100) if total_inventory > 0 else 0
        high_risk_skus = int(low_stock)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "Stockout Risk %",
            f"{stockout_risk:.1f}%",
            color="pink"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Return Rate %",
            f"{return_rate:.1f}%",
            color="orange"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Payment Failure %",
            f"{payment_failure_rate:.1f}%",
            color="purple"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "High-Risk SKUs",
            f"{high_risk_skus:,}",
            color="blue"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== CHART 1: GAUGE - Overall Stockout Risk (Left) + Bar Chart (Right) =====
    st.markdown('<p class="section-title section-title-teal">📊 Risk Overview</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # CHART 1: Gauge - Overall Stockout Risk %
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=stockout_risk,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Stockout Risk %", 'font': {'size': 18, 'color': '#e2e8f0'}},
            number={'suffix': "%", 'font': {'size': 36, 'color': '#e2e8f0'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#e2e8f0'},
                'bar': {'color': '#06b6d4'},
                'bgcolor': 'rgba(0,0,0,0)',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 30], 'color': 'rgba(16, 185, 129, 0.3)'},
                    {'range': [30, 60], 'color': 'rgba(245, 158, 11, 0.3)'},
                    {'range': [60, 100], 'color': 'rgba(239, 68, 68, 0.3)'}
                ],
                'threshold': {
                    'line': {'color': '#ef4444', 'width': 4},
                    'thickness': 0.75,
                    'value': 60
                }
            }
        ))
        
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            height=300
        )
        
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.caption("📌 Overall stockout risk. Green = Safe (0-30%), Yellow = Caution (30-60%), Red = Critical (60%+).")
    
    with col2:
        # CHART 2: Horizontal Bar - Stockout Risk by City-Channel
        if inventory_df is not None and stores_df is not None and 'store_id' in inventory_df.columns:
            inv_with_store = inventory_df.merge(stores_df[['store_id', 'city', 'channel']], on='store_id', how='left')
            
            if all(col in inv_with_store.columns for col in ['city', 'channel', 'stock_on_hand']):
                # Local filter
                top_n_risk = st.selectbox(
                    "Show Top",
                    [5, 10, "All"],
                    index=0,
                    key="city_channel_risk_top_n"
                )
                
                # FIXED: Use explicit aggregation instead of apply() to prevent misalignment
                # Step 1: Calculate aggregates per city-channel
                city_channel_agg = inv_with_store.groupby(['city', 'channel']).agg(
                    low_stock_count=('stock_on_hand', lambda x: (x < 10).sum()),
                    total_count=('stock_on_hand', 'count')
                ).reset_index()
                
                # Step 2: Calculate risk percentage
                city_channel_agg['Risk %'] = (
                    city_channel_agg['low_stock_count'] / city_channel_agg['total_count'] * 100
                ).round(2)
                
                # Step 3: Create label AFTER calculations to ensure alignment
                city_channel_agg['City-Channel'] = city_channel_agg['city'].astype(str) + ' - ' + city_channel_agg['channel'].astype(str)
                
                # Step 4: Sort by risk descending first (for top N selection)
                city_channel_agg = city_channel_agg.sort_values('Risk %', ascending=False)
                
                # Step 5: Apply Top N filter
                if top_n_risk != "All":
                    city_channel_agg = city_channel_agg.head(int(top_n_risk))
                
                # Step 6: Sort ascending for chart display (highest at bottom)
                city_channel_agg = city_channel_agg.sort_values('Risk %', ascending=True)
                
                # Step 7: Convert to lists to guarantee alignment in Plotly
                x_values = city_channel_agg['Risk %'].tolist()
                y_values = city_channel_agg['City-Channel'].tolist()
                
                # Step 8: Create colors based on risk values
                colors = ['#10b981' if x < 30 else '#f59e0b' if x < 60 else '#ef4444' for x in x_values]
                
                # Step 9: Create chart with explicit lists
                fig_risk_bar = go.Figure(go.Bar(
                    x=x_values,
                    y=y_values,
                    orientation='h',
                    marker_color=colors,
                    text=[f"{x:.1f}%" for x in x_values],
                    textposition='outside'
                ))
                
                fig_risk_bar.update_layout(
                    title="Stockout Risk by City-Channel",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=300,
                    xaxis_title="Risk %",
                    yaxis_title="",
                    xaxis=dict(range=[0, max(x_values) * 1.2 if x_values else 100])
                )
                fig_risk_bar.update_xaxes(gridcolor='#334155')
                fig_risk_bar.update_yaxes(gridcolor='#334155')
                
                st.plotly_chart(fig_risk_bar, use_container_width=True)
                st.caption("📌 Which city-channel combinations have highest stockout risk. Prioritize replenishment for red/yellow areas.")
            else:
                st.info("City-channel risk data not available")
        else:
            st.info("Inventory or store data not available")
    
    st.markdown("---")
    
    # ===== CHART 3 & 4: Demand vs Stock + Top 10 SKU Risk =====
    st.markdown('<p class="section-title section-title-orange">📦 Inventory Analysis</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CHART 3: Bar Chart - Demand vs Stock by Category (Dual Y-Axis)
        if sales_df is not None and inventory_df is not None and products_df is not None:
            try:
                sales_with_cat = sales_df.copy()
                sku_col = 'sku' if 'sku' in sales_with_cat.columns else 'product_id'
                
                # Merge category from products
                if sku_col in sales_with_cat.columns and sku_col in products_df.columns:
                    sales_with_cat = sales_with_cat.merge(
                        products_df[[sku_col, 'category']], 
                        on=sku_col, 
                        how='left'
                    )
                
                if 'category' in sales_with_cat.columns and 'qty' in sales_with_cat.columns:
                    # Calculate demand by category
                    sales_with_cat['qty'] = pd.to_numeric(sales_with_cat['qty'], errors='coerce').fillna(0)
                    demand_by_cat = sales_with_cat.groupby('category')['qty'].sum().reset_index()
                    demand_by_cat.columns = ['Category', 'Demand']
                    
                    # Calculate stock by category
                    inv_with_cat = inventory_df.copy()
                    if sku_col in inv_with_cat.columns and sku_col in products_df.columns:
                        inv_with_cat = inv_with_cat.merge(
                            products_df[[sku_col, 'category']], 
                            on=sku_col, 
                            how='left'
                        )
                    
                    if 'category' in inv_with_cat.columns and 'stock_on_hand' in inv_with_cat.columns:
                        inv_with_cat['stock_on_hand'] = pd.to_numeric(inv_with_cat['stock_on_hand'], errors='coerce').fillna(0)
                        stock_by_cat = inv_with_cat.groupby('category')['stock_on_hand'].sum().reset_index()
                        stock_by_cat.columns = ['Category', 'Stock']
                        
                        # Merge demand and stock
                        demand_stock = demand_by_cat.merge(stock_by_cat, on='Category', how='outer').fillna(0)
                        demand_stock = demand_stock.nlargest(8, 'Demand')
                        
                        # Calculate stock coverage ratio
                        demand_stock['Coverage'] = np.where(
                            demand_stock['Demand'] > 0,
                            demand_stock['Stock'] / demand_stock['Demand'],
                            0
                        )
                        
                        # Create figure with dual y-axis
                        fig_demand_stock = make_subplots(specs=[[{"secondary_y": True}]])
                        
                        # Add Demand bars (LEFT y-axis)
                        fig_demand_stock.add_trace(
                            go.Bar(
                                name='Demand (Units Sold)',
                                x=demand_stock['Category'],
                                y=demand_stock['Demand'],
                                marker_color='#8b5cf6',
                                text=[f"{int(v):,}" for v in demand_stock['Demand']],
                                textposition='outside',
                                offsetgroup=0
                            ),
                            secondary_y=False
                        )
                        
                        # Add Stock bars (RIGHT y-axis)
                        fig_demand_stock.add_trace(
                            go.Bar(
                                name='Stock (On Hand)',
                                x=demand_stock['Category'],
                                y=demand_stock['Stock'],
                                marker_color='#06b6d4',
                                text=[f"{int(v):,}" for v in demand_stock['Stock']],
                                textposition='outside',
                                offsetgroup=1
                            ),
                            secondary_y=True
                        )
                        
                        # Get theme colors
                        colors = get_theme_colors()
                        
                        # Update layout
                        fig_demand_stock.update_layout(
                            title="Demand vs Stock by Category",
                            barmode='group',
                            paper_bgcolor=colors['chart_bg'],
                            plot_bgcolor=colors['chart_bg'],
                            font=dict(color=colors['chart_text'], family='Inter, sans-serif'),
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1,
                                bgcolor='rgba(0,0,0,0)',
                                font=dict(color=colors['chart_text'])
                            ),
                            height=380,
                            margin=dict(l=20, r=20, t=80, b=60)
                        )
                        
                        # Update LEFT y-axis (Demand - Purple)
                        fig_demand_stock.update_yaxes(
                            title_text="Demand (Units Sold)",
                            secondary_y=False,
                            gridcolor=colors['chart_grid'],
                            tickfont=dict(color='#8b5cf6'),
                            title_font=dict(color='#8b5cf6')
                        )
                        
                        # Update RIGHT y-axis (Stock - Cyan)
                        fig_demand_stock.update_yaxes(
                            title_text="Stock (On Hand)",
                            secondary_y=True,
                            gridcolor=colors['chart_grid'],
                            tickfont=dict(color='#06b6d4'),
                            title_font=dict(color='#06b6d4')
                        )
                        
                        # Update x-axis
                        fig_demand_stock.update_xaxes(
                            tickfont=dict(color=colors['chart_text']),
                            tickangle=45,
                            gridcolor=colors['chart_grid']
                        )
                        
                        st.plotly_chart(fig_demand_stock, use_container_width=True)
                        
                        # Show warning for low coverage categories
                        low_coverage = demand_stock[demand_stock['Coverage'] < 10]
                        if len(low_coverage) > 0:
                            st.warning(f"⚠️ **{len(low_coverage)} categories** have less than 10x stock coverage: {', '.join(low_coverage['Category'].tolist())}")
                        else:
                            st.caption("📌 Purple = Demand (left axis), Cyan = Stock (right axis). Scales differ for better visibility.")
                    else:
                        st.info("Stock by category not available")
                else:
                    st.info("Category demand data not available")
            except Exception as e:
                st.info(f"Unable to create demand vs stock chart")
        else:
            st.info("Required data not available")
    
    with col2:
        # CHART 4: Horizontal Bar - Top N SKU-Store Stockout Risk
        if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
            # Get SKU column
            sku_col = 'sku' if 'sku' in inventory_df.columns else 'product_id'
            
            if sku_col in inventory_df.columns:
                # Local filter
                top_n_sku = st.selectbox(
                    "Show Top",
                    [5, 10, 15, 20],
                    index=1,
                    key="sku_stockout_top_n"
                )
                
                # Function to calculate risk based on absolute thresholds
                def calculate_stockout_risk(stock):
                    """
                    Calculate stockout risk based on absolute stock thresholds.
                    Returns varied scores based on actual inventory levels.
                    """
                    stock = float(stock)
                    if stock <= 0:
                        return 100.0
                    elif stock <= 5:
                        return 95 - (stock - 1) * 6.25  # 95% to 70%
                    elif stock <= 15:
                        return 65 - (stock - 6) * 2.5  # 65% to 40%
                    elif stock <= 30:
                        return 35 - (stock - 16) * 1.43  # 35% to 15%
                    elif stock <= 50:
                        return 14 - (stock - 31) * 0.45  # 14% to 5%
                    else:
                        return max(0, 5 - (stock - 51) * 0.05)  # 5% to 0%
                
                # Apply risk calculation to ALL inventory first
                inventory_with_risk = inventory_df.copy()
                inventory_with_risk['stock_on_hand'] = pd.to_numeric(inventory_with_risk['stock_on_hand'], errors='coerce').fillna(0)
                inventory_with_risk['risk_score'] = inventory_with_risk['stock_on_hand'].apply(calculate_stockout_risk)
                
                # Get top N HIGHEST RISK items
                risk_df = inventory_with_risk.nlargest(int(top_n_sku), 'risk_score').copy()
                
                # Add store info if available
                if stores_df is not None and 'store_id' in risk_df.columns and 'store_id' in stores_df.columns:
                    risk_df = risk_df.merge(stores_df[['store_id', 'city']], on='store_id', how='left')
                    risk_df['SKU-Location'] = (
                        risk_df[sku_col].astype(str) + ' @ ' + 
                        risk_df['city'].fillna('Unknown') + 
                        ' (Stock: ' + risk_df['stock_on_hand'].astype(int).astype(str) + ')'
                    )
                else:
                    risk_df['SKU-Location'] = (
                        risk_df[sku_col].astype(str) + 
                        ' (Stock: ' + risk_df['stock_on_hand'].astype(int).astype(str) + ')'
                    )
                
                # Sort for chart display (lowest risk at top, highest at bottom)
                risk_df = risk_df.sort_values('risk_score', ascending=True)
                
                # Convert to lists for guaranteed alignment
                x_values = risk_df['risk_score'].tolist()
                y_values = risk_df['SKU-Location'].tolist()
                
                # Color based on risk level
                colors = ['#ef4444' if x >= 70 else '#f59e0b' if x >= 40 else '#10b981' for x in x_values]
                
                # Create chart
                fig_sku_risk = go.Figure(go.Bar(
                    x=x_values,
                    y=y_values,
                    orientation='h',
                    marker_color=colors,
                    text=[f"{x:.0f}% risk" for x in x_values],
                    textposition='outside'
                ))
                
                fig_sku_risk.update_layout(
                    title=f"Top {top_n_sku} Stockout Risk SKU-Store",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    height=350,
                    xaxis_title="Risk Score %",
                    yaxis_title="",
                    xaxis=dict(range=[0, 110], gridcolor='#334155'),
                    yaxis=dict(gridcolor='#334155')
                )
                
                st.plotly_chart(fig_sku_risk, use_container_width=True)
                st.caption("📌 SKU-Store pairs most likely to run out of stock. Longer bar = higher risk. Action list for ops team.")
            else:
                st.info("SKU data not available")
        else:
            st.info("Inventory data not available")
    
    st.markdown("---")
    
    # ===== CHART 5: PARETO - Issues Log (Full Width) =====
    st.markdown('<p class="section-title section-title-pink">📋 Data Quality Analysis</p>', unsafe_allow_html=True)
    
    if st.session_state.is_cleaned and hasattr(st.session_state, 'issues_df') and st.session_state.issues_df is not None:
        issues_df = st.session_state.issues_df
        if len(issues_df) > 0 and 'issue_type' in issues_df.columns:
            # Extract count from record_identifier (e.g., "475 rows" → 475)
            pareto_df = issues_df.copy()
            pareto_df['Count'] = pareto_df['record_identifier'].str.extract(r'(\d+)').astype(float).fillna(1)
            
            # Group by issue type and sum counts
            issue_counts = pareto_df.groupby('issue_type')['Count'].sum().reset_index()
            issue_counts.columns = ['Issue Type', 'Count']
            issue_counts = issue_counts.sort_values('Count', ascending=False)
            
            # Local filter
            top_n_pareto = st.selectbox(
                "Show Top Issue Types",
                [5, 10, "All"],
                index=1,
                key="pareto_top_n"
            )
            
            # Apply Top N filter
            if top_n_pareto != "All":
                issue_counts = issue_counts.head(int(top_n_pareto))
            
            # Calculate cumulative percentage
            total_issues = issue_counts['Count'].sum()
            issue_counts['Cumulative'] = issue_counts['Count'].cumsum()
            issue_counts['Cumulative %'] = (issue_counts['Cumulative'] / total_issues * 100)
            
            # Create Pareto chart
            fig_pareto = go.Figure()
            
            # Bars
            fig_pareto.add_trace(go.Bar(
                x=issue_counts['Issue Type'],
                y=issue_counts['Count'],
                name='Count',
                marker_color='#8b5cf6',
                text=issue_counts['Count'].astype(int),
                textposition='outside'
            ))
            
            # Cumulative line
            fig_pareto.add_trace(go.Scatter(
                x=issue_counts['Issue Type'],
                y=issue_counts['Cumulative %'],
                name='Cumulative %',
                mode='lines+markers',
                line=dict(color='#f59e0b', width=3),
                marker=dict(size=8),
                yaxis='y2'
            ))
            
            # 80% line
            fig_pareto.add_hline(
                y=80,
                line_dash="dash",
                line_color="#ef4444",
                yref='y2',
                annotation_text="80% threshold",
                annotation_position="right"
            )
            
            fig_pareto.update_layout(
                title="Data Quality Issues - Pareto Analysis",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                height=400,
                xaxis_title="Issue Type",
                yaxis=dict(title='Count', side='left', gridcolor='#334155'),
                yaxis2=dict(title='Cumulative %', side='right', overlaying='y', range=[0, 105], gridcolor='#334155'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                barmode='group'
            )
            fig_pareto.update_xaxes(gridcolor='#334155', tickangle=45)
            
            st.plotly_chart(fig_pareto, use_container_width=True)
            st.caption("📌 Fix issues from left to right until the orange line crosses 80% (red dashed line). These few issue types cause most data problems.")
        else:
            st.info("No issues logged")
    else:
        st.info("Clean data first to see issues Pareto analysis")
    
    st.markdown("---")
    
    
    # ===== TOP RISK TABLE =====
    st.markdown('<p class="section-title section-title-orange">🚨 Top Stockout Risk Items - Action List</p>', unsafe_allow_html=True)
    
    if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
        sku_col = 'sku' if 'sku' in inventory_df.columns else 'product_id'
        
        if sku_col in inventory_df.columns:
            risk_table = inventory_df.nsmallest(10, 'stock_on_hand').copy()
            
            # Add store city if possible
            if stores_df is not None and 'store_id' in risk_table.columns and 'store_id' in stores_df.columns:
                risk_table = risk_table.merge(
                    stores_df[['store_id', 'city', 'channel']],
                    on='store_id',
                    how='left'
                )
            
            # Calculate risk level
            risk_table['Risk Level'] = risk_table['stock_on_hand'].apply(
                lambda x: '🔴 Critical' if x < 5 else ('🟠 High' if x < 10 else '🟡 Medium')
            )
            
            display_cols = [col for col in [sku_col, 'store_id', 'city', 'channel', 'stock_on_hand', 'Risk Level'] if col in risk_table.columns]
            
            st.dataframe(
                risk_table[display_cols],
                use_container_width=True,
                hide_index=True
            )
            st.caption("📌 Operations action list: SKU-Store pairs with lowest stock. Sort by any column. Export for immediate action.")
        else:
            st.info("SKU data not available")
    else:
        st.info("Inventory data not available for risk analysis")
    
    st.markdown("---")
    
    # ===== OPERATIONAL ALERTS =====
    st.markdown('<p class="section-title section-title-pink">⚠️ Operational Alerts</p>', unsafe_allow_html=True)
    
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
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(6, 182, 212, 0.2)); 
                    border-left: 4px solid #10b981; padding: 15px; border-radius: 8px;">
            <p style="color: #10b981; margin: 0; font-size: 1.1rem; font-weight: 600;">✅ All operational metrics within healthy ranges.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for alert in alerts:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(245, 158, 11, 0.1)); 
                        border-left: 4px solid #f59e0b; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                <p style="color: #e2e8f0; margin: 0; font-size: 1rem;">{alert}</p>
            </div>
            """, unsafe_allow_html=True)


def generate_executive_recommendations(kpis, city_kpis, channel_kpis, category_kpis):
    """Generate auto recommendations based on KPIs."""
    recommendations = []
    
    # Margin recommendation
    margin = kpis.get('profit_margin_pct', 0)
    if margin < 20:
        recommendations.append(f"📉 **Margin Alert**: Gross margin at {margin:.1f}% is below target. Consider reducing discounts or reviewing supplier costs.")
    elif margin > 35:
        recommendations.append(f"📈 **Strong Margins**: Gross margin at {margin:.1f}% is healthy. Opportunity to invest in growth.")
    
    # Discount recommendation
    avg_discount = kpis.get('avg_discount_pct', 0)
    if avg_discount > 15:
        recommendations.append(f"💸 **High Discounting**: Average discount at {avg_discount:.1f}%. Evaluate if promotions are driving profitable growth.")
    
    # City recommendation
    if len(city_kpis) > 0:
        top_city = city_kpis.iloc[0]['city']
        top_revenue = city_kpis.iloc[0]['revenue']
        recommendations.append(f"🏙️ **Top Market**: {top_city} leads with AED {top_revenue:,.0f} revenue. Consider increasing investment.")
    
    # Channel recommendation
    if len(channel_kpis) > 0:
        top_channel = channel_kpis.iloc[0]['channel']
        recommendations.append(f"📱 **Channel Focus**: {top_channel} is the top performing channel. Optimize marketing spend here.")
    
    if len(recommendations) == 0:
        recommendations.append("✅ Business performance is on track. Continue monitoring KPIs.")
    
    return recommendations
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
    
    # Show expected columns info
    with st.expander("ℹ️ Expected File Formats (Click to Expand)"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **📦 Products File:**
            - Required: `sku`, `category`, `base_price_aed`
            - Optional: `unit_cost_aed`, `brand`, `launch_flag`
            
            **🛒 Sales File:**
            - Required: `order_id`, `sku`, `store_id`, `qty`, `selling_price_aed`
            - Optional: `order_time`, `discount_pct`, `payment_status`, `return_flag`
            """)
        with col2:
            st.markdown("""
            **🏪 Stores File:**
            - Required: `store_id`, `city`, `channel`
            - Optional: `fulfillment_type`, `store_name`
            
            **📋 Inventory File:**
            - Required: `sku`, `store_id`, `stock_on_hand`
            - Optional: `snapshot_date`, `reorder_point`, `lead_time_days`
            """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Track validation status for each file
    valid_files = {}
    
    col1, col2 = st.columns(2)
    
    # ===== PRODUCTS UPLOAD WITH INSTANT VALIDATION =====
    with col1:
        products_file = st.file_uploader("📦 Products CSV", type=['csv'], key='products_upload')
        if products_file:
            try:
                products_df = pd.read_csv(products_file)
                products_file.seek(0)  # Reset file pointer for later use
                validation = FileValidator.validate_file(products_df, 'products')
                
                if validation['valid']:
                    st.success(f"✅ Valid products file ({len(products_df):,} rows)")
                    valid_files['products'] = products_df
                else:
                    st.error(f"❌ {validation['message']}")
                    if validation['missing_columns']:
                        st.warning(f"Missing: {', '.join(validation['missing_columns'])}")
                    if validation.get('detected_type'):
                        st.info(f"💡 This looks like a {validation['detected_type'].upper()} file. Upload it in the correct slot.")
            except Exception as e:
                st.error(f"❌ Cannot read file: {str(e)}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ===== SALES UPLOAD WITH INSTANT VALIDATION =====
        sales_file = st.file_uploader("🛒 Sales CSV", type=['csv'], key='sales_upload')
        if sales_file:
            try:
                sales_df = pd.read_csv(sales_file)
                sales_file.seek(0)
                validation = FileValidator.validate_file(sales_df, 'sales')
                
                if validation['valid']:
                    st.success(f"✅ Valid sales file ({len(sales_df):,} rows)")
                    valid_files['sales'] = sales_df
                else:
                    st.error(f"❌ {validation['message']}")
                    if validation['missing_columns']:
                        st.warning(f"Missing: {', '.join(validation['missing_columns'])}")
                    if validation.get('detected_type'):
                        st.info(f"💡 This looks like a {validation['detected_type'].upper()} file. Upload it in the correct slot.")
            except Exception as e:
                st.error(f"❌ Cannot read file: {str(e)}")
    
    # ===== STORES UPLOAD WITH INSTANT VALIDATION =====
    with col2:
        stores_file = st.file_uploader("🏪 Stores CSV", type=['csv'], key='stores_upload')
        if stores_file:
            try:
                stores_df = pd.read_csv(stores_file)
                stores_file.seek(0)
                validation = FileValidator.validate_file(stores_df, 'stores')
                
                if validation['valid']:
                    st.success(f"✅ Valid stores file ({len(stores_df):,} rows)")
                    valid_files['stores'] = stores_df
                else:
                    st.error(f"❌ {validation['message']}")
                    if validation['missing_columns']:
                        st.warning(f"Missing: {', '.join(validation['missing_columns'])}")
                    if validation.get('detected_type'):
                        st.info(f"💡 This looks like a {validation['detected_type'].upper()} file. Upload it in the correct slot.")
            except Exception as e:
                st.error(f"❌ Cannot read file: {str(e)}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ===== INVENTORY UPLOAD WITH INSTANT VALIDATION =====
        inventory_file = st.file_uploader("📋 Inventory CSV", type=['csv'], key='inventory_upload')
        if inventory_file:
            try:
                inventory_df = pd.read_csv(inventory_file)
                inventory_file.seek(0)
                validation = FileValidator.validate_file(inventory_df, 'inventory')
                
                if validation['valid']:
                    st.success(f"✅ Valid inventory file ({len(inventory_df):,} rows)")
                    valid_files['inventory'] = inventory_df
                else:
                    st.error(f"❌ {validation['message']}")
                    if validation['missing_columns']:
                        st.warning(f"Missing: {', '.join(validation['missing_columns'])}")
                    if validation.get('detected_type'):
                        st.info(f"💡 This looks like a {validation['detected_type'].upper()} file. Upload it in the correct slot.")
            except Exception as e:
                st.error(f"❌ Cannot read file: {str(e)}")
    
    st.markdown("---")
    
    # ===== LOAD BUTTON - ONLY LOADS VALID FILES =====
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
       # Show status before button
        required_files = ['products', 'stores', 'sales', 'inventory']
        missing_files = [f for f in required_files if f not in valid_files]
        
        if len(valid_files) == 4:
            st.success(f"✅ All 4 files valid and ready to load!")
        elif len(valid_files) > 0:
            st.warning(f"⚠️ {len(valid_files)}/4 files valid. Missing: {', '.join(missing_files)}")
        else:
            st.info("📤 Please upload all 4 files: Products, Stores, Sales, Inventory")
        
        # Disable button unless ALL 4 files are valid
        button_disabled = len(valid_files) != 4
        
        if st.button("📥 Load All Files", width='stretch', disabled=button_disabled):
            if 'products' in valid_files:
                st.session_state.raw_products = valid_files['products']
            if 'stores' in valid_files:
                st.session_state.raw_stores = valid_files['stores']
            if 'sales' in valid_files:
                st.session_state.raw_sales = valid_files['sales']
            if 'inventory' in valid_files:
                st.session_state.raw_inventory = valid_files['inventory']
            
            st.session_state.data_loaded = True
            st.session_state.is_cleaned = False
            st.success(f"✅ {len(valid_files)} file(s) loaded successfully!")
            st.rerun()
        
        if button_disabled and (products_file or stores_file or sales_file or inventory_file):
            st.error("⚠️ Cannot load - no valid files. Please fix the errors above.")
        elif button_disabled:
            st.info("📤 Upload files above to get started.")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎲 Generate Random Sample Data", width='stretch', key='sample_data_btn'):
            try:
                import random
                from datetime import datetime, timedelta
                
                # Random counts
                num_products = random.randint(50, 150)
                num_stores = random.randint(10, 30)
                num_sales = random.randint(500, 2000)
                num_inventory = num_products * num_stores
                
                # Random categories and cities
                all_categories = ['Electronics', 'Fashion', 'Grocery', 'Beauty', 'Home', 'Sports', 'Toys', 'Books']
                all_cities = ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Ras Al Khaimah']
                all_channels = ['Online', 'Retail', 'Wholesale']
                
                categories = random.sample(all_categories, random.randint(4, 6))
                cities = random.sample(all_cities, random.randint(3, 5))
                
                # Generate Products
                products_data = {
                    'sku': [f'SKU{str(i).zfill(4)}' for i in range(1, num_products + 1)],
                    'product_name': [f'Product {i}' for i in range(1, num_products + 1)],
                    'category': np.random.choice(categories, num_products),
                    'brand': np.random.choice(['BrandA', 'BrandB', 'BrandC', 'BrandD'], num_products),
                    'unit_cost_aed': np.random.uniform(10, 500, num_products).round(2),
                    'base_price_aed': np.random.uniform(50, 1000, num_products).round(2),
                }
                st.session_state.raw_products = pd.DataFrame(products_data)
                
                # Generate Stores
                stores_data = {
                    'store_id': [f'STR{str(i).zfill(3)}' for i in range(1, num_stores + 1)],
                    'store_name': [f'Store {i}' for i in range(1, num_stores + 1)],
                    'city': np.random.choice(cities, num_stores),
                    'channel': np.random.choice(all_channels, num_stores),
                }
                st.session_state.raw_stores = pd.DataFrame(stores_data)
                
                # Generate Sales
                end_date = datetime.now()
                start_date = end_date - timedelta(days=random.randint(30, 90))
                
                sales_data = {
                    'order_id': [f'ORD{str(i).zfill(6)}' for i in range(1, num_sales + 1)],
                    'order_time': [start_date + timedelta(days=random.randint(0, (end_date-start_date).days)) for _ in range(num_sales)],
                    'sku': np.random.choice(products_data['sku'], num_sales),
                    'store_id': np.random.choice(stores_data['store_id'], num_sales),
                    'qty': np.random.randint(1, 10, num_sales),
                    'selling_price_aed': np.random.uniform(50, 800, num_sales).round(2),
                    'discount_pct': np.random.choice([0, 5, 10, 15, 20], num_sales),
                    'payment_status': np.random.choice(['Paid', 'Paid', 'Paid', 'Failed', 'Refunded'], num_sales),
                    'return_flag': np.random.choice([0, 0, 0, 0, 1], num_sales),
                }
                st.session_state.raw_sales = pd.DataFrame(sales_data)
                
                # Generate Inventory
                inventory_data = {
                    'sku': np.repeat(products_data['sku'], num_stores),
                    'store_id': np.tile(stores_data['store_id'], num_products),
                    'stock_on_hand': np.random.randint(0, 200, num_inventory),
                    'reorder_point': np.random.randint(5, 30, num_inventory),
                }
                st.session_state.raw_inventory = pd.DataFrame(inventory_data)
                
                st.session_state.data_loaded = True
                st.session_state.is_cleaned = False
                st.success(f"✅ Random data generated! {num_products} products, {num_stores} stores, {num_sales} sales")
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
            else:
                st.info("📦 No products data loaded")
        
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
            else:
                st.info("🏪 No stores data loaded")
        
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
            else:
                st.info("🛒 No sales data loaded")
        
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
            else:
                st.info("📋 No inventory data loaded")
        
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
                <li>Duplicate Recordss</li>
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
        
        if len(issues_df) > 0 and not (len(issues_df) == 1 and issues_df.iloc[0]['issue_type'] == 'None'):
            total_fixed = stats.get('total_issues_fixed', 0)
            st.markdown(create_success_card(f"Total {total_fixed} issues detected and fixed automatically!"), unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                issue_counts = issues_df.groupby('issue_type').size().reset_index(name='count')
                
                fig = px.bar(
                    issue_counts,
                    x='count',
                    y='issue_type',
                    orientation='h',
                    title='Issues by Type',
                    color='count',
                    color_continuous_scale=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899']
                )
                fig = style_plotly_chart(fig)
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                table_counts = issues_df.groupby('table').size().reset_index(name='count')
                
                fig = px.pie(
                    table_counts,
                    values='count',
                    names='table',
                    title='Issues by Table',
                    color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899'],
                    hole=0.45
                )
                fig = style_plotly_chart(fig)
                st.plotly_chart(fig, width='stretch')
            
            st.markdown('<p class="section-title section-title-purple">💡 Cleaning Insight</p>', unsafe_allow_html=True)
            
            # Extract ACTUAL counts from record_identifier (e.g., "475 rows" → 475)
            insight_df = issues_df.copy()
            insight_df['actual_count'] = insight_df['record_identifier'].str.extract(r'(\d+)').astype(float).fillna(1)
            
            # Group by issue type and sum actual counts
            issue_summary = insight_df.groupby('issue_type')['actual_count'].sum().reset_index()
            issue_summary.columns = ['issue_type', 'count']
            
            # Filter out NO_ISSUES entries
            issue_summary = issue_summary[issue_summary['issue_type'] != 'NO_ISSUES']
            
            if len(issue_summary) > 0:
                # Find top issue
                top_issue = issue_summary.loc[issue_summary['count'].idxmax(), 'issue_type']
                top_count = int(issue_summary['count'].max())
                
                st.markdown(create_insight_card(
                    "Most Common Issue", 
                    f"'{top_issue}' was the most frequent issue with {top_count:,} occurrences. All instances have been automatically fixed."
                ), unsafe_allow_html=True)
            else:
                st.markdown(create_success_card("✅ No data quality issues found! Your data was already clean."), unsafe_allow_html=True)
            
            st.markdown('<p class="section-title section-title-blue">📋 Detailed Issues Log</p>', unsafe_allow_html=True)
            st.dataframe(issues_df, use_container_width=True)
            
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
    """Reverse Campaign Simulator: user sets budget + city, app recommends discount/margin/days."""

    st.markdown('<h1 class="page-title page-title-purple">🎯 Campaign Simulator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Set Budget + Target City, and we recommend the best Discount, Margin Floor, and Campaign Days for positive ROI.</p>', unsafe_allow_html=True)
    st.markdown("---")

    if not st.session_state.data_loaded:
        st.warning("⚠️ Please load data first. Go to 📂 Data page.")
        show_footer()
        return

    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products

    if sales_df is None or stores_df is None or products_df is None:
        st.warning("⚠️ Missing required tables (sales, stores, products). Please load all files.")
        show_footer()
        return

    # Options
    cities = ['All']
    channels = ['All']
    categories = ['All']

    if 'city' in stores_df.columns:
        cities += sorted(stores_df['city'].dropna().unique().tolist())
    if 'channel' in stores_df.columns:
        channels += sorted(stores_df['channel'].dropna().unique().tolist())
    if 'category' in products_df.columns:
        categories += sorted(products_df['category'].dropna().unique().tolist())

    st.markdown('<p class="section-title section-title-cyan">⚙️ Inputs (You Control)</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        promo_budget = st.number_input("Promo Budget (AED)", min_value=1000, max_value=500000, value=25000, step=5000)
        data_days = st.slider("Baseline Window (days)", 7, 90, 30, step=1)

    with col2:
        city = st.selectbox("Target City", cities)
        channel = st.selectbox("Target Channel (optional)", channels)

    with col3:
        category = st.selectbox("Target Category (optional)", categories)
        objective = st.selectbox("Optimize For", ["roi", "net_profit"], index=0)

    st.markdown("---")

    colA, colB, colC = st.columns([1, 2, 1])
    with colB:
        run_opt = st.button("🧠 Find Best Campaign (Positive ROI)", use_container_width=True, type="primary")

    if run_opt:
        with st.spinner("Searching best Discount / Margin Floor / Days..."):
            sim = Simulator()
            opt = sim.recommend_campaign(
                sales_df=sales_df,
                stores_df=stores_df,
                products_df=products_df,
                promo_budget=promo_budget,
                city=city,
                channel=channel,
                category=category,
                data_days=data_days,
                objective=objective,
                require_positive_roi=False
            )
            st.session_state.sim_opt_results = opt

    if "sim_opt_results" in st.session_state and st.session_state.sim_opt_results:
        opt = st.session_state.sim_opt_results
        best = opt.get("best")
        warnings = opt.get("warnings", [])

        st.markdown("---")
        st.markdown('<p class="section-title section-title-teal">🏆 Recommended Campaign (Best Result)</p>', unsafe_allow_html=True)

        if best is None:
            st.warning("No positive-ROI solution found in the search grid. Try increasing budget, changing city/category, or expanding search.")
            for w in warnings:
                st.warning(w)
            show_footer()
            return

        # Recommended knobs
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(create_metric_card("Recommended Discount %", f"{best['discount_pct']:.0f}%", color="cyan"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("Recommended Margin Floor %", f"{best['margin_floor']:.0f}%", color="purple"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card("Recommended Campaign Days", f"{best['campaign_days']}", color="blue"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Expected outcomes
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card("Expected Revenue", format_currency(best["expected_revenue"]), color="cyan"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("Expected Net Profit", format_currency(best["expected_net_profit"]), color="green"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card("Expected Margin %", f"{best['expected_margin_pct']:.1f}%", color="orange"), unsafe_allow_html=True)
        with col4:
            roi_color = "green" if best["roi_pct"] > 0 else "pink"
            st.markdown(create_metric_card("ROI", f"{best['roi_pct']:.1f}%", color=roi_color), unsafe_allow_html=True)

        if warnings:
            st.markdown("---")
            st.markdown('<p class="section-title section-title-orange">⚠️ Notes / Constraints</p>', unsafe_allow_html=True)
            for w in warnings:
                st.warning(w)

        # Optional: show top candidates table
        candidates_df = opt.get("candidates")
        if candidates_df is not None and len(candidates_df) > 0:
            st.markdown("---")
            st.markdown('<p class="section-title section-title-blue">🔎 Top Options (Debug / Comparison)</p>', unsafe_allow_html=True)
            st.dataframe(
                candidates_df.head(20)[[
                    "discount_pct", "margin_floor", "campaign_days",
                    "expected_revenue", "expected_net_profit", "expected_margin_pct", "roi_pct"
                ]],
                use_container_width=True,
                hide_index=True
            )

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
                    status_counts.columns = ['Status', 'count']
                    
                    fig = px.pie(
                        status_counts,
                        values='count',
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
elif page == "📊 Dashboard":
    show_dashboard_page()
elif page == "🎯 Simulator":
    show_simulator_page()
