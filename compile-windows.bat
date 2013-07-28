@echo off
cd /d %~dp0
echo This script will compile Nimbus. Before you continue, make sure that:
echo 1) Python 3 is installed to C:\Python33.
echo 2) PyQt4 is installed.
echo 3) cx_Freeze is installed.
PAUSE
C:\Python33\Scripts\cxfreeze.bat "nimbus.py" --target-dir="." --base-name="Win32GUI" && C:\Python33\python.exe "do-finish-compile-windows.py" && echo Compilation successful. && PAUSE
