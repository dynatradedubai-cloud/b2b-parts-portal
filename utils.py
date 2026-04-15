import hashlib
import platform
import socket

def normalize(text):
    return str(text).lower().strip()

def get_device_fingerprint():
    system = platform.system()
    node = platform.node()
    processor = platform.processor()
    return hashlib.sha256(f"{system}-{node}-{processor}".encode()).hexdigest()

def get_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "unknown"
