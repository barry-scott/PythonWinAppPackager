#
#	Makefile
#
CCC=cl /nologo
CC=cl /nologo


# /Zi - debug info
# /MT - link with LIBCMT.LIB
# /EHsc - c++ exceptions
# /GS - enable security checks
# /W3 - warning levevl 3
# /Zc:wchar_t - wchar_t is builtin
# /Od - disable optimization
# /sdl - security checks
# /D "NDEBUG" - 
# /D "_CONSOLE" - 
# /D "_UNICODE" - 
# /D "UNICODE" - 
# /WX- - [no] treat warnings as errors
# /Zc:forScope - enforce Standard C++ for scoping rules
# /RTC1 - Enable fast checks (stack and uninit locals)
# /Gd - _cdecl calling convention

COMMON_FLAGS=/Zi /MT /EHsc /GS /W3 /Gd /Zc:wchar_t /Od /sdl /Zc:inline /WX- /Zc:forScope /RTC1 /Iobj
COMMON_DEFINES=/D "NDEBUG" /D "_UNICODE" /D "UNICODE" /D "WIN32"
CLI_FLAGS=$(COMMON_FLAGS) $(COMMON_DEFINES) /D "_CONSOLE" $(EXTRA_FLAGS)
GUI_FLAGS=$(COMMON_FLAGS) $(COMMON_DEFINES) /D "_WINDOWS" $(EXTRA_FLAGS)

LDEXE=$(CCC) /Zi /MT /EHsc
CLI_LIBS=User32.lib Advapi32.lib
GUI_LIBS=User32.lib Advapi32.lib

all: obj obj\bootstrap-gui.exe obj\bootstrap-cli.exe

obj :
	mkdir obj

#
#	CLI App
#
obj\bootstrap-cli.exe : obj\bootstrap-cli.obj obj\bootstrap.res
	@echo Link obj\bootstrap-cli.exe
	$(LDEXE) $(CLI_FLAGS) /Feobj\bootstrap-cli.exe /Fdobj\bootstrap-cli.pdb obj\bootstrap-cli.obj obj\bootstrap.res $(CLI_LIBS)

obj\bootstrap-cli.obj : bootstrap.cpp obj\bootstrap-resource-ids.h
	@echo Compile: bootstrap.cpp into obj\bootstrap-cli.obj
	$(CCC) $(CLI_FLAGS) /c /Foobj\bootstrap-cli.obj /Fdobj\bootstrap-cli.pdb bootstrap.cpp

clean::
	if exist obj\bootstrap-cli.* del obj\bootstrap-cli.*


#
#	GUI App
#
obj\bootstrap-gui.exe : obj\bootstrap-gui.obj obj\bootstrap.res
	@echo Link obj\bootstrap-gui.exe
	$(LDEXE) $(GUI_FLAGS) /Feobj\bootstrap-gui.exe /Fdobj\bootstrap-gui.pdb obj\bootstrap-gui.obj obj\bootstrap.res $(GUI_LIBS)

obj\bootstrap-gui.obj : bootstrap.cpp obj\bootstrap-resource-ids.h
	@echo Compile: bootstrap-gui.cpp into obj\bootstrap-gui.obj
	$(CCC) $(GUI_FLAGS) /c /Foobj\bootstrap-gui.obj /Fdobj\bootstrap-gui.pdb bootstrap.cpp

clean::
	if exist obj\bootstrap-gui.* del obj\bootstrap-gui.*

#
#	common
#
obj\bootstrap.res : bootstrap.rc obj\bootstrap-resource-ids.h
	@echo Compile bootstrap.rc obj\bootstrap.res
	rc /nologo /v /r /i obj /foobj\bootstrap.res bootstrap.rc

obj\bootstrap-resource-ids.h : ..\win_app_package_exe_config.py
	..\win_app_package_exe_config.py create obj\bootstrap-resource-ids.h

clean::
	if exist obj\bootstrap.res del obj\bootstrap.res
