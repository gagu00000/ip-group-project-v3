# ============================================================================
# UAE Pulse Simulator + Data Rescue Dashboard
# Main Streamlit Application - EXECUTIVE THEME v3.1 COMPLETE
# All Charts, Insights & Light/Dark Mode Fixed
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
# THEME STATE INITIALIZATION
# ============================================================================

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# ============================================================================
# GET THEME COLORS (for use in Python)
# ============================================================================

def get_theme_colors():
    """Return color dictionary based on current theme."""
    is_dark = st.session_state.theme == 'dark'
    
    if is_dark:
        return {
            'bg_primary': '#0a0a0f',
            'bg_secondary': '#12121a',
            'bg_card': 'rgba(22, 22, 31, 0.95)',
            'text_primary': '#f8fafc',
            'text_secondary': '#cbd5e1',
            'text_muted': '#64748b',
            'border_default': 'rgba(148, 163, 184, 0.1)',
            'chart_bg': 'rgba(0,0,0,0)',
            'chart_grid': '#1e293b',
            'chart_text': '#e2e8f0',
            'chart_title': '#f1f5f9',
        }
    else:
        return {
            'bg_primary': '#f8fafc',
            'bg_secondary': '#ffffff',
            'bg_card': 'rgba(255, 255, 255, 0.95)',
            'text_primary': '#0f172a',
            'text_secondary': '#475569',
            'text_muted': '#64748b',
            'border_default': 'rgba(0, 0, 0, 0.08)',
            'chart_bg': 'rgba(0,0,0,0)',
            'chart_grid': '#e2e8f0',
            'chart_text': '#1e293b',
            'chart_title': '#0f172a',
        }

# ============================================================================
# DYNAMIC THEME CSS GENERATOR
# ============================================================================

def get_theme_css():
    """Generate CSS based on current theme state."""
    
    is_dark = st.session_state.theme == 'dark'
    
    if is_dark:
        colors = {
            'bg_primary': '#0a0a0f',
            'bg_secondary': '#12121a',
            'bg_tertiary': '#1a1a24',
            'bg_card': 'rgba(22, 22, 31, 0.95)',
            'bg_card_hover': 'rgba(30, 30, 45, 0.98)',
            'bg_glass': 'rgba(255, 255, 255, 0.03)',
            'bg_glass_border': 'rgba(255, 255, 255, 0.08)',
            
            'text_primary': '#f8fafc',
            'text_secondary': '#cbd5e1',
            'text_muted': '#64748b',
            'text_inverse': '#0f172a',
            
            'border_default': 'rgba(148, 163, 184, 0.1)',
            'border_hover': 'rgba(6, 182, 212, 0.4)',
            
            'shadow_sm': '0 2px 8px rgba(0, 0, 0, 0.3)',
            'shadow_md': '0 4px 20px rgba(0, 0, 0, 0.4)',
            'shadow_lg': '0 8px 40px rgba(0, 0, 0, 0.5)',
            'shadow_xl': '0 16px 60px rgba(0, 0, 0, 0.6)',
            'shadow_glow_cyan': '0 0 40px rgba(6, 182, 212, 0.15)',
            'shadow_glow_purple': '0 0 40px rgba(139, 92, 246, 0.15)',
            
            'gradient_hero': 'linear-gradient(135deg, rgba(6, 182, 212, 0.12) 0%, rgba(139, 92, 246, 0.12) 50%, rgba(236, 72, 153, 0.08) 100%)',
            'gradient_card': 'linear-gradient(145deg, rgba(22, 22, 31, 0.9) 0%, rgba(26, 26, 36, 0.95) 100%)',
            'gradient_sidebar': 'linear-gradient(180deg, #0d0d14 0%, #0f0f18 50%, #0a0a0f 100%)',
        }
    else:
        colors = {
            'bg_primary': '#f8fafc',
            'bg_secondary': '#ffffff',
            'bg_tertiary': '#f1f5f9',
            'bg_card': 'rgba(255, 255, 255, 0.95)',
            'bg_card_hover': 'rgba(248, 250, 252, 0.98)',
            'bg_glass': 'rgba(255, 255, 255, 0.7)',
            'bg_glass_border': 'rgba(0, 0, 0, 0.08)',
            
            'text_primary': '#0f172a',
            'text_secondary': '#475569',
            'text_muted': '#64748b',
            'text_inverse': '#f8fafc',
            
            'border_default': 'rgba(0, 0, 0, 0.08)',
            'border_hover': 'rgba(6, 182, 212, 0.5)',
            
            'shadow_sm': '0 2px 8px rgba(0, 0, 0, 0.06)',
            'shadow_md': '0 4px 20px rgba(0, 0, 0, 0.08)',
            'shadow_lg': '0 8px 40px rgba(0, 0, 0, 0.1)',
            'shadow_xl': '0 16px 60px rgba(0, 0, 0, 0.12)',
            'shadow_glow_cyan': '0 0 40px rgba(6, 182, 212, 0.1)',
            'shadow_glow_purple': '0 0 40px rgba(139, 92, 246, 0.1)',
            
            'gradient_hero': 'linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(139, 92, 246, 0.08) 50%, rgba(236, 72, 153, 0.05) 100%)',
            'gradient_card': 'linear-gradient(145deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.95) 100%)',
            'gradient_sidebar': 'linear-gradient(180deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%)',
        }
    
    return f"""
    <style>
        /* ===== GOOGLE FONTS ===== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        /* ===== CSS CUSTOM PROPERTIES ===== */
        :root {{
            --bg-primary: {colors['bg_primary']};
            --bg-secondary: {colors['bg_secondary']};
            --bg-tertiary: {colors['bg_tertiary']};
            --bg-card: {colors['bg_card']};
            --bg-card-hover: {colors['bg_card_hover']};
            --bg-glass: {colors['bg_glass']};
            --bg-glass-border: {colors['bg_glass_border']};
            
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --text-muted: {colors['text_muted']};
            --text-inverse: {colors['text_inverse']};
            
            --border-default: {colors['border_default']};
            --border-hover: {colors['border_hover']};
            
            --shadow-sm: {colors['shadow_sm']};
            --shadow-md: {colors['shadow_md']};
            --shadow-lg: {colors['shadow_lg']};
            --shadow-xl: {colors['shadow_xl']};
            --shadow-glow-cyan: {colors['shadow_glow_cyan']};
            --shadow-glow-purple: {colors['shadow_glow_purple']};
            
            --accent-cyan: #06b6d4;
            --accent-cyan-light: #22d3ee;
            --accent-blue: #3b82f6;
            --accent-blue-light: #60a5fa;
            --accent-purple: #8b5cf6;
            --accent-purple-light: #a78bfa;
            --accent-pink: #ec4899;
            --accent-pink-light: #f472b6;
            --accent-green: #10b981;
            --accent-green-light: #34d399;
            --accent-orange: #f59e0b;
            --accent-orange-light: #fbbf24;
            --accent-red: #ef4444;
            --accent-red-light: #f87171;
            --accent-teal: #14b8a6;
            --accent-teal-light: #2dd4bf;
            
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 24px;
            --radius-2xl: 32px;
            
            --transition-fast: 0.15s ease;
            --transition-normal: 0.25s ease;
            --transition-slow: 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        
        /* ===== KEYFRAME ANIMATIONS ===== */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes pulse3D {{
            0%, 100% {{ 
                box-shadow: var(--shadow-md), 0 0 20px rgba(6, 182, 212, 0.2);
                transform: translateY(0);
            }}
            50% {{ 
                box-shadow: var(--shadow-lg), 0 0 40px rgba(6, 182, 212, 0.35);
                transform: translateY(-2px);
            }}
        }}
        
        @keyframes float3D {{
            0%, 100% {{ transform: translateY(0) rotateX(0deg); }}
            50% {{ transform: translateY(-8px) rotateX(2deg); }}
        }}
        
        @keyframes gradientFlow {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        /* ===== HIDE STREAMLIT DEFAULTS ===== */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{display: none;}}
        
        /* ===== MAIN APP CONTAINER ===== */
        .stApp {{
            background: var(--bg-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            min-height: 100vh;
            transition: background var(--transition-normal);
        }}
        
        .stApp::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(ellipse at 20% 20%, rgba(6, 182, 212, 0.06) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, rgba(139, 92, 246, 0.06) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 80%, rgba(236, 72, 153, 0.04) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }}
        
        /* ===== SIDEBAR ===== */
        [data-testid="stSidebar"] {{
            background: {colors['gradient_sidebar']};
            border-right: 1px solid var(--border-default);
            box-shadow: 4px 0 30px rgba(0, 0, 0, 0.15);
        }}
        
        [data-testid="stSidebar"]::before {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 3px;
            height: 100%;
            background: linear-gradient(180deg, var(--accent-cyan), var(--accent-purple), var(--accent-pink));
            opacity: 0.8;
        }}
        
        /* ===== TYPOGRAPHY ===== */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Inter', sans-serif;
            color: var(--text-primary);
            font-weight: 700;
        }}
        
        p, span, div, label {{
            color: var(--text-secondary);
        }}
        
        /* ===== 3D METRIC CARDS ===== */
        .metric-card-3d {{
            background: {colors['gradient_card']};
            backdrop-filter: blur(20px);
            border-radius: var(--radius-xl);
            padding: 28px 24px;
            border: 1px solid var(--border-default);
            box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            transition: all var(--transition-slow);
            position: relative;
            overflow: hidden;
            height: 150px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        
        .metric-card-3d::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
            opacity: 0;
            transition: opacity var(--transition-normal);
        }}
        
        .metric-card-3d:hover {{
            transform: translateY(-8px) rotateX(2deg);
            box-shadow: var(--shadow-xl), 0 20px 40px rgba(6, 182, 212, 0.1);
            border-color: var(--border-hover);
        }}
        
        .metric-card-3d:hover::before {{
            opacity: 1;
        }}
        
        .metric-label {{
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            margin: 8px 0;
        }}
        
        .metric-value-cyan {{ color: var(--accent-cyan); }}
        .metric-value-blue {{ color: var(--accent-blue); }}
        .metric-value-purple {{ color: var(--accent-purple); }}
        .metric-value-pink {{ color: var(--accent-pink); }}
        .metric-value-green {{ color: var(--accent-green); }}
        .metric-value-orange {{ color: var(--accent-orange); }}
        .metric-value-teal {{ color: var(--accent-teal); }}
        
        .metric-delta {{
            font-size: 0.85rem;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        
        .metric-delta-positive {{
            color: var(--accent-green);
            background: rgba(16, 185, 129, 0.12);
        }}
        
        .metric-delta-negative {{
            color: var(--accent-red);
            background: rgba(239, 68, 68, 0.12);
        }}
        
        /* ===== 3D FEATURE CARDS ===== */
        .feature-card-3d {{
            background: {colors['gradient_card']};
            backdrop-filter: blur(20px);
            border-radius: var(--radius-xl);
            padding: 40px 28px;
            border: 1px solid var(--border-default);
            box-shadow: var(--shadow-md);
            transition: all var(--transition-slow);
            height: 240px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }}
        
        .feature-card-3d:hover {{
            transform: translateY(-12px) scale(1.02);
            box-shadow: var(--shadow-xl), 0 30px 60px rgba(6, 182, 212, 0.15);
            border-color: var(--border-hover);
        }}
        
        .feature-icon {{
            font-size: 3.5rem;
            margin-bottom: 20px;
            animation: float3D 4s ease-in-out infinite;
        }}
        
        .feature-title {{
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 10px;
            color: var(--text-primary);
        }}
        
        .feature-desc {{
            font-size: 0.9rem;
            color: var(--text-muted);
            line-height: 1.6;
        }}
        
        /* ===== HERO SECTION ===== */
        .hero-container {{
            background: {colors['gradient_hero']};
            backdrop-filter: blur(20px);
            border-radius: var(--radius-2xl);
            padding: 60px 50px;
            margin-bottom: 40px;
            border: 1px solid var(--border-default);
            box-shadow: var(--shadow-lg);
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.8s ease-out;
        }}
        
        .hero-title {{
            font-size: 4rem;
            font-weight: 900;
            background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-cyan) 40%, var(--accent-purple) 70%, var(--accent-pink) 100%);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 20px;
            line-height: 1.1;
            animation: gradientFlow 5s ease infinite;
        }}
        
        .hero-subtitle {{
            font-size: 1.25rem;
            color: var(--text-secondary);
            line-height: 1.7;
            max-width: 700px;
        }}
        
        .hero-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 24px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
            border-radius: 50px;
            color: white;
            font-size: 0.9rem;
            font-weight: 600;
            margin-right: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
        }}
        
        /* ===== PAGE TITLES ===== */
        .page-title {{
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 8px;
            animation: fadeInUp 0.5s ease-out;
        }}
        
        .page-title-cyan {{ color: var(--accent-cyan); }}
        .page-title-blue {{ color: var(--accent-blue); }}
        .page-title-purple {{ color: var(--accent-purple); }}
        .page-title-pink {{ color: var(--accent-pink); }}
        .page-title-green {{ color: var(--accent-green); }}
        .page-title-teal {{ color: var(--accent-teal); }}
        .page-title-orange {{ color: var(--accent-orange); }}
        
        .page-description {{
            color: var(--text-secondary);
            font-size: 1.15rem;
            margin-bottom: 24px;
        }}
        
        /* ===== SECTION TITLES ===== */
        .section-title {{
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 20px;
            color: var(--text-primary);
        }}
        
        .section-title-cyan {{ color: var(--accent-cyan) !important; }}
        .section-title-blue {{ color: var(--accent-blue) !important; }}
        .section-title-purple {{ color: var(--accent-purple) !important; }}
        .section-title-pink {{ color: var(--accent-pink) !important; }}
        .section-title-green {{ color: var(--accent-green) !important; }}
        .section-title-teal {{ color: var(--accent-teal) !important; }}
        .section-title-orange {{ color: var(--accent-orange) !important; }}
        
        /* ===== INFO/ALERT CARDS ===== */
        .info-card {{
            background: {colors['gradient_card']};
            backdrop-filter: blur(15px);
            border-radius: var(--radius-lg);
            padding: 22px 28px;
            border: 1px solid var(--border-default);
            border-left: 4px solid var(--accent-cyan);
            box-shadow: var(--shadow-sm);
            margin: 15px 0;
            transition: all var(--transition-normal);
            color: var(--text-secondary);
        }}
        
        .info-card:hover {{
            transform: translateX(8px);
            box-shadow: var(--shadow-md);
        }}
        
        .success-card {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(20, 184, 166, 0.08) 100%);
            backdrop-filter: blur(15px);
            border-radius: var(--radius-lg);
            padding: 22px 28px;
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-left: 4px solid var(--accent-green);
            margin: 15px 0;
            color: var(--text-primary);
        }}
        
        .warning-card {{
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(251, 146, 60, 0.08) 100%);
            backdrop-filter: blur(15px);
            border-radius: var(--radius-lg);
            padding: 22px 28px;
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-left: 4px solid var(--accent-orange);
            margin: 15px 0;
            color: var(--text-primary);
        }}
        
        .error-card {{
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(236, 72, 153, 0.08) 100%);
            backdrop-filter: blur(15px);
            border-radius: var(--radius-lg);
            padding: 22px 28px;
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-left: 4px solid var(--accent-red);
            margin: 15px 0;
            color: var(--text-primary);
        }}
        
        /* ===== INSIGHT CARD ===== */
        .insight-card {{
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.08) 100%);
            backdrop-filter: blur(15px);
            border-radius: var(--radius-lg);
            padding: 22px 28px;
            border: 1px solid rgba(139, 92, 246, 0.25);
            margin: 15px 0;
        }}
        
        .insight-card:hover {{
            transform: translateX(8px);
            border-color: var(--accent-purple);
        }}
        
        .insight-title {{
            color: var(--accent-purple-light);
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 8px;
        }}
        
        .insight-text {{
            color: var(--text-primary);
            font-size: 1rem;
            line-height: 1.6;
        }}
        
        /* ===== RECOMMENDATION CARD ===== */
        .recommendation-card {{
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(59, 130, 246, 0.08));
            border-left: 4px solid var(--accent-purple);
            padding: 16px 20px;
            border-radius: var(--radius-md);
            margin-bottom: 12px;
        }}
        
        .recommendation-card p {{
            color: var(--text-primary);
            margin: 0;
            font-size: 1rem;
        }}
        
        /* ===== ALERT CARD ===== */
        .alert-card {{
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(245, 158, 11, 0.08));
            border-left: 4px solid var(--accent-orange);
            padding: 16px 20px;
            border-radius: var(--radius-md);
            margin-bottom: 12px;
        }}
        
        .alert-card p {{
            color: var(--text-primary);
            margin: 0;
            font-size: 1rem;
        }}
        
        /* ===== TABS ===== */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: {colors['gradient_card']};
            border-radius: var(--radius-md);
            color: var(--text-secondary);
            padding: 14px 28px;
            border: 1px solid var(--border-default);
            font-weight: 600;
            box-shadow: var(--shadow-sm);
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-hover);
            transform: translateY(-3px);
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue)) !important;
            color: white !important;
            border: none !important;
            box-shadow: var(--shadow-md), 0 4px 20px rgba(6, 182, 212, 0.3);
        }}
        
        /* ===== BUTTONS ===== */
        .stButton > button {{
            background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
            color: white;
            border: none;
            border-radius: var(--radius-lg);
            padding: 16px 36px;
            font-weight: 700;
            box-shadow: var(--shadow-md), 0 4px 15px rgba(6, 182, 212, 0.25);
            transition: all var(--transition-normal);
        }}
        
        .stButton > button:hover {{
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg), 0 8px 30px rgba(59, 130, 246, 0.35);
        }}
        
        /* ===== STATUS INDICATOR ===== */
        .status-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 10px;
            animation: pulse3D 2s ease-in-out infinite;
        }}
        
        .status-dot-green {{ background: var(--accent-green); box-shadow: 0 0 10px var(--accent-green); }}
        .status-dot-yellow {{ background: var(--accent-orange); box-shadow: 0 0 10px var(--accent-orange); }}
        .status-dot-red {{ background: var(--accent-red); box-shadow: 0 0 10px var(--accent-red); }}
        
        /* ===== DIVIDER ===== */
        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--border-default) 20%, var(--border-default) 80%, transparent);
            margin: 35px 0;
        }}
        
        /* ===== FOOTER ===== */
        .footer {{
            background: {colors['gradient_card']};
            backdrop-filter: blur(20px);
            padding: 40px;
            text-align: center;
            border-top: 1px solid var(--border-default);
            margin-top: 60px;
            border-radius: var(--radius-2xl) var(--radius-2xl) 0 0;
            position: relative;
        }}
        
        .footer::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple), var(--accent-pink));
        }}
        
        .footer-title {{ color: var(--text-primary); font-size: 1.25rem; font-weight: 700; margin-bottom: 12px; }}
        .footer-subtitle {{ color: var(--text-muted); font-size: 0.95rem; margin-bottom: 12px; }}
        .footer-names {{
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 1.1rem;
        }}
        
        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg-secondary); border-radius: 5px; }}
        ::-webkit-scrollbar-thumb {{ background: linear-gradient(180deg, var(--accent-cyan), var(--accent-purple)); border-radius: 5px; }}
        
        /* ===== INPUTS ===== */
        .stSelectbox > div > div, .stMultiSelect > div > div, .stTextInput > div > div, .stNumberInput > div > div {{
            background: var(--bg-card);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-md);
            color: var(--text-primary);
        }}
        
        .stSlider > div > div > div {{ background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue)) !important; }}
        
        /* ===== FILE UPLOADER ===== */
        .stFileUploader > div {{
            background: var(--bg-card);
            border: 2px dashed var(--border-default);
            border-radius: var(--radius-lg);
        }}
        
        .stFileUploader > div:hover {{ border-color: var(--accent-cyan); }}
        
    </style>
    """

# Apply theme CSS
st.markdown(get_theme_css(), unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS FOR UI
# ============================================================================

def create_metric_card(label, value, delta=None, delta_type="positive", color="cyan"):
    """Create a 3D styled metric card."""
    delta_html = ""
    if delta:
        delta_class = "metric-delta metric-delta-positive" if delta_type == "positive" else "metric-delta metric-delta-negative"
        delta_icon = "↑" if delta_type == "positive" else "↓"
        delta_html = f'<div class="{delta_class}">{delta_icon} {delta}</div>'
    else:
        delta_html = '<div style="height: 28px;"></div>'
    
    return f"""
    <div class="metric-card-3d">
        <div class="metric-label">{label}</div>
        <div class="metric-value metric-value-{color}">{value}</div>
        {delta_html}
    </div>
    """

def format_currency(value):
    """Format large currency values for display."""
    if value is None:
        return "AED 0"
    
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 1_000_000_000:
        return f"{sign}AED {abs_value / 1_000_000_000:.1f}B"
    elif abs_value >= 1_000_000:
        return f"{sign}AED {abs_value / 1_000_000:.1f}M"
    elif abs_value >= 1_000:
        return f"{sign}AED {abs_value / 1_000:.1f}K"
    else:
        return f"{sign}AED {abs_value:,.0f}"

def create_feature_card(icon, title, description, color="cyan"):
    """Create a 3D feature card."""
    color_map = {
        "cyan": "var(--accent-cyan)",
        "blue": "var(--accent-blue)",
        "purple": "var(--accent-purple)",
        "pink": "var(--accent-pink)",
        "green": "var(--accent-green)",
        "orange": "var(--accent-orange)",
        "teal": "var(--accent-teal)",
    }
    accent = color_map.get(color, color_map["cyan"])
    
    return f"""
    <div class="feature-card-3d">
        <div class="feature-icon">{icon}</div>
        <div class="feature-title" style="color: {accent};">{title}</div>
        <div class="feature-desc">{description}</div>
    </div>
    """

def create_info_card(content):
    return f'<div class="info-card">{content}</div>'

def create_success_card(content):
    return f'<div class="success-card">✅ {content}</div>'

def create_warning_card(content):
    return f'<div class="warning-card">⚠️ {content}</div>'

def create_error_card(content):
    return f'<div class="error-card">❌ {content}</div>'

def create_insight_card(title, insight_text):
    return f"""
    <div class="insight-card">
        <div class="insight-title">💡 {title}</div>
        <div class="insight-text">{insight_text}</div>
    </div>
    """

def style_plotly_chart_themed(fig, height=None):
    """Apply theme-aware styling to Plotly charts with visible axis text."""
    colors = get_theme_colors()
    
    fig.update_layout(
        paper_bgcolor=colors['chart_bg'],
        plot_bgcolor=colors['chart_bg'],
        font=dict(
            color=colors['chart_text'],
            family='Inter, sans-serif',
            size=12
        ),
        title_font=dict(
            size=18,
            color=colors['chart_title'],
            family='Inter, sans-serif'
        ),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(color=colors['chart_text'], size=11),
            bordercolor='rgba(0,0,0,0)'
        ),
        margin=dict(l=20, r=20, t=60, b=40),
        hoverlabel=dict(
            bgcolor=colors['bg_card'],
            font_size=12,
            font_family='Inter'
        )
    )
    
    # Update axes with visible text colors
    fig.update_xaxes(
        gridcolor=colors['chart_grid'],
        zerolinecolor=colors['chart_grid'],
        tickfont=dict(color=colors['chart_text'], size=11),
        title_font=dict(color=colors['chart_text'], size=12),
        linecolor=colors['chart_grid']
    )
    
    fig.update_yaxes(
        gridcolor=colors['chart_grid'],
        zerolinecolor=colors['chart_grid'],
        tickfont=dict(color=colors['chart_text'], size=11),
        title_font=dict(color=colors['chart_text'], size=12),
        linecolor=colors['chart_grid']
    )
    
    if height:
        fig.update_layout(height=height)
    
    return fig

def show_footer():
    """Display the footer."""
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
    
    if kpis.get('total_revenue', 0) > 0:
        aov = kpis.get('avg_order_value', 0)
        if aov > 500:
            insights.append(("High-Value Customers", f"Average order value is AED {aov:,.0f}, indicating premium customer segment. Consider upselling strategies."))
        elif aov < 200:
            insights.append(("Growth Opportunity", f"Average order value is AED {aov:,.0f}. Bundle offers could increase basket size by 15-25%."))
    
    margin = kpis.get('profit_margin_pct', 0)
    if margin > 25:
        insights.append(("Strong Margins", f"Profit margin at {margin:.1f}% is healthy. Room for strategic discounts without hurting profitability."))
    elif margin < 15:
        insights.append(("Margin Alert", f"Profit margin at {margin:.1f}% is below industry benchmark. Review pricing strategy and costs."))
    
    return_rate = kpis.get('return_rate_pct', 0)
    if return_rate > 10:
        insights.append(("High Returns", f"Return rate of {return_rate:.1f}% is above normal. Investigate product quality or description accuracy."))
    elif return_rate < 3:
        insights.append(("Excellent Quality", f"Low return rate of {return_rate:.1f}% indicates high customer satisfaction."))
    
    if city_kpis is not None and len(city_kpis) > 0:
        top_city = city_kpis.iloc[0]['city'] if 'city' in city_kpis.columns else None
        if top_city:
            top_revenue = city_kpis.iloc[0]['revenue']
            total_revenue = city_kpis['revenue'].sum()
            pct = (top_revenue / total_revenue * 100) if total_revenue > 0 else 0
            insights.append(("Market Concentration", f"{top_city} contributes {pct:.0f}% of total revenue. {'Diversify to reduce risk.' if pct > 50 else 'Healthy market distribution.'}"))
    
    return insights[:4]

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
    # Theme Toggle
    st.markdown("<div style='padding: 10px 0 20px 0;'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        theme_icon = "🌙" if st.session_state.theme == 'dark' else "☀️"
        theme_label = "Dark Mode" if st.session_state.theme == 'dark' else "Light Mode"
        if st.button(f"{theme_icon} {theme_label}", key="theme_toggle_btn", use_container_width=True):
            toggle_theme()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Logo
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0 30px 0;">
        <div style="font-size: 56px; margin-bottom: 10px;">🛒</div>
        <div style="
            font-size: 28px;
            font-weight: 900;
            -webkit-background-clip: text;
            -webkit-text-fill-color: #8b5cf6;
        ">UAE Pulse</div>
        <div style="background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));"; font-size: 13px; margin-top: 5px;">SIMULATOR + DATA RESCUE</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown('<p style="color: var(--accent-pink); font-weight: 700; letter-spacing: 2px; font-size: 0.75rem;">📍 NAVIGATION</p>', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📂 Data", "🧹 Cleaner", "📊 Dashboard", "🎯 Simulator"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Status
    st.markdown('<p style="color: var(--accent-blue); font-weight: 700; letter-spacing: 2px; font-size: 0.75rem;">📡 STATUS</p>', unsafe_allow_html=True)
    
    data_loaded = st.session_state.data_loaded
    data_cleaned = st.session_state.is_cleaned
    
    status_class_loaded = "status-dot-green" if data_loaded else "status-dot-red"
    status_class_cleaned = "status-dot-green" if data_cleaned else ("status-dot-yellow" if data_loaded else "status-dot-red")
    
    st.markdown(f"""
    <div style="background: var(--bg-card); border-radius: var(--radius-lg); padding: 20px; border: 1px solid var(--border-default);">
        <div style="display: flex; align-items: center; margin: 8px 0;">
            <span class="status-dot {status_class_loaded}"></span>
            <span style="color: var(--text-secondary); font-size: 0.9rem;">Data Loaded</span>
        </div>
        <div style="display: flex; align-items: center; margin: 8px 0;">
            <span class="status-dot {status_class_cleaned}"></span>
            <span style="color: var(--text-secondary); font-size: 0.9rem;">Data Cleaned</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats
    if st.session_state.data_loaded:
        st.markdown("---")
        st.markdown('<p style="color: var(--accent-purple); font-weight: 700; letter-spacing: 2px; font-size: 0.75rem;">📈 QUICK STATS</p>', unsafe_allow_html=True)
        
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
            <div style="background: var(--bg-card); border-radius: var(--radius-lg); padding: 20px; border: 1px solid var(--border-default);">
                <div style="margin-bottom: 16px;">
                    <span style="color: var(--text-muted); font-size: 0.7rem; text-transform: uppercase;">Records</span><br>
                    <span style="color: var(--accent-cyan); font-weight: 800; font-size: 1.6rem;">{total_records:,}</span>
                </div>
                <div>
                    <span style="color: var(--text-muted); font-size: 0.7rem; text-transform: uppercase;">Revenue</span><br>
                    <span style="color: var(--accent-green); font-weight: 800; font-size: 1.4rem;">{format_currency(total_revenue)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Download
    if st.session_state.data_loaded and st.session_state.is_cleaned:
        st.markdown("---")
        st.markdown('<p style="color: var(--accent-green); font-weight: 700; letter-spacing: 2px; font-size: 0.75rem;">📥 EXPORT</p>', unsafe_allow_html=True)
        
        import io, zipfile
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
        
        st.download_button("📦 Download All (ZIP)", data=zip_buffer, file_name="cleaned_data.zip", mime="application/zip", use_container_width=True)

# ============================================================================
# PAGE: HOME
# ============================================================================

def show_home_page():
    st.markdown("""
    <div class="hero-container">
        <div style="margin-bottom: 24px;">
            <span class="hero-badge">✨ UAE E-Commerce Analytics</span>
            <span class="hero-badge" style="background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));">🚀 v3.1</span>
        </div>
        <div class="hero-title">UAE Pulse Simulator</div>
        <p class="hero-subtitle">
            Transform your e-commerce data into actionable insights.<br>
            Clean dirty data, simulate promotional campaigns, and visualize performance metrics.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="section-title section-title-purple">✨ Powerful Features</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_feature_card("📂", "Data Upload", "Upload and preview your e-commerce CSV files", "cyan"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_feature_card("🧹", "Data Rescue", "Detect & auto-fix 15+ data quality issues", "blue"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_feature_card("🎯", "Simulator", "Run what-if scenarios and forecast ROI", "purple"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_feature_card("📊", "Analytics", "Interactive dashboards with KPI tracking", "pink"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.data_loaded:
        st.markdown(create_success_card("Data is loaded! Go to 📊 Dashboard to see your KPIs."), unsafe_allow_html=True)
    else:
        st.markdown(create_info_card("💡 <strong>Start by loading data.</strong> Go to 📂 Data page."), unsafe_allow_html=True)
    
    show_footer()

# ============================================================================
# PAGE: DASHBOARD - COMPLETE WITH ALL CHARTS & INSIGHTS
# ============================================================================

def show_dashboard_page():
    st.markdown('<h1 class="page-title page-title-cyan">📊 Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Business performance insights and operational metrics</p>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card("Please load data first. Go to 📂 Data page."), unsafe_allow_html=True)
        show_footer()
        return
    
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    inventory_df = st.session_state.clean_inventory if st.session_state.is_cleaned else st.session_state.raw_inventory
    
    if sales_df is None:
        st.markdown(create_warning_card("No sales data available."), unsafe_allow_html=True)
        show_footer()
        return
    
    st.markdown("---")
    
    # ===== GLOBAL FILTERS =====
    st.markdown('<p class="section-title section-title-blue">🎛️ Global Filters</p>', unsafe_allow_html=True)
    st.caption("💡 Leave empty to include all")
    
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        date_range = None
        if 'order_time' in sales_df.columns:
            try:
                sales_df['order_time'] = pd.to_datetime(sales_df['order_time'], errors='coerce')
                valid_dates = sales_df['order_time'].dropna()
                if len(valid_dates) > 0:
                    min_date = valid_dates.min().date()
                    max_date = valid_dates.max().date()
                    date_range = st.date_input("📅 Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date, key="global_date_filter")
            except:
                st.caption("Date filter unavailable")
    
    with filter_col2:
        all_cities = []
        selected_cities = []
        if stores_df is not None and 'city' in stores_df.columns:
            all_cities = sorted(stores_df['city'].dropna().unique().tolist())
            selected_cities = st.multiselect("🏙️ City", options=all_cities, default=[], placeholder="All Cities", key="global_city_filter")
            if len(selected_cities) == 0:
                selected_cities = all_cities
    
    with filter_col3:
        all_channels = []
        selected_channels = []
        if stores_df is not None and 'channel' in stores_df.columns:
            all_channels = sorted(stores_df['channel'].dropna().unique().tolist())
            selected_channels = st.multiselect("📱 Channel", options=all_channels, default=[], placeholder="All Channels", key="global_channel_filter")
            if len(selected_channels) == 0:
                selected_channels = all_channels
    
    with filter_col4:
        all_categories = []
        selected_categories = []
        if products_df is not None and 'category' in products_df.columns:
            all_categories = sorted(products_df['category'].dropna().unique().tolist())
            selected_categories = st.multiselect("📦 Category", options=all_categories, default=[], placeholder="All Categories", key="global_category_filter")
            if len(selected_categories) == 0:
                selected_categories = all_categories
    
    # Apply filters
    filtered_sales = sales_df.copy()
    filtered_stores = stores_df.copy() if stores_df is not None else None
    filtered_products = products_df.copy() if products_df is not None else None
    filtered_inventory = inventory_df.copy() if inventory_df is not None else None
    
    if date_range and len(date_range) == 2 and 'order_time' in filtered_sales.columns:
        start_date, end_date = date_range
        filtered_sales = filtered_sales[(filtered_sales['order_time'].dt.date >= start_date) & (filtered_sales['order_time'].dt.date <= end_date)]
    
    if filtered_stores is not None:
        if selected_cities:
            filtered_stores = filtered_stores[filtered_stores['city'].isin(selected_cities)]
        if selected_channels:
            filtered_stores = filtered_stores[filtered_stores['channel'].isin(selected_channels)]
        if 'store_id' in filtered_sales.columns and 'store_id' in filtered_stores.columns:
            valid_store_ids = filtered_stores['store_id'].unique()
            filtered_sales = filtered_sales[filtered_sales['store_id'].isin(valid_store_ids)]
    
    if filtered_products is not None and selected_categories:
        filtered_products = filtered_products[filtered_products['category'].isin(selected_categories)]
        if 'sku' in filtered_sales.columns and 'sku' in filtered_products.columns:
            valid_skus = filtered_products['sku'].unique()
            filtered_sales = filtered_sales[filtered_sales['sku'].isin(valid_skus)]
    
    if filtered_inventory is not None:
        if filtered_stores is not None and 'store_id' in filtered_inventory.columns:
            valid_store_ids = filtered_stores['store_id'].unique()
            filtered_inventory = filtered_inventory[filtered_inventory['store_id'].isin(valid_store_ids)]
        if filtered_products is not None and 'sku' in filtered_inventory.columns:
            valid_skus = filtered_products['sku'].unique()
            filtered_inventory = filtered_inventory[filtered_inventory['sku'].isin(valid_skus)]
    
    original_count = len(sales_df)
    filtered_count = len(filtered_sales)
    filter_pct = (filtered_count / original_count * 100) if original_count > 0 else 0
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(59, 130, 246, 0.1)); padding: 12px 24px; border-radius: var(--radius-md); margin: 15px 0; border: 1px solid var(--border-default);">
        <span style="color: var(--accent-cyan); font-weight: 700;">📊 Showing {filtered_count:,} of {original_count:,} records ({filter_pct:.1f}%)</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs
    tab_exec, tab_mgr = st.tabs(["👔 Executive View — Financial & Strategic", "📋 Manager View — Operational Risk & Execution"])
    
    sim = Simulator()
    kpis = sim.calculate_overall_kpis(filtered_sales, filtered_products)
    city_kpis = sim.calculate_kpis_by_dimension(filtered_sales, filtered_stores, filtered_products, 'city')
    channel_kpis = sim.calculate_kpis_by_dimension(filtered_sales, filtered_stores, filtered_products, 'channel')
    category_kpis = sim.calculate_kpis_by_dimension(filtered_sales, filtered_stores, filtered_products, 'category')
    
    with tab_exec:
        show_executive_view(kpis, city_kpis, channel_kpis, category_kpis, filtered_sales, filtered_products, filtered_stores)
    
    with tab_mgr:
        show_manager_view(kpis, city_kpis, channel_kpis, category_kpis, filtered_sales, filtered_products, filtered_stores, filtered_inventory)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.is_cleaned:
            st.markdown(create_success_card("Viewing cleaned data."), unsafe_allow_html=True)
        else:
            st.markdown(create_warning_card("Viewing raw data. Go to 🧹 Cleaner for validation."), unsafe_allow_html=True)
    
    with col2:
        source = "Cleaned Data ✨" if st.session_state.is_cleaned else "Raw Data 📥"
        st.markdown(create_info_card(f"<strong>Data Source:</strong> {source}"), unsafe_allow_html=True)
    
    show_footer()


def show_executive_view(kpis, city_kpis, channel_kpis, category_kpis, sales_df, products_df, stores_df):
    """Display Executive View - Financial & Strategic KPIs with ALL charts."""
    
    # ===== KPI CARDS =====
    st.markdown('<p class="section-title section-title-cyan">💰 Financial KPIs</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    gross_revenue = kpis.get('total_revenue', 0)
    refund_amount = kpis.get('refund_amount', 0)
    net_revenue = kpis.get('net_revenue', gross_revenue - refund_amount)
    cogs = kpis.get('total_cogs', 0)
    
    with col1:
        st.markdown(create_metric_card("Gross Revenue", format_currency(gross_revenue), color="cyan"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Refund Amount", format_currency(refund_amount), color="pink"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Net Revenue", format_currency(net_revenue), color="green"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("COGS", format_currency(cogs), color="orange"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    gross_margin = kpis.get('total_profit', 0)
    gross_margin_pct = kpis.get('profit_margin_pct', 0)
    avg_discount = kpis.get('avg_discount_pct', 0)
    avg_order_value = kpis.get('avg_order_value', 0)
    
    with col1:
        st.markdown(create_metric_card("Gross Margin (AED)", format_currency(gross_margin), color="teal"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Gross Margin %", f"{gross_margin_pct:.1f}%", color="purple"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Avg Discount %", f"{avg_discount:.1f}%", color="blue"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("Avg Order Value", format_currency(avg_order_value), color="cyan"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== CHART 1: WATERFALL - Profit Bridge =====
    st.markdown('<p class="section-title section-title-blue">📊 Profit Bridge Analysis</p>', unsafe_allow_html=True)
    
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
        text=[format_currency(gross_rev), format_currency(-refunds), format_currency(-discounts), format_currency(-cogs_val), format_currency(net_profit)],
        textposition="outside"
    ))
    
    fig_waterfall = style_plotly_chart_themed(fig_waterfall, height=400)
    fig_waterfall.update_layout(showlegend=False, title="")
    st.plotly_chart(fig_waterfall, use_container_width=True)
    st.caption("📌 How Net Profit is built: Gross Revenue minus Refunds, Discounts, and COGS.")
    
    st.markdown("---")
    
    # ===== CHART 2 & 3: Revenue Trend + Margin by Category =====
    st.markdown('<p class="section-title section-title-green">📈 Revenue & Margin Analysis</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CHART 2: Area Chart - Revenue Trend
        if sales_df is not None and 'order_time' in sales_df.columns:
            time_group = st.selectbox("Group by", ["Monthly", "Weekly", "Daily"], index=0, key="revenue_trend_time_group")
            
            sales_trend = sales_df.copy()
            sales_trend['order_time'] = pd.to_datetime(sales_trend['order_time'], errors='coerce')
            sales_trend = sales_trend.dropna(subset=['order_time'])
            
            if len(sales_trend) > 0:
                if time_group == "Daily":
                    sales_trend['time_period'] = sales_trend['order_time'].dt.strftime('%d %b %Y')
                    sales_trend['time_sort'] = sales_trend['order_time'].dt.date
                elif time_group == "Weekly":
                    sales_trend['time_period'] = sales_trend['order_time'].dt.to_period('W').apply(lambda x: x.start_time.strftime('%d %b %Y'))
                    sales_trend['time_sort'] = sales_trend['order_time'].dt.to_period('W').apply(lambda x: x.start_time)
                else:
                    sales_trend['time_period'] = sales_trend['order_time'].dt.strftime('%b %Y')
                    sales_trend['time_sort'] = sales_trend['order_time'].dt.to_period('M')
                
                if 'qty' in sales_trend.columns and 'selling_price_aed' in sales_trend.columns:
                    sales_trend['revenue'] = sales_trend['qty'] * sales_trend['selling_price_aed']
                elif 'selling_price_aed' in sales_trend.columns:
                    sales_trend['revenue'] = sales_trend['selling_price_aed']
                else:
                    sales_trend['revenue'] = 0
                
                if 'payment_status' in sales_trend.columns:
                    sales_trend = sales_trend[sales_trend['payment_status'] == 'Paid']
                
                trend_revenue = sales_trend.groupby(['time_sort', 'time_period']).agg({'revenue': 'sum'}).reset_index()
                trend_revenue = trend_revenue.sort_values('time_sort')
                
                fig_area = go.Figure()
                fig_area.add_trace(go.Scatter(
                    x=trend_revenue['time_period'],
                    y=trend_revenue['revenue'],
                    fill='tozeroy',
                    mode='lines+markers',
                    line=dict(color='#06b6d4', width=3),
                    fillcolor='rgba(6, 182, 212, 0.2)',
                    marker=dict(size=8),
                    name='Revenue'
                ))
                
                fig_area = style_plotly_chart_themed(fig_area, height=380)
                fig_area.update_layout(title=f"{time_group} Revenue Trend", xaxis_title=time_group, yaxis_title="Revenue (AED)", xaxis=dict(type='category'))
                st.plotly_chart(fig_area, use_container_width=True)
            else:
                st.info("No valid dates in data range")
        else:
            st.info("Revenue trend requires order_time column")
    
    with col2:
        # CHART 3: Bar Chart - Margin % by Category
        if category_kpis is not None and len(category_kpis) > 0:
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                top_n_margin = st.selectbox("Show Top", [5, 8, 10, "All"], index=1, key="margin_top_n")
            with filter_col2:
                sort_margin = st.selectbox("Sort by", ["Margin %", "Revenue"], index=0, key="margin_sort")
            
            cat_data = category_kpis.copy()
            if 'margin_pct' not in cat_data.columns:
                if 'profit' in cat_data.columns and 'revenue' in cat_data.columns:
                    cat_data['margin_pct'] = (cat_data['profit'] / cat_data['revenue'] * 100).fillna(0)
                else:
                    cat_data['margin_pct'] = 0
            
            if top_n_margin != "All":
                cat_data = cat_data.nlargest(int(top_n_margin), 'revenue')
            
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
            
            fig_margin = style_plotly_chart_themed(fig_margin, height=380)
            fig_margin.update_layout(title="Gross Margin % by Category", xaxis_title="Margin %", yaxis_title="")
            st.plotly_chart(fig_margin, use_container_width=True)
            st.caption("📌 Red < 20%, Yellow < 30%, Green ≥ 30%.")
        else:
            st.info("Category data not available")
    
    st.markdown("---")
    
    # ===== CHART 4 & 5: Sunburst + Discount Impact =====
    st.markdown('<p class="section-title section-title-purple">🎯 Revenue Mix & Discount Impact</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CHART 4: Sunburst - Revenue Mix
        if sales_df is not None and stores_df is not None and products_df is not None:
            try:
                sunburst_df = sales_df.copy()
                
                if 'store_id' in sunburst_df.columns and 'store_id' in stores_df.columns:
                    sunburst_df = sunburst_df.merge(stores_df[['store_id', 'city', 'channel']], on='store_id', how='left')
                
                if 'sku' in sunburst_df.columns and 'sku' in products_df.columns:
                    sunburst_df = sunburst_df.merge(products_df[['sku', 'category']], on='sku', how='left')
                elif 'product_id' in sunburst_df.columns and 'product_id' in products_df.columns:
                    sunburst_df = sunburst_df.merge(products_df[['product_id', 'category']], on='product_id', how='left')
                
                if all(col in sunburst_df.columns for col in ['city', 'channel', 'category', 'selling_price_aed']):
                    if 'qty' in sunburst_df.columns:
                        sunburst_df['revenue'] = sunburst_df['qty'] * sunburst_df['selling_price_aed']
                    else:
                        sunburst_df['revenue'] = sunburst_df['selling_price_aed']
                    
                    if 'payment_status' in sunburst_df.columns:
                        sunburst_df = sunburst_df[sunburst_df['payment_status'] == 'Paid']
                    
                    sunburst_agg = sunburst_df.groupby(['city', 'channel', 'category']).agg({'revenue': 'sum'}).reset_index()
                    sunburst_agg.columns = ['City', 'Channel', 'Category', 'Revenue']
                    sunburst_agg = sunburst_agg.nlargest(30, 'Revenue')
                    
                    fig_sunburst = px.sunburst(
                        sunburst_agg,
                        path=['City', 'Channel', 'Category'],
                        values='Revenue',
                        color='Revenue',
                        color_continuous_scale=['#00E5FF', '#4FB6E2', '#6A5ACD']
                    )
                    
                    fig_sunburst = style_plotly_chart_themed(fig_sunburst, height=400)
                    fig_sunburst.update_layout(title="Revenue Mix: City → Channel → Category")
                    st.plotly_chart(fig_sunburst, use_container_width=True)
                    st.caption("📌 Click to drill down: City → Channel → Category revenue contribution.")
                else:
                    # Fallback: Pie chart by channel
                    if 'channel' in sunburst_df.columns and 'selling_price_aed' in sunburst_df.columns:
                        if 'qty' in sunburst_df.columns:
                            sunburst_df['revenue'] = sunburst_df['qty'] * sunburst_df['selling_price_aed']
                        else:
                            sunburst_df['revenue'] = sunburst_df['selling_price_aed']
                        
                        channel_rev = sunburst_df.groupby('channel')['revenue'].sum().reset_index()
                        fig_fallback = px.pie(channel_rev, values='revenue', names='channel', title='Revenue by Channel', color_discrete_sequence=['#f65c5c', '#f68a5c', '#f6b85c'], hole=0.4)
                        fig_fallback = style_plotly_chart_themed(fig_fallback, height=400)
                        st.plotly_chart(fig_fallback, use_container_width=True)
                    else:
                        st.info("Revenue mix data not available")
            except Exception as e:
                st.info(f"Unable to create revenue mix chart")
        else:
            st.info("Sales, stores, or products data not available")
    
    with col2:
        # CHART 5: Combo Chart - Discount Impact
        st.markdown("**Discount Impact Analysis**")
        
        margin_floor = st.slider("Margin Floor %", min_value=10, max_value=40, value=20, step=5, key="discount_margin_floor")
        
        base_revenue = kpis.get('total_revenue', 0)
        base_cogs = kpis.get('total_cogs', 0)
        
        discount_levels = [0, 5, 10, 15, 20, 25, 30]
        profits = []
        margins = []
        
        for disc in discount_levels:
            volume_uplift = 1 + (disc * 0.02)
            simulated_revenue = base_revenue * volume_uplift * (1 - disc/100)
            simulated_cogs = base_cogs * volume_uplift
            profit = simulated_revenue - simulated_cogs
            margin = (profit / simulated_revenue * 100) if simulated_revenue > 0 else 0
            profits.append(profit)
            margins.append(margin)
        
        fig_combo = go.Figure()
        
        bar_colors = ['#10b981' if m >= margin_floor else '#ef4444' for m in margins]
        fig_combo.add_trace(go.Bar(
            x=discount_levels,
            y=profits,
            name='Profit',
            marker_color=bar_colors,
            text=[format_currency(p) for p in profits],
            textposition='outside'
        ))
        
        fig_combo.add_hline(y=base_revenue * margin_floor / 100, line_dash="dash", line_color="#f59e0b", annotation_text=f"Margin Floor ({margin_floor}%)", annotation_position="top right")
        
        fig_combo = style_plotly_chart_themed(fig_combo, height=380)
        fig_combo.update_layout(title="Profit at Different Discount Levels", xaxis_title="Discount %", yaxis_title="Profit (AED)", showlegend=False)
        st.plotly_chart(fig_combo, use_container_width=True)
        st.caption("📌 Green = above margin floor, Red = below margin floor.")
    
    st.markdown("---")
    
    # ===== EXECUTIVE RECOMMENDATIONS =====
    st.markdown('<p class="section-title section-title-purple">💡 Executive Recommendations</p>', unsafe_allow_html=True)
    
    recommendations = []
    
    if gross_margin_pct >= 30:
        recommendations.append(f"✅ **Healthy Margin**: Gross margin at {gross_margin_pct:.1f}% is strong. Room for promotional activity.")
    elif gross_margin_pct >= 20:
        recommendations.append(f"⚠️ **Moderate Margin**: Gross margin at {gross_margin_pct:.1f}%. Monitor discount levels carefully.")
    else:
        recommendations.append(f"🔴 **Low Margin Alert**: Gross margin at {gross_margin_pct:.1f}% is below healthy threshold. Reduce discounts or optimize COGS.")
    
    if avg_discount > 15:
        recommendations.append(f"⚠️ **High Discounting**: Average discount at {avg_discount:.1f}%. Consider reducing to protect margins.")
    elif avg_discount < 5:
        recommendations.append(f"💡 **Low Discount Opportunity**: Average discount at {avg_discount:.1f}%. Consider targeted promotions to drive volume.")
    
    if city_kpis is not None and len(city_kpis) > 0:
        top_city = city_kpis.nlargest(1, 'revenue')['city'].values[0]
        recommendations.append(f"🏆 **Top Market**: {top_city} leads in revenue. Consider increasing inventory allocation.")
    
    if channel_kpis is not None and len(channel_kpis) > 0:
        top_channel = channel_kpis.nlargest(1, 'revenue')['channel'].values[0]
        recommendations.append(f"📱 **Best Channel**: {top_channel} generates highest revenue. Prioritize marketing spend here.")
    
    for rec in recommendations:
        st.markdown(f'<div class="recommendation-card"><p>{rec}</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== BUSINESS INSIGHTS =====
    st.markdown('<p class="section-title section-title-teal">🔍 Business Insights</p>', unsafe_allow_html=True)
    
    insights = generate_insights(kpis, city_kpis, channel_kpis, category_kpis)
    for title, text in insights:
        st.markdown(create_insight_card(title, text), unsafe_allow_html=True)


def show_manager_view(kpis, city_kpis, channel_kpis, category_kpis, sales_df, products_df, stores_df, inventory_df):
    """Display Manager View - Operational Risk & Execution with ALL charts."""
    
    # ===== OPERATIONAL KPIs =====
    st.markdown('<p class="section-title section-title-blue">⚙️ Operational KPIs</p>', unsafe_allow_html=True)
    
    return_rate = kpis.get('return_rate_pct', 0)
    
    if sales_df is not None and 'payment_status' in sales_df.columns:
        total_orders = len(sales_df)
        failed_orders = (sales_df['payment_status'] == 'Failed').sum()
        payment_failure_rate = (failed_orders / total_orders * 100) if total_orders > 0 else 0
    else:
        payment_failure_rate = 0
    
    stockout_risk = 0
    high_risk_skus = 0
    if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
        total_inventory = len(inventory_df)
        if 'reorder_point' in inventory_df.columns:
            inventory_df['_stock'] = pd.to_numeric(inventory_df['stock_on_hand'], errors='coerce').fillna(0)
            inventory_df['_reorder'] = pd.to_numeric(inventory_df['reorder_point'], errors='coerce').fillna(10)
            low_stock = (inventory_df['_stock'] <= inventory_df['_reorder']).sum()
        else:
            avg_stock = inventory_df['stock_on_hand'].mean()
            threshold = max(10, avg_stock * 0.1)
            low_stock = (inventory_df['stock_on_hand'] < threshold).sum()
        stockout_risk = (low_stock / total_inventory * 100) if total_inventory > 0 else 0
        high_risk_skus = int(low_stock)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_card("Stockout Risk %", f"{stockout_risk:.1f}%", color="pink"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Return Rate %", f"{return_rate:.1f}%", color="orange"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Payment Failure %", f"{payment_failure_rate:.1f}%", color="purple"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("High-Risk SKUs", f"{high_risk_skus:,}", color="blue"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== CHART 1 & 2: Gauge + Risk by City-Channel =====
    st.markdown('<p class="section-title section-title-teal">📊 Risk Overview</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # CHART 1: Gauge - Stockout Risk
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=stockout_risk,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Stockout Risk %", 'font': {'size': 16, 'color': get_theme_colors()['chart_text']}},
            number={'suffix': "%", 'font': {'size': 32, 'color': get_theme_colors()['chart_text']}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': get_theme_colors()['chart_text']},
                'bar': {'color': '#06b6d4'},
                'steps': [
                    {'range': [0, 30], 'color': 'rgba(16, 185, 129, 0.3)'},
                    {'range': [30, 60], 'color': 'rgba(245, 158, 11, 0.3)'},
                    {'range': [60, 100], 'color': 'rgba(239, 68, 68, 0.3)'}
                ],
                'threshold': {'line': {'color': '#ef4444', 'width': 4}, 'thickness': 0.75, 'value': 60}
            }
        ))
        fig_gauge = style_plotly_chart_themed(fig_gauge, height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.caption("📌 Green = Safe (0-30%), Yellow = Caution (30-60%), Red = Critical (60%+)")
    
    with col2:
        # CHART 2: Horizontal Bar - Risk by City-Channel
        if inventory_df is not None and stores_df is not None and 'store_id' in inventory_df.columns:
            inv_with_store = inventory_df.merge(stores_df[['store_id', 'city', 'channel']], on='store_id', how='left')
            
            if all(col in inv_with_store.columns for col in ['city', 'channel', 'stock_on_hand']):
                top_n_risk = st.selectbox("Show Top", [5, 10, "All"], index=0, key="city_channel_risk_top_n")
                
                inv_with_store['city_channel'] = inv_with_store['city'] + ' - ' + inv_with_store['channel']
                city_channel_risk = inv_with_store.groupby('city_channel').apply(lambda x: (x['stock_on_hand'] < 10).sum() / len(x) * 100 if len(x) > 0 else 0, include_groups=False).reset_index()
                city_channel_risk.columns = ['City-Channel', 'Risk %']
                city_channel_risk = city_channel_risk.sort_values('Risk %', ascending=False)
                
                if top_n_risk != "All":
                    city_channel_risk = city_channel_risk.head(int(top_n_risk))
                
                city_channel_risk = city_channel_risk.sort_values('Risk %', ascending=True)
                colors = ['#10b981' if x < 30 else '#f59e0b' if x < 60 else '#ef4444' for x in city_channel_risk['Risk %']]
                
                fig_risk_bar = go.Figure(go.Bar(
                    x=city_channel_risk['Risk %'],
                    y=city_channel_risk['City-Channel'],
                    orientation='h',
                    marker_color=colors,
                    text=[f"{x:.1f}%" for x in city_channel_risk['Risk %']],
                    textposition='outside'
                ))
                fig_risk_bar = style_plotly_chart_themed(fig_risk_bar, height=300)
                fig_risk_bar.update_layout(title="Stockout Risk by City-Channel", xaxis_title="Risk %", yaxis_title="")
                st.plotly_chart(fig_risk_bar, use_container_width=True)
            else:
                st.info("City-channel risk data not available")
        else:
            st.info("Inventory or store data not available")
    
    st.markdown("---")
    
    # ===== CHART 3 & 4: Demand vs Stock + Top SKU Risk =====
    st.markdown('<p class="section-title section-title-orange">📦 Inventory Analysis</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CHART 3: Bar Chart - Demand vs Stock by Category (FIXED - Dual Y-Axis)
        if sales_df is not None and inventory_df is not None and products_df is not None:
            try:
                sales_with_cat = sales_df.copy()
                sku_col = 'sku' if 'sku' in sales_with_cat.columns else 'product_id'
                
                if sku_col in sales_with_cat.columns and sku_col in products_df.columns:
                    sales_with_cat = sales_with_cat.merge(products_df[[sku_col, 'category']], on=sku_col, how='left')
                
                if 'category' in sales_with_cat.columns and 'qty' in sales_with_cat.columns:
                    # Calculate demand
                    sales_with_cat['qty'] = pd.to_numeric(sales_with_cat['qty'], errors='coerce').fillna(0)
                    demand_by_cat = sales_with_cat.groupby('category')['qty'].sum().reset_index()
                    demand_by_cat.columns = ['Category', 'Demand']
                    
                    # Calculate stock
                    inv_with_cat = inventory_df.copy()
                    if sku_col in inv_with_cat.columns and sku_col in products_df.columns:
                        inv_with_cat = inv_with_cat.merge(products_df[[sku_col, 'category']], on=sku_col, how='left')
                    
                    if 'category' in inv_with_cat.columns and 'stock_on_hand' in inv_with_cat.columns:
                        inv_with_cat['stock_on_hand'] = pd.to_numeric(inv_with_cat['stock_on_hand'], errors='coerce').fillna(0)
                        stock_by_cat = inv_with_cat.groupby('category')['stock_on_hand'].sum().reset_index()
                        stock_by_cat.columns = ['Category', 'Stock']
                        
                        # Merge and get top categories
                        demand_stock = demand_by_cat.merge(stock_by_cat, on='Category', how='outer').fillna(0)
                        demand_stock = demand_stock.nlargest(8, 'Demand')
                        
                        # Calculate stock coverage ratio (days of stock)
                        demand_stock['Coverage'] = np.where(
                            demand_stock['Demand'] > 0,
                            demand_stock['Stock'] / demand_stock['Demand'],
                            0
                        )
                        
                        # Create figure with secondary y-axis
                        fig_demand_stock = make_subplots(specs=[[{"secondary_y": True}]])
                        
                        # Add Demand bars (primary y-axis - LEFT)
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
                        
                        # Add Stock bars (secondary y-axis - RIGHT)
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
                        
                        # Style the chart
                        colors = get_theme_colors()
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
                        
                        # Update y-axes with proper colors
                        fig_demand_stock.update_yaxes(
                            title_text="Demand (Units Sold)",
                            secondary_y=False,
                            gridcolor=colors['chart_grid'],
                            tickfont=dict(color='#8b5cf6'),
                            title_font=dict(color='#8b5cf6')
                        )
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
                        
                        # Show coverage ratio as additional insight
                        low_coverage = demand_stock[demand_stock['Coverage'] < 10]
                        if len(low_coverage) > 0:
                            st.markdown(f"""
                            <div class="warning-card">
                                ⚠️ <strong>{len(low_coverage)} categories</strong> have less than 10x stock coverage: 
                                {', '.join(low_coverage['Category'].tolist())}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.caption("📌 Purple = Demand (left axis), Cyan = Stock (right axis). Scales differ for visibility.")
                    else:
                        st.info("Stock by category not available")
                else:
                    st.info("Category demand data not available")
            except Exception as e:
                st.info(f"Unable to create demand vs stock chart: {str(e)}")
        else:
            st.info("Required data not available")
    
    with col2:
        # CHART 4: Horizontal Bar - Top N SKU-Store Stockout Risk
        if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
            sku_col = 'sku' if 'sku' in inventory_df.columns else 'product_id'
            
            if sku_col in inventory_df.columns:
                top_n_sku = st.selectbox("Show Top", [5, 10, 15, 20], index=1, key="sku_stockout_top_n")
                
                risk_df = inventory_df.nsmallest(int(top_n_sku), 'stock_on_hand').copy()
                
                if stores_df is not None and 'store_id' in risk_df.columns and 'store_id' in stores_df.columns:
                    risk_df = risk_df.merge(stores_df[['store_id', 'city']], on='store_id', how='left')
                    risk_df['SKU-Location'] = risk_df[sku_col].astype(str) + ' @ ' + risk_df['city'].fillna('Unknown')
                else:
                    risk_df['SKU-Location'] = risk_df[sku_col].astype(str)
                
                max_stock = risk_df['stock_on_hand'].max() + 1
                risk_df['risk_score'] = ((max_stock - risk_df['stock_on_hand']) / max_stock * 100).clip(0, 100)
                risk_df = risk_df.sort_values('risk_score', ascending=True)
                
                colors = ['#10b981' if x < 50 else '#f59e0b' if x < 80 else '#ef4444' for x in risk_df['risk_score']]
                
                fig_sku_risk = go.Figure(go.Bar(
                    x=risk_df['risk_score'],
                    y=risk_df['SKU-Location'],
                    orientation='h',
                    marker_color=colors,
                    text=[f"{x:.0f}% risk" for x in risk_df['risk_score']],
                    textposition='outside'
                ))
                fig_sku_risk = style_plotly_chart_themed(fig_sku_risk, height=350)
                fig_sku_risk.update_layout(title=f"Top {top_n_sku} Stockout Risk SKU-Store", xaxis_title="Risk Score %", yaxis_title="")
                st.plotly_chart(fig_sku_risk, use_container_width=True)
                st.caption("📌 Action list for ops team.")
            else:
                st.info("SKU data not available")
        else:
            st.info("Inventory data not available")
    
    st.markdown("---")
    
    # ===== CHART 5: PARETO - Issues Log =====
    st.markdown('<p class="section-title section-title-pink">📋 Data Quality Analysis</p>', unsafe_allow_html=True)
    
    if st.session_state.is_cleaned and hasattr(st.session_state, 'issues_df') and st.session_state.issues_df is not None:
        issues_df = st.session_state.issues_df
        if len(issues_df) > 0 and 'issue_type' in issues_df.columns:
            pareto_df = issues_df.copy()
            pareto_df['Count'] = pareto_df['record_identifier'].str.extract(r'(\d+)').astype(float).fillna(1)
            
            issue_counts = pareto_df.groupby('issue_type')['Count'].sum().reset_index()
            issue_counts.columns = ['Issue Type', 'Count']
            issue_counts = issue_counts.sort_values('Count', ascending=False)
            
            top_n_pareto = st.selectbox("Show Top Issue Types", [5, 10, "All"], index=1, key="pareto_top_n")
            if top_n_pareto != "All":
                issue_counts = issue_counts.head(int(top_n_pareto))
            
            total_issues = issue_counts['Count'].sum()
            issue_counts['Cumulative'] = issue_counts['Count'].cumsum()
            issue_counts['Cumulative %'] = (issue_counts['Cumulative'] / total_issues * 100)
            
            fig_pareto = go.Figure()
            fig_pareto.add_trace(go.Bar(x=issue_counts['Issue Type'], y=issue_counts['Count'], name='Count', marker_color='#8b5cf6', text=issue_counts['Count'].astype(int), textposition='outside'))
            fig_pareto.add_trace(go.Scatter(x=issue_counts['Issue Type'], y=issue_counts['Cumulative %'], name='Cumulative %', mode='lines+markers', line=dict(color='#f59e0b', width=3), marker=dict(size=8), yaxis='y2'))
            fig_pareto.add_hline(y=80, line_dash="dash", line_color="#ef4444", yref='y2', annotation_text="80% threshold")
            
            fig_pareto = style_plotly_chart_themed(fig_pareto, height=400)
            fig_pareto.update_layout(title="Data Quality Issues - Pareto Analysis", xaxis_title="Issue Type", yaxis=dict(title='Count', side='left'), yaxis2=dict(title='Cumulative %', side='right', overlaying='y', range=[0, 105]), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), barmode='group')
            fig_pareto.update_xaxes(tickangle=45)
            
            st.plotly_chart(fig_pareto, use_container_width=True)
            st.caption("📌 Fix issues from left to right until orange line crosses 80%.")
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
            
            if stores_df is not None and 'store_id' in risk_table.columns and 'store_id' in stores_df.columns:
                risk_table = risk_table.merge(stores_df[['store_id', 'city', 'channel']], on='store_id', how='left')
            
            risk_table['Risk Level'] = risk_table['stock_on_hand'].apply(lambda x: '🔴 Critical' if x < 5 else ('🟠 High' if x < 10 else '🟡 Medium'))
            
            display_cols = [col for col in [sku_col, 'store_id', 'city', 'channel', 'stock_on_hand', 'Risk Level'] if col in risk_table.columns]
            st.dataframe(risk_table[display_cols], use_container_width=True, hide_index=True)
            st.caption("📌 Operations action list: SKU-Store pairs with lowest stock.")
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
        st.markdown(create_success_card("All operational metrics within healthy ranges."), unsafe_allow_html=True)
    else:
        for alert in alerts:
            st.markdown(f'<div class="alert-card"><p>{alert}</p></div>', unsafe_allow_html=True)


# ============================================================================
# PAGE: DATA
# ============================================================================

def show_data_page():
    st.markdown('<h1 class="page-title page-title-cyan">📂 Data Management</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Upload, view, and manage your e-commerce data files</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<p class="section-title section-title-blue">📤 Upload Data Files</p>', unsafe_allow_html=True)
    
    with st.expander("ℹ️ Expected File Formats"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""**📦 Products:** `sku`, `category`, `base_price_aed`\n**🛒 Sales:** `order_id`, `sku`, `store_id`, `qty`, `selling_price_aed`""")
        with col2:
            st.markdown("""**🏪 Stores:** `store_id`, `city`, `channel`\n**📋 Inventory:** `sku`, `store_id`, `stock_on_hand`""")
    
    valid_files = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        products_file = st.file_uploader("📦 Products CSV", type=['csv'], key='products_upload')
        if products_file:
            try:
                products_df = pd.read_csv(products_file)
                products_file.seek(0)
                validation = FileValidator.validate_file(products_df, 'products')
                if validation['valid']:
                    st.success(f"✅ Valid ({len(products_df):,} rows)")
                    valid_files['products'] = products_df
                else:
                    st.error(f"❌ {validation['message']}")
            except Exception as e:
                st.error(f"❌ Cannot read file")
        
        sales_file = st.file_uploader("🛒 Sales CSV", type=['csv'], key='sales_upload')
        if sales_file:
            try:
                sales_df = pd.read_csv(sales_file)
                sales_file.seek(0)
                validation = FileValidator.validate_file(sales_df, 'sales')
                if validation['valid']:
                    st.success(f"✅ Valid ({len(sales_df):,} rows)")
                    valid_files['sales'] = sales_df
                else:
                    st.error(f"❌ {validation['message']}")
            except Exception as e:
                st.error(f"❌ Cannot read file")
    
    with col2:
        stores_file = st.file_uploader("🏪 Stores CSV", type=['csv'], key='stores_upload')
        if stores_file:
            try:
                stores_df = pd.read_csv(stores_file)
                stores_file.seek(0)
                validation = FileValidator.validate_file(stores_df, 'stores')
                if validation['valid']:
                    st.success(f"✅ Valid ({len(stores_df):,} rows)")
                    valid_files['stores'] = stores_df
                else:
                    st.error(f"❌ {validation['message']}")
            except Exception as e:
                st.error(f"❌ Cannot read file")
        
        inventory_file = st.file_uploader("📋 Inventory CSV", type=['csv'], key='inventory_upload')
        if inventory_file:
            try:
                inventory_df = pd.read_csv(inventory_file)
                inventory_file.seek(0)
                validation = FileValidator.validate_file(inventory_df, 'inventory')
                if validation['valid']:
                    st.success(f"✅ Valid ({len(inventory_df):,} rows)")
                    valid_files['inventory'] = inventory_df
                else:
                    st.error(f"❌ {validation['message']}")
            except Exception as e:
                st.error(f"❌ Cannot read file")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if len(valid_files) == 4:
            st.success("✅ All 4 files valid!")
        elif len(valid_files) > 0:
            st.warning(f"⚠️ {len(valid_files)}/4 files valid")
        else:
            st.info("📤 Upload all 4 files")
        
        if st.button("📥 Load All Files", use_container_width=True, disabled=len(valid_files) != 4):
            for key, df in valid_files.items():
                setattr(st.session_state, f'raw_{key}', df)
            st.session_state.data_loaded = True
            st.session_state.is_cleaned = False
            st.success("✅ Loaded!")
            st.rerun()
    
    st.markdown("---")
    st.markdown('<p class="section-title section-title-purple">📦 Or Use Sample Data</p>', unsafe_allow_html=True)
    
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
    
    if st.session_state.data_loaded:
        st.markdown("---")
        st.markdown('<p class="section-title section-title-teal">👀 Data Preview</p>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📦 Products", "🏪 Stores", "🛒 Sales", "📋 Inventory"])
        
        for tab, name, key in [(tab1, "Products", "raw_products"), (tab2, "Stores", "raw_stores"), (tab3, "Sales", "raw_sales"), (tab4, "Inventory", "raw_inventory")]:
            with tab:
                df = getattr(st.session_state, key)
                if df is not None:
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
                else:
                    st.info(f"No {name.lower()} data loaded")
    
    show_footer()

# ============================================================================
# PAGE: CLEANER
# ============================================================================

def show_cleaner_page():
    st.markdown('<h1 class="page-title page-title-green">🧹 Data Rescue Center</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Validate, detect issues, and clean your dirty data automatically</p>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card("Please load data first. Go to 📂 Data page."), unsafe_allow_html=True)
        show_footer()
        return
    
    st.markdown("---")
    st.markdown('<p class="section-title section-title-cyan">🔍 Issues We Detect & Fix</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="info-card"><strong style="color: var(--accent-cyan);">Data Quality</strong><ul style="color: var(--text-secondary);"><li>Missing values</li><li>Duplicates</li><li>Whitespace</li></ul></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="info-card" style="border-left-color: var(--accent-purple);"><strong style="color: var(--accent-purple);">Format Issues</strong><ul style="color: var(--text-secondary);"><li>Multi-language</li><li>Case normalization</li><li>Fuzzy matching</li></ul></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="info-card" style="border-left-color: var(--accent-pink);"><strong style="color: var(--accent-pink);">Value Issues</strong><ul style="color: var(--text-secondary);"><li>Negative values</li><li>Outliers (IQR)</li><li>FK violations</li></ul></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run Data Cleaning", use_container_width=True, type="primary"):
            with st.spinner("🔄 Cleaning..."):
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
                    st.success("✅ Done!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    if st.session_state.is_cleaned:
        st.markdown("---")
        st.markdown('<p class="section-title section-title-blue">📊 Results</p>', unsafe_allow_html=True)
        
        stats = st.session_state.cleaner_stats
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card("Missing Fixed", f"{stats.get('missing_values_fixed', 0):,}", color="cyan"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card("Duplicates Removed", f"{stats.get('duplicates_removed', 0):,}", color="blue"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card("Outliers Fixed", f"{stats.get('outliers_fixed', 0):,}", color="purple"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card("Text Standardized", f"{stats.get('text_standardized', 0):,}", color="pink"), unsafe_allow_html=True)
        
        issues_df = st.session_state.issues_df
        if len(issues_df) > 0:
            st.markdown("---")
            st.markdown('<p class="section-title section-title-orange">🔍 Issues Log</p>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                issue_counts = issues_df.groupby('issue_type').size().reset_index(name='count')
                fig = px.bar(issue_counts, x='count', y='issue_type', orientation='h', title='Issues by Type', color='count', color_continuous_scale=['#06b6d4', '#8b5cf6'])
                fig = style_plotly_chart_themed(fig)
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                table_counts = issues_df.groupby('table').size().reset_index(name='count')
                fig = px.pie(table_counts, values='count', names='table', title='Issues by Table', color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899'], hole=0.45)
                fig = style_plotly_chart_themed(fig)
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(issues_df, use_container_width=True)
            
            csv = issues_df.to_csv(index=False)
            st.download_button("📥 Download Issues Log", data=csv, file_name="issues_log.csv", mime="text/csv")
        else:
            st.markdown(create_success_card("No major issues found!"), unsafe_allow_html=True)
    
    show_footer()

# ============================================================================
# PAGE: SIMULATOR
# ============================================================================

def show_simulator_page():
    st.markdown('<h1 class="page-title page-title-purple">🎯 Campaign Simulator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Run what-if scenarios and forecast campaign outcomes</p>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.warning("⚠️ Please load data first.")
        show_footer()
        return
    
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    
    st.markdown("---")
    st.markdown('<p class="section-title section-title-cyan">⚙️ Campaign Parameters</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p style="color: var(--accent-cyan); font-weight: 700;">💰 Pricing</p>', unsafe_allow_html=True)
        discount_pct = st.slider("Discount %", 0, 50, 15)
        promo_budget = st.number_input("Promo Budget (AED)", 1000, 500000, 25000, step=5000)
    
    with col2:
        st.markdown('<p style="color: var(--accent-purple); font-weight: 700;">📊 Constraints</p>', unsafe_allow_html=True)
        margin_floor = st.slider("Margin Floor %", 0, 50, 15)
        campaign_days = st.slider("Campaign Days", 1, 30, 7)
    
    with col3:
        st.markdown('<p style="color: var(--accent-pink); font-weight: 700;">🎯 Targeting</p>', unsafe_allow_html=True)
        
        cities = ['All'] + (sorted(stores_df['city'].dropna().unique().tolist()) if stores_df is not None and 'city' in stores_df.columns else [])
        channels = ['All'] + (sorted(stores_df['channel'].dropna().unique().tolist()) if stores_df is not None and 'channel' in stores_df.columns else [])
        categories = ['All'] + (sorted(products_df['category'].dropna().unique().tolist()) if products_df is not None and 'category' in products_df.columns else [])
        
        city = st.selectbox("Target City", cities)
        channel = st.selectbox("Target Channel", channels)
        category = st.selectbox("Target Category", categories)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        run_simulation = st.button("🚀 Run Simulation", use_container_width=True, type="primary")
    
    if run_simulation:
        with st.spinner("🔄 Running..."):
            try:
                sim = Simulator()
                results = sim.simulate_campaign(sales_df, stores_df, products_df, discount_pct=discount_pct, promo_budget=promo_budget, margin_floor=margin_floor, city=city, channel=channel, category=category, campaign_days=campaign_days)
                st.session_state.sim_results = results
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    if 'sim_results' in st.session_state and st.session_state.sim_results:
        results = st.session_state.sim_results
        outputs = results.get('outputs')
        comparison = results.get('comparison')
        warnings = results.get('warnings', [])
        
        if outputs:
            st.markdown("---")
            st.markdown('<p class="section-title section-title-teal">📊 Results</p>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                delta = f"{comparison['revenue_change_pct']:+.1f}%"
                st.markdown(create_metric_card("Expected Revenue", f"AED {outputs['expected_revenue']:,.0f}", delta, "positive" if comparison['revenue_change_pct'] > 0 else "negative", "cyan"), unsafe_allow_html=True)
            with col2:
                delta = f"{comparison['order_change_pct']:+.1f}%"
                st.markdown(create_metric_card("Expected Orders", f"{outputs['expected_orders']:,}", delta, "positive" if comparison['order_change_pct'] > 0 else "negative", "blue"), unsafe_allow_html=True)
            with col3:
                delta = f"{comparison['profit_change_pct']:+.1f}%"
                st.markdown(create_metric_card("Net Profit", f"AED {outputs['expected_net_profit']:,.0f}", delta, "positive" if comparison['profit_change_pct'] > 0 else "negative", "green"), unsafe_allow_html=True)
            with col4:
                st.markdown(create_metric_card("ROI", f"{outputs['roi_pct']:.1f}%", color="green" if outputs['roi_pct'] > 0 else "pink"), unsafe_allow_html=True)
            
            if warnings:
                st.markdown("---")
                for w in warnings:
                    st.warning(w)
            else:
                st.success("✅ Campaign looks healthy!")
            
            st.markdown("---")
            st.markdown('<p class="section-title section-title-blue">📈 Baseline vs Campaign</p>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Bar(name='Baseline', x=['Revenue', 'Profit'], y=[comparison['baseline_revenue'], comparison['baseline_profit']], marker_color='#3b82f6'))
                fig.add_trace(go.Bar(name='Campaign', x=['Revenue', 'Profit'], y=[outputs['expected_revenue'], outputs['expected_net_profit']], marker_color='#06b6d4'))
                fig = style_plotly_chart_themed(fig)
                fig.update_layout(barmode='group', title='Comparison')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(pd.DataFrame({'Type': ['Baseline', 'Campaign'], 'Orders': [comparison['baseline_orders'], outputs['expected_orders']]}), x='Type', y='Orders', title='Orders', color='Type', color_discrete_sequence=['#8b5cf6', '#ec4899'])
                fig = style_plotly_chart_themed(fig)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    
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
