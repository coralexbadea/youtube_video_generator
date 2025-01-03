@echo off
REM Open Chrome with Profile 5
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --profile-directory="Profile 5"
IF ERRORLEVEL 1 echo "Failed to start Chrome" >> C:\Users\user\Desktop\bat_error.log

REM Run the Python script
"C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe" C:\Users\user\Desktop\ProramFiles\create_video\create_video.py
IF ERRORLEVEL 1 echo "Failed to run Python script" >> C:\Users\user\Desktop\bat_error.log

REM Prevent window from closing
pause
