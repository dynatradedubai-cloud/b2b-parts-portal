import streamlit as st
import os
from database import load_encrypted_file


# =============================
# SESSION INIT (CART + NOTIFY)
# =============================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "notifications" not in st.session_state:
    st.session_state.notifications = ["Welcome to Dynatrade Portal"]


# =============================
# HEADER WITH BELL
# =============================
def render_header():

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
# ADD TO CART
# =============================
def add_to_cart(row):
    st.session_state.cart.append(row.to_dict())


# =============================
# CART PANEL
# =============================
def render_cart():

    st.markdown("## 🛒 Cart")

    if not st.session_state.cart:
        st.info("Cart is empty")
        return

    for i, item in enumerate(st.session_state.cart):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(f"{item.get('Description', '')} | {item.get('Price', '')}")

        with col2:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()


# =============================
# MAIN DASHBOARD
# =============================
def customer_dashboard():

    render_header()

    col_main, col_cart = st.columns([3, 1])

    # =============================
    # LEFT SIDE (SEARCH)
    # =============================
    with col_main:

        st.markdown("### 🔍 Search Parts")

        search = st.text_input(
            "",
            placeholder="Search OE / MFG / Brand / Vehicle..."
        )

        df = load_encrypted_file("price")

        if df is None:
            st.warning("Price list not uploaded yet")
            return

        if search:
            search = search.lower()

            results = df[
                df.astype(str)
                .apply(lambda row: row.str.lower().str.contains(search).any(), axis=1)
            ].head(20)
        else:
            results = df.head(20)

        if results.empty:
            st.warning("No results found")
            return

        # =============================
        # SHOW RESULTS
        # =============================
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
    # RIGHT SIDE (CART)
    # =============================
    with col_cart:
        render_cart()
