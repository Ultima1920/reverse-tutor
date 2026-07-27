import streamlit as st
import pandas as pd
from core.db import get_connection

st.set_page_config(page_title="Misconception Library — Reverse Tutor AI", page_icon="📚", layout="wide")

st.title("📚 Misconception Library")
st.caption("These are the structured misconceptions the AI uses to role-play as a confused peer. Shown here for transparency and judge review.")

@st.cache_data(ttl=30)
def load_library():
    try:
        conn = get_connection()
        df = pd.read_sql_query(
            "SELECT topic as Topic, misconception as Misconception, correction as Correction FROM misconception_library ORDER BY topic",
            conn
        )
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame({"Error": [str(e)]})

df = load_library()

if df.empty or "Error" in df.columns:
    st.error("Could not load the misconception library. Is the database initialized?")
else:
    topics = ["All"] + sorted(df["Topic"].unique().tolist())
    selected = st.selectbox("🔍 Filter by Topic", topics)

    if selected != "All":
        filtered = df[df["Topic"] == selected]
    else:
        filtered = df

    st.markdown(f"**{len(filtered)}** entries {f'for *{selected}*' if selected != 'All' else 'total'}")
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Topic": st.column_config.TextColumn("Topic", width="small"),
            "Misconception": st.column_config.TextColumn("Common Misconception", width="medium"),
            "Correction": st.column_config.TextColumn("The Correct Explanation", width="large"),
        }
    )

    st.divider()
    st.info(
        "💡 These misconceptions are seeded in the local SQLite database (`student.db`). "
        "The AI uses them to guide which 'confusions' to express when a student teaches a topic."
    )
