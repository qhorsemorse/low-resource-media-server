# ⚡ Ultra-Lightweight 32-Bit Python Media Server

A high-performance, ultra-lightweight Python media server built specifically for **32-bit single-core machines with 2GB DDR3 RAM**, optimized for **720p `.mp4` Direct Play streaming** with **0% transcoding overhead**.

---

## 🌟 Key Features

* **32-Bit & Python 3.11.2 Native:** Designed from the ground up to run effortlessly on low-power 32-bit single-core hardware.
* **Ultra-Low Memory Footprint:** Uses **~25 MB RAM idle** and **< 1 MB RAM per active stream**.
* **Zero Video Stuttering:** Uses non-blocking HTTP 206 Byte-Range streaming (`aiofiles` + `asyncio.sleep(0)` yields), ensuring background disk activities (like downloading new files) never freeze active 720p streams.
* **Auto-Resume Memory:** Remembers where you stopped watching video files and prompts to resume.
* **Live System Resource Monitor:** Displays real-time server RAM MB, CPU %, and stream count right in the Web UI navbar.
* **Modern Dark UI:** Responsive single-page web app with search, media filtering, and custom video player.

---

## 🚀 Quick Setup Instructions

### 1. Activate your Python VENV
Open a terminal / PowerShell in the project directory:

```bash
cd C:\Users\pietr\OneDrive\Desktop\python_media_server
```

Activate your virtual environment:
- **Windows (PowerShell):**
  ```powershell
  .\Scripts\Activate.ps1
  ```
- **Linux / 32-Bit Machine:**
  ```bash
  source bin/activate
  ```

### 2. Install Minimal Dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Media Files
Place your 720p `.mp4` files (or subfolders like `Movies/`, `TV/`, `Downloads/`) directly into the `media/` folder.

### 4. Start the Media Server
```bash
python run_server.py
```

---

## 📱 Accessing from local devices (Smart TV, Phone, Tablet)

When `run_server.py` starts, it displays your local network IP:

* **Local PC:** `http://localhost:8000`
* **Smart TV / Phone / Laptop:** `http://192.168.x.x:8000` (Use the IP printed in the terminal)

---

## 🛠️ Architecture & 32-Bit Optimizations

1. **Async Chunk Streaming (`64 KB` chunks):** Streaming reads in tiny 64 KB blocks rather than buffering whole files into RAM, easily supporting 2GB+ / 4GB+ files on 32-bit systems.
2. **Single Uvicorn Worker:** Runs on 1 worker process, avoiding CPU context-switching overhead on 1-core processors.
3. **Threaded Directory Scanner:** Library scanning runs in a background thread via `asyncio.to_thread`, ensuring file indexing never delays a playing 720p movie.
