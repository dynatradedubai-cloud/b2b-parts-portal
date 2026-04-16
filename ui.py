import streamlit as st

def apply_ui():

    st.markdown("""
    <style>

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background-color: #f5f7fb;
    }

    .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: white;
        padding: 12px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }

    .card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }

    .stButton button {
        background-color: #1f4e79;
        color: white;
        border-radius: 8px;
        height: 40px;
        border: none;
    }

    .stTextInput input {
        border-radius: 8px;
        height: 38px;
    }

    </style>
    """, unsafe_allow_html=True)
