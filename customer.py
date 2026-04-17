import streamlit as st
import os
import pandas as pd

from database import load_encrypted_file
from search_engine import prepare_search, search_parts
from security import log_event
from utils import send_alert_email, get_country


# =============================
# LANGUAGE
# =============================
def t(key):
    lang = st.session_state.get("lang", "EN")

    data = {
        "EN": {
            "search": "Search Parts",
            "cart": "Cart",
            "contact": "Sales Contact"
        },
        "AR": {
            "search": "بحث",
            "cart": "السلة",
            "contact": "التواصل"
        }
    }

    return data[lang][key]


# =============================
# HEADER
# =============================
def render_header():

    col1, col2, col3, col4 = st.columns([1, 5, 1, 1])

    with col1:
        if os.path.exists("dynatrade_logo.png"):
            st.image("dynatrade_logo.png", width=90)

    with col2:
        st.markdown("## Dynatrade Automotive LLC")

    with col3:
        if st.button("EN/AR"):
            st.session_state.lang = "AR" if st.session_state.get("lang","EN")=="EN" else "EN"

    with col4:
        with st.expander("🔔"):
            if os.path.exists("data"):
                for f in os.listdir("data"):
                    st.write(f)


# =============================
# SALES CONTACT
# =============================
def render_sales():

    users = load_encrypted_file("users")
    user = st.session_state.get("temp_user")

    row = users[users["Username"] == user]

    st.markdown(f"### 📞 {t('contact')}")

    st.write(row.iloc[0]["Salesman Name"])
    st.write(row.iloc[0]["Salesman Email"])
    st.write(row.iloc[0]["Salesman Phone"])

    phone = str(row.iloc[0]["Salesman Phone"]).replace("+","")
    st.markdown(f"https://wa.me/{phone}")


# =============================
# CART
# =============================
def render_cart():

    st.markdown(f"### 🛒 {t('cart')}")

    if "cart" not in st.session_state:
        st.session_state.cart = []

    total = 0

    for item in st.session_state.cart:
        st.write(item["Description"])
        total += float(item["Price"]) * item["Qty"]

    st.write("Total:", total)


# =============================
# MAIN
# =============================
def customer_dashboard():

    render_header()

    col1, col2 = st.columns([3, 1])

    with col1:

        st.markdown(f"### 🔍 {t('search')}")

        df = load_encrypted_file("price")

        if df is None:
            return

        df = prepare_search(df)

        search = st.text_input("")

        if not search:
            return

        results = search_parts(df, search)

        user = st.session_state.get("temp_user")

        country = get_country()

        if results.empty:
            log_event(user, "SEARCH_FAIL", search + f" ({country})")

            # EMAIL ALERT
            users = load_encrypted_file("users")
            row = users[users["Username"] == user]

            send_alert_email(
                row.iloc[0]["Salesman Email"],
                f"{user} searched: {search}"
            )

            st.warning("Not found")
            return

        else:
            log_event(user, "SEARCH_SUCCESS", search + f" ({country})")

        for _, row in results.iterrows():

            st.write(row["Description"])

            if st.button("Add"):
                item = row.to_dict()
                item["Qty"] = 1
                st.session_state.cart.append(item)

    with col2:
        render_cart()
        render_sales()
