import requests
import streamlit as st
import smtplib
from email.mime.text import MIMEText


def get_country():
    try:
        res = requests.get("https://ipapi.co/json/")
        return res.json().get("country_name", "Unknown")
    except:
        return "Unknown"


def send_alert_email(to_email, message):

    sender = st.secrets["SENDER_EMAIL"]
    password = st.secrets["SENDER_APP_PASSWORD"]

    msg = MIMEText(message)
    msg["Subject"] = "Part Not Found Alert"
    msg["From"] = sender
    msg["To"] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(sender, password)
        s.send_message(msg)
