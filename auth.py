import streamlit as st
import bcrypt
import time
import random
import smtplib

from datetime import datetime, timedelta
from email.mime.text import MIMEText

from security import log_event, rate_limit
from database import load_encrypted_file

OTP_EXPIRY = 300


# =============================
# SEND OTP (SAFE)
# =============================
def send_otp(email, otp):
    try:
        sender = st.secrets["SENDER_EMAIL"]
        password = st.secrets["SENDER_APP_PASSWORD"]
        server = st.secrets["SMTP_SERVER"]
        port = int(st.secrets["SMTP_PORT"])
    except Exception:
        st.error("Email configuration missing in secrets")
        return

    msg = MIMEText(f"Your OTP is: {otp}")
    msg["Subject"] = "Dynatrade OTP"
    msg["From"] = sender
    msg["To"] = email

    try:
        with smtplib.SMTP(server, port) as s:
            s.starttls()
            s.login(sender, password)
            s.send_message(msg)
    except Exception as e:
        st.error(f"Failed to send OTP: {str(e)}")


# =============================
# LOGIN FLOW
# =============================
def login_flow(is_admin):

    st.title("Dynatrade Automotive LLC")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):

        if not rate_limit(user):
            st.error("Too many attempts")
            return

        # =============================
        # ADMIN LOGIN
        # =============================
        if is_admin:
            try:
                admin_user = st.secrets["ADMIN_EMAIL"]
                admin_hash = st.secrets["ADMIN_PASSWORD"]
            except Exception:
                st.error("Admin secrets missing")
                return

            if user != admin_user:
                st.error("Invalid credentials")
                return

            try:
                valid = bcrypt.checkpw(pwd.encode(), admin_hash.encode())
            except Exception:
                st.error("Invalid password format")
                return

            if not valid:
                st.error("Invalid credentials")
                return

            st.session_state.authenticated = True
            st.session_state.role = "admin"
            st.session_state.last_activity = time.time()

            log_event(user, "Admin login success")

            st.rerun()

        # =============================
        # CUSTOMER LOGIN
        # =============================
        users = load_encrypted_file("users")

        if users is None:
            st.error("User database not found")
            return

        row = users[users["Username"] == user]

        if row.empty:
            st.error("User not found")
            return

        stored_hash = row.iloc[0]["Password"]

        if not bcrypt.checkpw(pwd.encode(), stored_hash.encode()):
            st.error("Invalid password")
            return

        # OTP
        otp = str(random.randint(100000, 999999))

        st.session_state.otp_hash = bcrypt.hashpw(otp.encode(), bcrypt.gensalt())
        st.session_state.otp_expiry = datetime.now() + timedelta(seconds=OTP_EXPIRY)
        st.session_state.temp_user = user
        st.session_state.user_email = row.iloc[0]["Customer email ID"]

        send_otp(st.session_state.user_email, otp)

        st.success("OTP sent")

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

                log_event(st.session_state.temp_user, "Customer login success")

                st.rerun()
            else:
                st.error("Invalid OTP")
