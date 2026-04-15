from cryptography.fernet import Fernet
import streamlit as st

def save_encrypted_file(uploaded_file):
    key = st.secrets["ENCRYPTION_KEY"].encode()
    fernet = Fernet(key)

    data = uploaded_file.read()
    encrypted = fernet.encrypt(data)

    with open(f"{uploaded_file.name}.enc", "wb") as f:
        f.write(encrypted)
