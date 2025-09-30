#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import subprocess
import os

"""检查环境并运行串口调试工具的脚本"""


def run_command(command):
    """运行命令并返回输出和错误"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1


def check_python():
    """检查Python环境"""
    print("=== 检查Python环境 ===")
    stdout, stderr, code = run_command("python --version")
    if code != 0:
        print(f"❌ Python未安装或未添加到系统PATH")
        print(f"错误信息: {stderr}")
        print("请先安装Python并确保添加到系统环境变量PATH中")
        return False
    print(f"✅ Python版本: {stdout.strip()}")
    return True


def check_dependencies():
    """检查必要的依赖包"""
    print("\n=== 检查依赖包 ===")
    dependencies = ["PyQt5", "pyserial"]
    missing = []
    
    for dep in dependencies:
        stdout, stderr, code = run_command(f"python -c 'import {dep.lower()}'")
        if code != 0:
            missing.append(dep)
            print(f"❌ 未安装: {dep}")
        else:
            print(f"✅ 已安装: {dep}")
    
    if missing:
        print(f"\n需要安装缺失的依赖包: {' '.join(missing)}")
        return False
    return True


def install_dependencies():
    """安装必要的依赖包"""
    print("\n=== 安装依赖包 ===")
    result = subprocess.run(
        "pip install PyQt5 pyserial",
        shell=True,
        check=False
    )
    if result.returncode != 0:
        print("❌ 依赖包安装失败")
        return False
    print("✅ 依赖包安装成功")
    return True


def run_serial_tool():
    """运行串口调试工具"""
    print("\n=== 启动串口调试工具 ===")
    try:
        # 直接运行Python脚本
        subprocess.Popen(
            [sys.executable, "main.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print("✅ 串口调试工具已启动！")
        print("\n如果您希望将程序打包成可执行文件，请运行build.bat")
        return True
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("欢迎使用单片机串口调试工具环境检查器\n")
    
    # 检查Python环境
    if not check_python():
        print("\n请安装Python后重试。")
        input("按回车键退出...")
        return
    
    # 检查依赖
    if not check_dependencies():
        # 询问是否安装依赖
        choice = input("\n是否安装缺失的依赖包？(y/n): ").lower()
        if choice == 'y':
            if not install_dependencies():
                print("\n依赖包安装失败，请手动安装。")
                print("手动安装命令: pip install PyQt5 pyserial")
                input("按回车键退出...")
                return
        else:
            print("\n请手动安装依赖包后重试。")
            print("手动安装命令: pip install PyQt5 pyserial")
            input("按回车键退出...")
            return
    
    # 运行工具
    if not run_serial_tool():
        print("\n程序启动失败，请检查错误信息。")
        input("按回车键退出...")
        return
    
    print("\n环境检查完成！")
    input("按回车键退出...")


if __name__ == "__main__":
    main()