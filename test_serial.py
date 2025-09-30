import serial
import sys

print(f"Python版本: {sys.version}")
print(f"serial模块路径: {serial.__file__}")
print(f"serial模块属性: {dir(serial)}")

try:
    # 检查serial.Serial是否存在
    if hasattr(serial, 'Serial'):
        print("serial.Serial存在")
        # 尝试创建一个简单的Serial对象（不实际打开端口）
        test_serial = serial.Serial()
        print("成功创建Serial对象")
    else:
        print("错误: serial模块没有Serial属性")
        
    # 检查是否有其他可能的导入方式
    try:
        from serial.serialutil import SerialBase
        print("找到serial.serialutil.SerialBase")
    except ImportError:
        print("未找到serial.serialutil.SerialBase")
        
    try:
        from serial.serialwin32 import Serial
        print("找到serial.serialwin32.Serial")
    except ImportError:
        print("未找到serial.serialwin32.Serial")
        
except Exception as e:
    print(f"发生异常: {e}")
    
print("\n按回车键退出...")
input()