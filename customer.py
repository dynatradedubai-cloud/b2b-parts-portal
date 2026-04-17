import streamlit as st
import os
import pandas as pd

from database import load_encrypted_file
from search_engine import prepare_search, search_parts, get_suggestions


# =============================
# SESSION INIT
# =============================
def init_session():

    if "cart" not in st.session_state:
        st.session_state.cart = []

    if "notifications" not in st.session_state:
        st.session_state.notifications = ["Welcome to Dynatrade Portal"]


# =============================
# HEADER
# =============================
def render_header():

    init_session()

    col1, col2, col3 = st.columns([1, 5, 1])

    with col1:
        if os.path.exists("dynatrade_logo.png"):
            st.image("dynatrade_logo.png", width=90)

    with col2:
        st.markdown("### Dynatrade Automotive LLC")

    with col3:
        with st.expander("🔔 NEW"):
            for n in st.session_state.notifications:
                st.write(n)


# =============================
# ADD TO CART (WITH QTY)
# =============================
def add_to_cart(row):

    item = row.to_dict()

    # Check if already exists
    for cart_item in st.session_state.cart:
        if cart_item["OE Part Number"] == item["OE Part Number"]:
            cart_item["Qty"] += 1
            return

    item["Qty"] = 1
    st.session_state.cart.append(item)


# =============================
# CART UI
# =============================
def render_cart():

    st.markdown("## 🛒 Cart")

    if not st.session_state.cart:
        st.info("Cart is empty")
        return

    total = 0

    for i, item in enumerate(st.session_state.cart):

        col1, col2, col3, col4 = st.columns([4, 1, 1, 1])

        with col1:
            st.write(item["Description"])

        with col2:
            if st.button("➖", key=f"minus_{i}"):
                item["Qty"] -= 1
                if item["Qty"] <= 0:
                    st.session_state.cart.pop(i)
                st.rerun()

        with col3:
            st.write(f"{item['Qty']}")

        with col4:
            if st.button("➕", key=f"plus_{i}"):
                item["Qty"] += 1
                st.rerun()

        price = float(item.get("Price", 0))
        total += price * item["Qty"]

        st.markdown("---")

    st.markdown(f"### 💰 Total: {round(total,2)}")

    # =============================
    # EXPORT TO EXCEL
    # =============================
    if st.button("📥 Download Excel"):

        df = pd.DataFrame(st.session_state.cart)

        file_path = "cart.xlsx"
        df.to_excel(file_path, index=False)

        with open(file_path, "rb") as f:
            st.download_button(
                label="Download File",
                data=f,
                file_name="cart.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


# =============================
# MAIN DASHBOARD
# =============================
def customer_dashboard():

    init_session()

    render_header()

    col_main, col_cart = st.columns([3, 1])

    # =============================
    # SEARCH AREA
    # =============================
    with col_main:

        st.markdown("### 🔍 Search Parts")

        df = load_encrypted_file("price")

        if df is None:
            st.warning("Price list not uploaded yet")
            return

        df = prepare_search(df)

        search = st.text_input(
            "",
            placeholder="Search OE / MFG / Brand / Vehicle..."
        )

        # Suggestions
        suggestions = get_suggestions(df, search)
        for s in suggestions:
            st.caption(f"🔎 {s}")

        results = search_parts(df, search)

        if results.empty:
            st.warning("No results found")
            return

        for i, row in results.iterrows():

            col1, col2 = st.columns([5, 1])

            with col1:
                st.markdown(f"""
                **{row.get('Description', '')}**  
                {row.get('Brand', '')} | {row.get('Vehicle', '')}  
                OE: {row.get('OE Part Number', '')}  
                MFG: {row.get('Manufacturing Part Number', '')}  
                Price: {row.get('Price', '')}
                """)

            with col2:
                if st.button("Add", key=f"add_{i}"):
                    add_to_cart(row)
                    st.success("Added to cart")

            st.markdown("---")

    # =============================
    # CART AREA
    # =============================
    with col_cart:
        render_cart()
