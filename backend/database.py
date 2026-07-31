"""数据库配置与初始化"""
import sqlite3
import os
import tempfile

# 数据库放在用户临时目录内
DB_DIR = os.path.join(tempfile.gettempdir(), "pbl_generator")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "pbl_data.db")


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()

    # 课程表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            topic TEXT NOT NULL,
            major TEXT NOT NULL,
            student_level TEXT DEFAULT '高职本科（应用型本科）',
            class_hours INTEGER DEFAULT 8,
            group_size INTEGER DEFAULT 4,
            project_type TEXT NOT NULL,
            project_scenario TEXT,
            learning_objectives TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 生成的资源表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            resource_type TEXT NOT NULL,
            content TEXT NOT NULL,
            model_used TEXT,
            temperature REAL DEFAULT 0.7,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        )
    """)

    # 生成历史表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            resource_types TEXT NOT NULL,
            status TEXT DEFAULT 'success',
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
