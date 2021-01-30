setlocal
set PY_VER=3.9
if X%1 == X (
    echo provide password as quoted %%1 arg
    goto :eof
)

set HOME=%USERPROFILE%
venv-%PY_VER%-64\scripts\python -m twine check uploads\*
    if errorlevel 1 goto :eof
venv-%PY_VER%-64\scripts\python -m twine upload -p %1 uploads\*
endlocal
