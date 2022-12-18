setlocal
set PY_VER=%1
if "%PY_VER%" == "" (
    py -3 -m colour_text "<>error Error: Usage %0 <python-version><>"
    goto :eof
)

py -3 -m colour_text "<>info Info:<> Install last built kit for Python %%s" "%PY_VER%"
if exist tests cd tests
cd ..
call localinstall.cmd %PY_VER%
    if errorlevel 1 goto :eof

rem needed for the GUI test and TZ test
py -%PY_VER% -m pip install --user --upgrade PyQt5 PyQt6 tzdata tzlocal

cd tests

rem CLI
py -3 -m colour_text "<>info Info:<> Build CLI test for Python %%s" "%PY_VER%"
if exist pkg-cli rmdir /s /q pkg-cli
mkdir pkg-cli
py -%PY_VER% -m win_app_packager build cli_test.py pkg-cli --cli --version 1.1
    if errorlevel 1 goto :eof

py -3 -m colour_text "<>info Info:<> Run CLI test for Python %%s" "%PY_VER%"
call pkg-cli\cli_test
   if errorlevel 1 goto :eof

rem CLI TZ
py -3 -m colour_text "<>info Info:<> Build CLI TZ test for Python %%s" "%PY_VER%"
if exist pkg-cli-tz rmdir /s /q pkg-cli-tz
mkdir pkg-cli-tz
py -%PY_VER% -m win_app_packager build cli_tz_test.py pkg-cli-tz --cli --version 1.1
    if errorlevel 1 goto :eof

py -3 -m colour_text "<>info Info:<> Run CLI TZ test for Python %%s" "%PY_VER%"
call pkg-cli-tz\cli_tz_test
    if errorlevel 1 goto :eof

rem GUI PyQt5
py -3 -m colour_text "<>info Info:<> Build GUI PyQt5 test for Python %%s" "%PY_VER%"
if exist pkg-gui-pyqt5 rmdir /s /q pkg-gui-pyqt5
mkdir pkg-gui-pyqt5
py -%PY_VER% -m win_app_packager build gui_pyqt5_test.py pkg-gui-pyqt5 --gui --version 2.3.8
    if errorlevel 1 goto :eof

py -3 -m colour_text "<>info Info:<> Run GUI PyQt5 test for Python %%s" "%PY_VER%"
call pkg-gui-pyqt5\gui_pyqt5_test
    if errorlevel 1 goto :eof

rem GUI PyQt6
py -3 -m colour_text "<>info Info:<> Build GUI PyQt6 test for Python %%s" "%PY_VER%"
if exist pkg-gui-pyqt6 rmdir /s /q pkg-gui-pyqt6
mkdir pkg-gui-pyqt6
py -%PY_VER% -m win_app_packager build gui_pyqt6_test.py pkg-gui-pyqt6 --gui --version 2.3.8
    if errorlevel 1 goto :eof

py -3 -m colour_text "<>info Info:<> Run GUI PyQt6 test for Python %%s" "%PY_VER%"
call pkg-gui-pyqt6\gui_pyqt6_test
    if errorlevel 1 goto :eof

endlocal
