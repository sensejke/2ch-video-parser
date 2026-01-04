# 🚀 Руководство по развертыванию

## 🪟 **Windows 10/11 (ЛОКАЛЬНАЯ РАЗРАБОТКА)**

Для локальной разработки и тестирования на Windows используйте автоматические скрипты установки.

### **Быстрая установка на Windows**

```batch
# 1. Клонировать репозиторий
git clone https://github.com/sensejke/2ch-video-parser.git
cd 2ch-video-parser

# 2. Быстрая установка (рекомендуется)
install.bat

# Или в PowerShell:
powershell -ExecutionPolicy Bypass -File install.ps1
```

### **Полная настройка Windows системы**

```batch
# Полная установка со всеми компонентами
setup.bat

# Или в PowerShell:
powershell -ExecutionPolicy Bypass -File windows-setup.ps1
```

### **Управление приложением на Windows**

```batch
# Запуск всех сервисов
run.bat

# Проверка статуса
run.bat -Status

# Просмотр логов
run.bat -Logs

# Остановка
run.bat -Stop

# Резервное копирование базы данных
run.bat -Backup
```

**🌐 Локальные URL после установки:**
- **Приложение:** http://localhost:5000
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (admin/admin)

### **Windows Troubleshooting**

```batch
# Если Docker не запускается
# 1. Перезагрузите компьютер
# 2. Запустите Docker Desktop
# 3. Проверьте: docker --version

# Если приложение не отвечает
run.bat -Logs app

# Переустановка (если проблемы)
run.bat -Stop
docker system prune -a -f
run.bat
```

---

## 🌐 **DuckDNS + Ubuntu 22.04 (БЕСПЛАТНЫЙ ДОМЕН)**

Если у тебя динамический IP (как у большинства), используй **DuckDNS** для бесплатного домена!

**Преимущества:**
- ✅ Бесплатно (навсегда)
- ✅ Домен вида `yourname.duckdns.org`
- ✅ Автоматическое обновление IP
- ✅ HTTPS поддержка

### **Шаг 1: Настройка DuckDNS (БЕСПЛАТНЫЙ ДОМЕН)**

```bash
# 1. Иди на https://www.duckdns.org
# 2. Создай аккаунт (используй Reddit или email)
# 3. Создай домен: "2chparser" или что-то свое
# 4. Скопируй токен (token)

# 5. На сервере Ubuntu 22.04:
sudo apt update
sudo apt install -y curl

# 6. Скачай и запусти скрипт настройки DuckDNS:
wget https://raw.githubusercontent.com/sensejke/2ch-video-parser/main/setup-duckdns.sh
chmod +x setup-duckdns.sh
sudo ./setup-duckdns.sh

# Введи свой домен и токен когда спросят

# 7. Проверь работу:
nslookup 2chparser.duckdns.org
```

### **Шаг 2: Развертывание проекта**

## ⚡ Быстрый деплой с Docker (РЕКОМЕНДУЕТСЯ)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/sensejke/2ch-parser.git
cd 2ch-parser

# 2. Настроить переменные окружения
cp env.example .env
nano .env  # Отредактировать при необходимости

# 3. Запустить с SQLite (разработка)
docker-compose up -d

# Или с PostgreSQL (продакшен)
docker-compose -f docker-compose.postgres.yml up -d

# 4. Проверить статус
docker-compose ps
docker-compose logs -f app
```

**Что включает Docker Compose:**
- ✅ Flask приложение на port 5000
- ✅ Redis кэш на port 6379
- ✅ Prometheus метрики на port 9090
- ✅ Автоматическое восстановление при сбое

---

## 🔧 Ручной деплой на Ubuntu 22.04 (РЕКОМЕНДУЕТСЯ)

### ✅ **Ubuntu 22.04 LTS - ИДЕАЛЬНЫЙ ВЫБОР!**

**Почему Ubuntu 22.04:**
- ✅ LTS версия (поддержка до 2027)
- ✅ Python 3.10+ (можно обновить до 3.11)
- ✅ Современные пакеты в apt
- ✅ Отличная поддержка Docker
- ✅ Стабильная и безопасная

### 📋 **Минимальные требования к серверу:**
- **RAM:** 2GB (4GB+ рекомендуется)
- **CPU:** 1 ядро (2+ для высокой нагрузки)
- **SSD:** 20GB+ (для базы данных)
- **ОС:** Ubuntu 22.04 LTS (x64)

### Требования ПО:
- Python 3.11+ (обновляем с 3.10)
- Systemd (уже есть)
- Nginx (для кэширования)
- Redis (опционально, с graceful degradation)
- PostgreSQL (опционально, SQLite по умолчанию)

### 🚀 **БЫСТРАЯ УСТАНОВКА НА UBUNTU 22.04:**

```bash
# 1. Скачать и запустить скрипт установки
wget https://raw.githubusercontent.com/your-username/2ch-video-parser/main/ubuntu-setup.sh
chmod +x ubuntu-setup.sh
sudo ./ubuntu-setup.sh

# 2. Выбрать тип установки:
#    1) Полная (Docker + все компоненты)
#    2) Минимальная (Python + Nginx + Redis)
#    3) Базовая (только Python)

# 3. Перезагрузить сервер
sudo reboot
```

**Что установит скрипт:**
- ✅ Python 3.11 + pip
- ✅ Nginx с кэшированием
- ✅ Redis (опционально)
- ✅ PostgreSQL (опционально)
- ✅ Docker + Docker Compose (опционально)
- ✅ UFW firewall
- ✅ Пользователь 'parser'
- ✅ Системные обновления

### 🚀 **ПОСЛЕ УСТАНОВКИ UBUNTU - ЗАПУСК ПРИЛОЖЕНИЯ:**

**1. Копирование проекта на сервер**
```bash
# На локальной машине
git clone https://github.com/your-username/2ch-video-parser.git /home/parser/

# Или если используешь Git
ssh parser@your-server-ip
cd /home/parser
git clone https://github.com/your-repo/2ch-parser.git .
```

**2. Настройка виртуального окружения**
```bash
cd /home/parser
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Первый запуск для тестирования**
```bash
# Активировать окружение
source venv/bin/activate

# Тестовый запуск (без парсинга)
python run_quick.py

# В другом терминале проверить
curl http://localhost:5000
```

**4. Настройка Nginx (автоматически)**
```bash
# Скрипт уже настроил Nginx, нужно только добавить конфиг сайта
sudo nano /etc/nginx/sites-available/2ch-parser

# Вставить конфигурацию из раздела "Настроить Nginx с кэшированием"
# (см. ниже в этом файле)

# Активировать сайт
sudo ln -s /etc/nginx/sites-available/2ch-parser /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**5. Настройка SSL (Let's Encrypt)**
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 📋 **АЛЬТЕРНАТИВА: РУЧНАЯ УСТАНОВКА (если скрипт не подошел)**

### Этапы:

**1. Подготовка сервера**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip supervisor nginx redis-server
```

**2. Скопировать код**
```bash
git clone https://github.com/your-username/2ch-video-parser.git /home/parser
cd /home/parser
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Создать Systemd сервис**
```bash
sudo nano /etc/systemd/system/2ch-parser.service
```

Содержимое:
```ini
[Unit]
Description=2ch.org Video Parser
After=network.target

[Service]
Type=simple
User=parser
WorkingDirectory=/home/parser
Environment="PATH=/home/parser/venv/bin"
ExecStart=/home/parser/venv/bin/python3 run_async.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**4. Запустить сервис**
```bash
sudo systemctl daemon-reload
sudo systemctl enable 2ch-parser
sudo systemctl start 2ch-parser
sudo systemctl status 2ch-parser
```

**5. Настроить Nginx с DuckDNS**
```bash
# Замени my2chparser.duckdns.org на свой домен
sudo nano /etc/nginx/sites-available/2ch-parser
```

**Содержимое для DuckDNS:**
```nginx
server {
    listen 80;
    server_name my2chparser.duckdns.org;

    # Логи
    access_log /var/log/nginx/2ch-access.log;
    error_log /var/log/nginx/2ch-error.log;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Таймауты
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

```bash
# Активируй сайт
sudo ln -s /etc/nginx/sites-available/2ch-parser /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**6. Настроить HTTPS (Let's Encrypt)**
```bash
# Установи certbot
sudo apt install -y certbot python3-certbot-nginx

# Получи сертификат (замени домен)
sudo certbot --nginx -d my2chparser.duckdns.org

# Автопродление будет настроено автоматически
```

---

## 🌐 **Альтернатива: Port Forwarding (если есть роутер)**

Если у тебя роутер с поддержкой DDNS:

1. **В роутере:** Настрой DuckDNS
2. **Пробрось порты:** 80 → 80, 443 → 443
3. **На сервере:** Nginx слушает на 80/443
4. **Результат:** `my2chparser.duckdns.org` → твой сервер

---

## 📊 **Проверка развертывания**

```bash
# Проверь домен
nslookup my2chparser.duckdns.org

# Проверь Nginx
curl http://my2chparser.duckdns.org

# Проверь HTTPS
curl https://my2chparser.duckdns.org

# Проверь приложение
curl https://my2chparser.duckdns.org/api/videos
```

---

## 🔧 **Устранение неполадок**

### **DuckDNS не обновляется:**
```bash
# Проверь скрипт
cat /usr/local/bin/update-duckdns.sh

# Запусти вручную
/usr/local/bin/update-duckdns.sh

# Проверь cron
sudo crontab -l
```

### **Сайт не открывается:**
```bash
# Проверь Nginx
sudo nginx -t
sudo systemctl status nginx

# Проверь порт
sudo netstat -tlnp | grep :80

# Проверь firewall
sudo ufw status
```

### **HTTPS не работает:**
```bash
# Проверь сертификат
sudo certbot certificates

# Перевыпусти
sudo certbot --nginx -d my2chparser.duckdns.org
```

---

**Готово!** Теперь у тебя есть бесплатный домен с HTTPS! 🚀

---

## ⚡ **Продвинутый деплой с кэшированием**

Содержимое с кэшированием:
```nginx
# Кэширование для статических файлов
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=static_cache:10m max_size=100m inactive=60m;

server {
    listen 80;
    server_name yourdomain.com;

    # Gzip сжатие
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Кэширование статических файлов
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        proxy_pass http://127.0.0.1:5000;
        proxy_cache static_cache;
        proxy_cache_valid 200 302 1y;
        proxy_cache_valid 404 1m;
        add_header X-Cache-Status $upstream_cache_status;
        expires 1y;
    }

    # Основной прокси
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Кэширование API ответов (короткий)
        proxy_cache static_cache;
        proxy_cache_valid 200 5m;
        proxy_cache_valid 404 1m;
        add_header X-Cache-Status $upstream_cache_status;
    }

    # Метрики без кэширования
    location /metrics {
        auth_basic "Metrics";
        auth_basic_user_file /etc/nginx/htpasswd;
        proxy_pass http://127.0.0.1:5000;
        proxy_cache off;
    }

    # API endpoints без кэширования
    location /api/cleanup {
        proxy_pass http://127.0.0.1:5000;
        proxy_cache off;
    }
}
```

**Создать директорию для кэша:**
```bash
sudo mkdir -p /var/cache/nginx
sudo chown www-data:www-data /var/cache/nginx
```

**6. Настроить CDN (CloudFlare)**
```bash
# 1. Зарегистрироваться на cloudflare.com
# 2. Добавить домен и настроить DNS
# 3. В CloudFlare Dashboard:
#    - SSL/TLS -> Full (Strict)
#    - Caching -> Browser Cache TTL: 4 hours
#    - Speed -> Auto Minify: HTML, CSS, JS
#    - Firewall -> Bot Fight Mode: On

# 4. Добавить заголовки в Nginx для CDN:
sudo nano /etc/nginx/sites-available/2ch-parser

# Добавить в server блок:
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

# 5. Включить сайт
sudo ln -s /etc/nginx/sites-available/2ch-parser /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Для видео файлов (опционально):**
Видео файлы хранятся на 2ch.org, поэтому прямой CDN не применим. Но можно:
- Использовать CloudFlare Workers для proxy видео запросов
- Настроить caching видео в браузере через meta tags
- Использовать service worker для кэширования популярных видео

---

## 🔐 Получить HTTPS сертификат (Certbot + Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

Certbot автоматически обновит конфиг Nginx с SSL.

---

## 📊 Мониторинг после деплоя

### Docker logs
```bash
docker-compose logs -f app
```

### Systemd logs
```bash
sudo journalctl -u 2ch-parser -f
```

### Проверить приложение
```bash
curl http://localhost:5000/api/videos?limit=1
```

### Посмотреть Prometheus метрики
```
http://your-domain.com/metrics
```

---

## 💾 Резервная копия базы данных

**Docker:**
```bash
docker-compose exec app cp videos.db videos.db.backup
```

**Manual:**
```bash
cp /home/parser/videos.db /home/parser/videos.db.$(date +%Y%m%d)
```

---

## 🆘 Решение проблем при деплое

| Проблема | Решение |
|----------|---------|
| `ModuleNotFoundError: No module named 'flask'` | `pip install -r requirements.txt` |
| `Address already in use port 5000` | `lsof -i :5000` и убить процесс |
| Redis не подключается | Нормально, работает с graceful degradation |
| Видео не парсятся | Проверить логи: `docker-compose logs` или `journalctl` |
| Nginx 502 Bad Gateway | Flask упал, проверить `docker-compose logs app` |

---

## ⚡ Оптимизации производительности

### 🚀 **Gunicorn (WSGI сервер)**
- **4 воркера** с Uvicorn (асинхронные)
- **Автоматическое масштабирование** на основе CPU ядер
- **Graceful reload** без простоев

### 🗄️ **База данных - ДВЕ ОПЦИИ:**

#### **SQLite (по умолчанию - для простоты)**
- **Файловая БД** - легко бэкапить и переносить
- **0 зависимостей** - работает везде
- **Отличная производительность** для < 100K записей

#### **PostgreSQL (для масштаба > 1M записей)**
- **Серверная БД** с connection pooling (5-20 соединений)
- **ACID транзакции** - надежность данных
- **Расширенный SQL** - JSON, массивы, полнотекстовый поиск
- **Репликация** - для высокой доступности
- **Миграции Alembic** - управление схемой

**Переход на PostgreSQL:**
```bash
# 1. Установить PostgreSQL
docker-compose -f docker-compose.postgres.yml up -d postgres

# 2. Миграция данных
python migrate_to_postgres.py

# 3. Запуск с PostgreSQL
docker-compose -f docker-compose.postgres.yml up -d app
```

#### **Оптимизации индексов (обе БД):**
- **Составные индексы** для быстрого поиска:
  - `(is_active, found_at DESC)` - сортировка по дате
  - `(board, is_active, found_at DESC)` - фильтрация по доске
  - `(is_active, board)` - статистика по доскам
- **Уникальный индекс** `(url, board)` - предотвращает дубли
- **Не конфликтуют** с обычными индексами!

### 🌐 **Nginx + CDN**
- **Кэширование статических файлов** на 1 год
- **API кэширование** на 5 минут
- **Gzip сжатие** для всех ответов
- **CloudFlare CDN** для глобального распределения
- **Безопасные заголовки** (CSP, XSS protection)

### 📊 **Мониторинг производительности**
- **Prometheus метрики**: запросы, задержки, память, CPU
- **Автоматическое обновление** системных метрик
- **Детальный мониторинг** БД запросов
- **Визуализация** через Grafana

## ✅ Чеклист перед продакшеном

- [ ] Убедиться что `debug=False` в app.py
- [ ] Скопировать `.env.example` → `.env`
- [ ] Отредактировать `.env` для сервера (пути, URL Redis)
- [ ] Обновить пути в `docker-compose.yml` если нужно
- [ ] **Включить rate limiting** в `app.py` для продакшена
- [ ] Тестировать локально перед загрузкой на сервер
- [ ] Убедиться что `videos.db` скопируется на сервер (или новая БД создастся)
- [ ] **Настроить HTTPS через Certbot**
- [ ] **Настроить CloudFlare CDN**
- [ ] **Настроить Nginx с кэшированием**
- [ ] Проверить что парсер запускается и работает
- [ ] Проверить что WEB доступен через браузер
- [ ] Настроить резервные копии БД
- [ ] **Проверить производительность**: `curl http://localhost:5000/metrics`

---

## 🎯 Быстрая проверка перед деплоем

На локальной машине:

```bash
# 1. Убедиться что всё работает
python3 run_async.py

# 2. В отдельном терминале проверить
curl http://localhost:5000
curl http://localhost:5000/api/videos?limit=1

# 3. Проверить Prometheus метрики
curl http://localhost:5000/metrics
```

Если всё работает локально - будет работать и на сервере! ✅

---

## 🐛 **TROUBLESHOOTING ДЛЯ UBUNTU 22.04**

### **После установки Ubuntu:**

| Проблема | Решение |
|----------|---------|
| `python3 --version` показывает 3.10 | `sudo update-alternatives --set python3 /usr/bin/python3.11` |
| `ModuleNotFoundError` после установки | `source venv/bin/activate` - активировать виртуальное окружение |
| Nginx не запускается | `sudo nginx -t` - проверить конфиг, `sudo systemctl status nginx` |
| Redis connection refused | `sudo systemctl status redis-server`, проверить порт 6379 |
| PostgreSQL не подключается | `sudo -u postgres psql`, проверить пользователя и пароль |
| Permission denied | `sudo chown -R parser:parser /home/parser` |

### **Проблемы с приложением:**

| Проблема | Решение |
|----------|---------|
| `Address already in use` | `sudo lsof -i :5000` - найти и убить процесс |
| Приложение падает | Проверить логи: `tail -f /home/parser/logs/*.log` |
| Nginx 502 Bad Gateway | Flask не запустился, проверить `sudo systemctl status parser` |
| Сайт не грузится | Проверить DNS, firewall: `sudo ufw status` |
| SSL сертификат не работает | `sudo certbot certificates` - проверить статус |

### **Мониторинг после запуска:**

```bash
# Статус всех служб
sudo systemctl status nginx redis postgresql

# Логи приложения
tail -f /home/parser/logs/*.log

# Мониторинг ресурсов
htop
df -h  # Диск
free -h  # Память

# Проверка приложения
curl http://localhost:5000/health
curl http://localhost:5000/api/videos?limit=1
```

### **Отладка падающего контейнера:**

```bash
# Посмотреть логи приложения
docker-compose logs app

# Посмотреть последние логи с follow
docker-compose logs -f app

# Зайти в контейнер для отладки
docker-compose exec app bash

# Проверить что внутри контейнера
docker-compose exec app ls -la
docker-compose exec app python --version
docker-compose exec app pip list

# Проверить переменные окружения
docker-compose exec app env

# Запустить приложение вручную для отладки
docker-compose exec app python run_quick.py
```

### **Аварийное восстановление Docker:**

```bash
# Остановить все контейнеры
docker-compose down

# Остановить конфликтующие службы
sudo systemctl stop redis-server nginx postgresql

# Очистить Docker
docker system prune -f

# Перезапустить проект
docker-compose up -d

# Проверить статус
docker-compose ps
docker-compose logs
```

### **Проверка занятых портов:**

```bash
# Установи net-tools если нет netstat
sudo apt install -y net-tools

# Посмотреть что занимает порты (вариант 1 - netstat)
sudo netstat -tulpn | grep :6379
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :80

# Посмотреть что занимает порты (вариант 2 - ss, более современный)
sudo ss -tulpn | grep :6379
sudo ss -tulpn | grep :5000
sudo ss -tulpn | grep :80

# Убить процесс если нужно
sudo kill -9 PID_НОМЕР

# Или остановить службу
sudo systemctl stop redis-server
```

---

## 💰 **СТОИМОСТЬ СЕРВЕРА UBUNTU 22.04**

### **Рекомендуемые тарифы:**

| Провайдер | CPU | RAM | SSD | Цена/мес | Для чего |
|-----------|-----|-----|-----|----------|---------|
| **Hetzner CX11** | 1 | 2GB | 20GB | €4.50 | **⭐ МОЙ ВЫБОР** |
| **DigitalOcean** | 1 | 2GB | 25GB | $12 | Маленький проект |
| **Vultr** | 2 | 4GB | 55GB | $18 | Надежный |
| **Linode** | 2 | 4GB | 50GB | $20 | Enterprise |
| **Contabo** | 4 | 8GB | 200GB | €5 | Много места |

### **Почему Hetzner CX11 (€4.50/мес):**
- ✅ Ubuntu 22.04 LTS предустановлена
- ✅ 20TB трафика (неограниченный!)
- ✅ DDoS защита включена
- ✅ Быстрая сеть в Европу/США
- ✅ Отличная производительность

**Итого:** €54/год для небольшого проекта - **СУПЕР!** 🚀

---

*Создано для комфортного деплоя на Ubuntu 22.04 LTS*
