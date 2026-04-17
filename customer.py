import streamlit as st
import os
import pandas as pd
import urllib.parse

from database import load_encrypted_file
from search_engine import prepare_search, search_parts

# =============================
# CONFIG + THEME
# =============================
st.set_page_config(layout="wide")

def apply_theme():
    st.markdown("""
    <style>
    body { background-color:#0e1117; }

    .header {
        background:#111827;
        padding:12px 20px;
        border-radius:10px;
        margin-bottom:10px;
    }

    .section {
        margin-top:15px;
    }

    .table-head {
        font-weight:600;
        color:#9ca3af;
    }

    </style>
    """, unsafe_allow_html=True)

# =============================
# HEADER
# =============================
def render_header():

    st.markdown('<div class="header">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2,5,2])

    with c1:
        if os.path.exists("dynatrade_logo.png"):
            st.image("dynatrade_logo.png", width=90)
        st.markdown("**Dynatrade Automotive LLC**")

    with c2:
        st.session_state.search = st.text_input(
            "Search parts...",
            value=st.session_state.get("search",""),
            label_visibility="collapsed"
        )

    with c3:
        with st.expander("🔔 Notifications"):
            if os.path.exists("data"):
                for f in os.listdir("data"):
                    st.write(f"🆕 {f}")

        st.write("👤 Customer")

    st.markdown('</div>', unsafe_allow_html=True)

# =============================
# CART LOGIC
# =============================
def get_cart_total():
    total = 0
    for item in st.session_state.cart:
        total += float(item["Price"]) * item["Qty"]
    return total

# =============================
# CART UI
# =============================
def render_cart():

    st.markdown("### 🛒 Cart")

    if "cart" not in st.session_state:
        st.session_state.cart = []

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

    total = get_cart_total()

    st.markdown(f"### 💰 Total: AED {total:,.2f}")

    # =============================
    # DOWNLOAD CART
    # =============================
    if st.session_state.cart:
        df = pd.DataFrame(st.session_state.cart)

        st.download_button(
            "📥 Download Cart",
            df.to_csv(index=False),
            "cart.csv",
            key="download_cart"
        )

        # =============================
        # WHATSAPP
        # =============================
        msg = "Inquiry:\n\n"
        for item in st.session_state.cart:
            msg += f"{item['Description']} x {item['Qty']}\n"

        encoded = urllib.parse.quote(msg)

        st.markdown(
            f"[💬 Send via WhatsApp](https://wa.me/?text={encoded})"
        )

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

    st.write(f"👤 {row.iloc[0]['Salesman Name']}")
    st.write(f"📧 {row.iloc[0]['Salesman Email']}")
    st.write(f"📱 {row.iloc[0]['Salesman Phone']}")

# =============================
# MAIN
# =============================
def customer_dashboard():

    apply_theme()
    render_header()

    col_main, col_side = st.columns([3,1])

    # =============================
    # MAIN AREA
    # =============================
    with col_main:

        df = load_encrypted_file("price")

        if df is None:
            st.warning("Upload price list")
            return

        df = prepare_search(df)

        search = st.session_state.get("search","")

        if not search:
            st.info("Search parts using the top bar")
            return

        results = search_parts(df, search)

        if results.empty:
            st.warning("No results found")
            return

        # TABLE HEADER
        h1,h2,h3,h4,h5,h6 = st.columns([2,2,2,3,1,1])
        h1.markdown("**Brand**")
        h2.markdown("**Vehicle**")
        h3.markdown("**OE**")
        h4.markdown("**Description**")
        h5.markdown("**Stock**")
        h6.markdown("")

        st.markdown("---")

        # TABLE ROWS
        for i, row in results.iterrows():

            c1,c2,c3,c4,c5,c6 = st.columns([2,2,2,3,1,1])

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
                st.session_state.cart.append(item)
                st.toast("Added to cart")

    # =============================
    # SIDE PANEL
    # =============================
    with col_side:
        render_cart()
        st.markdown("---")
        render_sales()
