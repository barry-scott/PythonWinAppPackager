setlocal
py -3 -m colour_text "<>info Info:<> build-all clean out uploads"
rmdir /s /q uploads

call build.cmd 3.9 64
    if errorlevel 1 goto :eof
call build.cmd 3.10 64
    if errorlevel 1 goto :eof
call build.cmd 3.11 64
    if errorlevel 1 goto :eof

py -3 -m colour_text "<>info Info:<> Built files in uploads"
dir /s /b uploads
endlocal
