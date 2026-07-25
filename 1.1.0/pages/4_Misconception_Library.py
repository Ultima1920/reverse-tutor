"""
pages/4_Misconception_Library.py — Browse the seeded misconception database.

A read-only view of the misconception_library table, filterable by topic.
"""

import streamlit as st
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Misconception Library — Reverse Tutor AI",
    page_icon="📚",
    layout="wide",
)

from core import db

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("📚 Misconception Library")
st.markdown(
    "A curated list of **common misconceptions** by topic, with corrections. "
    "These are the same misconceptions the AI uses to probe your understanding during sessions."
)
st.divider()

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
all_rows = db.get_all_misconceptions()
all_topics = ["All"] + db.get_all_topics()

# ---------------------------------------------------------------------------
# Topic filter
# ---------------------------------------------------------------------------
col_filter, col_count = st.columns([3, 1])

with col_filter:
    selected_topic = st.selectbox(
        "🔍 Filter by topic:",
        all_topics,
        key="ml_topic_filter",
    )

# Filter rows
if selected_topic == "All":
    filtered = all_rows
else:
    filtered = [r for r in all_rows if r["topic"] == selected_topic]

with col_count:
    st.metric("Entries shown", len(filtered))

# ---------------------------------------------------------------------------
# Misconception table
# ---------------------------------------------------------------------------
if not filtered:
    st.info("No misconceptions found for this filter.")
else:
    df = pd.DataFrame(filtered)[["topic", "misconception", "correction"]]
    df.columns = ["Topic", "Common Misconception", "Correct Explanation"]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Topic": st.column_config.TextColumn("Topic", width="small"),
            "Common Misconception": st.column_config.TextColumn(
                "Common Misconception", width="medium"
            ),
            "Correct Explanation": st.column_config.TextColumn(
                "Correct Explanation", width="large"
            ),
        },
    )

# ---------------------------------------------------------------------------
# Explanation panel for selected row (expandable)
# ---------------------------------------------------------------------------
st.divider()
st.subheader("📖 Explore a misconception in detail")

if filtered:
    topic_options = [f"[{r['topic']}] {r['misconception'][:60]}…" for r in filtered]
    selected_idx = st.selectbox("Choose one to expand:", range(len(filtered)),
                                format_func=lambda i: topic_options[i],
                                key="ml_expand_select")
    selected_row = filtered[selected_idx]

    with st.expander("View full details", expanded=True):
        st.markdown(f"**Topic:** {selected_row['topic']}")
        st.error(f"❌ **Misconception:** {selected_row['misconception']}")
        st.success(f"✅ **Correction:** {selected_row['correction']}")
