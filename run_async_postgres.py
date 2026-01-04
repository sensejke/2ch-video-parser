#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск с PostgreSQL вместо SQLite
"""

import asyncio
import logging
import os
import threading
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from async_parser import AsyncParser2ch
from cleanup_videos import cleanup_dead_videos
from database_postgres import init_db, close_db_pool
from config import UPDATE_INTERVAL
from app_postgres import app

# Создаем директорию для логов если её нет
os.makedirs('logs', exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/postgres_parser.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('async_run_postgres')

def run_flask():
    """Запуск Flask веб-сервера в отдельном потоке"""
    logger.info("Запуск Flask веб-сервера с PostgreSQL на http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

async def run_parser():
    """Асинхронный запуск парсера"""
    logger.info("Запуск парсера с PostgreSQL")

    try:
        async with AsyncParser2ch() as parser:
            count = await parser.run()
            logger.info(f"Парсинг завершён, новых видео: {count}")
    except Exception as e:
        logger.error(f"Ошибка парсинга: {e}")

async def main():
    """Главная асинхронная функция с PostgreSQL"""
    # Инициализируем PostgreSQL
    await init_db()
    logger.info("PostgreSQL готова")

    # Первичный парсинг
    logger.info("Запуск первичного парсинга...")
    await run_parser()

    # Настраиваем планировщик
    scheduler = AsyncIOScheduler()

    # Парсинг каждые N минут
    scheduler.add_job(
        run_parser,
        trigger=IntervalTrigger(minutes=UPDATE_INTERVAL),
        id='parser_job',
        name='2ch Video Parser (PostgreSQL)'
    )

    # Очистка мертвых видео каждый день в 3 часа ночи
    scheduler.add_job(
        cleanup_dead_videos,
        trigger=CronTrigger(hour=3, minute=0),
        id='cleanup_job',
        name='Cleanup Dead Videos (PostgreSQL)'
    )

    scheduler.start()
    logger.info("Планировщик запущен с PostgreSQL:")
    logger.info(f"  - Парсинг: каждые {UPDATE_INTERVAL} минут")
    logger.info("  - Очистка: каждый день в 03:00")

    # Запускаем Flask веб-сервер в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask веб-сервер запущен")

    # Бесконечный цикл для поддержания работы
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
        scheduler.shutdown()
        logger.info("Планировщик остановлен")
        await close_db_pool()
        logger.info("PostgreSQL соединения закрыты")
    except Exception as e:
        logger.error(f"Ошибка в главном цикле: {e}")
        scheduler.shutdown()
        await close_db_pool()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение остановлено")
