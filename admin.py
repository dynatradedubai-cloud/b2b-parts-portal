import streamlit as st
from database import save_encrypted
import pandas as pd
import os

def admin_dashboard():
    st.title("Admin Panel")

    tabs = st.tabs(["Users","Price","Campaigns","Logs"])

    with tabs[0]:
        file = st.file_uploader("Upload Users")
        if file:
            save_encrypted(file,"users")
            st.success("Users uploaded")

    with tabs[1]:
        file = st.file_uploader("Upload Price")
        if file:
            save_encrypted(file,"price")
            st.success("Price uploaded")

    with tabs[2]:
        file = st.file_uploader("Upload Campaign")
        if file:
            save_encrypted(file,"campaign")
            st.success("Campaign uploaded")

    with tabs[3]:
        if os.path.exists("logs/audit_log.csv"):
            df = pd.read_csv("logs/audit_log.csv")
            st.dataframe(df.tail(10))
            st.download_button("Download Logs", df.to_csv(index=False))
