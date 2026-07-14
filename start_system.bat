@echo off

echo Starting Smart Execution Platform...

start cmd /k "wsl redis-server"

start cmd /k "cd /d D:\python\机器学习-0\.vscode\execution-simulator\engineex\ecution_engine.py"

start cmd /k "cd /d D:\python\机器学习-0\.vscode\execution-simulator\engineex\dashboard/app.py"
