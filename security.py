import streamlit as st
import time
import os
import pandas as pd
import hashlib
import uuid
import requests

LOG_FILE = "logs/audit_log.csv"

# Required schema (do not change order)
COLUMNS = [
    "time", "user", "event", "detail",
    "ip", "country", "device_id"
]


# =============================
# FILE SAFETY (SELF-HEALING)
# =============================
def _ensure_log_file():
    os.makedirs("logs", exist_ok=True)

    if not os.path.exists(LOG_FILE):
        pd.DataFrame(columns=COLUMNS).to_csv(LOG_FILE, index=False)
        return

    try:
        df = pd.read_csv(LOG_FILE)
        if list(df.columns) != COLUMNS:
            raise ValueError("Bad structure")
    except Exception:
        pd.DataFrame(columns=COLUMNS).to_csv(LOG_FILE, index=False)


def _read_log():
    _ensure_log_file()
    try:
        return pd.read_csv(LOG_FILE)
    except Exception:
        _ensure_log_file()
        return pd.read_csv(LOG_FILE)


# =============================
# NETWORK / DEVICE
# =============================
def get_ip():
    # On Streamlit Cloud you may not get real client IP; keep safe fallback
    return st.session_state.get("client_ip", "0.0.0.0")


def get_country():
    try:
        res = requests.get("https://ipapi.co/json/", timeout=2)
        return res.json().get("country_name", "Unknown")
    except Exception:
        return "Unknown"


def get_device_id():
    # Stable per-session device fingerprint
    if "device_id" not in st.session_state:
        raw = f"{uuid.uuid4()}-{time.time()}"
        st.session_state.device_id = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return st.session_state.device_id


# =============================
# LOGGING (ENRICHED)
# =============================
def log_event(user, event, detail=""):
    df = _read_log()

    new_row = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "event": event,
        "detail": detail,
        "ip": get_ip(),
        "country": get_country(),
        "device_id": get_device_id()
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)


# =============================
# RATE LIMIT + BLOCKING
# =============================
def rate_limit(user):
    """
    - Max 5 attempts per minute per user
    - Max 20 attempts per minute per IP (coarse)
    - 10 failures => temporary block for 5 minutes
    """
    now = time.time()

    if "rl_user" not in st.session_state:
        st.session_state.rl_user = {}
    if "rl_ip" not in st.session_state:
        st.session_state.rl_ip = {}
    if "blocked" not in st.session_state:
        st.session_state.blocked = {}

    ip = get_ip()

    # Check temporary block
    block_info = st.session_state.blocked.get(user)
    if block_info and now < block_info["until"]:
        return False

    # Per-user window
    u_times = st.session_state.rl_user.get(user, [])
    u_times = [t for t in u_times if now - t < 60]
    if len(u_times) >= 5:
        return False

    # Per-IP window
    ip_times = st.session_state.rl_ip.get(ip, [])
    ip_times = [t for t in ip_times if now - t < 60]
    if len(ip_times) >= 20:
        return False

    # Record attempt
    u_times.append(now)
    ip_times.append(now)
    st.session_state.rl_user[user] = u_times
    st.session_state.rl_ip[ip] = ip_times

    return True


def register_failure(user):
    """
    Track failures and apply temporary block after 10 failures.
    """
    now = time.time()

    if "failures" not in st.session_state:
        st.session_state.failures = {}

    f = st.session_state.failures.get(user, {"count": 0, "last": now})
    # Reset window after 10 minutes of inactivity
    if now - f["last"] > 600:
        f = {"count": 0, "last": now}

    f["count"] += 1
    f["last"] = now
    st.session_state.failures[user] = f

    # Block for 5 minutes after 10 failures
    if f["count"] >= 10:
        st.session_state.blocked[user] = {"until": now + 300}
        log_event(user, "USER_BLOCKED", "Too many failures")


def clear_failures(user):
    if "failures" in st.session_state and user in st.session_state.failures:
        del st.session_state.failures[user]


# =============================
# SESSION CONTROL
# =============================
def auto_logout(timeout_seconds=3600):
    if "authenticated" not in st.session_state:
        return

    if "last_activity" not in st.session_state:
        st.session_state.last_activity = time.time()
        return

    if not isinstance(st.session_state.last_activity, (int, float)):
        st.session_state.last_activity = time.time()
        return

    if time.time() - st.session_state.last_activity > timeout_seconds:
        user = st.session_state.get("temp_user", "unknown")
        log_event(user, "SESSION_TIMEOUT")
        st.session_state.clear()
        st.warning("Session expired. Please login again.")
        st.rerun()


def update_activity():
    st.session_state.last_activity = time.time()
