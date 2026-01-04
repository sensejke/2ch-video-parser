# Используем Python 3.11 slim образ
FROM python:3.11-slim

# Устанавливаем системные зависимости и локали для Windows совместимости
RUN apt-get update && apt-get install -y \
    gcc \
    locales \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

# Устанавливаем UTF-8 локаль
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Создаем рабочую директорию
WORKDIR /app

# Копируем и устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем директории для логов и кэша
RUN mkdir -p logs cache

# Создаем директории и пустой файл базы данных
RUN mkdir -p logs cache && touch videos.db

# Открываем порты
EXPOSE 5000

# Запускаем приложение через Gunicorn в продакшене
CMD ["sh", "-c", "if [ \"$ENV\" = \"production\" ]; then gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class uvicorn.workers.UvicornWorker app:app; else python run_async.py; fi"]
