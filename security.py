import time
import csv
import os
import streamlit as st
from utils import get_device_fingerprint, get_ip

RATE_LIMIT = 5
BLOCK_TIME = 300  # seconds


# =============================
# RATE LIMIT
# =============================

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


# =============================
# LOGGING
# =============================

def log_event(user, event):
    os.makedirs("logs", exist_ok=True)
    file = "logs/audit_log.csv"

    ip = get_ip()
    device = get_device_fingerprint()

    new_file = not os.path.exists(file)

    with open(file, "a", newline="") as f:
        writer = csv.writer(f)

        if new_file:
            writer.writerow(["time", "user", "event", "ip", "device"])

        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            user,
            event,
            ip,
            device
        ])


# =============================
# SESSION ACTIVITY TRACKING
# =============================

def update_activity():
    st.session_state.last_activity = time.time()


# =============================
# AUTO LOGOUT (FIXED)
# =============================

def auto_logout():
    # If not logged in, ignore
    if "authenticated" not in st.session_state:
        return

    if not st.session_state.authenticated:
        return

    # If no activity yet, initialize
    if "last_activity" not in st.session_state or st.session_state.last_activity is None:
        st.session_state.last_activity = time.time()
        return

    # Safe check
    try:
        elapsed = time.time() - st.session_state.last_activity
    except Exception:
        st.session_state.last_activity = time.time()
        return

    if elapsed > 3600:  # 60 minutes
        st.session_state.authenticated = False
        st.session_state.role = None
        st.warning("⏱️ Session expired. Please login again.")
        st.rerun()
