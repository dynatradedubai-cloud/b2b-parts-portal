import streamlit as st
import os

from database import load_encrypted_file
from search_engine import prepare_search, search_parts
from security import log_event
from utils import send_alert_email, get_country


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

    phone = str(row.iloc[0]["Salesman Phone"]).replace("+", "")
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

        col1, col2, col3 = st.columns([5, 1, 1])

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

        search = st.text_input("Enter part / brand / vehicle")

        if not search:
            st.info("Start typing to search parts")
            return

        results = search_parts(df, search)

        user = st.session_state.get("temp_user", "unknown")
        country = get_country()

        # =============================
        # NO RESULT
        # =============================
        if results.empty:

            log_event(user, "SEARCH_FAIL", f"{search} ({country})")

            users = load_encrypted_file("users")

            if users is not None:
                row = users[users["Username"] == user]
                if not row.empty:
                    send_alert_email(
                        row.iloc[0]["Salesman Email"],
                        f"{user} searched: {search}"
                    )

            st.warning("No results found")
            return

        else:
            log_event(user, "SEARCH_SUCCESS", f"{search} ({country})")

        # =============================
        # RESULTS
        # =============================
        for idx, row in results.iterrows():

            st.markdown(f"""
            **{row['Description']}**  
            {row['Brand']} | {row['Vehicle']}  
            💰 {row['Price']}
            """)

            # 🔥 UNIQUE BUTTON KEY FIX
            if st.button("Add to Cart", key=f"add_{idx}"):

                item = row.to_dict()
                item["Qty"] = 1

                if "cart" not in st.session_state:
                    st.session_state.cart = []

                st.session_state.cart.append(item)

    # RIGHT SIDE
    with col2:
        render_cart()
        render_sales()
