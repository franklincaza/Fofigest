@echo off
setlocal enabledelayedexpansion

:: Anclar directorio de trabajo al .bat
cd /d "%~dp0"

title Fofigest - Despliegue Azure

echo.
echo ============================================================
echo   Fofigest v4.0  ^|  Deploy Azure App Service
echo ============================================================
echo.

:: ===============================================================
::  CONFIGURACION  - ajustar si cambian los recursos Azure
:: ===============================================================
set SUBSCRIPTION=Suscripcion de Azure 1
set RESOURCEGROUP=Fofimatic
set LOCATION=centralus
set PLANNAME=ASP-Fofimatic-a092
set PLANSKU=F1
set SITENAME=Fofimatic-ultimate-fofigest
set RUNTIME=PYTHON:3.12
set STARTUP_CMD=waitress-serve --host=0.0.0.0 --port=8000 app:app
set DEPLOY_ZIP=%TEMP%\fofigest_deploy.zip
set TEMP_DIR=%TEMP%\fofigest_build

:: ===============================================================
::  1. VERIFICAR AZURE CLI
:: ===============================================================
echo [1/7] Verificando Azure CLI...
az --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Azure CLI no encontrado.
    echo         Instalar desde: https://aka.ms/installazurecliwindows
    echo.
    pause
    exit /b 1
)
echo [OK]  Azure CLI disponible.

:: ===============================================================
::  2. AUTENTICACION
:: ===============================================================
echo.
echo [2/7] Verificando sesion Azure...
az account show >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] No hay sesion activa. Iniciando login...
    az login
    if %errorlevel% neq 0 (
        echo [ERROR] Login fallido.
        pause
        exit /b 1
    )
)
echo [OK]  Sesion activa.

echo [INFO] Configurando suscripcion: %SUBSCRIPTION%
az account set --subscription "%SUBSCRIPTION%"
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo configurar la suscripcion.
    echo         Verifica el nombre exacto con: az account list -o table
    pause
    exit /b 1
)
for /f "tokens=*" %%A in ('az account show --query name -o tsv 2^>nul') do set ACTIVE_SUB=%%A
echo [OK]  Suscripcion activa: %ACTIVE_SUB%

:: ===============================================================
::  3. RESOURCE GROUP
:: ===============================================================
echo.
echo [3/7] Verificando Resource Group "%RESOURCEGROUP%"...
az group show --name "%RESOURCEGROUP%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Creando Resource Group en %LOCATION%...
    az group create --name "%RESOURCEGROUP%" --location "%LOCATION%"
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el Resource Group.
        pause
        exit /b 1
    )
    echo [OK]  Resource Group creado.
) else (
    echo [OK]  Resource Group ya existe.
)

:: ===============================================================
::  4. APP SERVICE PLAN
:: ===============================================================
echo.
echo [4/7] Verificando App Service Plan "%PLANNAME%"...
az appservice plan show --name "%PLANNAME%" --resource-group "%RESOURCEGROUP%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Creando App Service Plan (%PLANSKU%, Linux)...
    az appservice plan create ^
        --name "%PLANNAME%" ^
        --resource-group "%RESOURCEGROUP%" ^
        --location "%LOCATION%" ^
        --is-linux ^
        --sku "%PLANSKU%"
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el App Service Plan.
        pause
        exit /b 1
    )
    echo [OK]  App Service Plan creado.
) else (
    echo [OK]  App Service Plan ya existe.
)

:: ===============================================================
::  5. WEB APP
:: ===============================================================
echo.
echo [5/7] Verificando Web App "%SITENAME%"...
az webapp show --name "%SITENAME%" --resource-group "%RESOURCEGROUP%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Creando Web App con runtime %RUNTIME%...
    az webapp create ^
        --name "%SITENAME%" ^
        --plan "%PLANNAME%" ^
        --runtime "%RUNTIME%" ^
        --resource-group "%RESOURCEGROUP%"
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear la Web App.
        pause
        exit /b 1
    )
    echo [OK]  Web App creada.
) else (
    echo [OK]  Web App ya existe.
)

:: Configurar startup command y settings de aplicacion
echo [INFO] Aplicando configuracion de la aplicacion...

az webapp config set ^
    --name "%SITENAME%" ^
    --resource-group "%RESOURCEGROUP%" ^
    --startup-file "%STARTUP_CMD%" ^
    >nul

az webapp config appsettings set ^
    --name "%SITENAME%" ^
    --resource-group "%RESOURCEGROUP%" ^
    --settings ^
        SCM_DO_BUILD_DURING_DEPLOYMENT=true ^
        WEBSITES_PORT=8000 ^
        FLASK_ENV=production ^
    >nul

echo [OK]  Configuracion aplicada.

:: ===============================================================
::  6. CREAR PAQUETE DE DESPLIEGUE (ZIP)
:: ===============================================================
echo.
echo [6/7] Creando paquete de despliegue...

:: Limpiar directorios temporales anteriores
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
if exist "%DEPLOY_ZIP%" del /f /q "%DEPLOY_ZIP%"
mkdir "%TEMP_DIR%"

:: Copiar proyecto excluyendo archivos innecesarios
echo [INFO] Copiando archivos del proyecto...
robocopy "%CD%" "%TEMP_DIR%" /E /NFL /NDL /NJH /NJS ^
    /XD .venv venv_desktop instance build __pycache__ .git ^
    /XF log.log *.pyc *.pyo deploy_deskt.bat deploy_azure.bat

:: Comprimir con PowerShell
echo [INFO] Comprimiendo...
powershell -NoProfile -Command "Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath '%DEPLOY_ZIP%' -Force"
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo crear el archivo zip.
    rmdir /s /q "%TEMP_DIR%"
    pause
    exit /b 1
)

:: Limpiar directorio temporal
rmdir /s /q "%TEMP_DIR%"

if not exist "%DEPLOY_ZIP%" (
    echo [ERROR] El archivo zip no fue generado.
    pause
    exit /b 1
)

for /f "tokens=*" %%S in ('powershell -NoProfile -Command "(Get-Item ''%DEPLOY_ZIP%'').length / 1MB ^| ForEach-Object { ''{0:N2} MB'' -f $_ }"') do set ZIP_SIZE=%%S
echo [OK]  Paquete listo: %ZIP_SIZE%

:: ===============================================================
::  7. DESPLEGAR EN AZURE
:: ===============================================================
echo.
echo [7/7] Desplegando en Azure App Service...
echo [INFO] Esto puede tardar varios minutos (Oryx build + pip install)...
echo.

az webapp deploy ^
    --name "%SITENAME%" ^
    --resource-group "%RESOURCEGROUP%" ^
    --src-path "%DEPLOY_ZIP%" ^
    --type zip

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] El despliegue fallo.
    echo [INFO]  Revisa los logs con:
    echo         az webapp log tail --name %SITENAME% --resource-group %RESOURCEGROUP%
    echo.
    del /f /q "%DEPLOY_ZIP%"
    pause
    exit /b 1
)

del /f /q "%DEPLOY_ZIP%"

:: ===============================================================
::  RESULTADO FINAL
:: ===============================================================
echo.
echo ============================================================
echo   [OK]  DESPLIEGUE COMPLETADO EXITOSAMENTE
echo.
echo   URL:  https://%SITENAME%.azurewebsites.net
echo.
echo   Logs: az webapp log tail --name %SITENAME%
echo         --resource-group %RESOURCEGROUP%
echo ============================================================
echo.

set /p OPEN_BROWSER="Abrir en el navegador? [S/N]: "
if /i "%OPEN_BROWSER%"=="S" (
    az webapp browse --name "%SITENAME%" --resource-group "%RESOURCEGROUP%"
)

endlocal
pause
