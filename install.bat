@echo off
REM Быстрая установка 2ch Video Parser
REM Использование: install.bat

echo 🚀 Быстрая установка 2ch Video Parser
echo ====================================
echo.

REM Проверка PowerShell
powershell -Command "Write-Host '✅ PowerShell доступен'" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ PowerShell не найден. Установите Windows Management Framework.
    echo Скачать: https://www.microsoft.com/en-us/download/details.aspx?id=54616
    pause
    exit /b 1
)

REM Запуск PowerShell скрипта
powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1"

REM Пауза для просмотра результата
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
