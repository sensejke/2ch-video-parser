# Start 2ch Video Parser on Windows
# Usage: .\run.ps1

param(
    [switch]$Stop,
    [switch]$Restart,
    [switch]$Logs,
    [switch]$Status,
    [switch]$Backup,
    [switch]$Update
)

# Functions for colored output
function Write-Success { param($Message) Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

# Check Docker
function Test-Docker {
    try {
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Docker not running. Start Docker Desktop."
            exit 1
        }
    } catch {
        Write-Error "Docker not installed or not running."
        Write-Info "Install Docker Desktop from https://www.docker.com/products/docker-desktop"
        exit 1
    }
}

# Определение docker-compose файла
function Get-DockerComposeFile {
    # Определяем ОС
    $os = $PSVersionTable.Platform
    if ($os -eq "Win32NT" -or $null -eq $os) {
        # Windows
        if (Test-Path "docker-compose.windows.yml") {
            return "docker-compose.windows.yml"
        }
    }

    # По умолчанию используем стандартный файл
    return "docker-compose.yml"
}

# Проверка docker-compose файла
function Test-DockerCompose {
    $composeFile = Get-DockerComposeFile
    if (-not (Test-Path $composeFile)) {
        Write-Error "Файл $composeFile не найден в текущей директории"
        Write-Info "Убедитесь, что вы находитесь в корневой папке проекта"
        exit 1
    }
}

# Запуск проекта
function Start-Project {
    Write-Info "Запуск 2ch Video Parser..."

    Test-Docker
    Test-DockerCompose
    $composeFile = Get-DockerComposeFile

    try {
        docker-compose -f $composeFile up -d

        Write-Info "Ожидание запуска..."
        Start-Sleep -Seconds 10

        # Проверка работы
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Success "Приложение запущено!"
                Write-Host ""
                Write-Host "🌐 Доступно по адресу:" -ForegroundColor Cyan
                Write-Host "http://localhost:5000" -ForegroundColor Green
                Write-Host ""
                Write-Host "📊 Мониторинг:" -ForegroundColor Cyan
                Write-Host "http://localhost:9090 - Prometheus" -ForegroundColor White
                Write-Host "http://localhost:3000 - Grafana (admin/admin)" -ForegroundColor White
            } else {
                Write-Warning "Приложение запустилось, но вернуло статус $($response.StatusCode)"
            }
        } catch {
            Write-Error "Приложение не отвечает. Проверьте логи: .\run.ps1 -Logs"
        }

    } catch {
        Write-Error "Ошибка запуска: $($_.Exception.Message)"
        exit 1
    }
}

# Остановка проекта
function Stop-Project {
    Write-Info "Остановка 2ch Video Parser..."

    Test-DockerCompose
    $composeFile = Get-DockerComposeFile

    try {
        docker-compose -f $composeFile down
        Write-Success "Приложение остановлено"
    } catch {
        Write-Error "Ошибка остановки: $($_.Exception.Message)"
        exit 1
    }
}

# Перезапуск проекта
function Restart-Project {
    Write-Info "Перезапуск 2ch Video Parser..."

    Stop-Project
    Start-Sleep -Seconds 2
    Start-Project
}

# Просмотр логов
function Show-Logs {
    param([string]$Service = "app")

    Write-Info "Просмотр логов ($Service)..."

    Test-DockerCompose
    $composeFile = Get-DockerComposeFile

    try {
        if ($Service -eq "all") {
            docker-compose -f $composeFile logs -f
        } else {
            docker-compose -f $composeFile logs -f $Service
        }
    } catch {
        Write-Error "Ошибка просмотра логов: $($_.Exception.Message)"
        exit 1
    }
}

# Статус проекта
function Get-Status {
    Write-Info "Статус 2ch Video Parser..."

    Test-DockerCompose
    $composeFile = Get-DockerComposeFile

    try {
        docker-compose -f $composeFile ps

        Write-Host ""
        Write-Host "📊 Детальная информация:" -ForegroundColor Cyan

        # Проверка портов
        $ports = @(
            @{Name="Web App"; Port=5000; Url="http://localhost:5000/health"},
            @{Name="Prometheus"; Port=9090; Url="http://localhost:9090"},
            @{Name="Grafana"; Port=3000; Url="http://localhost:3000"},
            @{Name="Redis"; Port=6379; Url=$null}
        )

        foreach ($service in $ports) {
            $portOpen = Test-NetConnection -ComputerName localhost -Port $service.Port -WarningAction SilentlyContinue
            if ($portOpen.TcpTestSucceeded) {
                Write-Host "$($service.Name): ✅ Порт $($service.Port) открыт" -ForegroundColor Green
                if ($service.Url) {
                    try {
                        $response = Invoke-WebRequest -Uri $service.Url -TimeoutSec 2
                        Write-Host "  └─ Сервис отвечает" -ForegroundColor Green
                    } catch {
                        Write-Host "  └─ Сервис не отвечает" -ForegroundColor Yellow
                    }
                }
            } else {
                Write-Host "$($service.Name): ❌ Порт $($service.Port) закрыт" -ForegroundColor Red
            }
        }

    } catch {
        Write-Error "Ошибка получения статуса: $($_.Exception.Message)"
        exit 1
    }
}

# Резервное копирование базы данных
function Backup-Database {
    Write-Info "Создание резервной копии базы данных..."

    Test-DockerCompose
    $composeFile = Get-DockerComposeFile
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $backupFile = "backup_$timestamp.sql"

    try {
        docker-compose -f $composeFile exec -T app sqlite3 /app/videos.db .dump > $backupFile
        Write-Success "Резервная копия создана: $backupFile"

        # Сжатие
        try {
            Compress-Archive -Path $backupFile -DestinationPath "$backupFile.zip" -Force
            Remove-Item $backupFile
            Write-Success "Архив создан: $backupFile.zip"
        } catch {
            Write-Warning "Ошибка создания архива, оставлен файл $backupFile"
        }

    } catch {
        Write-Error "Ошибка резервного копирования: $($_.Exception.Message)"
        exit 1
    }
}

# Обновление проекта
function Update-Project {
    Write-Info "Обновление 2ch Video Parser..."

    Test-DockerCompose
    $composeFile = Get-DockerComposeFile

    try {
        # Остановка
        Stop-Project

        # Обновление кода
        Write-Info "Обновление репозитория..."
        git pull

        # Обновление образов
        Write-Info "Обновление Docker образов..."
        docker-compose -f $composeFile pull

        # Запуск
        Start-Project

        Write-Success "Проект обновлен"

    } catch {
        Write-Error "Ошибка обновления: $($_.Exception.Message)"
        exit 1
    }
}

# Показать справку
function Show-Help {
    Write-Host "🚀 2ch Video Parser - управление проектом" -ForegroundColor Green
    Write-Host ""
    Write-Host "Использование:" -ForegroundColor Cyan
    Write-Host "  .\run.ps1 [команда]" -ForegroundColor White
    Write-Host ""
    Write-Host "Команды:" -ForegroundColor Cyan
    Write-Host "  (без параметров)  - Запуск проекта" -ForegroundColor White
    Write-Host "  -Stop             - Остановка проекта" -ForegroundColor White
    Write-Host "  -Restart          - Перезапуск проекта" -ForegroundColor White
    Write-Host "  -Status           - Показать статус всех сервисов" -ForegroundColor White
    Write-Host "  -Logs             - Просмотр логов приложения" -ForegroundColor White
    Write-Host "  -Logs app         - Логи приложения" -ForegroundColor White
    Write-Host "  -Logs prometheus  - Логи Prometheus" -ForegroundColor White
    Write-Host "  -Logs grafana     - Логи Grafana" -ForegroundColor White
    Write-Host "  -Logs all         - Логи всех сервисов" -ForegroundColor White
    Write-Host "  -Backup           - Резервное копирование БД" -ForegroundColor White
    Write-Host "  -Update           - Обновление проекта" -ForegroundColor White
    Write-Host ""
    Write-Host "Примеры:" -ForegroundColor Cyan
    Write-Host "  .\run.ps1                    # Запуск" -ForegroundColor White
    Write-Host "  .\run.ps1 -Status            # Статус" -ForegroundColor White
    Write-Host "  .\run.ps1 -Logs -Service app # Логи приложения" -ForegroundColor White
    Write-Host "  .\run.ps1 -Backup            # Бэкап БД" -ForegroundColor White
}

# Главная функция
function Main {
    # Если нет параметров - запускаем проект
    if ($PSBoundParameters.Count -eq 0) {
        Start-Project
        return
    }

    # Обработка параметров
    if ($Stop) {
        Stop-Project
    } elseif ($Restart) {
        Restart-Project
    } elseif ($Status) {
        Get-Status
    } elseif ($Backup) {
        Backup-Database
    } elseif ($Update) {
        Update-Project
    } elseif ($Logs) {
        Show-Logs
    } else {
        Show-Help
    }
}

# Запуск скрипта
try {
    Main
} catch {
    Write-Error "Критическая ошибка: $($_.Exception.Message)"
    exit 1
}
