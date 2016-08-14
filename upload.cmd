setlocal
if "%1" == "32" (
    set PY_VER=3.5-32
) else (
    set PY_VER=3.5
)

if "%2" == "" (
    echo provide password as quoted %%2 arg
    goto :eof
)

set HOME=%USERPROFILE%
py -%PY_VER% -m twine upload -p %2 dist\*
endlocal
