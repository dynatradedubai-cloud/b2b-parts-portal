import streamlit as st
import os

from database import load_encrypted_file
from search_engine import prepare_search, search_parts
from security import log_event
from utils import get_country


# =============================
# GLOBAL STYLE
# =============================
def apply_ui():
    st.markdown("""
    <style>

    .block-container {
        padding-top: 1rem;
    }

    .stButton button {
        border-radius: 8px;
        height: 35px;
    }

    .table-header {
        font-weight: bold;
        border-bottom: 1px solid #333;
        padding-bottom: 5px;
    }

    </style>
    """, unsafe_allow_html=True)


# =============================
# HEADER
# =============================
def render_header():

    col1, col2, col3 = st.columns([1, 6, 1])

    with col1:
        if os.path.exists("dynatrade_logo.png"):
            st.image("dynatrade_logo.png", width=80)

    with col2:
        st.markdown("## Dynatrade Automotive LLC")

    with col3:
        with st.expander("🔔"):
            if os.path.exists("data"):
                for f in os.listdir("data"):
                    st.write(f"📢 {f}")


# =============================
# CART (ADVANCED)
# =============================
def render_cart():

    st.markdown("### 🛒 Cart")

    if "cart" not in st.session_state:
        st.session_state.cart = []

    total = 0

    for i, item in enumerate(st.session_state.cart):

        col1, col2, col3, col4 = st.columns([4,1,1,1])

        with col1:
            st.write(item["Description"])

        with col2:
            if st.button("-", key=f"dec_{i}"):
                item["Qty"] -= 1
                if item["Qty"] <= 0:
                    st.session_state.cart.pop(i)
                st.rerun()

        with col3:
            st.write(item["Qty"])

        with col4:
            if st.button("+", key=f"inc_{i}"):
                item["Qty"] += 1
                st.rerun()

        total += float(item["Price"]) * item["Qty"]

    st.markdown(f"### 💰 Total: {total}")


# =============================
# SALES CONTACT
# =============================
def render_sales():

    users = load_encrypted_file("users")
    user = st.session_state.get("temp_user")

    if users is None:
        return

    row = users[users["Username"] == user]

    if row.empty:
        return

    st.markdown("### 📞 Sales Contact")

    st.write(row.iloc[0]["Salesman Name"])
    st.write(row.iloc[0]["Salesman Email"])
    st.write(row.iloc[0]["Salesman Phone"])

    phone = str(row.iloc[0]["Salesman Phone"]).replace("+","")
    st.markdown(f"[💬 WhatsApp](https://wa.me/{phone})")


# =============================
# MAIN
# =============================
def customer_dashboard():

    apply_ui()
    render_header()

    col_main, col_side = st.columns([3,1])

    # =============================
    # SEARCH AREA
    # =============================
    with col_main:

        st.markdown("### 🔍 Search Parts")

        df = load_encrypted_file("price")

        if df is None:
            st.warning("Upload price list")
            return

        df = prepare_search(df)

        search = st.text_input("Search part / brand / vehicle")

        if not search:
            st.info("Start typing to search parts")
            return

        results = search_parts(df, search)

        user = st.session_state.get("temp_user","unknown")
        country = get_country()

        if results.empty:
            log_event(user, "SEARCH_FAIL", search)
            st.warning("No results found")
            return
        else:
            log_event(user, "SEARCH_SUCCESS", search)

        # =============================
        # TABLE HEADER
        # =============================
        h1, h2, h3, h4, h5, h6 = st.columns([2,2,2,3,1,1])

        h1.markdown("**Brand**")
        h2.markdown("**Vehicle**")
        h3.markdown("**OE**")
        h4.markdown("**Description**")
        h5.markdown("**Stock**")
        h6.markdown("")

        st.markdown("---")

        # =============================
        # TABLE ROWS
        # =============================
        for idx, row in results.iterrows():

            c1, c2, c3, c4, c5, c6 = st.columns([2,2,2,3,1,1])

            with c1:
                st.write(row["Brand"])

            with c2:
                st.write(row["Vehicle"])

            with c3:
                st.write(row["OE Part Number"])

            with c4:
                st.write(row["Description"])

            with c5:
                stock = int(row["Stock"])

                if stock > 0:
                    st.markdown("🟢")
                else:
                    st.markdown("🔴")

            with c6:
                if st.button("Add", key=f"add_{idx}"):

                    item = row.to_dict()
                    item["Qty"] = 1

                    if "cart" not in st.session_state:
                        st.session_state.cart = []

                    st.session_state.cart.append(item)

                    st.toast("Added to cart")

    # =============================
    # RIGHT PANEL
    # =============================
    with col_side:
        render_cart()
        st.markdown("---")
        render_sales()
