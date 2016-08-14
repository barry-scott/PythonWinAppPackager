setlocal
set PY_VER=3.5
if %1 == "" (
    echo provide password as quoted %%1 arg
    goto :eof
)

set HOME=%USERPROFILE%
py -%PY_VER% -m twine upload -p %1 dist\*
endlocal
