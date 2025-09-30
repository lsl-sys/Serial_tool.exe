import sys
import serial
import os

print("===== Python 版本信息 =====")
print(f"Python 版本: {sys.version}")
print(f"Python 安装路径: {sys.executable}")

print("\n===== serial 模块信息 =====")
print(f"serial 模块路径: {serial.__file__}")
print(f"serial 模块版本: {getattr(serial, '__version__', '未知')}")

print("\n===== serial 模块属性检查 =====")
print(f"是否有Serial属性: {'Serial' in dir(serial)}")
print(f"是否有serialutil模块: {'serialutil' in dir(serial)}")
print(f"是否有serialwin32模块: {'serialwin32' in dir(serial)}")

# 尝试不同的导入方式
print("\n===== 尝试不同的Serial类导入方式 =====")

# 方式1: 直接从serial导入Serial
print("\n方式1: 尝试直接从serial导入Serial")
try:
    from serial import Serial as Serial1
    print("✓ 成功: 从serial导入Serial")
except ImportError as e:
    print(f"✗ 失败: {e}")

# 方式2: 从serial.serialutil导入SerialBase
print("\n方式2: 尝试从serial.serialutil导入SerialBase")
try:
    from serial.serialutil import SerialBase as Serial2
    print("✓ 成功: 从serial.serialutil导入SerialBase")
except ImportError as e:
    print(f"✗ 失败: {e}")

# 方式3: 从serial.serialwin32导入Serial
print("\n方式3: 尝试从serial.serialwin32导入Serial")
try:
    from serial.serialwin32 import Serial as Serial3
    print("✓ 成功: 从serial.serialwin32导入Serial")
except ImportError as e:
    print(f"✗ 失败: {e}")

# 方式4: 使用serial.Serial (如果存在)
print("\n方式4: 尝试直接使用serial.Serial")
try:
    if hasattr(serial, 'Serial'):
        test_serial = serial.Serial(timeout=0.1)
        print("✓ 成功: 可以创建serial.Serial对象")
        test_serial.close()
    else:
        print("✗ 失败: serial模块没有Serial属性")
except Exception as e:
    print(f"✗ 失败: {e}")

# 检查可用的串口
print("\n===== 可用串口列表 =====")
try:
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    if ports:
        for port in ports:
            print(f"端口: {port.device}, 描述: {port.description}, 硬件ID: {port.hwid}")
    else:
        print("未找到可用的串口")
except Exception as e:
    print(f"获取串口列表失败: {e}")

# 检查COM5端口是否存在
print("\n===== 检查COM5端口 =====")
found_com5 = False
try:
    for port in ports:
        if port.device == 'COM5':
            found_com5 = True
            print(f"✓ 找到COM5端口: {port.description}")
            break
    if not found_com5:
        print("✗ 未找到COM5端口")
except Exception as e:
    print(f"检查COM5端口失败: {e}")

# 测试打开COM5端口
if found_com5:
    print("\n===== 尝试打开COM5端口 =====")
    # 尝试所有可用的Serial类导入方式
    for i, serial_class in enumerate([Serial1, Serial2, Serial3] if 'Serial1' in locals() else [], 1):
        if serial_class is not None:
            print(f"\n使用方式{i}尝试打开COM5:")
            try:
                ser = serial_class('COM5', baudrate=115200, timeout=0.1)
                print("✓ 成功打开COM5端口")
                ser.close()
                print(f"推荐使用方式{i}的导入方式")
                break
            except Exception as e:
                print(f"✗ 无法打开COM5: {e}")

print("\n===== 测试完成 =====")
input("按回车键退出...")