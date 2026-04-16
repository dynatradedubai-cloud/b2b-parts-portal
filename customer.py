import streamlit as st
import pandas as pd
from database import load_encrypted_file
from search_engine import prepare_search, search_parts, get_suggestions

# =============================
# HEADER UI
# =============================

def render_header():
    col1, col2, col3 = st.columns([1, 6, 1])

    with col1:
        st.image("dynatrade_logo.png", width=120)

    with col2:
        st.markdown(
            "<h2 style='margin-top:10px;'>Dynatrade Automotive LLC</h2>",
            unsafe_allow_html=True
        )

    with col3:
        st.markdown("🔔 <span style='color:red;'>NEW</span>", unsafe_allow_html=True)

# =============================
# MAIN DASHBOARD
# =============================

def customer_dashboard():
    render_header()

    st.markdown("---")

    df = load_encrypted_file("price")

    if df is None:
        st.warning("No price data uploaded yet.")
        return

    df = prepare_search(df)

    # =============================
    # SEARCH BAR
    # =============================

    st.markdown("### 🔍 Search Parts")

    query = st.text_input(
        "Search by OE / MFG / Brand / Vehicle / Description",
        placeholder="Type part number, brand, or description..."
    )

    # =============================
    # AUTO SUGGESTIONS
    # =============================

    if query:
        suggestions = get_suggestions(df, query)

        for s in suggestions:
            st.caption(f"🔹 {s}")

    # =============================
    # SEARCH RESULTS
    # =============================

    if query:
        results = search_parts(df, query)

        if results.empty:
            st.error("No results found")
            return

        st.markdown("### 📊 Results")

        display_cols = [
            "Brand", "Vehicle", "OE Part Number",
            "Manufacturing Part Number",
            "Description", "Stock", "Price"
        ]

        results = results[display_cols]

        # Add quantity column
        results["Qty"] = 1

        for i, row in results.iterrows():
            cols = st.columns([1,1,1,1,2,1,1,1,1])

            cols[0].write(row["Brand"])
            cols[1].write(row["Vehicle"])
            cols[2].write(row["OE Part Number"])
            cols[3].write(row["Manufacturing Part Number"])
            cols[4].write(row["Description"])

            # Stock color
            if row["Stock"] > 0:
                cols[5].markdown(f"<span style='color:green'>{row['Stock']}</span>", unsafe_allow_html=True)
            else:
                cols[5].markdown(f"<span style='color:red'>Out</span>", unsafe_allow_html=True)

            cols[6].write(row["Price"])

            qty = cols[7].number_input(
                "Qty",
                min_value=1,
                value=1,
                key=f"qty_{i}"
            )

            if cols[8].button("Add", key=f"add_{i}"):
                add_to_cart(row, qty)

    # =============================
    # CART
    # =============================

    render_cart()

# =============================
# CART SYSTEM
# =============================

def add_to_cart(row, qty):
    if "cart" not in st.session_state:
        st.session_state.cart = []

    item = row.to_dict()
    item["Qty"] = qty
    item["Total"] = qty * row["Price"]

    st.session_state.cart.append(item)

def render_cart():
    st.markdown("---")
    st.markdown("## 🛒 Cart")

    if "cart" not in st.session_state or not st.session_state.cart:
        st.info("Cart is empty")
        return

    cart_df = pd.DataFrame(st.session_state.cart)

    total = 0

    for i, row in cart_df.iterrows():
        cols = st.columns([1,1,2,1,1,1,1])

        cols[0].write(row["Brand"])
        cols[1].write(row["OE Part Number"])
        cols[2].write(row["Description"])
        cols[3].write(row["Price"])

        qty = cols[4].number_input(
            "Qty",
            min_value=1,
            value=int(row["Qty"]),
            key=f"cart_qty_{i}"
        )

        total_price = qty * row["Price"]
        total += total_price

        cols[5].write(round(total_price, 2))

        if cols[6].button("❌", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    st.markdown(f"### 💰 Total: {round(total,2)} AED")

    # =============================
    # EXPORT
    # =============================

    if st.button("⬇ Download Excel"):
        export_cart(cart_df)

def export_cart(df):
    file = "cart.xlsx"
    df.to_excel(file, index=False)

    with open(file, "rb") as f:
        st.download_button("Download File", f, file_name="cart.xlsx")
