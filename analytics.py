import pandas as pd
import streamlit as st
import os

LOG_FILE = "logs/audit_log.csv"

def analytics_dashboard():

    st.markdown("## 📊 Analytics Dashboard")

    if not os.path.exists(LOG_FILE):
        st.info("No data yet")
        return

    df = pd.read_csv(LOG_FILE)

    if df.empty:
        st.info("No logs available")
        return

    # EVENT COUNT
    st.subheader("Event Summary")
    st.bar_chart(df["event"].value_counts())

    # SEARCH FAIL ANALYSIS
    fail_df = df[df["event"] == "SEARCH_FAIL"]

    if not fail_df.empty:
        st.subheader("Top Failed Searches")
        st.bar_chart(fail_df["detail"].value_counts().head(10))
