import os
import pandas as pd
from cryptography.fernet import Fernet

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

KEY_FILE = "data/secret.key"

# -----------------------------
# Load or create encryption key
# -----------------------------
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()

    return Fernet(key)

fernet = load_key()

# -----------------------------
# SAVE encrypted file
# -----------------------------
def save_encrypted_file(uploaded_file, name):
    try:
        raw = uploaded_file.read()
        encrypted = fernet.encrypt(raw)

        path = f"{DATA_DIR}/{name}.enc"
        with open(path, "wb") as f:
            f.write(encrypted)

        return True, f"{name} file uploaded & encrypted"

    except Exception as e:
        return False, f"Encrypt failed: {str(e)}"

# -----------------------------
# LOAD encrypted file
# -----------------------------
def load_encrypted_file(name):
    try:
        path = f"{DATA_DIR}/{name}.enc"

        if not os.path.exists(path):
            return None

        with open(path, "rb") as f:
            encrypted = f.read()

        decrypted = fernet.decrypt(encrypted)

        # Convert decrypted bytes → DataFrame
        df = pd.read_excel(decrypted)

        return df

    except Exception as e:
        print("Decrypt failed:", e)
        return None

