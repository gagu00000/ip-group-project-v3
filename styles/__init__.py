"""
Premium Theme CSS Loader for Streamlit
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


def load_premium_css(theme: str = "dark", include_orbs: bool = True) -> None:
    """Load premium CSS theme into Streamlit app."""
    
    # Load main CSS
    css = load_css_file("premium_theme.css")
    
    # If CSS loaded, inject it
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    # Floating orbs - inject separately
    if include_orbs:
        st.markdown("""
        <div class="floating-orbs">
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="orb orb-3"></div>
            <div class="orb orb-4"></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Light theme script
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


def create_metric_card(label: str, value: str, delta: str = None, delta_type: str = "positive", color: str = "cyan", stagger: int = 1) -> str:
    """Create a premium metric card HTML."""
    colors = {
        'cyan': '#06b6d4', 'blue': '#3b82f6', 'purple': '#8b5cf6',
        'pink': '#ec4899', 'green': '#10b981', 'orange': '#f59e0b',
        'teal': '#14b8a6', 'red': '#ef4444'
    }
    accent = colors.get(color, '#06b6d4')
    delta_color = "#10b981" if delta_type == "positive" else "#ef4444"
    arrow = "↑" if delta_type == "positive" else "↓"
    
    delta_html = f'<div style="font-size: 0.85rem; color: {delta_color};">{arrow} {delta}</div>' if delta else ''
    
    return f"""
    <div class="metric-card-premium stagger-{stagger}">
        <div class="metric-label-premium">{label}</div>
        <div class="metric-value-premium" style="color: {accent};">{value}</div>
        {delta_html}
    </div>
    """


def create_insight_card(title: str, text: str, stagger: int = 1) -> str:
    """Create a premium insight card HTML."""
    return f"""
    <div class="insight-premium stagger-{stagger}">
        <div class="insight-title-premium">💡 {title}</div>
        <div class="insight-text-premium">{text}</div>
    </div>
    """


def create_alert(content: str, alert_type: str = "info") -> str:
    """Create an alert HTML."""
    icons = {'info': 'ℹ️', 'success': '✅', 'warning': '⚠️', 'error': '❌'}
    icon = icons.get(alert_type, 'ℹ️')
    return f'<div class="alert-{alert_type}">{icon} {content}</div>'


def create_section_title(title: str, icon: str = "📊") -> str:
    """Create a section title HTML."""
    return f'<div class="section-title-premium">{icon} {title}</div>'


def create_page_title(title: str, color: str = "cyan") -> str:
    """Create a large page title HTML."""
    return f'<h1 class="page-title-premium">{title}</h1>'


def create_recommendation_box(title: str, items: list) -> str:
    """Create a recommendation box HTML."""
    items_html = "<br>".join([f"• {item}" for item in items])
    return f"""
    <div class="recommendation-premium">
        <div style="color: #10b981; font-size: 1.4rem; font-weight: 800; margin-bottom: 16px;">📋 {title}</div>
        <div style="color: var(--text-secondary); font-size: 1.05rem; line-height: 1.9;">{items_html}</div>
    </div>
    """


def create_footer(title: str, subtitle: str, credits: str) -> str:
    """Create a premium footer HTML."""
    return f"""
    <div class="footer-premium">
        <div style="font-size: 1.3rem; font-weight: 700; margin-bottom: 12px;">{title}</div>
        <div style="color: var(--text-muted); margin-bottom: 16px;">{subtitle}</div>
        <div class="gradient-text" style="font-weight: 800; font-size: 1.15rem;">{credits}</div>
    </div>
    """


def create_status_dot(color: str = "green") -> str:
    """Create a breathing status dot HTML."""
    return f'<div class="status-dot {color}"></div>'


def create_feature_card(icon: str, title: str, description: str, color: str = "cyan") -> str:
    """Create a feature card HTML."""
    colors = {"cyan": "#06b6d4", "blue": "#3b82f6", "purple": "#8b5cf6", "pink": "#ec4899", "green": "#10b981", "orange": "#f59e0b"}
    primary = colors.get(color, "#06b6d4")
    
    return f"""
    <div class="premium-container" style="height: 220px; text-align: center; padding: 30px 20px;">
        <div style="font-size: 48px; margin-bottom: 16px;">{icon}</div>
        <div style="color: {primary}; font-size: 1.15rem; font-weight: 700; margin-bottom: 10px;">{title}</div>
        <div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5;">{description}</div>
    </div>
    """


# Export all functions
__all__ = [
    'load_premium_css',
    'get_theme_colors',
    'get_plotly_template',
    'create_metric_card',
    'create_insight_card',
    'create_alert',
    'create_section_title',
    'create_page_title',
    'create_recommendation_box',
    'create_footer',
    'create_status_dot',
    'create_feature_card',
]
