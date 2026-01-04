#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import os
import threading
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from async_parser import AsyncParser2ch
from cleanup_videos import cleanup_dead_videos
from database import init_db
from config import UPDATE_INTERVAL
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

async def run_parser():
    """Асинхронный запуск парсера"""
    logger.info("Автоматический запуск асинхронного парсинга")

    try:
        async with AsyncParser2ch() as parser:
            count = await parser.run()
            logger.info(f"Парсинг завершён, новых видео: {count}")
    except Exception as e:
        logger.error(f"Ошибка в автоматическом парсинге: {e}")

async def main():
    """Главная асинхронная функция"""
    # Инициализируем БД
    try:
        await init_db()
        logger.info("База данных готова")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        # Создаем пустой файл БД если не удалось инициализировать
        import os
        db_path = "videos.db"
        if not os.path.exists(db_path):
            open(db_path, 'w').close()
            logger.info("Создан пустой файл базы данных")
        raise  # Перезапускаем контейнер

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
        name='2ch Video Parser'
    )
    
    # Очистка мёртвых видео каждый день в 3 часа ночи
    scheduler.add_job(
        cleanup_dead_videos,
        trigger=CronTrigger(hour=3, minute=0),
        id='cleanup_job',
        name='Cleanup Dead Videos'
    )

    scheduler.start()
    logger.info(f"Планировщик запущен:")
    logger.info(f"  - Парсинг: каждые {UPDATE_INTERVAL} минут")
    logger.info(f"  - Очистка: каждый день в 03:00")

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

