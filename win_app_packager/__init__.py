#
#   __init__.py
#
__commands = set( ['build', 'flags'] )

def dispatchCommand( argv ):
    if len(argv) < 2 or argv[1] not in __commands:
        from . import win_app_package_builder
        win_app_package_builder.AppPackage().usage()

        from . import win_app_package_exe_config
        win_app_package_exe_config.usage()

        return 1

    if argv[1] == 'build':
        from . import win_app_package_builder
        return win_app_package_builder.AppPackage().buildCommand( argv )

    elif argv[1] == 'flags':
        from . import win_app_package_exe_config
        win_app_package_exe_config.flagsCommand( argv )
