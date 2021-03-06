"""
setup.py for PythonWinAppPackager

"""

# Always prefer setuptools over distutils
import setuptools
import distutils.dist

import os.path

import win_app_packager
version = win_app_packager.VERSION

url = 'https://github.com/barry-scott/PythonWinAppPackager'

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

def getDevStatusFromVersion():
    if 'a' in version:
        return 'Development Status :: 3 - Alpha'

    elif 'b' in version:
        return 'Development Status :: 4 - Beta'

    else:
        return 'Development Status :: 5 - Production/Stable'

class DistributionAppPackager(distutils.dist.Distribution):
    # force wheel to be win32 or win64
    def has_c_libraries( self ):
        return True

setuptools.setup(
    name='win_app_packager',

    # force tag to include win32/win64 marker
    distclass=DistributionAppPackager, libraries = [],

    version=version,

    description='Python Win App Packager',
    long_description=long_description,
    long_description_content_type='text/x-rst',

    # The project's main homepage.
    url=url,

    # Author details
    author='Barry Scott',
    author_email='barry@barrys-emacs.org',

    # Choose your license
    license='Apache 2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        getDevStatusFromVersion(),

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # environment
        'Environment :: Win32 (MS Windows)',
        'Operating System :: Microsoft :: Windows :: Windows 7',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    # What does your project relate to?
    keywords='development',

    packages=['win_app_packager'],

    package_data={'win_app_packager':
                        ['BootStrap/obj/bootstrap-cli.exe'
                        ,'BootStrap/obj/bootstrap-gui.exe']},

    install_requires=["namedstruct >=1.2.2", "colour_text"]
)
