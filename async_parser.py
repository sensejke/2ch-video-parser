#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Асинхронный парсер видео с 2ch.org
Автор: @sensejke (https://t.me/sensejke)
"""

import asyncio
import aiohttp
import aiosqlite
import json
import re
import time
import warnings
import random
from datetime import datetime
from typing import Optional, List, Dict, Set, Union
from bs4 import BeautifulSoup
import redis
import logging
from prometheus_client import Counter, Gauge, Histogram

from config import *
from database import DB_LOCK

# Подавляем warning от BeautifulSoup о URL в комментариях
warnings.filterwarnings('ignore', message='The input looks more like a URL than markup')

# Prometheus метрики
videos_parsed_total = Counter('videos_parsed_total', 'Total videos parsed', ['board'])
videos_saved_total = Counter('videos_saved_total', 'Total videos saved')
boards_processed_total = Counter('boards_processed_total', 'Total boards processed')
threads_processed_total = Counter('threads_processed_total', 'Total threads processed')
parse_duration = Histogram('parse_duration_seconds', 'Parse duration in seconds', ['board'])
cache_hits_total = Counter('cache_hits_total', 'Total cache hits')
cache_misses_total = Counter('cache_misses_total', 'Total cache misses')

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('2ch_async_parser')

class AsyncParser2ch:

    async def download_thumbnail(self, url: str, session: aiohttp.ClientSession, save_path: str) -> bool:
        """Асинхронно скачивает превью по url"""
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    with open(save_path, 'wb') as f:
                        f.write(await resp.read())
                    return True
        except Exception as e:
            logger.debug(f"Ошибка скачивания превью {url}: {e}")
        return False

    async def download_thumbnails_parallel(self, thumb_tasks: list):
        """Параллельно скачивает превьюшки (список задач: (url, save_path))"""
        if not thumb_tasks:
            return 0
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            tasks = [self.download_thumbnail(url, session, save_path) for url, save_path in thumb_tasks]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        return sum(1 for r in results if r is True)
    def __init__(self):
        # Redis опциональный - если недоступен, работаем без кэша
        self.redis_cache = None
        try:
            self.redis_cache = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=1)
            self.redis_cache.ping()  # Проверяем подключение
            logger.info("Redis кэш подключен")
        except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
            logger.warning(f"Redis недоступен, работаем без кэширования: {e}")
            self.redis_cache = None

        self.session = None

        # Для отслеживания уже обработанных видео в текущей сессии
        self.seen_urls: Set[str] = set()

        # Кэшируем User-Agent для всех запросов
        self.user_agent = HEADERS.get('User-Agent')

        self.stats = {
            'new_videos': 0,
            'total_videos_found': 0,
            'threads_processed': 0,
            'boards_processed': 0,
            'errors': 0
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=HEADERS)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def is_video_url(self, url: str) -> bool:
        """Проверяет, является ли URL видео файлом"""
        if not url:
            return False
        return url.lower().endswith(VIDEO_EXTENSIONS)

    async def get_page(self, url: str) -> Optional[Union[BeautifulSoup, dict]]:
        """Асинхронно загружает и парсит страницу (HTML или JSON)"""
        cache_key = f"page:{url}"
        
        try:
            # Проверяем кэш сначала (если Redis доступен)
            if self.redis_cache is not None:
                try:
                    cached_data = self.redis_cache.get(cache_key)
                    if cached_data:
                        logger.debug(f"Cache hit for {url}")
                        cache_hits_total.inc()
                        return json.loads(cached_data)
                    cache_misses_total.inc()
                except Exception as e:
                    logger.debug(f"Ошибка чтения кэша: {e}")
            else:
                cache_misses_total.inc()

            async with self.session.get(url, timeout=30) as response:
                response.raise_for_status()

                # Проверяем Content-Type
                content_type = response.headers.get('Content-Type', '')

                if 'application/json' in content_type.lower():
                    data = await response.json()
                    # Кэшируем на 5 минут (если Redis доступен)
                    if self.redis_cache is not None:
                        try:
                            self.redis_cache.setex(cache_key, 300, json.dumps(data))
                        except Exception as e:
                            logger.debug(f"Ошибка записи в кэш: {e}")
                    return data
                elif 'text/html' in content_type.lower():
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    # Кэшируем HTML на 5 минут (если Redis доступен)
                    if self.redis_cache is not None:
                        try:
                            self.redis_cache.setex(cache_key, 300, html)
                        except Exception as e:
                            logger.debug(f"Ошибка записи в кэш: {e}")
                    return soup
                else:
                    logger.warning(f"Неожиданный Content-Type: {content_type}")
                    return None

        except Exception as e:
            logger.error(f"Ошибка загрузки {url}: {e}")
            self.stats['errors'] += 1
            return None

    def extract_video_info(self, link_element, board: str, thread_id: str = None) -> Optional[dict]:
        """Извлекает информацию о видео из HTML элемента"""
        href = link_element.get('href', '')

        if not self.is_video_url(href):
            return None

        url = make_absolute_url(href)

        if not url or url in self.seen_urls:
            return None

        self.seen_urls.add(url)

        # Извлекаем имя файла
        filename = href.split('/')[-1] if href else ''

        # Ищем оригинальное имя (в title или тексте ссылки)
        original_name = link_element.get('title', '') or link_element.get_text(strip=True) or filename

        # Ищем превью (thumbnail)
        # Сохраняем как относительный путь (начинается с /)
        thumbnail = None
        img = link_element.find('img')
        if img:
            thumb_src = img.get('src') or img.get('data-src')
            if thumb_src:
                # Если уже полный URL (http/https), извлекаем относительный путь
                if thumb_src.startswith('http://') or thumb_src.startswith('https://'):
                    # Извлекаем путь после домена
                    from urllib.parse import urlparse
                    parsed = urlparse(thumb_src)
                    thumbnail = parsed.path
                elif thumb_src.startswith('/'):
                    thumbnail = thumb_src
                else:
                    thumbnail = '/' + thumb_src

        # Ищем метаданные (размер, разрешение)
        width = height = duration = size = None

        # Ищем в соседнем span с классом post__filezise
        parent = link_element.parent
        if parent:
            filesize_span = parent.find('span', class_='post__filezise')
            if filesize_span:
                text = filesize_span.get_text()

                # Размер файла
                size_match = re.search(r'(\d+)\s*[КкKk][Ббб]', text)
                if size_match:
                    size = int(size_match.group(1)) * 1024  # KB to bytes

                # Разрешение
                res_match = re.search(r'(\d+)x(\d+)', text)
                if res_match:
                    width = int(res_match.group(1))
                    height = int(res_match.group(2))

                # Длительность
                dur_match = re.search(r'(\d{2}:\d{2}:\d{2})', text)
                if dur_match:
                    duration = dur_match.group(1)

        # Получаем ID поста
        post_id = None
        post_div = link_element.find_parent('div', class_='post')
        if post_div:
            post_id = post_div.get('data-num') or post_div.get('id', '').replace('post-', '')

        return {
            'url': url,
            'thread_id': str(thread_id) if thread_id else post_id,
            'post_id': post_id,
            'filename': filename,
            'original_name': original_name,
            'board': board,
            'thumbnail': thumbnail,
            'width': width,
            'height': height,
            'duration': duration,
            'size': size
        }

    async def parse_board_catalog(self, board: str) -> tuple:
        """
        Парсит каталог доски (JSON API)
        Возвращает (список видео, список ID тредов)
        """
        url = get_board_url(board, 0)
        data = await self.get_page(url)

        if not data or not isinstance(data, dict):
            return [], []

        videos = []
        thread_ids = []
        threads_data = data.get('threads', [])

        for thread_data in threads_data[:MAX_THREADS_PER_BOARD]:
            thread_id = str(thread_data.get('num', ''))
            if thread_id:
                thread_ids.append(thread_id)

                # Ищем видео в комментарии треда
                comment = thread_data.get('comment', '')
                soup = BeautifulSoup(comment, 'html.parser')
                video_links = soup.find_all('a', href=re.compile(r'\.(mp4|webm|avi|mov|mkv)$', re.I))

                for link in video_links:
                    video_info = self.extract_video_info(link, board, thread_id)
                    if video_info:
                        videos.append(video_info)

                # Также проверяем файлы
                files = thread_data.get('files', [])
                for file_info in files:
                    file_path = file_info.get('path', '')
                    if self.is_video_url(file_path):
                        # Создаем видео info из файла
                        # thumbnail сохраняем как относительный путь (без make_absolute_url)
                        thumbnail_url = file_info.get('thumbnail', '')

                        video_info = {
                            'url': make_absolute_url(file_path),
                            'thread_id': thread_id,
                            'post_id': thread_data.get('num'),
                            'filename': file_path.split('/')[-1],
                            'original_name': file_info.get('name', ''),
                            'board': board,
                            'thumbnail': thumbnail_url,  # Сохраняем как относительный путь
                            'width': file_info.get('width'),
                            'height': file_info.get('height'),
                            'duration': None,
                            'size': file_info.get('size')
                        }
                        videos.append(video_info)

        return videos, thread_ids

    async def parse_thread(self, board: str, thread_id: str) -> List[dict]:
        """Парсит полный тред"""
        url = get_thread_url(board, thread_id)
        data = await self.get_page(url)

        if not data or not isinstance(data, dict):
            return []

        videos = []
        
        # JSON API оборачивает посты в threads[0].posts
        threads = data.get('threads', [])
        if not threads:
            return []
        
        posts = threads[0].get('posts', [])

        for post in posts:
            post_id = post.get('num')
            
            # 1️⃣ Ищем видео в комментарии (встроенные ссылки)
            comment = post.get('comment', '')
            soup = BeautifulSoup(comment, 'html.parser')
            video_links = soup.find_all('a', href=re.compile(r'\.(mp4|webm|avi|mov|mkv)$', re.I))

            for link in video_links:
                video_info = self.extract_video_info(link, board, thread_id)
                if video_info:
                    videos.append(video_info)

            # 2️⃣ Также проверяем файлы поста (основной способ хранения видео на 2ch)
            files = post.get('files')
            if files:  # files может быть null или []
                for file_info in files:
                    file_path = file_info.get('path', '')
                    if self.is_video_url(file_path):
                        # Создаем видео info из файла
                        video_info = {
                            'url': make_absolute_url(file_path),
                            'thread_id': thread_id,
                            'post_id': post_id,
                            'filename': file_info.get('name', ''),
                            'original_name': file_info.get('displayname', ''),
                            'board': board,
                            'thumbnail': file_info.get('thumbnail', ''),
                            'width': file_info.get('width'),
                            'height': file_info.get('height'),
                            'duration': file_info.get('duration'),
                            'size': file_info.get('size')
                        }
                        
                        if video_info['url'] and video_info['url'] not in self.seen_urls:
                            self.seen_urls.add(video_info['url'])
                            videos.append(video_info)

        return videos

    async def save_video(self, video_data: dict) -> bool:
        """Асинхронно сохраняет видео в базу данных (batch-friendly)"""
        async with DB_LOCK:
            try:
                async with aiosqlite.connect(DATABASE_PATH) as db:
                    await db.execute('''
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
                    return True
            except Exception as e:
                logger.error(f"Ошибка сохранения видео {video_data.get('url')}: {e}")
                return False

    async def save_videos_batch(self, videos: list) -> int:
        """Асинхронно сохраняет список видео в БД батчем"""
        if not videos:
            return 0
        async with DB_LOCK:
            try:
                async with aiosqlite.connect(DATABASE_PATH) as db:
                    await db.executemany('''
                        INSERT OR IGNORE INTO videos
                        (url, thread_id, post_id, filename, original_name, board, thumbnail, width, height, duration, size)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', [(
                        v.get('url'), v.get('thread_id'), v.get('post_id'), v.get('filename'), v.get('original_name'),
                        v.get('board'), v.get('thumbnail'), v.get('width'), v.get('height'), v.get('duration'), v.get('size')
                    ) for v in videos])
                    await db.commit()
                    return len(videos)
            except Exception as e:
                logger.error(f"Ошибка batch-сохранения видео: {e}")
                return 0

    async def parse_board(self, board: str, deep_scan: bool = True):
        """Парсит всю доску асинхронно"""
        logger.info(f"Начинаем парсинг доски /{board}/")

        start_time = time.time()
        with parse_duration.labels(board=board).time():

        # Парсим каталог
            # Парсим каталог
            videos, thread_ids = await self.parse_board_catalog(board)

            new_count = 0
            for video in videos:
                if await self.save_video(video):
                    new_count += 1
                    self.stats['new_videos'] += 1
                    videos_saved_total.inc()

            videos_parsed_total.labels(board=board).inc(len(videos))
            self.stats['total_videos_found'] += len(videos)
            logger.info(f"Доска /{board}/: найдено {len(videos)} видео, сохранено {new_count} новых")

        # Глубокое сканирование тредов
        if deep_scan and thread_ids:
            unique_threads = list(set(thread_ids))[:MAX_THREADS_PER_BOARD]
            logger.info(f"Глубокое сканирование {len(unique_threads)} тредов...")

            for i, thread_id in enumerate(unique_threads):
                thread_videos = await self.parse_thread(board, thread_id)

                thread_new_count = 0
                for video in thread_videos:
                    if await self.save_video(video):
                        thread_new_count += 1
                        self.stats['new_videos'] += 1

                self.stats['total_videos_found'] += len(thread_videos)
                self.stats['threads_processed'] += 1
                threads_processed_total.inc()

                if thread_new_count > 0:
                    logger.info(f"Тред #{thread_id}: +{thread_new_count} видео")

                # Прогресс каждые 10 тредов
                if (i + 1) % 10 == 0:
                    logger.info(f"Обработано {i + 1}/{len(unique_threads)} тредов")

                await asyncio.sleep(REQUEST_DELAY)

            elapsed = time.time() - start_time
            self.stats['boards_processed'] += 1
            boards_processed_total.inc()
            logger.info(f"Доска /{board}/ завершена за {elapsed:.1f} сек")

    async def run(self, boards: list = None, deep_scan: bool = True):
        """Основной метод запуска асинхронного парсера"""
        if boards is None:
            boards = get_active_boards()

        # Перемешиваем доски для более равномерного распределения
        random.shuffle(boards)

        # Сброс
        self.seen_urls.clear()
        self.stats = {
            'new_videos': 0,
            'total_videos_found': 0,
            'threads_processed': 0,
            'boards_processed': 0,
            'errors': 0
        }

        start_time = time.time()

        logger.info(f"Запуск асинхронного парсера 2ch.org")
        logger.info(f"Домен: {BASE_URL}")
        logger.info(f"Досок: {len(boards)} (перемешаны)")
        logger.info(f"Режим: {'Глубокий' if deep_scan else 'Быстрый'}")

        # Парсим все доски параллельно
        tasks = [self.parse_board(board, deep_scan) for board in boards]
        await asyncio.gather(*tasks)

        elapsed = time.time() - start_time

        logger.info("Парсинг завершён!")
        logger.info(f"Статистика:")
        logger.info(f"  Обработано досок: {self.stats['boards_processed']}")
        logger.info(f"  Просканировано тредов: {self.stats['threads_processed']}")
        logger.info(f"  Найдено видео всего: {self.stats['total_videos_found']}")
        logger.info(f"  Сохранено новых: {self.stats['new_videos']}")
        logger.info(f"  Ошибок: {self.stats['errors']}")
        logger.info(f"  Время: {elapsed:.1f} сек ({elapsed/60:.1f} мин)")

        return self.stats['new_videos']


async def main():
    """Тест асинхронного парсера"""
    async with AsyncParser2ch() as parser:
        await parser.run(boards=['b'], deep_scan=False)


if __name__ == "__main__":
    asyncio.run(main())
