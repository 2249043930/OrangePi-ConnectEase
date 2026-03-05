import subprocess
import os
import logging

logger = logging.getLogger('HotspotManager')

class HotspotManager:
    def __init__(self):
        self.hotspot_name = "OrangePi-Connect"
        self.interface = "wlan0"
    
    def start_hotspot(self):
        """启动热点"""
        try:
            logger.info("开始启动热点")
            
            # 检查接口是否存在
            if not self._check_interface_exists():
                logger.error("WiFi接口 {} 不存在".format(self.interface))
                return False
            
            # 停止可能正在运行的服务
            logger.info("停止wpa_supplicant服务")
            subprocess.call(['systemctl', 'stop', 'wpa_supplicant'])
            logger.info("停止dnsmasq服务")
            subprocess.call(['systemctl', 'stop', 'dnsmasq'])
            
            # 配置网络接口
            logger.info("配置网络接口 {}".format(self.interface))
            try:
                subprocess.check_call(['ifconfig', self.interface, '192.168.42.1', 'netmask', '255.255.255.0'])
            except subprocess.CalledProcessError as e:
                logger.error("配置网络接口失败: {}".format(e))
                return False
            
            # 确保配置目录存在
            self._ensure_directories()
            
            # 配置hostapd和dnsmasq
            logger.info("配置hostapd")
            self._configure_hostapd()
            logger.info("配置dnsmasq")
            self._configure_dnsmasq()
            
            # 启动服务
            logger.info("启动hostapd服务")
            try:
                subprocess.check_call(['systemctl', 'start', 'hostapd'])
            except subprocess.CalledProcessError as e:
                logger.error("启动hostapd失败: {}".format(e))
                return False
            
            logger.info("启动dnsmasq服务")
            try:
                subprocess.check_call(['systemctl', 'start', 'dnsmasq'])
            except subprocess.CalledProcessError as e:
                logger.error("启动dnsmasq失败: {}".format(e))
                return False
            
            logger.info("热点已启动: {}".format(self.hotspot_name))
            return True
        except Exception as e:
            logger.error("启动热点失败: {}".format(e))
            return False
    
    def stop_hotspot(self):
        """停止热点"""
        try:
            logger.info("停止热点")
            subprocess.call(['systemctl', 'stop', 'hostapd'])
            subprocess.call(['systemctl', 'stop', 'dnsmasq'])
            logger.info("热点已停止")
        except Exception as e:
            logger.error("停止热点失败: {}".format(e))
    
    def _check_interface_exists(self):
        """检查WiFi接口是否存在"""
        try:
            subprocess.check_call(['ip', 'link', 'show', self.interface])
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _ensure_directories(self):
        """确保配置目录存在"""
        os.makedirs('/etc/hostapd', exist_ok=True)
    
    def _configure_hostapd(self):
        """配置hostapd"""
        config = "interface={}\ndriver=nl80211\nssid={}\nhw_mode=g\nchannel=6\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0".format(self.interface, self.hotspot_name)
        
        try:
            with open('/etc/hostapd/hostapd.conf', 'w') as f:
                f.write(config)
            logger.info("hostapd配置已写入")
        except Exception as e:
            logger.error("写入hostapd配置失败: {}".format(e))
        
        # 更新hostapd配置路径
        try:
            with open('/etc/default/hostapd', 'w') as f:
                f.write('DAEMON_CONF="/etc/hostapd/hostapd.conf"')
            logger.info("hostapd默认配置已更新")
        except Exception as e:
            logger.error("更新hostapd默认配置失败: {}".format(e))
    
    def _configure_dnsmasq(self):
        """配置dnsmasq"""
        config = "interface={}\ndhcp-range=192.168.42.2,192.168.42.20,255.255.255.0,24h\ndomain=local\naddress=/router.local/192.168.42.1".format(self.interface)
        
        try:
            with open('/etc/dnsmasq.conf', 'w') as f:
                f.write(config)
            logger.info("dnsmasq配置已写入")
        except Exception as e:
            logger.error("写入dnsmasq配置失败: {}".format(e))
