# 🪟 2ch Video Parser - Windows установка

Простая установка и запуск на Windows 10/11.

## 🚀 Быстрый старт (3 шага)

### Шаг 1: Скачать проект
```batch
git clone https://github.com/sensejke/2ch-video-parser.git
cd 2ch-video-parser
```

### Шаг 2: Установить (автоматически)
```batch
# Двойной клик по файлу:
install.bat

# Или в PowerShell:
powershell -ExecutionPolicy Bypass -File install.ps1
```

### Шаг 3: Запустить
```batch
# Двойной клик по файлу:
run.bat

# Или в PowerShell:
.\run.ps1
```

**Готово!** Откройте http://localhost:5000

---

## 📋 Что делает установщик

Автоматически устанавливает:
- ✅ Chocolatey (менеджер пакетов)
- ✅ Git (система контроля версий)
- ✅ Python 3.11 (для разработки)
- ✅ Docker Desktop (контейнеризация)
- ✅ Проект и зависимости

---

## 🎮 Управление приложением

| Команда | Что делает |
|---------|------------|
| `run.bat` | Запустить все сервисы |
| `run.bat -Status` | Проверить статус сервисов |
| `run.bat -Logs` | Посмотреть логи |
| `run.bat -Stop` | Остановить все сервисы |
| `run.bat -Backup` | Сделать бэкап базы данных |

---

## 🌐 Доступ к сервисам

После запуска откройте в браузере:

- **🎬 Приложение:** http://localhost:5000
- **📊 Prometheus:** http://localhost:9090
- **📈 Grafana:** http://localhost:3000 (admin/admin)

---

## 🔧 Расширенная настройка

### Полная установка системы
```batch
# Установит дополнительные компоненты
setup.bat

# Включает:
# - Visual Studio Code
# - Дополнительные инструменты разработки
```

### Ручная установка компонентов
```batch
# 1. Установить Chocolatey
# https://chocolatey.org/install

# 2. Установить Git
choco install git -y

# 3. Установить Python
choco install python311 -y

# 4. Установить Docker Desktop
choco install docker-desktop -y

# 5. Запустить проект
run.bat
```

---

## 🐛 Проблемы и решения

### Docker не запускается
```batch
# Перезагрузите компьютер
# Запустите Docker Desktop
# Проверьте: docker --version
```

### Приложение не открывается
```batch
# Проверьте статус
run.bat -Status

# Посмотрите логи
run.bat -Logs

# Перезапустите
run.bat -Restart
```

### Порт 5000 занят
```batch
# Найти процесс
netstat -ano | findstr :5000

# Убить процесс (PID из предыдущей команды)
taskkill /PID <PID> /F
```

---

## 📁 Структура проекта

```
2ch-video-parser/
├── videos.db          # База данных SQLite
├── logs/             # Логи приложения
├── cache/            # Кэш файлов
├── run.bat           # Запуск (Windows)
├── run.ps1           # Запуск (PowerShell)
├── install.bat       # Установка (Windows)
├── install.ps1       # Установка (PowerShell)
└── docker-compose.yml # Конфигурация сервисов
```

---

## 🔄 Обновление

```batch
# Остановить
run.bat -Stop

# Обновить код
git pull

# Обновить контейнеры
run.bat -Update

# Запустить
run.bat
```

---

## 🆘 Помощь

1. **Проверьте логи:** `run.bat -Logs`
2. **Статус сервисов:** `run.bat -Status`
3. **Перезапуск:** `run.bat -Restart`
4. **Создайте Issue** на GitHub с логами ошибки

---

## 📊 Мониторинг

- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (admin/admin)
- **Метрики приложения:** http://localhost:5000/metrics

---

## 🎯 Для разработчиков

```batch
# Установка зависимостей вручную
pip install -r requirements.txt

# Запуск без Docker (разработка)
python run_quick.py

# С отладкой
python -m debug run_async.py
```

---

*Наслаждайтесь парсингом видео с 2ch! 🚀*
