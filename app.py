# ============================================================================
# UAE Promo Pulse Simulator + Data Rescue Dashboard
# PREMIUM EDITION v3.0 - Advanced UI/UX with Theme Toggle
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
    initial_sidebar_state="collapsed"  # Collapsed by default for cleaner look
)

# ============================================================================
# THEME CONFIGURATION
# ============================================================================

def get_theme_css(theme):
    """Generate CSS based on selected theme."""
    
    if theme == "dark":
        return """
        :root {
            /* Dark Theme Colors */
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-tertiary: #16161f;
            --bg-card: #1a1a24;
            --bg-card-hover: #22222e;
            --bg-glass: rgba(26, 26, 36, 0.7);
            --bg-glass-hover: rgba(34, 34, 46, 0.8);
            
            --accent-primary: #06b6d4;
            --accent-secondary: #3b82f6;
            --accent-tertiary: #8b5cf6;
            --accent-quaternary: #ec4899;
            --accent-success: #10b981;
            --accent-warning: #f59e0b;
            --accent-error: #ef4444;
            --accent-teal: #14b8a6;
            
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --text-inverse: #0f172a;
            
            --border-primary: #2d2d3a;
            --border-secondary: #3d3d4a;
            --border-accent: rgba(6, 182, 212, 0.3);
            
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 8px 40px rgba(0, 0, 0, 0.5);
            --shadow-glow: 0 0 30px rgba(6, 182, 212, 0.15);
            
            --gradient-primary: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
            --gradient-secondary: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
            --gradient-success: linear-gradient(135deg, #10b981 0%, #14b8a6 100%);
            --gradient-bg: linear-gradient(180deg, #0a0a0f 0%, #12121a 50%, #0a0a0f 100%);
        }
        """
    else:
        return """
        :root {
            /* Light Theme Colors */
            --bg-primary: #f8fafc;
            --bg-secondary: #f1f5f9;
            --bg-tertiary: #e2e8f0;
            --bg-card: #ffffff;
            --bg-card-hover: #f8fafc;
            --bg-glass: rgba(255, 255, 255, 0.8);
            --bg-glass-hover: rgba(255, 255, 255, 0.95);
            
            --accent-primary: #0891b2;
            --accent-secondary: #2563eb;
            --accent-tertiary: #7c3aed;
            --accent-quaternary: #db2777;
            --accent-success: #059669;
            --accent-warning: #d97706;
            --accent-error: #dc2626;
            --accent-teal: #0d9488;
            
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-muted: #94a3b8;
            --text-inverse: #f8fafc;
            
            --border-primary: #e2e8f0;
            --border-secondary: #cbd5e1;
            --border-accent: rgba(8, 145, 178, 0.3);
            
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.06);
            --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.08);
            --shadow-lg: 0 8px 40px rgba(0, 0, 0, 0.12);
            --shadow-glow: 0 0 30px rgba(8, 145, 178, 0.1);
            
            --gradient-primary: linear-gradient(135deg, #0891b2 0%, #2563eb 100%);
            --gradient-secondary: linear-gradient(135deg, #7c3aed 0%, #db2777 100%);
            --gradient-success: linear-gradient(135deg, #059669 0%, #0d9488 100%);
            --gradient-bg: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 50%, #f8fafc 100%);
        }
        """

def get_base_css():
    """Base CSS that applies to both themes."""
    return """
    /* ===== IMPORTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* ===== ANIMATIONS ===== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes fadeInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(6, 182, 212, 0.3); }
        50% { box-shadow: 0 0 40px rgba(6, 182, 212, 0.5); }
    }
    
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes borderGlow {
        0%, 100% { border-color: var(--accent-primary); }
        50% { border-color: var(--accent-secondary); }
    }
    
    @keyframes scaleIn {
        from { transform: scale(0.9); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    
    @keyframes slideInFromBottom {
        from { transform: translateY(100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    /* ===== HIDE STREAMLIT DEFAULTS ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* ===== MAIN APP STYLING ===== */
    .stApp {
        background: var(--gradient-bg);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        min-height: 100vh;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-secondary);
        border-radius: 4px;
        transition: background 0.3s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-primary);
    }
    
    /* ===== SELECTION ===== */
    ::selection {
        background: var(--accent-primary);
        color: var(--text-inverse);
    }
    
    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--text-primary);
    }
    
    p, span, div {
        font-family: 'Inter', sans-serif;
        color: var(--text-secondary);
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* ===== SIDEBAR OVERRIDE (MINIMAL) ===== */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-primary);
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 2px;
        height: 100%;
        background: var(--gradient-primary);
        opacity: 0.5;
    }
    
    /* ===== TOP NAVIGATION BAR ===== */
    .top-nav {
        background: var(--bg-glass);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 20px 30px;
        margin-bottom: 30px;
        border: 1px solid var(--border-primary);
        box-shadow: var(--shadow-md);
        animation: fadeInDown 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .top-nav::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-primary);
    }
    
    /* ===== GLASS MORPHISM CONTAINERS ===== */
    .glass-container {
        background: var(--bg-glass);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 30px;
        border: 1px solid var(--border-primary);
        box-shadow: var(--shadow-md);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .glass-container:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg), var(--shadow-glow);
        border-color: var(--border-accent);
    }
    
    .glass-container::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        transition: left 0.6s ease;
    }
    
    .glass-container:hover::after {
        left: 100%;
    }
    
    /* ===== PREMIUM METRIC CARDS ===== */
    .metric-card-premium {
        background: var(--bg-card);
        border-radius: 20px;
        padding: 28px 24px;
        border: 1px solid var(--border-primary);
        box-shadow: var(--shadow-sm);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .metric-card-premium::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card-premium:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: var(--accent-primary);
        box-shadow: var(--shadow-lg), 0 0 30px rgba(6, 182, 212, 0.15);
    }
    
    .metric-card-premium:hover::before {
        opacity: 1;
    }
    
    .metric-label-premium {
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    
    .metric-value-premium {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.2;
        margin: 8px 0;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-delta-premium {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
    }
    
    .metric-delta-positive {
        background: rgba(16, 185, 129, 0.15);
        color: var(--accent-success);
    }
    
    .metric-delta-negative {
        background: rgba(239, 68, 68, 0.15);
        color: var(--accent-error);
    }
    
    /* ===== CHART CONTAINERS ===== */
    .chart-container {
        background: var(--bg-card);
        border-radius: 24px;
        padding: 24px;
        border: 1px solid var(--border-primary);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
        margin-bottom: 24px;
        position: relative;
    }
    
    .chart-container:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--border-accent);
    }
    
    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 1px solid var(--border-primary);
    }
    
    .chart-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .chart-filters {
        display: flex;
        gap: 12px;
        align-items: center;
    }
    
    /* ===== FILTER PILLS ===== */
    .filter-section {
        background: var(--bg-card);
        border-radius: 16px;
        padding: 20px 24px;
        border: 1px solid var(--border-primary);
        margin-bottom: 24px;
        animation: fadeInDown 0.4s ease-out;
    }
    
    .filter-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .filter-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .filter-row {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        align-items: flex-end;
    }
    
    .filter-group {
        flex: 1;
        min-width: 150px;
    }
    
    .filter-label {
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
        font-weight: 600;
    }
    
    /* ===== INSIGHT CARDS ===== */
    .insight-card-premium {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(236, 72, 153, 0.08) 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        margin: 16px 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .insight-card-premium::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: var(--gradient-secondary);
    }
    
    .insight-card-premium:hover {
        transform: translateX(8px);
        border-color: rgba(139, 92, 246, 0.4);
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.15);
    }
    
    .insight-icon {
        font-size: 2rem;
        margin-bottom: 12px;
    }
    
    .insight-title-premium {
        font-size: 1rem;
        font-weight: 700;
        color: var(--accent-tertiary);
        margin-bottom: 8px;
    }
    
    .insight-text-premium {
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* ===== RECOMMENDATION BOX ===== */
    .recommendation-box-premium {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(6, 182, 212, 0.08) 100%);
        border-radius: 20px;
        padding: 28px;
        border: 2px solid rgba(16, 185, 129, 0.3);
        margin: 24px 0;
        position: relative;
        overflow: hidden;
    }
    
    .recommendation-box-premium::before {
        content: '💡';
        position: absolute;
        top: 20px;
        right: 24px;
        font-size: 2.5rem;
        opacity: 0.3;
    }
    
    .recommendation-title-premium {
        color: var(--accent-success);
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .recommendation-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .recommendation-list li {
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.8;
        padding-left: 24px;
        position: relative;
        margin-bottom: 8px;
    }
    
    .recommendation-list li::before {
        content: '→';
        position: absolute;
        left: 0;
        color: var(--accent-success);
        font-weight: 700;
    }
    
    /* ===== HERO SECTION ===== */
    .hero-premium {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(139, 92, 246, 0.1) 50%, rgba(236, 72, 153, 0.1) 100%);
        border-radius: 32px;
        padding: 60px;
        margin-bottom: 40px;
        border: 1px solid var(--border-accent);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .hero-premium::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.1) 0%, transparent 50%);
        animation: float 8s ease-in-out infinite;
    }
    
    .hero-title-premium {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-primary) 40%, var(--accent-tertiary) 70%, var(--accent-quaternary) 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 20px;
        position: relative;
        z-index: 1;
        line-height: 1.1;
        animation: gradientFlow 4s ease infinite;
    }
    
    .hero-subtitle-premium {
        font-size: 1.3rem;
        color: var(--text-secondary);
        margin-bottom: 30px;
        position: relative;
        z-index: 1;
        line-height: 1.6;
    }
    
    .hero-badges {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 20px;
        position: relative;
        z-index: 1;
    }
    
    .hero-badge-premium {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 12px 24px;
        background: var(--gradient-primary);
        border-radius: 50px;
        color: white;
        font-size: 0.9rem;
        font-weight: 600;
        animation: pulse 2s infinite;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    }
    
    /* ===== PAGE TITLES ===== */
    .page-title-premium {
        font-size: 3rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 8px;
        line-height: 1.2;
        animation: fadeInLeft 0.5s ease-out;
    }
    
    .page-subtitle-premium {
        font-size: 1.15rem;
        color: var(--text-secondary);
        margin-bottom: 30px;
        animation: fadeInLeft 0.6s ease-out;
    }
    
    .section-title-premium {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    /* ===== FEATURE CARDS ===== */
    .feature-card-premium {
        background: var(--bg-card);
        border-radius: 24px;
        padding: 36px 28px;
        border: 1px solid var(--border-primary);
        box-shadow: var(--shadow-sm);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        height: 240px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    .feature-card-premium::before {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .feature-card-premium:hover {
        transform: translateY(-12px) scale(1.02);
        border-color: var(--accent-primary);
        box-shadow: var(--shadow-lg), 0 20px 50px rgba(6, 182, 212, 0.15);
    }
    
    .feature-card-premium:hover::before {
        opacity: 1;
    }
    
    .feature-icon-premium {
        font-size: 3.5rem;
        margin-bottom: 20px;
        animation: float 3s ease-in-out infinite;
    }
    
    .feature-title-premium {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--accent-primary);
        margin-bottom: 10px;
    }
    
    .feature-desc-premium {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* ===== INFO/SUCCESS/WARNING/ERROR CARDS ===== */
    .status-card {
        border-radius: 16px;
        padding: 20px 24px;
        margin: 16px 0;
        transition: all 0.3s ease;
        display: flex;
        align-items: flex-start;
        gap: 16px;
    }
    
    .status-card:hover {
        transform: translateX(8px);
    }
    
    .status-card-info {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
        border-left: 4px solid var(--accent-primary);
    }
    
    .status-card-success {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(20, 184, 166, 0.1) 100%);
        border-left: 4px solid var(--accent-success);
    }
    
    .status-card-warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 146, 60, 0.1) 100%);
        border-left: 4px solid var(--accent-warning);
    }
    
    .status-card-error {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
        border-left: 4px solid var(--accent-error);
    }
    
    .status-icon {
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    
    .status-content {
        flex: 1;
    }
    
    .status-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 4px;
    }
    
    .status-text {
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* ===== TABS STYLING ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--bg-card);
        border-radius: 12px;
        color: var(--text-secondary);
        padding: 14px 28px;
        border: 1px solid var(--border-primary);
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-card-hover);
        border-color: var(--accent-primary);
        transform: translateY(-2px);
        box-shadow: var(--shadow-sm);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: var(--gradient-primary);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 16px 36px;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--accent-secondary) 0%, var(--accent-tertiary) 100%);
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.4);
        transform: translateY(-3px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* ===== DOWNLOAD BUTTON ===== */
    .stDownloadButton > button {
        background: var(--gradient-success);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
    }
    
    /* ===== SELECTBOX ===== */
    .stSelectbox > div > div {
        background-color: var(--bg-card);
        border-color: var(--border-primary);
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--accent-primary);
    }
    
    /* ===== SLIDERS ===== */
    .stSlider > div > div > div > div {
        background: var(--gradient-primary) !important;
    }
    
    /* ===== FILE UPLOADER ===== */
    .stFileUploader > div {
        background: var(--bg-card);
        border: 2px dashed var(--border-primary);
        border-radius: 16px;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--accent-primary);
        background: var(--bg-card-hover);
    }
    
    /* ===== DATAFRAME ===== */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid var(--border-primary);
    }
    
    /* ===== FOOTER ===== */
    .footer-premium {
        background: var(--bg-card);
        padding: 40px;
        text-align: center;
        border-top: 1px solid var(--border-primary);
        margin-top: 60px;
        border-radius: 24px 24px 0 0;
        position: relative;
        overflow: hidden;
    }
    
    .footer-premium::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-primary);
    }
    
    .footer-title-premium {
        color: var(--text-primary);
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 12px;
    }
    
    .footer-subtitle-premium {
        color: var(--text-muted);
        font-size: 1rem;
        margin-bottom: 16px;
    }
    
    .footer-names-premium {
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        font-size: 1.15rem;
    }
    
    /* ===== DIVIDER ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-primary), transparent);
        margin: 36px 0;
    }
    
    /* ===== VIEW TOGGLE ===== */
    .view-toggle {
        display: flex;
        justify-content: center;
        gap: 16px;
        padding: 20px;
        background: var(--bg-card);
        border-radius: 16px;
        border: 1px solid var(--border-primary);
        margin-bottom: 30px;
    }
    
    /* ===== THEME TOGGLE ===== */
    .theme-toggle-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background: var(--bg-glass);
        backdrop-filter: blur(20px);
        border-radius: 50px;
        padding: 8px;
        border: 1px solid var(--border-primary);
        box-shadow: var(--shadow-md);
        animation: fadeInRight 0.5s ease-out;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .hero-title-premium {
            font-size: 2.5rem;
        }
        
        .page-title-premium {
            font-size: 2rem;
        }
        
        .metric-card-premium {
            height: 140px;
            padding: 20px;
        }
        
        .metric-value-premium {
            font-size: 1.5rem;
        }
        
        .filter-row {
            flex-direction: column;
        }
        
        .filter-group {
            width: 100%;
        }
    }
    """

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
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
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# ============================================================================
# APPLY THEME CSS
# ============================================================================

theme_css = get_theme_css(st.session_state.theme)
base_css = get_base_css()

st.markdown(f"<style>{theme_css}{base_css}</style>", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_chart_template():
    """Get Plotly template based on current theme."""
    if st.session_state.theme == 'dark':
        return {
            'paper_bgcolor': 'rgba(26, 26, 36, 0.8)',
            'plot_bgcolor': 'rgba(26, 26, 36, 0.8)',
            'font': {'color': '#94a3b8', 'family': 'Inter'},
            'title': {'font': {'color': '#f1f5f9', 'size': 16, 'family': 'Inter'}},
            'xaxis': {'gridcolor': '#2d2d3a', 'linecolor': '#2d2d3a', 'tickfont': {'color': '#94a3b8'}},
            'yaxis': {'gridcolor': '#2d2d3a', 'linecolor': '#2d2d3a', 'tickfont': {'color': '#94a3b8'}},
            'legend': {'font': {'color': '#94a3b8'}}
        }
    else:
        return {
            'paper_bgcolor': 'rgba(255, 255, 255, 0.9)',
            'plot_bgcolor': 'rgba(255, 255, 255, 0.9)',
            'font': {'color': '#475569', 'family': 'Inter'},
            'title': {'font': {'color': '#0f172a', 'size': 16, 'family': 'Inter'}},
            'xaxis': {'gridcolor': '#e2e8f0', 'linecolor': '#e2e8f0', 'tickfont': {'color': '#475569'}},
            'yaxis': {'gridcolor': '#e2e8f0', 'linecolor': '#e2e8f0', 'tickfont': {'color': '#475569'}},
            'legend': {'font': {'color': '#475569'}}
        }

def style_chart(fig):
    """Apply theme styling to Plotly figure."""
    template = get_chart_template()
    fig.update_layout(
        paper_bgcolor=template['paper_bgcolor'],
        plot_bgcolor=template['plot_bgcolor'],
        font=template['font'],
        title=template['title'],
        xaxis=template['xaxis'],
        yaxis=template['yaxis'],
        legend=template['legend'],
        margin=dict(l=20, r=20, t=60, b=20),
        hoverlabel=dict(
            bgcolor='rgba(26, 26, 36, 0.9)' if st.session_state.theme == 'dark' else 'white',
            font_size=13,
            font_family='Inter'
        )
    )
    return fig

def create_metric_card_html(label, value, delta=None, delta_type="positive", icon="📊", color="primary"):
    """Create premium metric card HTML."""
    color_map = {
        "primary": "#06b6d4",
        "secondary": "#3b82f6",
        "tertiary": "#8b5cf6",
        "quaternary": "#ec4899",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444"
    }
    accent = color_map.get(color, "#06b6d4")
    
    delta_html = ""
    if delta:
        delta_class = "metric-delta-positive" if delta_type == "positive" else "metric-delta-negative"
        delta_icon = "↑" if delta_type == "positive" else "↓"
        delta_html = f'<span class="metric-delta-premium {delta_class}">{delta_icon} {delta}</span>'
    
    return f"""
    <div class="metric-card-premium" style="--accent: {accent};">
        <div class="metric-label-premium">{icon} {label}</div>
        <div class="metric-value-premium" style="background: linear-gradient(135deg, {accent} 0%, {accent}88 100%); -webkit-background-clip: text;">{value}</div>
        {delta_html if delta_html else '<div style="height: 24px;"></div>'}
    </div>
    """

def create_insight_card_html(icon, title, text):
    """Create premium insight card HTML."""
    return f"""
    <div class="insight-card-premium">
        <div class="insight-icon">{icon}</div>
        <div class="insight-title-premium">{title}</div>
        <div class="insight-text-premium">{text}</div>
    </div>
    """

def create_status_card_html(type, icon, title, text):
    """Create status card HTML."""
    return f"""
    <div class="status-card status-card-{type}">
        <div class="status-icon">{icon}</div>
        <div class="status-content">
            <div class="status-title">{title}</div>
            <div class="status-text">{text}</div>
        </div>
    </div>
    """

def create_recommendation_html(title, items):
    """Create recommendation box HTML."""
    items_html = "".join([f"<li>{item}</li>" for item in items])
    return f"""
    <div class="recommendation-box-premium">
        <div class="recommendation-title-premium">📋 {title}</div>
        <ul class="recommendation-list">{items_html}</ul>
    </div>
    """

def show_footer():
    """Display premium footer."""
    st.markdown("""
    <div class="footer-premium">
        <div class="footer-title-premium">🚀 UAE Promo Pulse Simulator + Data Rescue Dashboard</div>
        <div class="footer-subtitle-premium">Built with ❤️ by</div>
        <div class="footer-names-premium">Kartik Joshi • Gagandeep Singh • Samuel Alex • Prem Kukreja</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TOP NAVIGATION BAR (REPLACES SIDEBAR)
# ============================================================================

def show_top_navigation():
    """Display top navigation bar with theme toggle."""
    
    col1, col2, col3 = st.columns([2, 6, 2])
    
    with col1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 2.5rem;">🛒</span>
            <div>
                <div style="font-size: 1.4rem; font-weight: 800; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Promo Pulse</div>
                <div style="font-size: 0.75rem; color: var(--text-muted);">UAE Retail Analytics</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        nav_cols = st.columns(6)
        pages = ["🏠 Home", "📂 Upload", "🧹 Rescue", "🎯 Simulator", "📊 Dashboard", "🔧 Test"]
        page_keys = ["Home", "Upload", "Rescue", "Simulator", "Dashboard", "Test"]
        
        for i, (page_name, page_key) in enumerate(zip(pages, page_keys)):
            with nav_cols[i]:
                if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.rerun()
    
    with col3:
        # Theme toggle
        theme_col1, theme_col2 = st.columns([3, 1])
        with theme_col2:
            theme_icon = "🌙" if st.session_state.theme == "dark" else "☀️"
            if st.button(theme_icon, key="theme_toggle"):
                st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
                st.rerun()
        
        with theme_col1:
            # Status indicators
            data_status = "🟢" if st.session_state.data_loaded else "🔴"
            clean_status = "🟢" if st.session_state.is_cleaned else "🟡" if st.session_state.data_loaded else "🔴"
            st.markdown(f"""
            <div style="font-size: 0.75rem; color: var(--text-muted); text-align: right;">
                {data_status} Data {clean_status} Clean
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")

# Show navigation
show_top_navigation()
# ============================================================================
# ADVANCED EDA VISUALIZATIONS
# ============================================================================

def create_price_elasticity_chart(sales_df, products_df):
    """
    HIGH-IMPACT VISUALIZATION 1: Price Elasticity Analysis
    Shows relationship between discount % and sales volume to identify optimal discount levels.
    """
    if sales_df is None or len(sales_df) == 0:
        return None
    
    try:
        df = sales_df.copy()
        df['discount_pct'] = pd.to_numeric(df.get('discount_pct', 0), errors='coerce').fillna(0)
        df['qty'] = pd.to_numeric(df.get('qty', 1), errors='coerce').fillna(1)
        df['selling_price_aed'] = pd.to_numeric(df.get('selling_price_aed', 0), errors='coerce').fillna(0)
        
        # Create discount buckets
        df['discount_bucket'] = pd.cut(df['discount_pct'], bins=[0, 5, 10, 15, 20, 25, 30, 50], 
                                       labels=['0-5%', '5-10%', '10-15%', '15-20%', '20-25%', '25-30%', '30%+'])
        
        elasticity = df.groupby('discount_bucket', observed=True).agg({
            'qty': 'sum',
            'selling_price_aed': 'sum',
            'order_id': 'nunique'
        }).reset_index()
        
        elasticity.columns = ['Discount Range', 'Units Sold', 'Revenue', 'Orders']
        elasticity['Avg Units/Order'] = elasticity['Units Sold'] / elasticity['Orders']
        
        # Create dual-axis chart
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(name='Units Sold', x=elasticity['Discount Range'], y=elasticity['Units Sold'],
                  marker_color='#06b6d4', opacity=0.8),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(name='Revenue', x=elasticity['Discount Range'], y=elasticity['Revenue'],
                      mode='lines+markers', marker=dict(size=10, color='#ec4899'),
                      line=dict(width=3, color='#ec4899')),
            secondary_y=True
        )
        
        fig = style_chart(fig)
        fig.update_layout(
            title='📈 Price Elasticity Analysis: Discount Impact on Sales',
            barmode='group',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_yaxes(title_text="Units Sold", secondary_y=False)
        fig.update_yaxes(title_text="Revenue (AED)", secondary_y=True)
        
        return fig
    except Exception as e:
        return None

def create_category_performance_matrix(sales_df, products_df):
    """
    HIGH-IMPACT VISUALIZATION 2: Category Performance Matrix (BCG-style)
    Shows categories in a 2D space of Revenue vs Profit Margin.
    """
    if sales_df is None or products_df is None:
        return None
    
    try:
        df = sales_df.merge(products_df[['product_id', 'category', 'unit_cost_aed']], on='product_id', how='left')
        df['selling_price_aed'] = pd.to_numeric(df.get('selling_price_aed', 0), errors='coerce').fillna(0)
        df['unit_cost_aed'] = pd.to_numeric(df.get('unit_cost_aed', 0), errors='coerce').fillna(0)
        df['qty'] = pd.to_numeric(df.get('qty', 1), errors='coerce').fillna(1)
        df['revenue'] = df['selling_price_aed'] * df['qty']
        df['cost'] = df['unit_cost_aed'] * df['qty']
        df['profit'] = df['revenue'] - df['cost']
        
        cat_perf = df.groupby('category').agg({
            'revenue': 'sum',
            'profit': 'sum',
            'order_id': 'nunique',
            'qty': 'sum'
        }).reset_index()
        
        cat_perf['margin_pct'] = (cat_perf['profit'] / cat_perf['revenue'] * 100).fillna(0)
        cat_perf['revenue_share'] = cat_perf['revenue'] / cat_perf['revenue'].sum() * 100
        
        # Quadrant thresholds
        avg_margin = cat_perf['margin_pct'].mean()
        avg_revenue = cat_perf['revenue'].mean()
        
        # Assign quadrants
        def get_quadrant(row):
            if row['revenue'] >= avg_revenue and row['margin_pct'] >= avg_margin:
                return 'Stars ⭐'
            elif row['revenue'] >= avg_revenue and row['margin_pct'] < avg_margin:
                return 'Cash Cows 💰'
            elif row['revenue'] < avg_revenue and row['margin_pct'] >= avg_margin:
                return 'Question Marks ❓'
            else:
                return 'Dogs 🐕'
        
        cat_perf['quadrant'] = cat_perf.apply(get_quadrant, axis=1)
        
        color_map = {'Stars ⭐': '#10b981', 'Cash Cows 💰': '#3b82f6', 
                     'Question Marks ❓': '#f59e0b', 'Dogs 🐕': '#ef4444'}
        
        fig = px.scatter(cat_perf, x='revenue', y='margin_pct', 
                        size='qty', color='quadrant',
                        hover_name='category',
                        hover_data={'revenue': ':,.0f', 'margin_pct': ':.1f', 'qty': ':,'},
                        color_discrete_map=color_map,
                        title='🎯 Category Performance Matrix (BCG-Style)')
        
        fig = style_chart(fig)
        
        # Add quadrant lines
        fig.add_hline(y=avg_margin, line_dash="dash", line_color="#64748b", opacity=0.5)
        fig.add_vline(x=avg_revenue, line_dash="dash", line_color="#64748b", opacity=0.5)
        
        fig.update_layout(
            xaxis_title="Revenue (AED)",
            yaxis_title="Profit Margin %",
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        
        return fig
    except Exception as e:
        return None

def create_cohort_analysis_chart(sales_df):
    """
    HIGH-IMPACT VISUALIZATION 3: Customer Cohort Analysis
    Shows customer retention patterns over time.
    """
    if sales_df is None or len(sales_df) == 0:
        return None
    
    try:
        df = sales_df.copy()
        df['order_time'] = pd.to_datetime(df['order_time'], errors='coerce')
        df = df.dropna(subset=['order_time'])
        
        if 'customer_id' not in df.columns:
            # Create synthetic customer_id from order patterns
            df['customer_id'] = df['order_id'].apply(lambda x: hash(str(x)[:8]) % 10000)
        
        # Get first purchase month for each customer
        df['order_month'] = df['order_time'].dt.to_period('M')
        first_purchase = df.groupby('customer_id')['order_month'].min().reset_index()
        first_purchase.columns = ['customer_id', 'cohort_month']
        
        df = df.merge(first_purchase, on='customer_id')
        
        # Calculate months since first purchase
        df['cohort_month_dt'] = df['cohort_month'].dt.to_timestamp()
        df['order_month_dt'] = df['order_month'].dt.to_timestamp()
        df['months_since_first'] = ((df['order_month_dt'] - df['cohort_month_dt']).dt.days / 30).astype(int)
        
        # Create cohort pivot
        cohort_data = df.groupby(['cohort_month', 'months_since_first'])['customer_id'].nunique().reset_index()
        cohort_data.columns = ['Cohort', 'Month', 'Customers']
        
        cohort_pivot = cohort_data.pivot(index='Cohort', columns='Month', values='Customers').fillna(0)
        
        # Calculate retention rates
        cohort_sizes = cohort_pivot.iloc[:, 0]
        retention = cohort_pivot.divide(cohort_sizes, axis=0) * 100
        retention = retention.iloc[:6, :6]  # Limit to 6x6 for clarity
        
        fig = go.Figure(data=go.Heatmap(
            z=retention.values,
            x=[f'Month {i}' for i in retention.columns],
            y=[str(p) for p in retention.index],
            colorscale=[[0, '#0f172a'], [0.5, '#06b6d4'], [1, '#10b981']],
            text=np.round(retention.values, 1),
            texttemplate='%{text}%',
            textfont={"size": 11},
            hoverongaps=False
        ))
        
        fig = style_chart(fig)
        fig.update_layout(
            title='👥 Customer Cohort Retention Analysis',
            xaxis_title='Months Since First Purchase',
            yaxis_title='Cohort (First Purchase Month)'
        )
        
        return fig
    except Exception as e:
        return None

def create_revenue_waterfall_chart(kpis, sim_results=None):
    """
    BONUS VISUALIZATION: Revenue Waterfall Chart
    Breaks down revenue into components.
    """
    try:
        gross = kpis.get('total_revenue', 0)
        discounts = gross * kpis.get('avg_discount_pct', 0) / 100
        returns = gross * kpis.get('return_rate_pct', 0) / 100
        net = gross - discounts - returns
        
        if sim_results:
            projected = sim_results.get('outputs', {}).get('expected_revenue', net)
        else:
            projected = net
        
        fig = go.Figure(go.Waterfall(
            name="Revenue",
            orientation="v",
            measure=["absolute", "relative", "relative", "total", "relative"],
            x=["Gross Revenue", "Discounts", "Returns", "Net Revenue", "Projected"],
            y=[gross, -discounts, -returns, 0, projected - net],
            connector={"line": {"color": "#64748b"}},
            decreasing={"marker": {"color": "#ef4444"}},
            increasing={"marker": {"color": "#10b981"}},
            totals={"marker": {"color": "#06b6d4"}}
        ))
        
        fig = style_chart(fig)
        fig.update_layout(title="💰 Revenue Waterfall Analysis", showlegend=False)
        
        return fig
    except:
        return None

# ============================================================================
# GENERATE ADVANCED INSIGHTS
# ============================================================================

def generate_advanced_insights(kpis, sales_df, products_df, stores_df, sim_results=None):
    """Generate deeper business insights from data analysis."""
    insights = []
    
    # 1. Revenue Concentration
    if kpis.get('total_revenue', 0) > 0:
        aov = kpis.get('avg_order_value', 0)
        if aov > 500:
            insights.append({
                'icon': '💎',
                'title': 'Premium Customer Base',
                'text': f'Average order value of AED {aov:,.0f} indicates a premium customer segment. Consider VIP loyalty programs and exclusive offers.'
            })
        elif aov < 150:
            insights.append({
                'icon': '📦',
                'title': 'Volume-Driven Business',
                'text': f'Low AOV of AED {aov:,.0f} suggests volume-focused strategy. Bundle deals and minimum order incentives could boost revenue 20-30%.'
            })
    
    # 2. Margin Analysis
    margin = kpis.get('profit_margin_pct', 0)
    if margin > 30:
        insights.append({
            'icon': '📈',
            'title': 'Strong Profit Margins',
            'text': f'Healthy {margin:.1f}% margin provides flexibility for aggressive promotions without risking profitability.'
        })
    elif margin < 15:
        insights.append({
            'icon': '⚠️',
            'title': 'Margin Pressure Alert',
            'text': f'Current margin of {margin:.1f}% is below retail benchmarks. Review supplier costs and optimize pricing strategy.'
        })
    
    # 3. Discount Efficiency
    avg_discount = kpis.get('avg_discount_pct', 0)
    if avg_discount > 0:
        discount_efficiency = kpis.get('total_revenue', 0) / (avg_discount + 1) / 1000
        if avg_discount > 20:
            insights.append({
                'icon': '🏷️',
                'title': 'High Discount Dependency',
                'text': f'Average {avg_discount:.1f}% discount suggests price-sensitive customers. Test value-based pricing to reduce discount reliance.'
            })
    
    # 4. Return Rate Analysis
    return_rate = kpis.get('return_rate_pct', 0)
    if return_rate > 8:
        insights.append({
            'icon': '🔄',
            'title': 'Return Rate Concern',
            'text': f'{return_rate:.1f}% return rate is above industry average. Review product descriptions, sizing guides, and quality control.'
        })
    elif return_rate < 2:
        insights.append({
            'icon': '✅',
            'title': 'Excellent Customer Satisfaction',
            'text': f'Low {return_rate:.1f}% return rate indicates strong product-market fit and accurate expectations.'
        })
    
    # 5. Simulation Impact
    if sim_results:
        roi = sim_results.get('outputs', {}).get('roi_pct', 0)
        if roi > 100:
            insights.append({
                'icon': '🚀',
                'title': 'High-Impact Campaign',
                'text': f'Projected ROI of {roi:.0f}% exceeds benchmarks. Strong recommendation to proceed with campaign.'
            })
        elif roi < 0:
            insights.append({
                'icon': '🛑',
                'title': 'Campaign Risk Alert',
                'text': f'Negative ROI of {roi:.0f}% projected. Consider reducing discount depth or narrowing target audience.'
            })
    
    return insights[:6]  # Return top 6 insights

def generate_strategic_recommendations(kpis, sim_results=None, stockout_risk=None):
    """Generate strategic recommendations for executives."""
    recommendations = []
    
    margin = kpis.get('profit_margin_pct', 0)
    aov = kpis.get('avg_order_value', 0)
    return_rate = kpis.get('return_rate_pct', 0)
    avg_discount = kpis.get('avg_discount_pct', 0)
    
    # Margin-based recommendations
    if margin > 25:
        recommendations.append(f"Strong {margin:.0f}% margin supports aggressive promotional campaigns up to 15% discount without margin erosion.")
    else:
        recommendations.append(f"Current {margin:.0f}% margin requires careful discount management. Limit promotions to high-margin categories.")
    
    # AOV recommendations
    if aov < 200:
        recommendations.append("Implement minimum cart value promotions (AED 200+) with free shipping to increase average order value by 15-20%.")
    elif aov > 500:
        recommendations.append("High-value customer base warrants investment in loyalty programs and exclusive early-access promotions.")
    
    # Return rate recommendations
    if return_rate > 5:
        recommendations.append(f"Address {return_rate:.1f}% return rate through enhanced product imagery, detailed sizing guides, and quality audits.")
    
    # Simulation-based recommendations
    if sim_results:
        roi = sim_results.get('outputs', {}).get('roi_pct', 0)
        demand_lift = sim_results.get('outputs', {}).get('demand_lift_pct', 0)
        
        if roi > 50:
            recommendations.append(f"Campaign projects {roi:.0f}% ROI with {demand_lift:.0f}% demand lift. Recommend immediate execution.")
        elif roi > 0:
            recommendations.append(f"Moderate {roi:.0f}% ROI projected. Consider A/B testing with control group before full rollout.")
    
    # Stockout recommendations
    if stockout_risk and stockout_risk.get('stockout_risk_pct', 0) > 15:
        recommendations.append("High stockout risk detected. Prioritize inventory replenishment for top-selling SKUs before campaign launch.")
    
    if not recommendations:
        recommendations.append("All metrics within optimal range. Proceed with planned promotional calendar.")
    
    return recommendations[:5]

# ============================================================================
# DASHBOARD WITH LOCALIZED FILTERS
# ============================================================================

def show_dashboard_page():
    """Display advanced dashboard with localized filters per chart."""
    
    st.markdown('<h1 class="page-title-premium">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle-premium">Real-time insights with interactive visualizations</p>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.markdown(create_status_card_html("warning", "⚠️", "No Data Loaded", 
                   "Please go to the Upload page to load your data files."), unsafe_allow_html=True)
        show_footer()
        return
    
    # Get data
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    inventory_df = st.session_state.clean_inventory if st.session_state.is_cleaned else st.session_state.raw_inventory
    
    # ===== VIEW TOGGLE =====
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        view_mode = st.radio(
            "Dashboard View",
            ["👔 Executive View", "⚙️ Manager View", "🔬 Advanced Analytics"],
            horizontal=True,
            key='dashboard_view'
        )
    
    st.markdown("---")
    
    # ===== GLOBAL FILTER BAR (IN MAIN BODY) =====
    with st.expander("🎛️ **Global Filters** - Click to expand", expanded=False):
        filter_cols = st.columns(5)
        
        with filter_cols[0]:
            # Date filter
            if sales_df is not None and 'order_time' in sales_df.columns:
                try:
                    temp_sales = sales_df.copy()
                    temp_sales['order_time'] = pd.to_datetime(temp_sales['order_time'], errors='coerce')
                    min_date = temp_sales['order_time'].min()
                    max_date = temp_sales['order_time'].max()
                    if pd.notna(min_date) and pd.notna(max_date):
                        date_range = st.date_input(
                            "📅 Date Range",
                            value=(min_date.date(), max_date.date()),
                            min_value=min_date.date(),
                            max_value=max_date.date(),
                            key='global_date_range'
                        )
                except:
                    pass
        
        with filter_cols[1]:
            cities = ['All']
            if stores_df is not None and 'city' in stores_df.columns:
                cities += sorted([str(c) for c in stores_df['city'].dropna().unique().tolist()])
            selected_city = st.selectbox("🏙️ City", cities, key='global_city')
        
        with filter_cols[2]:
            channels = ['All']
            if stores_df is not None and 'channel' in stores_df.columns:
                channels += sorted([str(c) for c in stores_df['channel'].dropna().unique().tolist()])
            selected_channel = st.selectbox("📱 Channel", channels, key='global_channel')
        
        with filter_cols[3]:
            categories = ['All']
            if products_df is not None and 'category' in products_df.columns:
                categories += sorted([str(c) for c in products_df['category'].dropna().unique().tolist()])
            selected_category = st.selectbox("📦 Category", categories, key='global_category')
        
        with filter_cols[4]:
            brands = ['All']
            if products_df is not None and 'brand' in products_df.columns:
                brand_list = [str(b) for b in products_df['brand'].dropna().unique().tolist()]
                brands += sorted(brand_list)[:20]
            selected_brand = st.selectbox("🏷️ Brand", brands, key='global_brand')
    
    # Apply global filters
    filtered_sales = apply_global_filters(sales_df, stores_df, products_df)
    
    # Calculate KPIs
    sim = Simulator()
    kpis = sim.calculate_overall_kpis(filtered_sales, products_df)
    
    # Route to view
    if view_mode == "👔 Executive View":
        show_executive_dashboard(filtered_sales, stores_df, products_df, inventory_df, kpis, sim)
    elif view_mode == "⚙️ Manager View":
        show_manager_dashboard(filtered_sales, stores_df, products_df, inventory_df, kpis, sim)
    else:
        show_advanced_analytics(filtered_sales, stores_df, products_df, inventory_df, kpis, sim)
    
    show_footer()

def apply_global_filters(sales_df, stores_df, products_df):
    """Apply global filters from the main body filter bar."""
    if sales_df is None:
        return sales_df
    
    filtered = sales_df.copy()
    
    # Date filter
    if 'global_date_range' in st.session_state:
        try:
            date_range = st.session_state.global_date_range
            if len(date_range) == 2:
                filtered['order_time'] = pd.to_datetime(filtered['order_time'], errors='coerce')
                filtered = filtered[
                    (filtered['order_time'].dt.date >= date_range[0]) &
                    (filtered['order_time'].dt.date <= date_range[1])
                ]
        except:
            pass
    
    # City filter
    if 'global_city' in st.session_state and st.session_state.global_city != 'All':
        if stores_df is not None and 'store_id' in filtered.columns:
            city_stores = stores_df[stores_df['city'] == st.session_state.global_city]['store_id'].tolist()
            filtered = filtered[filtered['store_id'].isin(city_stores)]
    
    # Channel filter
    if 'global_channel' in st.session_state and st.session_state.global_channel != 'All':
        if stores_df is not None and 'store_id' in filtered.columns:
            channel_stores = stores_df[stores_df['channel'] == st.session_state.global_channel]['store_id'].tolist()
            filtered = filtered[filtered['store_id'].isin(channel_stores)]
    
    # Category filter
    if 'global_category' in st.session_state and st.session_state.global_category != 'All':
        if products_df is not None and 'product_id' in filtered.columns:
            cat_products = products_df[products_df['category'] == st.session_state.global_category]['product_id'].tolist()
            filtered = filtered[filtered['product_id'].isin(cat_products)]
    
    # Brand filter
    if 'global_brand' in st.session_state and st.session_state.global_brand != 'All':
        if products_df is not None and 'product_id' in filtered.columns:
            brand_products = products_df[products_df['brand'] == st.session_state.global_brand]['product_id'].tolist()
            filtered = filtered[filtered['product_id'].isin(brand_products)]
    
    return filtered

def show_executive_dashboard(sales_df, stores_df, products_df, inventory_df, kpis, sim):
    """Executive dashboard with strategic KPIs and insights."""
    
    st.markdown('<p class="section-title-premium">💼 Executive Summary</p>', unsafe_allow_html=True)
    
    # KPI Row 1
    cols = st.columns(4)
    metrics = [
        ("Net Revenue", f"AED {kpis.get('net_revenue', kpis.get('total_revenue', 0)):,.0f}", "+12.5%", "positive", "💰", "primary"),
        ("Gross Margin", f"{kpis.get('profit_margin_pct', 0):.1f}%", "+2.3%", "positive", "📈", "success"),
        ("Total Orders", f"{kpis.get('total_orders', 0):,}", "+8.7%", "positive", "📦", "secondary"),
        ("Avg Order Value", f"AED {kpis.get('avg_order_value', 0):,.0f}", "-1.2%", "negative", "🛒", "tertiary")
    ]
    
    for i, (label, value, delta, delta_type, icon, color) in enumerate(metrics):
        with cols[i]:
            st.markdown(create_metric_card_html(label, value, delta, delta_type, icon, color), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # KPI Row 2
    cols = st.columns(4)
    metrics2 = [
        ("Profit Proxy", f"AED {kpis.get('total_profit', 0):,.0f}", "+15.2%", "positive", "💎", "success"),
        ("Avg Discount", f"{kpis.get('avg_discount_pct', 0):.1f}%", None, None, "🏷️", "warning"),
        ("Return Rate", f"{kpis.get('return_rate_pct', 0):.1f}%", "-0.5%", "positive", "🔄", "quaternary"),
        ("Unique Products", f"{kpis.get('unique_products', 0):,}", None, None, "📊", "primary")
    ]
    
    for i, (label, value, delta, delta_type, icon, color) in enumerate(metrics2):
        with cols[i]:
            st.markdown(create_metric_card_html(label, value, delta, delta_type, icon, color), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Calculate dimension KPIs
    city_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'city')
    channel_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'channel')
    cat_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'category')
    
    # Charts Row 1 - WITH LOCALIZED FILTERS
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-header">
                <div class="chart-title">📈 Revenue Trend</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Local filter for this chart
        trend_period = st.selectbox("Period", ["Daily", "Weekly", "Monthly"], key='trend_period', label_visibility="collapsed")
        
        daily = sim.calculate_daily_trends(sales_df, products_df)
        if daily is not None and len(daily) > 0:
            if trend_period == "Weekly":
                daily['date'] = pd.to_datetime(daily['date'])
                daily = daily.resample('W', on='date').sum().reset_index()
            elif trend_period == "Monthly":
                daily['date'] = pd.to_datetime(daily['date'])
                daily = daily.resample('M', on='date').sum().reset_index()
            
            fig = px.area(daily, x='date', y='revenue',
                         color_discrete_sequence=['#06b6d4'])
            fig = style_chart(fig)
            fig.update_traces(line=dict(width=3), fillcolor='rgba(6, 182, 212, 0.15)')
            fig.update_layout(title=None, margin=dict(t=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No trend data available")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-header">
                <div class="chart-title">🏙️ Performance by City</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Local filter
        city_metric = st.selectbox("Metric", ["Revenue", "Orders", "Margin %"], key='city_metric', label_visibility="collapsed")
        
        if city_kpis is not None and len(city_kpis) > 0:
            metric_col = 'revenue' if city_metric == "Revenue" else ('orders' if city_metric == "Orders" else 'profit_margin_pct')
            fig = px.bar(city_kpis, x='city', y=metric_col,
                        color='city', color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899'])
            fig = style_chart(fig)
            fig.update_layout(title=None, showlegend=False, margin=dict(t=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No city data available")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-header">
                <div class="chart-title">📦 Category Performance</div>
            </div>
        """, unsafe_allow_html=True)
        
        cat_view = st.selectbox("View", ["Revenue", "Margin %", "Orders"], key='cat_view', label_visibility="collapsed")
        
        if cat_kpis is not None and len(cat_kpis) > 0:
            y_col = 'revenue' if cat_view == "Revenue" else ('profit_margin_pct' if cat_view == "Margin %" else 'orders')
            fig = px.bar(cat_kpis.head(8), x='category', y=y_col,
                        color=y_col, color_continuous_scale=['#06b6d4', '#8b5cf6', '#ec4899'])
            fig = style_chart(fig)
            fig.update_layout(title=None, coloraxis_showscale=False, margin=dict(t=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-header">
                <div class="chart-title">📱 Channel Distribution</div>
            </div>
        """, unsafe_allow_html=True)
        
        channel_view = st.selectbox("View", ["Revenue Share", "Order Share"], key='channel_view', label_visibility="collapsed")
        
        if channel_kpis is not None and len(channel_kpis) > 0:
            val_col = 'revenue' if channel_view == "Revenue Share" else 'orders'
            fig = px.pie(channel_kpis, values=val_col, names='channel',
                        color_discrete_sequence=['#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b'], hole=0.45)
            fig = style_chart(fig)
            fig.update_layout(title=None, margin=dict(t=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No channel data available")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== KEY INSIGHTS =====
    st.markdown('<p class="section-title-premium">💡 Key Business Insights</p>', unsafe_allow_html=True)
    
    insights = generate_advanced_insights(kpis, sales_df, products_df, stores_df, st.session_state.sim_results)
    
    if insights:
        cols = st.columns(2)
        for i, insight in enumerate(insights):
            with cols[i % 2]:
                st.markdown(create_insight_card_html(
                    insight['icon'], 
                    insight['title'], 
                    insight['text']
                ), unsafe_allow_html=True)
    else:
        st.markdown(create_status_card_html("info", "ℹ️", "Limited Data", 
                   "More data is needed to generate actionable insights."), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== STRATEGIC RECOMMENDATIONS =====
    st.markdown('<p class="section-title-premium">📋 Strategic Recommendations</p>', unsafe_allow_html=True)
    
    stockout = sim.calculate_stockout_risk(inventory_df) if inventory_df is not None else {}
    recommendations = generate_strategic_recommendations(kpis, st.session_state.sim_results, stockout)
    
    st.markdown(create_recommendation_html("Action Items for Leadership", recommendations), unsafe_allow_html=True)

def show_manager_dashboard(sales_df, stores_df, products_df, inventory_df, kpis, sim):
    """Manager dashboard with operational metrics and alerts."""
    
    st.markdown('<p class="section-title-premium">⚙️ Operations Dashboard</p>', unsafe_allow_html=True)
    
    # Calculate operational metrics
    stockout = sim.calculate_stockout_risk(inventory_df) if inventory_df is not None else {'stockout_risk_pct': 0}
    
    # KPI Row
    cols = st.columns(4)
    stockout_color = "error" if stockout.get('stockout_risk_pct', 0) > 15 else "success"
    failure_rate = kpis.get('payment_failure_rate_pct', 0)
    failure_color = "error" if failure_rate > 5 else "success"
    
    metrics = [
        ("Stockout Risk", f"{stockout.get('stockout_risk_pct', 0):.1f}%", None, None, "📉", stockout_color),
        ("Return Rate", f"{kpis.get('return_rate_pct', 0):.1f}%", None, None, "🔄", "warning"),
        ("Payment Failures", f"{failure_rate:.1f}%", None, None, "💳", failure_color),
        ("Low Stock SKUs", f"{stockout.get('low_stock_items', 0):,}", None, None, "📦", "tertiary")
    ]
    
    for i, (label, value, delta, delta_type, icon, color) in enumerate(metrics):
        with cols[i]:
            st.markdown(create_metric_card_html(label, value, delta, delta_type, icon, color), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("**📊 Inventory Distribution**")
        
        inv_view = st.selectbox("Group by", ["City", "Category"], key='inv_view', label_visibility="collapsed")
        
        if inventory_df is not None and stores_df is not None:
            try:
                inv = inventory_df.copy()
                inv['stock_on_hand'] = pd.to_numeric(inv['stock_on_hand'], errors='coerce').fillna(0)
                
                if inv_view == "City":
                    inv = inv.merge(stores_df[['store_id', 'city']], on='store_id', how='left')
                    stock_by = inv.groupby('city')['stock_on_hand'].sum().reset_index()
                    fig = px.bar(stock_by, x='city', y='stock_on_hand',
                                color='stock_on_hand', color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'])
                else:
                    if products_df is not None:
                        inv = inv.merge(products_df[['product_id', 'category']], on='product_id', how='left')
                        stock_by = inv.groupby('category')['stock_on_hand'].sum().reset_index()
                        fig = px.bar(stock_by, x='category', y='stock_on_hand',
                                    color='stock_on_hand', color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'])
                    else:
                        fig = px.histogram(inv, x='stock_on_hand', nbins=30, color_discrete_sequence=['#8b5cf6'])
                
                fig = style_chart(fig)
                fig.update_layout(coloraxis_showscale=False, title=None, margin=dict(t=20))
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("Unable to generate inventory chart")
        else:
            st.info("No inventory data available")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("**⚠️ Top Risk Items**")
        
        if inventory_df is not None:
            try:
                inv = inventory_df.copy()
                inv['stock_on_hand'] = pd.to_numeric(inv['stock_on_hand'], errors='coerce').fillna(0)
                inv['reorder_point'] = pd.to_numeric(inv.get('reorder_point', 10), errors='coerce').fillna(10)
                inv['risk_score'] = inv['reorder_point'] - inv['stock_on_hand']
                
                top_risk = inv.nlargest(10, 'risk_score')[['product_id', 'store_id', 'stock_on_hand', 'risk_score']]
                top_risk['risk_score'] = top_risk['risk_score'].apply(lambda x: f"{'🔴' if x > 10 else '🟡'} {x:.0f}")
                
                st.dataframe(top_risk, use_container_width=True, height=300)
            except:
                st.info("Unable to calculate risk items")
        else:
            st.info("No inventory data available")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Operational Alerts
    st.markdown('<p class="section-title-premium">🚨 Operational Alerts</p>', unsafe_allow_html=True)
    
    alerts = []
    
    if stockout.get('stockout_risk_pct', 0) > 15:
        alerts.append(('error', '🔴', 'Critical Stockout Risk', 
                      f"{stockout['stockout_risk_pct']:.0f}% of SKUs at risk. Expedite reorders immediately."))
    
    if stockout.get('zero_stock', 0) > 0:
        alerts.append(('error', '⚠️', 'Out of Stock Items', 
                      f"{stockout['zero_stock']} items currently have zero stock."))
    
    if kpis.get('payment_failure_rate_pct', 0) > 5:
        alerts.append(('warning', '💳', 'Payment Gateway Issues', 
                      f"Failure rate at {kpis['payment_failure_rate_pct']:.1f}%. Investigate gateway performance."))
    
    if st.session_state.issues_df is not None and len(st.session_state.issues_df) > 0:
        alerts.append(('info', '📋', 'Data Quality Issues', 
                      f"{len(st.session_state.issues_df)} issues detected and logged."))
    
    if not alerts:
        alerts.append(('success', '✅', 'All Systems Normal', 
                      "All operational metrics within acceptable thresholds."))
    
    for alert_type, icon, title, text in alerts:
        st.markdown(create_status_card_html(alert_type, icon, title, text), unsafe_allow_html=True)

def show_advanced_analytics(sales_df, stores_df, products_df, inventory_df, kpis, sim):
    """Advanced analytics with EDA visualizations."""
    
    st.markdown('<p class="section-title-premium">🔬 Advanced Analytics</p>', unsafe_allow_html=True)
    
    st.markdown(create_status_card_html("info", "ℹ️", "Deep-Dive Analysis", 
               "These visualizations provide strategic insights not available in standard dashboards."), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # EDA Visualization 1: Price Elasticity
    st.markdown("### 📈 Price Elasticity Analysis")
    st.markdown("*Understanding how discounts impact sales volume and revenue*")
    
    with st.expander("🎛️ **Chart Filters**", expanded=True):
        pe_cols = st.columns(3)
        with pe_cols[0]:
            pe_category = ['All']
            if products_df is not None and 'category' in products_df.columns:
                pe_category += sorted(products_df['category'].dropna().unique().tolist())
            pe_cat_filter = st.selectbox("Category", pe_category, key='pe_category')
        with pe_cols[1]:
            pe_channel = ['All']
            if stores_df is not None and 'channel' in stores_df.columns:
                pe_channel += sorted(stores_df['channel'].dropna().unique().tolist())
            pe_chan_filter = st.selectbox("Channel", pe_channel, key='pe_channel')
    
    # Apply local filters
    pe_sales = sales_df.copy() if sales_df is not None else None
    if pe_sales is not None:
        if pe_cat_filter != 'All' and products_df is not None:
            cat_prods = products_df[products_df['category'] == pe_cat_filter]['product_id'].tolist()
            pe_sales = pe_sales[pe_sales['product_id'].isin(cat_prods)]
        if pe_chan_filter != 'All' and stores_df is not None:
            chan_stores = stores_df[stores_df['channel'] == pe_chan_filter]['store_id'].tolist()
            pe_sales = pe_sales[pe_sales['store_id'].isin(chan_stores)]
    
    fig_pe = create_price_elasticity_chart(pe_sales, products_df)
    if fig_pe:
        st.plotly_chart(fig_pe, use_container_width=True)
    else:
        st.info("Insufficient data for price elasticity analysis")
    
    st.markdown("---")
    
    # EDA Visualization 2: Category Performance Matrix
    st.markdown("### 🎯 Category Performance Matrix (BCG-Style)")
    st.markdown("*Identifying Stars, Cash Cows, Question Marks, and Dogs*")
    
    with st.expander("🎛️ **Chart Filters**", expanded=True):
        cp_cols = st.columns(2)
        with cp_cols[0]:
            cp_city = ['All']
            if stores_df is not None and 'city' in stores_df.columns:
                cp_city += sorted(stores_df['city'].dropna().unique().tolist())
            cp_city_filter = st.selectbox("City", cp_city, key='cp_city')
    
    cp_sales = sales_df.copy() if sales_df is not None else None
    if cp_sales is not None and cp_city_filter != 'All' and stores_df is not None:
        city_stores = stores_df[stores_df['city'] == cp_city_filter]['store_id'].tolist()
        cp_sales = cp_sales[cp_sales['store_id'].isin(city_stores)]
    
    fig_cp = create_category_performance_matrix(cp_sales, products_df)
    if fig_cp:
        st.plotly_chart(fig_cp, use_container_width=True)
    else:
        st.info("Insufficient data for category matrix")
    
    st.markdown("---")
    
    # EDA Visualization 3: Cohort Analysis
    st.markdown("### 👥 Customer Cohort Retention Analysis")
    st.markdown("*Understanding customer retention patterns over time*")
    
    fig_cohort = create_cohort_analysis_chart(sales_df)
    if fig_cohort:
        st.plotly_chart(fig_cohort, use_container_width=True)
    else:
        st.info("Insufficient data for cohort analysis")
    
    st.markdown("---")
    
    # Bonus: Revenue Waterfall
    st.markdown("### 💰 Revenue Waterfall Analysis")
    st.markdown("*Breaking down gross revenue to net revenue*")
    
    fig_waterfall = create_revenue_waterfall_chart(kpis, st.session_state.sim_results)
    if fig_waterfall:
        st.plotly_chart(fig_waterfall, use_container_width=True)
    else:
        st.info("Insufficient data for waterfall analysis")

# ============================================================================
# PAGE: HOME
# ============================================================================

def show_home_page():
    """Display the home page."""
    
    if not st.session_state.data_loaded:
        # Hero Section
        st.markdown("""
        <div class="hero-premium" style="text-align: center;">
            <div class="hero-badges">
                <span class="hero-badge-premium">✨ UAE E-Commerce Analytics</span>
                <span class="hero-badge-premium" style="background: var(--gradient-secondary);">🚀 v3.0 Premium</span>
            </div>
            <div class="hero-title-premium">Promo Pulse Simulator</div>
            <p class="hero-subtitle-premium">
                Data Rescue Toolkit + What-If Campaign Simulation<br>
                For UAE Omnichannel Retailers: Dubai • Abu Dhabi • Sharjah
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features
        st.markdown('<p class="section-title-premium">✨ Key Features</p>', unsafe_allow_html=True)
        
        cols = st.columns(4)
        features = [
            ("📂", "Data Upload", "Upload and preview your e-commerce CSV files with instant validation", "primary"),
            ("🧹", "Data Rescue", "Detect & auto-fix 15+ types of data quality issues", "secondary"),
            ("🎯", "Simulator", "Run what-if scenarios and forecast campaign ROI", "tertiary"),
            ("📊", "Dashboard", "Executive & Manager views with real-time KPIs", "quaternary")
        ]
        
        for i, (icon, title, desc, color) in enumerate(features):
            with cols[i]:
                st.markdown(f"""
                <div class="feature-card-premium">
                    <div class="feature-icon-premium">{icon}</div>
                    <div class="feature-title-premium">{title}</div>
                    <div class="feature-desc-premium">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # How it works
        st.markdown('<p class="section-title-premium">🔄 How It Works</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="glass-container">
                <h4 style="color: var(--accent-primary); margin-top: 0;">📥 Phase 1: Data Rescue Toolkit</h4>
                <ul style="color: var(--text-secondary); line-height: 2;">
                    <li>Upload dirty/raw datasets (CSV)</li>
                    <li>Automatic validation & issue detection</li>
                    <li>Clean data with documented fixes</li>
                    <li>Download issues log & cleaned data</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="glass-container">
                <h4 style="color: var(--accent-tertiary); margin-top: 0;">🎯 Phase 2: Promo Pulse Simulator</h4>
                <ul style="color: var(--text-secondary); line-height: 2;">
                    <li>Set discount %, budget & margin floor</li>
                    <li>Target by city, channel, category</li>
                    <li>See projected ROI & demand lift</li>
                    <li>Constraint violation warnings</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Getting started
        st.markdown(create_status_card_html("info", "🚀", "Get Started",
                   "Click on <strong>📂 Upload</strong> in the navigation bar above to load your data files."), unsafe_allow_html=True)
        
    else:
        # Data loaded view
        st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <div style="font-size: 4rem; margin-bottom: 15px;">🛒</div>
            <div class="hero-title-premium" style="font-size: 3rem;">Promo Pulse Simulator</div>
            <p style="color: var(--text-secondary); font-size: 1.1rem;">Data Loaded & Ready for Analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Status cards
        cols = st.columns(4)
        counts = [
            ("Products", len(st.session_state.raw_products) if st.session_state.raw_products is not None else 0, "📦", "primary"),
            ("Stores", len(st.session_state.raw_stores) if st.session_state.raw_stores is not None else 0, "🏪", "secondary"),
            ("Sales", len(st.session_state.raw_sales) if st.session_state.raw_sales is not None else 0, "🛒", "tertiary"),
            ("Inventory", len(st.session_state.raw_inventory) if st.session_state.raw_inventory is not None else 0, "📋", "quaternary")
        ]
        
        for i, (label, count, icon, color) in enumerate(counts):
            with cols[i]:
                st.markdown(create_metric_card_html(label, f"{count:,}", None, None, icon, color), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.session_state.is_cleaned:
            st.markdown(create_status_card_html("success", "✅", "Data Ready",
                       "Data has been cleaned and validated. Ready for simulation and analysis!"), unsafe_allow_html=True)
        else:
            st.markdown(create_status_card_html("warning", "⏳", "Cleaning Required",
                       "Data loaded but not yet cleaned. Go to <strong>🧹 Rescue</strong> to validate and fix issues."), unsafe_allow_html=True)
        
        # Next steps
        st.markdown('<p class="section-title-premium">📋 Next Steps</p>', unsafe_allow_html=True)
        
        cols = st.columns(3)
        steps = [
            ("✅" if st.session_state.is_cleaned else "1️⃣", "Clean Data", "Go to Rescue to validate and fix data quality issues.", "primary"),
            ("✅" if st.session_state.sim_results else "2️⃣", "Run Simulation", "Go to Simulator to test discount scenarios.", "tertiary"),
            ("3️⃣", "View Dashboard", "Go to Dashboard for Executive & Manager insights.", "quaternary")
        ]
        
        for i, (step, title, desc, color) in enumerate(steps):
            with cols[i]:
                st.markdown(f"""
                <div class="glass-container" style="text-align: center; height: 150px;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">{step}</div>
                    <div style="font-weight: 700; color: var(--accent-{color}); margin-bottom: 8px;">{title}</div>
                    <div style="color: var(--text-secondary); font-size: 0.9rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
    
    show_footer()

# ============================================================================
# PAGE: DATA UPLOAD
# ============================================================================

def show_upload_page():
    """Display the data upload page."""
    
    st.markdown('<h1 class="page-title-premium">📂 Data Upload</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle-premium">Upload your e-commerce data files or load sample data</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Upload section
    st.markdown('<p class="section-title-premium">📤 Upload Files</p>', unsafe_allow_html=True)
    
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
    st.markdown('<p class="section-title-premium">📦 Or Load Sample Data</p>', unsafe_allow_html=True)
    
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
        st.markdown('<p class="section-title-premium">👀 Data Preview</p>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📦 Products", "🏪 Stores", "🛒 Sales", "📋 Inventory"])
        
        datasets = [
            (tab1, st.session_state.raw_products, "Products"),
            (tab2, st.session_state.raw_stores, "Stores"),
            (tab3, st.session_state.raw_sales, "Sales"),
            (tab4, st.session_state.raw_inventory, "Inventory")
        ]
        
        for tab, df, name in datasets:
            with tab:
                if df is not None:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(create_metric_card_html("Rows", f"{len(df):,}", None, None, "📊", "primary"), unsafe_allow_html=True)
                    with col2:
                        st.markdown(create_metric_card_html("Columns", f"{len(df.columns)}", None, None, "📋", "secondary"), unsafe_allow_html=True)
                    with col3:
                        null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
                        st.markdown(create_metric_card_html("Null %", f"{null_pct:.1f}%", None, None, "⚠️", "warning"), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.dataframe(df.head(100), use_container_width=True)
                else:
                    st.info(f"No {name} data loaded")
    
    show_footer()

# ============================================================================
# PAGE: DATA RESCUE
# ============================================================================

def show_rescue_page():
    """Display the data rescue page."""
    
    st.markdown('<h1 class="page-title-premium">🧹 Data Rescue Center</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle-premium">Validate, detect issues, and clean your data automatically</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.markdown(create_status_card_html("warning", "⚠️", "No Data", 
                   "Please load data first. Go to 📂 Upload page."), unsafe_allow_html=True)
        show_footer()
        return
    
    # Issue types
    st.markdown('<p class="section-title-premium">🔍 Issues We Detect & Fix</p>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    issue_types = [
        ("Data Quality", ["Missing values", "Duplicate records", "Null representations"], "primary"),
        ("Format Issues", ["Invalid timestamps", "Inconsistent cities", "Mixed case values"], "tertiary"),
        ("Value Issues", ["Outliers & negatives", "FK violations", "Invalid categories"], "quaternary")
    ]
    
    for i, (title, items, color) in enumerate(issue_types):
        with cols[i]:
            items_html = "".join([f"<li>{item}</li>" for item in items])
            st.markdown(f"""
            <div class="glass-container">
                <strong style="color: var(--accent-{color});">{title}</strong>
                <ul style="color: var(--text-secondary); margin-bottom: 0; line-height: 2;">{items_html}</ul>
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
        st.markdown('<p class="section-title-premium">📊 Cleaning Results</p>', unsafe_allow_html=True)
        
        stats = st.session_state.cleaner_stats
        
        if stats:
            cols = st.columns(4)
            datasets = ['products', 'stores', 'sales', 'inventory']
            colors = ['primary', 'secondary', 'tertiary', 'quaternary']
            icons = ['📦', '🏪', '🛒', '📋']
            
            for i, (ds, color, icon) in enumerate(zip(datasets, colors, icons)):
                with cols[i]:
                    before = stats.get(ds, {}).get('before', 0)
                    after = stats.get(ds, {}).get('after', 0)
                    delta = f"{before - after} fixed" if before > after else "Clean"
                    delta_type = "negative" if before > after else "positive"
                    st.markdown(create_metric_card_html(ds.title(), f"{after:,}", delta, delta_type, icon, color), unsafe_allow_html=True)
        
        issues_df = st.session_state.issues_df
        
        if issues_df is not None and len(issues_df) > 0:
            st.markdown("---")
            st.markdown('<p class="section-title-premium">🔍 Issues Detected</p>', unsafe_allow_html=True)
            
            st.markdown(create_status_card_html("success", "✅", "Issues Fixed",
                       f"Total {len(issues_df)} issues detected and fixed automatically!"), unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                issue_counts = issues_df['issue_type'].value_counts().reset_index()
                issue_counts.columns = ['Issue Type', 'Count']
                
                fig = px.bar(issue_counts, x='Count', y='Issue Type', orientation='h',
                           color='Count', color_continuous_scale=['#06b6d4', '#8b5cf6'])
                fig = style_chart(fig)
                fig.update_layout(title='Issues by Type', coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                issue_counts_sorted = issue_counts.sort_values('Count', ascending=False)
                issue_counts_sorted['Cumulative %'] = (issue_counts_sorted['Count'].cumsum() / issue_counts_sorted['Count'].sum() * 100)
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(go.Bar(x=issue_counts_sorted['Issue Type'], y=issue_counts_sorted['Count'],
                                    name='Count', marker_color='#06b6d4'), secondary_y=False)
                fig.add_trace(go.Scatter(x=issue_counts_sorted['Issue Type'], y=issue_counts_sorted['Cumulative %'],
                                        name='Cumulative %', marker_color='#ec4899', mode='lines+markers'),
                             secondary_y=True)
                fig = style_chart(fig)
                fig.update_layout(title='Pareto Chart')
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<p class="section-title-premium">📋 Issues Log</p>', unsafe_allow_html=True)
            st.dataframe(issues_df, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                csv_issues = issues_df.to_csv(index=False)
                st.download_button("📥 Download Issues Log", csv_issues, "issues.csv", "text/csv")
            with col2:
                if st.session_state.clean_sales is not None:
                    csv_sales = st.session_state.clean_sales.to_csv(index=False)
                    st.download_button("📥 Download Cleaned Sales", csv_sales, "cleaned_sales.csv", "text/csv")
        else:
            st.markdown(create_status_card_html("success", "✅", "Clean Data",
                       "No issues found! Your data is already clean."), unsafe_allow_html=True)
    
    show_footer()

# ============================================================================
# PAGE: SIMULATOR
# ============================================================================

def show_simulator_page():
    """Display the simulator page."""
    
    st.markdown('<h1 class="page-title-premium">🎯 Promo Pulse Simulator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle-premium">Run what-if discount scenarios with budget & margin constraints</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.markdown(create_status_card_html("warning", "⚠️", "No Data",
                   "Please load data first."), unsafe_allow_html=True)
        show_footer()
        return
    
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    
    # Parameters
    st.markdown('<p class="section-title-premium">⚙️ Campaign Parameters</p>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown("**💰 Pricing**")
        discount_pct = st.slider("Discount %", 0, 50, 15, key='sim_discount')
        promo_budget = st.number_input("Budget (AED)", 1000, 500000, 25000, step=5000, key='sim_budget')
    
    with cols[1]:
        st.markdown("**📊 Constraints**")
        margin_floor = st.slider("Margin Floor %", 0, 50, 15, key='sim_margin')
        campaign_days = st.slider("Campaign Days", 1, 30, 7, key='sim_days')
    
    with cols[2]:
        st.markdown("**🎯 Targeting**")
        
        cities = ['All']
        channels = ['All']
        categories = ['All']
        
        if stores_df is not None and 'city' in stores_df.columns:
            cities += [str(c) for c in stores_df['city'].dropna().unique().tolist()]
        if stores_df is not None and 'channel' in stores_df.columns:
            channels += [str(c) for c in stores_df['channel'].dropna().unique().tolist()]
        if products_df is not None and 'category' in products_df.columns:
            categories += [str(c) for c in products_df['category'].dropna().unique().tolist()]
        
        city = st.selectbox("City", cities, key='sim_city')
        channel = st.selectbox("Channel", channels, key='sim_channel')
        category = st.selectbox("Category", categories, key='sim_category')
    
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
        st.markdown('<p class="section-title-premium">📊 Simulation Results</p>', unsafe_allow_html=True)
        
        cols = st.columns(4)
        metrics = [
            ("Expected Revenue", f"AED {outputs.get('expected_revenue', 0):,.0f}", 
             f"{comparison.get('revenue_change_pct', 0):+.1f}%", 
             "positive" if comparison.get('revenue_change_pct', 0) > 0 else "negative", "💰", "primary"),
            ("Net Profit", f"AED {outputs.get('expected_net_profit', 0):,.0f}",
             f"{comparison.get('profit_change_pct', 0):+.1f}%",
             "positive" if comparison.get('profit_change_pct', 0) > 0 else "negative", "💎", "success"),
            ("ROI", f"{outputs.get('roi_pct', 0):.1f}%", None, None, "📈", 
             "success" if outputs.get('roi_pct', 0) > 0 else "error"),
            ("Budget Used", f"{(outputs.get('promo_cost', 0) / promo_budget * 100) if promo_budget > 0 else 0:.1f}%",
             None, None, "🎯", "warning")
        ]
        
        for i, (label, value, delta, delta_type, icon, color) in enumerate(metrics):
            with cols[i]:
                st.markdown(create_metric_card_html(label, value, delta, delta_type, icon, color), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        cols = st.columns(4)
        metrics2 = [
            ("Demand Lift", f"+{outputs.get('demand_lift_pct', 0):.1f}%", None, None, "📈", "tertiary"),
            ("Exp. Margin", f"{outputs.get('expected_margin_pct', 0):.1f}%", None, None, "📊",
             "success" if outputs.get('expected_margin_pct', 0) >= margin_floor else "warning"),
            ("Promo Cost", f"AED {outputs.get('promo_cost', 0):,.0f}", None, None, "💸", "warning"),
            ("Expected Orders", f"{outputs.get('expected_orders', 0):,}", None, None, "📦", "secondary")
        ]
        
        for i, (label, value, delta, delta_type, icon, color) in enumerate(metrics2):
            with cols[i]:
                st.markdown(create_metric_card_html(label, value, delta, delta_type, icon, color), unsafe_allow_html=True)
        
        # Violations
        if constraint_violations:
            st.markdown("---")
            st.markdown('<p class="section-title-premium">⚠️ Constraint Violations</p>', unsafe_allow_html=True)
            for v in constraint_violations:
                st.markdown(create_status_card_html("error", "❌", v.get('constraint', 'Unknown'),
                           v.get('message', 'No details')), unsafe_allow_html=True)
        
        if warnings:
            for w in warnings:
                st.markdown(create_status_card_html("warning", "⚠️", "Warning", w), unsafe_allow_html=True)
        
        if not warnings and not constraint_violations:
            st.markdown(create_status_card_html("success", "✅", "Campaign Healthy",
                       "All metrics within acceptable range. Campaign looks good!"), unsafe_allow_html=True)
        
        # Comparison chart
        st.markdown("---")
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
            fig = style_chart(fig)
            fig.update_layout(barmode='group', title='Revenue & Profit Comparison')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            orders_data = pd.DataFrame({
                'Type': ['Baseline', 'Campaign'],
                'Orders': [comparison.get('baseline_orders', 0), outputs.get('expected_orders', 0)]
            })
            
            fig = px.bar(orders_data, x='Type', y='Orders', color='Type',
                        color_discrete_sequence=['#8b5cf6', '#ec4899'])
            fig = style_chart(fig)
            fig.update_layout(title='Orders Comparison', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    show_footer()

# ============================================================================
# PAGE: FACULTY TEST
# ============================================================================

def show_test_page():
    """Faculty dataset testing page."""
    
    st.markdown('<h1 class="page-title-premium">🔧 Faculty Dataset Test</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle-premium">Upload faculty-provided dataset and map columns to expected schema</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Upload CSV/Excel file", type=['csv', 'xlsx'], key='faculty_upload')
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                faculty_df = pd.read_excel(uploaded_file)
            else:
                faculty_df = pd.read_csv(uploaded_file)
            
            st.markdown(create_status_card_html("success", "✅", "File Loaded",
                       f"{len(faculty_df)} rows, {len(faculty_df.columns)} columns"), unsafe_allow_html=True)
            
            st.markdown("**Detected Columns:**")
            st.write(faculty_df.columns.tolist())
            
            st.markdown("---")
            st.markdown('<p class="section-title-premium">🔗 Column Mapping</p>', unsafe_allow_html=True)
            
            available_cols = ['-- Not Mapped --'] + faculty_df.columns.tolist()
            
            expected_cols = {
                'Sales': ['order_id', 'order_time', 'product_id', 'store_id', 'qty', 'selling_price_aed', 'discount_pct', 'payment_status', 'return_flag'],
                'Products': ['product_id', 'category', 'brand', 'base_price_aed', 'unit_cost_aed'],
                'Stores': ['store_id', 'city', 'channel', 'fulfillment_type'],
                'Inventory': ['product_id', 'store_id', 'stock_on_hand', 'reorder_point']
            }
            
            table_type = st.selectbox("Data Type", list(expected_cols.keys()))
            
            mappings = {}
            cols = st.columns(3)
            for i, expected_col in enumerate(expected_cols[table_type]):
                with cols[i % 3]:
                    mappings[expected_col] = st.selectbox(f"→ {expected_col}", available_cols, key=f'map_{expected_col}')
            
            if st.button("✅ Apply Mapping & Validate", use_container_width=True):
                mapped_df = pd.DataFrame()
                for expected_col, source_col in mappings.items():
                    if source_col != '-- Not Mapped --':
                        mapped_df[expected_col] = faculty_df[source_col]
                    else:
                        mapped_df[expected_col] = None
                
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
                
                st.success(f"✅ Mapped to {table_type}!")
                st.dataframe(mapped_df.head(20), use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    show_footer()

# ============================================================================
# MAIN ROUTING
# ============================================================================

page = st.session_state.current_page

if page == "Home":
    show_home_page()
elif page == "Upload":
    show_upload_page()
elif page == "Rescue":
    show_rescue_page()
elif page == "Simulator":
    show_simulator_page()
elif page == "Dashboard":
    show_dashboard_page()
elif page == "Test":
    show_test_page()
