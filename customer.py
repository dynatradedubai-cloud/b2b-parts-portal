import streamlit as st
import os
from database import load_encrypted_file


# =============================
# HEADER
# =============================
def render_header():

    st.markdown('<div class="header">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 4])

    with col1:
        if os.path.exists("dynatrade_logo.png"):
            st.image("dynatrade_logo.png", width=100)

    with col2:
        st.markdown("### Dynatrade Automotive LLC")

    st.markdown('</div>', unsafe_allow_html=True)


# =============================
# DASHBOARD
# =============================
def customer_dashboard():

    render_header()

    st.markdown("### Welcome to Customer Portal")

    # =============================
    # SEARCH BOX
    # =============================
    search = st.text_input(
        "🔍 Search Parts",
        placeholder="Enter OE / MFG / Brand / Vehicle..."
    )

    # =============================
    # LOAD DATA
    # =============================
    df = load_encrypted_file("price")

    if df is None:
        st.warning("Price list not uploaded yet")
        return

    # =============================
    # FILTER RESULTS
    # =============================
    if search:
        search = search.lower()

        results = df[
            df.astype(str)
            .apply(lambda row: row.str.lower().str.contains(search).any(), axis=1)
        ]

    else:
        results = df.head(20)

    # =============================
    # DISPLAY RESULTS
    # =============================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    if results.empty:
        st.warning("No results found")
    else:
        st.dataframe(results, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
