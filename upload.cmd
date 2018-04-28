setlocal
set PY_VER=3.6
if X%1 == X (
    echo provide password as quoted %%1 arg
    goto :eof
)

set HOME=%USERPROFILE%
py -%PY_VER% -m twine upload -p %1 dist\*
endlocal
