setlocal
echo on
if "%1" == "" (
    echo "Usage: %0 version 32|64"
    echo "       %0 3.7 64"
    goto :eof
)
if "%2" == "" (
    echo "Usage: %0 version 32|64"
    echo "       %0 3.7 64"
    goto :eof
)
set BUILD_VER=%1
set BUILD_ARCH=%2

if exist dist rmdir /s /q dist

goto build_%BUILD_ARCH%
:build_32
setlocal
echo Info: Build for 32 bit
if exist build rmdir /s /q build
if exist win_app_packager.egg-info rmdir /s /q win_app_packager.egg-info
if exist win_app_packager\BootStrap\obj rmdir /s /q win_app_packager\BootStrap\obj

if exist "C:\Program Files (x86)\Microsoft Visual Studio %VC_VER%\VC\vcvarsall.bat" (
    echo Found compiler VC %VC_VER%
    call "C:\Program Files (x86)\Microsoft Visual Studio %VC_VER%\VC\vcvarsall.bat"
    if errorlevel 1 goto :error

)
if exist "c:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Found compiler VC 2017
    call "c:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" x86
    if errorlevel 1 goto :error
)
set PY_VER=%BUILD_VER%-32

pushd win_app_packager\BootStrap
nmake /nologo
    if errorlevel 1 goto :error
popd >NUL

py -%PY_VER% setup.py sdist bdist_wheel %3 %4 %5 %6
    if errorlevel 1 goto :error
endlocal
)
goto :final_actions

:build_64
setlocal
echo Info: Build for 64 bit
if exist build rmdir /s /q build
if exist win_app_packager.egg-info rmdir /s /q win_app_packager.egg-info
if exist win_app_packager\BootStrap\obj rmdir /s /q win_app_packager\BootStrap\obj

if exist "C:\Program Files (x86)\Microsoft Visual Studio %VC_VER%\VC\bin\amd64\vcvars64.bat" (
    echo Found compiler VC %VC_VER%
    call "C:\Program Files (x86)\Microsoft Visual Studio %VC_VER%\VC\bin\amd64\vcvars64.bat"
    if errorlevel 1 goto :error
)
if exist "c:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Found compiler VC 2017
    call "c:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
    if errorlevel 1 goto :error
)
echo Onward
set PY_VER=%BUILD_VER%

pushd win_app_packager\BootStrap
nmake /nologo
    if errorlevel 1 goto :error
popd >NUL

py -%PY_VER% setup.py sdist bdist_wheel %3 %4 %5 %6
    if errorlevel 1 goto :error
dir /s /b dist\*.whl
endlocal
goto :final_actions

:final_actions

call tests\run-tests.cmd %1 %2

if not exist uploads mkdir uploads
copy dist\*.whl uploads
copy dist\*.tar.gz uploads
goto :eof

:error
    echo Error: Build failed
endlocal
