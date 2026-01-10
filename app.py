# ============================================================================
# UAE Pulse Simulator + Data Rescue Dashboard
# Main Streamlit Application - EXECUTIVE THEME v3.0
# Complete Visual Overhaul with Light/Dark Mode
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
# DYNAMIC THEME CSS GENERATOR
# ============================================================================

def get_theme_css():
    """Generate CSS based on current theme state."""
    
    is_dark = st.session_state.theme == 'dark'
    
    # Theme-specific color palettes
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
            
            'chart_bg': 'rgba(0,0,0,0)',
            'chart_grid': '#1e293b',
            'chart_text': '#e2e8f0',
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
            'text_muted': '#94a3b8',
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
            
            'chart_bg': 'rgba(0,0,0,0)',
            'chart_grid': '#e2e8f0',
            'chart_text': '#334155',
        }
    
    # Accent colors (same for both themes)
    accents = {
        'cyan': '#06b6d4',
        'cyan_light': '#22d3ee',
        'blue': '#3b82f6',
        'blue_light': '#60a5fa',
        'purple': '#8b5cf6',
        'purple_light': '#a78bfa',
        'pink': '#ec4899',
        'pink_light': '#f472b6',
        'green': '#10b981',
        'green_light': '#34d399',
        'orange': '#f59e0b',
        'orange_light': '#fbbf24',
        'red': '#ef4444',
        'red_light': '#f87171',
        'teal': '#14b8a6',
        'teal_light': '#2dd4bf',
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
            
            --accent-cyan: {accents['cyan']};
            --accent-cyan-light: {accents['cyan_light']};
            --accent-blue: {accents['blue']};
            --accent-blue-light: {accents['blue_light']};
            --accent-purple: {accents['purple']};
            --accent-purple-light: {accents['purple_light']};
            --accent-pink: {accents['pink']};
            --accent-pink-light: {accents['pink_light']};
            --accent-green: {accents['green']};
            --accent-green-light: {accents['green_light']};
            --accent-orange: {accents['orange']};
            --accent-orange-light: {accents['orange_light']};
            --accent-red: {accents['red']};
            --accent-red-light: {accents['red_light']};
            --accent-teal: {accents['teal']};
            --accent-teal-light: {accents['teal_light']};
            
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
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes slideInLeft {{
            from {{ opacity: 0; transform: translateX(-20px); }}
            to {{ opacity: 1; transform: translateX(0); }}
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
        
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        
        @keyframes gradientFlow {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        @keyframes borderGlow {{
            0%, 100% {{ border-color: var(--accent-cyan); }}
            33% {{ border-color: var(--accent-purple); }}
            66% {{ border-color: var(--accent-pink); }}
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
        
        /* ===== SIDEBAR - EXECUTIVE STYLE ===== */
        [data-testid="stSidebar"] {{
            background: {colors['gradient_sidebar']};
            border-right: 1px solid var(--border-default);
            box-shadow: 4px 0 30px rgba(0, 0, 0, 0.15);
            transition: all var(--transition-normal);
        }}
        
        [data-testid="stSidebar"]::before {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 3px;
            height: 100%;
            background: linear-gradient(180deg, 
                var(--accent-cyan) 0%, 
                var(--accent-purple) 50%, 
                var(--accent-pink) 100%);
            opacity: 0.8;
        }}
        
        [data-testid="stSidebar"] > div {{
            padding-top: 1rem;
        }}
        
        /* ===== TYPOGRAPHY ===== */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Inter', sans-serif;
            color: var(--text-primary);
            font-weight: 700;
            letter-spacing: -0.02em;
        }}
        
        p, span, div {{
            color: var(--text-secondary);
        }}
        
        /* ===== 3D METRIC CARDS ===== */
        .metric-card-3d {{
            background: {colors['gradient_card']};
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: var(--radius-xl);
            padding: 28px 24px;
            border: 1px solid var(--border-default);
            box-shadow: 
                var(--shadow-md),
                inset 0 1px 0 rgba(255, 255, 255, 0.05),
                inset 0 -1px 0 rgba(0, 0, 0, 0.1);
            transition: all var(--transition-slow);
            position: relative;
            overflow: hidden;
            height: 150px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transform-style: preserve-3d;
            perspective: 1000px;
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
        
        .metric-card-3d::after {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                45deg,
                transparent 40%,
                rgba(255, 255, 255, 0.03) 50%,
                transparent 60%
            );
            transform: translateX(-100%);
            transition: transform 0.6s ease;
        }}
        
        .metric-card-3d:hover {{
            transform: translateY(-8px) rotateX(2deg);
            box-shadow: 
                var(--shadow-xl),
                0 20px 40px rgba(6, 182, 212, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            border-color: var(--border-hover);
        }}
        
        .metric-card-3d:hover::before {{
            opacity: 1;
        }}
        
        .metric-card-3d:hover::after {{
            transform: translateX(100%);
        }}
        
        .metric-label {{
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 4px;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: -0.02em;
            margin: 8px 0;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
            -webkit-backdrop-filter: blur(20px);
            border-radius: var(--radius-xl);
            padding: 40px 28px;
            border: 1px solid var(--border-default);
            box-shadow: 
                var(--shadow-md),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
            transition: all var(--transition-slow);
            height: 240px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            position: relative;
            overflow: hidden;
            transform-style: preserve-3d;
        }}
        
        .feature-card-3d::before {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 60%;
            height: 4px;
            background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
            opacity: 0;
            transition: all var(--transition-normal);
        }}
        
        .feature-card-3d:hover {{
            transform: translateY(-12px) scale(1.02);
            box-shadow: 
                var(--shadow-xl),
                0 30px 60px rgba(6, 182, 212, 0.15);
            border-color: var(--border-hover);
        }}
        
        .feature-card-3d:hover::before {{
            opacity: 1;
            width: 80%;
        }}
        
        .feature-icon {{
            font-size: 3.5rem;
            margin-bottom: 20px;
            filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
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
            -webkit-backdrop-filter: blur(20px);
            border-radius: var(--radius-2xl);
            padding: 60px 50px;
            margin-bottom: 40px;
            border: 1px solid var(--border-default);
            box-shadow: 
                var(--shadow-lg),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.8s ease-out;
        }}
        
        .hero-container::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -30%;
            width: 80%;
            height: 200%;
            background: radial-gradient(
                ellipse,
                rgba(6, 182, 212, 0.08) 0%,
                transparent 60%
            );
            animation: float3D 8s ease-in-out infinite;
        }}
        
        .hero-title {{
            font-size: 4rem;
            font-weight: 900;
            background: linear-gradient(135deg, 
                var(--text-primary) 0%, 
                var(--accent-cyan) 40%, 
                var(--accent-purple) 70%, 
                var(--accent-pink) 100%);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 20px;
            line-height: 1.1;
            animation: gradientFlow 5s ease infinite;
            position: relative;
            z-index: 1;
        }}
        
        .hero-subtitle {{
            font-size: 1.25rem;
            color: var(--text-secondary);
            line-height: 1.7;
            position: relative;
            z-index: 1;
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
            animation: pulse3D 3s ease-in-out infinite;
        }}
        
        /* ===== PAGE TITLES ===== */
        .page-title {{
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 8px;
            letter-spacing: -0.03em;
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
            animation: fadeInUp 0.6s ease-out;
        }}
        
        /* ===== SECTION TITLES ===== */
        .section-title {{
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section-title::after {{
            content: '';
            flex: 1;
            height: 2px;
            background: linear-gradient(90deg, var(--border-default), transparent);
            margin-left: 15px;
        }}
        
        .section-title-cyan {{ color: var(--accent-cyan); }}
        .section-title-blue {{ color: var(--accent-blue); }}
        .section-title-purple {{ color: var(--accent-purple); }}
        .section-title-pink {{ color: var(--accent-pink); }}
        .section-title-green {{ color: var(--accent-green); }}
        .section-title-teal {{ color: var(--accent-teal); }}
        .section-title-orange {{ color: var(--accent-orange); }}
        
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
            box-shadow: var(--shadow-md), var(--shadow-glow-cyan);
            border-left-color: var(--accent-cyan-light);
        }}
        
        .success-card {{
            background: linear-gradient(135deg, 
                rgba(16, 185, 129, 0.08) 0%, 
                rgba(20, 184, 166, 0.08) 100%);
            backdrop-filter: blur(15px);
            border-radius: var(--radius-lg);
            padding: 22px 28px;
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-left: 4px solid var(--accent-green);
            box-shadow: var(--shadow-sm);
            margin: 15px 0;
            color: var(--text-primary);
            transition: all var(--transition-normal);
        }}
        
        .success-card:hover {{
            transform: translateX(8px);
            box-shadow: var(--shadow-md), 0 0 30px rgba(16, 185, 129, 0.1);
        }}
        
        .warning-card {{
            background: linear-gradient(135deg, 
                rgba(245, 158, 11, 0.08) 0%, 
                rgba(251, 146, 60, 0.08) 100%);
            backdrop-filter: blur(15px);
            border-radius: var(--radius-lg);
            padding: 22px 28px;
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-left: 4px solid var(--accent-orange);
            box-shadow: var(--shadow-sm);
            margin: 15px 0;
            color: var(--text-primary);
            transition: all var(--transition-normal);
        }}
        
        .warning-card:hover {{
            transform: translateX(8px);
            box-shadow: var(--shadow-md), 0 0 30px rgba(245, 158, 11, 0.1);
        }}
        
        .error-card {{
            background: linear-gradient(135deg, 
                rgba(239, 68, 68, 0.08) 0%, 
                rgba(236, 72, 153, 0.08) 100%);
            backdrop-filter: blur(15px);
            border-radius: var(--radius-lg);
            padding: 22px 28px;
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-left: 4px solid var(--accent-red);
            box-shadow: var(--shadow-sm);
            margin: 15px 0;
            color: var(--text-primary);
            transition: all var(--transition-normal);
        }}
        
        .error-card:hover {{
            transform: translateX(8px);
            box-shadow: var(--shadow-md), 0 0 30px rgba(239, 68, 68, 0.1);
        }}
        
        /* ===== INSIGHT CARD ===== */
        .insight-card {{
            background: linear-gradient(135deg, 
                rgba(139, 92, 246, 0.1) 0%, 
                rgba(236, 72, 153, 0.08) 100%);
            backdrop-filter: blur(15px);
            border-radius: var(--radius-lg);
            padding: 22px 28px;
            border: 1px solid rgba(139, 92, 246, 0.25);
            box-shadow: var(--shadow-sm);
            margin: 15px 0;
            transition: all var(--transition-normal);
        }}
        
        .insight-card:hover {{
            transform: translateX(8px);
            border-color: var(--accent-purple);
            box-shadow: var(--shadow-md), var(--shadow-glow-purple);
        }}
        
        .insight-title {{
            color: var(--accent-purple-light);
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .insight-text {{
            color: var(--text-primary);
            font-size: 1rem;
            line-height: 1.6;
        }}
        
        /* ===== TABS - 3D STYLE ===== */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: transparent;
            padding: 4px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: {colors['gradient_card']};
            border-radius: var(--radius-md);
            color: var(--text-secondary);
            padding: 14px 28px;
            border: 1px solid var(--border-default);
            font-weight: 600;
            font-size: 0.95rem;
            box-shadow: var(--shadow-sm);
            transition: all var(--transition-normal);
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-hover);
            transform: translateY(-3px);
            box-shadow: var(--shadow-md);
            color: var(--text-primary);
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue)) !important;
            color: white !important;
            border: none !important;
            box-shadow: var(--shadow-md), 0 4px 20px rgba(6, 182, 212, 0.3);
            transform: translateY(-2px);
        }}
        
        .stTabs [aria-selected="true"]:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg), 0 6px 30px rgba(6, 182, 212, 0.4);
        }}
        
        /* ===== BUTTONS - 3D STYLE ===== */
        .stButton > button {{
            background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
            color: white;
            border: none;
            border-radius: var(--radius-lg);
            padding: 16px 36px;
            font-weight: 700;
            font-size: 1rem;
            letter-spacing: 0.02em;
            box-shadow: 
                var(--shadow-md),
                0 4px 15px rgba(6, 182, 212, 0.25),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            transition: all var(--transition-normal);
            position: relative;
            overflow: hidden;
        }}
        
        .stButton > button::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.2),
                transparent
            );
            transition: left 0.5s ease;
        }}
        
        .stButton > button:hover {{
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
            transform: translateY(-4px);
            box-shadow: 
                var(--shadow-lg),
                0 8px 30px rgba(59, 130, 246, 0.35),
                inset 0 1px 0 rgba(255, 255, 255, 0.25);
        }}
        
        .stButton > button:hover::before {{
            left: 100%;
        }}
        
        .stButton > button:active {{
            transform: translateY(-2px);
        }}
        
        /* ===== THEME TOGGLE ===== */
        .theme-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background: {colors['gradient_card']};
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-default);
            border-radius: 50px;
            padding: 8px 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: var(--shadow-md);
            cursor: pointer;
            transition: all var(--transition-normal);
        }}
        
        .theme-toggle:hover {{
            transform: scale(1.05);
            box-shadow: var(--shadow-lg);
            border-color: var(--border-hover);
        }}
        
        .theme-toggle-icon {{
            font-size: 1.2rem;
        }}
        
        .theme-toggle-label {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-primary);
        }}
        
        /* ===== DATA TABLES ===== */
        .stDataFrame {{
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: var(--shadow-md);
        }}
        
        .stDataFrame > div {{
            background: var(--bg-card);
        }}
        
        /* ===== INPUT ELEMENTS ===== */
        .stSelectbox > div > div {{
            background: var(--bg-card);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-md);
            transition: all var(--transition-normal);
            color: var(--text-primary);
        }}
        
        .stSelectbox > div > div:hover {{
            border-color: var(--border-hover);
        }}
        
        .stMultiSelect > div > div {{
            background: var(--bg-card);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-md);
        }}
        
        .stSlider > div > div > div {{
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue)) !important;
        }}
        
        .stTextInput > div > div {{
            background: var(--bg-card);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-md);
        }}
        
        .stNumberInput > div > div {{
            background: var(--bg-card);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-md);
        }}
        
        /* ===== FILE UPLOADER ===== */
        .stFileUploader > div {{
            background: var(--bg-card);
            border: 2px dashed var(--border-default);
            border-radius: var(--radius-lg);
            padding: 30px;
            transition: all var(--transition-normal);
        }}
        
        .stFileUploader > div:hover {{
            border-color: var(--accent-cyan);
            background: var(--bg-card-hover);
        }}
        
        /* ===== EXPANDER ===== */
        .streamlit-expanderHeader {{
            background: var(--bg-card);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-md);
            padding: 16px 20px;
            font-weight: 600;
            color: var(--text-primary);
            transition: all var(--transition-normal);
        }}
        
        .streamlit-expanderHeader:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-hover);
        }}
        
        /* ===== DIVIDER ===== */
        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, 
                transparent, 
                var(--border-default) 20%, 
                var(--border-default) 80%, 
                transparent);
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
            overflow: hidden;
        }}
        
        .footer::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, 
                var(--accent-cyan), 
                var(--accent-blue), 
                var(--accent-purple), 
                var(--accent-pink));
        }}
        
        .footer-title {{
            color: var(--text-primary);
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 12px;
        }}
        
        .footer-subtitle {{
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-bottom: 12px;
        }}
        
        .footer-names {{
            background: linear-gradient(90deg, 
                var(--accent-cyan), 
                var(--accent-blue), 
                var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
            font-size: 1.1rem;
        }}
        
        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {{
            width: 10px;
            height: 10px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--bg-secondary);
            border-radius: 5px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(180deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 5px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(180deg, var(--accent-blue), var(--accent-pink));
        }}
        
        /* ===== STATUS INDICATOR ===== */
        .status-indicator {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 0;
        }}
        
        .status-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse3D 2s ease-in-out infinite;
        }}
        
        .status-dot-green {{
            background: var(--accent-green);
            box-shadow: 0 0 10px var(--accent-green);
        }}
        
        .status-dot-yellow {{
            background: var(--accent-orange);
            box-shadow: 0 0 10px var(--accent-orange);
        }}
        
        .status-dot-red {{
            background: var(--accent-red);
            box-shadow: 0 0 10px var(--accent-red);
        }}
        
        .status-text {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 500;
        }}
        
        /* ===== DOWNLOAD BUTTON ===== */
        .stDownloadButton > button {{
            background: linear-gradient(135deg, var(--accent-green) 0%, var(--accent-teal) 100%);
            color: white;
            border: none;
            border-radius: var(--radius-md);
            padding: 12px 24px;
            font-weight: 600;
            box-shadow: var(--shadow-sm), 0 4px 15px rgba(16, 185, 129, 0.2);
            transition: all var(--transition-normal);
        }}
        
        .stDownloadButton > button:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-md), 0 6px 25px rgba(16, 185, 129, 0.3);
        }}
        
        /* ===== RADIO BUTTONS ===== */
        .stRadio > div {{
            gap: 8px;
        }}
        
        .stRadio > div > label {{
            background: var(--bg-card);
            border: 1px solid var(--border-default);
            border-radius: var(--radius-md);
            padding: 12px 20px;
            transition: all var(--transition-normal);
            cursor: pointer;
        }}
        
        .stRadio > div > label:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-hover);
            transform: translateX(4px);
        }}
        
        /* ===== PLOTLY CHARTS CONTAINER ===== */
        .js-plotly-plot {{
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: var(--shadow-md);
        }}
        
    </style>
    """

# Apply dynamic theme CSS
st.markdown(get_theme_css(), unsafe_allow_html=True)

# ============================================================================
# THEME TOGGLE BUTTON (Fixed Position)
# ============================================================================

def render_theme_toggle():
    """Render the theme toggle button."""
    is_dark = st.session_state.theme == 'dark'
    icon = "🌙" if is_dark else "☀️"
    label = "Dark" if is_dark else "Light"
    
    st.markdown(f"""
    <div class="theme-toggle" id="theme-toggle">
        <span class="theme-toggle-icon">{icon}</span>
        <span class="theme-toggle-label">{label} Mode</span>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS FOR UI (Updated for 3D Theme)
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

def style_plotly_chart_themed(fig):
    """Apply theme-aware styling to Plotly charts."""
    is_dark = st.session_state.theme == 'dark'
    
    bg_color = 'rgba(0,0,0,0)'
    grid_color = '#1e293b' if is_dark else '#e2e8f0'
    text_color = '#e2e8f0' if is_dark else '#334155'
    
    fig.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color, family='Inter'),
        title_font=dict(size=18, color=text_color),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color)
        ),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    fig.update_xaxes(gridcolor=grid_color, zerolinecolor=grid_color)
    fig.update_yaxes(gridcolor=grid_color, zerolinecolor=grid_color)
    
    return fig

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
    
    if city_kpis is not None and len(city_kpis) > 0:
        top_city = city_kpis.iloc[0]['city'] if 'city' in city_kpis.columns else None
        if top_city:
            top_revenue = city_kpis.iloc[0]['revenue']
            total_revenue = city_kpis['revenue'].sum()
            pct = (top_revenue / total_revenue * 100) if total_revenue > 0 else 0
            insights.append(("Market Concentration", f"{top_city} contributes {pct:.0f}% of total revenue."))
    
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
# SIDEBAR NAVIGATION (Executive Style)
# ============================================================================

with st.sidebar:
    # Theme Toggle in Sidebar
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        theme_icon = "🌙" if st.session_state.theme == 'dark' else "☀️"
        theme_label = "Dark Mode" if st.session_state.theme == 'dark' else "Light Mode"
        if st.button(f"{theme_icon} {theme_label}", key="theme_toggle_btn", use_container_width=True):
            toggle_theme()
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Logo & Branding
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0 30px 0;">
        <div style="
            font-size: 56px; 
            margin-bottom: 10px;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
        ">🛒</div>
        <div style="
            font-size: 28px;
            font-weight: 900;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
        ">UAE Pulse</div>
        <div style="
            color: var(--text-muted); 
            font-size: 13px;
            margin-top: 5px;
            letter-spacing: 1px;
        ">SIMULATOR + DATA RESCUE</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("""
    <p style="
        color: var(--accent-pink); 
        font-weight: 700; 
        margin-bottom: 15px; 
        letter-spacing: 2px; 
        font-size: 0.75rem;
        text-transform: uppercase;
    ">📍 Navigation</p>
    """, unsafe_allow_html=True)
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📂 Data", "🧹 Cleaner", "📊 Dashboard", "🎯 Simulator"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Status Panel
    st.markdown("""
    <p style="
        color: var(--accent-blue); 
        font-weight: 700; 
        margin-bottom: 15px; 
        letter-spacing: 2px; 
        font-size: 0.75rem;
        text-transform: uppercase;
    ">📡 System Status</p>
    """, unsafe_allow_html=True)
    
    data_loaded = st.session_state.data_loaded
    data_cleaned = st.session_state.is_cleaned
    
    status_class_loaded = "status-dot-green" if data_loaded else "status-dot-red"
    status_class_cleaned = "status-dot-green" if data_cleaned else ("status-dot-yellow" if data_loaded else "status-dot-red")
    
    st.markdown(f"""
    <div style="
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 20px;
        border: 1px solid var(--border-default);
        box-shadow: var(--shadow-sm);
    ">
        <div class="status-indicator">
            <div class="status-dot {status_class_loaded}"></div>
            <span class="status-text">Data Loaded</span>
        </div>
        <div class="status-indicator">
            <div class="status-dot {status_class_cleaned}"></div>
            <span class="status-text">Data Cleaned</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats (if data loaded)
    if st.session_state.data_loaded:
        st.markdown("---")
        st.markdown("""
        <p style="
            color: var(--accent-purple); 
            font-weight: 700; 
            margin-bottom: 15px; 
            letter-spacing: 2px; 
            font-size: 0.75rem;
            text-transform: uppercase;
        ">📈 Quick Stats</p>
        """, unsafe_allow_html=True)
        
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
                background: var(--bg-card);
                border-radius: var(--radius-lg);
                padding: 20px;
                border: 1px solid var(--border-default);
                box-shadow: var(--shadow-sm);
            ">
                <div style="margin-bottom: 16px;">
                    <span style="
                        color: var(--text-muted); 
                        font-size: 0.7rem; 
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    ">Total Records</span><br>
                    <span style="
                        color: var(--accent-cyan); 
                        font-weight: 800; 
                        font-size: 1.6rem;
                        font-family: 'JetBrains Mono', monospace;
                    ">{total_records:,}</span>
                </div>
                <div>
                    <span style="
                        color: var(--text-muted); 
                        font-size: 0.7rem; 
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    ">Revenue</span><br>
                    <span style="
                        color: var(--accent-green); 
                        font-weight: 800; 
                        font-size: 1.4rem;
                        font-family: 'JetBrains Mono', monospace;
                    ">{formatted_revenue}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Download Section
    if st.session_state.data_loaded and st.session_state.is_cleaned:
        st.markdown("---")
        st.markdown("""
        <p style="
            color: var(--accent-green); 
            font-weight: 700; 
            margin-bottom: 15px; 
            letter-spacing: 2px; 
            font-size: 0.75rem;
            text-transform: uppercase;
        ">📥 Export</p>
        """, unsafe_allow_html=True)
        
        import io
        import zipfile
        
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
            label="📦 Download All (ZIP)",
            data=zip_buffer,
            file_name="cleaned_data.zip",
            mime="application/zip",
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <p style="
        color: var(--accent-teal); 
        font-weight: 700; 
        margin-bottom: 10px; 
        letter-spacing: 2px; 
        font-size: 0.75rem;
        text-transform: uppercase;
    ">🔬 Tech Stack</p>
    <div style="
        color: var(--text-muted); 
        font-size: 11px; 
        line-height: 1.8;
    ">
        Python • Pandas • Plotly<br>
        Streamlit • NumPy
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# FILE VALIDATION HELPER
# ============================================================================

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
    
    should_have_found = 0
    for col in config['should_have']:
        alternates = config['alternate_names'].get(col, [col])
        for alt in alternates:
            if alt.lower() in df_columns:
                should_have_found += 1
                found_columns.append(alt)
                break
    
    if len(missing_must_have) > 0:
        return False, f"Missing required columns: {', '.join(missing_must_have)}", found_columns
    
    total_expected = len(config['must_have']) + len(config['should_have'])
    total_found = len(config['must_have']) - len(missing_must_have) + should_have_found
    confidence = total_found / total_expected * 100
    
    if confidence < 40:
        return False, f"This doesn't look like a {file_type} file. Only {confidence:.0f}% columns match.", found_columns
    
    return True, f"Valid {file_type} file ({confidence:.0f}% confidence)", found_columns

# ============================================================================
# PAGE: HOME
# ============================================================================

def show_home_page():
    """Display the home page."""
    
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div style="margin-bottom: 24px;">
            <span class="hero-badge">✨ UAE E-Commerce Analytics</span>
            <span class="hero-badge" style="background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));">
                🚀 v3.0 Executive
            </span>
        </div>
        <div class="hero-title">UAE Pulse Simulator</div>
        <p class="hero-subtitle">
            Transform your e-commerce data into actionable insights.<br>
            Clean dirty data, simulate promotional campaigns, and visualize performance metrics.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
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
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Capabilities Section
    st.markdown('<p class="section-title section-title-teal">🔥 What You Can Do</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4 style="color: var(--accent-cyan); margin-top: 0; font-size: 1.15rem; font-weight: 700;">🧹 Data Cleaning Capabilities</h4>
            <ul style="color: var(--text-secondary); margin-bottom: 0; font-size: 0.95rem; line-height: 2;">
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
        <div class="info-card" style="border-left-color: var(--accent-purple);">
            <h4 style="color: var(--accent-purple); margin-top: 0; font-size: 1.15rem; font-weight: 700;">🎯 Simulation Features</h4>
            <ul style="color: var(--text-secondary); margin-bottom: 0; font-size: 0.95rem; line-height: 2;">
                <li>Discount impact modeling</li>
                <li>Category elasticity analysis</li>
                <li>Channel performance comparison</li>
                <li>ROI & margin forecasting</li>
                <li>Risk warning system</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Quick Start Guide
    st.markdown('<p class="section-title section-title-blue">🚀 Quick Start Guide</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    steps = [
        ("1️⃣", "Load Data", "Go to 📂 Data page and upload your files or load sample data", "cyan"),
        ("2️⃣", "Clean Data", "Go to 🧹 Cleaner to detect and fix data issues", "blue"),
        ("3️⃣", "View Insights", "Check 📊 Dashboard for Executive & Manager views", "purple"),
        ("4️⃣", "Simulate", "Go to 🎯 Simulator to run what-if campaigns", "pink"),
    ]
    
    for col, (num, title, desc, color) in zip([col1, col2, col3, col4], steps):
        with col:
            st.markdown(f"""
            <div style="
                text-align: center; 
                padding: 30px 20px;
                background: var(--bg-card);
                border-radius: var(--radius-xl);
                border: 1px solid var(--border-default);
                box-shadow: var(--shadow-sm);
                transition: all var(--transition-normal);
            ">
                <div style="font-size: 52px; margin-bottom: 15px;">{num}</div>
                <div style="color: var(--accent-{color}); font-weight: 700; margin-bottom: 8px; font-size: 1.1rem;">{title}</div>
                <div style="color: var(--text-muted); font-size: 0.9rem; line-height: 1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Data Status
    if st.session_state.data_loaded:
        st.markdown(create_success_card("Data is loaded! Go to 📊 Dashboard to see your KPIs."), unsafe_allow_html=True)
    else:
        st.markdown(create_info_card("💡 <strong>Start by loading data.</strong> Go to 📂 Data page."), unsafe_allow_html=True)
    
    show_footer()

# ============================================================================
# PAGE: DASHBOARD
# ============================================================================

def show_dashboard_page():
    """Display the dashboard page."""
    
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
    
    # Global Filters
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
                    date_range = st.date_input(
                        "📅 Date Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        key="global_date_filter"
                    )
            except:
                st.caption("Date filter unavailable")
    
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
    
    # Apply Filters
    filtered_sales = sales_df.copy()
    filtered_stores = stores_df.copy() if stores_df is not None else None
    filtered_products = products_df.copy() if products_df is not None else None
    filtered_inventory = inventory_df.copy() if inventory_df is not None else None
    
    if date_range and len(date_range) == 2 and 'order_time' in filtered_sales.columns:
        start_date, end_date = date_range
        filtered_sales = filtered_sales[
            (filtered_sales['order_time'].dt.date >= start_date) &
            (filtered_sales['order_time'].dt.date <= end_date)
        ]
    
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
    
    original_count = len(sales_df)
    filtered_count = len(filtered_sales)
    filter_pct = (filtered_count / original_count * 100) if original_count > 0 else 0
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(59, 130, 246, 0.1)); 
        padding: 12px 24px; 
        border-radius: var(--radius-md); 
        margin: 15px 0;
        border: 1px solid var(--border-default);
    ">
        <span style="color: var(--accent-cyan); font-weight: 700;">📊 Showing {filtered_count:,} of {original_count:,} records ({filter_pct:.1f}%)</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for Executive and Manager Views
    tab_exec, tab_mgr = st.tabs([
        "👔 Executive View — Financial & Strategic",
        "📋 Manager View — Operational Risk & Execution"
    ])
    
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
    """Display Executive View - Financial & Strategic KPIs."""
    
    st.markdown('<p class="section-title section-title-cyan">💰 Financial KPIs</p>', unsafe_allow_html=True)
    
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
        avg_order_value = kpis.get('avg_order_value', 0)
        st.markdown(create_metric_card(
            "Avg Order Value",
            format_currency(avg_order_value),
            color="cyan"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
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
        text=[format_currency(gross_rev), format_currency(-refunds), format_currency(-discounts), 
              format_currency(-cogs_val), format_currency(net_profit)],
        textposition="outside"
    ))
    
    fig_waterfall = style_plotly_chart_themed(fig_waterfall)
    fig_waterfall.update_layout(height=400, showlegend=False)
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    st.caption("📌 How Net Profit is built: Gross Revenue minus Refunds, Discounts, and COGS.")
    
    st.markdown("---")
    st.markdown('<p class="section-title section-title-green">📈 Revenue & Margin Analysis</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
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
                
                fig_area = style_plotly_chart_themed(fig_area)
                fig_area.update_layout(
                    title=f"{time_group} Revenue Trend",
                    height=380,
                    xaxis_title=time_group,
                    yaxis_title="Revenue (AED)",
                    xaxis=dict(type='category')
                )
                
                st.plotly_chart(fig_area, use_container_width=True)
                st.caption(f"📌 {time_group} revenue pattern to identify seasonality and plan promotions.")
            else:
                st.info("No valid dates in data range")
        else:
            st.info("Revenue trend requires order_time column")
    
    with col2:
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
            
            fig_margin = style_plotly_chart_themed(fig_margin)
            fig_margin.update_layout(
                title="Gross Margin % by Category",
                height=380,
                xaxis_title="Margin %",
                yaxis_title=""
            )
            
            st.plotly_chart(fig_margin, use_container_width=True)
            st.caption("📌 Red < 20%, Yellow < 30%, Green ≥ 30%.")
        else:
            st.info("Category data not available")
    
    st.markdown("---")
    st.markdown('<p class="section-title section-title-purple">💡 Executive Recommendations</p>', unsafe_allow_html=True)
    
    recommendations = []
    
    if gross_margin_pct >= 30:
        recommendations.append(f"✅ **Healthy Margin**: Gross margin at {gross_margin_pct:.1f}% is strong.")
    elif gross_margin_pct >= 20:
        recommendations.append(f"⚠️ **Moderate Margin**: Gross margin at {gross_margin_pct:.1f}%. Monitor discounts.")
    else:
        recommendations.append(f"🔴 **Low Margin Alert**: Gross margin at {gross_margin_pct:.1f}%. Reduce discounts or optimize COGS.")
    
    avg_discount = kpis.get('avg_discount_pct', 0)
    if avg_discount > 15:
        recommendations.append(f"⚠️ **High Discounting**: Average discount at {avg_discount:.1f}%.")
    
    if city_kpis is not None and len(city_kpis) > 0:
        top_city = city_kpis.nlargest(1, 'revenue')['city'].values[0]
        recommendations.append(f"🏆 **Top Market**: {top_city} leads in revenue.")
    
    for rec in recommendations:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(59, 130, 246, 0.08)); 
            border-left: 4px solid var(--accent-purple); 
            padding: 16px 20px; 
            border-radius: var(--radius-md); 
            margin-bottom: 12px;
        ">
            <p style="color: var(--text-primary); margin: 0; font-size: 1rem;">{rec}</p>
        </div>
        """, unsafe_allow_html=True)


def show_manager_view(kpis, city_kpis, channel_kpis, category_kpis, sales_df, products_df, stores_df, inventory_df):
    """Display Manager View - Operational Risk & Execution."""
    
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
    st.markdown('<p class="section-title section-title-teal">📊 Risk Overview</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=stockout_risk,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Stockout Risk %", 'font': {'size': 16}},
            number={'suffix': "%", 'font': {'size': 32}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': '#06b6d4'},
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
        
        fig_gauge = style_plotly_chart_themed(fig_gauge)
        fig_gauge.update_layout(height=300)
        
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.caption("📌 Green = Safe (0-30%), Yellow = Caution (30-60%), Red = Critical (60%+)")
    
    with col2:
        if inventory_df is not None and stores_df is not None and 'store_id' in inventory_df.columns:
            inv_with_store = inventory_df.merge(stores_df[['store_id', 'city', 'channel']], on='store_id', how='left')
            
            if all(col in inv_with_store.columns for col in ['city', 'channel', 'stock_on_hand']):
                top_n_risk = st.selectbox("Show Top", [5, 10, "All"], index=0, key="city_channel_risk_top_n")
                
                inv_with_store['city_channel'] = inv_with_store['city'] + ' - ' + inv_with_store['channel']
                
                city_channel_risk = inv_with_store.groupby('city_channel').apply(
                    lambda x: (x['stock_on_hand'] < 10).sum() / len(x) * 100 if len(x) > 0 else 0,
                    include_groups=False
                ).reset_index()
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
                
                fig_risk_bar = style_plotly_chart_themed(fig_risk_bar)
                fig_risk_bar.update_layout(
                    title="Stockout Risk by City-Channel",
                    height=300,
                    xaxis_title="Risk %",
                    yaxis_title=""
                )
                
                st.plotly_chart(fig_risk_bar, use_container_width=True)
                st.caption("📌 Prioritize replenishment for red/yellow areas.")
            else:
                st.info("City-channel risk data not available")
        else:
            st.info("Inventory or store data not available")
    
    st.markdown("---")
    st.markdown('<p class="section-title section-title-pink">⚠️ Operational Alerts</p>', unsafe_allow_html=True)
    
    alerts = []
    
    if stockout_risk > 15:
        alerts.append(f"🔴 **High Stockout Risk**: {stockout_risk:.1f}% of inventory at risk.")
    
    if return_rate > 5:
        alerts.append(f"🟠 **Elevated Return Rate**: {return_rate:.1f}% returns.")
    
    if payment_failure_rate > 3:
        alerts.append(f"🟡 **Payment Failures**: {payment_failure_rate:.1f}% orders failed.")
    
    if high_risk_skus > 50:
        alerts.append(f"🔴 **{high_risk_skus} SKUs** at critically low stock.")
    
    if len(alerts) == 0:
        st.markdown(create_success_card("All operational metrics within healthy ranges."), unsafe_allow_html=True)
    else:
        for alert in alerts:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(245, 158, 11, 0.08)); 
                border-left: 4px solid var(--accent-orange); 
                padding: 16px 20px; 
                border-radius: var(--radius-md); 
                margin-bottom: 12px;
            ">
                <p style="color: var(--text-primary); margin: 0; font-size: 1rem;">{alert}</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# PAGE: DATA
# ============================================================================

def show_data_page():
    """Display the data management page."""
    
    st.markdown('<h1 class="page-title page-title-cyan">📂 Data Management</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Upload, view, and manage your e-commerce data files</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<p class="section-title section-title-blue">📤 Upload Data Files</p>', unsafe_allow_html=True)
    
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
                    st.success(f"✅ Valid products file ({len(products_df):,} rows)")
                    valid_files['products'] = products_df
                else:
                    st.error(f"❌ {validation['message']}")
            except Exception as e:
                st.error(f"❌ Cannot read file: {str(e)}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
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
            except Exception as e:
                st.error(f"❌ Cannot read file: {str(e)}")
    
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
            except Exception as e:
                st.error(f"❌ Cannot read file: {str(e)}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
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
            except Exception as e:
                st.error(f"❌ Cannot read file: {str(e)}")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        required_files = ['products', 'stores', 'sales', 'inventory']
        missing_files = [f for f in required_files if f not in valid_files]
        
        if len(valid_files) == 4:
            st.success(f"✅ All 4 files valid and ready to load!")
        elif len(valid_files) > 0:
            st.warning(f"⚠️ {len(valid_files)}/4 files valid. Missing: {', '.join(missing_files)}")
        else:
            st.info("📤 Please upload all 4 files: Products, Stores, Sales, Inventory")
        
        button_disabled = len(valid_files) != 4
        
        if st.button("📥 Load All Files", use_container_width=True, disabled=button_disabled):
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
    
    st.markdown("---")
    
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
                st.dataframe(df.head(100), use_container_width=True)
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
                st.dataframe(df.head(100), use_container_width=True)
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
                st.dataframe(df.head(100), use_container_width=True)
            else:
                st.info("📋 No inventory data loaded")
    
    show_footer()

# ============================================================================
# PAGE: CLEANER
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
            <strong style="color: var(--accent-cyan); font-size: 1.1rem;">Data Quality</strong>
            <ul style="color: var(--text-secondary); font-size: 0.95rem; margin-bottom: 0; line-height: 1.8;">
                <li>Missing values</li>
                <li>Duplicate records</li>
                <li>Whitespace issues</li>
                <li>Text standardization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card" style="border-left-color: var(--accent-purple);">
            <strong style="color: var(--accent-purple); font-size: 1.1rem;">Format Issues</strong>
            <ul style="color: var(--text-secondary); font-size: 0.95rem; margin-bottom: 0; line-height: 1.8;">
                <li>Multi-language text</li>
                <li>Non-English values</li>
                <li>Fuzzy matching</li>
                <li>Case normalization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card" style="border-left-color: var(--accent-pink);">
            <strong style="color: var(--accent-pink); font-size: 1.1rem;">Value Issues</strong>
            <ul style="color: var(--text-secondary); font-size: 0.95rem; margin-bottom: 0; line-height: 1.8;">
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
            after = len(st.session_state.clean_products) if st.session_state.clean_products is not None else 0
            st.markdown(create_metric_card("Products", f"{after:,}", color="cyan"), unsafe_allow_html=True)
        
        with col2:
            after = len(st.session_state.clean_stores) if st.session_state.clean_stores is not None else 0
            st.markdown(create_metric_card("Stores", f"{after:,}", color="blue"), unsafe_allow_html=True)
        
        with col3:
            after = len(st.session_state.clean_sales) if st.session_state.clean_sales is not None else 0
            st.markdown(create_metric_card("Sales", f"{after:,}", color="purple"), unsafe_allow_html=True)
        
        with col4:
            after = len(st.session_state.clean_inventory) if st.session_state.clean_inventory is not None else 0
            st.markdown(create_metric_card("Inventory", f"{after:,}", color="pink"), unsafe_allow_html=True)
        
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
        
        issues_df = st.session_state.issues_df
        
        if len(issues_df) > 0:
            st.markdown("---")
            st.markdown('<p class="section-title section-title-orange">🔍 Issues Detected & Fixed</p>', unsafe_allow_html=True)
            
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
                fig = style_plotly_chart_themed(fig)
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            
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
                fig = style_plotly_chart_themed(fig)
                st.plotly_chart(fig, use_container_width=True)
            
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
    
    show_footer()

# ============================================================================
# PAGE: SIMULATOR
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
        st.markdown('<p style="color: var(--accent-cyan); font-weight: 700; margin-bottom: 12px;">💰 Pricing</p>', unsafe_allow_html=True)
        discount_pct = st.slider("Discount %", 0, 50, 15)
        promo_budget = st.number_input("Promo Budget (AED)", 1000, 500000, 25000, step=5000)
    
    with col2:
        st.markdown('<p style="color: var(--accent-purple); font-weight: 700; margin-bottom: 12px;">📊 Constraints</p>', unsafe_allow_html=True)
        margin_floor = st.slider("Margin Floor %", 0, 50, 15)
        campaign_days = st.slider("Campaign Days", 1, 30, 7)
    
    with col3:
        st.markdown('<p style="color: var(--accent-pink); font-weight: 700; margin-bottom: 12px;">🎯 Targeting</p>', unsafe_allow_html=True)
        
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
                fig = style_plotly_chart_themed(fig)
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
                fig = style_plotly_chart_themed(fig)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        elif warnings:
            for warning in warnings:
                st.warning(warning)
    
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
