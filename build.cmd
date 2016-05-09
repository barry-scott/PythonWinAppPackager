setlocal
if "%1" == "32" (
    call "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat"
    set PY_VER=3.5-32
) else if "%1" == "64" (
    call "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64\vcvars64.bat"
    set PY_VER=3.5
) else (
    echo Error: %%1 must be 32 or 64
    goto :eof
)

rmdir /s /q build
rmdir /s /q dist
rmdir /s /q dist2
rmdir /s /q PythonWinAppPackager.egg-info
rmdir /s /q win_app_packager\BootStrap\obj

pushd win_app_packager\BootStrap
nmake /nologo
popd

py -%PY_VER% setup.py sdist bdist_wheel %2 %3 %4 %5
dir/s/b dist\*.whl
endlocal
