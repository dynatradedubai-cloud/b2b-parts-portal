# =============================
# ADMIN LOGIN (NO OTP)
# =============================

if is_admin:
    valid = (
        user == st.secrets["ADMIN_EMAIL"] and
        bcrypt.checkpw(pwd.encode(), st.secrets["ADMIN_PASSWORD"].encode())
    )

    if not valid:
        log_event(user, "Admin Wrong Password")
        st.error("Invalid admin credentials")
        return

    # DIRECT LOGIN (NO OTP)
    st.session_state.authenticated = True
    st.session_state.role = "admin"
    st.session_state.last_activity = time.time()

    log_event(user, "Admin Login Success")
    st.success("Admin login successful")
    st.rerun()
