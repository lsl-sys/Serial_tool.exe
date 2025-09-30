@echo off

REM 设置中文编码
chcp 65001 >nul

REM 显示当前目录和EXE文件信息
echo 当前工作目录: %cd%
echo 检查EXE文件是否存在...

if exist "dist\main.exe" (
    echo 发现可执行文件: dist\main.exe
    echo 文件大小: %~z1 KB
) else (
    echo 错误: 未找到可执行文件 dist\main.exe
    echo 请先运行 build_final.bat 生成可执行文件
    pause
    exit /b 1
)

REM 运行生成的可执行文件
echo.
echo 正在启动串口调试工具...
echo 若程序未正常启动，请检查是否已安装串口驱动
start dist\main.exe

if %errorlevel% neq 0 (
    echo 错误: 启动程序失败，错误代码: %errorlevel%
    echo 可能的解决方法:
    echo 1. 确保您的电脑已安装必要的串口驱动
    echo 2. 尝试以管理员身份运行此批处理文件
    echo 3. 检查防火墙或安全软件是否阻止了程序运行
    pause
    exit /b %errorlevel%
)

REM 启动成功提示
echo 程序已成功启动！
echo 您可以在任务栏找到串口调试工具的图标
pause