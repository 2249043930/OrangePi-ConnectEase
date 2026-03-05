import time
import threading

class LEDControl:
    def __init__(self):
        self.red_led_pin = 'PA17'  # 红灯GPIO口
        self.green_led_pin = 'PL10'  # 绿灯GPIO口
        self._init_gpio()
        self._stop_event = threading.Event()
        self._thread = None
    
    def _get_gpio_number(self, pin):
        """获取GPIO编号"""
        # PA0-PA31: 0-31
        # PB0-PB31: 32-63
        # ...
        # PL0-PL31: 352-383
        if pin.startswith('PA'):
            return int(pin[2:])
        elif pin.startswith('PL'):
            return 352 + int(pin[2:])
        else:
            return int(pin[2:])
    
    def _init_gpio(self):
        """初始化GPIO"""
        try:
            # 导出GPIO
            red_gpio = self._get_gpio_number(self.red_led_pin)
            green_gpio = self._get_gpio_number(self.green_led_pin)
            
            with open('/sys/class/gpio/export', 'w') as f:
                f.write(str(red_gpio))
            with open('/sys/class/gpio/export', 'w') as f:
                f.write(str(green_gpio))
            
            # 设置为输出
            with open('/sys/class/gpio/{}/direction'.format(red_gpio), 'w') as f:
                f.write('out')
            with open('/sys/class/gpio/{}/direction'.format(green_gpio), 'w') as f:
                f.write('out')
        except Exception as e:
            print("初始化GPIO失败: {}".format(e))
    
    def _set_led(self, pin, state):
        """设置LED状态"""
        try:
            gpio_number = self._get_gpio_number(pin)
            with open('/sys/class/gpio/{}/value'.format(gpio_number), 'w') as f:
                f.write('1' if state else '0')
        except Exception as e:
            print("设置LED失败: {}".format(e))
    
    def set_disconnected(self):
        """设置未连接状态：红灯慢速闪烁"""
        # 停止当前线程
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        
        # 启动新线程控制LED
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._blink_red)
        self._thread.daemon = True
        self._thread.start()
    
    def set_connected(self):
        """设置已连接状态：红灯灭，绿灯慢速闪烁"""
        # 停止当前线程
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        
        # 关闭红灯
        self._set_led(self.red_led_pin, False)
        
        # 启动新线程控制绿灯
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._blink_green)
        self._thread.daemon = True
        self._thread.start()
    
    def _blink_red(self):
        """红灯闪烁"""
        while not self._stop_event.is_set():
            self._set_led(self.red_led_pin, True)
            time.sleep(1)
            self._set_led(self.red_led_pin, False)
            time.sleep(1)
    
    def _blink_green(self):
        """绿灯闪烁"""
        while not self._stop_event.is_set():
            self._set_led(self.green_led_pin, True)
            time.sleep(1)
            self._set_led(self.green_led_pin, False)
            time.sleep(1)
