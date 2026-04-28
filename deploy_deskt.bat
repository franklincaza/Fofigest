@echo off
setlocal enabledelayedexpansion

:: Anclar CWD al directorio del .bat (evita rutas relativas rotas)
cd /d "%~dp0"

title Fofigest - Build Desktop

echo.
echo ============================================================
echo   Fofigest Desktop  ^|  Build Script
echo ============================================================
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado en PATH.
    echo         Instala Python 3.10+ desde https://python.org
    echo         y marca "Add to PATH" al instalar.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%V in ('python --version 2^>^&1') do set PY_VER=%%V
echo [OK]  %PY_VER% detectado.

:: Crear entorno virtual si no existe
if not exist ".venv\" (
    echo [INFO] Creando entorno virtual .venv ...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo [OK]  Entorno virtual creado.
) else (
    echo [OK]  Entorno virtual .venv ya existe, reutilizando.
)

:: Activar entorno virtual
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo activar el entorno virtual.
    pause
    exit /b 1
)
echo [OK]  Entorno virtual activado.

:: Actualizar pip
echo.
echo [INFO] Actualizando pip ...
python -m pip install --upgrade pip --quiet
echo [OK]  pip actualizado.

:: Instalar dependencias
echo.
echo [INFO] Instalando dependencias desde requirements_desktop.txt
echo        (puede tardar 5-10 minutos la primera vez) ...
pip install -r requirements_desktop.txt --quiet
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Fallo al instalar dependencias.
    echo         Ejecuta manualmente para ver el error:
    echo           pip install -r requirements_desktop.txt
    pause
    exit /b 1
)
echo [OK]  Dependencias instaladas.

:: Verificar PyInstaller y pywebview
python -c "import PyInstaller; import webview" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller o pywebview no disponibles.
    echo         Verifica requirements_desktop.txt e intenta de nuevo.
    pause
    exit /b 1
)
echo [OK]  PyInstaller y pywebview disponibles.

:: Limpiar builds anteriores
echo.
echo [INFO] Limpiando builds anteriores ...
if exist "build\"      rmdir /s /q "build"
if exist "dist\"       rmdir /s /q "dist"
if exist "Fofigest.exe" del /q "Fofigest.exe"
echo [OK]  Carpetas build/ y dist/ limpias.

:: Ejecutar PyInstaller
echo.
echo [INFO] Ejecutando PyInstaller con build.spec ...
echo        (puede tardar entre 3 y 10 minutos) ...
echo.
pyinstaller build.spec --noconfirm --clean
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PyInstaller fallo. Revisa los mensajes anteriores.
    echo         Log en: build\Fofigest\warn-Fofigest.txt
    pause
    exit /b 1
)

:: Verificar que el .exe existe
if not exist "dist\Fofigest.exe" (
    echo [ERROR] No se encontro dist\Fofigest.exe tras el build.
    pause
    exit /b 1
)

:: Calcular tamanio via PowerShell (fiable en cualquier Windows 10/11)
set EXE_MB=?
for /f %%S in ('powershell -noprofile -command "[int]((Get-Item 'dist\Fofigest.exe').Length/1MB)"') do set EXE_MB=%%S

echo.
echo ============================================================
echo   BUILD EXITOSO
echo ============================================================
echo.
echo   Ejecutable : dist\Fofigest.exe
echo   Tamanio    : %EXE_MB% MB
echo.
echo   DISTRIBUCION:
echo   Copia dist\Fofigest.exe a cualquier equipo Windows 10/11.
echo   Al abrirlo se creara automaticamente:
echo     Fofigest_data\   (junto al .exe)
echo   con la base de datos SQLite y el archivo de log.
echo.
echo   REQUISITO en Windows 10:
echo   Necesita "WebView2 Runtime" instalado (gratuito de Microsoft).
echo   Windows 11 ya lo incluye de fabrica.
echo.
echo ============================================================
echo.
pause
