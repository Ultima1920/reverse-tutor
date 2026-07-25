import streamlit as st
from core.db import get_connection
import pandas as pd

st.set_page_config(page_title="Misconception Library", page_icon="📚")

st.title("📚 Misconception Library")
st.write("This library contains the known misconceptions that the AI uses to act like a confused peer.")

try:
    conn = get_connection()
    df = pd.read_sql_query("SELECT topic as Topic, misconception as Misconception, correction as Correction FROM misconception_library", conn)
    conn.close()
    
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"Could not load library: {e}")
