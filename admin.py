if is_admin:
    admin_user = st.secrets["ADMIN_EMAIL"]
    admin_pass = st.secrets["ADMIN_PASSWORD"]

    if user != admin_user or pwd != admin_pass:
        st.error("Invalid credentials")
        return

    st.session_state.authenticated = True
    st.session_state.role = "admin"
    st.session_state.last_activity = time.time()

    st.success("Admin login successful")
    st.rerun()
