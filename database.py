import pandas as pd
import streamlit as st
from cryptography.fernet import Fernet
import os
from io import BytesIO

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# =============================
# REQUIRED COLUMN DEFINITIONS
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
# ENCRYPTION HANDLER
# =============================

def get_fernet():
    return Fernet(st.secrets["ENCRYPTION_KEY"].encode())

# =============================
# FILE VALIDATION
# =============================

def validate_columns(df, required_cols):
    df_cols = [c.strip() for c in df.columns]
    missing = [col for col in required_cols if col not in df_cols]

    if missing:
        return False, f"Missing columns: {missing}"
    return True, "Valid file"

# =============================
# SAVE ENCRYPTED FILE
# =============================

def save_encrypted_file(uploaded_file, file_type):
    fernet = get_fernet()

    # Read file into dataframe
    try:
        df = pd.read_excel(uploaded_file)
    except:
        return False, "Invalid file format"

    # Validate
    if file_type == "users":
        valid, msg = validate_columns(df, USER_COLUMNS)
    elif file_type == "price":
        valid, msg = validate_columns(df, PRICE_COLUMNS)
    else:
        valid, msg = True, "OK"

    if not valid:
        return False, msg

    # Convert back to bytes (Excel → memory)
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    encrypted = fernet.encrypt(buffer.getvalue())

    # Save encrypted
    path = os.path.join(DATA_DIR, f"{file_type}.enc")
    with open(path, "wb") as f:
        f.write(encrypted)

    return True, "File uploaded & encrypted successfully"

# =============================
# LOAD (DECRYPT IN MEMORY ONLY)
# =============================

@st.cache_data
def load_encrypted_file(file_type):
    path = os.path.join(DATA_DIR, f"{file_type}.enc")

    if not os.path.exists(path):
        return None

    fernet = get_fernet()

    with open(path, "rb") as f:
        encrypted = f.read()

    decrypted = fernet.decrypt(encrypted)

    df = pd.read_excel(BytesIO(decrypted))
    df.columns = [c.strip() for c in df.columns]

    return df
