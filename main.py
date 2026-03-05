#!/usr/bin/env python3
import os
import sys
import time
import threading
import subprocess
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

# 导入自定义模块
from src.wifi_manager import WifiManager
from src.hotspot_manager import HotspotManager
from src.led_control import LEDControl
from src.database import DatabaseManager

app = Flask(__name__)

# 初始化各模块
db_manager = DatabaseManager()
wifi_manager = WifiManager(db_manager)
hotspot_manager = HotspotManager()
led_control = LEDControl()

# 全局变量
current_wifi = None

@app.route('/')
def index():
    # 扫描WiFi
    wifi_list = wifi_manager.scan_wifi()
    # 获取历史连接
    history = db_manager.get_wifi_history()
    # 获取当前连接
    current = wifi_manager.get_current_connection()
    return render_template('index.html', wifi_list=wifi_list, history=history, current=current)

@app.route('/connect', methods=['POST'])
def connect():
    ssid = request.form.get('ssid')
    password = request.form.get('password', '')
    
    # 尝试连接WiFi
    success = wifi_manager.connect(ssid, password)
    
    if success:
        # 保存到历史
        db_manager.save_wifi(ssid, password)
        # 关闭热点
        hotspot_manager.stop_hotspot()
        # 控制LED
        led_control.set_connected()
        return redirect(url_for('success'))
    else:
        # 连接失败，重新启动热点
        hotspot_manager.start_hotspot()
        return redirect(url_for('error'))

@app.route('/success')
def success():
    current = wifi_manager.get_current_connection()
    return render_template('success.html', current=current)

@app.route('/error')
def error():
    return render_template('error.html')

def check_wifi_and_start_hotspot():
    """检查是否有可用的WiFi连接，如果没有则启动热点"""
    global current_wifi
    
    # 尝试连接历史WiFi
    history = db_manager.get_wifi_history()
    connected = False
    
    for wifi in history:
        ssid, password = wifi[1], wifi[2]
        if wifi_manager.connect(ssid, password):
            current_wifi = ssid
            led_control.set_connected()
            connected = True
            break
    
    if not connected:
        # 没有可用连接，启动热点
        hotspot_manager.start_hotspot()
        led_control.set_disconnected()

if __name__ == '__main__':
    # 检查WiFi并启动热点（如果需要）
    check_wifi_and_start_hotspot()
    
    # 启动Web服务器
    app.run(host='0.0.0.0', port=8080, debug=False)
