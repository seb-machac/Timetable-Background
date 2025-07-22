# Timetable-Background

## Extensions needed
Install all libraries from requirements.txt by running:

**pip install -r requirements.txt**

## File setup
Change Username Password and ID number:

#### Example:
  
<img width="704" height="91" alt="Screenshot 2025-07-22 102108" src="https://github.com/user-attachments/assets/62ecee7e-b5b7-4408-8f0b-d897325b15d0" />
pmsc.xuno.com.au/index.php/timetable/**42**/2025-07-04
id_num = 42

## Setting Up .BAT file for Automation/Task Scheduler.
#### Change the file paths
"File Path to your python.exe file" "File to the XUNO_API_V3.py"

#### Example:

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
