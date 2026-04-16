import streamlit as st
import bcrypt
import time

from security import log_event

def login_flow(is_admin):

    st.title("Dynatrade Automotive LLC")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):

        if is_admin:

            try:
                stored_user = st.secrets["ADMIN_EMAIL"]
                stored_hash = st.secrets["ADMIN_PASSWORD"]
            except Exception:
                st.error("❌ Admin credentials not configured in secrets")
                return

            # SAFE CHECK
            if user != stored_user:
                log_event(user, "Admin wrong username")
                st.error("Invalid credentials")
                return

            try:
                valid = bcrypt.checkpw(pwd.encode(), stored_hash.encode())
            except Exception:
                st.error("❌ Invalid bcrypt hash in secrets")
                return

            if not valid:
                log_event(user, "Admin wrong password")
                st.error("Invalid credentials")
                return

            # SUCCESS
            st.session_state.authenticated = True
            st.session_state.role = "admin"
            st.session_state.last_activity = time.time()

            log_event(user, "Admin login success")

            st.success("Login successful")
            st.rerun()

        else:
            st.info("Customer login handled separately")
