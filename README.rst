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

win_app_packager supports python 3 for win64.

1.4.0 add support for packaging projects from a virtual env (venv).

1.3.0 supports changing the version resource of the created .EXE.
The version fields that name the app are set to the app .EXE name.

The --version option allows the app's version to be set.

Python version 3.5, 3.6 and 3.7 are supported.

Installation
------------

::

  py -3 -m pip install win-app-packager


Usage
-----

::

  C:\Users\barry> py -3 -m win_app_packager
  python3 -m win_app_packager build <main-script> <package-folder> [<options>...]
    main-script
      - python main module
    package-folder
      - folder to create package into
  
    Where <options> are:
      --console
      --cli
          build a windows console progam (the default).
      --gui
          build a windows gui program.
      --name
          name the program (defaults to the <main-script> name).
      --version <version>
          Set the version of the .EXE to be <version>.
          e.g 1.0.2.5
      --install-key <key>
      --install-value <value>
          The install path of the package can be read
          from the windows registry from key HKLM:<key> value <value>
          otherwise the install path is assumed to be the same folder
          that the .EXE files is in.
      --modules-allowed-to-be-missing-file <file-name>
          Add all the modules listed in the file <file-name> to the allowed
          to be missing list. Blank lines and lines starting with a '#' as ignored.
      --merge
          Do not clean out the <package-folder> before building the package.
          Useful for putting multiple programs into one package.
      --verbose
          Output extra information about the build process.
      --debug
          Developer option. Output lots of details about the build process.
      --bootstrap-debug
          Developer option. Copy PDF files and setup a Microsoft Visual
          Studio solution (.sln) file suitable for running the bootstrap
          under the debugger.
  
  python3 -m win_app_packager flags <exe-file> <verbose>'
    exe-file
      - the win_app_package create EXE file to modify
    verbose
      - either "0" or "1". The value to see the python verbose flag to.
