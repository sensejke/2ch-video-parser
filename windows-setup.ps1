# Установка 2ch Video Parser на Windows 10
# Запуск: powershell -ExecutionPolicy Bypass -File windows-setup.ps1

param(
    [switch]$SkipChecks,
    [switch]$Minimal,
    [switch]$Full
)

Write-Host "==> Installing 2ch Video Parser on Windows 10" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Functions for colored output
function Write-Success { param($Message) Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

# Проверка Windows версии
function Test-WindowsVersion {
    $osInfo = Get-ComputerInfo
    $version = $osInfo.WindowsVersion
    $build = $osInfo.WindowsBuildLabEx

    Write-Info "Windows версия: $version (Build: $build)"

    if ($version -lt 2004) {
        Write-Warning "Рекомендуется Windows 10 версии 2004 или выше"
        $continue = Read-Host "Продолжить установку? (y/N)"
        if ($continue -ne 'y' -and $continue -ne 'Y') {
            exit 1
        }
    } else {
        Write-Success "Windows 10 совместимая версия обнаружена"
    }
}

# Проверка и включение WSL2
function Install-WSL {
    Write-Info "Проверка WSL2..."

    try {
        $wslVersion = wsl --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "WSL2 уже установлен"
            return
        }
    } catch {
        Write-Info "Установка WSL2..."
    }

    # Включение WSL
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

    # Установка WSL2
    try {
        wsl --install -d Ubuntu-22.04 --no-launch
        Write-Success "WSL2 Ubuntu 22.04 установлен"
        Write-Warning "Перезагрузите компьютер и запустите скрипт заново!"
        exit 0
    } catch {
        Write-Error "Ошибка установки WSL2. Установите вручную через Microsoft Store"
        exit 1
    }
}

# Установка Chocolatey
function Install-Chocolatey {
    Write-Info "Установка Chocolatey..."

    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Success "Chocolatey уже установлен"
        return
    }

    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
        Write-Success "Chocolatey установлен"
    } catch {
        Write-Error "Ошибка установки Chocolatey"
        exit 1
    }
}

# Установка Git
function Install-Git {
    Write-Info "Установка Git..."

    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Success "Git уже установлен"
        return
    }

    try {
        choco install git -y
        Write-Success "Git установлен"
    } catch {
        Write-Error "Ошибка установки Git"
        exit 1
    }
}

# Установка Docker Desktop
function Install-Docker {
    Write-Info "Установка Docker Desktop..."

    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Write-Success "Docker уже установлен"
        return
    }

    try {
        choco install docker-desktop -y
        Write-Success "Docker Desktop установлен"
        Write-Warning "Запустите Docker Desktop и перезагрузите PowerShell"
    } catch {
        Write-Error "Ошибка установки Docker Desktop"
        exit 1
    }
}

# Установка Python 3.11
function Install-Python {
    Write-Info "Установка Python 3.11..."

    if (Get-Command python -ErrorAction SilentlyContinue) {
        $version = python --version 2>$null
        if ($version -match "Python 3.11") {
            Write-Success "Python 3.11 уже установлен"
            return
        }
    }

    try {
        choco install python311 -y
        Write-Success "Python 3.11 установлен"
    } catch {
        Write-Error "Ошибка установки Python"
        exit 1
    }
}

# Установка VS Code (опционально)
function Install-VSCode {
    Write-Info "Установка Visual Studio Code..."

    if (Get-Command code -ErrorAction SilentlyContinue) {
        Write-Success "VS Code уже установлен"
        return
    }

    try {
        choco install vscode -y
        Write-Success "VS Code установлен"
    } catch {
        Write-Warning "Ошибка установки VS Code (опционально)"
    }
}

# Настройка рабочей директории
function Setup-Workspace {
    Write-Info "Настройка рабочей директории..."

    $workspacePath = "$env:USERPROFILE\2ch-video-parser"

    if (Test-Path $workspacePath) {
        Write-Warning "Директория $workspacePath уже существует"
        return
    }

    try {
        New-Item -ItemType Directory -Path $workspacePath -Force | Out-Null
        Set-Location $workspacePath

        # Клонирование проекта
        Write-Info "Клонирование проекта..."
        git clone https://github.com/sensejke/2ch-video-parser.git .

        Write-Success "Рабочая директория настроена: $workspacePath"
    } catch {
        Write-Error "Ошибка настройки рабочей директории"
        exit 1
    }
}

# Создание ярлыков
function Create-Shortcuts {
    Write-Info "Создание ярлыков..."

    $workspacePath = "$env:USERPROFILE\2ch-video-parser"
    $desktopPath = [Environment]::GetFolderPath("Desktop")

    try {
        # Ярлык для запуска
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut("$desktopPath\2ch Parser.lnk")
        $shortcut.TargetPath = "powershell.exe"
        $shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$workspacePath\run.ps1`""
        $shortcut.WorkingDirectory = $workspacePath
        $shortcut.Description = "Запуск 2ch Video Parser"
        $shortcut.Save()

        Write-Success "Ярлык создан на рабочем столе"
    } catch {
        Write-Warning "Ошибка создания ярлыка (опционально)"
    }
}

# Основная функция установки
function Install-Full {
    Write-Info "Запуск полной установки..."

    if (-not $SkipChecks) {
        Test-WindowsVersion
    }

    Install-Chocolatey
    Install-Git
    Install-Python
    Install-Docker
    Install-VSCode

    Setup-Workspace
    Create-Shortcuts

    Write-Host ""
    Write-Success "🎉 Полная установка завершена!"
    Write-Host ""
    Write-Host "📋 Следующие шаги:" -ForegroundColor Cyan
    Write-Host "1. Перезагрузите компьютер" -ForegroundColor White
    Write-Host "2. Запустите Docker Desktop" -ForegroundColor White
    Write-Host "3. Откройте PowerShell и перейдите в папку проекта:" -ForegroundColor White
    Write-Host "   cd ~\2ch-video-parser" -ForegroundColor Yellow
    Write-Host "4. Запустите приложение:" -ForegroundColor White
    Write-Host "   .\run.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🌐 Приложение будет доступно на:" -ForegroundColor Cyan
    Write-Host "http://localhost:5000" -ForegroundColor Green
}

# Минимальная установка
function Install-Minimal {
    Write-Info "Запуск минимальной установки..."

    if (-not $SkipChecks) {
        Test-WindowsVersion
    }

    Install-Chocolatey
    Install-Git
    Install-Python
    Install-Docker

    Setup-Workspace

    Write-Host ""
    Write-Success "🎉 Минимальная установка завершена!"
    Write-Host ""
    Write-Host "📋 Следующие шаги:" -ForegroundColor Cyan
    Write-Host "1. Запустите Docker Desktop" -ForegroundColor White
    Write-Host "2. Откройте PowerShell в папке проекта" -ForegroundColor White
    Write-Host "3. Запустите: .\run.ps1" -ForegroundColor White
}

# Проверка прав администратора
function Test-AdminRights {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Главная функция
function Main {
    # Проверка прав администратора
    if (-not (Test-AdminRights)) {
        Write-Warning "Рекомендуется запускать с правами администратора"
        $continue = Read-Host "Продолжить без прав администратора? (y/N)"
        if ($continue -ne 'y' -and $continue -ne 'Y') {
            Write-Info "Запустите PowerShell от имени администратора и выполните:"
            Write-Host "powershell -ExecutionPolicy Bypass -File $PSCommandPath" -ForegroundColor Yellow
            exit 1
        }
    }

    Write-Host ""
    Write-Host "Выберите тип установки:" -ForegroundColor Cyan
    Write-Host "1) Полная установка (Docker + Python + Git + VS Code)"
    Write-Host "2) Минимальная установка (Docker + Python + Git)"
    Write-Host "3) Только проверка системы"
    Write-Host ""

    if ($Full) {
        $choice = 1
    } elseif ($Minimal) {
        $choice = 2
    } else {
        $choice = Read-Host "Выбор (1/2/3)"
    }

    switch ($choice) {
        1 {
            Write-Info "Выбрана полная установка со всеми компонентами"
            Install-Full
        }
        2 {
            Write-Info "Выбрана минимальная установка"
            Install-Minimal
        }
        3 {
            Write-Info "Проверка системы..."
            Test-WindowsVersion
            Install-WSL
            Write-Success "Проверка завершена"
        }
        default {
            Write-Error "Неверный выбор"
            exit 1
        }
    }
}

# Запуск скрипта
try {
    Main
} catch {
    Write-Error "Критическая ошибка: $($_.Exception.Message)"
    exit 1
}
