//
// cli-app.cpp : Defines the entry point for the console application.
//

#include <WinSDKVer.h>
#define _WIN32_WINNT 0x601  // Windows 7 - read SDKDDKVer for defs
#include <SDKDDKVer.h>

#define WIN32_LEAN_AND_MEAN             // Exclude rarely-used stuff from Windows headers
#include <Windows.h>

#include <cstdlib>
#include <cstdio>
#include <iostream>
#include <tchar.h>
#include <Strsafe.h>
#include <exception>
#include <sstream>

#include "bootstrap-resource-ids.h"

#define RESOURCE_FOLDER_NAME "PyWinAppRes"
#define LIBRARY_FOLDER_NAME RESOURCE_FOLDER_NAME "\\lib"

extern "C" {

#define NAME( name ) bootstrap_##name

#define DECLPROC( result, name, args )\
    typedef result ( __cdecl *__PROC__##name ) args;\
    __PROC__##name NAME(name) = NULL

#define GETPROC( name )\
    do {\
        NAME(name) = reinterpret_cast< __PROC__##name >( GetProcAddress( m_hPython, #name ) );\
        if ( NAME(name) == nullptr )\
        {\
            m_stderr << "Cannot GetProcAddress for " #name << std::endl;\
            throw CliAppError();\
        }\
    }\
    while( false )

#define DECLVAR( vartyp, name )\
    typedef vartyp __VAR__##name;\
    __VAR__##name *NAME(name) = nullptr

#define GETVAR( name )\
    do {\
        NAME(name) = reinterpret_cast<__VAR__##name *>( GetProcAddress( m_hPython, #name ) );\
        if( NAME(name) == nullptr )\
        {\
            m_stderr << "Cannot GetProcAddress for " #name << std::endl;\
            throw CliAppError();\
        }\
    }\
    while( false )

DECLVAR( int, Py_VerboseFlag );
DECLVAR( int, Py_IgnoreEnvironmentFlag );
DECLPROC(   void, Py_Initialize, (void) );
DECLPROC(   void, Py_SetProgramName, (wchar_t *) );
DECLPROC(   void, Py_SetPythonHome, (wchar_t *) );
DECLPROC(   void, Py_SetPath, (const wchar_t *) );
DECLPROC(   void, PySys_SetArgvEx, (int argc, wchar_t **argv, int updatepath) );
DECLPROC(    int, PyRun_SimpleString, (const char *script) );
DECLPROC(   void, PyEval_InitThreads, (void) );
DECLPROC( char *, Py_EncodeLocale, (const wchar_t *text, size_t *error_pos) );
}

class CliAppError: public std::exception
{
    virtual const char* what() const throw()
    {
        return "CliAppError";
    }
};


class ClientApp
{
public:
    ClientApp()
    : m_stderr()
    {
        m_hApp = GetModuleHandle( nullptr );
    }
    ~ClientApp()
    {
    }

    int main( int argc, wchar_t **argv )
    {
        try
        {
            return _main( argc, argv );
        }
        catch( CliAppError & )
        {
#if defined(_CONSOLE)
            std::wcerr << m_stderr.str();
#endif

#if defined(_WINDOWS)
            MessageBox( nullptr, m_stderr.str().data(), L"PythonWinApp Boot Strap Error", MB_OK | MB_ICONERROR );
#endif

            return 1;
        }
    }

    int _main( int argc, wchar_t **argv )
    {
#if defined(BOOTSTRAP_DEBUG)
        MessageBox( nullptr, L"Debug", L"PythonWinApp Boot Strap Error", MB_OK | MB_ICONERROR );
#endif

        readConfigFromResources();

        wchar_t filename[ c_pathname_size ];
        StringCchCopyW( filename, c_pathname_size, m_installation_folder );
        StringCchCatW( filename, c_pathname_size, L"\\" RESOURCE_FOLDER_NAME "\\" );
        StringCchCatW( filename, c_pathname_size, m_python_dll );

        m_hPython = LoadLibrary( filename );
        if( m_hPython == nullptr )
        {
            m_stderr << "Failed to load: " << filename << std::endl;
            throw CliAppError();
        }

        GETVAR( Py_VerboseFlag );
        GETVAR( Py_IgnoreEnvironmentFlag );
        GETPROC( Py_Initialize );
        GETPROC( Py_SetProgramName );
        GETPROC( Py_SetPythonHome );
        GETPROC( Py_SetPath );
        GETPROC( PySys_SetArgvEx );
        GETPROC( PyRun_SimpleString );
        GETPROC( PyEval_InitThreads );
        GETPROC( Py_EncodeLocale );

        wchar_t python_home[ c_pathname_size ];
        StringCchCopyW( python_home, c_pathname_size, m_installation_folder );
        StringCchCatW( python_home, c_pathname_size, L"\\" RESOURCE_FOLDER_NAME );

        wchar_t program_name[ c_pathname_size ];
        StringCchCopyW( program_name, c_pathname_size, python_home );
        StringCchCatW( program_name, c_pathname_size, L"\\" );
        StringCchCatW( program_name, c_pathname_size, m_main_py_module );
        StringCchCatW( program_name, c_pathname_size, L".exe" );

        NAME( Py_SetProgramName )( program_name );
        NAME( Py_SetPythonHome )( python_home );

        *NAME( Py_IgnoreEnvironmentFlag ) = 1;          // do not allow env vars to change how we run
        *NAME( Py_VerboseFlag ) = m_py_verbose;

        // between the program_name and the python_home
        // python can setup the sys.path it needs
        NAME( Py_Initialize )();
        NAME( PyEval_InitThreads )();
        NAME( PySys_SetArgvEx )( argc, argv, 0 );

        static const int len = 1024;
        wchar_t boot_script[ len ];

        //
        // runpy._run_module_as_main is not public - so expect things to break
        // is the python devs need to update the API
        //
        StringCchCopyW( boot_script, len, L"import run_win_app;run_win_app.run_win_app( '" );
        StringCchCatW( filename, c_pathname_size, m_installation_folder );
        StringCchCatW( filename, c_pathname_size, L"\\" RESOURCE_FOLDER_NAME "\\" );
        StringCchCatW( boot_script, len, m_main_py_module );
        StringCchCatW( boot_script, len, L"' )" );

        char *locale_boot_script = NAME( Py_EncodeLocale )( boot_script, NULL );
        return NAME( PyRun_SimpleString )( locale_boot_script );
    }

    void readConfigFromResources()
    {
        readConfigString( IDS_INSTALL_FOLDER_KEY, m_installation_folder_key, c_filename_size, true );
        readConfigString( IDS_PYTHON_DLL, m_python_dll, c_filename_size );
        readConfigString( IDS_MAIN_PY_MODULE, m_main_py_module, c_filename_size );

        wchar_t buffer[2];
        readConfigString( IDS_PY_VERBOSE, buffer, 2, true );
        m_py_verbose = buffer[0] == '1' ? 1 : 0;

        if( m_installation_folder_key[0] != 0 )
        {
            readConfigString( IDS_INSTALL_FOLDER_KEY, m_installation_folder_value, c_filename_size );
            readConfigFromRegistry();
        }
        else
        {
            // use path to this exe
            GetModuleFileName( nullptr, m_installation_folder, c_filename_size );

            // dirname
            wchar_t *last_sep = nullptr;
            for( wchar_t *p = m_installation_folder; *p != 0; ++p )
            {
                if( *p == '\\' )
                {
                    last_sep = p;
                }
            }
            if( last_sep == nullptr )
            {
                std::cerr << "Failed to find \\ in " << m_installation_folder << std::endl;
                throw CliAppError();
            }
            *last_sep = 0;
        }

    }

    void readConfigString( int id, wchar_t *buffer, int size, bool allow_missing=false )
    {
        buffer[0] = 0;

        int len = LoadString( m_hApp, id, buffer, size );
        if( len == 0 && !allow_missing )
        {
            m_stderr << "failed to LoadString id " << id << std::endl;
            throw CliAppError();
        }
    }

    void readConfigFromRegistry()
    {
        HKEY reg_key;
        long rc = RegOpenKeyEx( HKEY_LOCAL_MACHINE, m_installation_folder_key, 0, KEY_READ, &reg_key );
        if( rc != ERROR_SUCCESS )
        {
            wchar_t buffer[256];
            FormatMessage( FORMAT_MESSAGE_FROM_SYSTEM, 0, rc, 0, buffer, 256, nullptr );
            m_stderr << "failed to open " << m_installation_folder_key << " registry key " << rc << " " << buffer << std::endl;
            throw CliAppError();
        }

        DWORD value_length = c_pathname_size;
        rc = RegGetValue( reg_key, nullptr, m_installation_folder_value, RRF_RT_REG_SZ, nullptr, m_installation_folder, &value_length );
        if( rc != ERROR_SUCCESS )
        {
            wchar_t buffer[256];
            FormatMessage( FORMAT_MESSAGE_FROM_SYSTEM, 0, rc, 0, buffer, 256, nullptr );
            m_stderr << "failed to read " << m_installation_folder_value << " registry value from key " << m_installation_folder_key << " rc " << rc << " " << buffer << std::endl;
            throw CliAppError();
        }
    }

private:
    std::wostringstream m_stderr;

    HINSTANCE m_hApp;
    HMODULE m_hPython;
    static const int c_pathname_size = 1024;
    static const int c_filename_size = 64;
    wchar_t m_installation_folder_key[ c_pathname_size ];
    wchar_t m_installation_folder_value[ c_pathname_size ];
    wchar_t m_installation_folder[ c_pathname_size ];
    wchar_t m_python_dll[ c_filename_size ];
    wchar_t m_main_py_module[ c_filename_size ];
    int m_py_verbose;
};

#if defined(_CONSOLE)
int wmain( int argc, wchar_t **argv, wchar_t **envp )
{
    ClientApp client;
    return client.main( argc, argv );
}
#endif

#if defined(_WINDOWS)
int APIENTRY wWinMain(_In_ HINSTANCE hInstance,
                     _In_opt_ HINSTANCE hPrevInstance,
                     _In_ LPWSTR    lpCmdLine,
                     _In_ int       nCmdShow)
{
    ClientApp client;
    return client.main( __argc, __wargv );
}
#endif
