#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import importlib
import os

# 检查Python路径
sys_paths = sys.path
print(f"Python解释器路径: {sys.executable}")
print(f"Python版本: {sys.version}")
print("\nPython路径列表:")
for path in sys_paths:
    print(f" - {path}")

# 检查serial包
print("\n=== 检查serial包 ===")
try:
    # 尝试卸载可能存在的serial包
    try:
        import serial
        print(f"当前导入的serial包路径: {serial.__file__}")
        print(f"serial包版本: {getattr(serial, '__version__', '未知')}")
        print(f"serial包属性: {[attr for attr in dir(serial) if not attr.startswith('_')]}")
        
        # 检查Serial类是否存在
        if hasattr(serial, 'Serial'):
            print("✓ serial.Serial存在")
        else:
            print("✗ serial.Serial不存在")
            
        # 检查是否有其他可能的serial模块
        importlib.reload(serial)
    except ImportError:
        print("没有找到serial包")
        
    # 检查是否有其他可能冲突的模块
    conflicting_modules = []
    for path in sys_paths:
        if os.path.exists(os.path.join(path, 'serial.py')):
            conflicting_modules.append(os.path.join(path, 'serial.py'))
        if os.path.exists(os.path.join(path, 'serial')):
            conflicting_modules.append(os.path.join(path, 'serial'))
            
    if conflicting_modules:
        print("\n发现可能冲突的serial模块路径:")
        for mod in conflicting_modules:
            print(f" - {mod}")
    else:
        print("\n没有发现冲突的serial模块")
        
    # 测试直接从pyserial导入
    print("\n=== 测试从pyserial导入 ===")
    try:
        import pyserial
        print(f"pyserial包路径: {pyserial.__file__}")
        print(f"pyserial版本: {getattr(pyserial, '__version__', '未知')}")
    except ImportError:
        print("没有找到pyserial包")
        
    # 尝试直接导入Serial类
    print("\n=== 尝试直接导入Serial类 ===")
    try:
        from serial import Serial
        print("✓ 成功从serial导入Serial类")
        test_serial = Serial()
        print("✓ 成功创建Serial对象")
    except Exception as e:
        print(f"✗ 从serial导入Serial失败: {e}")
        
    # 检查serial.tools.list_ports
    print("\n=== 检查serial.tools.list_ports ===")
    try:
        from serial.tools import list_ports
        print(f"serial.tools.list_ports模块路径: {list_ports.__file__}")
        ports = list_ports.comports()
        print(f"找到{len(ports)}个可用串口")
    except Exception as e:
        print(f"✗ serial.tools.list_ports模块错误: {e}")
        
    print("\n=== 建议解决方案 ===")
    print("1. 如果存在多个serial包，请卸载冲突的包")
    print("2. 尝试重新安装pyserial: pip install --upgrade pyserial")
    print("3. 确保没有与serial同名的文件或文件夹在当前目录")
    
except Exception as e:
    print(f"测试过程中发生错误: {e}")
    import traceback
    traceback.print_exc()

input("按回车键退出...")