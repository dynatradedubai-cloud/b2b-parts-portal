import streamlit as st
import time
import os
import pandas as pd

LOG_FILE = "logs/audit_log.csv"


# =============================
# ENSURE LOG FILE
# =============================
def init_log():
    os.makedirs("logs", exist_ok=True)

    if not os.path.exists(LOG_FILE):
        df = pd.DataFrame(columns=[
            "time", "user", "event", "detail"
        ])
        df.to_csv(LOG_FILE, index=False)


# =============================
# LOG EVENT
# =============================
def log_event(user, event, detail=""):
    init_log()

    df = pd.read_csv(LOG_FILE)

    new_row = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "event": event,
        "detail": detail
    }

    df = pd.concat([df, pd.DataFrame([new_row])])
    df.to_csv(LOG_FILE, index=False)


# =============================
# RATE LIMIT
# =============================
def rate_limit(user):

    if "attempts" not in st.session_state:
        st.session_state.attempts = {}

    now = time.time()

    user_data = st.session_state.attempts.get(user, [])

    # keep last 60 sec
    user_data = [t for t in user_data if now - t < 60]

    if len(user_data) > 5:
        return False

    user_data.append(now)
    st.session_state.attempts[user] = user_data

    return True


# =============================
# AUTO LOGOUT
# =============================
def auto_logout():
    if "last_activity" not in st.session_state:
        return

    if time.time() - st.session_state.last_activity > 3600:
        st.session_state.clear()
        st.rerun()


def update_activity():
    st.session_state.last_activity = time.time()
