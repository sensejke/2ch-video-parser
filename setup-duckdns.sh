#!/bin/bash
# Настройка DuckDNS для 2ch Video Parser
# Использование: bash setup-duckdns.sh

set -e

echo "🦆 Настройка DuckDNS для 2ch Video Parser"
echo "=========================================="

# Проверка root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Запустите скрипт с sudo: sudo bash setup-duckdns.sh"
   exit 1
fi

# Проверка curl
if ! command -v curl &> /dev/null; then
    echo "📦 Установка curl..."
    apt update && apt install -y curl
fi

# Ввод данных
read -p "Введи домен DuckDNS (без .duckdns.org): " DOMAIN
read -p "Введи токен DuckDNS: " TOKEN

echo "🔧 Настройка..."

# Создание скрипта обновления
cat > /usr/local/bin/update-duckdns.sh << EOF
#!/bin/bash
DOMAIN="$DOMAIN"
TOKEN="$TOKEN"
curl -s "https://www.duckdns.org/update?domains=\$DOMAIN&token=\$TOKEN&ip=" > /dev/null
EOF

chmod +x /usr/local/bin/update-duckdns.sh

# Добавление в cron
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/update-duckdns.sh") | crontab -

# Тестовый запуск
echo "🧪 Тестирование..."
/usr/local/bin/update-duckdns.sh

# Проверка DNS
echo "🔍 Проверка DNS..."
sleep 5
if nslookup "$DOMAIN.duckdns.org" &>/dev/null; then
    echo "✅ DuckDNS настроен успешно!"
    echo "🌐 Домен: https://$DOMAIN.duckdns.org"
    echo "🔄 IP обновляется каждые 5 минут"
else
    echo "⚠️  DNS еще не обновился, подождите несколько минут"
fi

echo ""
echo "📋 Следующие шаги:"
echo "1. Настрой Nginx с доменом $DOMAIN.duckdns.org"
echo "2. Получи SSL сертификат: sudo certbot --nginx -d $DOMAIN.duckdns.org"
echo "3. Запусти приложение: docker-compose up -d"
echo ""
echo "🔗 Скрипт обновления: /usr/local/bin/update-duckdns.sh"
echo "📅 Cron: crontab -l"
