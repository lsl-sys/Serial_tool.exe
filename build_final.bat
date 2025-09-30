@echo off

REM 设置中文编码
chcp 65001 >nul

REM 显示当前目录和Python版本信息
echo 当前工作目录: %cd%
echo Python版本:
python --version
if %errorlevel% neq 0 (
    echo 无法找到Python，请确保已安装Python并添加到系统PATH
    pause
    exit /b %errorlevel%
)

echo.
echo 正在安装依赖包...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo 依赖包安装失败，请检查网络连接或Python环境
    echo 您可以尝试使用以下命令手动安装：
    echo pip install PyQt5 pyserial pyinstaller
    pause
    exit /b %errorlevel%
)

echo.
echo 依赖包安装成功，正在安装PyInstaller...
pip install pyinstaller

if %errorlevel% neq 0 (
    echo PyInstaller安装失败
    echo 您可以尝试使用以下命令手动安装：
    echo pip install pyinstaller
    pause
    exit /b %errorlevel%
)

echo.
echo 开始打包程序...
echo 注意：此命令会确保包含serial.tools.list_ports模块
echo 打包命令: python -m PyInstaller --onefile --windowed --hidden-import=serial.tools.list_ports --hidden-import=serial main.py
python -m PyInstaller --onefile --windowed --hidden-import=serial.tools.list_ports --hidden-import=serial main.py

if %errorlevel% neq 0 (
    echo 程序打包失败
    echo 您可以尝试手动运行命令：
    echo python -m PyInstaller --onefile --windowed --hidden-import=serial.tools.list_ports --hidden-import=serial main.py
    echo 或者
    echo 直接运行Python脚本：python main.py
    pause
    exit /b %errorlevel%
)

echo.
echo 程序打包成功！可执行文件位于 dist\main.exe

echo.
echo 按任意键打开dist目录查看可执行文件...
pause >nul
start explorer dist

REM 提供一个简单的批处理文件来运行程序
echo @echo off > run_serial_tool_exe.bat
echo chcp 65001 ^>nul >> run_serial_tool_exe.bat
echo echo 当前工作目录: %%cd%% >> run_serial_tool_exe.bat
echo echo 检查EXE文件是否存在... >> run_serial_tool_exe.bat
echo. >> run_serial_tool_exe.bat
echo if exist "dist\main.exe" ( >> run_serial_tool_exe.bat
echo     echo 发现可执行文件: dist\main.exe >> run_serial_tool_exe.bat
echo     echo 文件大小: %%~z1 KB >> run_serial_tool_exe.bat
echo ) else ( >> run_serial_tool_exe.bat
echo     echo 错误: 未找到可执行文件 dist\main.exe >> run_serial_tool_exe.bat
echo     echo 请先运行 build_final.bat 生成可执行文件 >> run_serial_tool_exe.bat
echo     pause >> run_serial_tool_exe.bat
echo     exit /b 1 >> run_serial_tool_exe.bat
echo ) >> run_serial_tool_exe.bat
echo. >> run_serial_tool_exe.bat
echo echo 正在启动串口调试工具... >> run_serial_tool_exe.bat
echo echo 若程序未正常启动，请检查是否已安装串口驱动 >> run_serial_tool_exe.bat
echo start dist\main.exe >> run_serial_tool_exe.bat
echo. >> run_serial_tool_exe.bat
echo if %%errorlevel%% neq 0 ( >> run_serial_tool_exe.bat
echo     echo 错误: 启动程序失败，错误代码: %%errorlevel%% >> run_serial_tool_exe.bat
echo     echo 可能的解决方法: >> run_serial_tool_exe.bat
echo     echo 1. 确保您的电脑已安装必要的串口驱动 >> run_serial_tool_exe.bat
echo     echo 2. 尝试以管理员身份运行此批处理文件 >> run_serial_tool_exe.bat
echo     echo 3. 检查防火墙或安全软件是否阻止了程序运行 >> run_serial_tool_exe.bat
echo     pause >> run_serial_tool_exe.bat
echo     exit /b %%errorlevel%% >> run_serial_tool_exe.bat
echo ) >> run_serial_tool_exe.bat
echo. >> run_serial_tool_exe.bat
echo echo 程序已成功启动！ >> run_serial_tool_exe.bat
echo echo 您可以在任务栏找到串口调试工具的图标 >> run_serial_tool_exe.bat
echo pause >> run_serial_tool_exe.bat
echo 已更新run_serial_tool_exe.bat文件，双击即可运行程序而不需要打包

pause