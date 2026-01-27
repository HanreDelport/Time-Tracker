@echo off
echo Building Time Tracker executable...
echo.

pyinstaller --name="TimeTracker" ^
    --windowed ^
    --onefile ^
    --icon=icon.ico ^
    --add-data="ui;ui" ^
    --add-data="icon.ico;." ^
    main.py

echo.
echo Build complete! Check the 'dist' folder for TimeTracker.exe
pause