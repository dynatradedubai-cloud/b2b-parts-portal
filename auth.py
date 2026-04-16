import streamlit as st
import bcrypt
import random
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText

from security import log_event, rate_limit
from database import load_encrypted_file

OTP_EXPIRY = 300  # 5 minutes


# =============================
# SEND OTP
# =============================

def send_otp(email, otp):
    msg = MIMEText(f"Your OTP is: {otp}")
    msg['Subject'] = "Dynatrade OTP"
    msg['From'] = st.secrets["SENDER_EMAIL"]
    msg['To'] = email

    with smtplib.SMTP(st.secrets["SMTP_SERVER"], int(st.secrets["SMTP_PORT"])) as s:
        s.starttls()
        s.login(st.secrets["SENDER_EMAIL"], st.secrets["SENDER_APP_PASSWORD"])
        s.send_message(msg)


# =============================
# LOGIN FLOW
# =============================

def login_flow(is_admin):

    st.title("Dynatrade Automotive LLC")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    # =============================
    # LOGIN BUTTON
    # =============================

    if st.button("Login"):

        if not rate_limit(user):
            st.error("Too many attempts. Try later.")
            return

        # =============================
        # ADMIN LOGIN (NO OTP)
        # =============================

        if is_admin:

            valid = (
                user == st.secrets["ADMIN_EMAIL"] and
                bcrypt.checkpw(pwd.encode(), st.secrets["ADMIN_PASSWORD"].encode())
            )

            if not valid:
                log_event(user, "Admin Wrong Password")
                st.error("Invalid admin credentials")
                return

            st.session_state.authenticated = True
            st.session_state.role = "admin"
            st.session_state.last_activity = time.time()

            log_event(user, "Admin Login Success")
            st.success("Admin login successful")
            st.rerun()

        # =============================
        # CUSTOMER LOGIN (WITH OTP)
        # =============================

        users = load_encrypted_file("users")

        if users is None:
            st.error("User database not found")
            return

        user_row = users[users["Username"] == user]

        if user_row.empty:
            st.error("User not found")
            return

        # Check blocked
        if user_row.iloc[0].get("Blocked", False):
            st.error("User is blocked")
            return

        # Password check
        stored_hash = user_row.iloc[0]["Password"]

        if not bcrypt.checkpw(pwd.encode(), stored_hash.encode()):
            log_event(user, "Wrong Password")
            st.error("Invalid credentials")
            return

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        st.session_state.otp_hash = bcrypt.hashpw(otp.encode(), bcrypt.gensalt())
        st.session_state.otp_expiry = datetime.now() + timedelta(seconds=OTP_EXPIRY)
        st.session_state.temp_user = user
        st.session_state.user_email = user_row.iloc[0]["Customer email ID"]

        send_otp(st.session_state.user_email, otp)
        st.success("OTP sent to your email")

    # =============================
    # OTP VERIFY
    # =============================

    if "otp_hash" in st.session_state:

        otp_input = st.text_input("Enter OTP")

        if st.button("Verify OTP"):

            if datetime.now() > st.session_state.otp_expiry:
                st.error("OTP expired")
                return

            if bcrypt.checkpw(otp_input.encode(), st.session_state.otp_hash):
                st.session_state.authenticated = True
                st.session_state.role = "customer"
                st.session_state.last_activity = time.time()

                log_event(st.session_state.temp_user, "Customer Login Success")

                st.success("Login successful")
                st.rerun()

            else:
                log_event(st.session_state.temp_user, "OTP Failed")
                st.error("Invalid OTP")
