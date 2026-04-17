import streamlit as st
import os
import pandas as pd

from database import load_encrypted_file
from search_engine import prepare_search, search_parts, get_suggestions
from security import log_event


# =============================
# HEADER
# =============================
def render_header():

    st.markdown("""
    <style>
    .header {
        position: sticky;
        top: 0;
        background: #0E1117;
        padding: 10px;
        z-index: 999;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 6, 1])

    with col1:
        if os.path.exists("dynatrade_logo.png"):
            st.image("dynatrade_logo.png", width=100)

    with col2:
        st.markdown("## Dynatrade Automotive LLC")

    with col3:
        with st.expander("🔔 Notifications"):

            if os.path.exists("data"):
                files = os.listdir("data")
                if files:
                    for f in files:
                        st.write(f"📢 {f}")
                else:
                    st.write("No updates")


# =============================
# SALES CONTACT
# =============================
def render_sales_contact():

    users = load_encrypted_file("users")

    username = st.session_state.get("temp_user")

    row = users[users["Username"] == username]

    if row.empty:
        return

    st.markdown("### 📞 Sales Contact")

    st.write(f"👤 {row.iloc[0]['Salesman Name']}")
    st.write(f"📧 {row.iloc[0]['Salesman Email']}")
    st.write(f"📱 {row.iloc[0]['Salesman Phone']}")

    phone = str(row.iloc[0]['Salesman Phone']).replace("+", "")
    st.markdown(f"[💬 WhatsApp](https://wa.me/{phone})")


# =============================
# CART
# =============================
def render_cart():

    st.markdown("### 🛒 Cart")

    if "cart" not in st.session_state:
        st.session_state.cart = []

    total = 0

    for i, item in enumerate(st.session_state.cart):

        st.write(item["Description"])

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("-", key=f"m{i}"):
                item["Qty"] -= 1
                if item["Qty"] <= 0:
                    st.session_state.cart.pop(i)
                st.rerun()

        with col2:
            st.write(item["Qty"])

        with col3:
            if st.button("+", key=f"p{i}"):
                item["Qty"] += 1
                st.rerun()

        total += float(item["Price"]) * item["Qty"]

    st.markdown(f"### 💰 Total: {total}")


# =============================
# MAIN
# =============================
def customer_dashboard():

    render_header()

    col1, col2 = st.columns([3, 1])

    with col1:

        st.markdown("### 🔍 Search Parts")

        df = load_encrypted_file("price")

        if df is None:
            st.warning("Upload price list")
            return

        df = prepare_search(df)

        search = st.text_input("Search")

        if not search:
            st.info("Start typing to search parts")
            return

        suggestions = get_suggestions(df, search)
        for s in suggestions:
            st.caption(s)

        results = search_parts(df, search)

        user = st.session_state.get("temp_user", "unknown")

        if results.empty:
            log_event(user, "SEARCH_FAIL", search)
            st.warning("No results")
            return
        else:
            log_event(user, "SEARCH_SUCCESS", search)

        for i, row in results.iterrows():

            st.markdown(f"""
            **{row['Description']}**  
            {row['Brand']} | {row['Vehicle']}  
            Price: {row['Price']}
            """)

            if st.button("Add", key=i):

                item = row.to_dict()
                item["Qty"] = 1

                st.session_state.cart.append(item)

    with col2:
        render_cart()
        render_sales_contact()
