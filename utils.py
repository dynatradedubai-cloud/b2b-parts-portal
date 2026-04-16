import hashlib
import platform
import socket

def normalize(text):
    return str(text).lower().strip()

def get_device_fingerprint():
    system = platform.system()
    node = platform.node()
    processor = platform.processor()
    return hashlib.sha256(f"{system}-{node}-{processor}".encode()).hexdigest()

def get_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "unknown"
LANG = {
    "en": {
        "search": "Search Parts",
        "cart": "Cart",
        "no_results": "No results found",
    },
    "ar": {
        "search": "بحث عن القطع",
        "cart": "سلة المشتريات",
        "no_results": "لا توجد نتائج",
    }
}

def t(key):
    import streamlit as st
    lang = st.session_state.get("lang", "en")
    return LANG[lang].get(key, key)
