"""
Асинхронная работа с PostgreSQL
Альтернатива database.py для продакшена
"""

import asyncpg
import asyncio
import os
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

# Глобальный пул соединений PostgreSQL
_db_pool = None

# Доски которые показываются в главной вкладке "Все без спама" (/b/ и /mus/)
ALLOWED_BOARDS_MAIN = ['b', 'mus']

async def get_db_pool():
    """Получить или создать пул соединений PostgreSQL"""
    global _db_pool

    if _db_pool is None:
        # Получить URL из переменных окружения
        database_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/2ch_parser')

        # Парсинг URL для asyncpg
        parsed = urlparse(database_url)

        _db_pool = await asyncpg.create_pool(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/'),
            min_size=5,      # Минимум 5 соединений
            max_size=20,     # Максимум 20 соединений
            command_timeout=60,
            # SSL если в продакшене
            ssl='require' if os.getenv('ENV') == 'production' else False
        )

    return _db_pool

async def init_db():
    """Инициализация базы данных PostgreSQL"""
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        # Создание таблицы
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                thread_id TEXT,
                post_id TEXT,
                filename TEXT,
                original_name TEXT,
                board TEXT,
                thumbnail TEXT,
                width INTEGER,
                height INTEGER,
                duration TEXT,
                size BIGINT,
                found_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')

        # Индексы для производительности
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_found_at ON videos(found_at DESC)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_board ON videos(board)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_url ON videos(url)')

        # Уникальный индекс (предотвращает дубли)
        await conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_url_board ON videos(url, board)')

        # Составные индексы для оптимизации
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_active_found_at ON videos(is_active, found_at DESC)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_board_active_found_at ON videos(board, is_active, found_at DESC)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_active_board ON videos(is_active, board)')

    print("[DB] PostgreSQL база данных готова")

async def add_video(video_data: dict) -> bool:
    """Добавить видео в PostgreSQL"""
    if not video_data or not video_data.get('url'):
        return False

    pool = await get_db_pool()

    try:
        async with pool.acquire() as conn:
            # Используем ON CONFLICT для PostgreSQL (аналог INSERT OR IGNORE)
            result = await conn.fetchval('''
                INSERT INTO videos
                (url, thread_id, post_id, filename, original_name, board, thumbnail, width, height, duration, size)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (url, board) DO NOTHING
                RETURNING id
            ''',
            video_data.get('url'),
            video_data.get('thread_id'),
            video_data.get('post_id'),
            video_data.get('filename'),
            video_data.get('original_name'),
            video_data.get('board'),
            video_data.get('thumbnail'),
            video_data.get('width'),
            video_data.get('height'),
            video_data.get('duration'),
            video_data.get('size')
            )

            return result is not None

    except Exception as e:
        print(f"[DB] Ошибка PostgreSQL: {e}")
        return False

async def get_videos(limit: int = 50, offset: int = 0, board: str = None, show_all: bool = False) -> List[Dict]:
    """Получить видео из PostgreSQL"""
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        if board:
            rows = await conn.fetch('''
                SELECT * FROM videos
                WHERE is_active = TRUE AND board = $1
                ORDER BY found_at DESC
                LIMIT $2 OFFSET $3
            ''', board, limit, offset)
        elif show_all:
            rows = await conn.fetch('''
                SELECT * FROM videos
                WHERE is_active = TRUE
                ORDER BY found_at DESC
                LIMIT $1 OFFSET $2
            ''', limit, offset)
        else:
            # Используем ANY для PostgreSQL вместо IN с подстановками
            rows = await conn.fetch('''
                SELECT * FROM videos
                WHERE is_active = TRUE AND board = ANY($1)
                ORDER BY found_at DESC
                LIMIT $2 OFFSET $3
            ''', ALLOWED_BOARDS_MAIN, limit, offset)

        return [dict(row) for row in rows]

async def get_video_count(board: str = None, show_all: bool = False) -> int:
    """Получить количество видео"""
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        if board:
            count = await conn.fetchval('''
                SELECT COUNT(*) FROM videos
                WHERE is_active = TRUE AND board = $1
            ''', board)
        elif show_all:
            count = await conn.fetchval('''
                SELECT COUNT(*) FROM videos
                WHERE is_active = TRUE
            ''')
        else:
            count = await conn.fetchval('''
                SELECT COUNT(*) FROM videos
                WHERE is_active = TRUE AND board = ANY($1)
            ''', ALLOWED_BOARDS_MAIN)

        return count

async def get_boards_stats() -> List[tuple]:
    """Получить статистику по доскам"""
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT board, COUNT(*) as count
            FROM videos
            WHERE is_active = TRUE
            GROUP BY board
            ORDER BY count DESC
        ''')

        return [(row['board'], row['count']) for row in rows]

async def close_db_pool():
    """Закрыть пул соединений (вызывать при завершении приложения)"""
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None

# Экспорт функций для совместимости
__all__ = ['init_db', 'add_video', 'get_videos', 'get_video_count', 'get_boards_stats', 'close_db_pool']
