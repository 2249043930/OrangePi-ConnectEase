# OrangePi ConnectEase

一个为 OrangePi 开发板设计的自动 WiFi 连接工具，实现开发板开机后自动扫描并连接历史 WiFi，若无可用连接则开启热点，通过 Web UI 进行 WiFi 配置。

## 功能特性

1. **自动连接历史 WiFi**：开机后自动尝试连接之前成功连接过的 WiFi
2. **热点自动开启**：当没有可用 WiFi 时，自动开启热点
3. **Web UI 配置**：通过手机或电脑连接热点后，访问 Web 界面配置 WiFi
4. **LED 状态指示**：
   - 未连接：红灯慢速闪烁
   - 已连接：绿灯慢速闪烁
5. **WiFi 历史管理**：使用 SQLite 数据库存储连接过的 WiFi 信息
6. **跨设备兼容**：Web UI 适配电脑和手机屏幕

## 项目架构

![项目架构图](images/architecture.png)

## Web 界面

![Web 界面截图](images/web_ui.png)

## LED 状态指示

![LED 状态指示](images/led_status.png)

## 技术栈

- **后端**：Python 3, Flask
- **前端**：HTML, Bootstrap 5
- **数据库**：SQLite
- **系统工具**：hostapd, dnsmasq, iwlist

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/OrangePi-ConnectEase.git
cd OrangePi-ConnectEase
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 安装系统依赖

```bash
# 安装 hostapd 和 dnsmasq
sudo apt-get update
sudo apt-get install hostapd dnsmasq
```

### 4. 配置系统服务

将项目设置为开机自启：

```bash
sudo cp orangepi-connectease.service /etc/systemd/system/
sudo systemctl enable orangepi-connectease
sudo systemctl start orangepi-connectease
```

## 使用方法

1. **开机自动运行**：系统启动后，程序会自动运行
2. **连接热点**：当开发板未连接 WiFi 时，会开启名为 `OrangePi-Connect` 的热点，无需密码
3. **配置 WiFi**：
   - 连接热点后，在浏览器中访问 `http://192.168.42.1:8080`
   - 在 Web 界面中选择要连接的 WiFi，输入密码（如果需要）
   - 点击「连接」按钮
4. **查看状态**：通过 LED 指示灯查看连接状态

## 项目结构

```
OrangePi-ConnectEase/
├── main.py                  # 主程序
├── src/                     # 源代码目录
│   ├── wifi_manager.py      # WiFi 管理模块
│   ├── hotspot_manager.py   # 热点管理模块
│   ├── led_control.py       # LED 控制模块
│   └── database.py          # 数据库管理模块
├── data/                    # 数据文件
│   └── wifi_history.db      # WiFi 历史数据库
├── logs/                    # 日志文件目录
│   └── orange pi-connectease-YYYY-MM-DD.log # 按日期命名的日志文件
├── templates/               # Web 模板
│   ├── index.html           # 主页面
│   ├── success.html         # 成功页面
│   └── error.html           # 错误页面
├── static/                  # 静态资源
│   └── styles.css           # CSS 样式文件
├── images/                  # 项目图片
│   ├── architecture.png     # 项目架构图
│   ├── web_ui.png           # Web 界面截图
│   └── led_status.png       # LED 状态指示图
├── orangepi-connectease.service # 系统服务配置文件
├── requirements.txt         # 依赖文件
├── README.md                # 项目文档
└── DEPLOY.md                # 部署指南
```

## 注意事项

1. 确保开发板已安装 `hostapd` 和 `dnsmasq` 服务
2. 确保开发板的 WiFi 模块正常工作
3. 首次使用时，开发板会开启热点，需要通过热点进行初始配置
4. 配置成功后，开发板会自动连接到配置的 WiFi，并关闭热点
5. 若连接失败，开发板会重新开启热点，需要重新配置

## 故障排除

- **热点无法开启**：检查 `hostapd` 和 `dnsmasq` 服务是否正常运行
- **WiFi 扫描失败**：检查 WiFi 模块是否正常工作
- **连接失败**：检查密码是否正确，或 WiFi 信号是否稳定
- **LED 不工作**：检查 GPIO 口是否正确配置

## 许可证

MIT License
