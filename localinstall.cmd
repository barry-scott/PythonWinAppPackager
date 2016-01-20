setlocal
if "%1" == "32" (
    set PY_VER=3.5-32
) else if "%1" == "64" (
    set PY_VER=3.5
) else (
    echo Error: %%1 must be 32 or 64
    goto :eof
)

for %%i in (dist\*.whl) do set WHEEL=%%~fi
cd %userprofile%
py -%PY_VER% -m pip install -U %WHEEL%

endlocal
