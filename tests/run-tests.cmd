setlocal
echo Info: Install last build kit

cd tests
cd ..
call localinstall.cmd %1 %2
    if errorlevel 1 goto :eof

rem needed for the GUI test
py -%1-%2 -m pip install --upgrade PyQt5

cd tests

if exist pkg-cli rmdir /s /q pkg-cli
mkdir pkg-cli
py -%1-%2 -m win_app_packager build cli_test.py pkg-cli -cli --version 1.1
    if errorlevel 1 goto :eof

call pkg-cli\cli_test
    if errorlevel 1 goto :eof

if exist pkg-gui rmdir /s /q pkg-gui
mkdir pkg-gui
py -%1-%2 -m win_app_packager build gui_test.py pkg-gui -gui --version 2.3.8
    if errorlevel 1 goto :eof

call pkg-gui\gui_test
    if errorlevel 1 goto :eof

endlocal
