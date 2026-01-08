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
        ["🏠 Home", "📂 Data", "🧹 Cleaner", "🎯 Simulator", "📊 Analytics"],
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
# ============================================================================
# PAGE: HOME
# ============================================================================

# ============================================================================
# PAGE: HOME (FIXED - BIG TITLE, BETTER LAYOUT)
# ============================================================================

def show_home_page():
    """Display the enhanced home page."""
    
    if not st.session_state.data_loaded:
        # ===== HERO SECTION (NO DATA LOADED) =====
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
    
    else:
        # ===== DATA LOADED - SHOW KPI DASHBOARD =====
        sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
        products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
        stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
        
        # ===== BIG STYLED TITLE (AFTER DATA LOADED) =====
        st.markdown("""
        <div style="text-align: center; margin-bottom: 40px; padding: 20px 0;">
            <div style="font-size: 48px; margin-bottom: 10px;">🛒</div>
            <div style="
                font-size: 56px;
                font-weight: 800;
                background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 15px;
                line-height: 1.2;
            ">UAE Pulse Simulator</div>
            <p style="color: #94a3b8; font-size: 1.2rem; margin: 0;">Data Rescue + Campaign Simulation Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize simulator
        sim = Simulator()
        
        # Calculate KPIs
        kpis = sim.calculate_overall_kpis(sales_df, products_df)
        
        st.markdown('<p class="section-title section-title-cyan">📈 Key Performance Indicators</p>', unsafe_allow_html=True)
        
        # ===== KPI CARDS ROW 1 =====
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
        st.markdown('<p class="section-title section-title-blue">📊 Quick Overview</p>', unsafe_allow_html=True)
        
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
                    color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6'],
                    hole=0.45
                )
                fig = style_plotly_chart(fig)
                fig.update_traces(textposition='outside', textinfo='percent+label', textfont_size=14)
                st.plotly_chart(fig, use_container_width=True)
        
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
                st.plotly_chart(fig, use_container_width=True)
        
        # ===== BUSINESS INSIGHTS =====
        st.markdown("---")
        st.markdown('<p class="section-title section-title-purple">💡 Key Business Insights</p>', unsafe_allow_html=True)
        
        insights = generate_insights(kpis, city_kpis, channel_kpis)
        
        for title, text in insights:
            st.markdown(create_insight_card(title, text), unsafe_allow_html=True)
        
        # ===== STATUS CARDS =====
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.is_cleaned:
                st.markdown(create_success_card("Data has been cleaned and validated. Ready for simulation!"), unsafe_allow_html=True)
            else:
                st.markdown(create_warning_card("Data not yet cleaned. Go to 🧹 Cleaner to validate and fix issues."), unsafe_allow_html=True)
        
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
    
    # Or load sample data
    st.markdown('<p class="section-title section-title-purple">📦 Or Use Sample Data</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📥 Load Sample Data", use_container_width=True, key='sample_data_btn'):
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
    
    # BIG PAGE TITLE
    st.markdown('<h1 class="page-title page-title-green">🧹 Data Rescue Center</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Validate, detect issues, and clean your dirty data automatically</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card("Please load data first. Go to 📂 Data page."), unsafe_allow_html=True)
        show_footer()
        return
    
    # Issue types info
    st.markdown('<p class="section-title section-title-cyan">🔍 Issues We Detect & Fix</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <strong style="color: #06b6d4; font-size: 1.1rem;">Data Quality</strong>
            <ul style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0; line-height: 1.8;">
                <li>Missing values</li>
                <li>Null representations</li>
                <li>Duplicate records</li>
                <li>Whitespace issues</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card" style="border-left-color: #8b5cf6;">
            <strong style="color: #8b5cf6; font-size: 1.1rem;">Format Issues</strong>
            <ul style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0; line-height: 1.8;">
                <li>Invalid timestamps</li>
                <li>Mixed case values</li>
                <li>Boolean strings</li>
                <li>Invalid categories</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card" style="border-left-color: #ec4899;">
            <strong style="color: #ec4899; font-size: 1.1rem;">Value Issues</strong>
            <ul style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0; line-height: 1.8;">
                <li>Negative values</li>
                <li>Outliers</li>
                <li>FK violations</li>
                <li>Invalid references</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Clean data button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run Data Cleaning", use_container_width=True, type="primary"):
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
                    st.session_state.is_cleaned = True
                    
                    st.success("✅ Data cleaning complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error during cleaning: {str(e)}")
    
    # Show results if cleaned
    if st.session_state.is_cleaned:
        st.markdown("---")
        st.markdown('<p class="section-title section-title-blue">📊 Cleaning Results</p>', unsafe_allow_html=True)
        
        stats = st.session_state.cleaner_stats
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            before = stats['products']['before']
            after = stats['products']['after']
            delta = f"{before - after} removed" if before > after else "No change"
            delta_type = "negative" if before > after else "positive"
            st.markdown(create_metric_card("Products", f"{after:,}", delta, delta_type, "cyan"), unsafe_allow_html=True)
        
        with col2:
            before = stats['stores']['before']
            after = stats['stores']['after']
            delta = f"{before - after} removed" if before > after else "No change"
            delta_type = "negative" if before > after else "positive"
            st.markdown(create_metric_card("Stores", f"{after:,}", delta, delta_type, "blue"), unsafe_allow_html=True)
        
        with col3:
            before = stats['sales']['before']
            after = stats['sales']['after']
            delta = f"{before - after} removed" if before > after else "No change"
            delta_type = "negative" if before > after else "positive"
            st.markdown(create_metric_card("Sales", f"{after:,}", delta, delta_type, "purple"), unsafe_allow_html=True)
        
        with col4:
            before = stats['inventory']['before']
            after = stats['inventory']['after']
            delta = f"{before - after} removed" if before > after else "No change"
            delta_type = "negative" if before > after else "positive"
            st.markdown(create_metric_card("Inventory", f"{after:,}", delta, delta_type, "pink"), unsafe_allow_html=True)
        
        # Issues summary
        st.markdown("---")
        st.markdown('<p class="section-title section-title-teal">🔍 Issues Detected & Fixed</p>', unsafe_allow_html=True)
        
        issues_df = st.session_state.issues_df
        
        if len(issues_df) > 0:
            st.markdown(create_success_card(f"Total {len(issues_df)} issues detected and fixed automatically!"), unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                issue_counts = issues_df['issue_type'].value_counts().reset_index()
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
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                table_counts = issues_df['table'].value_counts().reset_index()
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
                st.plotly_chart(fig, use_container_width=True)
            
            # Cleaning Insight
            st.markdown('<p class="section-title section-title-purple">💡 Cleaning Insight</p>', unsafe_allow_html=True)
            
            top_issue = issues_df['issue_type'].value_counts().idxmax()
            top_count = issues_df['issue_type'].value_counts().max()
            st.markdown(create_insight_card("Most Common Issue", f"'{top_issue}' was the most frequent issue with {top_count} occurrences. All instances have been automatically fixed."), unsafe_allow_html=True)
            
            # Issues table
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
            st.markdown(create_success_card("No issues found! Your data is already clean."), unsafe_allow_html=True)
    
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
        run_simulation = st.button("🚀 Run Simulation", use_container_width=True, type="primary")
    
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
                st.plotly_chart(fig, use_container_width=True)
            
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
                st.plotly_chart(fig, use_container_width=True)
        
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
                st.plotly_chart(fig, use_container_width=True)
                
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
                    st.plotly_chart(fig, use_container_width=True)
                
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
                    st.plotly_chart(fig, use_container_width=True)
                
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
                    st.plotly_chart(fig, use_container_width=True)
                
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
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('<p class="section-title section-title-teal">📋 City Performance Table</p>', unsafe_allow_html=True)
                st.dataframe(city_kpis, use_container_width=True)
                
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
                    st.plotly_chart(fig, use_container_width=True)
                
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
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown('<p class="section-title section-title-teal">📋 Category Performance Table</p>', unsafe_allow_html=True)
                st.dataframe(cat_kpis, use_container_width=True)
                
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
                    st.plotly_chart(fig, use_container_width=True)
                
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
                    st.plotly_chart(fig, use_container_width=True)
                
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
elif page == "🎯 Simulator":
    show_simulator_page()
elif page == "📊 Analytics":
    show_analytics_page()
