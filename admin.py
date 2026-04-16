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
            os.makedirs("data", exist_ok=True)
            path = f"data/campaign_{file.name}"
            with open(path, "wb") as f:
                f.write(file.read())

            st.success("Campaign uploaded")

    # =============================
    # LOGS (FIXED)
    # =============================

    with tabs[3]:
        log_file = "logs/audit_log.csv"

        if not os.path.exists(log_file):
            st.info("No logs available yet")
            return

        # 🔥 FIX: HANDLE EMPTY FILE
        if os.path.getsize(log_file) == 0:
            st.info("Logs file is empty")
            return

        try:
            df = pd.read_csv(log_file)

            if df.empty:
                st.info("No logs recorded yet")
                return

            st.dataframe(df.tail(10))

            st.download_button(
                "Download Logs",
                df.to_csv(index=False),
                file_name="audit_logs.csv"
            )

        except Exception as e:
            st.error(f"Failed to load logs: {str(e)}")
