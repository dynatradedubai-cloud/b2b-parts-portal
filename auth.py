import streamlit as st
import bcrypt, random, smtplib, time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from security import log_event, rate_limit

OTP_EXPIRY = 300

def send_otp(email, otp):
    msg = MIMEText(f"Your OTP is: {otp}")
    msg['Subject'] = "Dynatrade OTP"
    msg['From'] = st.secrets["SENDER_EMAIL"]
    msg['To'] = email

    with smtplib.SMTP(st.secrets["SMTP_SERVER"], int(st.secrets["SMTP_PORT"])) as s:
        s.starttls()
        s.login(st.secrets["SENDER_EMAIL"], st.secrets["SENDER_APP_PASSWORD"])
        s.send_message(msg)

def login_flow(is_admin):
    st.title("Dynatrade Automotive LLC")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if not rate_limit(user):
            st.error("Too many attempts. Try later.")
            return

        if is_admin:
            valid = (user == st.secrets["ADMIN_EMAIL"] and 
                     bcrypt.checkpw(pwd.encode(), st.secrets["ADMIN_PASSWORD"].encode()))
            email = st.secrets["SENDER_EMAIL"]
        else:
            # simplified user validation (will be from encrypted file)
            valid = True
            email = st.secrets["SENDER_EMAIL"]

        if not valid:
            log_event(user,"Wrong Password")
            st.error("Invalid credentials")
            return

        otp = str(random.randint(100000,999999))
        st.session_state.otp_hash = bcrypt.hashpw(otp.encode(), bcrypt.gensalt())
        st.session_state.otp_expiry = datetime.now() + timedelta(seconds=OTP_EXPIRY)
        st.session_state.temp_user = user

        send_otp(email, otp)
        st.success("OTP sent")

    if "otp_hash" in st.session_state:
        otp_input = st.text_input("Enter OTP")

        if st.button("Verify OTP"):
            if datetime.now() > st.session_state.otp_expiry:
                st.error("OTP expired")
                return

            if bcrypt.checkpw(otp_input.encode(), st.session_state.otp_hash):
                st.session_state.authenticated = True
                st.session_state.role = "admin" if is_admin else "customer"
                st.session_state.last_activity = time.time()
                st.success("Login success")
            else:
                log_event(user,"OTP Failed")
                st.error("Invalid OTP")
