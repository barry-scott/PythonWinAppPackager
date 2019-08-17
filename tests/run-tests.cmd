setlocal
set PY_VER=%1
colour-print "<>info Info:<> Install last built kit for Python %%s" "%PY_VER%"
cd tests
cd ..
call localinstall.cmd %PY_VER%
    if errorlevel 1 goto :eof

rem needed for the GUI test
py -%PY_VER% -m pip install --user --upgrade PyQt5

cd tests

colour-print "<>info Info:<> Build CLI test for Python %%s" "%PY_VER%"
if exist pkg-cli rmdir /s /q pkg-cli
mkdir pkg-cli
py -%PY_VER% -m win_app_packager build cli_test.py pkg-cli -cli --version 1.1
    if errorlevel 1 goto :eof

call pkg-cli\cli_test
    if errorlevel 1 goto :eof

colour-print "<>info Info:<> Build GUI test for Python %%s" "%PY_VER%"
if exist pkg-gui rmdir /s /q pkg-gui
mkdir pkg-gui
py -%PY_VER% -m win_app_packager build gui_test.py pkg-gui -gui --version 2.3.8
    if errorlevel 1 goto :eof

call pkg-gui\gui_test
    if errorlevel 1 goto :eof

endlocal
