#
#   run_win_app.py
#
#   Inspired by Python's runpy.py
#
import sys
import types

def run_win_app( path_name ):
    with open( path_name, "rb" ) as f:
        code = compile( f.read(), path_name, 'exec' )

    module = types.ModuleType( '__main__' )
    sys.modules[ '__main__' ] = module
    module.__dict__.update(
        __name__ = '__main__',
        __file__ = path_name,
        __cached__ = None,
        __doc__ = None,
        __loader__ = None,
        __package__ = '',
        __spec__ = None
        )
    exec( code, module.__dict__ )
