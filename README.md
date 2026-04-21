# 🚀 Oh-My-Port

> **A lightweight, real-time UART communication tool for embedded developers.**  
> No heavy IDE required. Just plug in your microcontroller and go.

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-blue)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📋 Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Download & Run (Windows)](#download--run-windows)
- [Build from Source (Linux / Fork)](#build-from-source-linux--fork)
- [Usage Guide](#usage-guide)
- [Log Files](#log-files)
- [Project Structure](#project-structure)

---

## Introduction

![UI](.\lib\1.png)

**Oh-My-Port** is a portable serial terminal application built with Python (`PyQt6` + `pyserial`).  
It is designed for embedded developers who need to quickly read from and write to microcontrollers over UART — without opening Visual Studio, STM32CubeIDE, or any other heavy IDE.

The UI is styled after the **Arch Linux Hyprland** aesthetic: dark background, neon borders, tiling-inspired layout, and monospace terminal font.

---

## Features

| Feature | Description |
|---|---|
| 🔍 **Port Auto-Scan** | Detects all available COM ports on startup |
| ⚡ **Auto Baud Rate Detection** | Tests common baud rates and identifies the correct one automatically |
| 📡 **Real-Time Listen Mode** | Non-blocking background reader with ~5ms poll interval. Display updates at 30fps |
| 📤 **Send Mode** | Supports plain text and JSON (with syntax validation before sending) |
| 🔁 **Burst Send** | Repeat a payload `N` times at a configurable frequency (`f` Hz) for stress testing |
| 🗂️ **Per-Session Logging** | Each session creates a new timestamped log file in `~/Documents/oh-my-port/` |
| 🖥️ **Hex View** | Toggle hex display of raw received bytes |

---

## Download & Run (Windows)

No installation required. Download the pre-built portable `.exe` from the **[Releases](../../releases)** page.

```
oh-my-port-windows.exe
```

Double-click to launch. Windows Defender may show a warning for unsigned executables — click **"More info" → "Run anyway"**.

> **Requirements:** Windows 10 or later (64-bit). No Python installation needed.

---

## Build from Source (Linux / Fork)

Linux users need to build the binary locally. The process takes approximately 1–2 minutes.

### Prerequisites

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install required system libraries for PyQt6 on Linux
sudo apt-get install -y \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libgl1-mesa-glx \
    libegl1
```

> On Arch Linux: `sudo pacman -S qt6-base`  
> On Fedora/RHEL: `sudo dnf install qt6-qtbase`

### Build Steps

```bash
# 1. Clone the repository
git clone https://github.com/NhatDang47/oh-my-port.git
cd oh-my-port

# 2. Install Python dependencies
uv sync

# 3. Build the portable binary
chmod +x build_linux.sh
./build_linux.sh
```

The output binary will be at:
```
dist/linux/oh-my-port
```

Run it directly:
```bash
./dist/linux/oh-my-port
```

> **Note:** On Linux, you may need to add your user to the `dialout` group to access serial ports:
> ```bash
> sudo usermod -aG dialout $USER
> # Log out and back in for changes to take effect
> ```

---

## Usage Guide

### Step 1 — Connect Your Device

1. Plug your microcontroller into a USB port.
2. Launch **Oh-My-Port**.
3. Click **"Scan Ports"** to refresh the port list.
4. Select your device's COM port from the dropdown.

### Step 2 — Configure Baud Rate

**Option A — Manual:**  
Select a standard baud rate from the dropdown (9600 / 19200 / 38400 / 57600 / **115200** / 230400 / 460800 / 921600).

**Option B — Auto Detect:**  
Click **"Auto Detect Baud"**. The software will cycle through common baud rates, sample incoming data, and automatically select the rate that produces valid readable output.

### Step 3 — Connect

Click **"Connect"**. The button turns red to indicate an active session.  
Incoming data from your device will appear immediately in the terminal window.

### Step 4 — Reading Data

- **Normal Mode**: Received bytes are decoded as UTF-8 text and displayed in green.
- **Hex View**: Check the "Hex View" checkbox to display raw bytes in hexadecimal.
- **Clear**: Click "Clear Terminal" to wipe the display (the log file is not affected).

### Step 5 — Sending Data

1. Type your payload in the input field at the bottom.
2. Select the output format:
   - **Text (`\r\n`)** — Appends carriage return + newline (standard for most MCU UARTs)
   - **Text (Raw)** — Sends exactly what you typed, no terminator added
   - **JSON** — Validates JSON syntax before sending; rejects malformed input
3. Click **"Send"** for a single transmission.

### Step 6 — Burst Send (Stress Test)

1. Type your payload and select the format as above.
2. Set **"Repeat N Times"** — how many times to send.
3. Set **"Frequency (Hz)"** — how fast to send (e.g., `10` = 10 messages per second).
4. Click **"Burst Send"**. Each successful send is indicated by a `.` in the terminal.

---

## Log Files

All received (RX) and transmitted (TX) data is automatically logged.

- **Location:** `~/Documents/oh-my-port/`
- **Format:** `log_YYYYMMDD_HHMMSS.txt`
- **Each session** creates a **new file** — previous logs are never overwritten.

Log entry format:
```
[2026-04-21 19:30:00] [RX] Hello from MCU!
[2026-04-21 19:30:05] [TX] {"cmd": "ping"}
```

---

## Project Structure

```
oh-my-port/
├── src/
│   ├── main.py                  # Application entry point
│   ├── gui/
│   │   └── main_window.py       # PyQt6 UI + QSS styling (Hyprland theme)
│   ├── core/
│   │   ├── serial_manager.py    # pyserial wrapper
│   │   └── threads.py           # Reader / AutoBaud / Repeater QThreads
│   └── utils/
│       └── logger.py            # Async file logger (queue-based)
├── oh-my-port.spec              # PyInstaller build spec
├── build_windows.ps1            # Build script for Windows
├── build_linux.sh               # Build script for Linux
└── .github/workflows/build.yml  # GitHub Actions CI (auto-build both platforms)
```

---

## Development (Run from Source)

```bash
uv sync
uv run src/main.py
```

---

*Built with ❤️ for the embedded systems community.*
