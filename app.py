# ============================================================================
# UAE Promo Pulse Simulator + Data Rescue Dashboard
# Main Streamlit Application - COMPLETE REFINED VERSION v2.1
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
        margin-right: 12px;
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
    
    /* ===== RECOMMENDATION BOX ===== */
    .recommendation-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 182, 212, 0.15) 100%);
        border-radius: 16px;
        padding: 25px 30px;
        border: 2px solid rgba(16, 185, 129, 0.4);
        margin: 20px 0;
        position: relative;
        overflow: hidden;
    }
    
    .recommendation-box::before {
        content: '💡';
        position: absolute;
        top: 15px;
        right: 20px;
        font-size: 2rem;
        opacity: 0.5;
    }
    
    .recommendation-title {
        color: #10b981;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 12px;
    }
    
    .recommendation-text {
        color: #e2e8f0;
        font-size: 1rem;
        line-height: 1.7;
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
    
    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #14b8a6 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #14b8a6 0%, #06b6d4 100%);
        transform: translateY(-2px);
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
    
    /* ===== RISK TABLE ===== */
    .risk-high { color: #ef4444; font-weight: 700; }
    .risk-medium { color: #f59e0b; font-weight: 600; }
    .risk-low { color: #10b981; font-weight: 500; }

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
        delta_html = '<div style="height: 22px;"></div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value metric-value-{color}">{value}</div>
        {delta_html}
    </div>
    """

def create_feature_card(icon, title, description, color="cyan"):
    """Create a feature card with uniform size and hover effect."""
    colors = {
        "cyan": "#06b6d4",
        "blue": "#3b82f6", 
        "purple": "#8b5cf6",
        "pink": "#ec4899",
        "green": "#10b981",
        "orange": "#f59e0b",
        "teal": "#14b8a6"
    }
    accent = colors.get(color, "#06b6d4")
    
    return f"""
    <div style="
        background: linear-gradient(145deg, #16161f 0%, #1a1a24 100%);
        border-radius: 16px;
        padding: 30px 20px;
        border: 1px solid #2d2d3a;
        text-align: center;
        height: 220px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        cursor: pointer;
    " onmouseover="this.style.transform='translateY(-8px)'; this.style.borderColor='{accent}'; this.style.boxShadow='0 12px 30px rgba(6,182,212,0.2)';" 
       onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='#2d2d3a'; this.style.boxShadow='none';">
        <div style="font-size: 48px; margin-bottom: 15px;">{icon}</div>
        <div style="color: {accent}; font-size: 1.1rem; font-weight: 600; margin-bottom: 10px;">{title}</div>
        <div style="color: #94a3b8; font-size: 0.85rem; line-height: 1.5;">{description}</div>
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

def create_recommendation_box(title, recommendations):
    """Create auto-generated recommendation box for Executive view."""
    reco_html = "<br>".join([f"• {r}" for r in recommendations])
    return f"""
    <div class="recommendation-box">
        <div class="recommendation-title">📋 {title}</div>
        <div class="recommendation-text">{reco_html}</div>
    </div>
    """

def show_footer():
    """Display the footer with team names."""
    st.markdown("""
    <div class="footer">
        <div class="footer-title">🚀 UAE Promo Pulse Simulator + Data Rescue Dashboard</div>
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
    
    # Category insight
    if cat_kpis is not None and len(cat_kpis) > 0:
        top_cat = cat_kpis.iloc[0]
        if 'category' in cat_kpis.columns and 'profit_margin_pct' in cat_kpis.columns:
            insights.append(("Top Category", f"{top_cat['category']} leads with {top_cat.get('profit_margin_pct', 0):.1f}% margin. Focus promotional efforts here for maximum ROI."))
    
    # Discount insight
    avg_discount = kpis.get('avg_discount_pct', 0)
    if avg_discount > 20:
        insights.append(("Heavy Discounting", f"Average discount of {avg_discount:.1f}% may be eroding margins. Consider value-based pricing."))
    elif avg_discount < 5:
        insights.append(("Discount Opportunity", f"Low discount rate of {avg_discount:.1f}% suggests room for targeted promotions to boost volume."))
    
    return insights[:5]  # Return top 5 insights

def generate_executive_recommendations(kpis, sim_results=None):
    """Generate auto recommendations for Executive view."""
    recommendations = []
    
    # Margin recommendation
    margin = kpis.get('profit_margin_pct', 0)
    if margin > 25:
        recommendations.append(f"Strong margin of {margin:.1f}% provides room for aggressive promotional discounts up to 15%.")
    elif margin < 15:
        recommendations.append(f"Current margin of {margin:.1f}% is below target. Consider reducing discount depth or focusing on high-margin categories.")
    
    # AOV recommendation
    aov = kpis.get('avg_order_value', 0)
    if aov < 200:
        recommendations.append(f"Average order value (AED {aov:.0f}) is low. Implement bundle offers or minimum cart value promotions.")
    elif aov > 500:
        recommendations.append(f"High AOV of AED {aov:.0f} indicates premium customer base. Focus on loyalty rewards over discounts.")
    
    # Revenue recommendation
    if sim_results:
        roi = sim_results.get('outputs', {}).get('roi_pct', 0)
        if roi > 50:
            recommendations.append(f"Projected ROI of {roi:.0f}% is excellent. Campaign is recommended for execution.")
        elif roi < 0:
            recommendations.append(f"Negative ROI projected. Consider reducing discount % or narrowing target segment.")
    
    # Return rate
    return_rate = kpis.get('return_rate_pct', 0)
    if return_rate > 10:
        recommendations.append(f"High return rate ({return_rate:.1f}%) impacting profitability. Review product descriptions and quality.")
    
    if not recommendations:
        recommendations.append("All metrics within normal range. Proceed with planned promotional strategy.")
    
    return recommendations

def generate_manager_alerts(stockout_risk, kpis, issues_df=None):
    """Generate operational alerts for Manager view."""
    alerts = []
    
    # Stockout alerts
    if stockout_risk.get('stockout_risk_pct', 0) > 15:
        alerts.append(f"⚠️ HIGH: {stockout_risk['stockout_risk_pct']:.0f}% of SKUs at stockout risk. Expedite reorders.")
    
    if stockout_risk.get('zero_stock', 0) > 0:
        alerts.append(f"🔴 CRITICAL: {stockout_risk['zero_stock']} items currently out of stock!")
    
    # Payment failure
    failure_rate = kpis.get('payment_failure_rate_pct', 0)
    if failure_rate > 5:
        alerts.append(f"⚠️ Payment failure rate at {failure_rate:.1f}%. Investigate gateway issues.")
    
    # Issues
    if issues_df is not None and len(issues_df) > 0:
        alerts.append(f"📋 {len(issues_df)} data quality issues detected and logged. Review issues log.")
    
    if not alerts:
        alerts.append("✅ All operational metrics within acceptable thresholds.")
    
    return alerts

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
if 'cleaner_stats' not in st.session_state:
    st.session_state.cleaner_stats = None

# ============================================================================
# SIDEBAR NAVIGATION & FILTERS
# ============================================================================

with st.sidebar:
    # Title
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
        ">Promo Pulse</div>
        <div style="color: #94a3b8; font-size: 13px;">UAE Retail Analytics</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown('<p style="color: #ec4899; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📍 NAVIGATION</p>', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📂 Data Upload", "🧹 Data Rescue", "🎯 Simulator", "📊 Dashboard", "🔧 Faculty Test"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # ===== GLOBAL FILTERS (5 Required) - FIXED VERSION =====
    if st.session_state.data_loaded:
        st.markdown('<p style="color: #06b6d4; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">🎛️ GLOBAL FILTERS</p>', unsafe_allow_html=True)
        
        sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
        stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
        products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
        
        # Filter 1: Date Range
        if sales_df is not None and 'order_time' in sales_df.columns:
            try:
                temp_sales = sales_df.copy()
                temp_sales['order_time'] = pd.to_datetime(temp_sales['order_time'], errors='coerce')
                min_date = temp_sales['order_time'].min()
                max_date = temp_sales['order_time'].max()
                if pd.notna(min_date) and pd.notna(max_date):
                    st.date_input(
                        "📅 Date Range",
                        value=(min_date.date(), max_date.date()),
                        min_value=min_date.date(),
                        max_value=max_date.date(),
                        key='filter_date_range'
                    )
            except:
                pass
        
        # Filter 2: City
        cities = ['All']
        if stores_df is not None and 'city' in stores_df.columns:
            cities += sorted([str(c) for c in stores_df['city'].dropna().unique().tolist()])
        st.selectbox("🏙️ City", cities, key='filter_city')
        
        # Filter 3: Channel
        channels = ['All']
        if stores_df is not None and 'channel' in stores_df.columns:
            channels += sorted([str(c) for c in stores_df['channel'].dropna().unique().tolist()])
        st.selectbox("📱 Channel", channels, key='filter_channel')
        
        # Filter 4: Category
        categories = ['All']
        if products_df is not None and 'category' in products_df.columns:
            categories += sorted([str(c) for c in products_df['category'].dropna().unique().tolist()])
        st.selectbox("📦 Category", categories, key='filter_category')
        
        # Filter 5: Brand
        brands = ['All']
        if products_df is not None and 'brand' in products_df.columns:
            brand_list = [str(b) for b in products_df['brand'].dropna().unique().tolist()]
            brands += sorted(brand_list)[:20]  # Limit to 20
        st.selectbox("🏷️ Brand", brands, key='filter_brand')
        
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

# ============================================================================
# HELPER: Apply Global Filters
# ============================================================================

def apply_filters(sales_df, stores_df, products_df):
    """Apply global sidebar filters to dataframes."""
    if sales_df is None:
        return sales_df
    
    filtered_sales = sales_df.copy()
    
    # Date filter
    if 'filter_date_range' in st.session_state and st.session_state.filter_date_range:
        try:
            date_range = st.session_state.filter_date_range
            if len(date_range) == 2:
                filtered_sales['order_time'] = pd.to_datetime(filtered_sales['order_time'], errors='coerce')
                filtered_sales = filtered_sales[
                    (filtered_sales['order_time'].dt.date >= date_range[0]) &
                    (filtered_sales['order_time'].dt.date <= date_range[1])
                ]
        except:
            pass
    
    # City filter
    if 'filter_city' in st.session_state and st.session_state.filter_city != 'All':
        if stores_df is not None and 'store_id' in filtered_sales.columns:
            city_stores = stores_df[stores_df['city'] == st.session_state.filter_city]['store_id'].tolist()
            filtered_sales = filtered_sales[filtered_sales['store_id'].isin(city_stores)]
    
    # Channel filter
    if 'filter_channel' in st.session_state and st.session_state.filter_channel != 'All':
        if stores_df is not None and 'store_id' in filtered_sales.columns:
            channel_stores = stores_df[stores_df['channel'] == st.session_state.filter_channel]['store_id'].tolist()
            filtered_sales = filtered_sales[filtered_sales['store_id'].isin(channel_stores)]
    
    # Category filter
    if 'filter_category' in st.session_state and st.session_state.filter_category != 'All':
        if products_df is not None and 'product_id' in filtered_sales.columns:
            cat_products = products_df[products_df['category'] == st.session_state.filter_category]['product_id'].tolist()
            filtered_sales = filtered_sales[filtered_sales['product_id'].isin(cat_products)]
    
    # Brand filter
    if 'filter_brand' in st.session_state and st.session_state.filter_brand != 'All':
        if products_df is not None and 'product_id' in filtered_sales.columns:
            brand_products = products_df[products_df['brand'] == st.session_state.filter_brand]['product_id'].tolist()
            filtered_sales = filtered_sales[filtered_sales['product_id'].isin(brand_products)]
    
    return filtered_sales

# ============================================================================
# PAGE: HOME (ORIGINAL CONTENT PRESERVED)
# ============================================================================

def show_home_page():
    """Display the home page."""
    
    if not st.session_state.data_loaded:
        # ===== HERO SECTION (NO DATA LOADED) - ORIGINAL CONTENT =====
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
            ">Promo Pulse Simulator</div>
            <p style="color: #94a3b8; font-size: 1.15rem; margin: 0; line-height: 1.6;">
                Data Rescue Toolkit + What-If Campaign Simulation<br>
                For UAE Omnichannel Retailers: Dubai • Abu Dhabi • Sharjah
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # ===== FEATURE CARDS =====
        st.markdown('<p class="section-title section-title-purple">✨ Key Features</p>', unsafe_allow_html=True)
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
                "📊", "Dashboard", 
                "Executive & Manager views with real-time KPIs",
                "pink"
            ), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ===== WORKFLOW SECTION =====
        st.markdown('<p class="section-title section-title-teal">🔄 How It Works</p>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="info-card">
                <h4 style="color: #06b6d4; margin-top: 0; font-size: 1.1rem;">📥 Phase 1: Data Rescue Toolkit</h4>
                <ul style="color: #94a3b8; margin-bottom: 0; font-size: 0.95rem; line-height: 1.8;">
                    <li>Upload dirty/raw datasets (CSV)</li>
                    <li>Automatic validation & issue detection</li>
                    <li>Clean data with documented fixes</li>
                    <li>Download issues log & cleaned data</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-card" style="border-left-color: #8b5cf6;">
                <h4 style="color: #8b5cf6; margin-top: 0; font-size: 1.1rem;">🎯 Phase 2: Promo Pulse Simulator</h4>
                <ul style="color: #94a3b8; margin-bottom: 0; font-size: 0.95rem; line-height: 1.8;">
                    <li>Set discount %, budget & margin floor</li>
                    <li>Target by city, channel, category</li>
                    <li>See projected ROI & demand lift</li>
                    <li>Constraint violation warnings</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ===== GETTING STARTED =====
        st.markdown('<p class="section-title section-title-orange">🚀 Get Started</p>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card" style="border-left-color: #f59e0b; text-align: center;">
            <p style="color: #e2e8f0; font-size: 1.1rem; margin: 0;">
                👈 Use the sidebar to navigate to <strong style="color: #06b6d4;">📂 Data Upload</strong> and load your data files.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # ===== DATA LOADED - SIMPLE STATUS VIEW (NO INSIGHTS HERE) =====
        st.markdown("""
        <div style="text-align: center; margin-bottom: 40px; padding: 30px 0;">
            <div style="font-size: 56px; margin-bottom: 15px;">🛒</div>
            <div style="
                font-size: 52px;
                font-weight: 800;
                background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 15px;
                line-height: 1.2;
            ">Promo Pulse Simulator</div>
            <p style="color: #94a3b8; font-size: 1.15rem; margin: 0;">Data Rescue + Campaign Simulation Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        # ===== QUICK STATUS CARDS =====
        st.markdown('<p class="section-title section-title-cyan">📡 Current Status</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Get counts
        products_count = len(st.session_state.raw_products) if st.session_state.raw_products is not None else 0
        stores_count = len(st.session_state.raw_stores) if st.session_state.raw_stores is not None else 0
        sales_count = len(st.session_state.raw_sales) if st.session_state.raw_sales is not None else 0
        inventory_count = len(st.session_state.raw_inventory) if st.session_state.raw_inventory is not None else 0
        
        with col1:
            st.markdown(create_metric_card("Products", f"{products_count:,}", color="cyan"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("Stores", f"{stores_count:,}", color="blue"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card("Sales Records", f"{sales_count:,}", color="purple"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card("Inventory", f"{inventory_count:,}", color="pink"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ===== STATUS MESSAGES =====
        if st.session_state.is_cleaned:
            st.markdown(create_success_card("Data has been cleaned and validated. Ready for simulation and analysis!"), unsafe_allow_html=True)
        else:
            st.markdown(create_warning_card("Data loaded but not yet cleaned. Go to <strong>🧹 Data Rescue</strong> to validate and fix issues."), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ===== NEXT STEPS GUIDE =====
        st.markdown('<p class="section-title section-title-purple">📋 Next Steps</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            step_status = "✅" if st.session_state.is_cleaned else "⏳"
            st.markdown(f"""
            <div class="info-card">
                <h4 style="color: #06b6d4; margin-top: 0;">{step_status} Step 1: Clean Data</h4>
                <p style="color: #94a3b8; margin-bottom: 0;">Go to <strong>🧹 Data Rescue</strong> to validate and fix data quality issues.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            step_status = "✅" if st.session_state.sim_results else "⏳"
            st.markdown(f"""
            <div class="info-card" style="border-left-color: #8b5cf6;">
                <h4 style="color: #8b5cf6; margin-top: 0;">{step_status} Step 2: Run Simulation</h4>
                <p style="color: #94a3b8; margin-bottom: 0;">Go to <strong>🎯 Simulator</strong> to test discount scenarios.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="info-card" style="border-left-color: #ec4899;">
                <h4 style="color: #ec4899; margin-top: 0;">📊 Step 3: View Dashboard</h4>
                <p style="color: #94a3b8; margin-bottom: 0;">Go to <strong>📊 Dashboard</strong> for Executive & Manager insights.</p>
            </div>
            """, unsafe_allow_html=True)
    
    show_footer()

# ============================================================================
# PAGE: DATA UPLOAD
# ============================================================================

def show_data_page():
    """Display the data upload page."""
    
    st.markdown('<h1 class="page-title page-title-cyan">📂 Data Upload</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Upload your e-commerce data files or load sample data</p>', unsafe_allow_html=True)
    
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
        if st.button("📥 Load Uploaded Files", use_container_width=True):
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
    
    # Sample data
    st.markdown('<p class="section-title section-title-purple">📦 Or Load Sample Data</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📥 Load Sample Data", use_container_width=True):
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
    
    # Preview
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
                st.dataframe(df.head(100), use_container_width=True)
        
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
                st.dataframe(df.head(100), use_container_width=True)
        
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
                st.dataframe(df.head(100), use_container_width=True)
        
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
                st.dataframe(df.head(100), use_container_width=True)
    
    show_footer()

# ============================================================================
# PAGE: DATA RESCUE (CLEANER)
# ============================================================================

def show_cleaner_page():
    """Display the data rescue page."""
    
    st.markdown('<h1 class="page-title page-title-green">🧹 Data Rescue Center</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Validate, detect issues, and clean your data automatically</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card("Please load data first. Go to 📂 Data Upload page."), unsafe_allow_html=True)
        show_footer()
        return
    
    # Issue types
    st.markdown('<p class="section-title section-title-cyan">🔍 Issues We Detect & Fix</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <strong style="color: #06b6d4;">Data Quality</strong>
            <ul style="color: #94a3b8; margin-bottom: 0;">
                <li>Missing values</li>
                <li>Duplicate records</li>
                <li>Null representations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card" style="border-left-color: #8b5cf6;">
            <strong style="color: #8b5cf6;">Format Issues</strong>
            <ul style="color: #94a3b8; margin-bottom: 0;">
                <li>Invalid timestamps</li>
                <li>Inconsistent cities</li>
                <li>Mixed case values</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card" style="border-left-color: #ec4899;">
            <strong style="color: #ec4899;">Value Issues</strong>
            <ul style="color: #94a3b8; margin-bottom: 0;">
                <li>Outliers & negatives</li>
                <li>FK violations</li>
                <li>Invalid categories</li>
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
                    st.session_state.is_cleaned = True
                    
                    st.success("✅ Data cleaning complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Results
    if st.session_state.is_cleaned:
        st.markdown("---")
        st.markdown('<p class="section-title section-title-blue">📊 Cleaning Results</p>', unsafe_allow_html=True)
        
        stats = st.session_state.cleaner_stats
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                before = stats.get('products', {}).get('before', 0)
                after = stats.get('products', {}).get('after', 0)
                delta = f"{before - after} removed" if before > after else "No change"
                delta_type = "negative" if before > after else "positive"
                st.markdown(create_metric_card("Products", f"{after:,}", delta, delta_type, "cyan"), unsafe_allow_html=True)
            
            with col2:
                before = stats.get('stores', {}).get('before', 0)
                after = stats.get('stores', {}).get('after', 0)
                delta = f"{before - after} removed" if before > after else "No change"
                delta_type = "negative" if before > after else "positive"
                st.markdown(create_metric_card("Stores", f"{after:,}", delta, delta_type, "blue"), unsafe_allow_html=True)
            
            with col3:
                before = stats.get('sales', {}).get('before', 0)
                after = stats.get('sales', {}).get('after', 0)
                delta = f"{before - after} removed" if before > after else "No change"
                delta_type = "negative" if before > after else "positive"
                st.markdown(create_metric_card("Sales", f"{after:,}", delta, delta_type, "purple"), unsafe_allow_html=True)
            
            with col4:
                before = stats.get('inventory', {}).get('before', 0)
                after = stats.get('inventory', {}).get('after', 0)
                delta = f"{before - after} removed" if before > after else "No change"
                delta_type = "negative" if before > after else "positive"
                st.markdown(create_metric_card("Inventory", f"{after:,}", delta, delta_type, "pink"), unsafe_allow_html=True)
        
        issues_df = st.session_state.issues_df
        
        if issues_df is not None and len(issues_df) > 0:
            st.markdown("---")
            st.markdown('<p class="section-title section-title-teal">🔍 Issues Detected & Fixed</p>', unsafe_allow_html=True)
            
            st.markdown(create_success_card(f"Total {len(issues_df)} issues detected and fixed automatically!"), unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Issues by type
                issue_counts = issues_df['issue_type'].value_counts().reset_index()
                issue_counts.columns = ['Issue Type', 'Count']
                
                fig = px.bar(issue_counts, x='Count', y='Issue Type', orientation='h',
                           title='Issues by Type', color='Count',
                           color_continuous_scale=['#06b6d4', '#8b5cf6'])
                fig = style_plotly_chart(fig)
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Pareto chart
                issue_counts_sorted = issue_counts.sort_values('Count', ascending=False)
                issue_counts_sorted['Cumulative %'] = (issue_counts_sorted['Count'].cumsum() / issue_counts_sorted['Count'].sum() * 100)
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(go.Bar(x=issue_counts_sorted['Issue Type'], y=issue_counts_sorted['Count'],
                                    name='Count', marker_color='#06b6d4'), secondary_y=False)
                fig.add_trace(go.Scatter(x=issue_counts_sorted['Issue Type'], y=issue_counts_sorted['Cumulative %'],
                                        name='Cumulative %', marker_color='#ec4899', mode='lines+markers'),
                             secondary_y=True)
                fig = style_plotly_chart(fig)
                fig.update_layout(title='Pareto Chart of Issues')
                st.plotly_chart(fig, use_container_width=True)
            
            # Issues table + download
            st.markdown('<p class="section-title section-title-purple">📋 Issues Log</p>', unsafe_allow_html=True)
            st.dataframe(issues_df, use_container_width=True)
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                csv_issues = issues_df.to_csv(index=False)
                st.download_button("📥 Download Issues Log (CSV)", csv_issues, "issues.csv", "text/csv")
            
            with col2:
                if st.session_state.clean_sales is not None:
                    csv_sales = st.session_state.clean_sales.to_csv(index=False)
                    st.download_button("📥 Download Cleaned Sales (CSV)", csv_sales, "cleaned_sales.csv", "text/csv")
        else:
            st.markdown(create_success_card("No issues found! Your data is already clean."), unsafe_allow_html=True)
    
    show_footer()

# ============================================================================
# PAGE: SIMULATOR
# ============================================================================

def show_simulator_page():
    """Display the simulator page."""
    
    st.markdown('<h1 class="page-title page-title-purple">🎯 Promo Pulse Simulator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Run what-if discount scenarios with budget & margin constraints</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card("Please load data first."), unsafe_allow_html=True)
        show_footer()
        return
    
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    
    st.markdown('<p class="section-title section-title-cyan">⚙️ Campaign Parameters</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p style="color: #06b6d4; font-weight: 600;">💰 Pricing</p>', unsafe_allow_html=True)
        discount_pct = st.slider("Discount %", 0, 50, 15, key='sim_discount')
        promo_budget = st.number_input("Promo Budget (AED)", 1000, 500000, 25000, step=5000, key='sim_budget')
    
    with col2:
        st.markdown('<p style="color: #8b5cf6; font-weight: 600;">📊 Constraints</p>', unsafe_allow_html=True)
        margin_floor = st.slider("Margin Floor %", 0, 50, 15, key='sim_margin')
        campaign_days = st.slider("Campaign Days", 1, 30, 7, key='sim_days')
    
    with col3:
        st.markdown('<p style="color: #ec4899; font-weight: 600;">🎯 Targeting</p>', unsafe_allow_html=True)
        
        cities = ['All']
        channels = ['All']
        categories = ['All']
        
        if stores_df is not None and 'city' in stores_df.columns:
            cities += [str(c) for c in stores_df['city'].dropna().unique().tolist()]
        if stores_df is not None and 'channel' in stores_df.columns:
            channels += [str(c) for c in stores_df['channel'].dropna().unique().tolist()]
        if products_df is not None and 'category' in products_df.columns:
            categories += [str(c) for c in products_df['category'].dropna().unique().tolist()]
        
        city = st.selectbox("Target City", cities, key='sim_city')
        channel = st.selectbox("Target Channel", channels, key='sim_channel')
        category = st.selectbox("Target Category", categories, key='sim_category')
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        run_sim = st.button("🚀 Run Simulation", use_container_width=True, type="primary")
    
    if run_sim:
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
                st.error(f"❌ Error: {str(e)}")
    
    # Results
    if st.session_state.sim_results:
        results = st.session_state.sim_results
        outputs = results.get('outputs', {})
        comparison = results.get('comparison', {})
        warnings = results.get('warnings', [])
        constraint_violations = results.get('constraint_violations', [])
        
        st.markdown("---")
        st.markdown('<p class="section-title section-title-teal">📊 Simulation Results</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            delta = f"{comparison.get('revenue_change_pct', 0):+.1f}%"
            delta_type = "positive" if comparison.get('revenue_change_pct', 0) > 0 else "negative"
            st.markdown(create_metric_card("Expected Revenue", f"AED {outputs.get('expected_revenue', 0):,.0f}", delta, delta_type, "cyan"), unsafe_allow_html=True)
        
        with col2:
            delta = f"{comparison.get('profit_change_pct', 0):+.1f}%"
            delta_type = "positive" if comparison.get('profit_change_pct', 0) > 0 else "negative"
            st.markdown(create_metric_card("Net Profit", f"AED {outputs.get('expected_net_profit', 0):,.0f}", delta, delta_type, "green"), unsafe_allow_html=True)
        
        with col3:
            roi = outputs.get('roi_pct', 0)
            color = "green" if roi > 0 else "pink"
            st.markdown(create_metric_card("ROI", f"{roi:.1f}%", color=color), unsafe_allow_html=True)
        
        with col4:
            budget_util = (outputs.get('promo_cost', 0) / promo_budget * 100) if promo_budget > 0 else 0
            st.markdown(create_metric_card("Budget Used", f"{budget_util:.1f}%", color="orange"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card("Demand Lift", f"+{outputs.get('demand_lift_pct', 0):.1f}%", color="purple"), unsafe_allow_html=True)
        
        with col2:
            margin_result = outputs.get('expected_margin_pct', 0)
            color = "green" if margin_result >= margin_floor else "orange"
            st.markdown(create_metric_card("Exp. Margin", f"{margin_result:.1f}%", color=color), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_metric_card("Promo Cost", f"AED {outputs.get('promo_cost', 0):,.0f}", color="orange"), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_metric_card("Expected Orders", f"{outputs.get('expected_orders', 0):,}", color="blue"), unsafe_allow_html=True)
        
        # Constraint violations
        if constraint_violations:
            st.markdown("---")
            st.markdown('<p class="section-title section-title-orange">⚠️ Constraint Violations</p>', unsafe_allow_html=True)
            for v in constraint_violations:
                st.error(f"❌ {v.get('constraint', 'Unknown')}: {v.get('message', 'No details')}")
                if 'top_contributors' in v and v['top_contributors']:
                    st.markdown("**Top 10 Contributors:**")
                    st.dataframe(pd.DataFrame(v['top_contributors']).head(10), use_container_width=True)
        
        if warnings:
            st.markdown("---")
            for w in warnings:
                st.warning(w)
        
        if not warnings and not constraint_violations:
            st.markdown("---")
            st.success("✅ All metrics within acceptable range. Campaign looks healthy!")
        
        # Comparison chart
        st.markdown("---")
        st.markdown('<p class="section-title section-title-blue">📈 Baseline vs Campaign</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            comp_data = pd.DataFrame({
                'Metric': ['Revenue', 'Profit'],
                'Baseline': [comparison.get('baseline_revenue', 0), comparison.get('baseline_profit', 0)],
                'Campaign': [outputs.get('expected_revenue', 0), outputs.get('expected_net_profit', 0)]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Baseline', x=comp_data['Metric'], y=comp_data['Baseline'], marker_color='#3b82f6'))
            fig.add_trace(go.Bar(name='Campaign', x=comp_data['Metric'], y=comp_data['Campaign'], marker_color='#06b6d4'))
            fig = style_plotly_chart(fig)
            fig.update_layout(barmode='group', title='Revenue & Profit Comparison')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            orders_data = pd.DataFrame({
                'Type': ['Baseline', 'Campaign'],
                'Orders': [comparison.get('baseline_orders', 0), outputs.get('expected_orders', 0)]
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
            st.plotly_chart(fig, use_container_width=True)
    
    show_footer()

# ============================================================================
# PAGE: DASHBOARD (EXECUTIVE vs MANAGER TOGGLE)
# ============================================================================

def show_dashboard_page():
    """Display the dashboard with Executive/Manager toggle."""
    
    st.markdown('<h1 class="page-title page-title-pink">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card("Please load data first."), unsafe_allow_html=True)
        show_footer()
        return
    
    # ===== VIEW TOGGLE (MANDATORY) =====
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        view = st.radio(
            "Select Dashboard View",
            ["👔 Executive View", "⚙️ Manager View"],
            horizontal=True,
            key='dashboard_view_toggle'
        )
    st.markdown("---")
    
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    inventory_df = st.session_state.clean_inventory if st.session_state.is_cleaned else st.session_state.raw_inventory
    
    # Apply filters
    filtered_sales = apply_filters(sales_df, stores_df, products_df)
    
    sim = Simulator()
    kpis = sim.calculate_overall_kpis(filtered_sales, products_df)
    
    if view == "👔 Executive View":
        show_executive_view(filtered_sales, stores_df, products_df, kpis, sim)
    else:
        show_manager_view(filtered_sales, stores_df, products_df, inventory_df, kpis, sim)
    
    show_footer()

def show_executive_view(sales_df, stores_df, products_df, kpis, sim):
    """Executive View: Strategic KPIs, Insights, and Recommendations."""
    
    st.markdown('<p class="section-title section-title-cyan">💼 Executive Dashboard</p>', unsafe_allow_html=True)
    
    # KPI Cards Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card("Net Revenue", f"AED {kpis.get('net_revenue', kpis.get('total_revenue', 0)):,.0f}", color="cyan"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Gross Margin %", f"{kpis.get('profit_margin_pct', 0):.1f}%", color="green"), unsafe_allow_html=True)
    with col3:
        profit_proxy = kpis.get('total_profit', 0)
        st.markdown(create_metric_card("Profit Proxy", f"AED {profit_proxy:,.0f}", color="purple"), unsafe_allow_html=True)
    with col4:
        budget_util = 0
        if st.session_state.sim_results:
            outputs = st.session_state.sim_results.get('outputs', {})
            budget_util = outputs.get('budget_utilization_pct', 0)
        st.markdown(create_metric_card("Budget Util.", f"{budget_util:.1f}%", color="orange"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # KPI Cards Row 2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card("Total Orders", f"{kpis.get('total_orders', 0):,}", color="blue"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Avg Order Value", f"AED {kpis.get('avg_order_value', 0):,.0f}", color="teal"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Avg Discount %", f"{kpis.get('avg_discount_pct', 0):.1f}%", color="orange"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("Return Rate %", f"{kpis.get('return_rate_pct', 0):.1f}%", color="pink"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Calculate dimension KPIs
    city_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'city')
    channel_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'channel')
    cat_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'category')
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        # Chart 1: Revenue trend
        daily = sim.calculate_daily_trends(sales_df, products_df)
        if daily is not None and len(daily) > 0:
            fig = px.area(daily, x='date', y='revenue', title='📈 Net Revenue Trend',
                         color_discrete_sequence=['#06b6d4'])
            fig = style_plotly_chart(fig)
            fig.update_traces(line=dict(width=3), fillcolor='rgba(6, 182, 212, 0.2)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trend data available.")
    
    with col2:
        # Chart 2: Revenue by city
        if city_kpis is not None and len(city_kpis) > 0:
            fig = px.bar(city_kpis, x='city', y='revenue', title='🏙️ Revenue by City',
                        color='city', color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6'])
            fig = style_plotly_chart(fig)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No city data available.")
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        # Chart 3: Margin by category
        if cat_kpis is not None and len(cat_kpis) > 0:
            fig = px.bar(cat_kpis, x='category', y='profit_margin_pct', title='📦 Margin % by Category',
                        color='profit_margin_pct', color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'])
            fig = style_plotly_chart(fig)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available.")
    
    with col2:
        # Chart 4: Scenario impact or channel revenue
        if st.session_state.sim_results:
            comparison = st.session_state.sim_results.get('comparison', {})
            sim_outputs = st.session_state.sim_results.get('outputs', {})
            impact_data = pd.DataFrame({
                'Metric': ['Baseline Profit', 'Simulated Profit'],
                'Value': [comparison.get('baseline_profit', 0), sim_outputs.get('expected_net_profit', 0)]
            })
            fig = px.bar(impact_data, x='Metric', y='Value', title='🎯 Scenario Impact: Profit',
                        color='Metric', color_discrete_sequence=['#3b82f6', '#10b981'])
            fig = style_plotly_chart(fig)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            if channel_kpis is not None and len(channel_kpis) > 0:
                fig = px.pie(channel_kpis, values='revenue', names='channel', title='📱 Revenue by Channel',
                            color_discrete_sequence=['#10b981', '#f59e0b', '#ec4899'], hole=0.45)
                fig = style_plotly_chart(fig)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Run simulation to see scenario impact chart.")
    
    st.markdown("---")
    
    # ===== KEY BUSINESS INSIGHTS =====
    st.markdown('<p class="section-title section-title-purple">💡 Key Business Insights</p>', unsafe_allow_html=True)
    
    insights = generate_insights(kpis, city_kpis, channel_kpis, cat_kpis)
    
    if insights:
        for title, text in insights:
            st.markdown(create_insight_card(title, text), unsafe_allow_html=True)
    else:
        st.markdown(create_info_card("Analyze more data to generate business insights."), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== RECOMMENDATION BOX =====
    st.markdown('<p class="section-title section-title-green">📋 Strategic Recommendations</p>', unsafe_allow_html=True)
    
    recommendations = generate_executive_recommendations(kpis, st.session_state.sim_results)
    st.markdown(create_recommendation_box("Action Items for Leadership", recommendations), unsafe_allow_html=True)

def show_manager_view(sales_df, stores_df, products_df, inventory_df, kpis, sim):
    """Manager View: Operational KPIs and risks."""
    
    st.markdown('<p class="section-title section-title-orange">⚙️ Operations Dashboard</p>', unsafe_allow_html=True)
    
    # Calculate operational metrics
    stockout = sim.calculate_stockout_risk(inventory_df)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        color = "pink" if stockout.get('stockout_risk_pct', 0) > 15 else "green"
        st.markdown(create_metric_card("Stockout Risk %", f"{stockout.get('stockout_risk_pct', 0):.1f}%", color=color), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Return Rate %", f"{kpis.get('return_rate_pct', 0):.1f}%", color="orange"), unsafe_allow_html=True)
    with col3:
        failure_rate = kpis.get('payment_failure_rate_pct', 0)
        color = "pink" if failure_rate > 5 else "green"
        st.markdown(create_metric_card("Payment Fail %", f"{failure_rate:.1f}%", color=color), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("High-Risk SKUs", f"{stockout.get('low_stock_items', 0):,}", color="purple"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Chart 1: Stockout risk by city
        if inventory_df is not None and stores_df is not None:
            try:
                inv_merged = inventory_df.merge(stores_df[['store_id', 'city']], on='store_id', how='left')
                inv_merged['stock_on_hand'] = pd.to_numeric(inv_merged['stock_on_hand'], errors='coerce').fillna(0)
                inv_merged['reorder_point'] = pd.to_numeric(inv_merged.get('reorder_point', 10), errors='coerce').fillna(10)
                inv_merged['at_risk'] = inv_merged['stock_on_hand'] <= inv_merged['reorder_point']
                
                risk_by_city = inv_merged.groupby('city').agg({
                    'at_risk': 'mean'
                }).reset_index()
                risk_by_city['risk_pct'] = risk_by_city['at_risk'] * 100
                
                fig = px.bar(risk_by_city, x='city', y='risk_pct', title='🏙️ Stockout Risk % by City',
                            color='risk_pct', color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'])
                fig = style_plotly_chart(fig)
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.info("Unable to calculate stockout by city.")
    
    with col2:
        # Chart 2: Top 10 risk items
        if inventory_df is not None:
            try:
                inv_copy = inventory_df.copy()
                inv_copy['stock_on_hand'] = pd.to_numeric(inv_copy['stock_on_hand'], errors='coerce').fillna(0)
                inv_copy['reorder_point'] = pd.to_numeric(inv_copy.get('reorder_point', 10), errors='coerce').fillna(10)
                inv_copy['risk_score'] = inv_copy['reorder_point'] - inv_copy['stock_on_hand']
                top_risk = inv_copy.nlargest(10, 'risk_score')[['product_id', 'store_id', 'stock_on_hand', 'risk_score']]
                
                st.markdown("**📋 Top 10 Stockout Risk Items**")
                st.dataframe(top_risk, use_container_width=True, height=300)
            except:
                st.info("Unable to calculate top risk items.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Chart 3: Inventory distribution
        if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
            fig = px.histogram(inventory_df, x='stock_on_hand', nbins=50, title='📦 Stock Level Distribution',
                             color_discrete_sequence=['#8b5cf6'])
            fig = style_plotly_chart(fig)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Chart 4: Pareto of issues
        if st.session_state.issues_df is not None and len(st.session_state.issues_df) > 0:
            issues_df = st.session_state.issues_df
            issue_counts = issues_df['issue_type'].value_counts().head(10).reset_index()
            issue_counts.columns = ['Issue Type', 'Count']
            
            fig = px.bar(issue_counts, x='Issue Type', y='Count', title='🔍 Top Data Issues',
                        color='Count', color_continuous_scale=['#06b6d4', '#ec4899'])
            fig = style_plotly_chart(fig)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Run Data Rescue to see issues distribution.")
    
    st.markdown("---")
    
    # Operational Alerts
    st.markdown('<p class="section-title section-title-pink">🚨 Operational Alerts</p>', unsafe_allow_html=True)
    
    alerts = generate_manager_alerts(stockout, kpis, st.session_state.issues_df)
    
    for alert in alerts:
        if "CRITICAL" in alert or "🔴" in alert:
            st.markdown(create_error_card(alert), unsafe_allow_html=True)
        elif "HIGH" in alert or "⚠️" in alert:
            st.markdown(create_warning_card(alert), unsafe_allow_html=True)
        else:
            st.markdown(create_info_card(alert), unsafe_allow_html=True)

# ============================================================================
# PAGE: FACULTY TEST (Column Mapping)
# ============================================================================

def show_faculty_test_page():
    """Faculty dataset testing with column mapping."""
    
    st.markdown('<h1 class="page-title page-title-teal">🔧 Faculty Dataset Test</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Upload faculty-provided dataset and map columns to expected schema</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Upload
    st.markdown('<p class="section-title section-title-cyan">📤 Upload Faculty Dataset</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload CSV/Excel file", type=['csv', 'xlsx'], key='faculty_upload')
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                faculty_df = pd.read_excel(uploaded_file)
            else:
                faculty_df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ File loaded: {len(faculty_df)} rows, {len(faculty_df.columns)} columns")
            
            # Display columns
            st.markdown('<p class="section-title section-title-blue">📋 Detected Columns</p>', unsafe_allow_html=True)
            st.write(faculty_df.columns.tolist())
            
            st.markdown("---")
            
            # Column mapping
            st.markdown('<p class="section-title section-title-purple">🔗 Column Mapping</p>', unsafe_allow_html=True)
            st.markdown("Map your dataset columns to the expected schema:")
            
            available_cols = ['-- Not Mapped --'] + faculty_df.columns.tolist()
            
            # Expected schema
            expected_cols = {
                'Sales': ['order_id', 'order_time', 'product_id', 'store_id', 'qty', 'selling_price_aed', 'discount_pct', 'payment_status', 'return_flag'],
                'Products': ['product_id', 'category', 'brand', 'base_price_aed', 'unit_cost_aed'],
                'Stores': ['store_id', 'city', 'channel', 'fulfillment_type'],
                'Inventory': ['product_id', 'store_id', 'stock_on_hand', 'reorder_point']
            }
            
            # Select table type
            table_type = st.selectbox("What type of data is this?", list(expected_cols.keys()))
            
            st.markdown(f"**Expected columns for {table_type}:**")
            
            mappings = {}
            cols = st.columns(3)
            for i, expected_col in enumerate(expected_cols[table_type]):
                with cols[i % 3]:
                    mappings[expected_col] = st.selectbox(
                        f"Map to: {expected_col}",
                        available_cols,
                        key=f'map_{expected_col}'
                    )
            
            st.markdown("---")
            
            if st.button("✅ Apply Mapping & Validate", use_container_width=True):
                # Apply mapping
                mapped_df = pd.DataFrame()
                for expected_col, source_col in mappings.items():
                    if source_col != '-- Not Mapped --':
                        mapped_df[expected_col] = faculty_df[source_col]
                    else:
                        mapped_df[expected_col] = None
                
                st.success(f"✅ Mapped {len([v for v in mappings.values() if v != '-- Not Mapped --'])} columns")
                
                # Store in session state
                if table_type == 'Sales':
                    st.session_state.raw_sales = mapped_df
                elif table_type == 'Products':
                    st.session_state.raw_products = mapped_df
                elif table_type == 'Stores':
                    st.session_state.raw_stores = mapped_df
                elif table_type == 'Inventory':
                    st.session_state.raw_inventory = mapped_df
                
                st.session_state.data_loaded = True
                st.session_state.is_cleaned = False
                
                # Validation
                st.markdown('<p class="section-title section-title-green">🔍 Validation Results</p>', unsafe_allow_html=True)
                
                issues = []
                
                # Check for nulls
                for col in mapped_df.columns:
                    null_count = mapped_df[col].isnull().sum()
                    if null_count > 0:
                        issues.append(f"Column '{col}': {null_count} null values ({null_count/len(mapped_df)*100:.1f}%)")
                
                # Check for duplicates
                if 'order_id' in mapped_df.columns:
                    dupes = mapped_df['order_id'].duplicated().sum()
                    if dupes > 0:
                        issues.append(f"Found {dupes} duplicate order_ids")
                
                if issues:
                    st.warning("⚠️ Issues Detected:")
                    for issue in issues:
                        st.write(f"• {issue}")
                else:
                    st.success("✅ No major issues detected!")
                
                # Preview
                st.markdown("**Mapped Data Preview:**")
                st.dataframe(mapped_df.head(20), use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    show_footer()

# ============================================================================
# MAIN ROUTING
# ============================================================================

if page == "🏠 Home":
    show_home_page()
elif page == "📂 Data Upload":
    show_data_page()
elif page == "🧹 Data Rescue":
    show_cleaner_page()
elif page == "🎯 Simulator":
    show_simulator_page()
elif page == "📊 Dashboard":
    show_dashboard_page()
elif page == "🔧 Faculty Test":
    show_faculty_test_page()
