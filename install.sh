#!/bin/bash
# Полная установка 2ch Video Parser на Ubuntu 22.04
# Использование: bash install.sh

set -e

echo "🚀 Установка 2ch Video Parser"
echo "============================="

# Проверка root прав
if [[ $EUID -eq 0 ]]; then
   echo "❌ Не запускай скрипт от root! Используй обычного пользователя с sudo."
   exit 1
fi

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка базовых пакетов
echo "🔧 Установка системных пакетов..."
sudo apt install -y curl wget git ufw htop

# Настройка firewall
echo "🔥 Настройка firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Установка Docker
echo "🐳 Установка Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Перезапуск Docker
sudo systemctl restart docker

# Установка Docker Compose
echo "📋 Установка Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Клонирование проекта
echo "📥 Скачивание проекта..."
cd ~
git clone https://github.com/sensejke/2ch-video-parser.git
cd 2ch-video-parser

# Запуск проекта
echo "🚀 Запуск проекта..."
docker-compose up -d

# Ожидание запуска
echo "⏳ Ожидание запуска..."
sleep 10

# Проверка работы
echo "🔍 Проверка работы..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Приложение запущено на http://localhost:5000"
else
    echo "❌ Приложение не запустилось"
fi

echo ""
echo "🎉 Установка завершена!"
echo ""
echo "📋 Что дальше:"
echo "1. Настрой DuckDNS: sudo ./setup-duckdns.sh"
echo "2. Настрой Nginx: см. DEPLOYMENT.md"
echo "3. Получи SSL: sudo certbot --nginx -d yourdomain.duckdns.org"
echo ""
echo "🌐 Твой сайт будет доступен на:"
echo "http://localhost:5000 (локально)"
echo "https://yourdomain.duckdns.org (после настройки)"
