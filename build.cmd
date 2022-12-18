setlocal
@echo off
if "%1" == "" (
    py -3 -m colour_text "<>em Usage: %0 version 32|64<>"
    py -3 -m colour_text "<>em        %0 3.7 64<>"
    goto :eof
)
if "%2" == "" (
    py -3 -m colour_text "<>em Usage: %0 version 32|64<>"
    py -3 -m colour_text "<>em        %0 3.7 64<>"
    goto :eof
)
set BUILD_VER=%1
set BUILD_ARCH=%2
set PY_VER=%BUILD_VER%-%BUILD_ARCH%

py -3 -m colour_text "<>info Info:<> Clean out old builds"
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist win_app_packager.egg-info rmdir /s /q win_app_packager.egg-info
if exist win_app_packager\BootStrap\obj rmdir /s /q win_app_packager\BootStrap\obj

echo on
if exist venv-%PY_VER% rmdir /s /q venv-%PY_VER%

py -3 -m colour_text "<>info Info:<> build venv requirements"
py -%PY_VER% -m venv venv-%PY_VER%
venv-%PY_VER%\scripts\pip install -r requirements.txt
set VPYTHON=%CD%\venv-%PY_VER%\scripts\python

if "%BUILD_ARCH%" == "32" set VC_ARCH=x86
if "%BUILD_ARCH%" == "64" set VC_ARCH=x64
if "%VC_ARCH%" == "" goto :error

py -3 -m colour_text "<>info Info:<> Build Python <>em %%s<> for %BUILD_ARCH% bit" "%PY_VER%"

if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" (
    py -3 -m colour_text "<>em Found compiler VC 2022<>"
    call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

) else if exist "c:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    py -3 -m colour_text "<>em Found compiler VC 2017<>"
    call "c:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" %VC_ARCH%
    if errorlevel 1 goto :error
)
if exist "c:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    py -3 -m colour_text "<>em Found compiler VC 2019<>"
    call "c:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" %VC_ARCH%
    if errorlevel 1 goto :error
)

py -3 -m colour_text "<>info Info:<> Build EXE"
pushd win_app_packager\BootStrap
nmake /nologo VPYTHON=%VPYTHON%
    if errorlevel 1 goto :error
popd >NUL

py -3 -m colour_text "<>info Info:<> Build wheel"
%VPYTHON% setup.py --quiet sdist bdist_wheel %3 %4 %5 %6
    if errorlevel 1 goto :error

dir /s /b dist\*.whl
py -3 -m colour_text "<>info Info:<> Check wheel"
%VPYTHON% -m twine check dist\*
    if errorlevel 1 goto :error

py -3 -m colour_text "<>info Info:<> Run tests for Python %%s" "%PY_VER%"

if not exist uploads mkdir uploads
copy dist\*.whl uploads
copy dist\*.tar.gz uploads

call tests\run-tests.cmd %PY_VER%

goto :eof

:error
    py -3 -m colour_text "<>error Error: Build failed for Python %%s<>" "%PY_VER%"
endlocal
