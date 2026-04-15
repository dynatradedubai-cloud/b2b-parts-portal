import streamlit as st
import bcrypt
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from security import log_event

def send_otp(email, otp):
    msg = MIMEText(f"Your OTP is: {otp}")
    msg['Subject'] = "OTP Verification"
    msg['From'] = st.secrets["SENDER_EMAIL"]
    msg['To'] = email

    with smtplib.SMTP(st.secrets["SMTP_SERVER"], int(st.secrets["SMTP_PORT"])) as server:
        server.starttls()
        server.login(st.secrets["SENDER_EMAIL"], st.secrets["SENDER_APP_PASSWORD"])
        server.send_message(msg)

def login_flow(is_admin=False):
    st.title("Dynatrade Automotive LLC")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if is_admin:
            if username == st.secrets["ADMIN_EMAIL"] and bcrypt.checkpw(
                password.encode(), st.secrets["ADMIN_PASSWORD"].encode()
            ):
                otp = str(random.randint(100000, 999999))
                st.session_state.otp = bcrypt.hashpw(otp.encode(), bcrypt.gensalt())
                st.session_state.otp_expiry = datetime.now() + timedelta(minutes=5)
                st.session_state.temp_user = username

                send_otp(st.secrets["SENDER_EMAIL"], otp)
                st.success("OTP sent to admin email")

            else:
                log_event(username, "Wrong Password")
                st.error("Invalid credentials")

        else:
            # Placeholder (will connect DB later)
            otp = str(random.randint(100000, 999999))
            st.session_state.otp = bcrypt.hashpw(otp.encode(), bcrypt.gensalt())
            st.session_state.otp_expiry = datetime.now() + timedelta(minutes=5)
            st.session_state.temp_user = username

            send_otp(st.secrets["SENDER_EMAIL"], otp)
            st.success("OTP sent")

    # OTP verification
    if "otp" in st.session_state:
        otp_input = st.text_input("Enter OTP")

        if st.button("Verify OTP"):
            if datetime.now() > st.session_state.otp_expiry:
                st.error("OTP expired")
                return

            if bcrypt.checkpw(otp_input.encode(), st.session_state.otp):
                st.session_state.authenticated = True
                st.session_state.role = "admin" if is_admin else "customer"
                st.success("Login successful")
            else:
                log_event(username, "OTP Failed")
                st.error("Invalid OTP")
