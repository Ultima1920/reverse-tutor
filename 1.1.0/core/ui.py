"""
core/ui.py
Modern UI Components for Reverse Tutor AI
"""

from __future__ import annotations

import streamlit as st
from html import escape
import textwrap

# ==========================================================
# THEME COLORS
# ==========================================================

PRIMARY = "#6366F1"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
DANGER = "#EF4444"

BACKGROUND = "#0F172A"
CARD = "#1E293B"
CARD_LIGHT = "#273549"

BORDER = "#334155"

TEXT = "#F8FAFC"
SUBTEXT = "#94A3B8"

# ==========================================================
# BASE CSS  (unchanged — this one already works)
# ==========================================================

def inject_base_css():
    st.markdown(
        textwrap.dedent(f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            html, body, [class*="css"] {{
                font-family: 'Inter', sans-serif;
                background:{BACKGROUND};
                color:{TEXT};
            }}
            .stApp{{ background:{BACKGROUND}; }}
            section[data-testid="stSidebar"]{{
                background:#111827;
                border-right:1px solid {BORDER};
            }}
            section[data-testid="stSidebar"] *{{ color:{TEXT}; }}
            h1,h2,h3,h4,h5,h6{{ color:{TEXT}; font-weight:700; }}
            p,span,label,div{{ color:{TEXT}; }}
            small{{ color:{SUBTEXT}; }}
            hr{{ border:none; height:1px; background:{BORDER}; margin:30px 0; }}
            div[data-testid="stMetric"]{{
                background:{CARD}; border:1px solid {BORDER}; padding:20px; border-radius:16px;
            }}
            div[data-testid="stMetricLabel"]{{ color:{SUBTEXT}; font-size:14px; }}
            div[data-testid="stMetricValue"]{{ font-size:28px; font-weight:700; }}
            .stButton>button{{
                background:{PRIMARY}; color:white; border:none; border-radius:12px;
                padding:12px 20px; font-weight:600; width:100%;
            }}
            .stButton>button:hover{{ background:#4F46E5; }}
            .stTextInput input, .stTextArea textarea{{
                background:{CARD}; color:{TEXT}; border:1px solid {BORDER}; border-radius:12px;
            }}
            .stTextInput input:focus, .stTextArea textarea:focus{{ border:1px solid {PRIMARY}; }}
            .stSelectbox div[data-baseweb="select"]{{ background:{CARD}; }}
            .stSlider{{ padding-top:10px; }}
            .block-container{{ padding-top:2rem; padding-bottom:2rem; max-width:1200px; }}
            .hero{{
                background:linear-gradient(135deg, #1E293B, #111827);
                padding:40px; border-radius:22px; border:1px solid {BORDER}; margin-bottom:30px;
            }}
            .hero-title{{ font-size:48px; font-weight:800; margin-bottom:10px; }}
            .hero-sub{{ font-size:18px; color:{SUBTEXT}; }}
            .card{{
                background:{CARD}; border:1px solid {BORDER}; border-radius:18px;
                padding:22px; margin-bottom:18px;
            }}
            .info-card{{ background:{CARD}; border-left:5px solid {PRIMARY}; padding:20px; border-radius:16px; margin-bottom:18px; }}
            .success-card{{ background:{CARD}; border-left:5px solid {SUCCESS}; padding:20px; border-radius:16px; margin-bottom:18px; }}
            .warning-card{{ background:{CARD}; border-left:5px solid {WARNING}; padding:20px; border-radius:16px; margin-bottom:18px; }}
            .danger-card{{ background:{CARD}; border-left:5px solid {DANGER}; padding:20px; border-radius:16px; margin-bottom:18px; }}
            .topic-chip{{
                display:inline-block; padding:8px 18px; border-radius:999px;
                background:{PRIMARY}; color:white; font-weight:600; font-size:14px;
            }}
            .chat-user{{ background:#2563EB20; border:1px solid #2563EB; padding:18px; border-radius:16px; margin:12px 0; }}
            .chat-ai{{ background:#10B98120; border:1px solid #10B981; padding:18px; border-radius:16px; margin:12px 0; }}
            .footer{{ text-align:center; padding:30px; color:{SUBTEXT}; }}
            .badge{{
                display:inline-block; padding:8px 14px; background:{PRIMARY};
                border-radius:999px; font-size:13px; font-weight:600; margin-bottom:15px;
            }}
            .score-good{{ background:{SUCCESS}; }}
            .score-mid{{ background:{WARNING}; }}
            .score-bad{{ background:{DANGER}; }}
            </style>
        """),
        unsafe_allow_html=True,
    )


# ==========================================================
# PAGE HEADER
# ==========================================================

def render_page_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a modern page hero/header."""
    icon_html = f"<div style='font-size:58px;margin-bottom:12px;'>{icon}</div>" if icon else ""

    st.markdown(
        f'<div class="hero">{icon_html}'
        f'<div class="hero-title">{escape(title)}</div>'
        f'<div class="hero-sub">{escape(subtitle)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ==========================================================
# METRIC CARD
# ==========================================================

def render_metric_card(title: str, value: str, color: str = PRIMARY):
    """Beautiful metric card."""
    st.markdown(
        f'<div class="card">'
        f'<div style="color:{SUBTEXT};font-size:14px;margin-bottom:8px;font-weight:500;">{escape(title)}</div>'
        f'<div style="font-size:34px;font-weight:800;color:{color};">{escape(str(value))}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ==========================================================
# INFO CARD
# ==========================================================

def render_info_card(title: str, body: str, variant: str = "info"):
    """Display information cards."""
    cls = {
        "info": "info-card",
        "success": "success-card",
        "warning": "warning-card",
        "danger": "danger-card",
    }.get(variant, "info-card")

    st.markdown(
        f'<div class="{cls}">'
        f'<h4 style="margin-top:0;">{escape(title)}</h4>'
        f'<div style="color:{SUBTEXT};line-height:1.7;">{body}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ==========================================================
# TOPIC CHIP
# ==========================================================

def render_topic_chip(topic: str):
    """Return a pill-shaped topic badge."""
    return f'<span class="topic-chip">📘 {escape(topic)}</span>'


# ==========================================================
# TURN DOTS
# ==========================================================

def render_turn_dots(turn: int, total: int = 4):
    """Progress dots."""
    cols = st.columns(total)

    for i, col in enumerate(cols, start=1):
        color = PRIMARY if i <= turn else BORDER

        with col:
            st.markdown(
                f'<div style="width:18px;height:18px;margin:auto;'
                f'border-radius:50%;background:{color};"></div>',
                unsafe_allow_html=True,
            )


# ==========================================================
# CHAT CARD
# ==========================================================

def render_chat_card(role: str, message: str):
    """
    Beautiful chat bubble.
    role: "user" or "assistant"
    """
    if role == "user":
        cls, avatar, name = "chat-user", "🧑‍🎓", "You"
    else:
        cls, avatar, name = "chat-ai", "🤔", "Alex"

    st.markdown(
        f'<div class="{cls}">'
        f'<div style="font-weight:700;margin-bottom:10px;">{avatar} {name}</div>'
        f'<div style="line-height:1.8;color:{TEXT};">{escape(message)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ==========================================================
# SECTION TITLE
# ==========================================================

def render_section(title: str):
    st.markdown(
        f'<h2 style="margin-top:30px;margin-bottom:18px;font-size:28px;font-weight:700;">'
        f'{escape(title)}</h2>',
        unsafe_allow_html=True,
    )


# ==========================================================
# HORIZONTAL DIVIDER
# ==========================================================

def render_divider():
    st.markdown("<hr>", unsafe_allow_html=True)


# ==========================================================
# SCORE BADGE
# ==========================================================

def render_score_badge(score: int | float, label: str = ""):
    """Render a clarity score badge."""
    score = max(0, min(10, int(score)))

    if score >= 8:
        cls = "score-good"
    elif score >= 5:
        cls = "score-mid"
    else:
        cls = "score-bad"

    st.markdown(
        f'<div class="card" style="text-align:center;">'
        f'<div style="font-size:15px;color:{SUBTEXT};margin-bottom:15px;">Clarity Score</div>'
        f'<div class="{cls}" style="width:110px;height:110px;border-radius:50%;margin:auto;'
        f'display:flex;align-items:center;justify-content:center;font-size:34px;'
        f'font-weight:800;color:white;">{score}/10</div>'
        f'<div style="margin-top:18px;font-weight:600;color:{TEXT};">{escape(label)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ==========================================================
# MISCONCEPTION BLOCK
# ==========================================================

def render_misconception_block(misconception: str, correction: str | None = None):
    """Display misconception and correction."""
    correction_html = ""

    if correction:
        correction_html = (
            f'<div style="margin-top:18px;padding-top:18px;border-top:1px solid {BORDER};">'
            f'<div style="color:{SUCCESS};font-weight:700;margin-bottom:8px;">✅ Correct Explanation</div>'
            f'<div style="color:{TEXT};line-height:1.7;">{escape(correction)}</div>'
            f'</div>'
        )

    st.markdown(
        f'<div class="danger-card">'
        f'<div style="color:{DANGER};font-size:18px;font-weight:700;margin-bottom:10px;">❌ Misconception</div>'
        f'<div style="color:{TEXT};line-height:1.7;">{escape(misconception)}</div>'
        f'{correction_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


# ==========================================================
# STATUS BADGE
# ==========================================================

def render_status_badge(text: str, color: str = PRIMARY):
    st.markdown(
        f'<span style="display:inline-block;background:{color};color:white;'
        f'padding:6px 14px;border-radius:999px;font-size:13px;font-weight:600;margin:4px 0;">'
        f'{escape(text)}</span>',
        unsafe_allow_html=True,
    )


# ==========================================================
# EMPTY STATE
# ==========================================================

def render_empty_state(title: str, body: str):
    st.markdown(
        f'<div class="card" style="text-align:center;padding:40px;">'
        f'<div style="font-size:46px;margin-bottom:12px;">📭</div>'
        f'<h3 style="margin-bottom:10px;">{escape(title)}</h3>'
        f'<p style="color:{SUBTEXT};max-width:500px;margin:auto;">{escape(body)}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ==========================================================
# FOOTER
# ==========================================================

def render_footer():
    st.markdown(
        f'<div class="footer"><hr>'
        f'<div style="font-size:22px;font-weight:700;margin-bottom:10px;">🎓 Reverse Tutor AI</div>'
        f'<div style="color:{SUBTEXT};margin-bottom:18px;">Teach • Explain • Discover • Improve</div>'
        f'<div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;">'
        f'<span class="topic-chip">🤖 Gemini</span>'
        f'<span class="topic-chip">🗄 SQLite</span>'
        f'<span class="topic-chip">⚡ Streamlit</span>'
        f'<span class="topic-chip">🧠 AI Learning</span>'
        f'</div>'
        f'<div style="margin-top:22px;color:{SUBTEXT};font-size:13px;">'
        f'Built for active learning using the Feynman Technique.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ==========================================================
# COMPATIBILITY HELPERS
# ==========================================================

def render_hero(title: str, subtitle: str = "", icon: str = "🎓"):
    """Backward-compatible wrapper."""
    render_page_header(title, subtitle, icon)


def render_status_card(title: str, body: str, variant: str = "info"):
    """Backward-compatible wrapper."""
    render_info_card(title, body, variant)


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [
    "inject_base_css",
    "render_page_header",
    "render_metric_card",
    "render_info_card",
    "render_status_card",
    "render_topic_chip",
    "render_turn_dots",
    "render_chat_card",
    "render_score_badge",
    "render_misconception_block",
    "render_status_badge",
    "render_empty_state",
    "render_footer",
    "render_section",
    "render_divider",
    "render_hero",
]
