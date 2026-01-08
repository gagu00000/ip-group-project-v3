# ============================================================================
# UAE Promo Pulse Simulator + Data Rescue Dashboard
# ULTRA PREMIUM VERSION v4.0 - Full Animation Pack
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
# THEME MANAGEMENT
# ============================================================================

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# Theme colors
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
        'gradient_1': 'rgba(6, 182, 212, 0.08)',
        'gradient_2': 'rgba(139, 92, 246, 0.08)',
        'gradient_3': 'rgba(236, 72, 153, 0.05)',
        'glass_bg': 'rgba(22, 22, 31, 0.7)',
        'glass_border': 'rgba(255, 255, 255, 0.1)',
    },
    'light': {
        'bg_primary': '#f8fafc',
        'bg_secondary': '#ffffff',
        'bg_card': '#ffffff',
        'bg_card_hover': '#f1f5f9',
        'text_primary': '#0f172a',
        'text_secondary': '#475569',
        'text_muted': '#64748b',
        'border_color': '#e2e8f0',
        'gradient_1': 'rgba(6, 182, 212, 0.05)',
        'gradient_2': 'rgba(139, 92, 246, 0.05)',
        'gradient_3': 'rgba(236, 72, 153, 0.03)',
        'glass_bg': 'rgba(255, 255, 255, 0.7)',
        'glass_border': 'rgba(0, 0, 0, 0.1)',
    }
}

current_theme = THEMES[st.session_state.theme]

# ============================================================================
# ULTRA PREMIUM CSS - FULL ANIMATION PACK
# ============================================================================

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* ============================================ */
    /* CSS VARIABLES                                */
    /* ============================================ */
    :root {{
        --bg-primary: {current_theme['bg_primary']};
        --bg-secondary: {current_theme['bg_secondary']};
        --bg-card: {current_theme['bg_card']};
        --bg-card-hover: {current_theme['bg_card_hover']};
        --text-primary: {current_theme['text_primary']};
        --text-secondary: {current_theme['text_secondary']};
        --text-muted: {current_theme['text_muted']};
        --border-color: {current_theme['border_color']};
        --glass-bg: {current_theme['glass_bg']};
        --glass-border: {current_theme['glass_border']};
        
        --accent-cyan: #06b6d4;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-pink: #ec4899;
        --accent-green: #10b981;
        --accent-orange: #f59e0b;
        --accent-red: #ef4444;
        --accent-teal: #14b8a6;
        
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, {'0.1' if st.session_state.theme == 'light' else '0.3'});
        --shadow-md: 0 4px 16px rgba(0, 0, 0, {'0.12' if st.session_state.theme == 'light' else '0.4'});
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, {'0.15' if st.session_state.theme == 'light' else '0.5'});
        --shadow-glow-cyan: 0 0 30px rgba(6, 182, 212, 0.4);
        --shadow-glow-purple: 0 0 30px rgba(139, 92, 246, 0.4);
        --shadow-glow-pink: 0 0 30px rgba(236, 72, 153, 0.4);
    }}
    
    /* ============================================ */
    /* KEYFRAME ANIMATIONS                          */
    /* ============================================ */
    
    /* Fade In Up - Staggered Entry */
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
    
    /* Fade In Scale - Pop Effect */
    @keyframes fadeInScale {{
        0% {{
            opacity: 0;
            transform: scale(0.9);
        }}
        50% {{
            transform: scale(1.02);
        }}
        100% {{
            opacity: 1;
            transform: scale(1);
        }}
    }}
    
    /* Blur to Sharp */
    @keyframes blurToSharp {{
        from {{
            opacity: 0;
            filter: blur(10px);
            transform: translateY(20px);
        }}
        to {{
            opacity: 1;
            filter: blur(0);
            transform: translateY(0);
        }}
    }}
    
    /* Slide In Left */
    @keyframes slideInLeft {{
        from {{
            opacity: 0;
            transform: translateX(-50px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}
    
    /* Slide In Right */
    @keyframes slideInRight {{
        from {{
            opacity: 0;
            transform: translateX(50px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}
    
    /* Pulse Glow */
    @keyframes pulseGlow {{
        0%, 100% {{
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
        }}
        50% {{
            box-shadow: 0 0 40px rgba(6, 182, 212, 0.6), 0 0 60px rgba(139, 92, 246, 0.3);
        }}
    }}
    
    /* Breathing Pulse - Status Dots */
    @keyframes breathe {{
        0%, 100% {{
            transform: scale(1);
            opacity: 1;
        }}
        50% {{
            transform: scale(1.2);
            opacity: 0.7;
        }}
    }}
    
    /* Shimmer Effect */
    @keyframes shimmer {{
        0% {{
            background-position: -1000px 0;
        }}
        100% {{
            background-position: 1000px 0;
        }}
    }}
    
    /* Gradient Flow - Moving Gradient */
    @keyframes gradientFlow {{
        0% {{
            background-position: 0% 50%;
        }}
        50% {{
            background-position: 100% 50%;
        }}
        100% {{
            background-position: 0% 50%;
        }}
    }}
    
    /* Rotating Border Gradient */
    @keyframes rotateBorder {{
        0% {{
            transform: rotate(0deg);
        }}
        100% {{
            transform: rotate(360deg);
        }}
    }}
    
    /* Float Animation */
    @keyframes float {{
        0%, 100% {{
            transform: translateY(0px) rotate(0deg);
        }}
        33% {{
            transform: translateY(-10px) rotate(1deg);
        }}
        66% {{
            transform: translateY(-5px) rotate(-1deg);
        }}
    }}
    
    /* Floating Orbs */
    @keyframes floatOrb {{
        0%, 100% {{
            transform: translate(0, 0) scale(1);
            opacity: 0.3;
        }}
        25% {{
            transform: translate(10px, -20px) scale(1.1);
            opacity: 0.5;
        }}
        50% {{
            transform: translate(-5px, -35px) scale(1);
            opacity: 0.3;
        }}
        75% {{
            transform: translate(-15px, -20px) scale(0.9);
            opacity: 0.4;
        }}
    }}
    
    /* Ripple Effect */
    @keyframes ripple {{
        0% {{
            transform: scale(0);
            opacity: 0.5;
        }}
        100% {{
            transform: scale(4);
            opacity: 0;
        }}
    }}
    
    /* Glitch Effect */
    @keyframes glitch {{
        0%, 90%, 100% {{
            transform: translate(0);
        }}
        91% {{
            transform: translate(-2px, 1px);
        }}
        92% {{
            transform: translate(2px, -1px);
        }}
        93% {{
            transform: translate(-1px, 2px);
        }}
        94% {{
            transform: translate(1px, -2px);
        }}
    }}
    
    /* Typing Cursor */
    @keyframes blink {{
        0%, 100% {{
            opacity: 1;
        }}
        50% {{
            opacity: 0;
        }}
    }}
    
    /* Number Count Up Pulse */
    @keyframes countPulse {{
        0% {{
            transform: scale(1);
        }}
        50% {{
            transform: scale(1.05);
            text-shadow: 0 0 20px currentColor;
        }}
        100% {{
            transform: scale(1);
        }}
    }}
    
    /* Underline Slide */
    @keyframes underlineSlide {{
        from {{
            transform: scaleX(0);
            transform-origin: left;
        }}
        to {{
            transform: scaleX(1);
            transform-origin: left;
        }}
    }}
    
    /* Background Mesh */
    @keyframes meshMove {{
        0%, 100% {{
            transform: translate(0%, 0%) rotate(0deg);
        }}
        25% {{
            transform: translate(5%, 5%) rotate(90deg);
        }}
        50% {{
            transform: translate(0%, 10%) rotate(180deg);
        }}
        75% {{
            transform: translate(-5%, 5%) rotate(270deg);
        }}
    }}
    
    /* Shake Animation */
    @keyframes shake {{
        0%, 100% {{ transform: translateX(0); }}
        10%, 30%, 50%, 70%, 90% {{ transform: translateX(-5px); }}
        20%, 40%, 60%, 80% {{ transform: translateX(5px); }}
    }}
    
    /* ============================================ */
    /* HIDE DEFAULTS                                */
    /* ============================================ */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* ============================================ */
    /* GLOBAL TRANSITIONS FOR THEME TOGGLE          */
    /* ============================================ */
    *, *::before, *::after {{
        transition: background-color 0.4s ease, 
                    border-color 0.4s ease, 
                    color 0.3s ease,
                    box-shadow 0.3s ease;
    }}
    
    /* ============================================ */
    /* MAIN BACKGROUND WITH ANIMATED GRADIENT       */
    /* ============================================ */
    .stApp {{
        background: var(--bg-primary);
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }}
    
    /* Animated Background Gradient Overlay */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(ellipse at 20% 20%, rgba(6, 182, 212, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 40% 60%, rgba(236, 72, 153, 0.05) 0%, transparent 50%);
        background-size: 200% 200%;
        animation: gradientFlow 15s ease infinite;
        pointer-events: none;
        z-index: 0;
    }}
    
    /* Grain/Noise Texture Overlay */
    .stApp::after {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
        opacity: {'0.02' if st.session_state.theme == 'dark' else '0.015'};
        pointer-events: none;
        z-index: 0;
    }}
    
    /* ============================================ */
    /* FLOATING ORBS BACKGROUND                     */
    /* ============================================ */
    .floating-orbs {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        pointer-events: none;
        z-index: 0;
    }}
    
    .orb {{
        position: absolute;
        border-radius: 50%;
        filter: blur(40px);
        animation: floatOrb 20s ease-in-out infinite;
    }}
    
    .orb-1 {{
        width: 300px;
        height: 300px;
        background: rgba(6, 182, 212, 0.15);
        top: 10%;
        left: 10%;
        animation-delay: 0s;
    }}
    
    .orb-2 {{
        width: 400px;
        height: 400px;
        background: rgba(139, 92, 246, 0.12);
        top: 50%;
        right: 10%;
        animation-delay: -5s;
    }}
    
    .orb-3 {{
        width: 250px;
        height: 250px;
        background: rgba(236, 72, 153, 0.1);
        bottom: 10%;
        left: 30%;
        animation-delay: -10s;
    }}
    
    /* ============================================ */
    /* SIDEBAR WITH GLASSMORPHISM                   */
    /* ============================================ */
    [data-testid="stSidebar"] {{
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid var(--glass-border);
        animation: slideInLeft 0.6s ease-out;
    }}
    
    [data-testid="stSidebar"]::before {{
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 3px;
        height: 100%;
        background: linear-gradient(180deg, var(--accent-cyan), var(--accent-purple), var(--accent-pink), var(--accent-cyan));
        background-size: 100% 300%;
        animation: gradientFlow 5s ease infinite;
    }}
    
    /* ============================================ */
    /* PREMIUM CONTAINER WITH GLASSMORPHISM         */
    /* ============================================ */
    .premium-container {{
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 32px;
        margin: 24px 0;
        border: 1px solid var(--glass-border);
        box-shadow: var(--shadow-md);
        position: relative;
        z-index: 1;
        animation: fadeInUp 0.6s ease-out backwards;
    }}
    
    .premium-container:hover {{
        box-shadow: var(--shadow-lg), var(--shadow-glow-cyan);
        transform: translateY(-4px);
        border-color: rgba(6, 182, 212, 0.3);
    }}
    
    /* ============================================ */
    /* HERO SECTION WITH ANIMATIONS                 */
    /* ============================================ */
    .hero-premium {{
        background: linear-gradient(135deg, 
            {current_theme['gradient_1']} 0%, 
            {current_theme['gradient_2']} 50%, 
            {current_theme['gradient_3']} 100%);
        backdrop-filter: blur(20px);
        border-radius: 28px;
        padding: 64px 48px;
        margin-bottom: 48px;
        border: 1px solid var(--glass-border);
        position: relative;
        overflow: hidden;
        animation: blurToSharp 1s ease-out;
        z-index: 1;
    }}
    
    .hero-premium::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 50%);
        animation: float 10s ease-in-out infinite;
    }}
    
    .hero-premium::after {{
        content: '';
        position: absolute;
        bottom: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.12) 0%, transparent 50%);
        animation: float 12s ease-in-out infinite reverse;
    }}
    
    /* Animated Gradient Title */
    .hero-title-premium {{
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 25%, #8b5cf6 50%, #ec4899 75%, #06b6d4 100%);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 24px;
        position: relative;
        z-index: 1;
        line-height: 1.1;
        letter-spacing: -2px;
        animation: gradientFlow 4s ease infinite, fadeInUp 0.8s ease-out;
    }}
    
    /* Subtle Glitch on Hover */
    .hero-title-premium:hover {{
        animation: gradientFlow 4s ease infinite, glitch 0.3s ease;
    }}
    
    /* ============================================ */
    /* METRIC CARDS - ULTRA PREMIUM                 */
    /* ============================================ */
    .metric-card-premium {{
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        padding: 18px 16px;
        border: 1px solid var(--glass-border);
        box-shadow: var(--shadow-sm);
        min-height: 130px;
        max-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
        z-index: 1;
        
        /* Staggered animation - use inline style for delay */
        animation: fadeInScale 0.5s ease-out backwards;
        
        /* 3D Transform Setup */
        transform-style: preserve-3d;
        perspective: 1000px;
    }}
    
    /* Animated Border Gradient */
    .metric-card-premium::before {{
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple), var(--accent-pink), var(--accent-cyan));
        background-size: 400% 400%;
        border-radius: 18px;
        z-index: -1;
        opacity: 0;
        transition: opacity 0.4s ease;
        animation: gradientFlow 3s ease infinite;
    }}
    
    /* Shimmer Effect Overlay */
    .metric-card-premium::after {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.1),
            transparent
        );
        transition: left 0.6s ease;
    }}
    
    .metric-card-premium:hover {{
        transform: translateY(-8px) rotateX(5deg) rotateY(-5deg);
        box-shadow: var(--shadow-lg), var(--shadow-glow-cyan);
        border-color: transparent;
    }}
    
    .metric-card-premium:hover::before {{
        opacity: 1;
    }}
    
    .metric-card-premium:hover::after {{
        left: 100%;
    }}
    
    .metric-label-premium {{
        font-size: 0.65rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 700;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    
    /* Value with shimmer on hover */
    .metric-value-premium {{
        font-size: 1.4rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        margin: 6px 0;
        line-height: 1.3;
        word-wrap: break-word;
        overflow-wrap: break-word;
        position: relative;
    }}
    
    /* Number pulse animation on load */
    .metric-value-premium.animate {{
        animation: countPulse 0.6s ease-out;
    }}
    
    .metric-delta {{
        font-size: 0.75rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 4px;
        margin-top: 4px;
    }}
    
    /* Delta arrow animation */
    .metric-delta .arrow {{
        display: inline-block;
        animation: float 2s ease-in-out infinite;
    }}
    
    /* Responsive */
    @media (max-width: 1400px) {{
        .metric-value-premium {{ font-size: 1.25rem; }}
        .metric-label-premium {{ font-size: 0.6rem; }}
    }}
    
    @media (max-width: 1200px) {{
        .metric-value-premium {{ font-size: 1.1rem; }}
    }}
    
    /* ============================================ */
    /* STATUS INDICATORS - BREATHING DOTS           */
    /* ============================================ */
    .status-dot {{
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        animation: breathe 2s ease-in-out infinite;
        box-shadow: 0 0 10px currentColor;
    }}
    
    .status-dot.green {{
        background: var(--accent-green);
        color: var(--accent-green);
    }}
    
    .status-dot.red {{
        background: var(--accent-red);
        color: var(--accent-red);
    }}
    
    .status-dot.orange {{
        background: var(--accent-orange);
        color: var(--accent-orange);
    }}
    
    /* ============================================ */
    /* PAGE TITLES WITH ANIMATIONS                  */
    /* ============================================ */
    .page-title-premium {{
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 16px;
        line-height: 1.1;
        letter-spacing: -1.5px;
        color: var(--text-primary);
        animation: blurToSharp 0.8s ease-out;
        position: relative;
        z-index: 1;
    }}
    
    .section-title-premium {{
        font-size: 1.8rem;
        font-weight: 700;
        margin: 32px 0 20px 0;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 12px;
        animation: slideInLeft 0.6s ease-out backwards;
        position: relative;
        z-index: 1;
    }}
    
    .section-title-premium::after {{
        content: '';
        flex: 1;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple), transparent);
        background-size: 200% 100%;
        animation: gradientFlow 3s ease infinite;
    }}
    
    /* ============================================ */
    /* INSIGHT CARDS WITH HOVER EFFECTS             */
    /* ============================================ */
    .insight-premium {{
        background: linear-gradient(135deg, 
            rgba(139, 92, 246, {'0.08' if st.session_state.theme == 'dark' else '0.05'}) 0%, 
            rgba(236, 72, 153, {'0.08' if st.session_state.theme == 'dark' else '0.05'}) 100%);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        margin: 16px 0;
        position: relative;
        overflow: hidden;
        z-index: 1;
        animation: fadeInUp 0.6s ease-out backwards;
    }}
    
    .insight-premium::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.1), transparent);
        transition: left 0.5s ease;
    }}
    
    .insight-premium:hover {{
        transform: translateX(8px);
        border-color: var(--accent-purple);
        box-shadow: var(--shadow-glow-purple);
    }}
    
    .insight-premium:hover::before {{
        left: 100%;
    }}
    
    .insight-title-premium {{
        color: var(--accent-purple);
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    .insight-text-premium {{
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.7;
    }}
    
    /* ============================================ */
    /* RECOMMENDATION BOX                           */
    /* ============================================ */
    .recommendation-premium {{
        background: linear-gradient(135deg, 
            rgba(16, 185, 129, {'0.12' if st.session_state.theme == 'dark' else '0.08'}) 0%, 
            rgba(6, 182, 212, {'0.12' if st.session_state.theme == 'dark' else '0.08'}) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 32px;
        border: 2px solid rgba(16, 185, 129, 0.3);
        margin: 24px 0;
        position: relative;
        overflow: hidden;
        z-index: 1;
        animation: fadeInScale 0.7s ease-out backwards;
    }}
    
    .recommendation-premium::before {{
        content: '💡';
        position: absolute;
        top: 20px;
        right: 20px;
        font-size: 3rem;
        opacity: 0.2;
        animation: float 4s ease-in-out infinite;
    }}
    
    .recommendation-premium:hover {{
        border-color: var(--accent-green);
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.25);
    }}
    
    /* ============================================ */
    /* CHART CONTAINER                              */
    /* ============================================ */
    .chart-container {{
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
        border: 1px solid var(--glass-border);
        box-shadow: var(--shadow-sm);
        position: relative;
        z-index: 1;
        animation: fadeInUp 0.6s ease-out backwards;
    }}
    
    .chart-container:hover {{
        box-shadow: var(--shadow-md);
        border-color: rgba(6, 182, 212, 0.2);
    }}
    
    /* ============================================ */
    /* TABS WITH ANIMATIONS                         */
    /* ============================================ */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        background: transparent;
        border-bottom: 2px solid var(--border-color);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 12px 12px 0 0;
        color: var(--text-secondary);
        padding: 14px 28px;
        border: 1px solid var(--glass-border);
        border-bottom: none;
        font-weight: 600;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }}
    
    /* Underline slide effect */
    .stTabs [data-baseweb="tab"]::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: var(--bg-card-hover);
        transform: translateY(-3px);
    }}
    
    .stTabs [data-baseweb="tab"]:hover::after {{
        transform: scaleX(1);
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
        animation: fadeInScale 0.3s ease-out;
    }}
    
    /* ============================================ */
    /* BUTTONS WITH RIPPLE EFFECT                   */
    /* ============================================ */
    .stButton > button {{
        background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-blue) 100%);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 16px 36px;
        font-weight: 700;
        font-size: 1.05rem;
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.3);
        letter-spacing: 0.5px;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        z-index: 1;
    }}
    
    .stButton > button::before {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.6s ease, height 0.6s ease;
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
        box-shadow: 0 12px 36px rgba(59, 130, 246, 0.5);
        transform: translateY(-3px);
    }}
    
    .stButton > button:hover::before {{
        width: 300px;
        height: 300px;
    }}
    
    .stButton > button:active {{
        transform: translateY(-1px);
    }}
    
    /* Download Button */
    .stDownloadButton > button {{
        background: linear-gradient(135deg, var(--accent-green) 0%, var(--accent-teal) 100%);
        color: white;
        border: none;
        border-radius: 12px;
        position: relative;
        overflow: hidden;
    }}
    
    .stDownloadButton > button:hover {{
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
        transform: translateY(-2px);
    }}
    
    /* ============================================ */
    /* ALERTS WITH ANIMATIONS                       */
    /* ============================================ */
    .alert-info {{
        background: linear-gradient(135deg, 
            rgba(6, 182, 212, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 0%, 
            rgba(59, 130, 246, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 100%);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid var(--accent-cyan);
        margin: 16px 0;
        color: var(--text-primary);
        animation: slideInLeft 0.5s ease-out backwards;
        position: relative;
        z-index: 1;
    }}
    
    .alert-success {{
        background: linear-gradient(135deg, 
            rgba(16, 185, 129, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 0%, 
            rgba(20, 184, 166, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 100%);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid var(--accent-green);
        margin: 16px 0;
        color: var(--text-primary);
        animation: slideInLeft 0.5s ease-out backwards;
        position: relative;
        z-index: 1;
    }}
    
    .alert-warning {{
        background: linear-gradient(135deg, 
            rgba(245, 158, 11, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 0%, 
            rgba(251, 146, 60, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 100%);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid var(--accent-orange);
        margin: 16px 0;
        color: var(--text-primary);
        animation: slideInLeft 0.5s ease-out backwards, shake 0.5s ease-out 0.5s;
        position: relative;
        z-index: 1;
    }}
    
    .alert-error {{
        background: linear-gradient(135deg, 
            rgba(239, 68, 68, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 0%, 
            rgba(236, 72, 153, {'0.1' if st.session_state.theme == 'dark' else '0.08'}) 100%);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid var(--accent-red);
        margin: 16px 0;
        color: var(--text-primary);
        animation: slideInLeft 0.5s ease-out backwards, shake 0.5s ease-out 0.3s;
        position: relative;
        z-index: 1;
    }}
    
    /* ============================================ */
    /* DATAFRAME                                    */
    /* ============================================ */
    .stDataFrame {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--glass-border);
        animation: fadeInUp 0.6s ease-out backwards;
    }}
    
    /* ============================================ */
    /* DIVIDER                                      */
    /* ============================================ */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-cyan), var(--accent-purple), transparent);
        margin: 40px 0;
        animation: gradientFlow 4s ease infinite;
        background-size: 200% 100%;
    }}
    
    /* ============================================ */
    /* FOOTER WITH GRADIENT BORDER                  */
    /* ============================================ */
    .footer-premium {{
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        padding: 48px;
        text-align: center;
        border-top: 1px solid var(--glass-border);
        margin-top: 80px;
        border-radius: 28px 28px 0 0;
        position: relative;
        z-index: 1;
        animation: fadeInUp 0.8s ease-out backwards;
    }}
    
    .footer-premium::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple), var(--accent-pink), var(--accent-cyan));
        background-size: 200% 100%;
        animation: gradientFlow 3s ease infinite;
    }}
    
    /* ============================================ */
    /* EXPANDER                                     */
    /* ============================================ */
    .streamlit-expanderHeader {{
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }}
    
    .streamlit-expanderHeader:hover {{
        background: var(--bg-card-hover) !important;
    }}
    
    /* ============================================ */
    /* SELECTBOX & INPUTS                           */
    /* ============================================ */
    .stSelectbox > div > div {{
        background-color: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-color: var(--glass-border);
        border-radius: 10px;
        transition: all 0.3s ease;
    }}
    
    .stSelectbox > div > div:hover {{
        border-color: var(--accent-cyan);
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.2);
    }}
    
    /* ============================================ */
    /* SLIDER                                       */
    /* ============================================ */
    .stSlider > div > div > div > div {{
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple)) !important;
        background-size: 200% 100%;
        animation: gradientFlow 3s ease infinite;
    }}
    
    /* ============================================ */
    /* NAVIGATION LINKS WITH UNDERLINE ANIMATION    */
    /* ============================================ */
    .nav-link {{
        position: relative;
        text-decoration: none;
        color: var(--text-secondary);
        padding: 8px 0;
        transition: color 0.3s ease;
    }}
    
    .nav-link::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
        transform: scaleX(0);
        transform-origin: right;
        transition: transform 0.3s ease;
    }}
    
    .nav-link:hover {{
        color: var(--accent-cyan);
    }}
    
    .nav-link:hover::after {{
        transform: scaleX(1);
        transform-origin: left;
    }}
    
    /* ============================================ */
    /* STAGGERED ANIMATION DELAYS                   */
    /* ============================================ */
    .stagger-1 {{ animation-delay: 0.1s !important; }}
    .stagger-2 {{ animation-delay: 0.2s !important; }}
    .stagger-3 {{ animation-delay: 0.3s !important; }}
    .stagger-4 {{ animation-delay: 0.4s !important; }}
    .stagger-5 {{ animation-delay: 0.5s !important; }}
    .stagger-6 {{ animation-delay: 0.6s !important; }}
    .stagger-7 {{ animation-delay: 0.7s !important; }}
    .stagger-8 {{ animation-delay: 0.8s !important; }}
    
    /* ============================================ */
    /* LOADING SPINNER CUSTOM                       */
    /* ============================================ */
    .custom-spinner {{
        width: 40px;
        height: 40px;
        border: 3px solid var(--glass-border);
        border-top: 3px solid var(--accent-cyan);
        border-radius: 50%;
        animation: rotateBorder 1s linear infinite;
    }}
    
    /* ============================================ */
    /* TOOLTIP ANIMATIONS                           */
    /* ============================================ */
    [data-tooltip] {{
        position: relative;
    }}
    
    [data-tooltip]::after {{
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%) translateY(10px);
        padding: 8px 12px;
        background: var(--bg-card);
        color: var(--text-primary);
        border-radius: 8px;
        font-size: 0.8rem;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
    }}
    
    [data-tooltip]:hover::after {{
        opacity: 1;
        visibility: visible;
        transform: translateX(-50%) translateY(0);
    }}
    
    /* ============================================ */
    /* PROGRESS BAR ANIMATION                       */
    /* ============================================ */
    .progress-bar {{
        height: 8px;
        background: var(--border-color);
        border-radius: 4px;
        overflow: hidden;
    }}
    
    .progress-bar-fill {{
        height: 100%;
        background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
        background-size: 200% 100%;
        animation: gradientFlow 2s ease infinite;
        transition: width 0.5s ease;
    }}
    
    /* ============================================ */
    /* FEATURE CARD HOVER 3D                        */
    /* ============================================ */
    .feature-card {{
        transform-style: preserve-3d;
        perspective: 1000px;
        transition: transform 0.5s ease;
    }}
    
    .feature-card:hover {{
        transform: rotateY(10deg) rotateX(5deg) translateZ(20px);
    }}
    
    /* ============================================ */
    /* REFLECTION EFFECT                            */
    /* ============================================ */
    .reflection {{
        position: relative;
    }}
    
    .reflection::after {{
        content: '';
        position: absolute;
        bottom: -50%;
        left: 0;
        right: 0;
        height: 50%;
        background: linear-gradient(to bottom, 
            rgba(var(--bg-card), 0.3), 
            transparent);
        transform: scaleY(-1);
        opacity: 0.3;
        filter: blur(5px);
        pointer-events: none;
    }}
</style>

<!-- Floating Orbs Background -->
<div class="floating-orbs">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
</div>
""", unsafe_allow_html=True)

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
# HELPER FUNCTIONS - NUMBER FORMATTING
# ============================================================================

def format_currency(value, prefix="AED "):
    """Format large currency values with K/M suffix."""
    try:
        value = float(value)
        if value >= 1_000_000:
            return f"{prefix}{value/1_000_000:.2f}M"
        elif value >= 100_000:
            return f"{prefix}{value/1_000:.0f}K"
        elif value >= 10_000:
            return f"{prefix}{value/1_000:.1f}K"
        else:
            return f"{prefix}{value:,.0f}"
    except:
        return f"{prefix}0"

def format_number(value):
    """Format numbers with K/M suffix."""
    try:
        value = float(value)
        if value >= 1_000_000:
            return f"{value/1_000_000:.2f}M"
        elif value >= 100_000:
            return f"{value/1_000:.0f}K"
        elif value >= 10_000:
            return f"{value/1_000:.1f}K"
        else:
            return f"{value:,.0f}"
    except:
        return "0"

def format_percentage(value):
    """Format percentage values."""
    try:
        value = float(value)
        return f"{value:.1f}%"
    except:
        return "0%"

# ============================================================================
# HELPER FUNCTIONS - UI COMPONENTS WITH STAGGERED ANIMATION
# ============================================================================

def create_metric_card_premium(label, value, delta=None, delta_type="positive", color="cyan", stagger=1):
    """Create premium metric card with staggered animation."""
    colors = {
        'cyan': '#06b6d4', 'blue': '#3b82f6', 'purple': '#8b5cf6',
        'pink': '#ec4899', 'green': '#10b981', 'orange': '#f59e0b',
        'teal': '#14b8a6', 'red': '#ef4444'
    }
    accent = colors.get(color, '#06b6d4')
    
    delta_html = ""
    if delta:
        delta_color = "#10b981" if delta_type == "positive" else "#ef4444"
        delta_icon = "↑" if delta_type == "positive" else "↓"
        delta_html = f'<div class="metric-delta"><span class="arrow" style="color: {delta_color};">{delta_icon}</span> <span style="color: {delta_color};">{delta}</span></div>'
    else:
        delta_html = '<div style="height: 18px;"></div>'
    
    display_label = label[:14] + ".." if len(label) > 14 else label
    
    return f"""
    <div class="metric-card-premium stagger-{stagger}" style="animation-delay: {stagger * 0.1}s;">
        <div class="metric-label-premium" title="{label}">{display_label}</div>
        <div class="metric-value-premium animate" style="color: {accent};">{value}</div>
        {delta_html}
    </div>
    """

def create_insight_card_premium(title, text, stagger=1):
    """Create premium insight card with animation."""
    return f"""
    <div class="insight-premium stagger-{stagger}" style="animation-delay: {stagger * 0.15}s;">
        <div class="insight-title-premium">💡 {title}</div>
        <div class="insight-text-premium">{text}</div>
    </div>
    """

def create_recommendation_premium(title, items):
    """Create premium recommendation box."""
    items_html = "<br>".join([f"• {item}" for item in items])
    return f"""
    <div class="recommendation-premium">
        <div style="color: #10b981; font-size: 1.4rem; font-weight: 800; margin-bottom: 16px;">📋 {title}</div>
        <div style="color: var(--text-secondary); font-size: 1.05rem; line-height: 1.9;">{items_html}</div>
    </div>
    """

def create_feature_card(icon, title, desc, color, stagger=1):
    """Create animated feature card."""
    return f"""
    <div class="premium-container feature-card stagger-{stagger}" style="height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; animation-delay: {stagger * 0.15}s;">
        <div style="font-size: 48px; margin-bottom: 12px; animation: float 3s ease-in-out infinite; animation-delay: {stagger * 0.2}s;">{icon}</div>
        <div style="color: var(--accent-{color}); font-size: 1.1rem; font-weight: 700; margin-bottom: 8px;">{title}</div>
        <div style="color: var(--text-secondary); font-size: 0.85rem;">{desc}</div>
    </div>
    """

def get_plotly_template():
    """Get Plotly template based on theme."""
    return 'plotly_dark' if st.session_state.theme == 'dark' else 'plotly_white'

def style_plotly_chart_themed(fig):
    """Style Plotly chart for current theme."""
    bg_color = 'rgba(22, 22, 31, 0.5)' if st.session_state.theme == 'dark' else 'rgba(255, 255, 255, 0.5)'
    text_color = current_theme['text_primary']
    grid_color = current_theme['border_color']
    
    fig.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color, family='Inter'),
        xaxis=dict(gridcolor=grid_color, linecolor=grid_color),
        yaxis=dict(gridcolor=grid_color, linecolor=grid_color),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(font=dict(color=text_color))
    )
    return fig

def show_footer():
    """Premium footer with animations."""
    st.markdown("""
    <div class="footer-premium">
        <div style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 12px;">
            🚀 UAE Promo Pulse Simulator - Premium Analytics Platform
        </div>
        <div style="color: var(--text-muted); font-size: 1rem; margin-bottom: 16px;">
            Advanced Data Rescue & Campaign Simulation
        </div>
        <div style="
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-purple), var(--accent-pink));
            background-size: 300% 100%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
            font-size: 1.15rem;
            animation: gradientFlow 4s ease infinite;
        ">Kartik Joshi • Gagandeep Singh • Samuel Alex • Prem Kukreja</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# ADVANCED EDA FUNCTIONS
# ============================================================================

def create_customer_cohort_analysis(sales_df):
    """EDA Insight 1: Customer Cohort Retention Analysis."""
    if sales_df is None or 'order_time' not in sales_df.columns:
        return None
    
    try:
        sales_copy = sales_df.copy()
        sales_copy['order_time'] = pd.to_datetime(sales_copy['order_time'], errors='coerce')
        sales_copy = sales_copy.dropna(subset=['order_time'])
        sales_copy['order_month'] = sales_copy['order_time'].dt.to_period('M')
        
        if 'customer_id' not in sales_copy.columns:
            sales_copy['customer_id'] = sales_copy['order_id'].apply(lambda x: hash(str(x)) % 10000)
        
        first_purchase = sales_copy.groupby('customer_id')['order_month'].min().reset_index()
        first_purchase.columns = ['customer_id', 'cohort_month']
        
        sales_copy = sales_copy.merge(first_purchase, on='customer_id')
        sales_copy['months_since_first'] = (sales_copy['order_month'] - sales_copy['cohort_month']).apply(lambda x: x.n if hasattr(x, 'n') else 0)
        
        cohort_data = sales_copy.groupby(['cohort_month', 'months_since_first'])['customer_id'].nunique().reset_index()
        cohort_pivot = cohort_data.pivot(index='cohort_month', columns='months_since_first', values='customer_id')
        
        cohort_size = cohort_pivot.iloc[:, 0]
        retention = cohort_pivot.divide(cohort_size, axis=0) * 100
        
        return retention.iloc[:6, :6]
    except:
        return None

def create_rfm_segmentation(sales_df):
    """EDA Insight 2: RFM Customer Segmentation."""
    if sales_df is None or 'order_time' not in sales_df.columns:
        return None
    
    try:
        sales_copy = sales_df.copy()
        sales_copy['order_time'] = pd.to_datetime(sales_copy['order_time'], errors='coerce')
        
        if 'customer_id' not in sales_copy.columns:
            sales_copy['customer_id'] = sales_copy['order_id'].apply(lambda x: hash(str(x)) % 10000)
        
        if 'selling_price_aed' in sales_copy.columns and 'qty' in sales_copy.columns:
            sales_copy['revenue'] = pd.to_numeric(sales_copy['selling_price_aed'], errors='coerce') * pd.to_numeric(sales_copy['qty'], errors='coerce')
        else:
            return None
        
        snapshot_date = sales_copy['order_time'].max() + timedelta(days=1)
        
        rfm = sales_copy.groupby('customer_id').agg({
            'order_time': lambda x: (snapshot_date - x.max()).days,
            'order_id': 'count',
            'revenue': 'sum'
        }).reset_index()
        
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        
        rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        
        def segment_customer(row):
            r, f = int(row['r_score']), int(row['f_score'])
            if r >= 4 and f >= 4:
                return 'Champions'
            elif r >= 3 and f >= 3:
                return 'Loyal Customers'
            elif r >= 4 and f <= 2:
                return 'Promising'
            elif r <= 2 and f >= 3:
                return 'At Risk'
            elif r <= 2 and f <= 2:
                return 'Hibernating'
            else:
                return 'Need Attention'
        
        rfm['segment'] = rfm.apply(segment_customer, axis=1)
        return rfm
    except:
        return None

def create_price_elasticity_analysis(sales_df, products_df):
    """EDA Insight 3: Price Elasticity & Discount Effectiveness."""
    if sales_df is None or 'discount_pct' not in sales_df.columns:
        return None
    
    try:
        sales_copy = sales_df.copy()
        sales_copy['discount_pct'] = pd.to_numeric(sales_copy['discount_pct'], errors='coerce').fillna(0)
        sales_copy['selling_price_aed'] = pd.to_numeric(sales_copy['selling_price_aed'], errors='coerce')
        sales_copy['qty'] = pd.to_numeric(sales_copy['qty'], errors='coerce')
        
        sales_copy['discount_bin'] = pd.cut(sales_copy['discount_pct'], 
                                             bins=[-1, 0, 5, 10, 15, 20, 100],
                                             labels=['0%', '1-5%', '6-10%', '11-15%', '16-20%', '20%+'])
        
        elasticity = sales_copy.groupby('discount_bin', observed=True).agg({
            'qty': 'sum',
            'selling_price_aed': 'mean',
            'order_id': 'count'
        }).reset_index()
        
        elasticity.columns = ['discount_bin', 'total_qty', 'avg_price', 'num_orders']
        elasticity['avg_qty_per_order'] = elasticity['total_qty'] / elasticity['num_orders']
        
        return elasticity
    except:
        return None

def generate_insights(kpis, city_kpis=None, channel_kpis=None, cat_kpis=None):
    """Generate business insights."""
    insights = []
    
    if kpis.get('total_revenue', 0) > 0:
        aov = kpis.get('avg_order_value', 0)
        if aov > 500:
            insights.append(("Premium Customers", f"AOV of AED {aov:,.0f} indicates high-value customers. Consider VIP loyalty programs."))
        elif aov < 200:
            insights.append(("Volume Opportunity", f"AOV of AED {aov:,.0f} suggests room for bundle offers."))
    
    margin = kpis.get('profit_margin_pct', 0)
    if margin > 25:
        insights.append(("Strong Margins", f"{margin:.1f}% margin supports promotional campaigns."))
    elif margin < 15:
        insights.append(("Margin Alert", f"{margin:.1f}% margin needs pricing review."))
    
    return_rate = kpis.get('return_rate_pct', 0)
    if return_rate > 10:
        insights.append(("High Returns", f"{return_rate:.1f}% return rate needs investigation."))
    
    return insights[:5]

def generate_recommendations(kpis, sim_results=None):
    """Generate strategic recommendations."""
    recommendations = []
    
    margin = kpis.get('profit_margin_pct', 0)
    if margin > 25:
        recommendations.append(f"Strong {margin:.0f}% margin supports up to 15% discount campaigns.")
    else:
        recommendations.append(f"Current {margin:.0f}% margin requires careful discount management.")
    
    aov = kpis.get('avg_order_value', 0)
    if aov < 200:
        recommendations.append("Implement minimum cart value promotions to increase AOV.")
    
    if sim_results:
        roi = sim_results.get('outputs', {}).get('roi_pct', 0)
        if roi > 50:
            recommendations.append(f"Campaign projects {roi:.0f}% ROI - recommend execution.")
        elif roi < 0:
            recommendations.append("Negative ROI projected - reduce discount or narrow targeting.")
    
    if not recommendations:
        recommendations.append("All metrics within optimal range.")
    
    return recommendations

# ============================================================================
# SIDEBAR WITH ANIMATIONS
# ============================================================================

with st.sidebar:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <div style="text-align: center; margin-top: -20px; padding-bottom: 15px;">
            <div style="font-size: 48px; margin-bottom: 5px; animation: float 3s ease-in-out infinite;">🛒</div>
            <div style="
                font-size: 26px;
                font-weight: 800;
                background: linear-gradient(135deg, #06b6d4, #3b82f6, #8b5cf6, #ec4899);
                background-size: 300% 100%;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: gradientFlow 4s ease infinite;
            ">Promo Pulse</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
        if st.button(theme_icon, key='theme_toggle', help="Toggle Theme"):
            toggle_theme()
            st.rerun()
    
    st.markdown("---")
    
    st.markdown('<p style="color: #ec4899; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📍 NAVIGATION</p>', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📂 Data Upload", "🧹 Data Rescue", "🎯 Simulator", "📊 Dashboard", "🔬 Advanced EDA"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Status with breathing dots
    st.markdown('<p style="color: #3b82f6; font-weight: 600; margin-bottom: 15px; letter-spacing: 1.2px; font-size: 0.85rem;">📡 STATUS</p>', unsafe_allow_html=True)
    
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

# ============================================================================
# PAGE: HOME
# ============================================================================

def show_home_page():
    """Premium home page with all animations."""
    st.markdown("""
    <div class="hero-premium">
        <div style="text-align: center; position: relative; z-index: 1;">
            <div style="margin-bottom: 24px; animation: fadeInUp 0.6s ease-out;">
                <span style="display: inline-block; padding: 12px 28px; background: linear-gradient(135deg, #06b6d4, #3b82f6); border-radius: 50px; color: white; font-size: 1rem; font-weight: 700; margin-right: 12px; animation: pulseGlow 2s ease-in-out infinite;">✨ Premium Analytics</span>
                <span style="display: inline-block; padding: 12px 28px; background: linear-gradient(135deg, #8b5cf6, #ec4899); border-radius: 50px; color: white; font-size: 1rem; font-weight: 700; animation: pulseGlow 2s ease-in-out infinite 0.5s;">🚀 v4.0</span>
            </div>
            <div class="hero-title-premium">Promo Pulse Simulator</div>
            <p style="color: var(--text-secondary); font-size: 1.3rem; margin: 0; line-height: 1.6; animation: fadeInUp 1s ease-out;">
                Advanced Data Intelligence + Campaign Simulation Platform<br>
                <span style="color: var(--accent-cyan); font-weight: 600;">UAE Omnichannel Retail Analytics</span>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.markdown('<div class="section-title-premium">✨ Platform Capabilities</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        features = [
            ("📂", "Data Upload", "Multi-format ingestion", "cyan", 1),
            ("🧹", "Data Rescue", "AI-powered cleaning", "blue", 2),
            ("🎯", "Simulator", "What-if scenarios", "purple", 3),
            ("📊", "Analytics", "Executive dashboards", "pink", 4)
        ]
        
        for col, (icon, title, desc, color, stagger) in zip([col1, col2, col3, col4], features):
            with col:
                st.markdown(create_feature_card(icon, title, desc, color, stagger), unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<div class="alert-info"><strong>👈 Navigate to Data Upload</strong> to load your e-commerce data files.</div>', unsafe_allow_html=True)
    
    else:
        st.markdown('<div class="section-title-premium">📊 Data Overview</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        counts = [
            ("Products", len(st.session_state.raw_products) if st.session_state.raw_products is not None else 0, "cyan", 1),
            ("Stores", len(st.session_state.raw_stores) if st.session_state.raw_stores is not None else 0, "blue", 2),
            ("Sales", len(st.session_state.raw_sales) if st.session_state.raw_sales is not None else 0, "purple", 3),
            ("Inventory", len(st.session_state.raw_inventory) if st.session_state.raw_inventory is not None else 0, "pink", 4)
        ]
        
        for col, (label, count, color, stagger) in zip([col1, col2, col3, col4], counts):
            with col:
                st.markdown(create_metric_card_premium(label, format_number(count), color=color, stagger=stagger), unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.session_state.is_cleaned:
            st.markdown('<div class="alert-success">✅ <strong>Data Ready:</strong> Your data has been cleaned!</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-warning">⚠️ <strong>Action Required:</strong> Go to Data Rescue to clean data.</div>', unsafe_allow_html=True)
    
    show_footer()

# ============================================================================
# PAGE: DATA UPLOAD
# ============================================================================

def show_data_page():
    """Data upload page with animations."""
    st.markdown('<h1 class="page-title-premium" style="color: var(--accent-cyan);">📂 Data Upload</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: var(--text-secondary); font-size: 1.1rem; animation: fadeInUp 0.5s ease-out;">Upload your data files or load sample data</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<div class="section-title-premium">📤 Upload Files</div>', unsafe_allow_html=True)
    
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
    
    st.markdown('<div class="section-title-premium">📦 Or Load Sample Data</div>', unsafe_allow_html=True)
    
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
        st.markdown('<div class="section-title-premium">👀 Data Preview</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📦 Products", "🏪 Stores", "🛒 Sales", "📋 Inventory"])
        
        for tab, df, name in [(tab1, st.session_state.raw_products, "Products"),
                              (tab2, st.session_state.raw_stores, "Stores"),
                              (tab3, st.session_state.raw_sales, "Sales"),
                              (tab4, st.session_state.raw_inventory, "Inventory")]:
            with tab:
                if df is not None:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(create_metric_card_premium("Rows", format_number(len(df)), color="cyan", stagger=1), unsafe_allow_html=True)
                    with col2:
                        st.markdown(create_metric_card_premium("Columns", str(len(df.columns)), color="blue", stagger=2), unsafe_allow_html=True)
                    with col3:
                        null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
                        st.markdown(create_metric_card_premium("Null %", f"{null_pct:.1f}%", color="orange", stagger=3), unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.dataframe(df.head(100), use_container_width=True)
    
    show_footer()

# ============================================================================
# PAGE: DATA RESCUE
# ============================================================================

def show_cleaner_page():
    """Data rescue page with animations."""
    st.markdown('<h1 class="page-title-premium" style="color: var(--accent-green);">🧹 Data Rescue Center</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: var(--text-secondary); font-size: 1.1rem; animation: fadeInUp 0.5s ease-out;">Detect issues and clean your data automatically</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.markdown('<div class="alert-warning">⚠️ Please load data first. Go to Data Upload page.</div>', unsafe_allow_html=True)
        show_footer()
        return
    
    st.markdown('<div class="section-title-premium">🔍 Issues We Detect & Fix</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    issue_types = [
        ("Data Quality", ["Missing values", "Duplicates", "Nulls"], "cyan", 1),
        ("Format Issues", ["Invalid timestamps", "Cities", "Case"], "purple", 2),
        ("Value Issues", ["Outliers", "FK violations", "Categories"], "pink", 3)
    ]
    
    for col, (title, items, color, stagger) in zip([col1, col2, col3], issue_types):
        with col:
            items_html = "".join([f"<li>{item}</li>" for item in items])
            st.markdown(f"""
            <div class="premium-container stagger-{stagger}" style="animation-delay: {stagger * 0.15}s;">
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
    
    if st.session_state.is_cleaned:
        st.markdown("---")
        st.markdown('<div class="section-title-premium">📊 Cleaning Results</div>', unsafe_allow_html=True)
        
        stats = st.session_state.cleaner_stats
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            for col, (ds, color, stagger) in zip([col1, col2, col3, col4], 
                                        [('products', 'cyan', 1), ('stores', 'blue', 2), ('sales', 'purple', 3), ('inventory', 'pink', 4)]):
                with col:
                    before = stats.get(ds, {}).get('before', 0)
                    after = stats.get(ds, {}).get('after', 0)
                    delta = f"{before - after} fixed" if before > after else "Clean"
                    delta_type = "negative" if before > after else "positive"
                    st.markdown(create_metric_card_premium(ds.title(), format_number(after), delta, delta_type, color, stagger), unsafe_allow_html=True)
        
        issues_df = st.session_state.issues_df
        if issues_df is not None and len(issues_df) > 0:
            st.markdown("---")
            st.markdown('<div class="section-title-premium">🔍 Issues Detected</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="alert-success">✅ Total {len(issues_df)} issues detected and fixed!</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                issue_counts = issues_df['issue_type'].value_counts().reset_index()
                issue_counts.columns = ['Issue Type', 'Count']
                fig = px.bar(issue_counts, x='Count', y='Issue Type', orientation='h', color='Count',
                           color_continuous_scale=['#06b6d4', '#8b5cf6'])
                fig = style_plotly_chart_themed(fig)
                fig.update_layout(title='Issues by Type', coloraxis_showscale=False, height=350)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                issue_counts_sorted = issue_counts.sort_values('Count', ascending=False)
                issue_counts_sorted['Cumulative %'] = (issue_counts_sorted['Count'].cumsum() / issue_counts_sorted['Count'].sum() * 100)
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(go.Bar(x=issue_counts_sorted['Issue Type'], y=issue_counts_sorted['Count'], name='Count', marker_color='#06b6d4'), secondary_y=False)
                fig.add_trace(go.Scatter(x=issue_counts_sorted['Issue Type'], y=issue_counts_sorted['Cumulative %'], name='Cumulative %', marker_color='#ec4899', mode='lines+markers'), secondary_y=True)
                fig = style_plotly_chart_themed(fig)
                fig.update_layout(title='Pareto Chart', height=350)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<div class="section-title-premium">📋 Issues Log</div>', unsafe_allow_html=True)
            st.dataframe(issues_df, use_container_width=True, height=300)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 Download Issues Log", issues_df.to_csv(index=False), "issues.csv", "text/csv")
            with col2:
                if st.session_state.clean_sales is not None:
                    st.download_button("📥 Download Cleaned Sales", st.session_state.clean_sales.to_csv(index=False), "cleaned_sales.csv", "text/csv")
        else:
            st.markdown('<div class="alert-success">✅ No issues found! Your data is clean.</div>', unsafe_allow_html=True)
    
    show_footer()

# ============================================================================
# PAGE: SIMULATOR
# ============================================================================

def show_simulator_page():
    """Simulator page with animations."""
    st.markdown('<h1 class="page-title-premium" style="color: var(--accent-purple);">🎯 Promo Pulse Simulator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: var(--text-secondary); font-size: 1.1rem; animation: fadeInUp 0.5s ease-out;">Run what-if discount scenarios with constraints</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not st.session_state.data_loaded:
        st.markdown('<div class="alert-warning">⚠️ Please load data first.</div>', unsafe_allow_html=True)
        show_footer()
        return
    
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    
    st.markdown('<div class="section-title-premium">⚙️ Campaign Parameters</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**💰 Pricing**")
        discount_pct = st.slider("Discount %", 0, 50, 15, key='sim_discount')
        promo_budget = st.number_input("Budget (AED)", 1000, 500000, 25000, step=5000, key='sim_budget')
    
    with col2:
        st.markdown("**📊 Constraints**")
        margin_floor = st.slider("Margin Floor %", 0, 50, 15, key='sim_margin')
        campaign_days = st.slider("Campaign Days", 1, 30, 7, key='sim_days')
    
    with col3:
        st.markdown("**🎯 Targeting**")
        cities = ['All'] + ([str(c) for c in stores_df['city'].dropna().unique()] if stores_df is not None and 'city' in stores_df.columns else [])
        channels = ['All'] + ([str(c) for c in stores_df['channel'].dropna().unique()] if stores_df is not None and 'channel' in stores_df.columns else [])
        categories = ['All'] + ([str(c) for c in products_df['category'].dropna().unique()] if products_df is not None and 'category' in products_df.columns else [])
        
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
                    discount_pct=discount_pct, promo_budget=promo_budget, margin_floor=margin_floor,
                    city=city, channel=channel, category=category, campaign_days=campaign_days
                )
                st.session_state.sim_results = results
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    if st.session_state.sim_results:
        results = st.session_state.sim_results
        outputs = results.get('outputs', {})
        comparison = results.get('comparison', {})
        warnings = results.get('warnings', [])
        violations = results.get('constraint_violations', [])
        
        st.markdown("---")
        st.markdown('<div class="section-title-premium">📊 Simulation Results</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            delta = f"{comparison.get('revenue_change_pct', 0):+.1f}%"
            delta_type = "positive" if comparison.get('revenue_change_pct', 0) > 0 else "negative"
            st.markdown(create_metric_card_premium("Exp. Revenue", format_currency(outputs.get('expected_revenue', 0)), delta, delta_type, "cyan", 1), unsafe_allow_html=True)
        with col2:
            delta = f"{comparison.get('profit_change_pct', 0):+.1f}%"
            delta_type = "positive" if comparison.get('profit_change_pct', 0) > 0 else "negative"
            st.markdown(create_metric_card_premium("Net Profit", format_currency(outputs.get('expected_net_profit', 0)), delta, delta_type, "green", 2), unsafe_allow_html=True)
        with col3:
            roi = outputs.get('roi_pct', 0)
            st.markdown(create_metric_card_premium("ROI", f"{roi:.1f}%", color="green" if roi > 0 else "red", stagger=3), unsafe_allow_html=True)
        with col4:
            budget_util = (outputs.get('promo_cost', 0) / promo_budget * 100) if promo_budget > 0 else 0
            st.markdown(create_metric_card_premium("Budget Used", f"{budget_util:.1f}%", color="orange", stagger=4), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(create_metric_card_premium("Demand Lift", f"+{outputs.get('demand_lift_pct', 0):.1f}%", color="purple", stagger=5), unsafe_allow_html=True)
        with col2:
            margin_val = outputs.get('expected_margin_pct', 0)
            st.markdown(create_metric_card_premium("Exp. Margin", f"{margin_val:.1f}%", color="green" if margin_val >= margin_floor else "orange", stagger=6), unsafe_allow_html=True)
        with col3:
            st.markdown(create_metric_card_premium("Promo Cost", format_currency(outputs.get('promo_cost', 0)), color="orange", stagger=7), unsafe_allow_html=True)
        with col4:
            st.markdown(create_metric_card_premium("Exp. Orders", format_number(outputs.get('expected_orders', 0)), color="blue", stagger=8), unsafe_allow_html=True)
        
        if violations:
            st.markdown("---")
            for v in violations:
                st.markdown(f'<div class="alert-error">❌ <strong>{v.get("constraint", "Unknown")}:</strong> {v.get("message", "")}</div>', unsafe_allow_html=True)
        
        if warnings:
            for w in warnings:
                st.markdown(f'<div class="alert-warning">⚠️ {w}</div>', unsafe_allow_html=True)
        
        if not warnings and not violations:
            st.markdown('<div class="alert-success">✅ All metrics healthy. Campaign looks good!</div>', unsafe_allow_html=True)
        
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
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(barmode='group', title='Revenue & Profit Comparison', height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            orders_data = pd.DataFrame({'Type': ['Baseline', 'Campaign'], 'Orders': [comparison.get('baseline_orders', 0), outputs.get('expected_orders', 0)]})
            fig = px.bar(orders_data, x='Type', y='Orders', color='Type', color_discrete_sequence=['#8b5cf6', '#ec4899'])
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(title='Orders Comparison', showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    show_footer()

# ============================================================================
# PAGE: DASHBOARD
# ============================================================================

def show_dashboard_page():
    """Dashboard page with filters in main body."""
    st.markdown('<h1 class="page-title-premium" style="color: var(--accent-pink);">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.markdown('<div class="alert-warning">⚠️ Please load data first.</div>', unsafe_allow_html=True)
        show_footer()
        return
    
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    stores_df = st.session_state.clean_stores if st.session_state.is_cleaned else st.session_state.raw_stores
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    inventory_df = st.session_state.clean_inventory if st.session_state.is_cleaned else st.session_state.raw_inventory
    
    # View Toggle
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        view_mode = st.radio("Dashboard View", ["👔 Executive", "⚙️ Manager"], horizontal=True, key='dashboard_view')
    
    st.markdown("---")
    
    # Global Filters in Body
    with st.expander("🎛️ **Global Filters** - Click to expand", expanded=False):
        filter_cols = st.columns(5)
        
        with filter_cols[0]:
            if sales_df is not None and 'order_time' in sales_df.columns:
                try:
                    temp = sales_df.copy()
                    temp['order_time'] = pd.to_datetime(temp['order_time'], errors='coerce')
                    min_date, max_date = temp['order_time'].min(), temp['order_time'].max()
                    if pd.notna(min_date) and pd.notna(max_date):
                        st.date_input("📅 Date Range", value=(min_date.date(), max_date.date()), min_value=min_date.date(), max_value=max_date.date(), key='global_date')
                except:
                    pass
        
        with filter_cols[1]:
            cities = ['All'] + (sorted([str(c) for c in stores_df['city'].dropna().unique()]) if stores_df is not None and 'city' in stores_df.columns else [])
            st.selectbox("🏙️ City", cities, key='global_city')
        
        with filter_cols[2]:
            channels = ['All'] + (sorted([str(c) for c in stores_df['channel'].dropna().unique()]) if stores_df is not None and 'channel' in stores_df.columns else [])
            st.selectbox("📱 Channel", channels, key='global_channel')
        
        with filter_cols[3]:
            categories = ['All'] + (sorted([str(c) for c in products_df['category'].dropna().unique()]) if products_df is not None and 'category' in products_df.columns else [])
            st.selectbox("📦 Category", categories, key='global_category')
        
        with filter_cols[4]:
            brands = ['All'] + (sorted([str(b) for b in products_df['brand'].dropna().unique()][:20]) if products_df is not None and 'brand' in products_df.columns else [])
            st.selectbox("🏷️ Brand", brands, key='global_brand')
    
    # Apply filters
    filtered_sales = sales_df.copy() if sales_df is not None else None
    if filtered_sales is not None:
        if 'global_city' in st.session_state and st.session_state.global_city != 'All' and stores_df is not None:
            city_stores = stores_df[stores_df['city'] == st.session_state.global_city]['store_id'].tolist()
            filtered_sales = filtered_sales[filtered_sales['store_id'].isin(city_stores)]
        if 'global_channel' in st.session_state and st.session_state.global_channel != 'All' and stores_df is not None:
            chan_stores = stores_df[stores_df['channel'] == st.session_state.global_channel]['store_id'].tolist()
            filtered_sales = filtered_sales[filtered_sales['store_id'].isin(chan_stores)]
        if 'global_category' in st.session_state and st.session_state.global_category != 'All' and products_df is not None:
            cat_prods = products_df[products_df['category'] == st.session_state.global_category]['product_id'].tolist()
            filtered_sales = filtered_sales[filtered_sales['product_id'].isin(cat_prods)]
    
    sim = Simulator()
    kpis = sim.calculate_overall_kpis(filtered_sales, products_df)
    
    if view_mode == "👔 Executive":
        show_executive_view(filtered_sales, stores_df, products_df, kpis, sim)
    else:
        show_manager_view(filtered_sales, stores_df, products_df, inventory_df, kpis, sim)
    
    show_footer()

def show_executive_view(sales_df, stores_df, products_df, kpis, sim):
    """Executive dashboard view with animations."""
    st.markdown('<div class="section-title-premium">💼 Executive Summary</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        revenue = kpis.get('net_revenue', kpis.get('total_revenue', 0))
        st.markdown(create_metric_card_premium("Net Revenue", format_currency(revenue), "+12.5%", "positive", "cyan", 1), unsafe_allow_html=True)
    with col2:
        margin = kpis.get('profit_margin_pct', 0)
        st.markdown(create_metric_card_premium("Gross Margin", f"{margin:.1f}%", "+2.3%", "positive", "green", 2), unsafe_allow_html=True)
    with col3:
        orders = kpis.get('total_orders', 0)
        st.markdown(create_metric_card_premium("Total Orders", format_number(orders), "+8.7%", "positive", "purple", 3), unsafe_allow_html=True)
    with col4:
        aov = kpis.get('avg_order_value', 0)
        st.markdown(create_metric_card_premium("Avg Order", format_currency(aov), "-1.2%", "negative", "pink", 4), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        profit = kpis.get('total_profit', 0)
        st.markdown(create_metric_card_premium("Profit Proxy", format_currency(profit), color="green", stagger=5), unsafe_allow_html=True)
    with col2:
        discount = kpis.get('avg_discount_pct', 0)
        st.markdown(create_metric_card_premium("Avg Discount", f"{discount:.1f}%", color="orange", stagger=6), unsafe_allow_html=True)
    with col3:
        return_rate = kpis.get('return_rate_pct', 0)
        st.markdown(create_metric_card_premium("Return Rate", f"{return_rate:.1f}%", color="pink", stagger=7), unsafe_allow_html=True)
    with col4:
        products = kpis.get('unique_products', 0)
        st.markdown(create_metric_card_premium("Products", format_number(products), color="blue", stagger=8), unsafe_allow_html=True)
    
    st.markdown("---")
    
    city_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'city')
    channel_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'channel')
    cat_kpis = sim.calculate_kpis_by_dimension(sales_df, stores_df, products_df, 'category')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📈 Revenue Trend**")
        trend_filter = st.selectbox("Period", ["Daily", "Weekly", "Monthly"], key='trend_period', label_visibility="collapsed")
        daily = sim.calculate_daily_trends(sales_df, products_df)
        if daily is not None and len(daily) > 0:
            if trend_filter == "Weekly":
                daily['date'] = pd.to_datetime(daily['date'])
                daily = daily.resample('W', on='date').sum().reset_index()
            elif trend_filter == "Monthly":
                daily['date'] = pd.to_datetime(daily['date'])
                daily = daily.resample('M', on='date').sum().reset_index()
            fig = px.area(daily, x='date', y='revenue', color_discrete_sequence=['#06b6d4'])
            fig = style_plotly_chart_themed(fig)
            fig.update_traces(line=dict(width=3), fillcolor='rgba(6, 182, 212, 0.15)')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**🏙️ Revenue by City**")
        city_metric = st.selectbox("Metric", ["Revenue", "Orders", "Margin %"], key='city_metric', label_visibility="collapsed")
        if city_kpis is not None and len(city_kpis) > 0:
            metric_col = 'revenue' if city_metric == "Revenue" else ('orders' if city_metric == "Orders" else 'profit_margin_pct')
            fig = px.bar(city_kpis, x='city', y=metric_col, color='city', color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899'])
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📦 Category Performance**")
        cat_view = st.selectbox("View", ["Revenue", "Margin %"], key='cat_view', label_visibility="collapsed")
        if cat_kpis is not None and len(cat_kpis) > 0:
            y_col = 'revenue' if cat_view == "Revenue" else 'profit_margin_pct'
            fig = px.bar(cat_kpis.head(8), x='category', y=y_col, color=y_col, color_continuous_scale=['#06b6d4', '#8b5cf6', '#ec4899'])
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(coloraxis_showscale=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**📱 Channel Distribution**")
        if channel_kpis is not None and len(channel_kpis) > 0:
            fig = px.pie(channel_kpis, values='revenue', names='channel', color_discrete_sequence=['#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b'], hole=0.45)
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown('<div class="section-title-premium">💡 Key Business Insights</div>', unsafe_allow_html=True)
    
    insights = generate_insights(kpis, city_kpis, channel_kpis, cat_kpis)
    if insights:
        cols = st.columns(2)
        for i, (title, text) in enumerate(insights):
            with cols[i % 2]:
                st.markdown(create_insight_card_premium(title, text, stagger=i+1), unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<div class="section-title-premium">📋 Strategic Recommendations</div>', unsafe_allow_html=True)
    
    recommendations = generate_recommendations(kpis, st.session_state.sim_results)
    st.markdown(create_recommendation_premium("Action Items for Leadership", recommendations), unsafe_allow_html=True)

def show_manager_view(sales_df, stores_df, products_df, inventory_df, kpis, sim):
    """Manager dashboard view with animations."""
    st.markdown('<div class="section-title-premium">⚙️ Operations Dashboard</div>', unsafe_allow_html=True)
    
    stockout = sim.calculate_stockout_risk(inventory_df) if inventory_df is not None else {'stockout_risk_pct': 0, 'low_stock_items': 0}
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        risk_pct = stockout.get('stockout_risk_pct', 0)
        color = "red" if risk_pct > 15 else "green"
        st.markdown(create_metric_card_premium("Stockout Risk", f"{risk_pct:.1f}%", color=color, stagger=1), unsafe_allow_html=True)
    with col2:
        return_rate = kpis.get('return_rate_pct', 0)
        st.markdown(create_metric_card_premium("Return Rate", f"{return_rate:.1f}%", color="orange", stagger=2), unsafe_allow_html=True)
    with col3:
        pf_rate = kpis.get('payment_failure_rate_pct', 0)
        st.markdown(create_metric_card_premium("Payment Fail", f"{pf_rate:.1f}%", color="red" if pf_rate > 5 else "green", stagger=3), unsafe_allow_html=True)
    with col4:
        low_stock = stockout.get('low_stock_items', 0)
        st.markdown(create_metric_card_premium("Low Stock SKUs", format_number(low_stock), color="purple", stagger=4), unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Inventory by City**")
        if inventory_df is not None and stores_df is not None:
            try:
                inv = inventory_df.merge(stores_df[['store_id', 'city']], on='store_id', how='left')
                inv['stock_on_hand'] = pd.to_numeric(inv['stock_on_hand'], errors='coerce').fillna(0)
                stock_by = inv.groupby('city')['stock_on_hand'].sum().reset_index()
                fig = px.bar(stock_by, x='city', y='stock_on_hand', color='stock_on_hand', color_continuous_scale=['#ef4444', '#f59e0b', '#10b981'])
                fig = style_plotly_chart_themed(fig)
                fig.update_layout(coloraxis_showscale=False, height=350)
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("Unable to generate chart")
    
    with col2:
        st.markdown("**⚠️ Top Risk Items**")
        if inventory_df is not None:
            try:
                inv = inventory_df.copy()
                inv['stock_on_hand'] = pd.to_numeric(inv['stock_on_hand'], errors='coerce').fillna(0)
                inv['reorder_point'] = pd.to_numeric(inv.get('reorder_point', 10), errors='coerce').fillna(10)
                inv['risk_score'] = inv['reorder_point'] - inv['stock_on_hand']
                top_risk = inv.nlargest(10, 'risk_score')[['product_id', 'store_id', 'stock_on_hand', 'risk_score']]
                st.dataframe(top_risk, use_container_width=True, height=300)
            except:
                st.info("Unable to calculate")
    
    st.markdown("---")
    st.markdown('<div class="section-title-premium">🚨 Operational Alerts</div>', unsafe_allow_html=True)
    
    alerts = []
    if stockout.get('stockout_risk_pct', 0) > 15:
        alerts.append(('error', f"🔴 Critical: {stockout['stockout_risk_pct']:.0f}% SKUs at stockout risk"))
    if kpis.get('payment_failure_rate_pct', 0) > 5:
        alerts.append(('warning', f"⚠️ Payment failure rate at {kpis['payment_failure_rate_pct']:.1f}%"))
    if st.session_state.issues_df is not None and len(st.session_state.issues_df) > 0:
        alerts.append(('info', f"📋 {len(st.session_state.issues_df)} data quality issues logged"))
    if not alerts:
        alerts.append(('success', "✅ All systems normal"))
    
    for alert_type, text in alerts:
        st.markdown(f'<div class="alert-{alert_type}">{text}</div>', unsafe_allow_html=True)

# ============================================================================
# PAGE: ADVANCED EDA
# ============================================================================

def show_advanced_eda_page():
    """Advanced EDA page with animations."""
    st.markdown('<h1 class="page-title-premium" style="color: var(--accent-purple);">🔬 Advanced EDA</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: var(--text-secondary); font-size: 1.1rem; animation: fadeInUp 0.5s ease-out;">Deep-dive analytics: cohorts, segmentation, price elasticity</p>', unsafe_allow_html=True)
    
    if not st.session_state.data_loaded:
        st.markdown('<div class="alert-warning">⚠️ Please load data first.</div>', unsafe_allow_html=True)
        show_footer()
        return
    
    sales_df = st.session_state.clean_sales if st.session_state.is_cleaned else st.session_state.raw_sales
    products_df = st.session_state.clean_products if st.session_state.is_cleaned else st.session_state.raw_products
    
    st.markdown("---")
    
    # 1. Cohort Analysis
    st.markdown('<div class="section-title-premium">📅 Customer Cohort Retention</div>', unsafe_allow_html=True)
    
    with st.expander("ℹ️ What is Cohort Analysis?", expanded=False):
        st.markdown('<div class="alert-info">Cohort analysis tracks customer behavior over time by grouping customers based on their first purchase month.</div>', unsafe_allow_html=True)
    
    cohort_data = create_customer_cohort_analysis(sales_df)
    
    if cohort_data is not None and len(cohort_data) > 0:
        fig = px.imshow(
            cohort_data.values,
            labels=dict(x="Months Since First Purchase", y="Cohort Month", color="Retention %"),
            x=[f"Month {i}" for i in range(cohort_data.shape[1])],
            y=[str(m) for m in cohort_data.index],
            color_continuous_scale='RdYlGn',
            aspect="auto"
        )
        fig = style_plotly_chart_themed(fig)
        fig.update_layout(title="Customer Retention Heatmap", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        avg_m1 = cohort_data.iloc[:, 1].mean() if cohort_data.shape[1] > 1 else 0
        st.markdown(create_insight_card_premium("Retention Insight", f"Average 1-month retention is {avg_m1:.1f}%. Consider 30-day engagement campaigns.", 1), unsafe_allow_html=True)
    else:
        st.info("Insufficient data for cohort analysis.")
    
    st.markdown("---")
    
    # 2. RFM Segmentation
    st.markdown('<div class="section-title-premium">👥 RFM Customer Segmentation</div>', unsafe_allow_html=True)
    
    with st.expander("ℹ️ What is RFM Analysis?", expanded=False):
        st.markdown('<div class="alert-info">RFM stands for Recency, Frequency, Monetary value. It segments customers for personalized marketing.</div>', unsafe_allow_html=True)
    
    rfm_data = create_rfm_segmentation(sales_df)
    
    if rfm_data is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            segment_counts = rfm_data['segment'].value_counts().reset_index()
            segment_counts.columns = ['Segment', 'Count']
            fig = px.bar(segment_counts, x='Segment', y='Count', title='Customer Segments', color='Segment', color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b'])
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            segment_value = rfm_data.groupby('segment')['monetary'].sum().reset_index()
            segment_value.columns = ['Segment', 'Total Value']
            fig = px.pie(segment_value, values='Total Value', names='Segment', title='Revenue by Segment', color_discrete_sequence=['#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b'], hole=0.4)
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        champions_pct = (rfm_data[rfm_data['segment'] == 'Champions'].shape[0] / len(rfm_data) * 100) if len(rfm_data) > 0 else 0
        at_risk_pct = (rfm_data[rfm_data['segment'] == 'At Risk'].shape[0] / len(rfm_data) * 100) if len(rfm_data) > 0 else 0
        
        recommendations = [
            f"Champions represent {champions_pct:.1f}% - prioritize VIP programs",
            f"{at_risk_pct:.1f}% are 'At Risk' - implement win-back campaigns",
            "Activate 'Hibernating' customers with re-engagement offers"
        ]
        st.markdown(create_recommendation_premium("RFM-Based Strategy", recommendations), unsafe_allow_html=True)
    else:
        st.info("Unable to calculate RFM segments.")
    
    st.markdown("---")
    
    # 3. Price Elasticity
    st.markdown('<div class="section-title-premium">💰 Price Elasticity Analysis</div>', unsafe_allow_html=True)
    
    with st.expander("ℹ️ What is Price Elasticity?", expanded=False):
        st.markdown('<div class="alert-info">Price elasticity measures how demand responds to price changes. Reveals optimal discount levels.</div>', unsafe_allow_html=True)
    
    # Local filter for this chart
    pe_cols = st.columns(2)
    with pe_cols[0]:
        categories = ['All'] + (sorted([str(c) for c in products_df['category'].dropna().unique()]) if products_df is not None and 'category' in products_df.columns else [])
        pe_category = st.selectbox("Filter by Category", categories, key='pe_cat_filter')
    
    # Apply local filter
    pe_sales = sales_df.copy() if sales_df is not None else None
    if pe_sales is not None and pe_category != 'All' and products_df is not None:
        cat_prods = products_df[products_df['category'] == pe_category]['product_id'].tolist()
        pe_sales = pe_sales[pe_sales['product_id'].isin(cat_prods)]
    
    elasticity_data = create_price_elasticity_analysis(pe_sales, products_df)
    
    if elasticity_data is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(elasticity_data, x='discount_bin', y='total_qty', title='Quantity by Discount Level', color='total_qty', color_continuous_scale='Blues')
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(coloraxis_showscale=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(elasticity_data, x='discount_bin', y='avg_qty_per_order', title='Avg Qty per Order', markers=True, line_shape='spline')
            fig.update_traces(line=dict(color='#06b6d4', width=3), marker=dict(size=10))
            fig = style_plotly_chart_themed(fig)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        optimal_idx = elasticity_data['avg_qty_per_order'].idxmax()
        optimal_discount = elasticity_data.iloc[optimal_idx]['discount_bin']
        optimal_qty = elasticity_data.iloc[optimal_idx]['avg_qty_per_order']
        
        st.markdown(create_insight_card_premium("Optimal Discount", f"The {optimal_discount} range shows highest avg quantity ({optimal_qty:.2f} units). This is your discount sweet spot.", 2), unsafe_allow_html=True)
    else:
        st.info("Unable to calculate price elasticity.")
    
    show_footer()

# ============================================================================
# MAIN ROUTER
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
elif page == "🔬 Advanced EDA":
    show_advanced_eda_page()
