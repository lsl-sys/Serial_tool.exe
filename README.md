# 单片机串口调试工具

这是一个基于Python和PyQt5开发的串口调试工具，用于与单片机等设备进行串口通信。

## 功能特点

- 自动检测并列出所有可用串口
- 支持多种串口参数配置（波特率、数据位、停止位、校验位）
- 支持文本和十六进制两种发送/接收模式
- 支持自动发送功能，可设置发送间隔
- 支持显示时间戳
- 自动滚动和手动滚动接收窗口
- 简洁美观的用户界面

## 找到.exe

在`dist`目录下找到`main.exe`，这是一个独立的可执行文件，无需安装Python环境即可运行。

## 快速开始

### 方法一：使用环境检查工具（推荐）

双击运行`check_and_run.bat`，该工具会自动检查Python环境和必要的依赖包，并引导安装缺失的组件。

### 方法二：直接运行Python脚本

在使用前，需要安装以下依赖包：

```bash
pip install -r requirements.txt
```

然后直接运行Python脚本：

```bash
python main.py
```

### 方法三：使用批处理文件运行

双击运行`run_serial_tool_fixed.bat`，这是一个简化的批处理文件，用于直接启动程序。

## 生成可执行文件（EXE）

### 自动打包方法

double-click运行`build_final.bat`，该批处理文件会自动：
- 设置中文编码支持
- 检查Python环境
- 安装必要的依赖包
- 使用PyInstaller打包程序（包含serial.tools.list_ports模块）
- 打包完成后自动打开dist目录

### 手动打包方法

如果批处理文件执行失败，您可以尝试手动打包：
1. 安装依赖包：
```bash
pip install PyQt5 pyserial pyinstaller
```
2. 执行打包命令：
```bash
python -m PyInstaller --onefile --windowed --hidden-import=serial.tools.list_ports main.py
```
3. 打包成功后，可执行文件位于 `dist\main.exe`

## 使用说明

1. 选择正确的串口和波特率
2. 点击"连接"按钮打开串口
3. 在下方发送区域输入要发送的数据
4. 点击"发送"按钮发送数据
5. 接收区域将显示从串口接收到的数据

## 注意事项

1. **重要提示**：使用前请确保已安装正确的串口驱动程序
2. 长时间不使用时，请断开串口连接以释放资源
3. 使用自动发送功能时，请注意设置合理的发送频率，避免数据拥塞
4. 如遇到"No module named 'serial.tools'"错误，请使用 `build_final.bat` 重新打包程序
5. 如程序无法启动，可能需要以管理员身份运行批处理文件

## 许可证

MIT License