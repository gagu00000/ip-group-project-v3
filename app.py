# ============================================================================
# UAE Promo Pulse Simulator + Data Rescue Dashboard
# PREMIUM UI/UX VERSION with Glassmorphism, Neumorphism & Theme Toggle
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
    load_sample_data, get_data_summary
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
# INITIALIZE THEME STATE
# ============================================================================

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'  # Default to dark mode

def toggle_theme():
    """Toggle between dark and light theme."""
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

def get_theme():
    """Get current theme."""
    return st.session_state.theme

# ============================================================================
# DYNAMIC CSS - GLASSMORPHISM + NEUMORPHISM + THEME SUPPORT
# ============================================================================

def get_dynamic_css(theme='dark'):
    """Generate CSS based on current theme."""
    
    if theme == 'dark':
        css = """
        <style>
            /* ===== IMPORTS ===== */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
            
            /* ===== CSS VARIABLES - DARK THEME ===== */
            :root {
                /* Background Colors */
                --bg-primary: #0a0a0f;
                --bg-secondary: #12121a;
                --bg-tertiary: #1a1a24;
                --bg-card: rgba(22, 22, 31, 0.7);
                --bg-card-hover: rgba(30, 30, 45, 0.8);
                --bg-glass: rgba(255, 255, 255, 0.03);
                --bg-glass-hover: rgba(255, 255, 255, 0.06);
                
                /* Accent Colors */
                --accent-cyan: #06b6d4;
                --accent-cyan-glow: rgba(6, 182, 212, 0.4);
                --accent-blue: #3b82f6;
                --accent-blue-glow: rgba(59, 130, 246, 0.4);
                --accent-purple: #8b5cf6;
                --accent-purple-glow: rgba(139, 92, 246, 0.4);
                --accent-pink: #ec4899;
                --accent-pink-glow: rgba(236, 72, 153, 0.4);
                --accent-green: #10b981;
                --accent-green-glow: rgba(16, 185, 129, 0.4);
                --accent-orange: #f59e0b;
                --accent-orange-glow: rgba(245, 158, 11, 0.4);
                --accent-red: #ef4444;
                --accent-teal: #14b8a6;
                
                /* Text Colors */
                --text-primary: #f1f5f9;
                --text-secondary: #94a3b8;
                --text-muted: #64748b;
                --text-inverse: #0f172a;
                
                /* Border & Shadow */
                --border-color: rgba(255, 255, 255, 0.08);
                --border-glass: rgba(255, 255, 255, 0.12);
                --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
                --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.4);
                --shadow-lg: 0 8px 40px rgba(0, 0, 0, 0.5);
                --shadow-glow: 0 0 40px rgba(6, 182, 212, 0.15);
                
                /* Neumorphism - Dark */
                --neu-shadow-dark: 8px 8px 20px rgba(0, 0, 0, 0.6);
                --neu-shadow-light: -8px -8px 20px rgba(255, 255, 255, 0.03);
                --neu-inset-dark: inset 4px 4px 10px rgba(0, 0, 0, 0.5);
                --neu-inset-light: inset -4px -4px 10px rgba(255, 255, 255, 0.02);
                
                /* Glassmorphism */
                --glass-blur: 20px;
                --glass-saturation: 180%;
            }
            
            /* ===== ANIMATIONS ===== */
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes fadeInScale {
                from { opacity: 0; transform: scale(0.95); }
                to { opacity: 1; transform: scale(1); }
            }
            
            @keyframes pulse-glow {
                0%, 100% { box-shadow: 0 0 20px var(--accent-cyan-glow); }
                50% { box-shadow: 0 0 40px var(--accent-cyan-glow), 0 0 60px var(--accent-blue-glow); }
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                25% { transform: translateY(-8px) rotate(1deg); }
                75% { transform: translateY(-4px) rotate(-1deg); }
            }
            
            @keyframes shimmer {
                0% { background-position: -200% center; }
                100% { background-position: 200% center; }
            }
            
            @keyframes gradient-shift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            @keyframes border-flow {
                0% { border-color: var(--accent-cyan); }
                33% { border-color: var(--accent-purple); }
                66% { border-color: var(--accent-pink); }
                100% { border-color: var(--accent-cyan); }
            }
            
            /* ===== HIDE STREAMLIT DEFAULTS ===== */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display: none;}
            
            /* ===== MAIN BACKGROUND ===== */
            .stApp {
                background: 
                    radial-gradient(ellipse at 0% 0%, rgba(6, 182, 212, 0.08) 0%, transparent 50%),
                    radial-gradient(ellipse at 100% 0%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
                    radial-gradient(ellipse at 50% 100%, rgba(236, 72, 153, 0.05) 0%, transparent 50%),
                    linear-gradient(180deg, #0a0a0f 0%, #0d0d14 25%, #0f0f18 50%, #0d0d14 75%, #0a0a0f 100%);
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                min-height: 100vh;
                color: var(--text-primary);
            }
            
            /* ===== SIDEBAR - GLASSMORPHISM ===== */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, 
                    rgba(12, 12, 20, 0.95) 0%, 
                    rgba(15, 15, 24, 0.98) 50%, 
                    rgba(10, 10, 15, 0.95) 100%);
                backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
                -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
                border-right: 1px solid var(--border-glass);
            }
            
            [data-testid="stSidebar"]::before {
                content: '';
                position: absolute;
                top: 0;
                right: 0;
                width: 2px;
                height: 100%;
                background: linear-gradient(180deg, 
                    var(--accent-cyan), 
                    var(--accent-purple), 
                    var(--accent-pink),
                    var(--accent-cyan));
                background-size: 100% 200%;
                animation: gradient-shift 8s ease infinite;
                opacity: 0.7;
            }
            
            /* ===== GLASSMORPHISM CONTAINERS ===== */
            .glass-container {
                background: var(--bg-glass);
                backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
                -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
                border: 1px solid var(--border-glass);
                border-radius: 24px;
                padding: 30px;
                position: relative;
                overflow: hidden;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .glass-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, 
                    transparent 0%, 
                    rgba(255, 255, 255, 0.2) 50%, 
                    transparent 100%);
            }
            
            .glass-container:hover {
                background: var(--bg-glass-hover);
                border-color: rgba(255, 255, 255, 0.15);
                transform: translateY(-4px);
                box-shadow: var(--shadow-lg), var(--shadow-glow);
            }
            
            /* ===== NEUMORPHISM CARDS ===== */
            .neu-card {
                background: linear-gradient(145deg, #18181f 0%, #14141a 100%);
                border-radius: 20px;
                padding: 24px;
                box-shadow: var(--neu-shadow-dark), var(--neu-shadow-light);
                border: 1px solid var(--border-color);
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }
            
            .neu-card::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.02) 0%, transparent 50%);
                opacity: 0;
                transition: opacity 0.4s ease;
            }
            
            .neu-card:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 
                    12px 12px 30px rgba(0, 0, 0, 0.7),
                    -12px -12px 30px rgba(255, 255, 255, 0.04),
                    0 0 40px var(--accent-cyan-glow);
            }
            
            .neu-card:hover::before {
                opacity: 1;
            }
            
            /* ===== NEUMORPHISM INSET (for inputs/toggles) ===== */
            .neu-inset {
                background: linear-gradient(145deg, #12121a 0%, #0f0f15 100%);
                box-shadow: var(--neu-inset-dark), var(--neu-inset-light);
                border-radius: 12px;
                border: 1px solid var(--border-color);
            }
            
            /* ===== HERO SECTION - GLASSMORPHISM ===== */
            .hero-glass {
                background: linear-gradient(135deg, 
                    rgba(6, 182, 212, 0.08) 0%, 
                    rgba(139, 92, 246, 0.08) 50%, 
                    rgba(236, 72, 153, 0.08) 100%);
                backdrop-filter: blur(30px) saturate(200%);
                -webkit-backdrop-filter: blur(30px) saturate(200%);
                border-radius: 32px;
                padding: 60px 50px;
                margin-bottom: 40px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                position: relative;
                overflow: hidden;
                animation: fadeInScale 0.8s ease-out;
            }
            
            .hero-glass::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, 
                    var(--accent-cyan), 
                    var(--accent-blue), 
                    var(--accent-purple), 
                    var(--accent-pink));
                background-size: 200% 100%;
                animation: shimmer 3s ease infinite;
            }
            
            .hero-glass::after {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle at 30% 30%, rgba(6, 182, 212, 0.1) 0%, transparent 50%);
                animation: float 8s ease-in-out infinite;
            }
            
            /* ===== HERO TITLE ===== */
            .hero-title {
                font-size: 4.5rem;
                font-weight: 900;
                background: linear-gradient(135deg, 
                    #ffffff 0%, 
                    #06b6d4 30%, 
                    #8b5cf6 60%, 
                    #ec4899 100%);
                background-size: 200% 200%;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 20px;
                position: relative;
                z-index: 1;
                line-height: 1.1;
                animation: gradient-shift 6s ease infinite;
                text-shadow: 0 0 60px rgba(6, 182, 212, 0.3);
            }
            
            .hero-subtitle {
                font-size: 1.4rem;
                color: var(--text-secondary);
                margin-bottom: 30px;
                position: relative;
                z-index: 1;
                line-height: 1.7;
                font-weight: 400;
            }
            
            .hero-badge {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 12px 28px;
                background: linear-gradient(135deg, 
                    rgba(6, 182, 212, 0.2) 0%, 
                    rgba(59, 130, 246, 0.2) 100%);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(6, 182, 212, 0.3);
                border-radius: 50px;
                color: var(--accent-cyan);
                font-size: 0.95rem;
                font-weight: 600;
                margin-right: 12px;
                margin-bottom: 20px;
                transition: all 0.3s ease;
                animation: pulse-glow 3s ease infinite;
            }
            
            .hero-badge:hover {
                transform: translateY(-2px);
                border-color: var(--accent-cyan);
            }
            
            /* ===== PAGE TITLES ===== */
            .page-title {
                font-size: 3rem;
                font-weight: 800;
                margin-bottom: 12px;
                line-height: 1.2;
                letter-spacing: -0.02em;
            }
            
            .page-title-gradient {
                background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .page-description {
                color: var(--text-secondary);
                font-size: 1.2rem;
                margin-bottom: 30px;
                font-weight: 400;
            }
            
            /* ===== SECTION TITLES ===== */
            .section-title {
                font-size: 1.6rem;
                font-weight: 700;
                margin-bottom: 24px;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .section-title::after {
                content: '';
                flex: 1;
                height: 1px;
                background: linear-gradient(90deg, var(--border-color), transparent);
            }
            
            /* ===== METRIC CARDS - NEUMORPHISM ===== */
            .metric-card-neu {
                background: linear-gradient(145deg, #18181f 0%, #14141a 100%);
                border-radius: 20px;
                padding: 28px;
                box-shadow: var(--neu-shadow-dark), var(--neu-shadow-light);
                border: 1px solid var(--border-color);
                height: 150px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                position: relative;
                overflow: hidden;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .metric-card-neu::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: var(--card-accent, var(--accent-cyan));
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .metric-card-neu:hover {
                transform: translateY(-10px);
                box-shadow: 
                    15px 15px 35px rgba(0, 0, 0, 0.7),
                    -15px -15px 35px rgba(255, 255, 255, 0.04);
            }
            
            .metric-card-neu:hover::before {
                opacity: 1;
            }
            
            .metric-label {
                font-size: 0.75rem;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 2px;
                font-weight: 600;
            }
            
            .metric-value {
                font-size: 2.2rem;
                font-weight: 800;
                font-family: 'JetBrains Mono', monospace;
                margin: 8px 0;
                background: linear-gradient(135deg, var(--value-color, var(--accent-cyan)) 0%, var(--value-color-end, var(--accent-blue)) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .metric-delta {
                font-size: 0.9rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            .metric-delta-positive { color: var(--accent-green); }
            .metric-delta-negative { color: var(--accent-red); }
            
            /* ===== FEATURE CARDS - GLASSMORPHISM ===== */
            .feature-card-glass {
                background: var(--bg-glass);
                backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
                -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
                border-radius: 24px;
                padding: 40px 28px;
                border: 1px solid var(--border-glass);
                text-align: center;
                height: 240px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
                transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .feature-card-glass::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(circle at 50% 0%, var(--card-glow, var(--accent-cyan-glow)) 0%, transparent 60%);
                opacity: 0;
                transition: opacity 0.4s ease;
            }
            
            .feature-card-glass:hover {
                transform: translateY(-12px) scale(1.02);
                border-color: var(--card-border, var(--accent-cyan));
                box-shadow: 
                    0 20px 50px rgba(0, 0, 0, 0.4),
                    0 0 50px var(--card-glow, var(--accent-cyan-glow));
            }
            
            .feature-card-glass:hover::before {
                opacity: 1;
            }
            
            .feature-icon {
                font-size: 4rem;
                margin-bottom: 20px;
                position: relative;
                z-index: 1;
                filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
                transition: transform 0.4s ease;
            }
            
            .feature-card-glass:hover .feature-icon {
                transform: scale(1.15) translateY(-5px);
            }
            
            .feature-title {
                font-size: 1.2rem;
                font-weight: 700;
                color: var(--text-primary);
                margin-bottom: 12px;
                position: relative;
                z-index: 1;
            }
            
            .feature-desc {
                color: var(--text-secondary);
                font-size: 0.95rem;
                line-height: 1.6;
                position: relative;
                z-index: 1;
            }
            
            /* ===== INFO CARDS - GLASSMORPHISM ===== */
            .info-card-glass {
                background: linear-gradient(135deg, 
                    rgba(6, 182, 212, 0.08) 0%, 
                    rgba(59, 130, 246, 0.05) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 24px 28px;
                border: 1px solid rgba(6, 182, 212, 0.2);
                border-left: 4px solid var(--accent-cyan);
                margin: 16px 0;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .info-card-glass::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(6, 182, 212, 0.05), transparent);
                transform: translateX(-100%);
                transition: transform 0.6s ease;
            }
            
            .info-card-glass:hover {
                transform: translateX(8px);
                box-shadow: 0 8px 30px rgba(6, 182, 212, 0.15);
            }
            
            .info-card-glass:hover::before {
                transform: translateX(100%);
            }
            
            .success-card-glass {
                background: linear-gradient(135deg, 
                    rgba(16, 185, 129, 0.08) 0%, 
                    rgba(20, 184, 166, 0.05) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 24px 28px;
                border: 1px solid rgba(16, 185, 129, 0.2);
                border-left: 4px solid var(--accent-green);
                margin: 16px 0;
                color: var(--text-primary);
                transition: all 0.3s ease;
            }
            
            .success-card-glass:hover {
                transform: translateX(8px);
                box-shadow: 0 8px 30px rgba(16, 185, 129, 0.15);
            }
            
            .warning-card-glass {
                background: linear-gradient(135deg, 
                    rgba(245, 158, 11, 0.08) 0%, 
                    rgba(251, 146, 60, 0.05) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 24px 28px;
                border: 1px solid rgba(245, 158, 11, 0.2);
                border-left: 4px solid var(--accent-orange);
                margin: 16px 0;
                color: var(--text-primary);
                transition: all 0.3s ease;
            }
            
            .warning-card-glass:hover {
                transform: translateX(8px);
                box-shadow: 0 8px 30px rgba(245, 158, 11, 0.15);
            }
            
            .error-card-glass {
                background: linear-gradient(135deg, 
                    rgba(239, 68, 68, 0.08) 0%, 
                    rgba(236, 72, 153, 0.05) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 24px 28px;
                border: 1px solid rgba(239, 68, 68, 0.2);
                border-left: 4px solid var(--accent-red);
                margin: 16px 0;
                color: var(--text-primary);
                transition: all 0.3s ease;
            }
            
            .error-card-glass:hover {
                transform: translateX(8px);
                box-shadow: 0 8px 30px rgba(239, 68, 68, 0.15);
            }
            
            /* ===== INSIGHT CARD ===== */
            .insight-card-glass {
                background: linear-gradient(135deg, 
                    rgba(139, 92, 246, 0.08) 0%, 
                    rgba(236, 72, 153, 0.05) 100%);
                backdrop-filter: blur(15px);
                border-radius: 16px;
                padding: 24px 28px;
                border: 1px solid rgba(139, 92, 246, 0.2);
                margin: 16px 0;
                transition: all 0.4s ease;
                position: relative;
                overflow: hidden;
            }
            
            .insight-card-glass::before {
                content: '💡';
                position: absolute;
                top: 15px;
                right: 20px;
                font-size: 1.5rem;
                opacity: 0.4;
            }
            
            .insight-card-glass:hover {
                transform: translateX(8px);
                border-color: rgba(139, 92, 246, 0.4);
                box-shadow: 0 8px 30px rgba(139, 92, 246, 0.15);
            }
            
            .insight-title {
                color: #a78bfa;
                font-weight: 700;
                font-size: 1.05rem;
                margin-bottom: 12px;
            }
            
            .insight-text {
                color: var(--text-primary);
                font-size: 1rem;
                line-height: 1.7;
            }
            
            /* ===== RECOMMENDATION BOX ===== */
            .recommendation-box-glass {
                background: linear-gradient(135deg, 
                    rgba(16, 185, 129, 0.1) 0%, 
                    rgba(6, 182, 212, 0.1) 100%);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 30px 35px;
                border: 2px solid rgba(16, 185, 129, 0.3);
                margin: 24px 0;
                position: relative;
                overflow: hidden;
            }
            
            .recommendation-box-glass::before {
                content: '📋';
                position: absolute;
                top: 20px;
                right: 25px;
                font-size: 2rem;
                opacity: 0.5;
            }
            
            .recommendation-title {
                color: var(--accent-green);
                font-size: 1.3rem;
                font-weight: 700;
                margin-bottom: 16px;
            }
            
            .recommendation-text {
                color: var(--text-primary);
                font-size: 1.05rem;
                line-height: 1.8;
            }
            
            /* ===== TABS - NEUMORPHISM ===== */
            .stTabs [data-baseweb="tab-list"] {
                gap: 12px;
                background: transparent;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                background: linear-gradient(145deg, #18181f 0%, #14141a 100%);
                box-shadow: var(--neu-shadow-dark), var(--neu-shadow-light);
                border-radius: 14px;
                color: var(--text-secondary);
                padding: 14px 28px;
                border: 1px solid var(--border-color);
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .stTabs [data-baseweb="tab"]:hover {
                transform: translateY(-4px);
                box-shadow: 
                    10px 10px 25px rgba(0, 0, 0, 0.6),
                    -10px -10px 25px rgba(255, 255, 255, 0.03);
                border-color: var(--accent-cyan);
                color: var(--accent-cyan);
            }
            
            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%) !important;
                color: white !important;
                border: none !important;
                box-shadow: 
                    0 8px 25px var(--accent-cyan-glow),
                    var(--neu-shadow-dark);
            }
            
            .stTabs [aria-selected="true"]:hover {
                transform: translateY(-4px);
                box-shadow: 
                    0 12px 35px var(--accent-cyan-glow),
                    var(--neu-shadow-dark);
            }
            
            /* ===== BUTTONS - NEUMORPHISM ===== */
            .stButton > button {
                background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
                color: white;
                border: none;
                border-radius: 14px;
                padding: 16px 36px;
                font-weight: 700;
                font-size: 1.05rem;
                letter-spacing: 0.5px;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 
                    0 6px 20px var(--accent-cyan-glow),
                    var(--neu-shadow-dark);
                position: relative;
                overflow: hidden;
            }
            
            .stButton > button::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s ease;
            }
            
            .stButton > button:hover {
                background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
                transform: translateY(-4px) scale(1.02);
                box-shadow: 
                    0 12px 35px var(--accent-blue-glow),
                    var(--neu-shadow-dark);
            }
            
            .stButton > button:hover::before {
                left: 100%;
            }
            
            .stButton > button:active {
                transform: translateY(-2px) scale(1);
                box-shadow: 
                    0 6px 20px var(--accent-blue-glow),
                    var(--neu-inset-dark);
            }
            
            /* ===== DOWNLOAD BUTTON ===== */
            .stDownloadButton > button {
                background: linear-gradient(135deg, var(--accent-green) 0%, var(--accent-teal) 100%);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 600;
                box-shadow: 0 4px 15px var(--accent-green-glow);
            }
            
            .stDownloadButton > button:hover {
                background: linear-gradient(135deg, var(--accent-teal) 0%, var(--accent-cyan) 100%);
                transform: translateY(-3px);
                box-shadow: 0 8px 25px var(--accent-green-glow);
            }
            
            /* ===== SLIDER - NEUMORPHISM ===== */
            .stSlider > div > div > div > div {
                background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple)) !important;
                height: 8px !important;
                border-radius: 4px !important;
            }
            
            .stSlider > div > div > div > div > div {
                background: white !important;
                border: 3px solid var(--accent-cyan) !important;
                box-shadow: 0 2px 10px var(--accent-cyan-glow) !important;
                width: 20px !important;
                height: 20px !important;
            }
            
            /* ===== SELECTBOX - NEUMORPHISM ===== */
            .stSelectbox > div > div {
                background: linear-gradient(145deg, #18181f 0%, #14141a 100%);
                box-shadow: var(--neu-inset-dark), var(--neu-inset-light);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                color: var(--text-primary);
            }
            
            .stSelectbox > div > div:hover {
                border-color: var(--accent-cyan);
            }
            
            /* ===== FILE UPLOADER ===== */
            .stFileUploader > div > div {
                background: var(--bg-glass);
                backdrop-filter: blur(10px);
                border: 2px dashed var(--border-glass);
                border-radius: 16px;
                padding: 40px;
                transition: all 0.3s ease;
            }
            
            .stFileUploader > div > div:hover {
                border-color: var(--accent-cyan);
                background: var(--bg-glass-hover);
            }
            
            /* ===== DATAFRAME ===== */
            .stDataFrame {
                background: var(--bg-glass);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                border: 1px solid var(--border-glass);
                overflow: hidden;
            }
            
            /* ===== THEME TOGGLE SWITCH ===== */
            .theme-toggle-container {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 16px;
                padding: 12px 24px;
                background: linear-gradient(145deg, #18181f 0%, #14141a 100%);
                box-shadow: var(--neu-shadow-dark), var(--neu-shadow-light);
                border-radius: 50px;
                border: 1px solid var(--border-color);
                margin: 20px auto;
                width: fit-content;
            }
            
            .theme-toggle-label {
                font-size: 1.2rem;
                transition: all 0.3s ease;
            }
            
            .theme-toggle-label.active {
                transform: scale(1.2);
            }
            
            /* ===== CHART CONTAINER ===== */
            .chart-container-glass {
                background: var(--bg-glass);
                backdrop-filter: blur(var(--glass-blur));
                border-radius: 20px;
                padding: 24px;
                border: 1px solid var(--border-glass);
                margin: 16px 0;
                transition: all 0.3s ease;
            }
            
            .chart-container-glass:hover {
                border-color: rgba(255, 255, 255, 0.15);
                box-shadow: var(--shadow-lg);
            }
            
            /* ===== FOOTER ===== */
            .footer-glass {
                background: linear-gradient(135deg, 
                    rgba(15, 15, 24, 0.9) 0%, 
                    rgba(18, 18, 26, 0.95) 100%);
                backdrop-filter: blur(20px);
                padding: 40px;
                text-align: center;
                border-top: 1px solid var(--border-glass);
                margin-top: 60px;
                border-radius: 24px 24px 0 0;
                position: relative;
                overflow: hidden;
            }
            
            .footer-glass::before {
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
                background-size: 200% 100%;
                animation: shimmer 4s ease infinite;
            }
            
            .footer-title {
                color: var(--text-primary);
                font-size: 1.3rem;
                font-weight: 700;
                margin-bottom: 12px;
            }
            
            .footer-subtitle {
                color: var(--text-muted);
                font-size: 1rem;
                margin-bottom: 12px;
            }
            
            .footer-names {
                background: linear-gradient(90deg, 
                    var(--accent-cyan), 
                    var(--accent-blue), 
                    var(--accent-purple), 
                    var(--accent-pink));
                background-size: 200% 100%;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 800;
                font-size: 1.2rem;
                animation: shimmer 4s ease infinite;
            }
            
            /* ===== DIVIDER ===== */
            hr {
                border: none;
                height: 1px;
                background: linear-gradient(90deg, 
                    transparent 0%, 
                    var(--border-glass) 20%, 
                    var(--border-glass) 80%, 
                    transparent 100%);
                margin: 40px 0;
            }
            
            /* ===== SCROLLBAR ===== */
            ::-webkit-scrollbar {
                width: 10px;
                height: 10px;
            }
            
            ::-webkit-scrollbar-track {
                background: var(--bg-secondary);
                border-radius: 10px;
            }
            
            ::-webkit-scrollbar-thumb {
                background: linear-gradient(180deg, var(--accent-cyan), var(--accent-purple));
                border-radius: 10px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: linear-gradient(180deg, var(--accent-blue), var(--accent-pink));
            }
            
            /* ===== ANIMATIONS FOR PAGE ELEMENTS ===== */
            .animate-fade-in {
                animation: fadeInUp 0.6s ease-out forwards;
            }
            
            .animate-delay-1 { animation-delay: 0.1s; }
            .animate-delay-2 { animation-delay: 0.2s; }
            .animate-delay-3 { animation-delay: 0.3s; }
            .animate-delay-4 { animation-delay: 0.4s; }
            
            /* ===== 3D LAYER EFFECT ===== */
            .layer-3d {
                transform-style: preserve-3d;
                perspective: 1000px;
            }
            
            .layer-3d-child {
                transform: translateZ(20px);
                transition: transform 0.4s ease;
            }
            
            .layer-3d:hover .layer-3d-child {
                transform: translateZ(40px);
            }
            
        </style>
        """
    else:
        # LIGHT THEME CSS
        css = """
        <style>
            /* ===== IMPORTS ===== */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
            
            /* ===== CSS VARIABLES - LIGHT THEME ===== */
            :root {
                /* Background Colors */
                --bg-primary: #f8fafc;
                --bg-secondary: #f1f5f9;
                --bg-tertiary: #e2e8f0;
                --bg-card: rgba(255, 255, 255, 0.7);
                --bg-card-hover: rgba(255, 255, 255, 0.9);
                --bg-glass: rgba(255, 255, 255, 0.6);
                --bg-glass-hover: rgba(255, 255, 255, 0.8);
                
                /* Accent Colors - Slightly deeper for light mode */
                --accent-cyan: #0891b2;
                --accent-cyan-glow: rgba(8, 145, 178, 0.25);
                --accent-blue: #2563eb;
                --accent-blue-glow: rgba(37, 99, 235, 0.25);
                --accent-purple: #7c3aed;
                --accent-purple-glow: rgba(124, 58, 237, 0.25);
                --accent-pink: #db2777;
                --accent-pink-glow: rgba(219, 39, 119, 0.25);
                --accent-green: #059669;
                --accent-green-glow: rgba(5, 150, 105, 0.25);
                --accent-orange: #d97706;
                --accent-orange-glow: rgba(217, 119, 6, 0.25);
                --accent-red: #dc2626;
                --accent-teal: #0d9488;
                
                /* Text Colors */
                --text-primary: #0f172a;
                --text-secondary: #475569;
                --text-muted: #94a3b8;
                --text-inverse: #f8fafc;
                
                /* Border & Shadow */
                --border-color: rgba(0, 0, 0, 0.08);
                --border-glass: rgba(0, 0, 0, 0.1);
                --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
                --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.12);
                --shadow-lg: 0 8px 40px rgba(0, 0, 0, 0.15);
                --shadow-glow: 0 0 40px rgba(8, 145, 178, 0.1);
                
                /* Neumorphism - Light */
                --neu-shadow-dark: 8px 8px 20px rgba(0, 0, 0, 0.1);
                --neu-shadow-light: -8px -8px 20px rgba(255, 255, 255, 0.9);
                --neu-inset-dark: inset 4px 4px 10px rgba(0, 0, 0, 0.08);
                --neu-inset-light: inset -4px -4px 10px rgba(255, 255, 255, 0.9);
                
                /* Glassmorphism */
                --glass-blur: 20px;
                --glass-saturation: 120%;
            }
            
            /* ===== ANIMATIONS ===== */
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes fadeInScale {
                from { opacity: 0; transform: scale(0.95); }
                to { opacity: 1; transform: scale(1); }
            }
            
            @keyframes pulse-glow {
                0%, 100% { box-shadow: 0 0 20px var(--accent-cyan-glow); }
                50% { box-shadow: 0 0 40px var(--accent-cyan-glow), 0 0 60px var(--accent-blue-glow); }
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                25% { transform: translateY(-8px) rotate(1deg); }
                75% { transform: translateY(-4px) rotate(-1deg); }
            }
            
            @keyframes shimmer {
                0% { background-position: -200% center; }
                100% { background-position: 200% center; }
            }
            
            @keyframes gradient-shift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            /* ===== HIDE STREAMLIT DEFAULTS ===== */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display: none;}
            
            /* ===== MAIN BACKGROUND - LIGHT ===== */
            .stApp {
                background: 
                    radial-gradient(ellipse at 0% 0%, rgba(8, 145, 178, 0.08) 0%, transparent 50%),
                    radial-gradient(ellipse at 100% 0%, rgba(124, 58, 237, 0.08) 0%, transparent 50%),
                    radial-gradient(ellipse at 50% 100%, rgba(219, 39, 119, 0.05) 0%, transparent 50%),
                    linear-gradient(180deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                min-height: 100vh;
                color: var(--text-primary);
            }
            
            /* ===== SIDEBAR - LIGHT GLASSMORPHISM ===== */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, 
                    rgba(248, 250, 252, 0.95) 0%, 
                    rgba(241, 245, 249, 0.98) 50%, 
                    rgba(226, 232, 240, 0.95) 100%);
                backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
                -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
                border-right: 1px solid var(--border-glass);
            }
            
            [data-testid="stSidebar"]::before {
                content: '';
                position: absolute;
                top: 0;
                right: 0;
                width: 2px;
                height: 100%;
                background: linear-gradient(180deg, 
                    var(--accent-cyan), 
                    var(--accent-purple), 
                    var(--accent-pink),
                    var(--accent-cyan));
                background-size: 100% 200%;
                animation: gradient-shift 8s ease infinite;
                opacity: 0.7;
            }
            
            /* ===== GLASSMORPHISM CONTAINERS - LIGHT ===== */
            .glass-container {
                background: var(--bg-glass);
                backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
                -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
                border: 1px solid var(--border-glass);
                border-radius: 24px;
                padding: 30px;
                position: relative;
                overflow: hidden;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .glass-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 1px;
                background: linear-gradient(90deg, 
                    transparent 0%, 
                    rgba(255, 255, 255, 0.8) 50%, 
                    transparent 100%);
            }
            
            .glass-container:hover {
                background: var(--bg-glass-hover);
                border-color: rgba(0, 0, 0, 0.12);
                transform: translateY(-4px);
                box-shadow: var(--shadow-lg), var(--shadow-glow);
            }
            
            /* ===== NEUMORPHISM CARDS - LIGHT ===== */
            .neu-card {
                background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
                border-radius: 20px;
                padding: 24px;
                box-shadow: var(--neu-shadow-dark), var(--neu-shadow-light);
                border: 1px solid var(--border-color);
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }
            
            .neu-card:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 
                    12px 12px 30px rgba(0, 0, 0, 0.12),
                    -12px -12px 30px rgba(255, 255, 255, 1),
                    0 0 40px var(--accent-cyan-glow);
            }
            
            /* ===== HERO SECTION - LIGHT GLASSMORPHISM ===== */
            .hero-glass {
                background: linear-gradient(135deg, 
                    rgba(8, 145, 178, 0.1) 0%, 
                    rgba(124, 58, 237, 0.1) 50%, 
                    rgba(219, 39, 119, 0.1) 100%);
                backdrop-filter: blur(30px) saturate(150%);
                -webkit-backdrop-filter: blur(30px) saturate(150%);
                border-radius: 32px;
                padding: 60px 50px;
                margin-bottom: 40px;
                border: 1px solid rgba(0, 0, 0, 0.08);
                position: relative;
                overflow: hidden;
                animation: fadeInScale 0.8s ease-out;
            }
            
            .hero-glass::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, 
                    var(--accent-cyan), 
                    var(--accent-blue), 
                    var(--accent-purple), 
                    var(--accent-pink));
                background-size: 200% 100%;
                animation: shimmer 3s ease infinite;
            }
            
            /* ===== HERO TITLE - LIGHT ===== */
            .hero-title {
                font-size: 4.5rem;
                font-weight: 900;
                background: linear-gradient(135deg, 
                    #0f172a 0%, 
                    #0891b2 30%, 
                    #7c3aed 60%, 
                    #db2777 100%);
                background-size: 200% 200%;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 20px;
                position: relative;
                z-index: 1;
                line-height: 1.1;
                animation: gradient-shift 6s ease infinite;
            }
            
            .hero-subtitle {
                font-size: 1.4rem;
                color: var(--text-secondary);
                margin-bottom: 30px;
                position: relative;
                z-index: 1;
                line-height: 1.7;
                font-weight: 400;
            }
            
            .hero-badge {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 12px 28px;
                background: linear-gradient(135deg, 
                    rgba(8, 145, 178, 0.15) 0%, 
                    rgba(37, 99, 235, 0.15) 100%);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(8, 145, 178, 0.3);
                border-radius: 50px;
                color: var(--accent-cyan);
                font-size: 0.95rem;
                font-weight: 600;
                margin-right: 12px;
                margin-bottom: 20px;
                transition: all 0.3s ease;
            }
            
            /* ===== PAGE TITLES ===== */
            .page-title {
                font-size: 3rem;
                font-weight: 800;
                margin-bottom: 12px;
                line-height: 1.2;
                letter-spacing: -0.02em;
                color: var(--text-primary);
            }
            
            .page-title-gradient {
                background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .page-description {
                color: var(--text-secondary);
                font-size: 1.2rem;
                margin-bottom: 30px;
                font-weight: 400;
            }
            
            /* ===== SECTION TITLES ===== */
            .section-title {
                font-size: 1.6rem;
                font-weight: 700;
                margin-bottom: 24px;
                color: var(--text-primary);
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .section-title::after {
                content: '';
                flex: 1;
                height: 1px;
                background: linear-gradient(90deg, var(--border-color), transparent);
            }
            
            /* ===== METRIC CARDS - LIGHT NEUMORPHISM ===== */
            .metric-card-neu {
                background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
                border-radius: 20px;
                padding: 28px;
                box-shadow: var(--neu-shadow-dark), var(--neu-shadow-light);
                border: 1px solid var(--border-color);
                height: 150px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                position: relative;
                overflow: hidden;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .metric-card-neu::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: var(--card-accent, var(--accent-cyan));
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .metric-card-neu:hover {
                transform: translateY(-10px);
                box-shadow: 
                    15px 15px 35px rgba(0, 0, 0, 0.12),
                    -15px -15px 35px rgba(255, 255, 255, 1);
            }
            
            .metric-card-neu:hover::before {
                opacity: 1;
            }
            
            .metric-label {
                font-size: 0.75rem;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 2px;
                font-weight: 600;
            }
            
            .metric-value {
                font-size: 2.2rem;
                font-weight: 800;
                font-family: 'JetBrains Mono', monospace;
                margin: 8px 0;
                background: linear-gradient(135deg, var(--value-color, var(--accent-cyan)) 0%, var(--value-color-end, var(--accent-blue)) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .metric-delta {
                font-size: 0.9rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 4px;
            }
            
            .metric-delta-positive { color: var(--accent-green); }
            .metric-delta-negative { color: var(--accent-red); }
            
            /* ===== FEATURE CARDS - LIGHT GLASSMORPHISM ===== */
            .feature-card-glass {
                background: var(--bg-glass);
                backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
                -webkit-backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-saturation));
                border-radius: 24px;
                padding: 40px 28px;
                border: 1px solid var(--border-glass);
                text-align: center;
                height: 240px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
                transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .feature-card-glass:hover {
                transform: translateY(-12px) scale(1.02);
                border-color: var(--card-border, var(--accent-cyan));
                box-shadow: 
                    0 20px 50px rgba(0, 0, 0, 0.1),
                    0 0 50px var(--card-glow, var(--accent-cyan-glow));
            }
            
            .feature-icon {
                font-size: 4rem;
                margin-bottom: 20px;
                position: relative;
                z-index: 1;
                filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
                transition: transform 0.4s ease;
            }
            
            .feature-card-glass:hover .feature-icon {
                transform: scale(1.15) translateY(-5px);
            }
            
            .feature-title {
                font-size: 1.2rem;
                font-weight: 700;
                color: var(--text-primary);
                margin-bottom: 12px;
                position: relative;
                z-index: 1;
            }
            
            .feature-desc {
                color: var(--text-secondary);
                font-size: 0.95rem;
                line-height: 1.6;
                position: relative;
                z-index: 1;
            }
            
            /* ===== INFO CARDS - LIGHT ===== */
            .info-card-glass {
                background: linear-gradient(135deg, 
                    rgba(8, 145, 178, 0.08) 0%, 
                    rgba(37, 99, 235, 0.05) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 24px 28px;
                border: 1px solid rgba(8, 145, 178, 0.2);
                border-left: 4px solid var(--accent-cyan);
                margin: 16px 0;
                transition: all 0.3s ease;
            }
            
            .info-card-glass:hover {
                transform: translateX(8px);
                box-shadow: 0 8px 30px rgba(8, 145, 178, 0.12);
            }
            
            .success-card-glass {
                background: linear-gradient(135deg, 
                    rgba(5, 150, 105, 0.08) 0%, 
                    rgba(13, 148, 136, 0.05) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 24px 28px;
                border: 1px solid rgba(5, 150, 105, 0.2);
                border-left: 4px solid var(--accent-green);
                margin: 16px 0;
                color: var(--text-primary);
                transition: all 0.3s ease;
            }
            
            .success-card-glass:hover {
                transform: translateX(8px);
                box-shadow: 0 8px 30px rgba(5, 150, 105, 0.12);
            }
            
            .warning-card-glass {
                background: linear-gradient(135deg, 
                    rgba(217, 119, 6, 0.08) 0%, 
                    rgba(251, 146, 60, 0.05) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 24px 28px;
                border: 1px solid rgba(217, 119, 6, 0.2);
                border-left: 4px solid var(--accent-orange);
                margin: 16px 0;
                color: var(--text-primary);
                transition: all 0.3s ease;
            }
            
            .warning-card-glass:hover {
                transform: translateX(8px);
                box-shadow: 0 8px 30px rgba(217, 119, 6, 0.12);
            }
            
            .error-card-glass {
                background: linear-gradient(135deg, 
                    rgba(220, 38, 38, 0.08) 0%, 
                    rgba(219, 39, 119, 0.05) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 24px 28px;
                border: 1px solid rgba(220, 38, 38, 0.2);
                border-left: 4px solid var(--accent-red);
                margin: 16px 0;
                color: var(--text-primary);
                transition: all 0.3s ease;
            }
            
            .error-card-glass:hover {
                transform: translateX(8px);
                box-shadow: 0 8px 30px rgba(220, 38, 38, 0.12);
            }
            
            /* ===== INSIGHT CARD - LIGHT ===== */
            .insight-card-glass {
                background: linear-gradient(135deg, 
                    rgba(124, 58, 237, 0.08) 0%, 
                    rgba(219, 39, 119, 0.05) 100%);
                backdrop-filter: blur(15px);
                border-radius: 16px;
                padding: 24px 28px;
                border: 1px solid rgba(124, 58, 237, 0.2);
                margin: 16px 0;
                transition: all 0.4s ease;
                position: relative;
            }
            
            .insight-card-glass::before {
                content: '💡';
                position: absolute;
                top: 15px;
                right: 20px;
                font-size: 1.5rem;
                opacity: 0.4;
            }
            
            .insight-card-glass:hover {
                transform: translateX(8px);
                border-color: rgba(124, 58, 237, 0.4);
                box-shadow: 0 8px 30px rgba(124, 58, 237, 0.12);
            }
            
            .insight-title {
                color: var(--accent-purple);
                font-weight: 700;
                font-size: 1.05rem;
                margin-bottom: 12px;
            }
            
            .insight-text {
                color: var(--text-primary);
                font-size: 1rem;
                line-height: 1.7;
            }
            
            /* ===== RECOMMENDATION BOX - LIGHT ===== */
            .recommendation-box-glass {
                background: linear-gradient(135deg, 
                    rgba(5, 150, 105, 0.1) 0%, 
                    rgba(8, 145, 178, 0.1) 100%);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 30px 35px;
                border: 2px solid rgba(5, 150, 105, 0.3);
                margin: 24px 0;
                position: relative;
            }
            
            .recommendation-box-glass::before {
                content: '📋';
                position: absolute;
                top: 20px;
                right: 25px;
                font-size: 2rem;
                opacity: 0.5;
            }
            
            .recommendation-title {
                color: var(--accent-green);
                font-size: 1.3rem;
                font-weight: 700;
                margin-bottom: 16px;
            }
            
            .recommendation-text {
                color: var(--text-primary);
                font-size: 1.05rem;
                line-height: 1.8;
            }
            
            /* ===== TABS - LIGHT NEUMORPHISM ===== */
            .stTabs [data-baseweb="tab-list"] {
                gap: 12px;
                background: transparent;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
                box-shadow: var(--neu-shadow-dark), var(--neu-shadow-light);
                border-radius: 14px;
                color: var(--text-secondary);
                padding: 14px 28px;
                border: 1px solid var(--border-color);
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .stTabs [data-baseweb="tab"]:hover {
                transform: translateY(-4px);
                box-shadow: 
                    10px 10px 25px rgba(0, 0, 0, 0.1),
                    -10px -10px 25px rgba(255, 255, 255, 0.9);
                border-color: var(--accent-cyan);
                color: var(--accent-cyan);
            }
            
            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%) !important;
                color: white !important;
                border: none !important;
                box-shadow: 
                    0 8px 25px var(--accent-cyan-glow),
                    var(--neu-shadow-dark);
            }
            
            /* ===== BUTTONS - LIGHT ===== */
            .stButton > button {
                background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
                color: white;
                border: none;
                border-radius: 14px;
                padding: 16px 36px;
                font-weight: 700;
                font-size: 1.05rem;
                letter-spacing: 0.5px;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 
                    0 6px 20px var(--accent-cyan-glow),
                    var(--neu-shadow-dark);
            }
            
            .stButton > button:hover {
                background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
                transform: translateY(-4px) scale(1.02);
                box-shadow: 
                    0 12px 35px var(--accent-blue-glow),
                    var(--neu-shadow-dark);
            }
            
            /* ===== DOWNLOAD BUTTON ===== */
            .stDownloadButton > button {
                background: linear-gradient(135deg, var(--accent-green) 0%, var(--accent-teal) 100%);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 600;
                box-shadow: 0 4px 15px var(--accent-green-glow);
            }
            
            .stDownloadButton > button:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px var(--accent-green-glow);
            }
            
            /* ===== SLIDER - LIGHT ===== */
            .stSlider > div > div > div > div {
                background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple)) !important;
                height: 8px !important;
                border-radius: 4px !important;
            }
            
            /* ===== SELECTBOX - LIGHT ===== */
            .stSelectbox > div > div {
                background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
                box-shadow: var(--neu-inset-dark), var(--neu-inset-light);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                color: var(--text-primary);
            }
            
            /* ===== FILE UPLOADER - LIGHT ===== */
            .stFileUploader > div > div {
                background: var(--bg-glass);
                backdrop-filter: blur(10px);
                border: 2px dashed var(--border-glass);
                border-radius: 16px;
                padding: 40px;
            }
            
            .stFileUploader > div > div:hover {
                border-color: var(--accent-cyan);
            }
            
            /* ===== DATAFRAME - LIGHT ===== */
            .stDataFrame {
                background: var(--bg-glass);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                border: 1px solid var(--border-glass);
            }
            
            /* ===== CHART CONTAINER - LIGHT ===== */
            .chart-container-glass {
                background: var(--bg-glass);
                backdrop-filter: blur(var(--glass-blur));
                border-radius: 20px;
                padding: 24px;
                border: 1px solid var(--border-glass);
                margin: 16px 0;
            }
            
            .chart-container-glass:hover {
                border-color: rgba(0, 0, 0, 0.12);
                box-shadow: var(--shadow-lg);
            }
            
            /* ===== FOOTER - LIGHT ===== */
            .footer-glass {
                background: linear-gradient(135deg, 
                    rgba(248, 250, 252, 0.9) 0%, 
                    rgba(241, 245, 249, 0.95) 100%);
                backdrop-filter: blur(20px);
                padding: 40px;
                text-align: center;
                border-top: 1px solid var(--border-glass);
                margin-top: 60px;
                border-radius: 24px 24px 0 0;
                position: relative;
            }
            
            .footer-glass::before {
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
                background-size: 200% 100%;
                animation: shimmer 4s ease infinite;
            }
            
            .footer-title {
                color: var(--text-primary);
                font-size: 1.3rem;
                font-weight: 700;
                margin-bottom: 12px;
            }
            
            .footer-subtitle {
                color: var(--text-muted);
                font-size: 1rem;
                margin-bottom: 12px;
            }
            
            .footer-names {
                background: linear-gradient(90deg, 
                    var(--accent-cyan), 
                    var(--accent-blue), 
                    var(--accent-purple), 
                    var(--accent-pink));
                background-size: 200% 100%;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 800;
                font-size: 1.2rem;
                animation: shimmer 4s ease infinite;
            }
            
            /* ===== DIVIDER ===== */
            hr {
                border: none;
                height: 1px;
                background: linear-gradient(90deg, 
                    transparent 0%, 
                    var(--border-glass) 20%, 
                    var(--border-glass) 80%, 
                    transparent 100%);
                margin: 40px 0;
            }
            
            /* ===== SCROLLBAR - LIGHT ===== */
            ::-webkit-scrollbar {
                width: 10px;
                height: 10px;
            }
            
            ::-webkit-scrollbar-track {
                background: var(--bg-secondary);
                border-radius: 10px;
            }
            
            ::-webkit-scrollbar-thumb {
                background: linear-gradient(180deg, var(--accent-cyan), var(--accent-purple));
                border-radius: 10px;
            }
            
        </style>
        """
    
    return css

# Apply dynamic CSS based on current theme
st.markdown(get_dynamic_css(get_theme()), unsafe_allow_html=True)

# ============================================================================
# PLOTLY CHART STYLING FUNCTION - THEME AWARE
# ============================================================================

def style_plotly_chart(fig, theme=None):
    """Apply theme-aware styling to Plotly charts."""
    if theme is None:
        theme = get_theme()
    
    if theme == 'dark':
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family='Inter, sans-serif',
                color='#e2e8f0',
                size=12
            ),
            title=dict(
                font=dict(size=18, color='#f1f5f9', family='Inter, sans-serif'),
                x=0.02
            ),
            legend=dict(
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(255,255,255,0.1)',
                font=dict(color='#94a3b8')
            ),
            xaxis=dict(
                gridcolor='rgba(255,255,255,0.06)',
                linecolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='#94a3b8'),
                title_font=dict(color='#94a3b8')
            ),
            yaxis=dict(
                gridcolor='rgba(255,255,255,0.06)',
                linecolor='rgba(255,255,255,0.1)',
                tickfont=dict(color='#94a3b8'),
                title_font=dict(color='#94a3b8')
            ),
            margin=dict(l=40, r=40, t=60, b=40),
            hoverlabel=dict(
                bgcolor='rgba(22, 22, 31, 0.95)',
                bordercolor='#06b6d4',
                font=dict(color='#f1f5f9', family='Inter')
            )
        )
    else:
        fig.update_layout(
            template='plotly_white',
            paper_bgcolor='rgba(255,255,255,0)',
            plot_bgcolor='rgba(255,255,255,0)',
            font=dict(
                family='Inter, sans-serif',
                color='#334155',
                size=12
            ),
            title=dict(
                font=dict(size=18, color='#0f172a', family='Inter, sans-serif'),
                x=0.02
            ),
            legend=dict(
                bgcolor='rgba(255,255,255,0)',
                bordercolor='rgba(0,0,0,0.1)',
                font=dict(color='#64748b')
            ),
            xaxis=dict(
                gridcolor='rgba(0,0,0,0.06)',
                linecolor='rgba(0,0,0,0.1)',
                tickfont=dict(color='#64748b'),
                title_font=dict(color='#64748b')
            ),
            yaxis=dict(
                gridcolor='rgba(0,0,0,0.06)',
                linecolor='rgba(0,0,0,0.1)',
                tickfont=dict(color='#64748b'),
                title_font=dict(color='#64748b')
            ),
            margin=dict(l=40, r=40, t=60, b=40),
            hoverlabel=dict(
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='#0891b2',
                font=dict(color='#0f172a', family='Inter')
            )
        )
    
    return fig

# ============================================================================
# HELPER FUNCTIONS FOR UI COMPONENTS
# ============================================================================

def create_metric_card_neu(label, value, delta=None, delta_type="positive", color="cyan"):
    """Create a neumorphic metric card."""
    theme = get_theme()
    
    # Color mappings
    colors = {
        'cyan': ('#06b6d4', '#0891b2') if theme == 'dark' else ('#0891b2', '#06b6d4'),
        'blue': ('#3b82f6', '#2563eb') if theme == 'dark' else ('#2563eb', '#3b82f6'),
        'purple': ('#8b5cf6', '#7c3aed') if theme == 'dark' else ('#7c3aed', '#8b5cf6'),
        'pink': ('#ec4899', '#db2777') if theme == 'dark' else ('#db2777', '#ec4899'),
        'green': ('#10b981', '#059669') if theme == 'dark' else ('#059669', '#10b981'),
        'orange': ('#f59e0b', '#d97706') if theme == 'dark' else ('#d97706', '#f59e0b'),
        'teal': ('#14b8a6', '#0d9488') if theme == 'dark' else ('#0d9488', '#14b8a6'),
    }
    
    accent_color = colors.get(color, colors['cyan'])
    
    delta_html = ""
    if delta:
        delta_icon = "↑" if delta_type == "positive" else "↓"
        delta_class = "metric-delta-positive" if delta_type == "positive" else "metric-delta-negative"
        delta_html = f'<div class="metric-delta {delta_class}">{delta_icon} {delta}</div>'
    else:
        delta_html = '<div style="height: 24px;"></div>'
    
    return f"""
    <div class="metric-card-neu" style="--card-accent: {accent_color[0]};">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="--value-color: {accent_color[0]}; --value-color-end: {accent_color[1]};">{value}</div>
        {delta_html}
    </div>
    """

def create_feature_card_glass(icon, title, description, color="cyan"):
    """Create a glassmorphic feature card."""
    theme = get_theme()
    
    colors = {
        'cyan': ('#06b6d4', 'rgba(6,182,212,0.4)') if theme == 'dark' else ('#0891b2', 'rgba(8,145,178,0.25)'),
        'blue': ('#3b82f6', 'rgba(59,130,246,0.4)') if theme == 'dark' else ('#2563eb', 'rgba(37,99,235,0.25)'),
        'purple': ('#8b5cf6', 'rgba(139,92,246,0.4)') if theme == 'dark' else ('#7c3aed', 'rgba(124,58,237,0.25)'),
        'pink': ('#ec4899', 'rgba(236,72,153,0.4)') if theme == 'dark' else ('#db2777', 'rgba(219,39,119,0.25)'),
    }
    
    accent, glow = colors.get(color, colors['cyan'])
    
    return f"""
    <div class="feature-card-glass" style="--card-border: {accent}; --card-glow: {glow};">
        <div class="feature-icon">{icon}</div>
        <div class="feature-title" style="color: {accent};">{title}</div>
        <div class="feature-desc">{description}</div>
    </div>
    """

def create_info_card_glass(content):
    """Create a glassmorphic info card."""
    return f'<div class="info-card-glass">{content}</div>'

def create_success_card_glass(content):
    """Create a glassmorphic success card."""
    return f'<div class="success-card-glass">✅ {content}</div>'

def create_warning_card_glass(content):
    """Create a glassmorphic warning card."""
    return f'<div class="warning-card-glass">⚠️ {content}</div>'

def create_error_card_glass(content):
    """Create a glassmorphic error card."""
    return f'<div class="error-card-glass">❌ {content}</div>'

def create_insight_card_glass(title, insight_text):
    """Create a glassmorphic insight card."""
    return f"""
    <div class="insight-card-glass">
        <div class="insight-title">{title}</div>
        <div class="insight-text">{insight_text}</div>
    </div>
    """

def create_recommendation_box_glass(title, recommendations):
    """Create a glassmorphic recommendation box."""
    reco_html = "<br>".join([f"• {r}" for r in recommendations])
    return f"""
    <div class="recommendation-box-glass">
        <div class="recommendation-title">{title}</div>
        <div class="recommendation-text">{reco_html}</div>
    </div>
    """

def show_theme_toggle():
    """Display the theme toggle switch in the sidebar."""
    current_theme = get_theme()
    
    st.markdown(f"""
    <div class="theme-toggle-container">
        <span class="theme-toggle-label {'active' if current_theme == 'dark' else ''}">🌙</span>
        <span style="color: var(--text-secondary); font-weight: 600;">Theme</span>
        <span class="theme-toggle-label {'active' if current_theme == 'light' else ''}">☀️</span>
    </div>
    """, unsafe_allow_html=True)

def show_footer():
    """Display the glassmorphic footer."""
    st.markdown("""
    <div class="footer-glass">
        <div class="footer-title">🚀 UAE Promo Pulse Simulator + Data Rescue Dashboard</div>
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
    
    return insights[:5]

def generate_executive_recommendations(kpis, sim_results=None):
    """Generate auto recommendations for Executive view."""
    recommendations = []
    
    margin = kpis.get('profit_margin_pct', 0)
    if margin > 25:
        recommendations.append(f"Strong margin of {margin:.1f}% provides room for aggressive promotional discounts up to 15%.")
    elif margin < 15:
        recommendations.append(f"Current margin of {margin:.1f}% is below target. Consider reducing discount depth or focusing on high-margin categories.")
    
    aov = kpis.get('avg_order_value', 0)
    if aov < 200:
        recommendations.append(f"Average order value (AED {aov:.0f}) is low. Implement bundle offers or minimum cart value promotions.")
    elif aov > 500:
        recommendations.append(f"High AOV of AED {aov:.0f} indicates premium customer base. Focus on loyalty rewards over discounts.")
    
    if sim_results:
        roi = sim_results.get('outputs', {}).get('roi_pct', 0)
        if roi > 50:
            recommendations.append(f"Projected ROI of {roi:.0f}% is excellent. Campaign is recommended for execution.")
        elif roi < 0:
            recommendations.append(f"Negative ROI projected. Consider reducing discount % or narrowing target segment.")
    
    if not recommendations:
        recommendations.append("All metrics within normal range. Proceed with planned promotional strategy.")
    
    return recommendations

def generate_manager_alerts(stockout_risk, kpis, issues_df=None):
    """Generate operational alerts for Manager view."""
    alerts = []
    
    if stockout_risk.get('stockout_risk_pct', 0) > 15:
        alerts.append(f"⚠️ HIGH: {stockout_risk['stockout_risk_pct']:.0f}% of SKUs at stockout risk. Expedite reorders.")
    
    if stockout_risk.get('zero_stock', 0) > 0:
        alerts.append(f"🔴 CRITICAL: {stockout_risk['zero_stock']} items currently out of stock!")
    
    failure_rate = kpis.get('payment_failure_rate_pct', 0)
    if failure_rate > 5:
        alerts.append(f"⚠️ Payment failure rate at {failure_rate:.1f}%. Investigate gateway issues.")
    
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
    # Logo & Title
    st.markdown(f"""
    <div style="text-align: center; margin-top: -20px; padding-bottom: 20px;">
        <div style="font-size: 52px; margin-bottom: 8px;">🛒</div>
        <div style="
            font-size: 28px;
            font-weight: 900;
            background: linear-gradient(135deg, {'#06b6d4' if get_theme() == 'dark' else '#0891b2'}, {'#8b5cf6' if get_theme() == 'dark' else '#7c3aed'}, {'#ec4899' if get_theme() == 'dark' else '#db2777'});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.5px;
        ">Promo Pulse</div>
        <div style="color: {'#94a3b8' if get_theme() == 'dark' else '#64748b'}; font-size: 13px; margin-top: 4px;">UAE Retail Analytics</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== THEME TOGGLE =====
    st.markdown(f'<p style="color: {"#f59e0b" if get_theme() == "dark" else "#d97706"}; font-weight: 600; margin-bottom: 12px; letter-spacing: 1.2px; font-size: 0.85rem;">🎨 THEME</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        theme_label = "🌙 Dark" if get_theme() == 'dark' else "☀️ Light"
        if st.button(theme_label, key='theme_toggle_btn', use_container_width=True):
            toggle_theme()
            st.rerun()
    
    st.markdown("---")
    
    # Navigation
    st.markdown(f'<p style="color: {"#ec4899" if get_theme() == "dark" else "#db2777"}; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📍 NAVIGATION</p>', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📂 Data Upload", "🧹 Data Rescue", "🎯 Simulator", "📊 Dashboard", "🔧 Faculty Test"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Global Filters
    if st.session_state.data_loaded:
        st.markdown(f'<p style="color: {"#06b6d4" if get_theme() == "dark" else "#0891b2"}; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">🎛️ GLOBAL FILTERS</p>', unsafe_allow_html=True)
        
        sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
        stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
        products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
        
        # Date Range
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
        
        # City
        cities = ['All']
        if stores_df is not None and 'city' in stores_df.columns:
            cities += sorted([str(c) for c in stores_df['city'].dropna().unique().tolist()])
        st.selectbox("🏙️ City", cities, key='filter_city')
        
        # Channel
        channels = ['All']
        if stores_df is not None and 'channel' in stores_df.columns:
            channels += sorted([str(c) for c in stores_df['channel'].dropna().unique().tolist()])
        st.selectbox("📱 Channel", channels, key='filter_channel')
        
        # Category
        categories = ['All']
        if products_df is not None and 'category' in products_df.columns:
            categories += sorted([str(c) for c in products_df['category'].dropna().unique().tolist()])
        st.selectbox("📦 Category", categories, key='filter_category')
        
        # Brand
        brands = ['All']
        if products_df is not None and 'brand' in products_df.columns:
            brand_list = [str(b) for b in products_df['brand'].dropna().unique().tolist()]
            brands += sorted(brand_list)[:20]
        st.selectbox("🏷️ Brand", brands, key='filter_brand')
        
        st.markdown("---")
    
    # Status
    st.markdown(f'<p style="color: {"#3b82f6" if get_theme() == "dark" else "#2563eb"}; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📡 STATUS</p>', unsafe_allow_html=True)
    
    data_loaded = st.session_state.data_loaded
    data_cleaned = st.session_state.is_cleaned
    
    status_color_loaded = "#10b981" if data_loaded else "#ef4444"
    status_color_cleaned = "#10b981" if data_cleaned else "#f59e0b" if data_loaded else "#ef4444"
    
    st.markdown(f"""
    <div style="
        background: {'linear-gradient(145deg, #18181f 0%, #14141a 100%)' if get_theme() == 'dark' else 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)'};
        border-radius: 16px;
        padding: 18px;
        border: 1px solid {'rgba(255,255,255,0.08)' if get_theme() == 'dark' else 'rgba(0,0,0,0.08)'};
        box-shadow: {'8px 8px 20px rgba(0,0,0,0.4), -8px -8px 20px rgba(255,255,255,0.02)' if get_theme() == 'dark' else '8px 8px 20px rgba(0,0,0,0.08), -8px -8px 20px rgba(255,255,255,0.9)'};
    ">
        <div style="display: flex; align-items: center; margin: 10px 0;">
            <div style="
                width: 14px; 
                height: 14px; 
                border-radius: 50%; 
                background: {status_color_loaded}; 
                margin-right: 14px;
                box-shadow: 0 0 12px {status_color_loaded};
            "></div>
            <span style="color: {'#e0e0e0' if get_theme() == 'dark' else '#334155'}; font-size: 0.95rem; font-weight: 500;">Data Loaded</span>
        </div>
        <div style="display: flex; align-items: center; margin: 10px 0;">
            <div style="
                width: 14px; 
                height: 14px; 
                border-radius: 50%; 
                background: {status_color_cleaned}; 
                margin-right: 14px;
                box-shadow: 0 0 12px {status_color_cleaned};
            "></div>
            <span style="color: {'#e0e0e0' if get_theme() == 'dark' else '#334155'}; font-size: 0.95rem; font-weight: 500;">Data Cleaned</span>
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
# PAGE: HOME
# ============================================================================

def show_home_page():
    """Display the home page with glassmorphic design."""
    theme = get_theme()
    
    if not st.session_state.data_loaded:
        # Hero Section
        st.markdown(f"""
        <div class="hero-glass">
            <div style="margin-bottom: 24px; position: relative; z-index: 1;">
                <span class="hero-badge">✨ UAE E-Commerce Analytics</span>
                <span class="hero-badge" style="background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(236,72,153,0.2)); border-color: rgba(139,92,246,0.3); color: {'#a78bfa' if theme == 'dark' else '#7c3aed'};">🚀 Premium v3.0</span>
            </div>
            <div class="hero-title">Promo Pulse Simulator</div>
            <p class="hero-subtitle">
                Advanced Data Rescue Toolkit + What-If Campaign Simulation Engine<br>
                Designed for UAE Omnichannel Retailers: Dubai • Abu Dhabi • Sharjah
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature Cards
        st.markdown(f'<p class="section-title" style="color: {"#8b5cf6" if theme == "dark" else "#7c3aed"};">✨ Key Features</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_feature_card_glass("📂", "Data Upload", "Upload and preview your e-commerce CSV files with instant validation", "cyan"), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_feature_card_glass("🧹", "Data Rescue", "Detect & auto-fix 15+ types of data quality issues", "blue"), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_feature_card_glass("🎯", "Simulator", "Run what-if scenarios and forecast campaign ROI", "purple"), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_feature_card_glass("📊", "Dashboard", "Executive & Manager views with real-time KPIs", "pink"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Workflow
        st.markdown(f'<p class="section-title" style="color: {"#14b8a6" if theme == "dark" else "#0d9488"};">🔄 How It Works</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="info-card-glass">
                <h4 style="color: {'#06b6d4' if theme == 'dark' else '#0891b2'}; margin-top: 0; font-size: 1.15rem; font-weight: 700;">📥 Phase 1: Data Rescue Toolkit</h4>
                <ul style="color: {'#94a3b8' if theme == 'dark' else '#64748b'}; margin-bottom: 0; font-size: 0.95rem; line-height: 2;">
                    <li>Upload dirty/raw datasets (CSV)</li>
                    <li>Automatic validation & issue detection</li>
                    <li>Clean data with documented fixes</li>
                    <li>Download issues log & cleaned data</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="info-card-glass" style="border-left-color: {'#8b5cf6' if theme == 'dark' else '#7c3aed'};">
                <h4 style="color: {'#8b5cf6' if theme == 'dark' else '#7c3aed'}; margin-top: 0; font-size: 1.15rem; font-weight: 700;">🎯 Phase 2: Promo Pulse Simulator</h4>
                <ul style="color: {'#94a3b8' if theme == 'dark' else '#64748b'}; margin-bottom: 0; font-size: 0.95rem; line-height: 2;">
                    <li>Set discount %, budget & margin floor</li>
                    <li>Target by city, channel, category</li>
                    <li>See projected ROI & demand lift</li>
                    <li>Constraint violation warnings</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Get Started
        st.markdown(f'<p class="section-title" style="color: {"#f59e0b" if theme == "dark" else "#d97706"};">🚀 Get Started</p>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-card-glass" style="border-left-color: {'#f59e0b' if theme == 'dark' else '#d97706'}; text-align: center;">
            <p style="color: {'#e2e8f0' if theme == 'dark' else '#334155'}; font-size: 1.15rem; margin: 0;">
                👈 Use the sidebar to navigate to <strong style="color: {'#06b6d4' if theme == 'dark' else '#0891b2'};">📂 Data Upload</strong> and load your data files.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # Data loaded view
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 40px; padding: 30px 0;">
            <div style="font-size: 60px; margin-bottom: 15px;">🛒</div>
            <div class="hero-title" style="font-size: 3.5rem;">Promo Pulse Simulator</div>
            <p style="color: {'#94a3b8' if theme == 'dark' else '#64748b'}; font-size: 1.2rem; margin: 0;">Data Rescue + Campaign Simulation Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Status
        st.markdown(f'<p class="section-title" style="color: {"#06b6d4" if theme == "dark" else "#0891b2"};">📡 Current Status</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        products_count = len(st.session_state.raw_products) if st.session_state.raw_products is not None else 0
        stores_count = len(st.session_state.raw_stores) if st.session_state.raw_stores is not None else 0
        sales_count = len(st.session_state.raw_sales) if st.session_state.raw_sales is not None else 0
        inventory_count = len(st.session_state.raw_inventory) if st.session_state.raw_inventory is not None else 0
        
        with col1:
            st.markdown(create_metric_card_neu("Products", f"{products_count:,}", color="cyan"), unsafe_allow_html=True)
        with col2:
            st.markdown(create_metric_card_neu("Stores", f"{stores_count:,}", color="blue"), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card_neu("Sales Records", f"{sales_count:,}", color="purple"), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card_neu("Inventory", f"{inventory_count:,}", color="pink"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.session_state.is_cleaned:
            st.markdown(create_success_card_glass("Data has been cleaned and validated. Ready for simulation and analysis!"), unsafe_allow_html=True)
        else:
            st.markdown(create_warning_card_glass("Data loaded but not yet cleaned. Go to <strong>🧹 Data Rescue</strong> to validate and fix issues."), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Next Steps
        st.markdown(f'<p class="section-title" style="color: {"#8b5cf6" if theme == "dark" else "#7c3aed"};">📋 Next Steps</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            step_status = "✅" if st.session_state.is_cleaned else "⏳"
            st.markdown(f"""
            <div class="info-card-glass">
                <h4 style="color: {'#06b6d4' if theme == 'dark' else '#0891b2'}; margin-top: 0;">{step_status} Step 1: Clean Data</h4>
                <p style="color: {'#94a3b8' if theme == 'dark' else '#64748b'}; margin-bottom: 0;">Go to <strong>🧹 Data Rescue</strong> to validate and fix data quality issues.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            step_status = "✅" if st.session_state.sim_results else "⏳"
            st.markdown(f"""
            <div class="info-card-glass" style="border-left-color: {'#8b5cf6' if theme == 'dark' else '#7c3aed'};">
                <h4 style="color: {'#8b5cf6' if theme == 'dark' else '#7c3aed'}; margin-top: 0;">{step_status} Step 2: Run Simulation</h4>
                <p style="color: {'#94a3b8' if theme == 'dark' else '#64748b'}; margin-bottom: 0;">Go to <strong>🎯 Simulator</strong> to test discount scenarios.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="info-card-glass" style="border-left-color: {'#ec4899' if theme == 'dark' else '#db2777'};">
                <h4 style="color: {'#ec4899' if theme == 'dark' else '#db2777'}; margin-top: 0;">📊 Step 3: View Dashboard</h4>
                <p style="color: {'#94a3b8' if theme == 'dark' else '#64748b'}; margin-bottom: 0;">Go to <strong>📊 Dashboard</strong> for Executive & Manager insights.</p>
            </div>
            """, unsafe_allow_html=True)
    
    show_footer()

# ============================================================================
# PAGE: DATA UPLOAD
# ============================================================================

def show_data_page():
    """Display the data upload page."""
    theme = get_theme()
    
    st.markdown(f'<h1 class="page-title page-title-gradient">📂 Data Upload</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Upload your e-commerce data files or load sample data</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f'<p class="section-title" style="color: {"#3b82f6" if theme == "dark" else "#2563eb"};">📤 Upload Data Files</p>', unsafe_allow_html=True)
    
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
    
    st.markdown(f'<p class="section-title" style="color: {"#8b5cf6" if theme == "dark" else "#7c3aed"};">📦 Or Load Sample Data</p>', unsafe_allow_html=True)
    
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
        st.markdown(f'<p class="section-title" style="color: {"#14b8a6" if theme == "dark" else "#0d9488"};">👀 Data Preview</p>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📦 Products", "🏪 Stores", "🛒 Sales", "📋 Inventory"])
        
        with tab1:
            if st.session_state.raw_products is not None:
                df = st.session_state.raw_products
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(create_metric_card_neu("Rows", f"{len(df):,}", color="cyan"), unsafe_allow_html=True)
                with col2:
                    st.markdown(create_metric_card_neu("Columns", f"{len(df.columns)}", color="blue"), unsafe_allow_html=True)
                with col3:
                    null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
                    st.markdown(create_metric_card_neu("Null %", f"{null_pct:.1f}%", color="orange"), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df.head(100), use_container_width=True)
        
        with tab2:
            if st.session_state.raw_stores is not None:
                df = st.session_state.raw_stores
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(create_metric_card_neu("Rows", f"{len(df):,}", color="cyan"), unsafe_allow_html=True)
                with col2:
                    st.markdown(create_metric_card_neu("Columns", f"{len(df.columns)}", color="blue"), unsafe_allow_html=True)
                with col3:
                    null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
                    st.markdown(create_metric_card_neu("Null %", f"{null_pct:.1f}%", color="orange"), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df.head(100), use_container_width=True)
        
        with tab3:
            if st.session_state.raw_sales is not None:
                df = st.session_state.raw_sales
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(create_metric_card_neu("Rows", f"{len(df):,}", color="cyan"), unsafe_allow_html=True)
                with col2:
                    st.markdown(create_metric_card_neu("Columns", f"{len(df.columns)}", color="blue"), unsafe_allow_html=True)
                with col3:
                    null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
                    st.markdown(create_metric_card_neu("Null %", f"{null_pct:.1f}%", color="orange"), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df.head(100), use_container_width=True)
        
        with tab4:
            if st.session_state.raw_inventory is not None:
                df = st.session_state.raw_inventory
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(create_metric_card_neu("Rows", f"{len(df):,}", color="cyan"), unsafe_allow_html=True)
                with col2:
                    st.markdown(create_metric_card_neu("Columns", f"{len(df.columns)}", color="blue"), unsafe_allow_html=True)
                with col3:
                    null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
                    st.markdown(create_metric_card_neu("Null %", f"{null_pct:.1f}%", color="orange"), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(df.head(100), use_container_width=True)
    
    show_footer()

# ============================================================================
# PAGE: DATA RESCUE (CLEANER)
# ============================================================================

def show_cleaner_page():
    """Display the data rescue page."""
    theme = get_theme()
    
    st.markdown('<h1 class="page-title page-title-gradient" style="background: linear-gradient(135deg, #10b981, #14b8a6);">🧹 Data Rescue Center</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Validate, detect issues, and clean your data automatically</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card_glass("Please load data first. Go to 📂 Data Upload page."), unsafe_allow_html=True)
        show_footer()
        return
    
    # Issue types
    st.markdown(f'<p class="section-title" style="color: {"#06b6d4" if theme == "dark" else "#0891b2"};">🔍 Issues We Detect & Fix</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="info-card-glass">
            <strong style="color: {'#06b6d4' if theme == 'dark' else '#0891b2'};">Data Quality</strong>
            <ul style="color: {'#94a3b8' if theme == 'dark' else '#64748b'}; margin-bottom: 0;">
                <li>Missing values</li>
                <li>Duplicate records</li>
                <li>Null representations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-card-glass" style="border-left-color: {'#8b5cf6' if theme == 'dark' else '#7c3aed'};">
            <strong style="color: {'#8b5cf6' if theme == 'dark' else '#7c3aed'};">Format Issues</strong>
            <ul style="color: {'#94a3b8' if theme == 'dark' else '#64748b'}; margin-bottom: 0;">
                <li>Invalid timestamps</li>
                <li>Inconsistent cities</li>
                <li>Mixed case values</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="info-card-glass" style="border-left-color: {'#ec4899' if theme == 'dark' else '#db2777'};">
            <strong style="color: {'#ec4899' if theme == 'dark' else '#db2777'};">Value Issues</strong>
            <ul style="color: {'#94a3b8' if theme == 'dark' else '#64748b'}; margin-bottom: 0;">
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
        st.markdown(f'<p class="section-title" style="color: {"#3b82f6" if theme == "dark" else "#2563eb"};">📊 Cleaning Results</p>', unsafe_allow_html=True)
        
        stats = st.session_state.cleaner_stats
        
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                before = stats.get('products', {}).get('before', 0)
                after = stats.get('products', {}).get('after', 0)
                delta = f"{before - after} removed" if before > after else "No change"
                delta_type = "negative" if before > after else "positive"
                st.markdown(create_metric_card_neu("Products", f"{after:,}", delta, delta_type, "cyan"), unsafe_allow_html=True)
            
            with col2:
                before = stats.get('stores', {}).get('before', 0)
                after = stats.get('stores', {}).get('after', 0)
                delta = f"{before - after} removed" if before > after else "No change"
                delta_type = "negative" if before > after else "positive"
                st.markdown(create_metric_card_neu("Stores", f"{after:,}", delta, delta_type, "blue"), unsafe_allow_html=True)
            
            with col3:
                before = stats.get('sales', {}).get('before', 0)
                after = stats.get('sales', {}).get('after', 0)
                delta = f"{before - after} removed" if before > after else "No change"
                delta_type = "negative" if before > after else "positive"
                st.markdown(create_metric_card_neu("Sales", f"{after:,}", delta, delta_type, "purple"), unsafe_allow_html=True)
            
            with col4:
                before = stats.get('inventory', {}).get('before', 0)
                after = stats.get('inventory', {}).get('after', 0)
                delta = f"{before - after} removed" if before > after else "No change"
                delta_type = "negative" if before > after else "positive"
                st.markdown(create_metric_card_neu("Inventory", f"{after:,}", delta, delta_type, "pink"), unsafe_allow_html=True)
        
        issues_df = st.session_state.issues_df
        
        if issues_df is not None and len(issues_df) > 0:
            st.markdown("---")
            st.markdown(f'<p class="section-title" style="color: {"#14b8a6" if theme == "dark" else "#0d9488"};">🔍 Issues Detected & Fixed</p>', unsafe_allow_html=True)
            
            st.markdown(create_success_card_glass(f"Total {len(issues_df)} issues detected and fixed automatically!"), unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                issue_counts = issues_df['issue_type'].value_counts().reset_index()
                issue_counts.columns = ['Issue Type', 'Count']
                
                fig = px.bar(issue_counts, x='Count', y='Issue Type', orientation='h',
                           title='Issues by Type', color='Count',
                           color_continuous_scale=['#06b6d4', '#8b5cf6'])
                fig = style_plotly_chart(fig)
                fig.update_layout(coloraxis_showscale=False)
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
                fig = style_plotly_chart(fig)
                fig.update_layout(title='Pareto Chart of Issues')
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown(f'<p class="section-title" style="color: {"#8b5cf6" if theme == "dark" else "#7c3aed"};">📋 Issues Log</p>', unsafe_allow_html=True)
            st.dataframe(issues_df, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                csv_issues = issues_df.to_csv(index=False)
                st.download_button("📥 Download Issues Log (CSV)", csv_issues, "issues.csv", "text/csv")
            
            with col2:
                if st.session_state.clean_sales is not None:
                    csv_sales = st.session_state.clean_sales.to_csv(index=False)
                    st.download_button("📥 Download Cleaned Sales (CSV)", csv_sales, "cleaned_sales.csv", "text/csv")
        else:
            st.markdown(create_success_card_glass("No issues found! Your data is already clean."), unsafe_allow_html=True)
    
    show_footer()

# ============================================================================
# PAGE: SIMULATOR
# ============================================================================

def show_simulator_page():
    """Display the simulator page."""
    theme = get_theme()
    
    st.markdown('<h1 class="page-title page-title-gradient" style="background: linear-gradient(135deg, #8b5cf6, #ec4899);">🎯 Promo Pulse Simulator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Run what-if discount scenarios with budget & margin constraints</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card_glass("Please load data first."), unsafe_allow_html=True)
        show_footer()
        return
    
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    
    st.markdown(f'<p class="section-title" style="color: {"#06b6d4" if theme == "dark" else "#0891b2"};">⚙️ Campaign Parameters</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'<p style="color: {"#06b6d4" if theme == "dark" else "#0891b2"}; font-weight: 600;">💰 Pricing</p>', unsafe_allow_html=True)
        discount_pct = st.slider("Discount %", 0, 50, 15, key='sim_discount')
        promo_budget = st.number_input("Promo Budget (AED)", 1000, 500000, 25000, step=5000, key='sim_budget')
    
    with col2:
        st.markdown(f'<p style="color: {"#8b5cf6" if theme == "dark" else "#7c3aed"}; font-weight: 600;">📊 Constraints</p>', unsafe_allow_html=True)
        margin_floor = st.slider("Margin Floor %", 0, 50, 15, key='sim_margin')
        campaign_days = st.slider("Campaign Days", 1, 30, 7, key='sim_days')
    
    with col3:
        st.markdown(f'<p style="color: {"#ec4899" if theme == "dark" else "#db2777"}; font-weight: 600;">🎯 Targeting</p>', unsafe_allow_html=True)
        
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
        st.markdown(f'<p class="section-title" style="color: {"#14b8a6" if theme == "dark" else "#0d9488"};">📊 Simulation Results</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            delta = f"{comparison.get('revenue_change_pct', 0):+.1f}%"
            delta_type = "positive" if comparison.get('revenue_change_pct', 0) > 0 else "negative"
            st.markdown(create_metric_card_neu("Expected Revenue", f"AED {outputs.get('expected_revenue', 0):,.0f}", delta, delta_type, "cyan"), unsafe_allow_html=True)
        
        with col2:
            delta = f"{comparison.get('profit_change_pct', 0):+.1f}%"
            delta_type = "positive" if comparison.get('profit_change_pct', 0) > 0 else "negative"
            st.markdown(create_metric_card_neu("Net Profit", f"AED {outputs.get('expected_net_profit', 0):,.0f}", delta, delta_type, "green"), unsafe_allow_html=True)
        
        with col3:
            roi = outputs.get('roi_pct', 0)
            color = "green" if roi > 0 else "pink"
            st.markdown(create_metric_card_neu("ROI", f"{roi:.1f}%", color=color), unsafe_allow_html=True)
        
        with col4:
            budget_util = (outputs.get('promo_cost', 0) / promo_budget * 100) if promo_budget > 0 else 0
            st.markdown(create_metric_card_neu("Budget Used", f"{budget_util:.1f}%", color="orange"), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card_neu("Demand Lift", f"+{outputs.get('demand_lift_pct', 0):.1f}%", color="purple"), unsafe_allow_html=True)
        
        with col2:
            margin_result = outputs.get('expected_margin_pct', 0)
            color = "green" if margin_result >= margin_floor else "orange"
            st.markdown(create_metric_card_neu("Exp. Margin", f"{margin_result:.1f}%", color=color), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_metric_card_neu("Promo Cost", f"AED {outputs.get('promo_cost', 0):,.0f}", color="orange"), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_metric_card_neu("Expected Orders", f"{outputs.get('expected_orders', 0):,}", color="blue"), unsafe_allow_html=True)
        
        if constraint_violations:
            st.markdown("---")
            st.markdown(f'<p class="section-title" style="color: {"#f59e0b" if theme == "dark" else "#d97706"};">⚠️ Constraint Violations</p>', unsafe_allow_html=True)
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
        st.markdown(f'<p class="section-title" style="color: {"#3b82f6" if theme == "dark" else "#2563eb"};">📈 Baseline vs Campaign</p>', unsafe_allow_html=True)
        
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
# PAGE: DASHBOARD
# ============================================================================

def show_dashboard_page():
    """Display the dashboard with Executive/Manager toggle."""
    theme = get_theme()
    
    st.markdown('<h1 class="page-title page-title-gradient" style="background: linear-gradient(135deg, #ec4899, #f59e0b);">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.markdown(create_warning_card_glass("Please load data first."), unsafe_allow_html=True)
        show_footer()
        return
    
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
    
    filtered_sales = apply_filters(sales_df, stores_df, products_df)
    
    sim = Simulator()
    kpis = sim.calculate_overall_kpis(filtered_sales, products_df)
    
    if view == "👔 Executive View":
        show_executive_view(filtered_sales, stores_df, products_df, kpis, sim, theme)
    else:
        show_manager_view(filtered_sales, stores_df, products_df, inventory_df, kpis, sim, theme)
    
    show_footer()

def show_executive_view(sales_df, stores_df, products_df, kpis, sim, theme):
    """Executive View: Strategic KPIs, Insights, and Recommendations."""
    
    st.markdown(f'<p class="section-title" style="color: {"#06b6d4" if theme == "dark" else "#0891b2"};">💼 Executive Dashboard</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card_neu("Net Revenue", f"AED {kpis.get('net_revenue', kpis.get('total_revenue', 0)):,.0f}", color="cyan"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card_neu("Gross Margin %", f"{kpis.get('profit_margin_pct', 0):.1f}%", color="green"), unsafe_allow_html=True)
    with col3:
        profit_proxy = kpis.get('total_profit', 0)
        st.markdown(create_metric_card_neu("Profit Proxy", f"AED {profit_proxy:,.0f}", color="purple"), unsafe_allow_html=True)
    with col4:
        budget_util = 0
        if st.session_state.sim_results:
            outputs = st.session_state.sim_results.get('outputs', {})
            budget_util = outputs.get('budget_utilization_pct', 0)
        st.markdown(create_metric_card_neu("Budget Util.", f"{budget_util:.1f}%", color="orange"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card_neu("Total Orders", f"{kpis.get('total_orders', 0):,}", color="blue"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card_neu("Avg Order Value", f"AED {kpis.get('avg_order_value', 0):,.0f}", color="teal"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card_neu("Avg Discount %", f"{kpis.get('avg_discount_pct', 0):.1f}%", color="orange"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card_neu("Return Rate %", f"{kpis.get('return_rate_pct', 0):.1f}%", color="pink"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    city_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'city')
    channel_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'channel')
    cat_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'category')
    
    col1, col2 = st.columns(2)
    
    with col1:
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
        if city_kpis is not None and len(city_kpis) > 0:
            fig = px.bar(city_kpis, x='city', y='revenue', title='🏙️ Revenue by City',
                        color='city', color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6'])
            fig = style_plotly_chart(fig)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No city data available.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if cat_kpis is not None and len(cat_kpis) > 0:
            fig = px.bar(cat_kpis, x='category', y='profit_margin_pct', title='📦 Margin % by Category',
                        color='profit_margin_pct', color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'])
            fig = style_plotly_chart(fig)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available.")
    
    with col2:
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
    
    st.markdown(f'<p class="section-title" style="color: {"#8b5cf6" if theme == "dark" else "#7c3aed"};">💡 Key Business Insights</p>', unsafe_allow_html=True)
    
    insights = generate_insights(kpis, city_kpis, channel_kpis, cat_kpis)
    
    if insights:
        for title, text in insights:
            st.markdown(create_insight_card_glass(title, text), unsafe_allow_html=True)
    else:
        st.markdown(create_info_card_glass("Analyze more data to generate business insights."), unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f'<p class="section-title" style="color: {"#10b981" if theme == "dark" else "#059669"};">📋 Strategic Recommendations</p>', unsafe_allow_html=True)
    
    recommendations = generate_executive_recommendations(kpis, st.session_state.sim_results)
    st.markdown(create_recommendation_box_glass("Action Items for Leadership", recommendations), unsafe_allow_html=True)

def show_manager_view(sales_df, stores_df, products_df, inventory_df, kpis, sim, theme):
    """Manager View: Operational KPIs and risks."""
    
    st.markdown(f'<p class="section-title" style="color: {"#f59e0b" if theme == "dark" else "#d97706"};">⚙️ Operations Dashboard</p>', unsafe_allow_html=True)
    
    stockout = sim.calculate_stockout_risk(inventory_df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        color = "pink" if stockout.get('stockout_risk_pct', 0) > 15 else "green"
        st.markdown(create_metric_card_neu("Stockout Risk %", f"{stockout.get('stockout_risk_pct', 0):.1f}%", color=color), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card_neu("Return Rate %", f"{kpis.get('return_rate_pct', 0):.1f}%", color="orange"), unsafe_allow_html=True)
    with col3:
        failure_rate = kpis.get('payment_failure_rate_pct', 0)
        color = "pink" if failure_rate > 5 else "green"
        st.markdown(create_metric_card_neu("Payment Fail %", f"{failure_rate:.1f}%", color=color), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card_neu("High-Risk SKUs", f"{stockout.get('low_stock_items', 0):,}", color="purple"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
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
        if inventory_df is not None and 'stock_on_hand' in inventory_df.columns:
            fig = px.histogram(inventory_df, x='stock_on_hand', nbins=50, title='📦 Stock Level Distribution',
                             color_discrete_sequence=['#8b5cf6'])
            fig = style_plotly_chart(fig)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
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
    
    st.markdown(f'<p class="section-title" style="color: {"#ec4899" if theme == "dark" else "#db2777"};">🚨 Operational Alerts</p>', unsafe_allow_html=True)
    
    alerts = generate_manager_alerts(stockout, kpis, st.session_state.issues_df)
    
    for alert in alerts:
        if "CRITICAL" in alert or "🔴" in alert:
            st.markdown(create_error_card_glass(alert), unsafe_allow_html=True)
        elif "HIGH" in alert or "⚠️" in alert:
            st.markdown(create_warning_card_glass(alert), unsafe_allow_html=True)
        else:
            st.markdown(create_info_card_glass(alert), unsafe_allow_html=True)

# ============================================================================
# PAGE: FACULTY TEST
# ============================================================================

def show_faculty_test_page():
    """Faculty dataset testing with column mapping."""
    theme = get_theme()
    
    st.markdown('<h1 class="page-title page-title-gradient" style="background: linear-gradient(135deg, #14b8a6, #06b6d4);">🔧 Faculty Dataset Test</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-description">Upload faculty-provided dataset and map columns to expected schema</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f'<p class="section-title" style="color: {"#06b6d4" if theme == "dark" else "#0891b2"};">📤 Upload Faculty Dataset</p>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload CSV/Excel file", type=['csv', 'xlsx'], key='faculty_upload')
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                faculty_df = pd.read_excel(uploaded_file)
            else:
                faculty_df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ File loaded: {len(faculty_df)} rows, {len(faculty_df.columns)} columns")
            
            st.markdown(f'<p class="section-title" style="color: {"#3b82f6" if theme == "dark" else "#2563eb"};">📋 Detected Columns</p>', unsafe_allow_html=True)
            st.write(faculty_df.columns.tolist())
            
            st.markdown("---")
            
            st.markdown(f'<p class="section-title" style="color: {"#8b5cf6" if theme == "dark" else "#7c3aed"};">🔗 Column Mapping</p>', unsafe_allow_html=True)
            st.markdown("Map your dataset columns to the expected schema:")
            
            available_cols = ['-- Not Mapped --'] + faculty_df.columns.tolist()
            
            expected_cols = {
                'Sales': ['order_id', 'order_time', 'product_id', 'store_id', 'qty', 'selling_price_aed', 'discount_pct', 'payment_status', 'return_flag'],
                'Products': ['product_id', 'category', 'brand', 'base_price_aed', 'unit_cost_aed'],
                'Stores': ['store_id', 'city', 'channel', 'fulfillment_type'],
                'Inventory': ['product_id', 'store_id', 'stock_on_hand', 'reorder_point']
            }
            
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
                mapped_df = pd.DataFrame()
                for expected_col, source_col in mappings.items():
                    if source_col != '-- Not Mapped --':
                        mapped_df[expected_col] = faculty_df[source_col]
                    else:
                        mapped_df[expected_col] = None
                
                st.success(f"✅ Mapped {len([v for v in mappings.values() if v != '-- Not Mapped --'])} columns")
                
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
                
                st.markdown(f'<p class="section-title" style="color: {"#10b981" if theme == "dark" else "#059669"};">🔍 Validation Results</p>', unsafe_allow_html=True)
                
                issues = []
                
                for col in mapped_df.columns:
                    null_count = mapped_df[col].isnull().sum()
                    if null_count > 0:
                        issues.append(f"Column '{col}': {null_count} null values ({null_count/len(mapped_df)*100:.1f}%)")
                
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
