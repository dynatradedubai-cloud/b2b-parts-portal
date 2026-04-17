import streamlit as st
import time
import random
import smtplib
import bcrypt

from datetime import datetime, timedelta
from email.mime.text import MIMEText

from security import log_event, rate_limit
from database import load_encrypted_file

OTP_EXPIRY = 300


def send_otp(email, otp):

    sender = st.secrets["SENDER_EMAIL"]
    password = st.secrets["SENDER_APP_PASSWORD"]
    server = st.secrets["SMTP_SERVER"]
    port = int(st.secrets["SMTP_PORT"])

    msg = MIMEText(f"Your OTP is: {otp}")
    msg["Subject"] = "Dynatrade OTP"
    msg["From"] = sender
    msg["To"] = email

    with smtplib.SMTP(server, port) as s:
        s.starttls()
        s.login(sender, password)
        s.send_message(msg)


def login_flow(is_admin):

    st.markdown("## 🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):

        if not rate_limit(user):
            st.error("Too many attempts")
            return

        # ADMIN LOGIN
        if is_admin:
            admin_user = st.secrets["ADMIN_EMAIL"]
            admin_hash = st.secrets["ADMIN_PASSWORD"]

            if user != admin_user:
                st.error("Invalid credentials")
                return

            if not bcrypt.checkpw(pwd.encode(), admin_hash.encode()):
                st.error("Invalid credentials")
                return

            st.session_state.authenticated = True
            st.session_state.role = "admin"
            st.session_state.last_activity = time.time()

            log_event(user, "ADMIN_LOGIN")

            st.rerun()

        # CUSTOMER LOGIN
        users = load_encrypted_file("users")

        if users is None:
            st.error("User database not found")
            return

        row = users[users["Username"] == user]

        if row.empty:
            st.error("User not found")
            return

        if pwd != str(row.iloc[0]["Password"]):
            st.error("Invalid password")
            return

        otp = str(random.randint(100000, 999999))

        st.session_state.otp = otp
        st.session_state.otp_expiry = datetime.now() + timedelta(seconds=OTP_EXPIRY)
        st.session_state.temp_user = user
        st.session_state.user_email = row.iloc[0]["Customer email ID"]

        send_otp(st.session_state.user_email, otp)

        st.success("OTP sent")

    # OTP VERIFY
    if "otp" in st.session_state:

        remaining = int((st.session_state.otp_expiry - datetime.now()).total_seconds())

        if remaining > 0:
            mins = remaining // 60
            secs = remaining % 60
            st.warning(f"⏳ OTP expires in {mins}:{secs:02d}")
        else:
            st.error("OTP expired")
            return

        otp_input = st.text_input("Enter OTP")

        if st.button("Verify OTP"):

            if otp_input == st.session_state.otp:
                st.session_state.authenticated = True
                st.session_state.role = "customer"
                st.session_state.last_activity = time.time()

                log_event(st.session_state.temp_user, "CUSTOMER_LOGIN")

                st.rerun()
            else:
                st.error("Invalid OTP")
