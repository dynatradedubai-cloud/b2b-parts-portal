import streamlit as st
import os
import pandas as pd
from database import save_encrypted_file, load_encrypted_file


# =============================
# HEADER (SAME STYLE AS CUSTOMER)
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
# CARD WRAPPER
# =============================
def card(title):
    st.markdown(f"### {title}")
    st.markdown('<div class="card">', unsafe_allow_html=True)


# =============================
# ADMIN DASHBOARD
# =============================
def admin_dashboard():

    render_header()

    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Users",
        "📦 Price List",
        "📢 Campaigns",
        "📊 Logs"
    ])

    # =============================
    # USERS
    # =============================
    with tab1:

        card("Upload Users File")

        file = st.file_uploader("Upload Users Excel", type=["xlsx"])

        if file:
            ok, msg = save_encrypted_file(file, "users")
            if ok:
                st.success(msg)
            else:
                st.error(msg)
            st.cache_data.clear()

        df = load_encrypted_file("users")

        if df is not None:
            st.dataframe(df)

        st.markdown('</div>', unsafe_allow_html=True)

    # =============================
    # PRICE
    # =============================
    with tab2:

        card("Upload Price List")

        file = st.file_uploader("Upload Price Excel", type=["xlsx"])

        if file:
            ok, msg = save_encrypted_file(file, "price")
            if ok:
                st.success(msg)
            else:
                st.error(msg)
            st.cache_data.clear()

        df = load_encrypted_file("price")

        if df is not None:
            st.dataframe(df.head(50))

        st.markdown('</div>', unsafe_allow_html=True)

    # =============================
    # CAMPAIGNS
    # =============================
    with tab3:

        card("Upload Campaigns")

        file = st.file_uploader("Upload Campaign File")

        if file:
            os.makedirs("data", exist_ok=True)
            path = f"data/{file.name}"

            with open(path, "wb") as f:
                f.write(file.read())

            st.success("Uploaded successfully")

        st.markdown('</div>', unsafe_allow_html=True)

    # =============================
    # LOGS
    # =============================
    with tab4:

        card("System Logs")

        log_file = "logs/audit_log.csv"

        if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
            df = pd.read_csv(log_file)
            st.dataframe(df.tail(20))
        else:
            st.info("No logs yet")

        st.markdown('</div>', unsafe_allow_html=True)
