@echo off
REM Полная настройка системы для 2ch Video Parser
REM Использование: setup.bat

echo 🚀 Полная настройка системы для 2ch Video Parser
echo ================================================
echo.

REM Проверка прав администратора
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Для настройки нужны права администратора
    echo Запустите командную строку от имени администратора
    echo или PowerShell: Start-Process cmd -Verb RunAs
    pause
    exit /b 1
)

REM Проверка PowerShell
powershell -Command "Write-Host 'PowerShell OK' -ForegroundColor Green" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ PowerShell не найден. Установите Windows Management Framework.
    echo Скачать: https://www.microsoft.com/en-us/download/details.aspx?id=54616
    pause
    exit /b 1
)

echo Выберите тип установки:
echo 1) Полная установка (все компоненты)
echo 2) Минимальная установка (Docker + Python)
echo 3) Только проверка системы
echo.

set /p choice="Выбор (1/2/3): "

if "%choice%"=="1" (
    powershell -ExecutionPolicy Bypass -File "%~dp0windows-setup.ps1" -Full
) else if "%choice%"=="2" (
    powershell -ExecutionPolicy Bypass -File "%~dp0windows-setup.ps1" -Minimal
) else if "%choice%"=="3" (
    powershell -ExecutionPolicy Bypass -File "%~dp0windows-setup.ps1" -SkipChecks
) else (
    echo ❌ Неверный выбор
    pause
    exit /b 1
)

echo.
echo Нажмите любую клавишу для выхода...
pause >nul
