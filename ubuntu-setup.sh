#!/bin/bash
# Установка 2ch Video Parser на Ubuntu 22.04 LTS
# Запуск: bash ubuntu-setup.sh

set -e

echo "🚀 Установка 2ch Video Parser на Ubuntu 22.04"
echo "==============================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода с цветом
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка Ubuntu версии
check_ubuntu_version() {
    if [[ ! -f /etc/os-release ]]; then
        print_error "Не удалось определить версию ОС"
        exit 1
    fi

    . /etc/os-release
    if [[ "$ID" != "ubuntu" ]] || [[ "${VERSION_ID:0:2}" != "22" ]]; then
        print_warning "Рекомендуется Ubuntu 22.04. Текущая версия: $PRETTY_NAME"
        read -p "Продолжить? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_status "Ubuntu 22.04 обнаружена: $PRETTY_NAME"
    fi
}

# Обновление системы
update_system() {
    print_status "Обновление системы..."
    sudo apt update && sudo apt upgrade -y
    sudo apt autoremove -y
}

# Установка Python 3.11
install_python() {
    print_status "Установка Python 3.11..."

    # Добавление репозитория deadsnakes
    sudo apt install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update

    # Установка Python 3.11
    sudo apt install -y python3.11 python3.11-venv python3.11-dev

    # Установка pip для Python 3.11
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

    # Обновление симлинков
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
    sudo update-alternatives --set python3 /usr/bin/python3.11

    python3 --version
    pip3 --version
}

# Установка системных зависимостей
install_system_deps() {
    print_status "Установка системных зависимостей..."

    # Основные пакеты
    sudo apt install -y \
        build-essential \
        gcc \
        git \
        curl \
        wget \
        htop \
        vim \
        ufw \
        fail2ban \
        unattended-upgrades \
        logrotate

    # Для компиляции Python пакетов
    sudo apt install -y \
        libssl-dev \
        libffi-dev \
        libjpeg-dev \
        libpng-dev \
        zlib1g-dev

    print_status "Системные зависимости установлены"
}

# Установка и настройка Nginx
install_nginx() {
    print_status "Установка и настройка Nginx..."

    sudo apt install -y nginx

    # Создание директории для кэша
    sudo mkdir -p /var/cache/nginx
    sudo chown www-data:www-data /var/cache/nginx

    # Настройка бэкапа дефолтного конфига
    sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

    print_status "Nginx установлен. Настройка DuckDNS..."

# Настройка DuckDNS
read -p "Настроить DuckDNS? (y/N): " setup_duckdns
if [[ $setup_duckdns =~ ^[Yy]$ ]]; then
    read -p "Введи домен DuckDNS (без .duckdns.org): " duck_domain
    read -p "Введи токен DuckDNS: " duck_token

    # Создать скрипт обновления DuckDNS
    cat > /usr/local/bin/update-duckdns.sh << EOF
#!/bin/bash
DOMAIN="$duck_domain"
TOKEN="$duck_token"
curl -s "https://www.duckdns.org/update?domains=\$DOMAIN&token=\$TOKEN&ip=" > /dev/null
EOF

    sudo chmod +x /usr/local/bin/update-duckdns.sh

    # Добавить в cron
    (sudo crontab -l ; echo "*/5 * * * * /usr/local/bin/update-duckdns.sh") | sudo crontab -

    # Тестовый запуск
    /usr/local/bin/update-duckdns.sh

    print_status "DuckDNS настроен: $duck_domain.duckdns.org"
fi

print_status "Nginx и DuckDNS настроены."
}

# Установка Redis (опционально)
install_redis() {
    print_status "Установка Redis..."

    sudo apt install -y redis-server

    # Настройка Redis для запуска
    sudo systemctl enable redis-server
    sudo systemctl start redis-server

    print_status "Redis установлен и запущен"
}

# Установка PostgreSQL (опционально)
install_postgresql() {
    print_status "Установка PostgreSQL..."

    # Добавление репозитория PostgreSQL
    sudo apt install -y postgresql postgresql-contrib

    # Запуск и включение
    sudo systemctl enable postgresql
    sudo systemctl start postgresql

    # Создание пользователя и базы данных
    sudo -u postgres psql -c "CREATE USER parser_user WITH PASSWORD 'change_this_password';"
    sudo -u postgres psql -c "CREATE DATABASE parser_db OWNER parser_user;"

    print_status "PostgreSQL установлен. Пользователь: parser_user, БД: parser_db"
    print_warning "ОБЯЗАТЕЛЬНО измените пароль пользователя parser_user!"
}

# Настройка firewall
setup_firewall() {
    print_status "Настройка UFW firewall..."

    sudo ufw --force enable
    sudo ufw allow ssh
    sudo ufw allow 80
    sudo ufw allow 443

    sudo ufw status
}

# Создание пользователя для приложения
create_app_user() {
    print_status "Создание пользователя для приложения..."

    sudo useradd -m -s /bin/bash parser
    sudo usermod -aG www-data parser

    print_status "Пользователь 'parser' создан"
}

# Установка Docker (опционально)
install_docker() {
    print_status "Установка Docker..."

    # Установка Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    sudo usermod -aG docker parser

    # Установка Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose

    # Запуск Docker
    sudo systemctl enable docker
    sudo systemctl start docker

    print_status "Docker и Docker Compose установлены"
}

# Основная функция
main() {
    check_ubuntu_version

    echo
    read -p "Выберите тип установки:
1) Полная установка (Docker + Nginx + Redis + PostgreSQL)
2) Минимальная установка (Python + Nginx + Redis)
3) Только Python и базовые зависимости
Выбор (1/2/3): " choice

    case $choice in
        1)
            print_status "Выбрана полная установка со всеми компонентами"
            update_system
            install_python
            install_system_deps
            install_nginx
            install_redis
            install_postgresql
            setup_firewall
            create_app_user
            install_docker
            ;;
        2)
            print_status "Выбрана минимальная установка"
            update_system
            install_python
            install_system_deps
            install_nginx
            install_redis
            setup_firewall
            create_app_user
            ;;
        3)
            print_status "Выбрана базовая установка Python"
            update_system
            install_python
            install_system_deps
            setup_firewall
            create_app_user
            ;;
        *)
            print_error "Неверный выбор"
            exit 1
            ;;
    esac

    echo
    print_status "🎉 Установка завершена!"
    echo
    echo "📋 Следующие шаги:"
    echo "1. Перезагрузите сервер: sudo reboot"
    echo "2. Скопируйте проект: scp -r /path/to/project parser@server:/home/parser/"
    echo "3. Настройте приложение согласно DEPLOYMENT.md"
    echo "4. Запустите: cd /home/parser && python run_quick.py"
    echo
    echo "🔗 Полезные команды:"
    echo "- Статус служб: sudo systemctl status nginx redis postgresql"
    echo "- Логи приложения: tail -f /home/parser/logs/*.log"
    echo "- Мониторинг: htop"
    echo
    print_warning "Не забудьте изменить пароли и настроить SSL!"
}

# Запуск скрипта
main "$@"
