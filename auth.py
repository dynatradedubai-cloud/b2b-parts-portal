import streamlit as st
import bcrypt
import time

def login_flow(is_admin):

    st.title("Admin Login Debug")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):

        st.write("DEBUG → Entered Username:", user)
        st.write("DEBUG → Entered Password:", pwd)

        try:
            admin_user = st.secrets["ADMIN_EMAIL"]
            admin_hash = st.secrets["ADMIN_PASSWORD"]

            st.write("DEBUG → Secret Username:", admin_user)
            st.write("DEBUG → Secret Hash Exists:", bool(admin_hash))

        except Exception as e:
            st.error(f"Secrets error: {e}")
            return

        if user != admin_user:
            st.error("Username mismatch")
            return

        try:
            result = bcrypt.checkpw(pwd.encode(), admin_hash.encode())
            st.write("DEBUG → bcrypt result:", result)
        except Exception as e:
            st.error(f"bcrypt error: {e}")
            return

        if result:
            st.success("LOGIN SUCCESS")
        else:
            st.error("Password mismatch")
