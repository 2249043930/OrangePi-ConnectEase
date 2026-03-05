import subprocess
import time

class WifiManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def scan_wifi(self):
        """扫描周围的WiFi"""
        try:
            # 使用iwlist命令扫描WiFi
            result = subprocess.run(['iwlist', 'wlan0', 'scan'], 
                                  capture_output=True, text=True)
            
            wifi_list = []
            lines = result.stdout.split('\n')
            
            current_wifi = {}
            for line in lines:
                line = line.strip()
                if 'ESSID:' in line:
                    if current_wifi:
                        wifi_list.append(current_wifi)
                        current_wifi = {}
                    essid = line.split('ESSID:')[1].strip('"')
                    current_wifi['ssid'] = essid
                elif 'Signal level=' in line:
                    # 提取信号强度
                    signal = line.split('Signal level=')[1].split(' ')[0]
                    current_wifi['signal'] = int(signal)
                elif 'Encryption key:' in line:
                    # 检查是否需要密码
                    encrypted = line.split('Encryption key:')[1].strip()
                    current_wifi['encrypted'] = encrypted == 'on'
            
            if current_wifi:
                wifi_list.append(current_wifi)
            
            return wifi_list
        except Exception as e:
            print("扫描WiFi失败: {}".format(e))
            return []
    
    def connect(self, ssid, password):
        """连接到WiFi"""
        try:
            # 生成wpa_supplicant配置
            config = "network={\n    ssid=\"{}\"\n".format(ssid)
            if password:
                config += "    psk=\"{}\"\n".format(password)
            else:
                config += "    key_mgmt=NONE\n"
            config += "}\n"
            
            # 写入配置文件
            with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
                f.write(config)
            
            # 重启网络服务
            subprocess.run(['systemctl', 'restart', 'networking'], check=True)
            
            # 等待连接
            time.sleep(10)
            
            # 检查是否连接成功
            return self.get_current_connection() is not None
        except Exception as e:
            print("连接WiFi失败: {}".format(e))
            return False
    
    def get_current_connection(self):
        """获取当前连接的WiFi"""
        try:
            result = subprocess.run(['iwgetid', '-r'], 
                                  capture_output=True, text=True)
            ssid = result.stdout.strip()
            if ssid:
                return ssid
            return None
        except Exception as e:
            print("获取当前连接失败: {}".format(e))
            return None
