# ⚔️ Triển Khai Thực Chiến (Deployment PoC)

## 1. Thiết lập Môi trường (Lab Setup & Scenario)
Bối cảnh của môi trường thử nghiệm đã được cô lập hoàn toàn (Sandbox):

| Thành phần | Thông số kỹ thuật | Vai trò |
| :--- | :--- | :--- |
| **Attacker (C2 Server)** | Kali Linux (`192.168.x.x`) | Chạy Flask Server (Port 1234), Quản lý Agent. |
| **Target (Victim)** | Windows 10/11 (`192.168.x.y`) | Máy mục tiêu bị xâm nhập qua tệp thực thi giả mạo. |
| **Vector** | Social Engineering / Payload | Nạn nhân thực thi tệp tin giả mạo (Trojanized Game). |

---

## 2. Chiến Dịch Thực Thi (The Campaign Walkthrough)

### Bước 1: Xâm nhập & Lập hồ sơ mục tiêu (Initial Access)
Giai đoạn đầu tiên ngay sau khi payload được thực thi trên máy nạn nhân.

<p align="center">
  <video src="media/videos/agent_checkin.mp4" width="900" controls></video>
</p>

| Khía cạnh | Chi tiết luồng xử lý |
| :--- | :--- |
| **Diễn biến** | Ngay khi tệp được mở, Agent bí mật thu thập "vân tay" hệ thống (Hostname, OS, CPU, RAM) và gửi về Server. |
| **Cơ chế Kỹ thuật** | Agent gọi hàm `check_in()`, đóng gói dữ liệu qua `psutil` và `platform` gửi POST đến API `/api/agent_checkin`. |
| **Telemetry** | Bắt đầu Beaconing: Agent gửi báo cáo CPU/RAM mỗi 1 giây để Server cập nhật trạng thái Live. |

---

### Bước 2: Thực thi Shell có trạng thái (Stateful Shell)
Quản trị viên thực hiện điều khiển máy mục tiêu thông qua dòng lệnh trực tiếp.

<p align="center">
  <video src="media/videos/stateful_shell.mp4" width="900" controls></video>
</p>

| Khía cạnh | Chi tiết luồng xử lý |
| :--- | :--- |
| **Diễn biến** | Thao tác `cd`, `dir` hoạt động mượt mà. Hệ thống ghi nhớ thư mục làm việc, không bị reset sau mỗi lệnh. |
| **Cơ chế Kỹ thuật** | Agent sử dụng biến toàn cục `current_working_dir` kết hợp `os.chdir()` và `subprocess.run(cwd=...)` để duy trì trạng thái. |
| **Kết quả** | Operator có quyền truy cập sâu vào cấu trúc file của nạn nhân như một phiên Terminal thực thụ. |

---

### Bước 3: Triển khai Payload bổ sung (Data Infiltration)
Đẩy các công cụ độc hại khác từ máy chủ C2 xuống máy mục tiêu.

<p align="center">
  <video src="media/videos/upload_cmd.mp4" width="900" controls></video>
</p>

| Khía cạnh | Chi tiết luồng xử lý |
| :--- | :--- |
| **Diễn biến** | Operator sử dụng lệnh `upload` để đẩy một tệp tin (VD: `malware.exe`) từ kho vũ khí C2 xuống máy nạn nhân. |
| **Cơ chế Kỹ thuật** | Server đọc file -> Mã hóa Base64 -> Gửi qua JSON. Agent nhận, giải mã và ghi xuống đĩa cứng máy mục tiêu. |

---

### Bước 4: Khai thác & Rút trích dữ liệu (Exfiltration)
Thu thập các tài liệu nhạy cảm từ máy nạn nhân về máy chủ điều khiển.

<p align="center">
  <video src="media/videos/download_cmd.mp4" width="900" controls></video>
</p>

| Khía cạnh | Chi tiết luồng xử lý |
| :--- | :--- |
| **Diễn biến** | Rút trích thành công các tệp tin mật từ máy mục tiêu. Dữ liệu xuất hiện ngay lập tức trong thư mục `c2_downloads`. |
| **Cơ chế Kỹ thuật** | Agent đọc file binary -> Base64 -> POST lên `/api/transfer/download`. Server lưu vào Loot Vault theo từng ID Agent. |

---

### Bước 5: Rút lui & Xóa dấu vết (Kill Switch)
Agent tự hủy để tránh bị phát hiện sau khi hoàn thành chiến dịch.

<p align="center">
  <video src="media/videos/erase_agent.mp4" width="900" controls></video>
</p>

| Khía cạnh | Chi tiết luồng xử lý |
| :--- | :--- |
| **Diễn biến** | Khi nhận lệnh `suicide`, Agent lập tức gỡ bỏ chính nó khỏi Registry startup và kết thúc tiến trình. |
| **Cơ chế Kỹ thuật** | Gọi hàm `remove_from_startup()` sử dụng `winreg` để xóa khóa Run. Xóa các tệp tin tạm và thoát bằng `sys.exit()`. |

---

## 3. Phân tích Dấu vết (Defensive Perspective)
Dưới góc độ của một **Blue Team / SOC Analyst**, chúng ta có thể phát hiện labRAT qua các dấu hiệu sau:

| Loại dấu vết | Phương pháp phát hiện | Mô tả chi tiết |
| :--- | :--- | :--- |
| **Mạng (Network)** | Traffic Analysis | Tần suất kết nối cố định (Beaconing) 1 giây/lần tới một IP lạ là dấu hiệu bất thường rõ rệt. |
| **Hệ thống (Host)** | Registry Monitoring | Sự xuất hiện của khóa lạ `WindowsUpdateService` trong `HKCU\...\Run` trỏ tới một file `.exe` không xác định. |
| **Hành vi (Behavior)** | Process Tree | Tiến trình cha (`agent.exe`) liên tục sinh ra các tiến trình con `cmd.exe` thực thi lệnh shell. |

---
<p align="center">
  <b>Made with 💻 and ☕ by <a href="https://github.com/Lux1dus">Lux1dus</a></b>
</p>