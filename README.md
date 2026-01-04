# 🎬 2ch Video Parser

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-%23336791.svg?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Автоматический парсер/граббер видео с имиджборды 2ch.org (2ch.hk). Собирает видео с популярных досок, индексирует по размеру, длительности и другим параметрам. Поддерживает как SQLite (для разработки), так и PostgreSQL (для продакшена).

## ✨ Возможности

- 🚀 **Высокая производительность** - асинхронный парсинг с Gunicorn + Uvicorn
- 📊 **Мониторинг** - Prometheus метрики + Grafana дашборды
- 🐳 **Docker Ready** - полная контейнеризация
- 🔍 **SEO оптимизация** - мета-теги для поисковиков
- 🗄️ **Две БД** - SQLite (простота) или PostgreSQL (масштаб)
- 🌐 **Кэширование** - Nginx + Redis для максимальной скорости
- 🔒 **Безопасность** - HTTPS, заголовки безопасности, rate limiting
- 📱 **Адаптивный дизайн** - работает на всех устройствах
-   **webm grabber/parser**

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   Flask App     │    │   Database      │
│   (Кэширование) │◄──►│   (API)         │◄──►│   (SQLite/PostgreSQL)
│   Port 80/443   │    │   Port 5000     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Redis         │    │   Prometheus     │    │   Grafana       │
│   (Кэш)         │    │   (Метрики)      │    │   (Визуализация) │
│   Port 6379     │    │   Port 9090      │    │   Port 3000      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Установка и запуск

### 🪟 Windows 10/11 (Рекомендуется для начинающих)

#### Вариант 1: Быстрая установка (автоматическая)

```batch
# Скачайте проект
git clone https://github.com/sensejke/2ch-video-parser.git
cd 2ch-video-parser

# Запустите установку (двойной клик или в PowerShell)
install.bat

# Или в PowerShell:
powershell -ExecutionPolicy Bypass -File install.ps1
```

#### Вариант 2: Полная настройка системы

```batch
# Полная настройка (установит все компоненты)
setup.bat

# Или в PowerShell:
powershell -ExecutionPolicy Bypass -File windows-setup.ps1
```

#### Управление приложением

```batch
# Запуск
run.bat

# Статус всех сервисов
run.bat -Status

# Просмотр логов
run.bat -Logs

# Остановка
run.bat -Stop

# Резервное копирование БД
run.bat -Backup
```

**🌐 После установки приложение будет доступно на:**
- **Web интерфейс:** http://localhost:5000
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (admin/admin)

---

### 🐧 Ubuntu 22.04 (для продакшена)

#### Быстрая установка

```bash
# Скачайте и запустите установку
wget https://raw.githubusercontent.com/sensejke/2ch-video-parser/main/install.sh
chmod +x install.sh
sudo ./install.sh
```

#### Полная настройка сервера

```bash
# Полная установка со всеми компонентами
wget https://raw.githubusercontent.com/sensejke/2ch-video-parser/main/ubuntu-setup.sh
chmod +x ubuntu-setup.sh
sudo ./ubuntu-setup.sh

# Следуйте инструкциям скрипта
```

#### Настройка домена (DuckDNS)

```bash
# Настройка бесплатного домена
sudo ./setup-duckdns.sh

# Введите ваш домен и токен с duckdns.org
```

#### Управление

```bash
# Статус сервисов
sudo systemctl status nginx redis postgresql

# Логи приложения
tail -f ~/2ch-video-parser/logs/*.log

# Управление Docker
cd ~/2ch-video-parser
docker-compose ps
docker-compose logs -f app
```

---

### 🐳 Docker (кроссплатформенный)

```bash
# Клонировать репозиторий
git clone https://github.com/sensejke/2ch-video-parser.git
cd 2ch-video-parser

# Запустить с SQLite (разработка)
docker-compose up -d

# Или с PostgreSQL (продакшен)
docker-compose -f docker-compose.postgres.yml up -d

# Проверить работу
curl http://localhost:5000/health
```

### 🐍 Ручная установка (для разработчиков)

```bash
# Требования: Python 3.11+, Docker, Git
pip install -r requirements.txt

# Для разработки (без Docker)
python run_quick.py

# Для продакшена
python run_async.py
```

## ⚡ Требования

### 🪟 Windows 10/11
- **ОС:** Windows 10 версии 2004+ или Windows 11
- **RAM:** Минимум 4GB (рекомендуется 8GB+)
- **Диск:** 5GB свободного места
- **Интернет:** Стабильное подключение для загрузки компонентов

**Автоматически устанавливается:**
- Chocolatey (менеджер пакетов)
- Git
- Python 3.11
- Docker Desktop
- Visual Studio Code (опционально)

### 🐧 Ubuntu 22.04
- **ОС:** Ubuntu 22.04 LTS
- **RAM:** Минимум 2GB (рекомендуется 4GB+)
- **Диск:** 5GB свободного места
- **Пользователь:** с правами sudo

**Автоматически устанавливается:**
- Python 3.11
- Docker & Docker Compose
- Nginx
- Redis
- PostgreSQL (опционально)
- Certbot (для HTTPS)

### 🐳 Docker (все платформы)
- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB RAM
- 5GB дискового пространства

## 📊 API

### Получить видео
```bash
# Все видео
GET /api/videos

# По доске
GET /api/videos?board=b

# С пагинацией
GET /api/videos?page=2&per_page=50
```

### Очистка мертвых ссылок
```bash
POST /api/cleanup
```

### Метрики Prometheus
```bash
GET /metrics
```

## 🗄️ Базы данных

### SQLite (По умолчанию)
- ✅ Нулевые зависимости
- ✅ Файловая БД
- ✅ Отличная производительность до 100K записей
- ✅ Простота резервного копирования

### PostgreSQL (Масштаб)
```bash
# Миграция с SQLite на PostgreSQL
python migrate_to_postgres.py
```

## 🔧 Конфигурация

Создайте `.env` файл:

```env
# База данных
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Окружение
ENV=production

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

## 📈 Мониторинг

### Prometheus метрики
- `http_requests_total` - счетчик запросов
- `http_request_duration_seconds` - время ответа
- `db_queries_total` - запросы к БД
- `memory_usage_bytes` - использование памяти

### Графана дашборд
Автоматически настраивается с Docker Compose.

## 🏭 Деплой

### Ubuntu 22.04 (Рекомендуется)

```bash
# Автоматическая установка
wget https://raw.githubusercontent.com/sensejke/2ch-video-parser/main/ubuntu-setup.sh
chmod +x ubuntu-setup.sh
sudo ./ubuntu-setup.sh
```

### Docker продакшен

```bash
# Сборка и запуск
docker build -t 2ch-parser .
docker run -d -p 5000:5000 --name parser 2ch-parser

# С Nginx прокси
docker run -d --name nginx -p 80:80 nginx:alpine
```

Подробная инструкция: [DEPLOYMENT.md](DEPLOYMENT.md)

## 🔍 SEO и поисковики

Проект оптимизирован для поисковых систем:
- Мета-теги для Google, Yandex
- Структурированные данные
- Быстрая загрузка страниц
- Мобильная адаптация

## 🤝 Contributing

1. Fork проект
2. Создайте ветку (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add AmazingFeature'`)
4. Push в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📝 Лицензия

Распространяется под лицензией MIT. См. `LICENSE` для подробностей.

## 🙏 Автор

**@sensejke** - [Telegram](https://t.me/sensejke)

## 📞 Поддержка

- 💬 Telegram: [@sensejke](https://t.me/sensejke)
---

⭐ Если проект оказался полезным, поставьте звезду!
