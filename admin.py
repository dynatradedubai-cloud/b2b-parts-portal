import streamlit as st
import os
import pandas as pd

from database import save_encrypted_file, load_encrypted_file

LOG_FILE = "logs/audit_log.csv"


# =============================
# HEADER
# =============================
def render_header():

    col1, col2 = st.columns([1, 5])

    with col1:
        if os.path.exists("dynatrade_logo.png"):
            st.image("dynatrade_logo.png", width=90)

    with col2:
        st.markdown("### Dynatrade Admin Panel")

    st.markdown("---")


# =============================
# ADMIN DASHBOARD
# =============================
def admin_dashboard():

    render_header()

    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Users",
        "📦 Price",
        "📢 Campaigns",
        "📊 Analytics"
    ])

    # USERS
    with tab1:
        file = st.file_uploader("Upload Users", type=["xlsx"])
        if file:
            ok, msg = save_encrypted_file(file, "users")
            st.success(msg)
            st.cache_data.clear()

    # PRICE
    with tab2:
        file = st.file_uploader("Upload Price", type=["xlsx"])
        if file:
            ok, msg = save_encrypted_file(file, "price")
            st.success(msg)
            st.cache_data.clear()

    # CAMPAIGNS
    with tab3:
        file = st.file_uploader("Upload Campaign")
        if file:
            os.makedirs("data", exist_ok=True)
            with open(f"data/{file.name}", "wb") as f:
                f.write(file.read())
            st.success("Uploaded")

    # ANALYTICS
    with tab4:

        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:

            df = pd.read_csv(LOG_FILE)

            st.markdown("### Recent Activity")
            st.dataframe(df.tail(20))

            st.markdown("### Event Summary")
            st.dataframe(df["event"].value_counts())

            st.download_button(
                "Download Logs",
                df.to_csv(index=False),
                "logs.csv"
            )
        else:
            st.info("No logs yet")
