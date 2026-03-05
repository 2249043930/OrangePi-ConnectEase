import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path='data/wifi_history.db'):
        # 确保data目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建WiFi历史表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS wifi_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ssid TEXT NOT NULL,
            password TEXT,
            connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_wifi(self, ssid, password):
        """保存WiFi到历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查是否已存在
        cursor.execute('SELECT id FROM wifi_history WHERE ssid = ?', (ssid,))
        existing = cursor.fetchone()
        
        if existing:
            # 更新
            cursor.execute('''
            UPDATE wifi_history 
            SET password = ?, connected_at = CURRENT_TIMESTAMP 
            WHERE ssid = ?
            ''', (password, ssid))
        else:
            # 插入
            cursor.execute('''
            INSERT INTO wifi_history (ssid, password) 
            VALUES (?, ?)
            ''', (ssid, password))
        
        conn.commit()
        conn.close()
    
    def get_wifi_history(self):
        """获取WiFi历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM wifi_history 
        ORDER BY connected_at DESC
        ''')
        
        history = cursor.fetchall()
        conn.close()
        return history
    
    def get_wifi_by_ssid(self, ssid):
        """根据SSID获取WiFi信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM wifi_history WHERE ssid = ?', (ssid,))
        wifi = cursor.fetchone()
        
        conn.close()
        return wifi
