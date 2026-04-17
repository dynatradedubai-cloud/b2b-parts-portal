import streamlit as st
import os

from database import load_encrypted_file
from search_engine import prepare_search, search_parts

# =============================
# GLOBAL UI THEME
# =============================
def apply_theme():
    st.set_page_config(layout="wide")

    st.markdown("""
    <style>

    body {
        background-color: #0e1117;
    }

    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 1rem;
    }

    /* HEADER BAR */
    .header {
        background-color: #111827;
        padding: 12px 20px;
        border-radius: 10px;
        margin-bottom: 15px;
    }

    /* SEARCH BAR */
    input {
        border-radius: 8px !important;
    }

    /* TABLE HEADER */
    .table-head {
        font-weight: 600;
        color: #9ca3af;
        border-bottom: 1px solid #1f2937;
        padding-bottom: 5px;
    }

    /* CARD */
    .card {
        background-color: #161b22;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 8px;
    }

    </style>
    """, unsafe_allow_html=True)


# =============================
# HEADER (TOP NAV)
# =============================
def render_header():

    st.markdown('<div class="header">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2,5,2])

    with col1:
        if os.path.exists("dynatrade_logo.png"):
            st.image("dynatrade_logo.png", width=90)
        st.markdown("**Dynatrade Automotive LLC**")

    with col2:
        st.session_state.search = st.text_input(
            "Search parts...", label_visibility="collapsed"
        )

    with col3:
        with st.expander("🔔 Notifications"):
            if os.path.exists("data"):
                for f in os.listdir("data"):
                    st.write(f"📢 {f}")

        st.write("👤 User")

    st.markdown('</div>', unsafe_allow_html=True)


# =============================
# CART PANEL
# =============================
def render_cart():

    st.markdown("### 🛒 Cart")

    if "cart" not in st.session_state:
        st.session_state.cart = []

    total = 0

    for i, item in enumerate(st.session_state.cart):

        c1, c2, c3, c4 = st.columns([4,1,1,1])

        c1.write(item["Description"])

        if c2.button("-", key=f"dec_{i}"):
            item["Qty"] -= 1
            if item["Qty"] <= 0:
                st.session_state.cart.pop(i)
            st.rerun()

        c3.write(item["Qty"])

        if c4.button("+", key=f"inc_{i}"):
            item["Qty"] += 1
            st.rerun()

        total += float(item["Price"]) * item["Qty"]

    st.markdown(f"### 💰 Total: AED {total}")


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
# MAIN DASHBOARD
# =============================
def customer_dashboard():

    apply_theme()
    render_header()

    col_main, col_side = st.columns([3,1])

    # =============================
    # MAIN SEARCH RESULTS
    # =============================
    with col_main:

        df = load_encrypted_file("price")

        if df is None:
            st.warning("Upload price list")
            return

        df = prepare_search(df)

        search = st.session_state.get("search", "")

        if not search:
            st.info("Search parts using top bar")
            return

        results = search_parts(df, search)

        if results.empty:
            st.warning("No results found")
            return

        # HEADER ROW
        h1, h2, h3, h4, h5, h6 = st.columns([2,2,2,3,1,1])
        h1.markdown("**Brand**")
        h2.markdown("**Vehicle**")
        h3.markdown("**OE**")
        h4.markdown("**Description**")
        h5.markdown("**Stock**")
        h6.markdown("")

        st.markdown("---")

        # DATA ROWS
        for i, row in results.iterrows():

            c1, c2, c3, c4, c5, c6 = st.columns([2,2,2,3,1,1])

            c1.write(row["Brand"])
            c2.write(row["Vehicle"])
            c3.write(row["OE Part Number"])
            c4.write(row["Description"])

            if int(row["Stock"]) > 0:
                c5.markdown("🟢")
            else:
                c5.markdown("🔴")

            if c6.button("Add", key=f"add_{i}"):

                item = row.to_dict()
                item["Qty"] = 1

                if "cart" not in st.session_state:
                    st.session_state.cart = []

                st.session_state.cart.append(item)

                st.toast("Added to cart")

    # =============================
    # SIDE PANEL
    # =============================
    with col_side:
        render_cart()
        st.markdown("---")
        render_sales()
