import streamlit as st

def apply_ui():

    st.markdown("""
    <style>

    /* Remove default */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Page background */
    .stApp {
        background-color: #f5f7fb;
    }

    /* Header */
    .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: white;
        padding: 10px 20px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }

    /* Cards */
    .card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }

    /* Buttons */
    .stButton button {
        background-color: #1f4e79;
        color: white;
        border-radius: 8px;
        height: 40px;
    }

    </style>
    """, unsafe_allow_html=True)
