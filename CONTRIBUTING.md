# 🤝 Contributing to 2ch Video Parser

Спасибо за интерес к проекту! Вот как вы можете помочь:

## 🚀 Быстрый старт

1. **Fork** проект на [GitHub](https://github.com/sensejke/2ch-video-parser)
2. **Clone** ваш форк: `git clone https://github.com/sensejke/2ch-video-parser.git`
3. **Создайте ветку**: `git checkout -b feature/AmazingFeature`
4. **Установите зависимости**: `pip install -r requirements.txt`
5. **Запустите тесты**: `python run_quick.py`

## 🐛 Сообщение о багах

Используйте [GitHub Issues](https://github.com/sensejke/2ch-video-parser/issues) для:

- 🐛 **Баги**: детальное описание проблемы
- 💡 **Фичи**: предложения по улучшению
- ❓ **Вопросы**: помощь с установкой/использованием

### Формат баг-репорта:
```markdown
**Ожидаемое поведение:**
Что должно происходить

**Фактическое поведение:**
Что происходит вместо этого

**Шаги для воспроизведения:**
1. Шаг 1
2. Шаг 2
3. Шаг 3

**Окружение:**
- OS: Ubuntu 22.04
- Python: 3.11
- Docker: Да/Нет
```

## 🔧 Разработка

### Структура проекта:
```
├── app.py                 # Основное Flask приложение
├── database.py            # Работа с SQLite
├── async_parser.py        # Асинхронный парсер
├── templates/             # HTML шаблоны
├── static/               # Статические файлы
├── docker-compose.yml     # Docker конфигурация
└── DEPLOYMENT.md         # Инструкции по деплою
```

### Стиль кода:
- **PEP 8** для Python
- **Google Style** для комментариев
- **Асинхронность** везде где возможно
- **Обработка ошибок** в каждом компоненте

### Тестирование:
```bash
# Локальный запуск
python run_quick.py

# Проверка API
curl http://localhost:5000/api/videos

# Просмотр логов
tail -f logs/async_parser.log
```

## 📝 Pull Requests

### Процесс:
1. **Обновите** вашу ветку с main: `git pull origin main`
2. **Создайте PR** с понятным названием
3. **Опишите** изменения в PR
4. **Дождитесь** ревью и исправьте замечания

### Требования к PR:
- ✅ **Тестирование**: проверено локально
- ✅ **Документация**: обновлен README если нужно
- ✅ **Совместимость**: работает с существующими функциями
- ✅ **Безопасность**: нет уязвимостей

## 🎯 Roadmap

### Ближайшие планы:
- [ ] **Тесты** (pytest)
- [ ] **CI/CD** (GitHub Actions)
- [ ] **API документация** (Swagger)
- [ ] **Многоязычность** (i18n)
- [ ] **Кэширование** Redis кластер

### Идеи для контрибьютинга:
- 🔍 **Поиск по видео** (по названию, тегам)
- 📊 **Статистика** по доскам и трендам
- 🎨 **Темы оформления**
- 📱 **PWA** (Progressive Web App)
- 🔄 **Webhook уведомления**

## 📞 Контакты

- **Автор**: @sensejke
- **Telegram**: [@sensejke](https://t.me/sensejke)
- **Issues**: [GitHub Issues](https://github.com/sensejke/2ch-video-parser/issues)

## 📜 Лицензия

Contributing to this project means you agree to the [MIT License](LICENSE).

---

**Спасибо за вклад в проект!** 🎉
