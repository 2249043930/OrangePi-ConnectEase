# OrangePi ConnectEase 部署指南

## 1. 准备工作

### 1.1 开发板要求
- OrangePi Zero 开发板
- 已安装操作系统（推荐 Armbian 或 OrangePi OS）
- 已连接网络（以太网或 WiFi）
- 具有 root 权限

### 1.2 系统依赖
- `hostapd` - 用于创建热点
- `dnsmasq` - 用于 DNS 和 DHCP 服务
- `python3` - 运行项目
- `pip3` - 安装 Python 依赖

## 2. 部署步骤

### 2.1 上传项目文件

#### 方法一：使用 SCP（推荐）
```bash
# 在本地电脑上执行
scp -r OrangePi-ConnectEase orangepi@192.168.10.5:/home/
```

#### 方法二：使用 U 盘
1. 将项目文件复制到 U 盘
2. 将 U 盘插入开发板
3. 挂载 U 盘并复制文件到 `/home` 目录

### 2.2 安装依赖

```bash
# 登录开发板后执行
cd /home/OrangePi-ConnectEase

# 安装系统依赖
sudo apt-get update
sudo apt-get install -y hostapd dnsmasq python3-venv

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装 Python 依赖
pip install -r requirements.txt
```

### 2.3 配置系统服务

项目已经包含了系统服务配置文件 `orangepi-connectease.service`，直接复制到系统目录即可：

```bash
sudo cp orangepi-connectease.service /etc/systemd/system/
sudo systemctl enable orangepi-connectease
sudo systemctl start orangepi-connectease
```

### 2.4 验证部署

#### 查看服务状态
```bash
sudo systemctl status orangepi-connectease
```

#### 查看日志
```bash
sudo journalctl -u orangepi-connectease
```

## 3. 使用方法

### 3.1 首次使用
1. 开发板开机后，程序会自动运行
2. 如果没有可用的 WiFi 连接，开发板会开启名为 `OrangePi-Connect` 的热点
3. 热点无需密码，直接连接即可

### 3.2 配置 WiFi
1. 使用手机或电脑连接 `OrangePi-Connect` 热点
2. 在浏览器中访问 `http://192.168.42.1:8080`
3. 在 Web 界面中选择要连接的 WiFi
4. 输入密码（如果需要）
5. 点击「连接」按钮

![Web 界面截图](images/web_ui.png)

### 3.3 查看连接状态
- **未连接**：红灯慢速闪烁（GPIO PA17）
- **已连接**：绿灯慢速闪烁（GPIO PL10）

![LED 状态指示](images/led_status.png)

## 4. 故障排除

### 4.1 热点无法开启
- 检查 `hostapd` 和 `dnsmasq` 服务是否正常安装
- 检查 WiFi 模块是否正常工作
- 查看日志：`sudo journalctl -u orangepi-connectease`

### 4.2 WiFi 扫描失败
- 检查 WiFi 模块是否正常工作
- 检查 `iwlist` 命令是否可用

### 4.3 连接失败
- 检查密码是否正确
- 检查 WiFi 信号是否稳定
- 查看日志：`sudo journalctl -u orangepi-connectease`

### 4.4 LED 不工作
- 检查 GPIO 口是否正确配置
- 检查 `/sys/class/gpio` 目录是否存在

## 5. 项目结构

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

## 6. 注意事项

- 首次使用时，开发板会开启热点，需要通过热点进行初始配置
- 配置成功后，开发板会自动连接到配置的 WiFi，并关闭热点
- 若连接失败，开发板会重新开启热点，需要重新配置
- 程序会自动保存连接过的 WiFi 信息，下次开机时会自动尝试连接
