#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Функция для проверки живых видео и очистки мёртвых ссылок
"""

import aiohttp
import aiosqlite
import asyncio
import logging
from config import DATABASE_PATH
from database import DB_LOCK


logger = logging.getLogger('cleanup_videos')

async def check_video_alive(session: aiohttp.ClientSession, url: str):
    """Проверяет доступность видео по HEAD-запросу"""
    try:
        async with session.head(url, timeout=5) as resp:
            status = resp.status
            is_alive = 200 <= status < 400
            logger.debug(f"[CHECK_ALIVE] URL: {url}, Status: {status}, Alive: {is_alive}")
            return is_alive
    except Exception as e:
        logger.debug(f"[CHECK_ALIVE] URL: {url}, Error: {e}, Alive: False")
        return False

async def cleanup_dead_videos(board=None):
    """Помечает неактивные видео (404/410/5xx) как is_active=0"""
    try:
        async with DB_LOCK:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                # Получаем все активные видео
                if board:
                    query = 'SELECT id, url FROM videos WHERE is_active = 1 AND board = ?'
                    cursor = await db.execute(query, (board,))
                else:
                    query = 'SELECT id, url FROM videos WHERE is_active = 1'
                    cursor = await db.execute(query)

                videos = await cursor.fetchall()

                if not videos:
                    logger.info("Нет активных видео для проверки")
                    return 0

                logger.info(f"Проверяем {len(videos)} видео...")

                dead_count = 0
                async with aiohttp.ClientSession() as session:
                    for video_id, url in videos:
                        is_alive = await check_video_alive(session, url)

                        if not is_alive:
                            # Помечаем как неактивное
                            await db.execute(
                                'UPDATE videos SET is_active = 0 WHERE id = ?',
                                (video_id,)
                            )
                            dead_count += 1
                            logger.debug(f"Помечено как мёртвое: {url}")

                        # Небольшая задержка чтобы не перегружать сервер
                        await asyncio.sleep(0.1)

                    await db.commit()

            logger.info(f"✅ Очистка завершена: помечено мёртвых видео: {dead_count}")
            print(f"[CLEANUP] Проверено: {len(videos)}, удалено мёртвых видео: {dead_count}")

            return dead_count

    except Exception as e:
        logger.error(f"Ошибка при очистке видео: {e}")
        return 0

if __name__ == "__main__":
    # Для тестирования
    logging.basicConfig(level=logging.DEBUG)
    
    # Проверяем видео со всех досок
    count = asyncio.run(cleanup_dead_videos())
    print(f"\nПомечено мёртвых видео: {count}")
