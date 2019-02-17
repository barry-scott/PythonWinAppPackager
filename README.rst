Python Win App Packager
-----------------------

Distributing end user software on windows should not require the
end user to install dependancies, like python.

This tool turns a python program into a package that is suitable
to be installed on window via installation software like INNO setup
(http://www.jrsoftware.org/isinfo.php).

The method used to create the package copies the source code of the
program, the source code from any python libraries and any required
python extensions and the DLLs that depend on.

The inclusion of the source code allows users to modify the program,
if they so desire.

win_app_packer supports python 3 for win64 and starting with 1.1.0
win32.

1.2.0 changes how package contents is collected. All files within
a package are included, not just the referenced include.

This, for example, allows packages like pytz to be packaged with its
binary zoneinfo files. And it removes the need for the special case
code for encodings.

1.2.2 add the --modules-allowed-to-be-missing-file to allow the new
module names to be added to the allowed to be missing list without
requiring a new release of win-app-packager. Typcially packages that
support both python 2  and python 3 will reference python 2 modules
that can be ignored.

1.2.4 fixed an issue with dbghelp.dll that is not required for the
app package being reported as required.

Installation
------------

::

py -3.6 -m pip install win-app-packager


Usage
-----

py -3.6 -m win_app_packager
