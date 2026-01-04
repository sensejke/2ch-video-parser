@echo off
REM Запуск 2ch Video Parser
REM Использование: run.bat [команда]

echo 🚀 2ch Video Parser
echo ===================
echo.

REM Проверка PowerShell
powershell -Command "Write-Host 'PowerShell OK' -ForegroundColor Green" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ PowerShell не найден.
    pause
    exit /b 1
)

REM Запуск PowerShell скрипта с передачей параметров
powershell -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*

REM Если нет параметров, пауза для просмотра
if "%1"=="" (
    echo.
    echo Нажмите любую клавишу для выхода...
    pause >nul
)
