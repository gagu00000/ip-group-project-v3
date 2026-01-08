"""
Premium Theme CSS Loader for Streamlit
======================================
UAE Promo Pulse Simulator Style Pack v4.0

Usage:
    from styles import load_premium_css, create_metric_card, ...
    load_premium_css(theme='dark', include_orbs=True)
"""

import streamlit as st
from pathlib import Path


def load_css_file(file_path: str) -> str:
    """Load CSS file and return as string."""
    css_path = Path(__file__).parent / file_path
    if css_path.exists():
        return css_path.read_text()
    return ""


def load_premium_css(theme: str = "dark", include_orbs: bool = True) -> None:
    """
    Load premium CSS theme into Streamlit app.
    
    Args:
        theme: "dark" or "light"
        include_orbs: Whether to include floating orbs background
    """
    # Load main CSS
    css = load_css_file("premium_theme.css")
    
    # Floating orbs HTML
    orbs_html = """
    <div class="floating-orbs">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
        <div class="orb orb-4"></div>
    </div>
    """ if include_orbs else ""
    
    # Theme class for body
    theme_script = ""
    if theme == "light":
        theme_script = """
        <script>
            const checkBody = setInterval(() => {
                const app = document.querySelector('.stApp');
                if (app) {
                    app.classList.add('light-theme');
                    clearInterval(checkBody);
                }
            }, 100);
        </script>
        """
    
    # Inject CSS and HTML
    st.markdown(f"""
    <style>
    {css}
    </style>
    {orbs_html}
    {theme_script}
    """, unsafe_allow_html=True)


def get_theme_colors(theme: str = "dark") -> dict:
    """
    Get theme colors as a dictionary for use in Python (e.g., Plotly charts).
    
    Args:
        theme: "dark" or "light"
    
    Returns:
        Dictionary of color values
    """
    if theme == "dark":
        return {
            'bg_primary': '#0a0a0f',
            'bg_secondary': '#12121a',
            'bg_card': '#16161f',
            'bg_card_hover': '#1e1e2d',
            'text_primary': '#f1f5f9',
            'text_secondary': '#94a3b8',
            'text_muted': '#64748b',
            'border_color': '#2d2d3a',
            'glass_bg': 'rgba(22, 22, 31, 0.7)',
            'accent_cyan': '#06b6d4',
            'accent_blue': '#3b82f6',
            'accent_purple': '#8b5cf6',
            'accent_pink': '#ec4899',
            'accent_green': '#10b981',
            'accent_orange': '#f59e0b',
            'accent_red': '#ef4444',
            'accent_teal': '#14b8a6',
        }
    else:
        return {
            'bg_primary': '#f8fafc',
            'bg_secondary': '#ffffff',
            'bg_card': '#ffffff',
            'bg_card_hover': '#f1f5f9',
            'text_primary': '#0f172a',
            'text_secondary': '#475569',
            'text_muted': '#64748b',
            'border_color': '#e2e8f0',
            'glass_bg': 'rgba(255, 255, 255, 0.7)',
            'accent_cyan': '#06b6d4',
            'accent_blue': '#3b82f6',
            'accent_purple': '#8b5cf6',
            'accent_pink': '#ec4899',
            'accent_green': '#10b981',
            'accent_orange': '#f59e0b',
            'accent_red': '#ef4444',
            'accent_teal': '#14b8a6',
        }


def get_plotly_template(theme: str = "dark") -> dict:
    """
    Get Plotly chart template matching the theme.
    
    Args:
        theme: "dark" or "light"
    
    Returns:
        Dictionary for Plotly layout
    """
    colors = get_theme_colors(theme)
    
    return {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {
            'color': colors['text_primary'],
            'family': 'Inter, sans-serif'
        },
        'title': {
            'font': {
                'color': colors['text_primary'],
                'size': 18,
                'family': 'Inter, sans-serif'
            }
        },
        'xaxis': {
            'gridcolor': colors['border_color'],
            'linecolor': colors['border_color'],
            'tickfont': {'color': colors['text_secondary']}
        },
        'yaxis': {
            'gridcolor': colors['border_color'],
            'linecolor': colors['border_color'],
            'tickfont': {'color': colors['text_secondary']}
        },
        'legend': {
            'font': {'color': colors['text_secondary']}
        },
        'margin': {'t': 60, 'b': 40, 'l': 40, 'r': 20}
    }


# =============================================================================
# COMPONENT HELPER FUNCTIONS
# =============================================================================

def create_metric_card(
    label: str, 
    value: str, 
    delta: str = None, 
    delta_type: str = "positive", 
    color: str = "cyan", 
    stagger: int = 1
) -> str:
    """
    Create a premium metric card HTML.
    
    Args:
        label: Card label/title
        value: Main value to display
        delta: Change value (e.g., "+12.5%")
        delta_type: "positive" or "negative"
        color: cyan, blue, purple, pink, green, orange, teal, red
        stagger: Animation delay index (1-8)
    
    Returns:
        HTML string for the metric card
    """
    colors = {
        'cyan': '#06b6d4', 
        'blue': '#3b82f6', 
        'purple': '#8b5cf6',
        'pink': '#ec4899', 
        'green': '#10b981', 
        'orange': '#f59e0b',
        'teal': '#14b8a6', 
        'red': '#ef4444'
    }
    accent = colors.get(color, '#06b6d4')
    delta_color = "#10b981" if delta_type == "positive" else "#ef4444"
    arrow = "↑" if delta_type == "positive" else "↓"
    
    if delta:
        delta_html = f'''
        <div class="metric-delta">
            <span class="arrow" style="color: {delta_color};">{arrow}</span> 
            <span style="color: {delta_color};">{delta}</span>
        </div>
        '''
    else:
        delta_html = '<div style="height: 18px;"></div>'
    
    return f"""
    <div class="metric-card-premium stagger-{stagger}" style="animation-delay: {stagger * 0.1}s;">
        <div class="metric-label-premium">{label}</div>
        <div class="metric-value-premium animate" style="color: {accent};">{value}</div>
        {delta_html}
    </div>
    """


def create_insight_card(title: str, text: str, stagger: int = 1) -> str:
    """
    Create a premium insight card HTML.
    
    Args:
        title: Insight title
        text: Insight description
        stagger: Animation delay index
    
    Returns:
        HTML string for the insight card
    """
    return f"""
    <div class="insight-premium stagger-{stagger}" style="animation-delay: {stagger * 0.15}s;">
        <div class="insight-title-premium">💡 {title}</div>
        <div class="insight-text-premium">{text}</div>
    </div>
    """


def create_alert(content: str, alert_type: str = "info") -> str:
    """
    Create an alert HTML.
    
    Args:
        content: Alert message
        alert_type: info, success, warning, error
    
    Returns:
        HTML string for the alert
    """
    icons = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    icon = icons.get(alert_type, 'ℹ️')
    return f'<div class="alert-{alert_type}">{icon} {content}</div>'


def create_badge(text: str, badge_type: str = "primary", glow: bool = False) -> str:
    """
    Create a badge HTML.
    
    Args:
        text: Badge text
        badge_type: primary, success, warning, danger, purple
        glow: Whether to add glow animation
    
    Returns:
        HTML string for the badge
    """
    glow_class = "badge-glow" if glow else ""
    return f'<span class="badge badge-{badge_type} {glow_class}">{text}</span>'


def create_status_dot(color: str = "green") -> str:
    """
    Create a breathing status dot HTML.
    
    Args:
        color: green, red, orange, blue, purple
    
    Returns:
        HTML string for the status dot
    """
    return f'<div class="status-dot {color}"></div>'


def create_progress_bar(percent: float) -> str:
    """
    Create an animated progress bar HTML.
    
    Args:
        percent: Progress percentage (0-100)
    
    Returns:
        HTML string for the progress bar
    """
    return f"""
    <div class="progress-bar">
        <div class="progress-bar-fill" style="width: {percent}%;"></div>
    </div>
    """


def create_section_title(title: str, icon: str = "📊") -> str:
    """
    Create a section title with gradient line HTML.
    
    Args:
        title: Section title text
        icon: Emoji icon
    
    Returns:
        HTML string for the section title
    """
    return f'<div class="section-title-premium">{icon} {title}</div>'


def create_page_title(title: str, color: str = "cyan") -> str:
    """
    Create a large page title HTML.
    
    Args:
        title: Page title text
        color: Accent color name
    
    Returns:
        HTML string for the page title
    """
    return f'<h1 class="page-title-premium" style="color: var(--accent-{color});">{title}</h1>'


def create_recommendation_box(title: str, items: list) -> str:
    """
    Create a recommendation box HTML.
    
    Args:
        title: Box title
        items: List of recommendation strings
    
    Returns:
        HTML string for the recommendation box
    """
    items_html = "<br>".join([f"• {item}" for item in items])
    return f"""
    <div class="recommendation-premium">
        <div style="color: #10b981; font-size: 1.4rem; font-weight: 800; margin-bottom: 16px;">📋 {title}</div>
        <div style="color: var(--text-secondary); font-size: 1.05rem; line-height: 1.9;">{items_html}</div>
    </div>
    """


def create_footer(title: str, subtitle: str, credits: str) -> str:
    """
    Create a premium footer HTML.
    
    Args:
        title: Footer title
        subtitle: Footer subtitle
        credits: Credits text (team names, etc.)
    
    Returns:
        HTML string for the footer
    """
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


def create_hero_section(
    title: str, 
    subtitle: str, 
    badges: list = None
) -> str:
    """
    Create a hero section HTML.
    
    Args:
        title: Main hero title
        subtitle: Hero subtitle/description
        badges: List of tuples [(text, color), ...]
    
    Returns:
        HTML string for the hero section
    """
    badges_html = ""
    if badges:
        for text, color in badges:
            badges_html += f'''
            <span style="
                display: inline-block;
                padding: 10px 24px;
                background: linear-gradient(135deg, var(--accent-{color}), var(--accent-blue));
                border-radius: 50px;
                color: white;
                font-size: 0.95rem;
                font-weight: 600;
                margin-right: 12px;
                margin-bottom: 10px;
            ">{text}</span>
            '''
    
    return f"""
    <div class="hero-premium">
        <div style="margin-bottom: 20px; position: relative; z-index: 1;">
            {badges_html}
        </div>
        <div class="hero-title-premium">{title}</div>
        <p style="color: var(--text-secondary); font-size: 1.2rem; margin: 0; line-height: 1.6; position: relative; z-index: 1;">
            {subtitle}
        </p>
    </div>
    """


def create_feature_card(
    icon: str, 
    title: str, 
    description: str, 
    color: str = "cyan"
) -> str:
    """
    Create a feature card HTML.
    
    Args:
        icon: Emoji icon
        title: Card title
        description: Card description
        color: Accent color
    
    Returns:
        HTML string for the feature card
    """
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
    <div class="premium-container feature-card" style="
        height: 220px; 
        min-height: 220px;
        max-height: 220px;
        text-align: center; 
        padding: 30px 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    ">
        <div style="font-size: 48px; margin-bottom: 16px; animation: float 3s ease-in-out infinite;">{icon}</div>
        <div style="color: {primary}; font-size: 1.15rem; font-weight: 700; margin-bottom: 10px;">{title}</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">{description}</div>
    </div>
    """


def create_stat_card(
    label: str, 
    value: str, 
    icon: str = "📊", 
    color: str = "cyan"
) -> str:
    """
    Create a simple stat card HTML.
    
    Args:
        label: Stat label
        value: Stat value
        icon: Emoji icon
        color: Accent color
    
    Returns:
        HTML string for the stat card
    """
    colors = {
        'cyan': '#06b6d4', 
        'blue': '#3b82f6', 
        'purple': '#8b5cf6',
        'pink': '#ec4899', 
        'green': '#10b981', 
        'orange': '#f59e0b',
        'teal': '#14b8a6', 
        'red': '#ef4444'
    }
    accent = colors.get(color, '#06b6d4')
    
    return f"""
    <div class="premium-container" style="padding: 20px; text-align: center;">
        <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
        <div style="color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">{label}</div>
        <div style="color: {accent}; font-size: 1.8rem; font-weight: 800; margin-top: 8px;">{value}</div>
    </div>
    """


# =============================================================================
# EXPORT ALL PUBLIC FUNCTIONS
# =============================================================================

__all__ = [
    'load_premium_css',
    'get_theme_colors',
    'get_plotly_template',
    'create_metric_card',
    'create_insight_card',
    'create_alert',
    'create_badge',
    'create_status_dot',
    'create_progress_bar',
    'create_section_title',
    'create_page_title',
    'create_recommendation_box',
    'create_footer',
    'create_hero_section',
    'create_feature_card',
    'create_stat_card',
]
