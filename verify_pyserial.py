import sys

# 验证pyserial包是否正常工作
try:
    import serial
    print(f"导入的serial包路径: {serial.__file__}")
    print(f"serial包版本: {getattr(serial, '__version__', '未知')}")
    print(f"serial包中可用的属性: {[attr for attr in dir(serial) if not attr.startswith('_')]}")
    
    # 检查Serial类是否存在
    print("\n检查Serial类是否存在...")
    if hasattr(serial, 'Serial'):
        print("✓ serial.Serial存在")
        # 尝试创建一个简单的Serial对象（不实际打开端口）
        try:
            test_serial = serial.Serial()
            print("✓ 成功创建Serial对象")
        except Exception as e:
            print(f"✗ 创建Serial对象失败: {e}")
    else:
        print("✗ serial.Serial不存在")
    
    # 检查serial.tools.list_ports是否正常工作
    print("\n检查serial.tools.list_ports是否正常工作...")
    try:
        from serial.tools import list_ports
        print(f"serial.tools.list_ports模块路径: {list_ports.__file__}")
        
        # 获取可用端口列表
        ports = list_ports.comports()
        print(f"找到{len(ports)}个可用串口:")
        for port in ports:
            print(f"  - {port.device}: {port.description} ({port.hwid})")
            
    except Exception as e:
        print(f"✗ serial.tools.list_ports模块错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n===== 验证完成 =====")
    print("现在应该可以正常使用串口功能了！")
except Exception as e:
    print(f"验证过程中发生错误: {e}")
    import traceback
    traceback.print_exc()

input("按回车键退出...")