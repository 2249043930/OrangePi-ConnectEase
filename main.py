#!/usr/bin/env python3
import os
import sys
import time
import threading
import subprocess
import sqlite3
import logging
from flask import Flask, render_template, request, redirect, url_for

# 配置日志
import datetime
import os

# 创建logs目录
logs_dir = 'logs'
os.makedirs(logs_dir, exist_ok=True)

# 生成当天日期的日志文件名
today = datetime.datetime.now().strftime('%Y-%m-%d')
log_file = os.path.join(logs_dir, f'orange pi-connectease-{today}.log')

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('OrangePi-ConnectEase')

# 导入自定义模块
from src.wifi_manager import WifiManager
from src.hotspot_manager import HotspotManager
from src.led_control import LEDControl
from src.database import DatabaseManager

app = Flask(__name__)

# 初始化各模块
try:
    logger.info("初始化数据库管理器")
    db_manager = DatabaseManager()
    
    logger.info("初始化WiFi管理器")
    wifi_manager = WifiManager(db_manager)
    
    logger.info("初始化热点管理器")
    hotspot_manager = HotspotManager()
    
    logger.info("初始化LED控制器")
    led_control = LEDControl()
except Exception as e:
    logger.error("初始化模块失败: {}".format(e))
    sys.exit(1)

# 全局变量
current_wifi = None

@app.route('/')
def index():
    try:
        # 扫描WiFi
        logger.info("扫描可用WiFi")
        wifi_list = wifi_manager.scan_wifi()
        
        # 获取历史连接
        logger.info("获取历史WiFi连接")
        history = db_manager.get_wifi_history()
        
        # 获取当前连接
        logger.info("获取当前WiFi连接")
        current = wifi_manager.get_current_connection()
        
        return render_template('index.html', wifi_list=wifi_list, history=history, current=current)
    except Exception as e:
        logger.error("处理主页请求失败: {}".format(e))
        return render_template('error.html')

@app.route('/connect', methods=['POST'])
def connect():
    try:
        ssid = request.form.get('ssid')
        password = request.form.get('password', '')
        
        logger.info("尝试连接WiFi: {}".format(ssid))
        # 尝试连接WiFi
        success = wifi_manager.connect(ssid, password)
        
        if success:
            logger.info("连接WiFi成功: {}".format(ssid))
            # 保存到历史
            db_manager.save_wifi(ssid, password)
            # 关闭热点
            hotspot_manager.stop_hotspot()
            # 控制LED
            led_control.set_connected()
            return redirect(url_for('success'))
        else:
            logger.error("连接WiFi失败: {}".format(ssid))
            # 连接失败，重新启动热点
            hotspot_manager.start_hotspot()
            return redirect(url_for('error'))
    except Exception as e:
        logger.error("处理连接请求失败: {}".format(e))
        # 连接失败，重新启动热点
        hotspot_manager.start_hotspot()
        return redirect(url_for('error'))

@app.route('/success')
def success():
    try:
        current = wifi_manager.get_current_connection()
        return render_template('success.html', current=current)
    except Exception as e:
        logger.error("处理成功页面请求失败: {}".format(e))
        return render_template('error.html')

@app.route('/error')
def error():
    return render_template('error.html')

def check_wifi_and_start_hotspot():
    """检查是否有可用的WiFi连接，如果没有则启动热点"""
    global current_wifi
    
    try:
        # 尝试连接历史WiFi
        logger.info("获取历史WiFi连接")
        history = db_manager.get_wifi_history()
        connected = False
        
        if history:
            logger.info("尝试连接历史WiFi，共 {} 个".format(len(history)))
            for wifi in history:
                ssid, password = wifi[1], wifi[2]
                logger.info("尝试连接: {}".format(ssid))
                if wifi_manager.connect(ssid, password):
                    current_wifi = ssid
                    led_control.set_connected()
                    connected = True
                    logger.info("连接成功: {}".format(ssid))
                    break
        else:
            logger.info("没有历史WiFi连接")
        
        if not connected:
            # 没有可用连接，启动热点
            logger.info("没有可用WiFi连接，启动热点")
            hotspot_manager.start_hotspot()
            led_control.set_disconnected()
    except Exception as e:
        logger.error("检查WiFi并启动热点失败: {}".format(e))
        # 发生错误，尝试启动热点
        try:
            hotspot_manager.start_hotspot()
            led_control.set_disconnected()
        except Exception as e2:
            logger.error("启动热点失败: {}".format(e2))

if __name__ == '__main__':
    try:
        # 检查WiFi并启动热点（如果需要）
        logger.info("启动OrangePi ConnectEase服务")
        check_wifi_and_start_hotspot()
        
        # 启动Web服务器
        logger.info("启动Web服务器，监听 0.0.0.0:8080")
        app.run(host='0.0.0.0', port=8080, debug=False)
    except Exception as e:
        logger.error("启动服务失败: {}".format(e))
        sys.exit(1)
