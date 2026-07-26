"""
core/ui.py — Shared "Chalkboard & Red Pen" design system for Reverse Tutor AI.

Every page calls inject_base_css() once, near the top, right after
st.set_page_config(). The rest of this module is small, reusable HTML
snippets (score circles, misconception call-outs, turn-progress dots,
topic chips) that keep the same look everywhere they're used.

Design tokens (see palette below) are the single source of truth —
change a color here and it updates across the whole app.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
BG_DEEP = "#10201A"       # page background — chalkboard
BG_PANEL = "#172B22"      # card / panel surface
CHALK_WHITE = "#F5F1E6"   # headings
CHALK_SAGE = "#A8BFB0"    # body text
CHALK_YELLOW = "#E8C468"  # primary accent — chalk stick
PEN_RED = "#E2626B"       # corrections / errors — red pen
SLATE_TEAL = "#5FB8A6"    # correct / success, distinct from yellow

# A gently wobbly circle path used for the hand-drawn score badge
_CHALK_CIRCLE_PATH = (
    "M50,10 C70,8 92,25 90,50 C88,75 70,92 48,90 "
    "C25,88 8,70 10,45 C12,22 30,8 50,10 Z"
)


def inject_base_css() -> None:
    """Inject the shared chalkboard design system. Call once per page,
    right after st.set_page_config()."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

        :root {{
            --bg-deep: {BG_DEEP};
            --bg-panel: {BG_PANEL};
            --chalk-white: {CHALK_WHITE};
            --chalk-sage: {CHALK_SAGE};
            --chalk-yellow: {CHALK_YELLOW};
            --pen-red: {PEN_RED};
            --slate-teal: {SLATE_TEAL};
        }}

        /* ---- Base page ---------------------------------------------------- */
        .stApp {{
            background:
                radial-gradient(circle at 15% 8%, rgba(232,196,104,0.05), transparent 40%),
                radial-gradient(circle at 85% 92%, rgba(95,184,166,0.05), transparent 40%),
                var(--bg-deep);
            color: var(--chalk-sage);
            font-family: 'Inter', sans-serif;
        }}
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

        h1, h2, h3 {{
            font-family: 'Kalam', cursive;
            color: var(--chalk-white) !important;
            font-weight: 700;
            letter-spacing: 0.2px;
        }}
        h4, h5, h6 {{ color: var(--chalk-white) !important; }}
        p, li, label, span {{ color: var(--chalk-sage); }}
        strong {{ color: var(--chalk-white); }}

        /* ---- Dividers: dashed chalk line instead of a plain hr ------------ */
        hr {{
            border: none;
            border-top: 2px dashed rgba(168,191,176,0.35);
            margin: 1.6rem 0;
        }}

        /* ---- Buttons -------------------------------------------------------*/
        [data-testid="stButton"] button,
        [data-testid="baseButton-primary"],
        [data-testid="baseButton-secondary"] {{
            border-radius: 8px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            border: 2px solid var(--chalk-yellow);
            transition: transform 0.12s ease, box-shadow 0.12s ease;
        }}
        [data-testid="stButton"] button[kind="primary"],
        [data-testid="baseButton-primary"] {{
            background: var(--chalk-yellow);
            color: var(--bg-deep) !important;
        }}
        [data-testid="stButton"] button[kind="secondary"],
        [data-testid="baseButton-secondary"] {{
            background: transparent;
            color: var(--chalk-yellow) !important;
        }}
        [data-testid="stButton"] button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 0 rgba(0,0,0,0.25);
        }}

        /* ---- Text inputs / text areas -------------------------------------*/
        [data-testid="stTextArea"] textarea,
        [data-testid="stTextInput"] input {{
            background: var(--bg-panel) !important;
            border: 2px dashed rgba(168,191,176,0.4) !important;
            border-radius: 8px !important;
            color: var(--chalk-white) !important;
            font-family: 'Inter', sans-serif;
        }}
        [data-testid="stTextArea"] textarea:focus,
        [data-testid="stTextInput"] input:focus {{
            border-color: var(--chalk-yellow) !important;
        }}

        /* ---- Selectbox / slider -------------------------------------------*/
        [data-baseweb="select"] > div {{
            background: var(--bg-panel) !important;
            border: 2px dashed rgba(168,191,176,0.4) !important;
            border-radius: 8px !important;
        }}

        /* ---- Metrics --------------------------------------------------------*/
        [data-testid="stMetric"] {{
            background: var(--bg-panel);
            border-radius: 10px;
            border-left: 4px solid var(--chalk-yellow);
            padding: 0.9rem 1rem;
        }}
        [data-testid="stMetricValue"] {{
            font-family: 'IBM Plex Mono', monospace;
            color: var(--chalk-white) !important;
        }}

        /* ---- Alerts (info / success / error / warning) --------------------*/
        [data-testid="stAlert"] {{
            border-radius: 10px;
            background: var(--bg-panel);
            border: 1px solid rgba(168,191,176,0.25);
        }}

        /* ---- Dataframe ------------------------------------------------------*/
        [data-testid="stDataFrame"] {{
            border: 2px dashed rgba(168,191,176,0.3);
            border-radius: 10px;
        }}

        /* ---- Sidebar ----------------------------------------------------------*/
        [data-testid="stSidebar"] {{
            background: var(--bg-panel);
            border-right: 2px dashed rgba(168,191,176,0.25);
        }}

        /* ---- Chat messages ---------------------------------------------------*/
        [data-testid="stChatMessage"] {{
            background: var(--bg-panel);
            border: 2px dashed rgba(168,191,176,0.3);
            border-radius: 12px;
        }}

        /* ---- Custom components (see below) ------------------------------- */
        .chalk-hero {{
            text-align: center;
            padding: 3rem 1.5rem 2.5rem 1.5rem;
            background: var(--bg-panel);
            border: 2px dashed rgba(232,196,104,0.35);
            border-radius: 18px;
            margin-bottom: 1.6rem;
        }}
        .chalk-hero h1 {{
            font-size: 3.2rem;
            margin: 0;
        }}
        .chalk-hero .tagline {{
            font-family: 'IBM Plex Mono', monospace;
            color: var(--chalk-yellow);
            font-size: 0.85rem;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 0.6rem;
        }}
        .chalk-hero p {{
            font-size: 1.05rem;
            color: var(--chalk-sage);
            max-width: 640px;
            margin: 0.8rem auto 0 auto;
        }}

        .index-card {{
            background: var(--bg-panel);
            border: 2px solid rgba(168,191,176,0.25);
            border-bottom: none;
            border-radius: 14px 14px 0 0;
            padding: 1.4rem 1.2rem 1.1rem 1.2rem;
            min-height: 190px;
            transition: transform 0.15s ease;
        }}
        .index-card:hover {{ transform: translateY(-4px) rotate(-0.3deg); }}
        .index-card h3 {{ font-size: 1.15rem; margin: 0 0 0.5rem 0; }}
        .index-card p {{ font-size: 0.88rem; margin: 0; }}

        .topic-chip {{
            display: inline-block;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.78rem;
            color: var(--bg-deep);
            background: var(--chalk-yellow);
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            font-weight: 600;
        }}

        .turn-dots {{ display: flex; gap: 6px; align-items: center; }}
        .turn-dot {{
            width: 10px; height: 10px; border-radius: 50%;
            border: 2px solid var(--chalk-yellow);
            background: transparent;
        }}
        .turn-dot.filled {{ background: var(--chalk-yellow); }}

        .chalk-score-wrap {{ display: flex; align-items: center; gap: 1.2rem; }}
        .chalk-score-svg {{ width: 92px; height: 92px; flex-shrink: 0; }}
        .chalk-score-num {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 1.5rem;
            font-weight: 600;
        }}
        .chalk-score-label {{
            font-family: 'Inter', sans-serif;
            font-size: 0.82rem;
            color: var(--chalk-sage);
        }}

        .misconception-block {{
            background: var(--bg-panel);
            border: 2px dashed var(--pen-red);
            border-radius: 10px;
            padding: 1rem 1.1rem;
            margin: 0.6rem 0;
        }}
        .misconception-block .label {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--pen-red);
        }}
        .misconception-block .text {{
            color: var(--chalk-white);
            text-decoration: underline wavy var(--pen-red);
            text-decoration-thickness: 2px;
            text-underline-offset: 4px;
        }}

        .correction-block {{
            background: var(--bg-panel);
            border: 2px solid var(--slate-teal);
            border-radius: 10px;
            padding: 1rem 1.1rem;
            margin: 0.6rem 0;
        }}
        .correction-block .label {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--slate-teal);
        }}
        .correction-block .text {{ color: var(--chalk-white); }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _score_color(score: int) -> str:
    if score >= 7:
        return SLATE_TEAL
    elif score >= 4:
        return CHALK_YELLOW
    else:
        return PEN_RED


def render_score_badge(score: int, label: str) -> None:
    """Hand-drawn chalk-circle score badge — the app's signature element."""
    color = _score_color(score)
    st.markdown(
        f"""
        <div class="chalk-score-wrap">
            <svg class="chalk-score-svg" viewBox="0 0 100 100">
                <path d="{_CHALK_CIRCLE_PATH}" fill="none" stroke="{color}" stroke-width="4" />
                <text x="50" y="57" text-anchor="middle"
                      font-family="IBM Plex Mono, monospace" font-size="26"
                      font-weight="600" fill="{color}">{score}</text>
            </svg>
            <div>
                <div class="chalk-score-num" style="color:{color};">{score}/10</div>
                <div class="chalk-score-label">{label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_misconception_block(misconception: str, correction: str | None = None) -> None:
    """Red-pen annotated misconception, with an optional teal correction below."""
    st.markdown(
        f"""
        <div class="misconception-block">
            <div class="label">✗ Misconception found</div>
            <div class="text">{misconception}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if correction:
        st.markdown(
            f"""
            <div class="correction-block">
                <div class="label">✓ Correct explanation</div>
                <div class="text">{correction}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_turn_dots(current: int, total: int) -> None:
    """Small row of filled/empty dots showing conversation progress."""
    dots = "".join(
        f'<div class="turn-dot{" filled" if i < current else ""}"></div>'
        for i in range(total)
    )
    st.markdown(f'<div class="turn-dots">{dots}</div>', unsafe_allow_html=True)


def render_topic_chip(topic: str) -> str:
    """Return an inline HTML chip for a topic — embed inside other markdown."""
    return f'<span class="topic-chip">{topic}</span>'


def render_hero(tagline: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="chalk-hero">
            <div class="tagline">{tagline}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
