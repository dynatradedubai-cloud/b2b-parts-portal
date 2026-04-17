import streamlit as st
import os
import pandas as pd

from database import save_encrypted_file
from analytics import analytics_dashboard


# =============================
# SAFE LOG LOAD
# =============================
def load_logs():

    log_file = "logs/audit_log.csv"

    if not os.path.exists(log_file):
        return pd.DataFrame(columns=["time", "user", "event", "detail"])

    try:
        df = pd.read_csv(log_file)

        # Validate structure
        required = ["time", "user", "event", "detail"]

        if list(df.columns) != required:
            return pd.DataFrame(columns=required)

        return df

    except:
        return pd.DataFrame(columns=["time", "user", "event", "detail"])


# =============================
# ADMIN DASHBOARD
# =============================
def admin_dashboard():

    st.markdown("## ⚙️ Admin Panel")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["👥 Users", "💰 Price", "📢 Campaigns", "📄 Logs", "📊 Analytics"]
    )

    # =============================
    # USERS
    # =============================
    with tab1:

        st.subheader("Upload Users File")

        file = st.file_uploader("Upload Users Excel", key="users")

        if file:
            save_encrypted_file(file, "users")
            st.success("✅ Users file uploaded & encrypted")

    # =============================
    # PRICE
    # =============================
    with tab2:

        st.subheader("Upload Price List")

        file = st.file_uploader("Upload Price Excel", key="price")

        if file:
            save_encrypted_file(file, "price")
            st.success("✅ Price file uploaded & encrypted")

    # =============================
    # CAMPAIGNS
    # =============================
    with tab3:

        st.subheader("Upload Campaign / Announcement")

        file = st.file_uploader("Upload File (PDF / Image / Excel)")

        if file:

            os.makedirs("data", exist_ok=True)

            file_path = os.path.join("data", file.name)

            with open(file_path, "wb") as f:
                f.write(file.read())

            st.success("✅ Campaign uploaded")

        # Show existing campaigns
        st.markdown("### 📁 Available Campaigns")

        if os.path.exists("data"):

            files = os.listdir("data")

            if files:
                for f in files:
                    st.write(f"📢 {f}")
            else:
                st.info("No campaigns uploaded")

    # =============================
    # LOGS
    # =============================
    with tab4:

        st.subheader("System Logs")

        df = load_logs()

        if df.empty:
            st.info("No logs available")
        else:
            st.dataframe(df.tail(50), use_container_width=True)

            # Download logs
            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "⬇️ Download Logs",
                csv,
                "logs.csv",
                "text/csv"
            )

    # =============================
    # ANALYTICS
    # =============================
    with tab5:

        analytics_dashboard()

    # =============================
    # FOOTER
    # =============================
    st.markdown("---")
    st.caption("Dynatrade Automotive LLC • Admin Panel")
