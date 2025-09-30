@echo off

REM 设置中文编码
chcp 65001 >nul

echo 正在启动环境检查和串口调试工具...
python check_env_and_run.py

pause