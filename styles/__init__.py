"""
Premium Theme CSS Loader for Streamlit
Complete Version with All Helper Functions
"""

import streamlit as st
from pathlib import Path


def load_css_file(file_path: str) -> str:
    """Load CSS file and return as string."""
    try:
        css_path = Path(__file__).parent / file_path
        if css_path.exists():
            return css_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error loading CSS: {e}")
    return ""


def load_premium_css(theme: str = "dark", include_orbs: bool = False) -> None:
    """Load premium CSS theme into Streamlit app."""
    
    # Load external CSS file
    css = load_css_file("premium_theme.css")
    
    # Fallback inline CSS if file doesn't load
    if not css:
        css = get_fallback_css()
    
    # Inject CSS
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    # Floating orbs
    if include_orbs:
        st.markdown("""
        <div class="floating-orbs">
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="orb orb-3"></div>
            <div class="orb orb-4"></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Light theme
    if theme == "light":
        st.markdown("""
        <script>
            const checkBody = setInterval(() => {
                const app = document.querySelector('.stApp');
                if (app) {
                    app.classList.add('light-theme');
                    clearInterval(checkBody);
                }
            }, 100);
        </script>
        """, unsafe_allow_html=True)


def get_fallback_css() -> str:
    """Fallback CSS if external file doesn't load."""
    return """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-card: #16161f;
        --bg-card-hover: #1e1e2d;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border-color: #2d2d3a;
        --glass-bg: rgba(22, 22, 31, 0.7);
        --glass-border: rgba(255, 255, 255, 0.1);
        --accent-cyan: #06b6d4;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-pink: #ec4899;
        --accent-green: #10b981;
        --accent-orange: #f59e0b;
        --accent-red: #ef4444;
        --accent-teal: #14b8a6;
    }
    
    .stApp {
        background: var(--bg-primary);
        font-family: 'Inter', sans-serif;
    }
    
    .premium-container, .metric-card-premium, .insight-premium, 
    .recommendation-premium, .info-card, .success-card, 
    .warning-card, .error-card, .footer-premium {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid var(--glass-border);
        margin: 16px 0;
    }
    
    .metric-card-premium {
        min-height: 140px;
        padding: 20px;
    }
    
    .metric-label-premium {
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .metric-value-premium {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 8px 0;
    }
    
    .insight-premium {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.1));
        border-left: 4px solid var(--accent-purple);
    }
    
    .insight-title-premium {
        color: var(--accent-purple);
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 8px;
    }
    
    .insight-text-premium {
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    .info-card {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(59, 130, 246, 0.1));
        border-left: 4px solid var(--accent-cyan);
    }
    
    .success-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(20, 184, 166, 0.1));
        border-left: 4px solid var(--accent-green);
    }
    
    .warning-card {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(251, 146, 60, 0.1));
        border-left: 4px solid var(--accent-orange);
    }
    
    .error-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(236, 72, 153, 0.1));
        border-left: 4px solid var(--accent-red);
    }
    
    .footer-premium {
        text-align: center;
        margin-top: 60px;
        padding: 40px;
        border-top: 1px solid var(--glass-border);
    }
    
    .gradient-text {
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple), var(--accent-pink));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .section-title-premium {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 24px 0 16px 0;
        color: var(--text-primary);
    }
    
    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        animation: breathe 2s ease-in-out infinite;
    }
    
    .status-dot.green { background: var(--accent-green); }
    .status-dot.red { background: var(--accent-red); }
    .status-dot.orange { background: var(--accent-orange); }
    
    @keyframes breathe {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.2); opacity: 0.7; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .floating-orbs {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
    }
    
    .orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(40px);
        animation: floatOrb 20s ease-in-out infinite;
    }
    
    .orb-1 { width: 300px; height: 300px; background: rgba(6, 182, 212, 0.15); top: 10%; left: 10%; }
    .orb-2 { width: 400px; height: 400px; background: rgba(139, 92, 246, 0.12); top: 50%; right: 10%; }
    .orb-3 { width: 250px; height: 250px; background: rgba(236, 72, 153, 0.1); bottom: 10%; left: 30%; }
    .orb-4 { width: 200px; height: 200px; background: rgba(16, 185, 129, 0.1); top: 30%; right: 30%; }
    
    @keyframes floatOrb {
        0%, 100% { transform: translate(0, 0); opacity: 0.3; }
        50% { transform: translate(-10px, -30px); opacity: 0.5; }
    }
    """


def get_theme_colors(theme: str = "dark") -> dict:
    """Get theme colors as a dictionary."""
    if theme == "dark":
        return {
            'bg_primary': '#0a0a0f',
            'bg_secondary': '#12121a',
            'bg_card': '#16161f',
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
        }
    else:
        return {
            'bg_primary': '#f8fafc',
            'bg_secondary': '#ffffff',
            'bg_card': '#ffffff',
            'text_primary': '#0f172a',
            'text_secondary': '#475569',
            'text_muted': '#64748b',
            'border_color': '#e2e8f0',
            'accent_cyan': '#06b6d4',
            'accent_blue': '#3b82f6',
            'accent_purple': '#8b5cf6',
            'accent_pink': '#ec4899',
            'accent_green': '#10b981',
            'accent_orange': '#f59e0b',
            'accent_red': '#ef4444',
        }


def get_plotly_template(theme: str = "dark") -> dict:
    """Get Plotly chart template matching the theme."""
    colors = get_theme_colors(theme)
    return {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': colors['text_primary'], 'family': 'Inter, sans-serif'},
        'xaxis': {'gridcolor': colors['border_color'], 'linecolor': colors['border_color']},
        'yaxis': {'gridcolor': colors['border_color'], 'linecolor': colors['border_color']},
        'margin': {'t': 60, 'b': 40, 'l': 40, 'r': 20}
    }


# =============================================================================
# METRIC CARD
# =============================================================================
def create_metric_card(
    label: str, 
    value: str, 
    delta: str = None, 
    delta_type: str = "positive", 
    color: str = "cyan", 
    stagger: int = 1
) -> str:
    """Create a premium metric card HTML."""
    colors = {
        'cyan': '#06b6d4', 'blue': '#3b82f6', 'purple': '#8b5cf6',
        'pink': '#ec4899', 'green': '#10b981', 'orange': '#f59e0b',
        'teal': '#14b8a6', 'red': '#ef4444'
    }
    accent = colors.get(color, '#06b6d4')
    
    delta_html = ""
    if delta:
        delta_color = "#10b981" if delta_type == "positive" else "#ef4444"
        arrow = "↑" if delta_type == "positive" else "↓"
        delta_html = f'<div style="font-size: 0.85rem; color: {delta_color}; margin-top: 8px;">{arrow} {delta}</div>'
    
    return f"""
    <div class="metric-card-premium" style="animation-delay: {stagger * 0.1}s;">
        <div class="metric-label-premium">{label}</div>
        <div class="metric-value-premium" style="color: {accent};">{value}</div>
        {delta_html}
    </div>
    """


# =============================================================================
# INFO / SUCCESS / WARNING / ERROR CARDS
# =============================================================================
def create_info_card(content: str, icon: str = "ℹ️") -> str:
    """Create an info card HTML."""
    return f"""
    <div class="info-card">
        <div style="display: flex; align-items: flex-start; gap: 12px;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <div style="color: var(--text-primary); line-height: 1.6;">{content}</div>
        </div>
    </div>
    """


def create_success_card(content: str, icon: str = "✅") -> str:
    """Create a success card HTML."""
    return f"""
    <div class="success-card">
        <div style="display: flex; align-items: flex-start; gap: 12px;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <div style="color: var(--text-primary); line-height: 1.6;">{content}</div>
        </div>
    </div>
    """


def create_warning_card(content: str, icon: str = "⚠️") -> str:
    """Create a warning card HTML."""
    return f"""
    <div class="warning-card">
        <div style="display: flex; align-items: flex-start; gap: 12px;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <div style="color: var(--text-primary); line-height: 1.6;">{content}</div>
        </div>
    </div>
    """


def create_error_card(content: str, icon: str = "❌") -> str:
    """Create an error card HTML."""
    return f"""
    <div class="error-card">
        <div style="display: flex; align-items: flex-start; gap: 12px;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <div style="color: var(--text-primary); line-height: 1.6;">{content}</div>
        </div>
    </div>
    """


def create_alert(content: str, alert_type: str = "info") -> str:
    """Create an alert HTML (alias for card functions)."""
    if alert_type == "success":
        return create_success_card(content)
    elif alert_type == "warning":
        return create_warning_card(content)
    elif alert_type == "error":
        return create_error_card(content)
    else:
        return create_info_card(content)


# =============================================================================
# INSIGHT CARD
# =============================================================================
def create_insight_card(title: str, text: str, stagger: int = 1) -> str:
    """Create a premium insight card HTML."""
    return f"""
    <div class="insight-premium" style="animation-delay: {stagger * 0.15}s;">
        <div class="insight-title-premium">💡 {title}</div>
        <div class="insight-text-premium">{text}</div>
    </div>
    """


# =============================================================================
# SECTION & PAGE TITLES
# =============================================================================
def create_section_title(title: str, icon: str = "📊") -> str:
    """Create a section title HTML."""
    return f'<div class="section-title-premium">{icon} {title}</div>'


def create_page_title(title: str, color: str = "cyan") -> str:
    """Create a large page title HTML."""
    colors = {
        'cyan': '#06b6d4', 'blue': '#3b82f6', 'purple': '#8b5cf6',
        'pink': '#ec4899', 'green': '#10b981', 'orange': '#f59e0b'
    }
    accent = colors.get(color, '#06b6d4')
    return f'<h1 style="color: {accent}; font-size: 2.5rem; font-weight: 800; margin-bottom: 16px;">{title}</h1>'


# =============================================================================
# RECOMMENDATION BOX
# =============================================================================
def create_recommendation_box(title: str, items: list) -> str:
    """Create a recommendation box HTML."""
    items_html = "".join([f"<li style='margin: 8px 0;'>{item}</li>" for item in items])
    return f"""
    <div class="recommendation-premium" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(6, 182, 212, 0.1)); border-left: 4px solid #10b981;">
        <div style="color: #10b981; font-size: 1.3rem; font-weight: 800; margin-bottom: 16px;">📋 {title}</div>
        <ul style="color: var(--text-secondary); font-size: 1rem; line-height: 1.8; padding-left: 20px; margin: 0;">
            {items_html}
        </ul>
    </div>
    """


# =============================================================================
# FOOTER
# =============================================================================
def create_footer(title: str, subtitle: str, credits: str) -> str:
    """Create a premium footer HTML."""
    return f"""
    <div class="footer-premium">
        <div style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 12px;">
            {title}
        </div>
        <div style="color: var(--text-muted); font-size: 1rem; margin-bottom: 16px;">
            {subtitle}
        </div>
        <div class="gradient-text" style="font-weight: 800; font-size: 1.15rem;">
            {credits}
        </div>
    </div>
    """


def show_footer():
    """Display the default footer."""
    st.markdown(create_footer(
        "🚀 UAE Pulse Simulator + Data Rescue Dashboard",
        "Built with ❤️ by",
        "Kartik Joshi • Gagandeep Singh • Samuel Alex • Prem Kukreja"
    ), unsafe_allow_html=True)


# =============================================================================
# FEATURE CARD
# =============================================================================
def create_feature_card(icon: str, title: str, description: str, color: str = "cyan") -> str:
    """Create a feature card HTML."""
    colors = {
        "cyan": "#06b6d4", "blue": "#3b82f6", "purple": "#8b5cf6",
        "pink": "#ec4899", "green": "#10b981", "orange": "#f59e0b"
    }
    primary = colors.get(color, "#06b6d4")
    
    return f"""
    <div class="premium-container" style="height: 220px; text-align: center; padding: 30px 20px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <div style="font-size: 48px; margin-bottom: 16px; animation: float 3s ease-in-out infinite;">{icon}</div>
        <div style="color: {primary}; font-size: 1.15rem; font-weight: 700; margin-bottom: 10px;">{title}</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">{description}</div>
    </div>
    """


# =============================================================================
# STATUS DOT
# =============================================================================
def create_status_dot(color: str = "green") -> str:
    """Create a breathing status dot HTML."""
    return f'<div class="status-dot {color}"></div>'


# =============================================================================
# HERO SECTION
# =============================================================================
def create_hero_section(title: str, subtitle: str, badges: list = None) -> str:
    """Create a hero section HTML."""
    badges_html = ""
    if badges:
        for text, color in badges:
            badges_html += f'''
            <span style="display: inline-block; padding: 10px 24px; background: linear-gradient(135deg, var(--accent-{color}), var(--accent-blue)); border-radius: 50px; color: white; font-size: 0.9rem; font-weight: 600; margin-right: 10px; margin-bottom: 10px;">{text}</span>
            '''
    
    return f"""
    <div class="premium-container" style="padding: 50px 40px; margin-bottom: 32px; background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(139, 92, 246, 0.1), rgba(236, 72, 153, 0.05));">
        <div style="margin-bottom: 20px;">{badges_html}</div>
        <h1 class="gradient-text" style="font-size: 3.5rem; font-weight: 900; margin-bottom: 16px; line-height: 1.1;">{title}</h1>
        <p style="color: var(--text-secondary); font-size: 1.2rem; line-height: 1.6; margin: 0;">{subtitle}</p>
    </div>
    """


# =============================================================================
# PROGRESS BAR
# =============================================================================
def create_progress_bar(percent: float, color: str = "cyan") -> str:
    """Create an animated progress bar HTML."""
    colors = {
        'cyan': '#06b6d4', 'blue': '#3b82f6', 'purple': '#8b5cf6',
        'green': '#10b981', 'orange': '#f59e0b', 'red': '#ef4444'
    }
    bar_color = colors.get(color, '#06b6d4')
    
    return f"""
    <div style="background: var(--border-color); border-radius: 8px; height: 8px; overflow: hidden;">
        <div style="width: {percent}%; height: 100%; background: {bar_color}; border-radius: 8px; transition: width 0.5s ease;"></div>
    </div>
    """


# =============================================================================
# BADGE
# =============================================================================
def create_badge(text: str, badge_type: str = "primary") -> str:
    """Create a badge HTML."""
    colors = {
        'primary': 'linear-gradient(135deg, #06b6d4, #3b82f6)',
        'success': 'linear-gradient(135deg, #10b981, #14b8a6)',
        'warning': 'linear-gradient(135deg, #f59e0b, #fb923c)',
        'danger': 'linear-gradient(135deg, #ef4444, #ec4899)',
        'purple': 'linear-gradient(135deg, #8b5cf6, #ec4899)',
    }
    bg = colors.get(badge_type, colors['primary'])
    
    return f'<span style="display: inline-block; padding: 6px 14px; background: {bg}; border-radius: 50px; color: white; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">{text}</span>'


# =============================================================================
# STAT CARD (Simple)
# =============================================================================
def create_stat_card(label: str, value: str, icon: str = "📊", color: str = "cyan") -> str:
    """Create a simple stat card HTML."""
    colors = {
        'cyan': '#06b6d4', 'blue': '#3b82f6', 'purple': '#8b5cf6',
        'green': '#10b981', 'orange': '#f59e0b', 'red': '#ef4444'
    }
    accent = colors.get(color, '#06b6d4')
    
    return f"""
    <div class="premium-container" style="padding: 24px; text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
        <div style="color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">{label}</div>
        <div style="color: {accent}; font-size: 1.8rem; font-weight: 800; margin-top: 8px;">{value}</div>
    </div>
    """


# =============================================================================
# EXPORT ALL FUNCTIONS
# =============================================================================
__all__ = [
    'load_premium_css',
    'get_theme_colors',
    'get_plotly_template',
    'create_metric_card',
    'create_info_card',
    'create_success_card',
    'create_warning_card',
    'create_error_card',
    'create_alert',
    'create_insight_card',
    'create_section_title',
    'create_page_title',
    'create_recommendation_box',
    'create_footer',
    'show_footer',
    'create_feature_card',
    'create_status_dot',
    'create_hero_section',
    'create_progress_bar',
    'create_badge',
    'create_stat_card',
]
