import streamlit as st
import pandas as pd
from database import load_encrypted
from search_engine import load_data, search

def customer_dashboard():
    st.markdown("## 🔍 Parts Search")

    df = load_encrypted("price")
    if df is None:
        st.warning("No data uploaded")
        return

    df = load_data(df)

    query = st.text_input("Search")

    if query:
        results = search(df, query)
        st.dataframe(results)

        if "cart" not in st.session_state:
            st.session_state.cart = []

        for i,row in results.iterrows():
            if st.button(f"Add {i}"):
                st.session_state.cart.append(row.to_dict())

    st.markdown("## 🛒 Cart")
    if "cart" in st.session_state:
        cart_df = pd.DataFrame(st.session_state.cart)
        st.dataframe(cart_df)

        if st.button("Download Excel"):
            cart_df.to_excel("cart.xlsx", index=False)
            with open("cart.xlsx","rb") as f:
                st.download_button("Download", f)
