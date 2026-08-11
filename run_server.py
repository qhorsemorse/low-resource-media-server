"""
Server Launcher Script for Python Media Server.
Python 3.11.2 Compatible.
Run this script to start the server.
"""

import socket
import sys

import uvicorn

from core.config import HOST, MEDIA_DIR, PORT


def get_local_ip() -> str:
    """Get local area network IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    local_ip = get_local_ip()
    
    print("=" * 65)
    print(" ⚡ ULTRA-LIGHTWEIGHT 32-BIT PYTHON MEDIA SERVER (V2 - LAYERED)")
    print(f" Python Version: {sys.version.split()[0]}")
    print("=" * 65)
    print(f" 📂 Media Directory: {MEDIA_DIR}")
    print(" 🚀 Server is running!")
    print(f" 💻 Access locally on this PC : http://localhost:{PORT}")
    print(f" 📱 Access from TV / Phone / Laptop: http://{local_ip}:{PORT}")
    print("=" * 65)
    print(" Place your 720p .mp4 video files inside the 'media/' folder.")
    print(" Press Ctrl+C to stop the server.")
    print("=" * 65 + "\n")

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,
        workers=1,
        access_log=False
    )


if __name__ == "__main__":
    main()
