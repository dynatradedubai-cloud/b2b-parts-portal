import streamlit as st
from auth import login_flow
from admin import admin_dashboard
from customer import customer_dashboard
from security import auto_logout

st.set_page_config(layout="wide", page_title="Dynatrade Portal")

# Hide Streamlit UI
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Session init
for key in ["authenticated","role","last_activity"]:
    if key not in st.session_state:
        st.session_state[key] = None

# Auto logout
auto_logout()

# Detect admin
is_admin = st.query_params.get("admin") == "1"

# Route
if not st.session_state.authenticated:
    login_flow(is_admin)
else:
    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        customer_dashboard()
