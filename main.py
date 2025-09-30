import sys
import sys
import re
from datetime import datetime

# 使用pyserial包进行串口通信
import serial
import serial.tools.list_ports

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QTextEdit, QCheckBox, QMessageBox,
    QSplitter, QGroupBox, QFormLayout, QSpinBox, QSizePolicy, QTabWidget,
    QAction, QMenuBar, QMenu, QDialog, QGridLayout, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QBrush, QFontDatabase

class SerialThread(QThread):
    """串口数据接收线程"""
    data_received = pyqtSignal(str)
    connection_closed = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.running = False
        
    def run(self):
        self.running = True
        while self.running and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    self.data_received.emit(data.decode('utf-8', errors='replace'))
                self.msleep(10)
            except Exception as e:
                self.error_occurred.emit(str(e))
                self.running = False
                if self.serial_port.is_open:
                    self.serial_port.close()
                self.connection_closed.emit()
                break
        
    def stop(self):
        self.running = False
        self.wait()

class SerialMonitor(QMainWindow):
    """串口调试工具主窗口"""
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.receive_thread = None
        
        # 数据帧功能相关变量
        self.data_frames = []
        
        # 加载用户设置
        self.settings = QSettings("SerialMonitor", "Settings")
        self.load_settings()
        
        self.init_ui()
        self.refresh_ports()
        
        # 设置定时器定期刷新端口列表
        self.port_timer = QTimer(self)
        self.port_timer.timeout.connect(self.refresh_ports)
        self.port_timer.start(5000)  # 每5秒刷新一次
        

        
    def init_ui(self):
        """初始化用户界面，优化布局使其符合现代设计风格"""
        # 窗口设置
        self.setWindowTitle("现代串口调试工具")
        self.setGeometry(100, 100, 1080, 768)  # 增大窗口尺寸
        
        # 设置程序图标
        icon_path = "LOGO/NEWLOGO.jpg"
        self.setWindowIcon(QIcon(icon_path))
        
        # 初始化字体相关设置
        self.current_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.current_font.setPointSize(13)  # 默认字体大小
        
        # 创建菜单
        self.create_menu()
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # 添加状态栏
        self.statusBar().showMessage("就绪")
        
        # 初始化数据计数器
        self.received_bytes_count = 0
        self.sent_bytes_count = 0
        
        # 创建状态栏标签
        self.received_bytes_label = QLabel("接收: 0 字节")
        self.sent_bytes_label = QLabel("发送: 0 字节")
        
        # 将标签添加到状态栏
        self.statusBar().addPermanentWidget(self.received_bytes_label)
        self.statusBar().addPermanentWidget(QLabel("   "))  # 间隔
        self.statusBar().addPermanentWidget(self.sent_bytes_label)
        
        # 顶部控制区域 - 采用卡片式布局
        control_group = QGroupBox("串口设置")
        control_group.setObjectName("controlGroup")
        control_layout = QVBoxLayout()
        control_group.setLayout(control_layout)
        
        # 第一行设置：端口和波特率
        top_settings_layout = QHBoxLayout()
        top_settings_layout.setSpacing(15)
        
        # 端口选择
        port_layout = QHBoxLayout()
        port_label = QLabel("端口:")
        port_label.setFixedWidth(40)
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(200)
        refresh_button = QPushButton("刷新端口")
        refresh_button.setFixedWidth(90)
        refresh_button.clicked.connect(self.refresh_ports)
        
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(refresh_button)
        
        # 波特率选择
        baudrate_layout = QHBoxLayout()
        baudrate_label = QLabel("波特率:")
        baudrate_label.setFixedWidth(60)
        self.baudrate_combo = QComboBox()
        common_baudrates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        for baudrate in common_baudrates:
            self.baudrate_combo.addItem(str(baudrate), baudrate)
        self.baudrate_combo.setCurrentText("115200")
        self.baudrate_combo.setMinimumWidth(120)
        
        baudrate_layout.addWidget(baudrate_label)
        baudrate_layout.addWidget(self.baudrate_combo)
        baudrate_layout.addStretch()
        
        top_settings_layout.addLayout(port_layout)
        top_settings_layout.addLayout(baudrate_layout)
        control_layout.addLayout(top_settings_layout)
        
        # 第二行设置：数据位、停止位、校验位
        middle_settings_layout = QHBoxLayout()
        middle_settings_layout.setSpacing(15)
        
        # 数据位
        data_bits_layout = QHBoxLayout()
        data_bits_label = QLabel("数据位:")
        data_bits_label.setFixedWidth(60)
        self.data_bits_combo = QComboBox()
        for bits in [5, 6, 7, 8]:
            self.data_bits_combo.addItem(str(bits), bits)
        self.data_bits_combo.setCurrentText("8")
        self.data_bits_combo.setMinimumWidth(80)
        
        data_bits_layout.addWidget(data_bits_label)
        data_bits_layout.addWidget(self.data_bits_combo)
        
        # 停止位
        stop_bits_layout = QHBoxLayout()
        stop_bits_label = QLabel("停止位:")
        stop_bits_label.setFixedWidth(60)
        self.stop_bits_combo = QComboBox()
        self.stop_bits_combo.addItem("1", 1)
        self.stop_bits_combo.addItem("1.5", 1.5)
        self.stop_bits_combo.addItem("2", 2)
        self.stop_bits_combo.setCurrentText("1")
        self.stop_bits_combo.setMinimumWidth(80)
        
        stop_bits_layout.addWidget(stop_bits_label)
        stop_bits_layout.addWidget(self.stop_bits_combo)
        
        # 校验位
        parity_layout = QHBoxLayout()
        parity_label = QLabel("校验位:")
        parity_label.setFixedWidth(60)
        self.parity_combo = QComboBox()
        self.parity_combo.addItem("无", 'N')
        self.parity_combo.addItem("奇校验", 'O')
        self.parity_combo.addItem("偶校验", 'E')
        self.parity_combo.setCurrentIndex(0)
        self.parity_combo.setMinimumWidth(100)
        
        parity_layout.addWidget(parity_label)
        parity_layout.addWidget(self.parity_combo)
        
        # 流控制
        flow_control_layout = QHBoxLayout()
        flow_control_label = QLabel("流控制:")
        flow_control_label.setFixedWidth(60)
        self.flow_control_combo = QComboBox()
        self.flow_control_combo.addItem("无", 'N')
        self.flow_control_combo.addItem("RTS/CTS", 'R')
        self.flow_control_combo.addItem("XON/XOFF", 'X')
        self.flow_control_combo.addItem("两者", 'B')
        self.flow_control_combo.setCurrentIndex(0)
        self.flow_control_combo.setMinimumWidth(120)
        
        flow_control_layout.addWidget(flow_control_label)
        flow_control_layout.addWidget(self.flow_control_combo)
        
        middle_settings_layout.addLayout(data_bits_layout)
        middle_settings_layout.addLayout(stop_bits_layout)
        middle_settings_layout.addLayout(parity_layout)
        middle_settings_layout.addLayout(flow_control_layout)
        control_layout.addLayout(middle_settings_layout)
        
        # 第三行设置：流控信号和连接按钮
        bottom_settings_layout = QHBoxLayout()
        bottom_settings_layout.setSpacing(15)
        
        # 流控信号控制
        signal_layout = QHBoxLayout()
        signal_label = QLabel("流控信号:")
        signal_label.setFixedWidth(80)
        self.dtr_check = QCheckBox("DTR")
        self.rts_check = QCheckBox("RTS")
        self.break_check = QCheckBox("Break")
        
        # 连接信号变化
        self.dtr_check.stateChanged.connect(self.on_signal_changed)
        self.rts_check.stateChanged.connect(self.on_signal_changed)
        self.break_check.stateChanged.connect(self.on_signal_changed)
        
        signal_layout.addWidget(signal_label)
        signal_layout.addWidget(self.dtr_check)
        signal_layout.addWidget(self.rts_check)
        signal_layout.addWidget(self.break_check)
        
        # 连接状态和按钮
        connection_layout = QHBoxLayout()
        connection_layout.addStretch()
        
        # 连接状态指示灯
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(16, 16)
        self.status_indicator.setStyleSheet("background-color: #dc3545; border-radius: 8px;")
        connection_layout.addWidget(self.status_indicator)
        connection_layout.addSpacing(5)
        
        self.status_label = QLabel("未连接")
        self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        connection_layout.addWidget(self.status_label)
        connection_layout.addSpacing(10)
        
        self.connect_button = QPushButton("连接")
        self.connect_button.setFixedSize(120, 35)
        self.connect_button.clicked.connect(self.toggle_connection)
        connection_layout.addWidget(self.connect_button)
        
        bottom_settings_layout.addLayout(signal_layout)
        bottom_settings_layout.addLayout(connection_layout)
        
        control_layout.addLayout(bottom_settings_layout)
        main_layout.addWidget(control_group)
        
        # 中间分割器 - 调整比例使接收区域更大
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(5)  # 更细的分割线
        
        # 接收区域 - 优化样式和布局
        receive_group = QGroupBox("接收数据")
        receive_group.setObjectName("receiveGroup")
        receive_layout = QVBoxLayout()
        receive_layout.setSpacing(5)
        receive_group.setLayout(receive_layout)
        
        # 接收控制 - 更紧凑的布局
        receive_control_layout = QHBoxLayout()
        receive_control_layout.setSpacing(15)
        self.receive_hex_check = QCheckBox("十六进制显示")
        self.receive_timestamp_check = QCheckBox("显示时间戳")
        self.auto_scroll_check = QCheckBox("自动滚动")
        self.auto_scroll_check.setChecked(True)
        self.clear_receive_button = QPushButton("清空接收")
        self.clear_receive_button.setFixedWidth(90)
        self.clear_receive_button.clicked.connect(self.clear_receive)
        
        receive_control_layout.addWidget(self.receive_hex_check)
        receive_control_layout.addWidget(self.receive_timestamp_check)
        receive_control_layout.addWidget(self.auto_scroll_check)
        receive_control_layout.addStretch()
        receive_control_layout.addWidget(self.clear_receive_button)
        
        receive_layout.addLayout(receive_control_layout)
        
        # 接收文本框 - 使用更现代的字体和样式
        self.receive_text = QTextEdit()
        self.receive_text.setReadOnly(True)
        self.receive_text.setLineWrapMode(QTextEdit.WidgetWidth)
        font = QFont("Consolas", 12)
        self.receive_text.setFont(font)
        receive_layout.addWidget(self.receive_text)
        
        splitter.addWidget(receive_group)
        
        # 发送区域 - 优化样式和布局
        send_group = QGroupBox("发送数据")
        send_group.setObjectName("sendGroup")
        send_layout = QVBoxLayout()
        send_layout.setSpacing(5)
        send_group.setLayout(send_layout)
        
        # 发送控制 - 更紧凑的布局
        send_control_layout = QHBoxLayout()
        send_control_layout.setSpacing(15)
        self.send_hex_check = QCheckBox("十六进制发送")
        self.append_newline_check = QCheckBox("追加换行")
        self.auto_send_check = QCheckBox("自动发送")
        
        self.auto_send_interval = QSpinBox()
        self.auto_send_interval.setRange(10, 3600000)
        self.auto_send_interval.setValue(1000)
        self.auto_send_interval.setSuffix("ms")
        self.auto_send_interval.setEnabled(False)
        self.auto_send_interval.setFixedWidth(100)
        
        self.auto_send_check.stateChanged.connect(
            lambda: self.auto_send_interval.setEnabled(self.auto_send_check.isChecked())
        )
        
        # 连接自动发送复选框状态变化到定时器控制
        self.auto_send_check.stateChanged.connect(self.toggle_auto_send)
        
        send_control_layout.addWidget(self.send_hex_check)
        send_control_layout.addWidget(self.append_newline_check)
        send_control_layout.addWidget(self.auto_send_check)
        send_control_layout.addWidget(QLabel("间隔:"))
        send_control_layout.addWidget(self.auto_send_interval)
        send_control_layout.addStretch()
        
        send_layout.addLayout(send_control_layout)
        
        # 发送文本框 - 调整高度和样式
        self.send_text = QTextEdit()
        self.send_text.setMaximumHeight(90)  # 略微增加高度
        self.send_text.setFont(font)  # 使用相同的字体设置
        send_layout.addWidget(self.send_text)
        
        # 发送按钮 - 更醒目的样式
        send_button_layout = QHBoxLayout()
        send_button_layout.setSpacing(10)
        self.send_button = QPushButton("发送")
        self.send_button.setMinimumHeight(32)
        self.send_button.clicked.connect(self.send_data)
        self.send_button.setEnabled(False)
        self.send_button.setFixedWidth(100)
        
        self.clear_send_button = QPushButton("清空发送")
        self.clear_send_button.clicked.connect(self.clear_send)
        self.clear_send_button.setFixedWidth(100)
        
        send_button_layout.addWidget(self.send_button)
        send_button_layout.addWidget(self.clear_send_button)
        send_button_layout.addStretch()
        
        send_layout.addLayout(send_button_layout)
        
        splitter.addWidget(send_group)
        
        # 设置分割器比例 - 接收区域更大
        splitter.setSizes([550, 250])
        
        main_layout.addWidget(splitter)
        
        # 自动发送定时器
        self.auto_send_timer = QTimer(self)
        self.auto_send_timer.timeout.connect(self.send_data)
        
        # 设置样式
        self.set_style()
        
        # 应用字体设置
        self.apply_font_settings()
        
    def create_menu(self):
        """创建菜单栏"""
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具")
        
        # 界面设置动作
        ui_settings_action = QAction("界面设置", self)
        ui_settings_action.triggered.connect(self.show_ui_settings)
        tools_menu.addAction(ui_settings_action)
        
        # 数据帧管理动作
        frame_manager_action = QAction("数据帧管理", self)
        frame_manager_action.triggered.connect(self.show_frame_manager)
        tools_menu.addAction(frame_manager_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        # 关于动作
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        

                
    def show_ui_settings(self):
        """显示界面设置对话框"""
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("界面设置")
        dialog.resize(400, 350)
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        
        # 字体设置组
        font_group = QGroupBox("字体设置")
        font_layout = QGridLayout(font_group)
        
        # 字体大小选择
        font_size_label = QLabel("字体大小:")
        font_size_spin = QSpinBox()
        font_size_spin.setRange(8, 24)
        font_size_spin.setValue(self.current_font.pointSize())
        
        # 字体类型选择（固定宽度字体列表）
        font_family_label = QLabel("字体类型:")
        font_family_combo = QComboBox()
        
        # 创建QFontDatabase实例
        font_db = QFontDatabase()
        
        # 获取所有固定宽度字体
        fixed_fonts = []
        for font_family in font_db.families():
            if font_db.isFixedPitch(font_family):
                font_family_combo.addItem(font_family)
        
        # 设置当前字体
        current_font_index = font_family_combo.findText(self.current_font.family())
        if current_font_index >= 0:
            font_family_combo.setCurrentIndex(current_font_index)
        
        # 添加到布局
        font_layout.addWidget(font_size_label, 0, 0)
        font_layout.addWidget(font_size_spin, 0, 1)
        font_layout.addWidget(font_family_label, 1, 0)
        font_layout.addWidget(font_family_combo, 1, 1)
        
        # 添加字体设置组到主布局
        layout.addWidget(font_group)
        
        # 界面缩放设置组
        scale_group = QGroupBox("界面缩放")
        scale_layout = QVBoxLayout(scale_group)
        
        scale_label = QLabel("缩放比例: {:.0f}%".format(self.settings.value("ui_scale", 1.0, type=float) * 100))
        scale_layout.addWidget(scale_label)
        
        # 提示信息
        hint_label = QLabel("提示: 界面缩放设置需要重启程序后生效")
        hint_label.setStyleSheet("color: #666;")
        hint_label.setWordWrap(True)
        scale_layout.addWidget(hint_label)
        
        # 添加缩放设置组到主布局
        layout.addWidget(scale_group)
        
        # 按钮盒
        buttons_layout = QHBoxLayout()
        apply_button = QPushButton("应用")
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        # 连接信号
        # 添加到布局
        font_layout.addWidget(font_size_label, 0, 0)
        font_layout.addWidget(font_size_spin, 0, 1)
        font_layout.addWidget(font_family_label, 1, 0)
        font_layout.addWidget(font_family_combo, 1, 1)
        
        # 添加字体设置组到主布局
        layout.addWidget(font_group)
        
        # 界面缩放设置组
        scale_group = QGroupBox("界面缩放")
        scale_layout = QVBoxLayout(scale_group)
        
        scale_label = QLabel("缩放比例: {:.0f}%".format(self.settings.value("ui_scale", 1.0, type=float) * 100))
        scale_layout.addWidget(scale_label)
        
        # 提示信息
        hint_label = QLabel("提示: 界面缩放设置需要重启程序后生效")
        hint_label.setStyleSheet("color: #666;")
        hint_label.setWordWrap(True)
        scale_layout.addWidget(hint_label)
        
        # 添加缩放设置组到主布局
        layout.addWidget(scale_group)
        
        # 按钮盒
        buttons_layout = QHBoxLayout()
        apply_button = QPushButton("应用")
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        # 连接信号
        def apply_settings():
            # 应用字体设置
            new_font = QFont(font_family_combo.currentText(), font_size_spin.value())
            self.current_font = new_font
            self.apply_font_settings()
            
        def accept_settings():
            apply_settings()
            dialog.accept()
            
        apply_button.clicked.connect(apply_settings)
        ok_button.clicked.connect(accept_settings)
        cancel_button.clicked.connect(dialog.reject)
        
        # 添加按钮到布局
        buttons_layout.addWidget(apply_button)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        
        # 添加按钮盒到主布局
        layout.addLayout(buttons_layout)
        
        # 显示对话框
        dialog.exec_()
        
    def apply_font_settings(self):
        """应用字体设置到所有相关组件，确保字体大小正确更新"""
        # 设置样式表，但不使用字体相关的样式
        self.set_style_no_font()
        
        # 应用字体到所有窗口组件，包括菜单、状态栏等
        self.set_font_recursive(self)
        self.set_font_recursive(self.menuBar())
        self.set_font_recursive(self.statusBar())
        
        # 强制刷新字体设置
        self.receive_text.document().setDefaultFont(self.current_font)
        self.send_text.document().setDefaultFont(self.current_font)
        
        # 立即更新显示
        self.receive_text.update()
        self.send_text.update()
        
        # 强制重绘
        self.receive_text.repaint()
        self.send_text.repaint()
        
        # 保存字体设置
        self.settings.setValue("font_family", self.current_font.family())
        self.settings.setValue("font_size", self.current_font.pointSize())
        self.settings.sync()
        
        # 强制应用样式
        self.style().polish(self.receive_text)
        self.style().polish(self.send_text)
        
    def set_font_recursive(self, widget):
        """递归地为所有子组件设置字体"""
        if widget is None:
            return
        
        # 设置当前组件的字体
        if hasattr(widget, 'setFont'):
            widget.setFont(self.current_font)
        
        # 特殊处理：如果是QTextEdit，还需要设置document的默认字体
        if hasattr(widget, 'document'):
            widget.document().setDefaultFont(self.current_font)
        
        # 特殊处理：如果是QComboBox，还需要设置下拉列表和弹出视图的字体
        if isinstance(widget, QComboBox):
            view = widget.view()
            if view:
                self.set_font_recursive(view)
            # 只设置字体相关的样式
            widget.setStyleSheet(f"QComboBox {{font-family: '{self.current_font.family()}'; font-size: {self.current_font.pointSize()}pt;}}")
        
        # 特殊处理：如果是QTableWidget，设置表头和单元格字体
        if isinstance(widget, QTableWidget):
            header = widget.horizontalHeader()
            if header:
                header.setFont(self.current_font)
            header = widget.verticalHeader()
            if header:
                header.setFont(self.current_font)
            # 设置所有单元格的字体
            for row in range(widget.rowCount()):
                for col in range(widget.columnCount()):
                    item = widget.item(row, col)
                    if item:
                        item.setFont(self.current_font)
        
        # 特殊处理：如果是QLabel，确保应用字体
        if isinstance(widget, QLabel):
            widget.setFont(self.current_font)
        
        # 特殊处理：如果是QPushButton，确保应用字体
        if isinstance(widget, QPushButton):
            widget.setFont(self.current_font)
        
        # 特殊处理：如果是QCheckBox，确保应用字体
        if isinstance(widget, QCheckBox):
            widget.setFont(self.current_font)
        
        # 特殊处理：如果是QSpinBox或QDoubleSpinBox，确保应用字体
        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.setFont(self.current_font)
        
        # 递归设置所有子组件的字体
        for child in widget.children():
            if isinstance(child, QWidget):
                self.set_font_recursive(child)
        
    def set_style_no_font(self):
        """设置界面样式，但不包含字体设置，避免覆盖通过代码设置的字体"""
        # 设置接收区域的样式（不含字体）
        receive_style = """QTextEdit {
            background-color: #ffffff;
            color: #1d1d1f;
            border: 1px solid #d2d2d7;
            border-radius: 6px;
            padding: 8px;
        }
        
        QTextEdit:focus {
            border-color: #007aff;
            border-width: 1px;
            outline: none;
        }
        
        QTextEdit:read-only {
            background-color: #f9f9f9;
        }"""
        self.receive_text.setStyleSheet(receive_style)
        
        # 设置发送区域的样式（不含字体）
        send_style = """QTextEdit {
            background-color: #ffffff;
            border: 1px solid #d2d2d7;
            border-radius: 6px;
            padding: 8px;
        }
        
        QTextEdit:focus {
            border-color: #007aff;
            border-width: 1px;
            outline: none;
        }"""
        self.send_text.setStyleSheet(send_style)
        
    def show_frame_manager(self):
        """显示数据帧管理对话框"""
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("数据帧管理")
        dialog.resize(600, 400)
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        
        # 创建表格
        self.frame_table = QTableWidget(len(self.data_frames), 3)
        self.frame_table.setHorizontalHeaderLabels(["名称", "数据内容", "操作"])
        self.frame_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 填充表格
        for row, frame in enumerate(self.data_frames):
            name_item = QTableWidgetItem(frame["name"])
            data_item = QTableWidgetItem(frame["data"])
            
            # 创建操作按钮
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2)
            
            send_button = QPushButton("发送")
            send_button.setFixedSize(60, 24)
            send_button.clicked.connect(lambda checked, r=row: self.send_saved_frame(r))
            
            delete_button = QPushButton("删除")
            delete_button.setFixedSize(60, 24)
            delete_button.clicked.connect(lambda checked, r=row: self.delete_frame(r))
            
            action_layout.addWidget(send_button)
            action_layout.addWidget(delete_button)
            action_layout.addStretch()
            
            self.frame_table.setItem(row, 0, name_item)
            self.frame_table.setItem(row, 1, data_item)
            self.frame_table.setCellWidget(row, 2, action_widget)
        
        # 添加表格到布局
        layout.addWidget(self.frame_table)
        
        # 底部操作区
        bottom_layout = QHBoxLayout()
        
        # 添加数据帧按钮
        add_frame_button = QPushButton("添加数据帧")
        add_frame_button.clicked.connect(self.add_new_frame)
        
        # 从发送区添加按钮
        add_from_send_button = QPushButton("从发送区添加")
        add_from_send_button.clicked.connect(self.add_frame_from_send)
        
        # 添加按钮到布局
        bottom_layout.addWidget(add_frame_button)
        bottom_layout.addWidget(add_from_send_button)
        bottom_layout.addStretch()
        
        # 添加底部布局到主布局
        layout.addLayout(bottom_layout)
        
        # 显示对话框
        dialog.exec_()
        
    def add_new_frame(self):
        """添加新的数据帧"""
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("添加数据帧")
        dialog.resize(400, 200)
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        
        # 名称输入
        name_label = QLabel("名称:")
        name_input = QTextEdit()
        name_input.setMaximumHeight(40)
        
        # 数据内容输入
        data_label = QLabel("数据内容:")
        data_input = QTextEdit()
        
        # 按钮盒
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        # 连接信号
        def accept_new_frame():
            name = name_input.toPlainText().strip()
            data = data_input.toPlainText().strip()
            
            if name and data:
                self.data_frames.append({"name": name, "data": data})
                self.show_frame_manager()
                dialog.accept()
            else:
                QMessageBox.warning(self, "警告", "名称和数据内容不能为空")
        
        ok_button.clicked.connect(accept_new_frame)
        cancel_button.clicked.connect(dialog.reject)
        
        # 添加到布局
        layout.addWidget(name_label)
        layout.addWidget(name_input)
        layout.addWidget(data_label)
        layout.addWidget(data_input)
        layout.addLayout(buttons_layout)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        
        # 显示对话框
        dialog.exec_()
        
    def add_frame_from_send(self):
        """从发送区添加数据帧"""
        data = self.send_text.toPlainText().strip()
        
        if data:
            # 创建对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("添加数据帧")
            dialog.resize(400, 150)
            
            # 创建布局
            layout = QVBoxLayout(dialog)
            
            # 名称输入
            name_label = QLabel("名称:")
            name_input = QTextEdit()
            name_input.setMaximumHeight(40)
            
            # 按钮盒
            buttons_layout = QHBoxLayout()
            ok_button = QPushButton("确定")
            cancel_button = QPushButton("取消")
            
            # 连接信号
            def accept_new_frame():
                name = name_input.toPlainText().strip()
                
                if name:
                    self.data_frames.append({"name": name, "data": data})
                    self.show_frame_manager()
                    dialog.accept()
                else:
                    QMessageBox.warning(self, "警告", "名称不能为空")
            
            ok_button.clicked.connect(accept_new_frame)
            cancel_button.clicked.connect(dialog.reject)
            
            # 添加到布局
            layout.addWidget(name_label)
            layout.addWidget(name_input)
            layout.addLayout(buttons_layout)
            buttons_layout.addWidget(ok_button)
            buttons_layout.addWidget(cancel_button)
            
            # 显示对话框
            dialog.exec_()
        else:
            QMessageBox.warning(self, "警告", "发送区没有数据")
        
    def send_saved_frame(self, row):
        """发送保存的数据帧"""
        if 0 <= row < len(self.data_frames):
            frame = self.data_frames[row]
            self.send_text.setPlainText(frame["data"])
            self.send_data()
        
    def delete_frame(self, row):
        """删除数据帧"""
        if 0 <= row < len(self.data_frames):
            reply = QMessageBox.question(self, "确认", "确定要删除这个数据帧吗？", 
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                del self.data_frames[row]
                self.show_frame_manager()
        
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", "现代串口调试工具\n版本 1.0\n\n一款功能强大的串口调试工具")
        
    def load_settings(self):
        """加载用户设置"""
        # 加载字体设置
        font_family = self.settings.value("font_family", "")
        font_size = self.settings.value("font_size", 13, type=int)
        
        if font_family:
            self.current_font = QFont(font_family, font_size)
        else:
            self.current_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
            self.current_font.setPointSize(font_size)
        
        # 加载界面缩放设置
        ui_scale = self.settings.value("ui_scale", 1.0, type=float)
        
    def save_settings(self):
        """保存用户设置"""
        # 保存字体设置
        self.settings.setValue("font_family", self.current_font.family())
        self.settings.setValue("font_size", self.current_font.pointSize())
        
        # 保存界面缩放设置
        # ui_scale = ... (获取当前缩放比例)
        # self.settings.setValue("ui_scale", ui_scale)
        
    def on_signal_changed(self):
        """流控信号变化时的处理"""
        if self.serial_port and self.serial_port.is_open:
            try:
                # 设置DTR信号
                self.serial_port.dtr = self.dtr_check.isChecked()
                
                # 设置RTS信号
                self.serial_port.rts = self.rts_check.isChecked()
                
                # 设置Break信号
                self.serial_port.break_condition = self.break_check.isChecked()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"设置信号失败: {str(e)}")
        
    def set_style(self):
        """设置界面样式，使其更符合现代设计风格"""
        # 设置全局样式表
        self.setStyleSheet("""
        /* 全局样式 */
        QMainWindow {
            background-color: #f5f5f7;
            color: #1d1d1f;
        }
        
        /* 状态栏样式 */
        QStatusBar {
            background-color: #ffffff;
            border-top: 1px solid #d2d2d7;
            padding: 4px 8px;
            font-size: 12px;
            color: #6e6e73;
        }
        
        QStatusBar QLabel {
            color: #6e6e73;
            font-size: 12px;
        }
        
        /* 分组框样式 */
        QGroupBox {
            background-color: #ffffff;
            border: 1px solid #e0e0e5;
            border-radius: 8px;
            margin-top: 10px;
            padding: 12px;
            font-weight: 600;
            color: #1d1d1f;
            font-size: 13px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px 0 6px;
            background-color: transparent;
            font-size: 13px;
            color: #1d1d1f;
        }
        
        #controlGroup {
            border: 1px solid #e0e0e5;
            border-radius: 8px;
            background-color: #ffffff;
        }
        
        #receiveGroup, #sendGroup {
            border: 1px solid #e0e0e5;
            border-radius: 8px;
            background-color: #ffffff;
        }
        
        /* 标签样式 */
        QLabel {
            color: #3a3a3c;
            font-size: 13px;
        }
        
        /* 组合框样式 */
        QComboBox {
            background-color: #ffffff;
            border: 1px solid #d2d2d7;
            border-radius: 6px;
            padding: 6px 10px;
            min-width: 80px;
            font-size: 13px;
            color: #1d1d1f;
        }
        
        QComboBox:hover {
            border-color: #1d1d1f;
        }
        
        QComboBox:focus {
            border-color: #007aff;
            border-width: 1px;
            outline: none;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left-width: 1px;
            border-left-color: #d2d2d7;
            border-left-style: solid;
        }
        
        /* 按钮样式 */
        QPushButton {
            background-color: #007aff;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
        }
        
        QPushButton:hover {
            background-color: #0062cc;
        }
        
        QPushButton:pressed {
            background-color: #0052a3;
        }
        
        QPushButton:disabled {
            background-color: #d1d1d6;
            color: #9e9e9e;
        }
        
        /* 文本编辑框样式 */
        QTextEdit {
            background-color: #ffffff;
            border: 1px solid #d2d2d7;
            border-radius: 6px;
            padding: 8px;
            font-family: 'Consolas', 'Courier New', monospace;
            color: #1d1d1f;
        }
        
        QTextEdit:focus {
            border-color: #007aff;
            border-width: 1px;
            outline: none;
        }
        
        QTextEdit:read-only {
            background-color: #f9f9f9;
        }
        
        /* 复选框样式 */
        QCheckBox {
            color: #1d1d1f;
            font-size: 13px;
            spacing: 6px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid #d2d2d7;
            border-radius: 4px;
            background-color: #ffffff;
        }
        
        QCheckBox::indicator:checked {
            background-color: #007aff;
            border-color: #007aff;
            image: url(:/icons/check.png);
        }
        
        /* 微调框样式 */
        QSpinBox {
            background-color: #ffffff;
            border: 1px solid #d2d2d7;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 13px;
            color: #1d1d1f;
        }
        
        QSpinBox:focus {
            border-color: #007aff;
            border-width: 1px;
            outline: none;
        }
        
        /* 分割器样式 */
        QSplitter::handle {
            background-color: #d2d2d7;
        }
        
        QSplitter::handle:hover {
            background-color: #a8a8ad;
        }
        
        /* 滚动条样式 */
        QScrollBar:vertical {
            background-color: #f0f0f0;
            width: 10px;
            margin: 0;
        }
        
        QScrollBar::handle:vertical {
            background-color: #a8a8ad;
            border-radius: 5px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #86868b;
        }
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
            width: 0;
        }
        
        QScrollBar:horizontal {
            background-color: #f0f0f0;
            height: 10px;
            margin: 0;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #a8a8ad;
            border-radius: 5px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #86868b;
        }
        
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            height: 0;
            width: 0;
        }
        """)
        
        # 初始化时设置文本框样式，但不包含字体设置
        self.set_style_no_font()
        
        # 设置连接按钮为更醒目的样式
        self.connect_button.setStyleSheet("""QPushButton {
            background-color: #34c759;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
        }
        
        QPushButton:hover {
            background-color: #29a745;
        }
        
        QPushButton:pressed {
            background-color: #218838;
        }
        
        QPushButton:disabled {
            background-color: #d1d1d6;
            color: #9e9e9e;
        }""")
        
        # 发送按钮特定样式
        self.send_button.setStyleSheet("""QPushButton {
            background-color: #007aff;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
        }
        
        QPushButton:hover {
            background-color: #0062cc;
        }
        
        QPushButton:pressed {
            background-color: #0052a3;
        }
        
        QPushButton:disabled {
            background-color: #d1d1d6;
            color: #9e9e9e;
        }""")
        
        # 刷新按钮样式
        refresh_buttons = self.findChildren(QPushButton, "")
        for btn in refresh_buttons:
            if btn.text() == "刷新端口":
                btn.setStyleSheet("""QPushButton {
                    background-color: #5856d6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: 600;
                }
                
                QPushButton:hover {
                    background-color: #4846cc;
                }
                
                QPushButton:pressed {
                    background-color: #3e3d9e;
                }
                
                QPushButton:disabled {
                    background-color: #d1d1d6;
                    color: #9e9e9e;
                }""")
                break
        
    def refresh_ports(self):
        """刷新串口列表"""
        current_port = self.port_combo.currentText()
        self.port_combo.clear()
        
        # 获取所有可用串口
        ports = serial.tools.list_ports.comports()
        for port in ports:
            port_info = f"{port.device} - {port.description}"
            self.port_combo.addItem(port_info, port.device)
        
        # 如果之前选择的端口仍然存在，则保持选中
        if ports and current_port:
            index = self.port_combo.findText(current_port)
            if index >= 0:
                self.port_combo.setCurrentIndex(index)
        
    def toggle_connection(self):
        """切换串口连接状态"""
        if self.serial_port and self.serial_port.is_open:
            self.close_serial()
        else:
            self.open_serial()
            
    def open_serial(self):
        """打开串口"""
        try:
            if not self.port_combo.currentText():
                QMessageBox.warning(self, "警告", "请选择串口")
                return
            
            # 获取串口参数
            port_name = self.port_combo.currentData()
            baudrate = self.baudrate_combo.currentData()
            data_bits = self.data_bits_combo.currentData()
            stop_bits = self.stop_bits_combo.currentData()
            parity = self.parity_combo.currentData()
            flow_control = self.flow_control_combo.currentData()
            
            # 确定流控制参数
            xonxoff = False
            rtscts = False
            if flow_control == 'X' or flow_control == 'B':
                xonxoff = True
            if flow_control == 'R' or flow_control == 'B':
                rtscts = True
            
            # 简化串口打开逻辑，直接使用serial.Serial
            try:
                self.serial_port = serial.Serial(
                    port=port_name,
                    baudrate=baudrate,
                    bytesize=data_bits,
                    parity=parity,
                    stopbits=stop_bits,
                    timeout=0,
                    xonxoff=xonxoff,
                    rtscts=rtscts
                )
                self.statusBar().showMessage(f"成功打开端口 {port_name}")
            except Exception as e:
                # 提供更详细的错误信息
                raise Exception(f"无法打开串口 {port_name}: {str(e)}")
            
            # 禁用串口设置
            self.port_combo.setEnabled(False)
            self.baudrate_combo.setEnabled(False)
            self.data_bits_combo.setEnabled(False)
            self.stop_bits_combo.setEnabled(False)
            self.parity_combo.setEnabled(False)
            self.connect_button.setText("断开连接")
            self.send_button.setEnabled(True)
            
            # 更新连接状态显示
            self.status_indicator.setStyleSheet("background-color: #28a745; border-radius: 8px;")
            self.status_label.setText("已连接")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            
            # 启动接收线程
            self.receive_thread = SerialThread(self.serial_port)
            self.receive_thread.data_received.connect(self.append_received_data)
            self.receive_thread.connection_closed.connect(self.on_connection_closed)
            self.receive_thread.error_occurred.connect(self.on_serial_error)
            self.receive_thread.start()
            
            # 如果启用了自动发送，启动定时器
            if self.auto_send_check.isChecked():
                self.auto_send_timer.start(self.auto_send_interval.value())
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开串口: {str(e)}")
            # 确保状态显示为未连接
            self.status_indicator.setStyleSheet("background-color: #dc3545; border-radius: 8px;")
            self.status_label.setText("未连接")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            
    def close_serial(self):
        """关闭串口"""
        # 停止自动发送定时器
        self.auto_send_timer.stop()
        
        # 停止接收线程
        if self.receive_thread:
            self.receive_thread.stop()
            self.receive_thread = None
        
        # 关闭串口
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        
        # 启用串口设置
        self.port_combo.setEnabled(True)
        self.baudrate_combo.setEnabled(True)
        self.data_bits_combo.setEnabled(True)
        self.stop_bits_combo.setEnabled(True)
        self.parity_combo.setEnabled(True)
        self.connect_button.setText("连接")
        self.send_button.setEnabled(False)
        
        # 更新连接状态显示
        self.status_indicator.setStyleSheet("background-color: #dc3545; border-radius: 8px;")
        self.status_label.setText("未连接")
        self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        
    def append_received_data(self, data):
        """追加接收的数据到文本框，优化十六进制显示格式"""
        # 更新接收字节计数
        self.received_bytes_count += len(data)
        self.received_bytes_label.setText(f"接收: {self.received_bytes_count} 字节")
        
        # 如果选择了十六进制显示
        if self.receive_hex_check.isChecked():
            # 将字节数据转换为十六进制字符串
            hex_data = []
            for byte in data:
                hex_data.append(f'{ord(byte):02X}')
            
            # 格式化十六进制数据，每行显示16个字节
            formatted_hex = []
            for i in range(0, len(hex_data), 16):
                line_hex = ' '.join(hex_data[i:i+16])
                # 添加ASCII字符表示
                ascii_part = ''.join([c if 32 <= ord(c) <= 126 else '.' for c in data[i:i+16]])
                formatted_hex.append(f"{line_hex:<47}  {ascii_part}")
            
            display_data = '\n'.join(formatted_hex) + '\n'
        else:
            # 确保中文正确显示
            display_data = data
            
        # 如果选择了显示时间戳
        if self.receive_timestamp_check.isChecked():
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            if self.receive_hex_check.isChecked():
                # 为十六进制模式添加时间戳前缀
                lines = display_data.split('\n')
                timestamped_lines = [f"[{timestamp}] {line}" for line in lines]
                display_data = '\n'.join(timestamped_lines)
            else:
                display_data = f"[{timestamp}] {display_data}"
            
        # 追加数据
        self.receive_text.insertPlainText(display_data)
        
        # 如果选择了自动滚动
        if self.auto_scroll_check.isChecked():
            # 使用QTimer确保文本框更新后再滚动到底部
            QTimer.singleShot(0, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """滚动到文本框底部"""
        self.receive_text.verticalScrollBar().setValue(
            self.receive_text.verticalScrollBar().maximum()
        )
            
    def send_data(self):
        """发送数据"""
        if not self.serial_port or not self.serial_port.is_open:
            return
            
        try:
            # 获取发送文本
            text = self.send_text.toPlainText()
            if not text:
                return
                
            # 如果选择了十六进制发送
            if self.send_hex_check.isChecked():
                # 移除所有非十六进制字符
                hex_text = re.sub(r'[^0-9A-Fa-f]', '', text)
                # 检查十六进制字符串长度是否为偶数
                if len(hex_text) % 2 != 0:
                    hex_text += '0'  # 补齐
                # 转换为字节
                data = bytes.fromhex(hex_text)
            else:
                # 普通文本发送
                data = text.encode('utf-8')
                
            # 如果选择了追加换行
            if self.append_newline_check.isChecked():
                data += b'\r\n'
                
            # 发送数据
            bytes_sent = self.serial_port.write(data)
            
            # 更新发送字节计数
            self.sent_bytes_count += bytes_sent
            self.sent_bytes_label.setText(f"发送: {self.sent_bytes_count} 字节")
            
            # 在状态栏显示发送成功信息
            self.statusBar().showMessage(f"成功发送 {bytes_sent} 字节", 2000)
            
        except Exception as e:
            error_msg = f"发送数据失败: {str(e)}"
            QMessageBox.critical(self, "错误", error_msg)
            self.statusBar().showMessage(error_msg, 3000)
            
    def clear_receive(self):
        """清空接收文本框"""
        self.receive_text.clear()
        # 重置接收字节计数
        self.received_bytes_count = 0
        self.received_bytes_label.setText(f"接收: {self.received_bytes_count} 字节")
        
    def clear_send(self):
        """清空发送文本框"""
        self.send_text.clear()
        # 重置发送字节计数
        self.sent_bytes_count = 0
        self.sent_bytes_label.setText(f"发送: {self.sent_bytes_count} 字节")
        
    def toggle_auto_send(self):
        """切换自动发送功能的状态"""
        if self.auto_send_check.isChecked():
            # 获取自动发送间隔
            interval = self.auto_send_interval.value()
            # 启动定时器
            self.auto_send_timer.start(interval)
            # 在状态栏显示自动发送已启动
            self.statusBar().showMessage(f"自动发送已启动，间隔: {interval}ms", 2000)
        else:
            # 停止定时器
            self.auto_send_timer.stop()
            # 在状态栏显示自动发送已停止
            self.statusBar().showMessage("自动发送已停止", 2000)
        
    def on_connection_closed(self):
        """连接关闭时的处理"""
        self.close_serial()
        # 避免在程序关闭时弹出警告
        if self.isVisible():
            QMessageBox.warning(self, "警告", "串口连接已关闭")
        
    def on_serial_error(self, error_msg):
        """串口错误处理"""
        QMessageBox.critical(self, "错误", f"串口错误: {error_msg}")
        
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.close_serial()
        self.save_settings()  # 保存用户设置
        event.accept()

if __name__ == "__main__":
    try:
        # 尝试导入必要的模块
        app = QApplication(sys.argv)
        window = SerialMonitor()
        window.show()
        sys.exit(app.exec_())
    except ImportError as e:
        print(f"导入模块失败: {str(e)}")
        print("请确保已安装必要的依赖包:")
        print("pip install PyQt5 pyserial")
        input("按回车键退出...")
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        input("按回车键退出...")