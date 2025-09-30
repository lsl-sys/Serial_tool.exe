import sys

# 检查导入的是哪个serial包
try:
    import serial
    print(f"导入的serial包路径: {serial.__file__}")
    print(f"serial包版本: {getattr(serial, '__version__', '未知')}")
    print(f"serial包中可用的属性: {[attr for attr in dir(serial) if not attr.startswith('_')]}")
    
    # 检查serial.tools是否存在
    print("\n检查serial.tools模块...")
    try:
        import serial.tools
        print(f"serial.tools路径: {serial.tools.__file__}")
        # 检查serial.tools.list_ports
        print("\n检查serial.tools.list_ports模块...")
        try:
            import serial.tools.list_ports
            print(f"serial.tools.list_ports路径: {serial.tools.list_ports.__file__}")
            print("✓ 成功导入serial.tools.list_ports")
        except Exception as e:
            print(f"✗ 无法导入serial.tools.list_ports: {e}")
    except Exception as e:
        print(f"✗ 无法导入serial.tools: {e}")
        
    # 检查pyserial是否被正确安装
    print("\n检查pyserial包是否存在...")
    try:
        # 尝试直接检查pyserial是否在已安装包中
        import pkg_resources
        pyserial_dist = pkg_resources.get_distribution('pyserial')
        print(f"pyserial包版本: {pyserial_dist.version}")
        print(f"pyserial包位置: {pyserial_dist.location}")
    except pkg_resources.DistributionNotFound:
        print("✗ 未找到pyserial包")
    except Exception as e:
        print(f"检查pyserial包时出错: {e}")
    
    # 检查是否有其他可能的导入方式
    print("\n尝试其他导入方式...")
    try:
        import pyserial
        print(f"✓ 成功导入pyserial包: {pyserial.__file__}")
        try:
            from pyserial import Serial
            print("✓ 成功从pyserial导入Serial")
        except Exception as e:
            print(f"✗ 无法从pyserial导入Serial: {e}")
    except ImportError:
        print("✗ 无法导入pyserial包")
    
    # 尝试不同的Serial导入路径
    print("\n尝试从serial.serialwin32导入Serial...")
    try:
        from serial.serialwin32 import Serial
        print("✓ 成功从serial.serialwin32导入Serial")
    except ImportError as e:
        print(f"✗ 无法从serial.serialwin32导入Serial: {e}")
    
    print("\n===== 测试完成 =====")
except Exception as e:
    print(f"测试过程中发生错误: {e}")
    import traceback
    traceback.print_exc()

input("按回车键退出...")