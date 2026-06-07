# 🛠️ Hướng Dẫn Tùy Chỉnh Chuyên Sâu (CUSTOMIZATION GUIDE)

Tài liệu này hướng dẫn bạn cách chỉnh sửa code để thay đổi cảm giác điều khiển cho từng hành động cụ thể: **Click, Drag, Zoom, Tab, Scroll...**

---

## 1. 🖱️ Chỉnh Click Trái (Left Click)

Mặc định: **Chụm ngón cái & trỏ thật nhanh (< 0.2s)**.

**Để chỉnh độ nhạy (Dễ hay Khó chụm):**
Mở file `config.py`, sửa dòng:
```python
PINCH_THRESHOLD = 0.05
```
*   **Tăng lên (VD: 0.08)**: Dễ click hơn, nhưng dễ bị click nhầm khi chưa muốn.
*   **Giảm xuống (VD: 0.03)**: Khó click hơn, cần chụm sát hơn.

**Để chỉnh tốc độ click (Chống click đúp):**
Mở file `config.py`, sửa dòng:
```python
ACTION_COOLDOWN = 0.25
```
*   Đây là thời gian nghỉ (giây) giữa 2 lần click. Giảm xuống nếu bạn muốn spam click nhanh hơn.

---

## 2. ✊ Chỉnh Drag (Kéo Thả)

Mặc định: **Chụm ngón cái & trỏ và GIỮ (> 0.2s)**.

**Để thay đổi thời gian giữ:**
Mở file `main.py`, tìm dòng (khoảng dòng 108):
```python
CLICK_THRESHOLD = 0.2
```
*   **0.2 (giây)**: Là ranh giới. Chụm thả < 0.2s là Click. Chụm giữ > 0.2s là Drag.
*   Tăng lên (VD: 0.5): Bạn phải giữ lâu hơn mới bắt đầu kéo (tránh bị nhầm thành drag khi muốn click).
*   Giảm xuống (VD: 0.1): Drag nhạy hơn, nhưng dễ bị nhầm click thành drag.

---

## 3. ✌️ Chỉnh Click Phải (Right Click)

Mặc định: **Giơ 2 ngón (Trỏ + Giữa)**.

Cử chỉ này được quy định cứng trong logic nhận diện. Nếu muốn đổi cử chỉ, bạn phải sửa code trong `src/gesture_engine.py` (Nâng cao).
Tuy nhiên, bạn có thể chỉnh độ nhạy nhận diện cử chỉ chung trong `config.py`:
```python
GESTURE_CONFIRM_FRAMES = 2
```
*   Tăng lên: Cần giữ dáng tay lâu hơn máy mới nhận (tránh nhận nhầm).

---

## 4. ✊✊ Chỉnh Zoom (2 Tay Nắm)

Mặc định: **Nắm 2 tay và kéo ra xa / lại gần nhau**.

**Cách chỉnh cảm giác Zoom:**
Loại này dùng logic khoảng cách 2 tay. Code nằm trong `src/gesture_engine.py`.
Tìm đoạn:
```python
if dist_change > 0.03:  # Spreading apart -> Zoom IN
elif dist_change < -0.03:  # Coming together -> Zoom OUT
```
*   Tăng số `0.03` lên (VD 0.05): Phải kéo tay dứt khoát hơn mới zoom (đỡ bị zoom liên tục).
*   Giảm xuống: Zoom nhạy hơn.

---

## 5. 💨 Chỉnh Swipe (Phẩy Tay chuyển Tab)

Mặc định: **Xòe tay (OpenHand) và phẩy nhanh sang trái/phải**.

**Để chỉnh độ nhạy phẩy tay:**
Trong `src/gesture_engine.py`, tìm:
```python
self.SWIPE_WINDOW = 0.3      # Thời gian phẩy (phải nhanh hơn 0.3s)
self.SWIPE_THRESHOLD = 0.25  # Khoảng cách phẩy (phải dài hơn 25% màn hình)
```
*   Nếu thấy khó phẩy: **Tăng** `SWIPE_WINDOW` (cho phép phẩy chậm hơn) hoặc **Giảm** `SWIPE_THRESHOLD` (phẩy ngắn cũng nhận).

---

## 6. 📑 Chỉnh Tab (Chuyển ô nhập liệu)

Mặc định: Dùng **Giọng Nói** ("Tab", "Next").

**Để đổi từ lệnh:**
Mở `config.py`, sửa phần `"tab"` trong `VOICE_COMMANDS`:
```python
"tab": ["tab", "tiếp", "next", "sang ô kia"],
```

---

## 6. 📜 Chỉnh Scroll (Cuộn Trang)

Mặc định: **Nắm Tay (Fist) + Di chuyển tay**.

**Để chỉnh độ nhạy cuộn:**
Mở `config.py`:
```python
SCROLL_SENSITIVITY = 40  # Tốc độ cuộn (số dòng mỗi lần cuộn)
SCROLL_DEAD_ZONE = 0.02  # Vùng chết (di chuyển tay ít thì không cuộn)
SCROLL_MULTIPLIER = 8    # Hệ số nhân (di chuyển tay 1cm thì cuộn bao nhiêu)
```
*   Nếu thấy cuộn quá nhanh/chóng mặt: **Giảm** `SCROLL_SENSITIVITY`.
*   Nếu thấy phải vẩy tay mạnh mới cuộn: **Giảm** `SCROLL_DEAD_ZONE`.

---

## Tóm gọn: Sửa gì ở đâu?

| Muốn sửa... | Vào file... | Tìm dòng... |
| :--- | :--- | :--- |
| Độ nhạy Click/Độ khó chụm tay | `config.py` | `PINCH_THRESHOLD` |
| Delay giữa các lần click | `config.py` | `ACTION_COOLDOWN` |
| Thời gian giữ để Drag | `main.py` | `CLICK_THRESHOLD` |
| Tốc độ chuột | `config.py` | `MOUSE_SPEED_...` |
| Tốc độ cuộn trang | `config.py` | `SCROLL_SENSITIVITY` |
| Các câu lệnh giọng nói | `config.py` | `VOICE_COMMANDS` |
