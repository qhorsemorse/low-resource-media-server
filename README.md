# ⚡ Ultra-Lightweight 32-Bit Python Media Server (Layered Architecture)

A high-performance, modular Python media server built specifically for **32-bit single-core machines with 2GB DDR3 RAM**, optimized for **720p `.mp4` Direct Play streaming** with **0% transcoding overhead**.

---

## 🏗️ Layered Architecture Layout

```
python_media_server/
├── main.py                     # App factory & middleware assembly
├── run_server.py               # Launcher script with local IP detection
├── core/                       # Core system utilities
│   ├── config.py               # System & stream parameters (64KB chunk size)
│   └── system.py               # Hardware monitoring (psutil RAM & CPU)
├── domain/                     # Domain schemas & custom exceptions
│   ├── models.py               # Pydantic data contracts (MediaItem, PaginatedResponse)
│   └── exceptions.py           # Domain exceptions
├── services/                   # Business Logic Layer
│   ├── library_service.py      # Threaded scanner, search & pagination logic
│   └── streaming_service.py    # Non-blocking HTTP 206 Range Stream Generator
├── api/                        # Presentation API Layer (Controllers & Routers)
│   ├── routes_media.py         # Paginated media API (/api/media)
│   ├── routes_stream.py        # 720p Stream API (/api/stream/{id})
│   ├── routes_stats.py         # Hardware stats API (/api/stats)
│   └── routes_system.py        # Background scan API (/api/scan)
├── static/                     # Web UI Frontend (HTML/CSS/JS with state persistence)
└── media/                      # 720p Video library storage
```

---

## 🚀 Quick Setup Instructions

1. Navigate to the project directory:
   ```bash
   cd C:\Users\pietr\OneDrive\Desktop\python_media_server
   ```
2. Activate your virtual environment and install minimal dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your 720p `.mp4` video files into the `media/` directory.
4. Launch the server:
   ```bash
   python run_server.py
   ```
