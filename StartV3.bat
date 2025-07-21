@echo off
:: Check if already minimized
if not defined IS_MINIMIZED (
    set IS_MINIMIZED=1
    start "" /min "%~f0"
    exit /b
)

"C:\Users\lenna\AppData\Local\Programs\Python\Python311\python.exe" "D:\V2_XUNO\xuniapi_v3.py"

:: Force Windows to refresh the desktop wallpaper
RUNDLL32.EXE USER32.DLL,UpdatePerUserSystemParameters 1, True

exit
