# 🚀 Oh-My-Port

> **Công cụ giao tiếp UART nhẹ, hiển thị thời gian thực dành cho lập trình viên nhúng.**  
> Không cần IDE nặng nề. Cắm vi điều khiển vào và dùng ngay.

![Platform](https://img.shields.io/badge/nền%20tảng-Windows%20%7C%20Linux-blue)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/giấy%20phép-MIT-green)

---

## 📋 Mục lục

- [Giới thiệu](#giới-thiệu)
- [Tính năng](#tính-năng)
- [Tải về và chạy (Windows)](#tải-về-và-chạy-windows)
- [Tự build từ mã nguồn (Linux / Fork)](#tự-build-từ-mã-nguồn-linux--fork)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
- [File Log](#file-log)
- [Cấu trúc dự án](#cấu-trúc-dự-án)

---

## Giới thiệu

![UI](Lib\1.png)

**Oh-My-Port** là một ứng dụng terminal cổng nối tiếp portable, được xây dựng bằng Python (`PyQt6` + `pyserial`).  
Phần mềm được thiết kế dành cho các lập trình viên nhúng, cho phép đọc và ghi UART tới vi điều khiển một cách nhanh chóng — không cần mở Visual Studio, STM32CubeIDE, hay bất kỳ IDE nặng nào khác.

Giao diện được thiết kế theo phong cách **Arch Linux Hyprland**: nền tối, viền màu neon, bố cục gọn gàng và font chữ monospace kiểu terminal.

---

## Tính năng

| Tính năng | Mô tả |
|---|---|
| 🔍 **Quét cổng tự động** | Phát hiện tất cả các cổng COM khả dụng khi khởi động |
| ⚡ **Tự động dò Baud Rate** | Thử nghiệm các tốc độ baud phổ biến và chốt tốc độ đúng một cách tự động |
| 📡 **Chế độ lắng nghe thời gian thực** | Đọc non-blocking với chu kỳ poll ~5ms, giao diện cập nhật 30fps |
| 📤 **Chế độ gửi** | Hỗ trợ văn bản thô và JSON (kiểm tra cú pháp trước khi gửi) |
| 🔁 **Gửi hàng loạt (Burst Send)** | Gửi lặp lại `N` lần với tần số `f` Hz để kiểm thử tải phần cứng |
| 🗂️ **Ghi log theo phiên làm việc** | Mỗi lần kết nối tạo ra một file log mới theo thời gian, không ghi đè file cũ |
| 🖥️ **Chế độ Hex** | Chuyển đổi hiển thị dữ liệu nhận về dạng thập lục phân |

---

## Tải về và chạy (Windows)

Không cần cài đặt. Tải file `.exe` portable từ trang **[Releases](../../releases)**.

```
oh-my-port-windows.exe
```

Nhấp đúp để chạy. Windows Defender có thể hiện cảnh báo cho file chưa được ký — nhấn **"More info" → "Run anyway"** để tiếp tục.

> **Yêu cầu:** Windows 10 trở lên (64-bit). Không cần cài Python.

---

## Tự build từ mã nguồn (Linux / Fork)

Người dùng Linux cần tự build binary trên máy. Quá trình mất khoảng 1–2 phút.

### Chuẩn bị

```bash
# Cài đặt uv (trình quản lý gói Python)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Cài đặt thư viện hệ thống cho PyQt6 trên Linux
sudo apt-get install -y \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libgl1-mesa-glx \
    libegl1
```

> Trên Arch Linux: `sudo pacman -S qt6-base`  
> Trên Fedora/RHEL: `sudo dnf install qt6-qtbase`

### Các bước build

```bash
# 1. Clone mã nguồn
git clone https://github.com/NhatDang47/oh-my-port.git
cd oh-my-port

# 2. Cài đặt các thư viện Python
uv sync

# 3. Build binary portable
chmod +x build_linux.sh
./build_linux.sh
```

File đầu ra sẽ nằm tại:
```
dist/linux/oh-my-port
```

Chạy trực tiếp:
```bash
./dist/linux/oh-my-port
```

> **Lưu ý:** Trên Linux, bạn có thể cần thêm user vào nhóm `dialout` để có quyền truy cập cổng serial:
> ```bash
> sudo usermod -aG dialout $USER
> # Đăng xuất và đăng nhập lại để áp dụng
> ```

---

## Hướng dẫn sử dụng

### Bước 1 — Kết nối thiết bị

1. Cắm vi điều khiển vào cổng USB.
2. Mở **Oh-My-Port**.
3. Nhấn **"Scan Ports"** để làm mới danh sách cổng.
4. Chọn cổng COM của thiết bị từ danh sách thả xuống.

### Bước 2 — Cấu hình Baud Rate

**Cách A — Chọn thủ công:**  
Chọn tốc độ baud từ danh sách (9600 / 19200 / 38400 / 57600 / **115200** / 230400 / 460800 / 921600).

**Cách B — Dò tự động:**  
Nhấn **"Auto Detect Baud"**. Phần mềm sẽ lần lượt thử từng tốc độ baud phổ biến, lấy mẫu dữ liệu đến và tự động chọn tốc độ cho kết quả đọc hợp lệ.

### Bước 3 — Kết nối

Nhấn **"Connect"**. Nút chuyển sang màu đỏ để báo hiệu phiên đang hoạt động.  
Dữ liệu từ vi điều khiển sẽ hiển thị ngay lập tức trên cửa sổ terminal.

### Bước 4 — Đọc dữ liệu

- **Chế độ thường**: Dữ liệu nhận được giải mã UTF-8 và hiển thị màu xanh lá.
- **Chế độ Hex**: Tích vào ô "Hex View" để xem byte thô dưới dạng thập lục phân.
- **Xóa màn hình**: Nhấn "Clear Terminal" để xóa hiển thị (file log không bị ảnh hưởng).

### Bước 5 — Gửi dữ liệu

1. Nhập nội dung cần gửi vào ô nhập liệu ở phía dưới.
2. Chọn định dạng đầu ra:
   - **Text (`\r\n`)** — Thêm ký tự kết thúc dòng (chuẩn cho hầu hết UART vi điều khiển)
   - **Text (Raw)** — Gửi đúng những gì bạn nhập, không thêm ký tự nào
   - **JSON** — Kiểm tra cú pháp JSON trước khi gửi; từ chối nếu JSON không hợp lệ
3. Nhấn **"Send"** để gửi một lần.

### Bước 6 — Gửi hàng loạt (Kiểm thử tải)

1. Nhập nội dung và chọn định dạng như bước 5.
2. Đặt **"Repeat N Times"** — số lần gửi lặp lại.
3. Đặt **"Frequency (Hz)"** — tốc độ gửi (ví dụ: `10` = 10 tin mỗi giây).
4. Nhấn **"Burst Send"**. Mỗi lần gửi thành công sẽ hiển thị một dấu `.` trên terminal.

---

## File Log

Toàn bộ dữ liệu nhận (RX) và gửi (TX) đều được tự động ghi lại.

- **Vị trí:** `~/Documents/oh-my-port/`
- **Định dạng tên file:** `log_YYYYMMDD_HHMMSS.txt`
- **Mỗi phiên làm việc** tạo ra **một file mới** — log cũ không bao giờ bị ghi đè.

Định dạng một dòng log:
```
[2026-04-21 19:30:00] [RX] Hello from MCU!
[2026-04-21 19:30:05] [TX] {"cmd": "ping"}
```

---

## Cấu trúc dự án

```
oh-my-port/
├── src/
│   ├── main.py                  # Điểm khởi động ứng dụng
│   ├── gui/
│   │   └── main_window.py       # Giao diện PyQt6 + QSS (Hyprland theme)
│   ├── core/
│   │   ├── serial_manager.py    # Wrapper pyserial
│   │   └── threads.py           # QThread: Reader / AutoBaud / Repeater
│   └── utils/
│       └── logger.py            # Logger bất đồng bộ (queue-based)
├── oh-my-port.spec              # Cấu hình build PyInstaller
├── build_windows.ps1            # Script build Windows
├── build_linux.sh               # Script build Linux
└── .github/workflows/build.yml  # GitHub Actions CI (tự build cả 2 nền tảng)
```

---

## Chạy từ mã nguồn (Development)

```bash
uv sync
uv run src/main.py
```

---

*Được xây dựng với ❤️ dành cho cộng đồng lập trình nhúng.*
