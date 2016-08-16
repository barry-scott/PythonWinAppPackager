setlocal
rmdir /s /q dist


setlocal
echo Info: Build for 32 bit
rmdir /s /q build
rmdir /s /q win_app_packager.egg-info
rmdir /s /q win_app_packager\BootStrap\obj

call "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat"
    if errorlevel 1 goto :error
set PY_VER=3.5-32

pushd win_app_packager\BootStrap
nmake /nologo
    if errorlevel 1 goto :error
popd >NUL

py -%PY_VER% setup.py sdist bdist_wheel %2 %3 %4 %5
    if errorlevel 1 goto :error
endlocal

setlocal
echo Info: Build for 64 bit
rmdir /s /q build
rmdir /s /q win_app_packager.egg-info
rmdir /s /q win_app_packager\BootStrap\obj

call "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64\vcvars64.bat"
    if errorlevel 1 goto :error
set PY_VER=3.5

pushd win_app_packager\BootStrap
nmake /nologo
    if errorlevel 1 goto :error
popd >NUL

py -%PY_VER% setup.py sdist bdist_wheel %2 %3 %4 %5
    if errorlevel 1 goto :error
dir/s/b dist\*.whl
endlocal
goto :eof

:error
    echo Error: Build failed

endlocal
