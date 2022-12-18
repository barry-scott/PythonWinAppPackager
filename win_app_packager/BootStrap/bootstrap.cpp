//
// bootstrap.cpp
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

#define RESOURCE_FOLDER_NAME L"PyWinAppRes"
#define LIBRARY_FOLDER_NAME RESOURCE_FOLDER_NAME L"\\lib"

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
            throw BootstrapError();\
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
            throw BootstrapError();\
        }\
    }\
    while( false )

DECLVAR( int, Py_VerboseFlag );
DECLVAR( int, Py_IgnoreEnvironmentFlag );
DECLVAR( int, Py_NoUserSiteDirectory );
DECLPROC(   void, Py_Initialize, (void) );
DECLPROC(   void, Py_SetProgramName, (wchar_t *) );
DECLPROC(   void, Py_SetPythonHome, (wchar_t *) );
DECLPROC(   void, Py_SetPath, (const wchar_t *) );
DECLPROC(   void, PySys_SetArgvEx, (int argc, wchar_t **argv, int updatepath) );
DECLPROC(    int, PyRun_SimpleString, (const char *script) );
DECLPROC(   void, PyEval_InitThreads, (void) );
DECLPROC( char *, Py_EncodeLocale, (const wchar_t *text, size_t *error_pos) );
}

class BootstrapError: public std::exception
{
    virtual const char* what() const throw()
    {
        return "BootstrapError";
    }
};


class WCharT
{
public:
    WCharT( int size )
    : m_allocated_size( size )
    , m_str( new wchar_t[ size ] )
    {
        m_str[0] = 0;
    }
    ~WCharT()
    {
        delete m_str;
    }

    WCharT &operator<<( const wchar_t *str )
    {
        StringCchCatW( m_str, m_allocated_size, str );
        return *this;
    }

    WCharT &operator<<( const WCharT &str )
    {
        StringCchCatW( m_str, m_allocated_size, str.c_str() );
        return *this;
    }

    // python expect none-const strings
    operator wchar_t *()
    {
        return m_str;
    }

    const wchar_t *c_str() const
    {
        return m_str;
    }

    int size()
    {
        return m_allocated_size;
    }

private:
    int m_allocated_size;
    wchar_t  *m_str;
};

std::wostream& operator<<( std::wostream& stream, const WCharT &str )
{
    stream << str.c_str();
    return stream;
}

class BootstrapApp
{
public:
    BootstrapApp()
    : m_stderr()
    , m_hApp( GetModuleHandle( nullptr ) )
    , m_hPython( nullptr )
    , m_win_app_debug( c_filename_size )
    , m_debug( false )
    , m_installation_folder_key( c_pathname_size )
    , m_installation_folder_value( c_pathname_size )
    , m_installation_folder( c_pathname_size )
    , m_python_dll( c_filename_size )
    , m_main_py_module( c_filename_size )
    , m_py_verbose( 0 )
    {
    }
    ~BootstrapApp()
    {
    }

    int main( int argc, wchar_t **argv )
    {
        try
        {
            return _main( argc, argv );
        }
        catch( BootstrapError & )
        {
#if defined(_CONSOLE)
            std::wcerr << "Error: Application bootstrap failed:" << std::endl;
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
        GetEnvironmentVariableW( L"PY_WIN_APP_DEBUG", m_win_app_debug, m_win_app_debug.size() );
        if( m_win_app_debug.c_str()[0] != 0
        &&  m_win_app_debug.c_str()[0] == '1' )
        {
            m_debug = true;
        }

        if( m_debug )
        {
#if defined(_CONSOLE)
            std::wcerr << "PythonWinApp Bootstrap starting" << std::endl;
#endif
#if defined( _WINDOWS )
            MessageBox( nullptr, L"Starting", L"PythonWinApp Bootstrap", MB_OK | MB_ICONERROR );
#endif
        }

        m_stderr << "readConfigFromResources()" << std::endl;
        readConfigFromResources();

        m_stderr << "Installation folder: " << m_installation_folder << std::endl;

        WCharT filename( c_pathname_size );
        filename << m_installation_folder << L"\\" RESOURCE_FOLDER_NAME "\\" << m_python_dll;
        m_stderr << "LoadLibrary " << filename << std::endl;

        m_hPython = LoadLibrary( filename );
        if( m_hPython == nullptr )
        {
            m_stderr << "Failed to load: " << filename << std::endl;
            m_stderr << "Failed to load2: " << filename << std::endl;
            throw BootstrapError();
        }

        GETVAR( Py_VerboseFlag );
        GETVAR( Py_IgnoreEnvironmentFlag );
        GETVAR( Py_NoUserSiteDirectory );
        GETPROC( Py_Initialize );
        GETPROC( Py_SetProgramName );
        GETPROC( Py_SetPythonHome );
        GETPROC( Py_SetPath );
        GETPROC( PySys_SetArgvEx );
        GETPROC( PyRun_SimpleString );
        GETPROC( PyEval_InitThreads );
        GETPROC( Py_EncodeLocale );

        WCharT python_home( c_pathname_size );
        python_home << m_installation_folder << L"\\" RESOURCE_FOLDER_NAME;
        m_stderr << "python home: " << python_home << std::endl;

        WCharT program_name( c_pathname_size );
        program_name << python_home << L"\\" << m_main_py_module << L".exe";
        m_stderr << "program home: " << program_name << std::endl;

        m_stderr << "Py_SetProgramName " << program_name << std::endl;
        NAME( Py_SetProgramName )( program_name );

        m_stderr << "Py_SetPythonHome " << python_home << std::endl;
        NAME( Py_SetPythonHome )( python_home );

        // do not allow env vars to change how we run
        m_stderr << "Py_IgnoreEnvironmentFlag 1" << std::endl;
        *NAME( Py_IgnoreEnvironmentFlag ) = 1;

        // do not allow users install packages to change how we run
        m_stderr << "Py_NoUserSiteDirectory 1" << std::endl;
        *NAME( Py_NoUserSiteDirectory ) = 1;

        m_stderr << "Py_VerboseFlag " << m_py_verbose << std::endl;
        *NAME( Py_VerboseFlag ) = m_py_verbose;

        // between the program_name and the python_home
        // python can setup the sys.path it needs
        m_stderr << "Py_Initialize" << std::endl;
        NAME( Py_Initialize )();

        m_stderr << "PyEval_InitThreads" << std::endl;
        NAME( PyEval_InitThreads )();

        m_stderr << "PySys_SetArgvEx" << std::endl;
        NAME( PySys_SetArgvEx )( argc, argv, 0 );

        //
        // runpy._run_module_as_main is not public - so expect things to break
        // is the python devs need to update the API
        //
        //  use r"\path\file.py" so that "'" can be in the path and r so that we can
        //  avoid quoting the \.
        //
        WCharT boot_script( 1024 );
        boot_script
            << L"import run_win_app;"
            << L"run_win_app.run_win_app( "
                << L"r\"" << m_installation_folder << L"\\" << RESOURCE_FOLDER_NAME << L"\\" << m_main_py_module << L"\""
                << L" )";

        m_stderr << "boot script: " << boot_script << std::endl;

        m_stderr << "Py_EncodeLocale" << std::endl;
        char *locale_boot_script = NAME( Py_EncodeLocale )( boot_script, NULL );

#if defined(_CONSOLE)
            std::wcerr << "PyWinAppRes before PyRun_SimpleString:" << std::endl;
            std::wcerr << m_stderr.str();
#endif

#if defined(_WINDOWS)
            MessageBox( nullptr, m_stderr.str().data(), L"PyWinAppRes before PyRun_SimpleString", MB_OK | MB_ICONERROR );
#endif

        m_stderr << "PyRun_SimpleString" << std::endl;
        NAME( PyRun_SimpleString )( locale_boot_script );

        m_stderr << "return 0" << std::endl;
        return 0;
    }

    void readConfigFromResources()
    {
        readConfigString( IDS_INSTALL_FOLDER_KEY, m_installation_folder_key, m_installation_folder_key.size(), true );
        readConfigString( IDS_PYTHON_DLL, m_python_dll, m_python_dll.size() );
        readConfigString( IDS_MAIN_PY_MODULE, m_main_py_module, m_main_py_module.size() );

        wchar_t buffer[2];
        readConfigString( IDS_PY_VERBOSE, buffer, 2, true );
        m_py_verbose = buffer[0] == '1' ? 1 : 0;

        if( m_installation_folder_key[0] != 0 )
        {
            readConfigString( IDS_INSTALL_FOLDER_KEY, m_installation_folder_value, m_installation_folder_value.size() );
            m_stderr << "readConfigString m_installation_folder_value " << m_installation_folder_value << std::endl;
            readConfigFromRegistry();
            m_stderr << "readConfigFromRegistry m_installation_folder " << m_installation_folder << std::endl;
        }
        else
        {
            // use path to this exe
            GetModuleFileName( nullptr, m_installation_folder, m_installation_folder.size() );
            m_stderr << "GetModuleFileName m_installation_folder " << m_installation_folder << std::endl;

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
                m_stderr << "Failed to find \\ in " << m_installation_folder << std::endl;
                throw BootstrapError();
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
            throw BootstrapError();
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
            throw BootstrapError();
        }

        DWORD value_length = m_installation_folder_value.size();
        rc = RegGetValue( reg_key, nullptr, m_installation_folder_value, RRF_RT_REG_SZ, nullptr, m_installation_folder, &value_length );
        if( rc != ERROR_SUCCESS )
        {
            wchar_t buffer[256];
            FormatMessage( FORMAT_MESSAGE_FROM_SYSTEM, 0, rc, 0, buffer, sizeof(buffer)/sizeof(wchar_t), nullptr );
            m_stderr << "failed to read " << m_installation_folder_value << " registry value from key " << m_installation_folder_key << " rc " << rc << " " << buffer << std::endl;
            throw BootstrapError();
        }
    }

private:
    std::wostringstream m_stderr;

    HINSTANCE m_hApp;
    HMODULE m_hPython;
    static const int c_pathname_size = 65536;
    static const int c_filename_size = 128;
    WCharT m_win_app_debug;
    bool m_debug;
    WCharT m_installation_folder_key;
    WCharT m_installation_folder_value;
    WCharT m_installation_folder;
    WCharT m_python_dll;
    WCharT m_main_py_module;
    int m_py_verbose;
};

#if defined(_CONSOLE)
int wmain( int argc, wchar_t **argv, wchar_t **envp )
{
    BootstrapApp client;
    return client.main( argc, argv );
}
#endif

#if defined(_WINDOWS)
int APIENTRY wWinMain(
    _In_ HINSTANCE hInstance,
    _In_opt_ HINSTANCE hPrevInstance,
    _In_ LPWSTR lpCmdLine,
    _In_ int nCmdShow )
{
    BootstrapApp client;
    return client.main( __argc, __wargv );
}
#endif
