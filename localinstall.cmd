setlocal
if "%1" == "" (
    echo "Usage: %0 <version>"
    echo "       %0 3.6-32"
    goto :eof
)

set PY_VER=%1

for %%i in (dist\*.whl) do set WHEEL=%%~fi
set PYTHONPATH=
cd %userprofile%
py -%PY_VER% -m pip install --user --upgrade %WHEEL%

endlocal
