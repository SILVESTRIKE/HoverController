# 🖐️ PRESENTATION GOD (HoverController + Voice)

**Công cụ hỗ trợ thuyết trình "3 KHÔNG": Không chạm - Không độ trễ - Không mạng.**

Đây là hệ thống điều khiển máy tính rảnh tay tối ưu, kết hợp cử chỉ (MediaPipe) và giọng nói offline (Vosk) để giúp bạn thuyết trình như một vị thần.

---

## 🚀 Tính Năng Nổi Bật

*   **⚡ Real-time Control**: Phản hồi tức thì nhờ thuật toán OneEuroFilter và tối ưu đa luồng.
*   **🖱️ Mouse Navigation**: Di chuột, click, kéo thả, cuộn trang bằng cử chỉ tay.
*   **🎤 Offline Voice**: Gõ văn bản và ra lệnh bằng giọng nói mà không cần Internet.
*   **🔄 Dual Modes**: Chuyển đổi linh hoạt giữa chế độ Điều khiển (Navigation) và Nhập liệu (Input).

---

## 🛠️ Cài Đặt

1.  **Yêu cầu**: Python 3.8+
2.  **Cài đặt thư viện**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Model Giọng Nói**:
    *   Đảm bảo thư mục `vosk-model-small-en-us-0.15` (hoặc bản VN) nằm cùng cấp với `main.py`.

---

## 🎮 Hướng Dẫn Sử Dụng

### 1. Khởi động
Chạy lệnh sau trong terminal:
```bash
python main.py
```
*(Nếu gặp lỗi, đảm bảo Webcam đang không bị ứng dụng khác chiếm dụng)*

### 2. Các Chế Độ (Modes)

Hệ thống có 2 chế độ chính, nhìn vào góc trên bên trái màn hình Camera để biết trạng thái:

#### 🟢 Chế Độ NAVIGATION (Mặc định)
*   **Mục đích**: Di chuột, click, thao tác trên màn hình.
*   **Mic**: Tắt (Mute) để tránh nhận diện nhầm khi bạn đang thuyết trình.

#### 🔴 Chế Độ INPUT (Nhập liệu)
*   **Mục đích**: Gõ văn bản hoặc ra lệnh bằng giọng nói.
*   **Mic**: Bật (Listening).

---

### 3. Bảng Cử Chỉ (Hand Gestures)

| Cử Chỉ | Hành Động | Mẹo |
| :--- | :--- | :--- |
| **☝️ Ngón trỏ (chỉ)** | **Di chuột** | Di chuyển nhẹ nhàng, hệ thống sẽ tự làm mượt. |
| **✌️ Hai ngón (trỏ+giữa)** | **Click TRÁI** | Giơ 2 ngón tay hình chữ V. |
| **🤏 Chụm tay (nhanh)** | **Click PHẢI** | Chụm ngón cái & trỏ chạm nhau rồi thả ra nhanh (< 0.2s). |
| **🖐️ Xoè 5 ngón (giữ)** | **Kéo Thả (Drag)** | Xòe tay ra và di chuyển để kéo (drag). |
| **💨 Phẩy tay nhanh** | **Alt+Tab** | Phẩy tay từ trái sang phải hoặc ngược lại. |
| **✊ 2 Tay Nắm** | **Zoom In/Out** | Nắm 2 tay: Kéo ra = Zoom In, Kéo vào = Zoom Out. |
| **✊ Nắm tay + Di chuyển** | **Cuộn Trang** | Nắm 1 tay lại và di chuyển lên/xuống để cuộn. |
| **👍 Thumbs Up** | **Vào chế độ INPUT** | Giơ ngón cái lên để bật Mic. |
| **✊ Nắm tay (khi ở Input)** | **Về chế độ NAVIGATION** | Nắm tay lại để tắt Mic. |

---

### 4. Lệnh Giọng Nói (Voice Commands)

Chỉ hoạt động khi ở chế độ **INPUT** (🔴).

| Câu Lệnh (Tiếng Anh) | Hành Động |
| :--- | :--- |
| *"Hello World"* (bất kỳ) | Gõ văn bản *"hello world"* |
| *"Enter", "Submit"* | Nhấn phím **Enter** |
| *"Tab", "Next"* | Nhấn phím **Tab** |
| *"Delete", "Back"* | Xóa (Backspace x5) |
| *"Clear"* | Xóa hết (Ctrl+A -> Del) |
| *"Copy", "Paste"* | Copy / Paste |
| *"Zoom In", "Zoom Out"* | Phóng to / Thu nhỏ (Trình duyệt) |
| *"Scroll Up", "Scroll Down"* | Cuộn trang lên / xuống |
| *"System Off"* | **Thoát chương trình** |

---

## 🔧 Tinh Chỉnh (Config)

Mở file `config.py` để chỉnh sửa độ nhạy theo ý muốn:

*   `MOUSE_SPEED_NORMAL`: Tốc độ chuột bình thường.
*   `MOUSE_SPEED_FAST`: Tốc độ khi vẩy tay nhanh.
*   `SCROLL_SENSITIVITY`: Độ nhạy cuộn trang.
*   `CLICK_THRESHOLD`: Thời gian phân biệt giữa Click và Drag (mặc định 0.2s).

---

## ❓ Xử Lý Sự Cố (Troubleshooting)

1.  **Delay/Lag?**
    *   Đảm bảo ánh sáng đủ tốt (nhưng không quá chói).
    *   Giảm `GESTURE_CONFIRM_FRAMES` trong `config.py` xuống 2 hoặc 1.
2.  **Khó Click/Hay bị Drag nhầm?**
    *   Tập chụm tay nhanh và dứt khoát.
    *   Tăng `PINCH_THRESHOLD` trong `config.py` nếu tay bạn nhỏ.
3.  **Lỗi "Vosk model not found"?**
    *   Kiểm tra lại tên thư mục model trong `voice_engine.py` hoặc tải lại model từ trang chủ Vosk.

---
**Enjoy your presentation! 🎤✨**
