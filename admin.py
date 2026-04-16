import streamlit as st
from database import save_encrypted_file, load_encrypted_file
import pandas as pd
import os

def admin_dashboard():
    st.title("🔐 Admin Panel")

    tabs = st.tabs([
        "👤 Users",
        "📦 Price List",
        "📢 Campaigns",
        "📊 Audit Logs"
    ])

    # =============================
    # USERS
    # =============================

    with tabs[0]:
        file = st.file_uploader("Upload Users Excel")

        if file:
            ok, msg = save_encrypted_file(file, "users")
            if ok:
                st.success(msg)
            else:
                st.error(msg)

        df = load_encrypted_file("users")

        if df is not None:
            st.dataframe(df)

    # =============================
    # PRICE
    # =============================

    with tabs[1]:
        file = st.file_uploader("Upload Price List")

        if file:
            ok, msg = save_encrypted_file(file, "price")
            if ok:
                st.success(msg)
            else:
                st.error(msg)

        df = load_encrypted_file("price")

        if df is not None:
            st.dataframe(df.head(50))

    # =============================
    # CAMPAIGNS
    # =============================

    with tabs[2]:
        file = st.file_uploader("Upload Campaign")

        if file:
            path = f"data/campaign_{file.name}"
            with open(path, "wb") as f:
                f.write(file.read())
            st.success("Campaign uploaded")

    # =============================
    # LOGS
    # =============================

    with tabs[3]:
        log_file = "logs/audit_log.csv"

        if os.path.exists(log_file):
            df = pd.read_csv(log_file)
            st.dataframe(df.tail(10))

            st.download_button(
                "Download Logs",
                df.to_csv(index=False),
                file_name="audit_logs.csv"
            )
        else:
            st.info("No logs available")
