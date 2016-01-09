setlocal
if "%1" == "32" (
    set PY_VER=3.5-32
) else (
    set PY_VER=3.5
)


py -%PY_VER% -m twine upload dist\*
endlocal
