import time, csv, os
import streamlit as st
from utils import get_device_fingerprint, get_ip

RATE_LIMIT = 5
BLOCK_TIME = 300  # seconds

def rate_limit(user):
    if "attempts" not in st.session_state:
        st.session_state.attempts = {}

    now = time.time()

    if user not in st.session_state.attempts:
        st.session_state.attempts[user] = []

    attempts = st.session_state.attempts[user]

    # Remove old attempts
    attempts = [t for t in attempts if now - t < BLOCK_TIME]
    st.session_state.attempts[user] = attempts

    if len(attempts) >= RATE_LIMIT:
        return False

    attempts.append(now)
    return True

def log_event(user, event):
    os.makedirs("logs", exist_ok=True)
    file = "logs/audit_log.csv"

    ip = get_ip()
    device = get_device_fingerprint()

    new = not os.path.exists(file)

    with open(file, "a", newline="") as f:
        writer = csv.writer(f)

        if new:
            writer.writerow(["time", "user", "event", "ip", "device"])

        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), user, event, ip, device])

def auto_logout():
    if "last_activity" in st.session_state:
        if time.time() - st.session_state.last_activity > 3600:
            st.session_state.authenticated = False
            st.warning("Session expired")
