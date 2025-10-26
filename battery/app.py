from flask import Flask, request, jsonify, render_template
import pymysql
import re
import random
import string
from datetime import datetime, date

# ---------------- 配置 MySQL ----------------
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "sql",
    "password": "wRWVEW2BDZ",
    "database": "sql",
    "charset": "utf8mb4"
}

def get_conn():
    return pymysql.connect(**DB_CONFIG)

# ---------------- 初始化 Flask ----------------
app = Flask(__name__)

# ---------------- 工具函数 ----------------
def generate_table_name():
    """生成合法表名：8位，至少包含一个小写字母和一个数字"""
    while True:
        name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        if re.fullmatch(r'(?=.*[a-z])(?=.*\d)[a-z\d]{8}', name):
            return name

def check_table_name(name):
    """检查表名是否合法"""
    if not name:
        return False
    return bool(re.fullmatch(r'(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{8}', name))

def create_table_if_not_exists(cursor, table_name):
    """检查表是否存在，如果不存在则创建"""
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            time DATETIME NOT NULL,
            battery INT NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

def insert_battery(cursor, table_name, battery_value):
    """写入时间 + 电量"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(f"""
        INSERT INTO `{table_name}` (time, battery) VALUES (%s, %s)
    """, (now, battery_value))

# ---------------- Flask 路由 ----------------
@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = request.get_json()
        if not data or 'battery' not in data:
            return jsonify({'error': 'battery field required'}), 400

        battery = data['battery']
        table = data.get('table')
        if not table:
            table = generate_table_name()

        if not check_table_name(table):
            return jsonify({'error': 'Invalid table name'}), 400

        conn = get_conn()
        cursor = conn.cursor()


        # 创建表（如果不存在）
        create_table_if_not_exists(cursor, table)

        # 写入数据
        insert_battery(cursor, table, battery)
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "成功", "table": table, "battery": battery})

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

# --- 页面路由 ---
@app.route('/')
def index():
    return render_template('view.html')


# --- API：返回表的电量数据（去除连续相同电量值 + 动态 min/max） ---
@app.route('/api/data')
def api_data():
    table = request.args.get('table', '').strip()
    date_str = request.args.get('date', '')
    if not check_table_name(table):
        return jsonify({"error": "invalid table name"}), 400

    try:
        query_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except Exception:
        return jsonify({"error": "invalid date"}), 400

    try:
        conn = get_conn()
        cursor = conn.cursor()
        sql = f"""
            SELECT time, battery FROM `{table}`
            WHERE DATE(time) = %s
            ORDER BY time ASC
        """
        cursor.execute(sql, (query_date,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        raw_data = [{"time": r[0].strftime("%H:%M:%S"), "battery": int(r[1])} for r in rows]

        # 去除连续相同电量值
        filtered = []
        last_battery = None
        for entry in raw_data:
            if entry["battery"] != last_battery:
                filtered.append(entry)
                last_battery = entry["battery"]

        if filtered:
            min_bat = min(d["battery"] for d in filtered)
            max_bat = max(d["battery"] for d in filtered)
        else:
            min_bat, max_bat = 0, 100

        return jsonify({
            "status": "ok",
            "table": table,
            "date": str(query_date),
            "data": filtered,
            "min_battery": min_bat,
            "max_battery": max_bat
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
# ---------------- 启动 Flask ----------------
if __name__ == '__main__':
    print("Starting Flask server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
