#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый запуск приложения без парсинга
Для тестирования и просмотра интерфейса
"""

import asyncio
import logging
import os
import threading
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from cleanup_videos import cleanup_dead_videos
from database import init_db
from app import app

# Создаем директорию для логов если её нет
os.makedirs('logs', exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/async_parser.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('async_run')

def run_flask():
    """Запуск Flask веб-сервера в отдельном потоке"""
    logger.info("Запуск Flask веб-сервера на http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

async def main():
    """Главная асинхронная функция (без парсинга)"""
    # Инициализируем БД
    await init_db()
    logger.info("База данных готова")
    logger.info("⚠️  Парсинг отключен - запуск в режиме просмотра")

    # Настраиваем планировщик (только очистка мёртвых видео)
    scheduler = AsyncIOScheduler()
    
    # Очистка мёртвых видео каждый день в 3 часа ночи
    scheduler.add_job(
        cleanup_dead_videos,
        trigger=CronTrigger(hour=3, minute=0),
        id='cleanup_job',
        name='Cleanup Dead Videos'
    )

    scheduler.start()
    logger.info(f"Планировщик запущен:")
    logger.info(f"  - Очистка: каждый день в 03:00")
    logger.info(f"  - Парсинг: ОТКЛЮЧЕН")

    # Запускаем Flask веб-сервер в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask веб-сервер запущен")

    # Бесконечный цикл для поддержания работы
    try:
        # Ожидаем завершения (Ctrl+C)
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
        scheduler.shutdown()
        logger.info("Планировщик остановлен")
    except Exception as e:
        logger.error(f"Ошибка в главном цикле: {e}")
        scheduler.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение остановлено")

