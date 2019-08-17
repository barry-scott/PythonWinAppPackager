setlocal
if "%1" == "" (
    colour-print "<>em Usage: %0 <version><>"
    colour-print "<>em        %0 3.7-64<>"
    goto :eof
)

set PY_VER=%1

for %%i in (dist\*.whl) do set WHEEL=%%~fi
set PYTHONPATH=
cd %USERPROFILE%

colour-print "<>info Info:<> For Python <>em %%s<> installing <>em %%s<>" "%PY_VER%" "%WHEEL%"
py -%PY_VER% -m pip install --user --upgrade %WHEEL%

endlocal
