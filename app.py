import streamlit as st

# 🔥 MUST BE FIRST
st.set_page_config(layout="wide")

from auth import login_flow
from admin import admin_dashboard
from customer import customer_dashboard
from security import auto_logout, update_activity

# =============================
# ROUTING
# =============================
query_params = st.query_params
is_admin = query_params.get("admin") == "1"

# =============================
# SESSION CONTROL
# =============================
auto_logout()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# =============================
# LOGIN
# =============================
if not st.session_state.authenticated:
    login_flow(is_admin)
else:
    update_activity()

    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        customer_dashboard()
