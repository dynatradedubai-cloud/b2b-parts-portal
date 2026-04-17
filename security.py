import streamlit as st
import time
import os
import pandas as pd

LOG_FILE = "logs/audit_log.csv"

REQUIRED_COLUMNS = ["time", "user", "event", "detail"]


# =============================
# FORCE CREATE VALID FILE
# =============================
def create_clean_log():
    os.makedirs("logs", exist_ok=True)
    df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    df.to_csv(LOG_FILE, index=False)


# =============================
# SAFE READ (BULLETPROOF)
# =============================
def read_log():

    # File not exists → create
    if not os.path.exists(LOG_FILE):
        create_clean_log()

    try:
        df = pd.read_csv(LOG_FILE)

        # Validate structure
        if list(df.columns) != REQUIRED_COLUMNS:
            raise ValueError("Invalid structure")

    except Exception:
        # ANY error → rebuild file
        create_clean_log()
        df = pd.read_csv(LOG_FILE)

    return df


# =============================
# LOG EVENT
# =============================
def log_event(user, event, detail=""):

    df = read_log()

    new_row = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "event": event,
        "detail": detail
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)


# =============================
# RATE LIMIT
# =============================
def rate_limit(user):

    if "attempts" not in st.session_state:
        st.session_state.attempts = {}

    now = time.time()

    user_data = st.session_state.attempts.get(user, [])
    user_data = [t for t in user_data if now - t < 60]

    if len(user_data) > 5:
        return False

    user_data.append(now)
    st.session_state.attempts[user] = user_data

    return True


# =============================
# SAFE AUTO LOGOUT
# =============================
def auto_logout():

    if "authenticated" not in st.session_state:
        return

    if "last_activity" not in st.session_state:
        st.session_state.last_activity = time.time()
        return

    if not isinstance(st.session_state.last_activity, (int, float)):
        st.session_state.last_activity = time.time()
        return

    if time.time() - st.session_state.last_activity > 3600:
        st.session_state.clear()
        st.warning("Session expired. Please login again.")
        st.rerun()


# =============================
# UPDATE ACTIVITY
# =============================
def update_activity():
    st.session_state.last_activity = time.time()
