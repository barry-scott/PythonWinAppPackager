setlocal
set PY_VER=3.7
if X%1 == X (
    echo provide password as quoted %%1 arg
    goto :eof
)

set HOME=%USERPROFILE%
py -%PY_VER% -m twine check uploads\*
    if errorlevel 1 goto :eof
py -%PY_VER% -m twine upload -p %1 uploads\*
endlocal
