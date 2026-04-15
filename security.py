import datetime

def log_event(user, event):
    with open("logs.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} - {user} - {event}\n")
