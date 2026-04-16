import pandas as pd
import streamlit as st
from cryptography.fernet import Fernet
import os
from io import BytesIO

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


# =============================
# FERNET KEY
# =============================

def get_fernet():
    key = st.secrets["ENCRYPTION_KEY"]
    return Fernet(key.encode())


# =============================
# FILE PATH (FIXED)
# =============================

def get_path(file_type):
    return os.path.join(DATA_DIR, f"{file_type}.enc")


# =============================
# SAVE ENCRYPTED FILE
# =============================

def save_encrypted_file(uploaded_file, file_type):
    try:
        df = pd.read_excel(uploaded_file)
    except Exception:
        return False, "Invalid Excel file"

    buffer = BytesIO()
    df.to_excel(buffer, index=False)

    encrypted = get_fernet().encrypt(buffer.getvalue())

    path = get_path(file_type)

    with open(path, "wb") as f:
        f.write(encrypted)

    return True, f"{file_type} file uploaded & encrypted"


# =============================
# LOAD FILE (FIXED DEBUG)
# =============================

@st.cache_data
def load_encrypted_file(file_type):

    path = get_path(file_type)

    # 🔴 DEBUG IMPORTANT
    if not os.path.exists(path):
        st.error(f"Missing file: {path}")
        return None

    try:
        with open(path, "rb") as f:
            encrypted = f.read()

        decrypted = get_fernet().decrypt(encrypted)

        df = pd.read_excel(BytesIO(decrypted))

        return df

    except Exception as e:
        st.error(f"Decrypt failed: {str(e)}")
        return None
