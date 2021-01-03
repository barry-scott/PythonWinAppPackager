setlocal
colour-print "<>info Info:<> build-all clean out uploads"
rmdir /s /q uploads

call build.cmd 3.7 64
    if errorlevel 1 goto :eof
call build.cmd 3.8 64
    if errorlevel 1 goto :eof
call build.cmd 3.9 64
    if errorlevel 1 goto :eof
call build.cmd 3.8 64
    if errorlevel 1 goto :eof

colour-print "<>info Info:<> Built files in uploads"
dir /s /b uploads
endlocal
