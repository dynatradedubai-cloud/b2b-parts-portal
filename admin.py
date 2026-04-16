import streamlit as st
import pandas as pd
import os
from database import save_encrypted_file, load_encrypted_file

def admin_dashboard():

    st.title("🔐 Dynatrade Admin Panel")

    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Users",
        "📦 Price List",
        "📢 Campaigns",
        "📊 Audit Logs"
    ])

    # =============================
    # USERS TAB
    # =============================
    with tab1:

        st.subheader("Upload Users File")

        file = st.file_uploader("Upload Users Excel", type=["xlsx"], key="users")

        if file is not None:
            ok, msg = save_encrypted_file(file, "users")
            if ok:
                st.success(msg)
                st.cache_data.clear()
            else:
                st.error(msg)

        df = load_encrypted_file("users")

        if df is not None:
            st.dataframe(df)

    # =============================
    # PRICE TAB
    # =============================
    with tab2:

        st.subheader("Upload Price List")

        file = st.file_uploader("Upload Price Excel", type=["xlsx"], key="price")

        if file is not None:
            ok, msg = save_encrypted_file(file, "price")
            if ok:
                st.success(msg)
                st.cache_data.clear()
            else:
                st.error(msg)

        df = load_encrypted_file("price")

        if df is not None:
            st.dataframe(df.head(50))

    # =============================
    # CAMPAIGNS TAB
    # =============================
    with tab3:

        st.subheader("Upload Campaign Files")

        file = st.file_uploader("Upload Campaign", type=["pdf", "png", "jpg", "xlsx"], key="campaign")

        if file is not None:
            os.makedirs("data", exist_ok=True)
            path = os.path.join("data", f"campaign_{file.name}")

            with open(path, "wb") as f:
                f.write(file.read())

            st.success("Campaign uploaded successfully")

    # =============================
    # AUDIT LOGS TAB
    # =============================
    with tab4:

        st.subheader("Audit Logs")

        log_file = "logs/audit_log.csv"

        # If file does not exist
        if not os.path.exists(log_file):
            st.info("No logs available yet")
            return

        # If file exists but empty
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
            st.error(f"Error loading logs: {str(e)}")

