setlocal
@echo off
if "%1" == "" (
    colour-print "<>em Usage: %0 version 32|64<>"
    colour-print "<>em        %0 3.7 64<>"
    goto :eof
)
if "%2" == "" (
    colour-print "<>em Usage: %0 version 32|64<>"
    colour-print "<>em        %0 3.7 64<>"
    goto :eof
)
set BUILD_VER=%1
set BUILD_ARCH=%2
set PY_VER=%BUILD_VER%-%BUILD_ARCH%

colour-print "<>info Info:<> Clean out old builds"
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist win_app_packager.egg-info rmdir /s /q win_app_packager.egg-info
if exist win_app_packager\BootStrap\obj rmdir /s /q win_app_packager\BootStrap\obj

goto build_%BUILD_ARCH%
:build_32
setlocal
colour-print "<>info Info:<> Build Python <>em %%s<> for 32 bit" "%PY_VER%"

if exist "c:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    colour-print "<>em Found compiler VC 2017<>"
    call "c:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" x86
    if errorlevel 1 goto :error
)
if exist "c:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    colour-print "<>em Found compiler VC 2019<>"
    call "c:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" x86
    if errorlevel 1 goto :error
)

pushd win_app_packager\BootStrap
nmake /nologo
    if errorlevel 1 goto :error
popd >NUL

colour-print "<>info Info:<> Install requirements"
py -%PY_VER% -m pip install --user --no-warn-script-location --upgrade -r requirements.txt

colour-print "<>info Info:<> Build wheel"
py -%PY_VER% setup.py --quiet sdist bdist_wheel %3 %4 %5 %6
    if errorlevel 1 goto :error

dir /s /b dist\*.whl
colour-print "<>info Info:<> Check wheel"
py -%PY_VER% -m twine check dist\*
    if errorlevel 1 goto :error

endlocal
)
goto :final_actions

:build_64
setlocal
colour-print "<>info Info:<> Build Python <>em %%s<> for 64 bit" "%PY_VER%"

if exist "c:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    colour-print "<>em Found compiler VC 2017<>"
    call "c:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
    if errorlevel 1 goto :error
)
if exist "c:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    colour-print "<>em Found compiler VC 2019<>"
    call "c:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
    if errorlevel 1 goto :error
)
colour-print "<>info Info:<> Build EXE"

pushd win_app_packager\BootStrap
nmake /nologo
    if errorlevel 1 goto :error
popd >NUL

colour-print "<>info Info:<> Install requirements"
py -%PY_VER% -m pip install --no-warn-script-location --user --upgrade -r requirements.txt

colour-print "<>info Info:<> Build wheel"
py -%PY_VER% setup.py --quiet sdist bdist_wheel %3 %4 %5 %6
    if errorlevel 1 goto :error

dir /s /b dist\*.whl
colour-print "<>info Info:<> Check wheel"
py -%PY_VER% -m twine check dist\*
    if errorlevel 1 goto :error

endlocal
goto :final_actions

:final_actions

colour-print "<>info Info:<> Run tests for Python %%s" "%PY_VER%"
call tests\run-tests.cmd %PY_VER%

if not exist uploads mkdir uploads
copy dist\*.whl uploads
copy dist\*.tar.gz uploads
goto :eof

:error
    colour-print "<>error Error: Build failed for Python %%s<>" "%PY_VER%"
endlocal
