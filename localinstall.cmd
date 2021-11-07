setlocal
if "%1" == "" (
    colour-print "<>em Usage: %0 <version><>"
    colour-print "<>em        %0 3.7-64<>"
    goto :eof
)

set PY_VER=%1

for /F "delims=- tokens=1,2" %%a in ("%PY_VER%") do set MAJ_MIN=%%a&set ARCH=%%b
for /F "delims=. tokens=1,2" %%a in ("%MAJ_MIN%") do set MAJ=%%a&set MIN=%%b

for %%i in (uploads\*-cp%MAJ%%MIN%-*.whl) do set WHEEL=%%~fi
set PYTHONPATH=
cd %USERPROFILE%

colour-print "<>info Info:<> For Python <>em %%s<> installing <>em %%s<>" "%PY_VER%" "%WHEEL%"
py -%PY_VER% -m pip uninstall --yes win-app-packager
py -%PY_VER% -m pip install --user --upgrade %WHEEL%

endlocal
