import subprocess
import time
import logging

logger = logging.getLogger('WifiManager')

class WifiManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        logger.info("初始化WiFi管理器")
    
    def scan_wifi(self):
        """扫描周围的WiFi"""
        try:
            logger.info("开始扫描周围的WiFi")
            # 使用iwlist命令扫描WiFi
            import subprocess
            proc = subprocess.Popen(['iwlist', 'wlan0', 'scan'], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            result = stdout.decode('utf-8')
            
            wifi_list = []
            lines = result.split('\n')
            
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
            
            logger.info(f"扫描完成，发现 {len(wifi_list)} 个WiFi网络")
            return wifi_list
        except Exception as e:
            logger.error("扫描WiFi失败: {}".format(e))
            return []
    
    def connect(self, ssid, password):
        """连接到WiFi"""
        try:
            logger.info(f"尝试连接WiFi: {ssid}")
            # 生成wpa_supplicant配置
            config = "network={\n    ssid=\"{}\"\n".format(ssid)
            if password:
                logger.debug(f"使用密码连接WiFi: {ssid}")
                config += "    psk=\"{}\"\n".format(password)
            else:
                logger.debug(f"无密码连接WiFi: {ssid}")
                config += "    key_mgmt=NONE\n"
            config += "}\n"
            
            # 写入配置文件
            logger.debug("写入wpa_supplicant配置文件")
            with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
                f.write(config)
            
            # 重启网络服务
            logger.info("重启网络服务")
            subprocess.run(['systemctl', 'restart', 'networking'], check=True)
            
            # 等待连接
            logger.info("等待连接...")
            time.sleep(10)
            
            # 检查是否连接成功
            connected_ssid = self.get_current_connection()
            if connected_ssid:
                logger.info(f"连接成功: {connected_ssid}")
                return True
            else:
                logger.error(f"连接失败: {ssid}")
                return False
        except Exception as e:
            logger.error("连接WiFi失败: {}".format(e))
            return False
    
    def get_current_connection(self):
        """获取当前连接的WiFi"""
        try:
            logger.debug("获取当前连接的WiFi")
            proc = subprocess.Popen(['iwgetid', '-r'], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            ssid = stdout.decode('utf-8').strip()
            if ssid:
                logger.info(f"当前连接的WiFi: {ssid}")
                return ssid
            else:
                logger.info("未连接到任何WiFi")
                return None
        except Exception as e:
            logger.error("获取当前连接失败: {}".format(e))
            return None
