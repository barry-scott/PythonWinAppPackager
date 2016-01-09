rmdir /s /q build
rmdir /s /q dist
rmdir /s /q PythonWinAppPackager.egg-info
rmdir /s /q app_packager\BootStrap\obj

setlocal
if "%1" == "32" (
    call "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat"
    set PY_VER=3.5-32
) else (
    call "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64\vcvars64.bat"
    set PY_VER=3.5
)

pushd app_packager\BootStrap
nmake /nologo
popd

py -%PY_VER% setup.py sdist bdist_wheel %2 %3 %4 %5
endlocal
