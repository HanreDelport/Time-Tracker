@echo off
echo Building Time Tracker executable...
echo.

pyinstaller --name="TimeTracker" ^
    --windowed ^
    --onefile ^
    --icon=assets/stopwatch.ico ^
    --add-data="ui;ui" ^
    --add-data="assets/stopwatch.ico;assets" ^
    main.py

echo.
echo Build complete! Check the 'dist' folder for TimeTracker.exe
pause