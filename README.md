#### ⚠️ Tuyên bố miễn trừ trách nhiệm

Dự án này là một Proof of Concept được phát triển cho mục đích giáo dục, nghiên cứu an ninh mạng và thử nghiệm trong môi trường kiểm soát, đã được cấp phép. Tác giả (Lux1dus) không chịu trách nhiệm đối với bất kỳ hành vi lạm dụng, thiệt hại hoặc hoạt động trái pháp luật nào phát sinh từ việc sử dụng dự án này. Việc sử dụng công cụ này trên các hệ thống khi chưa có sự cho phép rõ ràng có thể vi phạm pháp luật.
<br>

---

# 🐀 C2 Tactical Ops (LabRAT)

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-black?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Vanilla JS](https://img.shields.io/badge/Vanilla_JS-Frontend-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

--- 

## Trải nghiệm Nhanh (System Preview)

Dưới đây là giao diện trung tâm điều khiển (Command Center) của labRAT khi vừa khởi động server.

<p align="center">
  <img src="media/gifs/dashboard.gif" alt="LabRAT Dashboard Preview" width="900">
</p>

**Bạn tò mò hệ thống này vận hành thực tế sẽ ra sao?**

[👉 Triển khai & Demo (DEPLOYMENT_PoC.md)](DEPLOYMENT_PoC.md)

---

## I. Câu Chuyện Phía Sau (The Backstory & Motivation)

### Khởi nguồn ý tưởng
Mọi chuyện bắt đầu từ một sự cố thực tế: một người bạn chung phòng với tôi đã vô tình thực thi mã độc (Trojan) do nhầm lẫn nó là một tựa game. Dù đã trực tiếp tham gia xử lý sự cố (Incident Response) ngay lúc đó, chúng tôi cuối cùng vẫn phải cài đặt lại toàn bộ hệ thống để đảm bảo an toàn tuyệt đối. 

Sự việc này đã để lại trong tôi một trăn trở lớn. Thay vì chỉ dừng lại ở việc dùng phần mềm diệt virus và phản ứng thụ động, tôi muốn thực sự chạm vào "phần chìm của tảng băng". Đó là lý do **labRAT** ra đời. Bằng việc tự tay xây dựng một C2 Framework từ con số không, động lực cốt lõi của tôi là thấu hiểu trọn vẹn cách các tác nhân đe dọa (Threat Actors) thiết lập cơ chế giao tiếp, duy trì quyền điều khiển (Persistence), lẩn tránh hệ thống phòng thủ và thao tác trên máy mục tiêu.

### Mục tiêu cá nhân
* Không muốn "chỉ biết tấn công" mà để bước vào thế giới của "Kiến trúc hệ thống". Hiểu rõ hơn cách vận hành của mã độc.
* Xây dựng một góc nhìn đa chiều (Purple Team mindset): Hiểu sâu sắc cách mã độc hoạt động để từ đó thiết kế các phương án phòng thủ (Blue Team) hiệu quả hơn.

---

## II. Tổng Quan Dự Án (Project Overview)

### Tóm tắt (Executive Summary)
- **labRAT (C2 Tactical Ops)** là một hệ thống Command and Control thu nhỏ, hoạt động dựa trên mô hình Client-Server.

- Hệ thống cho phép quản trị viên giám sát và điều khiển các Agent (mục tiêu) từ xa thông qua một bảng điều khiển web (Tactical Dashboard) theo thời gian thực.

- Agent được thiết kế để tự động thu thập sinh hiệu hệ thống (CPU, RAM, OS), nhận lệnh, thực thi ẩn danh và báo cáo kết quả về máy chủ thông qua giao thức HTTP Polling.

### Công nghệ sử dụng (Tech Stack)
Hệ thống được thiết kế theo kiến trúc module hóa, tối ưu sự gọn nhẹ và độc lập. Dưới đây là các thành phần cốt lõi:

| Thành phần (Component) | Công nghệ (Tech) | Vai trò & Đặc điểm (Role & Features) |
| :--- | :--- | :--- |
| **Backend**<br>*(C2 Server)* | `Python (Flask)`<br>`SQLite3` | Xử lý RESTful API, quản lý hàng đợi lệnh (Command Queue). Lưu trữ vĩnh cửu trạng thái các Agent, lịch sử lệnh và event logs. |
| **Frontend**<br>*(Command Center)* | `HTML5 / CSS3`<br>`Vanilla JS` | Cung cấp giao diện Tactical tối màu. Sử dụng Fetch API để xử lý AJAX, cập nhật dữ liệu DOM liên tục mà không cần tải lại trang. |
| **Client**<br>*(Agent / Payload)* | `Python`<br>`PyInstaller` | Dùng `os`, `subprocess`, `psutil`, `winreg` để thao tác sâu vào hệ điều hành. Đóng gói payload thành tập tin `.exe` độc lập.<br>*(Lưu ý: Tệp thực thi biên dịch không được publish trên repository này).* |
---

## 🚀 Khởi động Nhanh (Getting Started - Local Lab)

Để triển khai thử nghiệm LabRAT trong môi trường nội bộ (Localhost), hãy làm theo các bước sau:

### 1. Cài đặt Môi trường
Tải mã nguồn và cài đặt các thư viện phụ thuộc:
```bash
# Clone repository (nếu bạn đang xem trên Git)
git clone https://github.com/Lux1dus/LabRAT.git
cd LabRAT

# Cài đặt thư viện
pip install -r requirements.txt
```

### 2. Khởi chạy C2 Server
Mở terminal tại thư mục `C2_Server` và chạy:
```bash
cd C2_Server
python server.py
```
*Mặc định Server sẽ lắng nghe tại cổng **1234**. Bạn có thể truy cập Dashboard tại: `http://127.0.0.1:1234`*

### 3. Triển khai Agent (Mục tiêu)
Mở một terminal mới tại thư mục `C2_Agent`:
```bash
cd C2_Agent
# Chạy agent dưới dạng script để kiểm tra kết nối
python agent.py
```
*Lưu ý: Đảm bảo biến `SERVER_URL` trong `agent.py` đang trỏ đúng về địa chỉ IP của Server (mặc định là localhost).*

---

### Quy Trình Hoạt Động (Workflow)

![Quy trình hoạt động](media/images/quytrinhhethong.png)

Hệ thống được chia làm 3 phân hệ rõ rệt, giao tiếp với nhau qua các RESTful API. Trái tim của hệ thống là `C2 Server` và `SQLite Database` đóng vai trò là trạm trung chuyển. 

Để duy trì kết nối mượt mà, Agent hoạt động theo cơ chế Polling kết hợp Beaconing (nhận lệnh & báo cáo trạng thái), trong khi Dashboard sử dụng AJAX Polling để liên tục cập nhật dữ liệu theo thời gian thực.

---

## III. Kiến Trúc API & Phân Tích Luồng Dữ Liệu (API & Data Flow)

Hệ thống vận hành nhờ 8 API cốt lõi, áp dụng Polling cho UI (0.5s) và Agent (1s) để đạt độ trễ cực thấp.

| Phân hệ | Endpoint | Phương thức | Chức năng cốt lõi (Luồng xử lý) |
| :--- | :--- | :--- | :--- |
| **Agent** | ``/api/agent_checkin`` | POST | Đăng ký Agent mới, thu thập info phần cứng, tạo bot_id. |
| **Agent** | `/api/sync` | POST | Beaconing duy trì kết nối (báo cáo CPU/RAM) và lấy lệnh từ Queue. |
| **Agent** | `/api/post_result` | POST | Gửi trả kết quả thực thi Shell về C2 để lưu vào Database. |
| **Transfer** | `/api/transfer/upload` | POST | Server đọc file -> Base64 -> Gửi cho Agent ghi xuống máy mục tiêu. |
| **Transfer**| `/api/transfer/download` | POST | Agent đọc file -> Base64 -> Gửi lên Server lưu làm chiến lợi phẩm (Loot). |
| **UI** | `/api/dashboard_data` | GET | app.js gọi mỗi 0.5s lấy toàn bộ trạng thái DB để update DOM (Real-time).|
| **UI** | `/api/send_command` | POST | Đẩy lệnh do Operator nhập vào Command Queue của Database. |
| **UI** | `/` | GET | Trả về index.html (Giao diện Tactical Dashboard). |

---

### Sơ Đồ Giao Tiếp Chuyên Sâu (Detailed API Routing)
Để làm rõ quá trình xử lý của các Endpoint trên, dưới đây là sơ đồ luồng dữ liệu chi tiết, minh họa chính xác cách Agent, C2 Server và lớp cơ sở dữ liệu (Database) tương tác với nhau trong một vòng đời thực thi lệnh:

![Sơ Đồ API Chi Tiết](media/images/hethongapi.png)

---

## IV. Các Điểm Hạn Chế & Cần Cải Thiện (Current Limitations)

Là một dự án Lab (Proof of Concept), **labRAT** vẫn còn một số điểm yếu cốt lõi nếu bị triển khai trong môi trường thực chiến có hệ thống giám sát chặt chẽ (EDR/IDS):

| Nhược điểm (Limitation) | Nguyên nhân kỹ thuật | Rủi ro Bảo mật (Risk) |
| :--- | :--- | :--- |
| **Dấu vết mạng ồn ào**<br>*(Noisy Network Traffic)* | Agent thiết lập Beaconing cố định mỗi 1 giây (nhịp tim tĩnh). | Rất dễ bị các hệ thống phân tích lưu lượng (Network Traffic Analysis) phát hiện sự bất thường. |
| **Giao tiếp bản rõ**<br>*(Plaintext HTTP)* | Toàn bộ lệnh và kết quả đang đi qua kênh HTTP không được bọc mã hóa. | Các công cụ giám sát hoặc IDS (như Wireshark, Snort) có thể bắt gói tin (Sniffing) và đọc được toàn bộ dữ liệu. |
| **Kích thước Payload lớn**<br>*(Heavy Payload)* | Agent viết bằng Python và đóng gói bằng PyInstaller thường tạo ra file `.exe` dung lượng >10MB. | Dễ bị các phần mềm Diệt virus (AV) truyền thống nhận diện, phân tích và chặn đứng dựa trên chữ ký (Signature). |

---

## V. Hướng Phát Triển Tương Lai (Future Roadmap)

Để nâng cấp labRAT tiệm cận hơn với một C2 Framework cấp độ nghiên cứu (Research-grade) và tăng khả năng lẩn tránh (Defense Evasion), lộ trình phát triển được chia thành các giai đoạn sau:

| Giai đoạn | Module Nâng cấp | Mô tả chi tiết kỹ thuật | Mục tiêu cốt lõi |
| :---: | :--- | :--- | :--- |
| **Phase 2** | **Mở rộng Vũ khí**<br>*(Offensive Modules)* | Bổ sung tính năng Keylogger, chụp ảnh màn hình (Screenshot), và trích xuất thông tin định danh (Credential dumping). | Nâng cao khả năng thu thập thông tin tình báo sau khi xâm nhập (Post-Exploitation). |
| **Phase 3** | **Phân tán Nằm vùng**<br>*(Redundant Persistence)* | Không chỉ dựa vào Registry, Agent sẽ phân thân và duy trì qua nhiều trạm: Scheduled Tasks, WMI Events, hoặc DLL Hijacking. Xây dựng một tiến trình "Watchdog" theo dõi chéo. | Đảm bảo Agent "bất tử". Nếu nạn nhân xóa khóa Registry, các cơ chế dự phòng sẽ lập tức khôi phục lại kết nối. |
| **Phase 4** | **Mã hóa Giao tiếp**<br>*(Payload Encryption)* | Tích hợp TLS/HTTPS hoặc tự bọc (wrap) dữ liệu API bằng các thuật toán mã hóa mạnh như AES-256 kết hợp trao đổi khóa RSA. | Chống lại việc phân tích gói tin mạng và che giấu hoàn toàn các thao tác điều khiển. |
| **Phase 5** | **Tàng hình Nhịp tim**<br>*(Beacon Jittering)* | Thay vì ngủ cố định 1s, Agent sẽ dùng thuật toán random thời gian ngủ (VD: 2s ± 15%). | Đánh lừa các thuật toán phân tích hành vi mạng dựa trên chu kỳ tĩnh của Blue Team. |
| **Phase 6** | **Tối ưu Hóa Payload**<br>*(Compiled Language)* | Chuyển đổi toàn bộ mã nguồn Agent từ Python sang các ngôn ngữ biên dịch cấp thấp như `C/C++`, `Rust` hoặc `Golang`. | Giảm thiểu tối đa kích thước file (< 2MB), loại bỏ các thư viện dependency và gây khó khăn cho quá trình dịch ngược (Reverse Engineering). |

---

## VI. Những kiến thức mới (Key Learnings & Concepts)

Trong quá trình xây dựng **labRAT**, tôi đã tiếp cận và làm chủ được các kỹ thuật cốt lõi sau:

| Kiến thức | Chi tiết kỹ thuật & Ứng dụng |
| :--- | :--- |
| **Kiến trúc Client-Server (Flask)** | Xây dựng C2 Server quản lý Agent, triển khai cơ chế truyền tải tệp tin đa nền tảng (Linux/Windows) trong mạng LAN. |
| **AJAX & JSON Dynamic Data** | Sử dụng Fetch API để đồng bộ hóa dữ liệu thời gian thực giữa UI và Backend; xử lý và trích xuất dữ liệu từ cấu trúc JSON. |
| **Payload Packaging (PyInstaller)** | Đóng gói mã nguồn Python thành tệp thực thi `.exe` độc lập, tối ưu hóa khả năng chạy trên môi trường mục tiêu không có sẵn Python. |
| **System Interaction (os & sys)** | Thao tác sâu với OS qua Absolute Path, quản lý Working Directory (CWD) và điều khiển vòng đời tiến trình qua trình thông dịch. |
| **Binary Data Transfer (Base64)** | Ứng dụng mã hóa Base64 để vận chuyển dữ liệu nhị phân (files) an toàn qua các giao thức text-based (HTTP/JSON) mà không làm hỏng cấu trúc. |

---

<p align="center">
  <b>Made with 💻 and ☕ by <a href="https://github.com/Lux1dus">Lux1dus</a></b>
</p>
