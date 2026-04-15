import streamlit as st
import pandas as pd

def customer_dashboard():
    st.title("Welcome to Dynatrade")

    search = st.text_input("Search Parts")

    # Dummy data (will connect search engine later)
    data = pd.DataFrame({
        "Brand": ["Sampa"],
        "Vehicle": ["Daimler"],
        "OE": ["000000005503"],
        "Description": ["Hex Bolt"],
        "Stock": [10],
        "Price": [13.72]
    })

    st.dataframe(data)

    if "cart" not in st.session_state:
        st.session_state.cart = []

    if st.button("Add to Cart"):
        st.session_state.cart.append(data.iloc[0].to_dict())

    st.write("Cart:", st.session_state.cart)
