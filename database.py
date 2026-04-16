import pandas as pd
import streamlit as st
from cryptography.fernet import Fernet
import os
from io import BytesIO

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# =============================
# SAFE FERNET HANDLER
# =============================

def get_fernet():
    try:
        key = st.secrets["ENCRYPTION_KEY"]
    except Exception:
        st.error("❌ ENCRYPTION_KEY missing in Streamlit Secrets")
        st.stop()

    return Fernet(key.encode())


# =============================
# REQUIRED COLUMNS
# =============================

USER_COLUMNS = [
    "Username", "Password", "Customer Name", "Customer Code",
    "Max search per day", "Customer email ID",
    "Salesman Name", "Salesman Phone", "Salesman Email"
]

PRICE_COLUMNS = [
    "Brand", "Vehicle", "OE Part Number",
    "Manufacturing Part Number", "Description",
    "Stock", "Price"
]

# =============================
# VALIDATE FILE
# =============================

def validate_columns(df, required_cols):
    df.columns = [c.strip() for c in df.columns]
    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        return False, f"Missing columns: {missing}"

    return True, "OK"


# =============================
# SAVE ENCRYPTED FILE
# =============================

def save_encrypted_file(uploaded_file, file_type):
    try:
        df = pd.read_excel(uploaded_file)
    except Exception:
        return False, "Invalid Excel file"

    # Validate
    if file_type == "users":
        valid, msg = validate_columns(df, USER_COLUMNS)
    elif file_type == "price":
        valid, msg = validate_columns(df, PRICE_COLUMNS)
    else:
        valid, msg = True, "OK"

    if not valid:
        return False, msg

    # Encrypt
    fernet = get_fernet()

    buffer = BytesIO()
    df.to_excel(buffer, index=False)

    encrypted = fernet.encrypt(buffer.getvalue())

    path = os.path.join(DATA_DIR, f"{file_type}.enc")

    with open(path, "wb") as f:
        f.write(encrypted)

    return True, "✅ File uploaded & encrypted"


# =============================
# LOAD ENCRYPTED FILE
# =============================

@st.cache_data
def load_encrypted_file(file_type):
    path = os.path.join(DATA_DIR, f"{file_type}.enc")

    if not os.path.exists(path):
        return None

    try:
        fernet = get_fernet()

        with open(path, "rb") as f:
            encrypted = f.read()

        decrypted = fernet.decrypt(encrypted)

        df = pd.read_excel(BytesIO(decrypted))
        df.columns = [c.strip() for c in df.columns]

        return df

    except Exception as e:
        st.error(f"❌ Failed to load {file_type}: {str(e)}")
        return None
