import streamlit as st
import pandas as pd
import os
from database import save_encrypted_file, load_encrypted_file

def admin_dashboard():
    st.title("Admin Panel")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Users", "Price", "Campaign", "Logs"
    ])

    with tab1:
        file = st.file_uploader("Upload Users", type=["xlsx"])
        if file:
            ok, msg = save_encrypted_file(file, "users")
            st.success(msg if ok else msg)

        df = load_encrypted_file("users")
        if df is not None:
            st.dataframe(df)

    with tab2:
        file = st.file_uploader("Upload Price", type=["xlsx"])
        if file:
            ok, msg = save_encrypted_file(file, "price")
            st.success(msg if ok else msg)

        df = load_encrypted_file("price")
        if df is not None:
            st.dataframe(df.head(20))

    with tab3:
        file = st.file_uploader("Upload Campaign")
        if file:
            os.makedirs("data", exist_ok=True)
            with open(f"data/{file.name}", "wb") as f:
                f.write(file.read())
            st.success("Uploaded")

    with tab4:
        st.write("Logs will appear here")
