import sqlite3
import os
import logging

logger = logging.getLogger('DatabaseManager')

class DatabaseManager:
    def __init__(self, db_path='data/wifi_history.db'):
        # 确保data目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        logger.info(f"初始化数据库管理器，数据库路径: {db_path}")
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        try:
            logger.info("初始化数据库，创建WiFi历史表")
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
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"初始化数据库失败: {e}")
    
    def save_wifi(self, ssid, password):
        """保存WiFi到历史"""
        try:
            logger.info(f"保存WiFi到历史: {ssid}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查是否已存在
            cursor.execute('SELECT id FROM wifi_history WHERE ssid = ?', (ssid,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新
                logger.info(f"更新已有WiFi: {ssid}")
                cursor.execute('''
                UPDATE wifi_history 
                SET password = ?, connected_at = CURRENT_TIMESTAMP 
                WHERE ssid = ?
                ''', (password, ssid))
            else:
                # 插入
                logger.info(f"插入新WiFi: {ssid}")
                cursor.execute('''
                INSERT INTO wifi_history (ssid, password) 
                VALUES (?, ?)
                ''', (ssid, password))
            
            conn.commit()
            conn.close()
            logger.info(f"WiFi保存成功: {ssid}")
        except Exception as e:
            logger.error(f"保存WiFi失败: {e}")
    
    def get_wifi_history(self):
        """获取WiFi历史记录"""
        try:
            logger.info("获取WiFi历史记录")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM wifi_history 
            ORDER BY connected_at DESC
            ''')
            
            history = cursor.fetchall()
            conn.close()
            logger.info(f"获取到 {len(history)} 条WiFi历史记录")
            return history
        except Exception as e:
            logger.error(f"获取WiFi历史记录失败: {e}")
            return []
    
    def get_wifi_by_ssid(self, ssid):
        """根据SSID获取WiFi信息"""
        try:
            logger.info(f"根据SSID获取WiFi信息: {ssid}")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM wifi_history WHERE ssid = ?', (ssid,))
            wifi = cursor.fetchone()
            
            conn.close()
            if wifi:
                logger.info(f"找到WiFi信息: {ssid}")
            else:
                logger.info(f"未找到WiFi信息: {ssid}")
            return wifi
        except Exception as e:
            logger.error(f"根据SSID获取WiFi信息失败: {e}")
            return None
