import streamlit as st
from database import save_encrypted_file

def admin_dashboard():
    st.title("Admin Panel")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Users Upload", "Price Upload", "Campaigns", "Audit Logs"]
    )

    with tab1:
        file = st.file_uploader("Upload Users CSV")
        if file:
            save_encrypted_file(file)
            st.success("Users uploaded & encrypted")

    with tab2:
        file = st.file_uploader("Upload Price List")
        if file:
            save_encrypted_file(file)
            st.success("Price uploaded")

    with tab3:
        file = st.file_uploader("Upload Campaign")
        if file:
            save_encrypted_file(file)
            st.success("Campaign uploaded")

    with tab4:
        st.write("Logs coming soon...")
