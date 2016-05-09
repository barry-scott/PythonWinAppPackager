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

Installation
------------

::

py -3.5 -m pip install win-app-packager


Usage
-----

py -3.5 -m win_app_packager
