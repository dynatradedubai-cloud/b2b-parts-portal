from cryptography.fernet import Fernet
import streamlit as st
import pandas as pd
import os

DATA_DIR = "data"

def get_fernet():
    return Fernet(st.secrets["ENCRYPTION_KEY"].encode())

def save_encrypted(file, name):
    f = get_fernet()
    encrypted = f.encrypt(file.read())

    with open(f"{DATA_DIR}/{name}.enc","wb") as out:
        out.write(encrypted)

def load_encrypted(name):
    path = f"{DATA_DIR}/{name}.enc"
    if not os.path.exists(path):
        return None

    f = get_fernet()
    with open(path,"rb") as file:
        decrypted = f.decrypt(file.read())

    return pd.read_excel(decrypted)
