# Quick installation of 2ch Video Parser on Windows 10
# Usage: powershell -ExecutionPolicy Bypass -File install.ps1

Write-Host "==> Quick installation of 2ch Video Parser" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Functions for colored output
function Write-Success { param($Message) Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

# Проверка администраторских прав
function Test-AdminRights {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
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
    } catch {
        Write-Error "Ошибка установки Docker Desktop"
        exit 1
    }
}

# Клонирование и настройка проекта
function Setup-Project {
    Write-Info "Настройка проекта..."

    $projectPath = "$env:USERPROFILE\2ch-video-parser"

    # Создание директории
    if (-not (Test-Path $projectPath)) {
        New-Item -ItemType Directory -Path $projectPath -Force | Out-Null
    }

    Set-Location $projectPath

    # Клонирование проекта
    if (-not (Test-Path ".git")) {
        Write-Info "Клонирование проекта..."
        git clone https://github.com/sensejke/2ch-video-parser.git .
    } else {
        Write-Info "Обновление проекта..."
        git pull
    }

    Write-Success "Проект настроен в: $projectPath"
}

# Запуск проекта
function Start-Project {
    Write-Info "Запуск проекта..."

    try {
        # Проверка Docker
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Docker не запущен. Запустите Docker Desktop и повторите попытку."
            exit 1
        }

        # Запуск через Docker Compose
        Write-Info "Запуск контейнеров..."
        docker-compose up -d

        # Ожидание запуска
        Write-Info "Ожидание запуска..."
        Start-Sleep -Seconds 15

        # Проверка работы
        Write-Info "Проверка работы..."
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Success "Приложение запущено на http://localhost:5000"
            } else {
                Write-Warning "Приложение запустилось, но вернуло статус $($response.StatusCode)"
            }
        } catch {
            Write-Error "Приложение не отвечает на http://localhost:5000/health"
            Write-Info "Проверьте логи: docker-compose logs app"
        }

    } catch {
        Write-Error "Ошибка запуска проекта: $($_.Exception.Message)"
        exit 1
    }
}

# Создание ярлыков
function Create-Shortcuts {
    Write-Info "Создание ярлыков..."

    $projectPath = "$env:USERPROFILE\2ch-video-parser"
    $desktopPath = [Environment]::GetFolderPath("Desktop")

    try {
        # Ярлык для запуска
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut("$desktopPath\2ch Parser.lnk")
        $shortcut.TargetPath = "powershell.exe"
        $shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$projectPath\run.ps1`""
        $shortcut.WorkingDirectory = $projectPath
        $shortcut.Description = "Запуск 2ch Video Parser"
        $shortcut.Save()

        # Ярлык для остановки
        $stopShortcut = $shell.CreateShortcut("$desktopPath\Stop 2ch Parser.lnk")
        $stopShortcut.TargetPath = "powershell.exe"
        $stopShortcut.Arguments = "-ExecutionPolicy Bypass -Command `"docker-compose -f '$projectPath\docker-compose.yml' down`""
        $stopShortcut.WorkingDirectory = $projectPath
        $stopShortcut.Description = "Остановка 2ch Video Parser"
        $stopShortcut.Save()

        Write-Success "Ярлыки созданы на рабочем столе"
    } catch {
        Write-Warning "Ошибка создания ярлыков (опционально)"
    }
}

# Основная функция
function Main {
    try {
        # Проверка прав администратора
        if (-not (Test-AdminRights)) {
            Write-Warning "Для полной установки нужны права администратора"
            $continue = Read-Host "Продолжить без прав администратора? (y/N)"
            if ($continue -ne 'y' -and $continue -ne 'Y') {
                Write-Info "Запустите PowerShell от имени администратора"
                exit 1
            }
        }

        # Установка компонентов
        Install-Chocolatey
        Install-Git
        Install-Docker
        Setup-Project

        # Обновление переменных среды
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

        # Создание ярлыков
        Create-Shortcuts

        # Запуск проекта
        Start-Project

        Write-Host ""
        Write-Success "🎉 Установка завершена!"
        Write-Host ""
        Write-Host "📋 Что дальше:" -ForegroundColor Cyan
        Write-Host "1. Приложение запущено на: http://localhost:5000" -ForegroundColor Green
        Write-Host "2. Ярлыки созданы на рабочем столе" -ForegroundColor White
        Write-Host "3. Для остановки: docker-compose down" -ForegroundColor White
        Write-Host "4. Для просмотра логов: docker-compose logs -f app" -ForegroundColor White
        Write-Host ""
        Write-Host "🔧 Управление:" -ForegroundColor Cyan
        Write-Host "- Перезапуск: docker-compose restart" -ForegroundColor White
        Write-Host "- Обновление: docker-compose pull && docker-compose up -d" -ForegroundColor White
        Write-Host "- Резервное копирование: docker-compose exec app sqlite3 /app/videos.db .dump > backup.sql" -ForegroundColor White

    } catch {
        Write-Error "Критическая ошибка установки: $($_.Exception.Message)"
        Write-Info "Проверьте логи и повторите установку"
        exit 1
    }
}

# Запуск скрипта
Main
