import subprocess
import os

class HotspotManager:
    def __init__(self):
        self.hotspot_name = "OrangePi-Connect"
    
    def start_hotspot(self):
        """启动热点"""
        try:
            # 停止可能正在运行的服务
            subprocess.run(['systemctl', 'stop', 'wpa_supplicant'], capture_output=True)
            subprocess.run(['systemctl', 'stop', 'dnsmasq'], capture_output=True)
            
            # 配置网络接口
            subprocess.run(['ifconfig', 'wlan0', '192.168.42.1', 'netmask', '255.255.255.0'], check=True)
            
            # 配置hostapd和dnsmasq
            self._configure_hostapd()
            self._configure_dnsmasq()
            
            # 启动服务
            subprocess.run(['systemctl', 'start', 'hostapd'], check=True)
            subprocess.run(['systemctl', 'start', 'dnsmasq'], check=True)
            
            print("热点已启动: {}".format(self.hotspot_name))
        except Exception as e:
            print("启动热点失败: {}".format(e))
    
    def stop_hotspot(self):
        """停止热点"""
        try:
            subprocess.run(['systemctl', 'stop', 'hostapd'], capture_output=True)
            subprocess.run(['systemctl', 'stop', 'dnsmasq'], capture_output=True)
            print("热点已停止")
        except Exception as e:
            print("停止热点失败: {}".format(e))
    
    def _configure_hostapd(self):
        """配置hostapd"""
        config = "interface=wlan0\ndriver=nl80211\nssid={}\nhw_mode=g\nchannel=6\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0".format(self.hotspot_name)
        
        with open('/etc/hostapd/hostapd.conf', 'w') as f:
            f.write(config)
        
        # 更新hostapd配置路径
        with open('/etc/default/hostapd', 'w') as f:
            f.write('DAEMON_CONF="/etc/hostapd/hostapd.conf"')
    
    def _configure_dnsmasq(self):
        """配置dnsmasq"""
        config = "interface=wlan0\ndhcp-range=192.168.42.2,192.168.42.20,255.255.255.0,24h\ndomain=local\naddress=/router.local/192.168.42.1"
        
        with open('/etc/dnsmasq.conf', 'w') as f:
            f.write(config)
