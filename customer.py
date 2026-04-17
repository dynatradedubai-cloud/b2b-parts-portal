import streamlit as st
import os

from database import load_encrypted_file
from search_engine import prepare_search, search_parts
from security import log_event
from utils import send_alert_email, get_country


# =============================
# GLOBAL STYLE (VERY IMPORTANT)
# =============================
def apply_ui():

    st.markdown("""
    <style>

    .main {
        padding-top: 10px;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    .card {
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #2c2c2c;
        margin-bottom: 10px;
        background-color: #161a1d;
    }

    .price {
        font-size: 18px;
        font-weight: bold;
        color: #00d084;
    }

    .title {
        font-size: 16px;
        font-weight: 600;
    }

    .sub {
        font-size: 13px;
        color: #aaa;
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
            st.image("dynatrade_logo.png", width=90)

    with col2:
        st.markdown("## Dynatrade Automotive LLC")

    with col3:
        with st.expander("🔔"):
            if os.path.exists("data"):
                for f in os.listdir("data"):
                    st.write(f"📢 {f}")


# =============================
# CART PANEL
# =============================
def render_cart():

    st.markdown("### 🛒 Cart")

    if "cart" not in st.session_state:
        st.session_state.cart = []

    total = 0

    for i, item in enumerate(st.session_state.cart):

        with st.container():
            col1, col2, col3 = st.columns([5, 2, 1])

            with col1:
                st.write(item["Description"])

            with col2:
                st.write(f"Qty: {item['Qty']}")

            with col3:
                if st.button("❌", key=f"remove_{i}"):
                    st.session_state.cart.pop(i)
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

    phone = str(row.iloc[0]["Salesman Phone"]).replace("+", "")
    st.markdown(f"[💬 WhatsApp](https://wa.me/{phone})")


# =============================
# MAIN DASHBOARD
# =============================
def customer_dashboard():

    apply_ui()
    render_header()

    col_main, col_side = st.columns([3, 1])

    # =============================
    # LEFT SIDE (SEARCH)
    # =============================
    with col_main:

        st.markdown("### 🔍 Search Parts")

        df = load_encrypted_file("price")

        if df is None:
            st.warning("Upload price list")
            return

        df = prepare_search(df)

        search = st.text_input("Search by part / brand / vehicle")

        if not search:
            st.info("Start typing to search parts")
            return

        results = search_parts(df, search)

        user = st.session_state.get("temp_user", "unknown")
        country = get_country()

        if results.empty:

            log_event(user, "SEARCH_FAIL", search)

            st.warning("No results found")
            return

        else:
            log_event(user, "SEARCH_SUCCESS", search)

        # =============================
        # RESULTS CARDS
        # =============================
        for idx, row in results.iterrows():

            st.markdown(f"""
            <div class="card">
                <div class="title">{row['Description']}</div>
                <div class="sub">{row['Brand']} | {row['Vehicle']}</div>
                <div class="price">AED {row['Price']}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("➕ Add to Cart", key=f"add_{idx}"):

                item = row.to_dict()
                item["Qty"] = 1

                if "cart" not in st.session_state:
                    st.session_state.cart = []

                st.session_state.cart.append(item)

                st.success("Added to cart")

    # =============================
    # RIGHT SIDE
    # =============================
    with col_side:

        render_cart()
        st.markdown("---")
        render_sales()
