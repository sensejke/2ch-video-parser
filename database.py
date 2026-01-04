import aiosqlite
import asyncio

# Глобальная блокировка для доступа к базе данных
DB_LOCK = asyncio.Lock()
from config import DATABASE_PATH

# Доски которые показываются в главной вкладке "Все без спама" (/b/ и /mus/)
ALLOWED_BOARDS_MAIN = ['b', 'mus']

async def init_db():
    async with DB_LOCK:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    size INTEGER,
                    found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Обычные индексы
            await db.execute('CREATE INDEX IF NOT EXISTS idx_found_at ON videos(found_at DESC)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_board ON videos(board)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_url ON videos(url)')

            # Уникальный индекс (не конфликтует с обычными)
            await db.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_url_board ON videos(url, board)')

            # Составные индексы для оптимизации запросов (НЕ КОНФЛИКТУЮТ!)
            await db.execute('CREATE INDEX IF NOT EXISTS idx_active_found_at ON videos(is_active, found_at DESC)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_board_active_found_at ON videos(board, is_active, found_at DESC)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_active_board ON videos(is_active, board)')
            
            await db.commit()
        print("[DB] База данных готова")

async def add_video(video_data: dict) -> bool:
    if not video_data or not video_data.get('url'):
        return False
    
    async with DB_LOCK:
        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                cursor = await db.execute('''
                    INSERT OR IGNORE INTO videos 
                    (url, thread_id, post_id, filename, original_name, board, thumbnail, width, height, duration, size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
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
                ))
                await db.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[DB] Ошибка: {e}")
            return False

async def get_videos(limit: int = 50, offset: int = 0, board: str = None, show_all: bool = False):
    async with DB_LOCK:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row # Устанавливаем row_factory для получения словарей
            if board:
                cursor = await db.execute('''
                    SELECT * FROM videos 
                    WHERE is_active = 1 AND board = ?
                    ORDER BY found_at DESC 
                    LIMIT ? OFFSET ?
                ''', (board, limit, offset))
            elif show_all:
                cursor = await db.execute('''
                    SELECT * FROM videos 
                    WHERE is_active = 1
                    ORDER BY found_at DESC 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
            else:
                placeholders = ','.join('?' * len(ALLOWED_BOARDS_MAIN))
                cursor = await db.execute(f'''
                    SELECT * FROM videos
                    WHERE is_active = 1 AND board IN ({placeholders})
                    ORDER BY found_at DESC
                    LIMIT ? OFFSET ?
                ''', (*ALLOWED_BOARDS_MAIN, limit, offset))
            
            videos = [dict(row) for row in await cursor.fetchall()]
    return videos

async def get_video_count(board: str = None, show_all: bool = False):
    async with DB_LOCK:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.cursor()
            if board:
                await cursor.execute('SELECT COUNT(*) FROM videos WHERE is_active = 1 AND board = ?', (board,))
            elif show_all:
                await cursor.execute('SELECT COUNT(*) FROM videos WHERE is_active = 1')
            else:
                placeholders = ','.join('?' * len(ALLOWED_BOARDS_MAIN))
                await cursor.execute(f'SELECT COUNT(*) FROM videos WHERE is_active = 1 AND board IN ({placeholders})',
                                      ALLOWED_BOARDS_MAIN)
            
            count = (await cursor.fetchone())[0]
    return count

import time

_boards_stats_cache = None
_boards_stats_cache_time = 0
_boards_stats_cache_ttl = 30  # секунд

async def get_boards_stats():
    global _boards_stats_cache, _boards_stats_cache_time
    now = time.time()
    if _boards_stats_cache and (now - _boards_stats_cache_time < _boards_stats_cache_ttl):
        return _boards_stats_cache
    
    async with DB_LOCK:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute('''
                SELECT board, COUNT(*) as count 
                FROM videos 
                WHERE is_active = 1 
                GROUP BY board 
                ORDER BY count DESC
            ''')
            stats = await cursor.fetchall()
    
    _boards_stats_cache = stats
    _boards_stats_cache_time = now
    return stats