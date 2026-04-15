import streamlit as st
from auth import login_flow
from admin import admin_dashboard
from customer import customer_dashboard

st.set_page_config(page_title="Dynatrade Portal", layout="wide")

# Hide Streamlit UI
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Detect admin mode
query_params = st.query_params
is_admin = query_params.get("admin") == "1"

# Session state init
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "role" not in st.session_state:
    st.session_state.role = None

# Login flow
if not st.session_state.authenticated:
    login_flow(is_admin)
else:
    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        customer_dashboard()
