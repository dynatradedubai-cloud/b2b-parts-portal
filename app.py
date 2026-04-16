import streamlit as st
from auth import login_flow
from admin import admin_dashboard
from customer import customer_dashboard
from security import auto_logout, update_activity
from ui import apply_ui

st.set_page_config(page_title="Dynatrade Portal", layout="wide")

# ✅ APPLY UI
apply_ui()

# Session init
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "role" not in st.session_state:
    st.session_state.role = None

if "last_activity" not in st.session_state:
    st.session_state.last_activity = None

# Auto logout
auto_logout()

# Detect admin mode
is_admin = st.query_params.get("admin") == "1"

# Routing
if not st.session_state.authenticated:
    login_flow(is_admin)
else:
    update_activity()

    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        customer_dashboard()
