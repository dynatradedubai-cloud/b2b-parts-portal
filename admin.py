import streamlit as st
import os
import pandas as pd

from database import save_encrypted_file

def admin_dashboard():

    st.markdown("## ⚙️ Admin Panel")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Users", "Price", "Campaigns", "Logs"]
    )

    with tab1:
        file = st.file_uploader("Upload Users")
        if file:
            save_encrypted_file(file, "users")
            st.success("Uploaded")

    with tab2:
        file = st.file_uploader("Upload Price")
        if file:
            save_encrypted_file(file, "price")
            st.success("Uploaded")

    with tab3:
        file = st.file_uploader("Upload Campaign")
        if file:
            os.makedirs("data", exist_ok=True)
            with open(f"data/{file.name}", "wb") as f:
                f.write(file.read())
            st.success("Uploaded")

    with tab4:
        if os.path.exists("logs/audit_log.csv"):
            df = pd.read_csv("logs/audit_log.csv")
            st.dataframe(df.tail(20))
