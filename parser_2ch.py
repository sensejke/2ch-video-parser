import requests
from bs4 import BeautifulSoup
import re
import time
import json
import warnings
from typing import Optional, List, Dict, Set, Union
from config import *
import config
from database import add_video

# Подавляем warning от BeautifulSoup о URL в комментариях
warnings.filterwarnings('ignore', message='The input looks more like a URL than markup')

class Parser2ch:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

        # Сначала посещаем главную страницу для установки cookies
        try:
            self.session.get(BASE_URL, timeout=10)
            time.sleep(0.5)
        except:
            pass

        # Устанавливаем cookies для подтверждения возраста
        # Пробуем различные варианты cookies
        self.session.cookies.set('age_confirmed', '1', domain='2ch.org')
        self.session.cookies.set('adult_confirmed', '1', domain='2ch.org')
        self.session.cookies.set('agebox', '1', domain='2ch.org')
        self.session.cookies.set('user_age', '18', domain='2ch.org')
        self.session.cookies.set('age_verified', 'true', domain='2ch.org')
        self.session.cookies.set('over18', '1', domain='2ch.org')
        self.session.cookies.set('cf_clearance', 'some_value', domain='2ch.org')

        # Для отслеживания уже обработанных видео в текущей сессии
        self.seen_urls: Set[str] = set()
        
        self.stats = {
            'new_videos': 0,
            'total_videos_found': 0,
            'threads_processed': 0,
            'boards_processed': 0,
            'errors': 0
        }
    
    def is_video_url(self, url: str) -> bool:
        """Проверяет, является ли URL видео файлом"""
        if not url:
            return False
        return url.lower().endswith(VIDEO_EXTENSIONS)
    
    def get_page(self, url: str) -> Optional[Union[BeautifulSoup, dict]]:
        """Загружает и парсит страницу (HTML или JSON)"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Проверяем Content-Type
            content_type = response.headers.get('Content-Type', '')

            if 'application/json' in content_type.lower():
                # Это JSON API
                try:
                    return response.json()
                except json.JSONDecodeError as e:
                    print(f"    [!] Ошибка парсинга JSON: {e}")
                    return None
            elif 'text/html' in content_type.lower():
                # Это HTML страница
                try:
                    soup = BeautifulSoup(response.text, 'html.parser')
                except Exception as e:
                    print(f"    [!] Ошибка парсинга HTML: {e}")
                    return None

            # Проверяем, есть ли окно подтверждения возраста
            warning_box = soup.find('div', class_='warningbox')
            if warning_box:
                print(f"    [!] Обнаружено окно подтверждения возраста, пытаемся обойти...")

                # Пробуем различные способы обхода
                attempts = [
                    # Способ 1: Дополнительные cookies
                    lambda: self._set_age_cookies(),
                    # Способ 2: Имитация POST запроса
                    lambda: self._simulate_age_confirmation(url),
                    # Способ 3: Добавление referer
                    lambda: self._add_referer_header(url)
                ]

                for attempt in attempts:
                    attempt()
                    time.sleep(0.5)
                    response = self.session.get(url, timeout=30)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')

                    if not soup.find('div', class_='warningbox'):
                        print(f"    [+] Подтверждение возраста успешно обойдено")
                        break
                else:
                    print(f"    [!!!] Не удалось обойти подтверждение возраста")
                    return None

            return soup
        except requests.exceptions.RequestException as e:
            print(f"    [!] Ошибка загрузки {url}: {e}")
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
                # Парсим "7258Кб, 640x360, 00:01:29"
                
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
    
    def parse_board_page(self, board: str, page: int = 0) -> tuple:
        """
        Парсит страницу доски.
        Возвращает (список видео, список ID тредов)
        """
        url = get_board_url(board, page)

        data = self.get_page(url)
        if not data:
            return [], []

        videos = []
        thread_ids = []

        if isinstance(data, dict):
            # JSON API
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
                            video_info = {
                                'url': make_absolute_url(file_path),
                                'thread_id': thread_id,
                                'post_id': thread_data.get('num'),
                                'filename': file_path.split('/')[-1],
                                'original_name': file_info.get('name', ''),
                                'board': board,
                                'thumbnail': file_info.get('thumbnail', ''),
                                'width': file_info.get('width'),
                                'height': file_info.get('height'),
                                'duration': None,
                                'size': file_info.get('size')
                            }
                            videos.append(video_info)

        elif isinstance(data, BeautifulSoup):
            # HTML парсинг (резервный вариант)
            threads = data.find_all('div', class_='thread')

            for thread in threads:
                thread_id = thread.get('id', '').replace('thread-', '')
                if thread_id:
                    thread_ids.append(thread_id)

                # Ищем все ссылки на видео в треде
                video_links = thread.find_all('a', href=re.compile(r'\.(mp4|webm|avi|mov|mkv)$', re.I))

                for link in video_links:
                    video_info = self.extract_video_info(link, board, thread_id)
                    if video_info:
                        videos.append(video_info)

        return videos, thread_ids
    
    def parse_thread(self, board: str, thread_id: str) -> List[dict]:
        """Парсит полный тред"""
        url = get_thread_url(board, thread_id)

        data = self.get_page(url)
        if not data:
            return []

        videos = []

        if isinstance(data, dict):
            # JSON API - посты обернуты в threads[0].posts
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

        elif isinstance(data, BeautifulSoup):
            # HTML парсинг
            video_links = data.find_all('a', href=re.compile(r'\.(mp4|webm|avi|mov|mkv)$', re.I))

            for link in video_links:
                video_info = self.extract_video_info(link, board, thread_id)
                if video_info:
                    videos.append(video_info)

        return videos
    
    def parse_board(self, board: str, deep_scan: bool = True):
        """Парсит всю доску"""
        print(f"\n{'='*60}")
        print(f"   ДОСКА /{board}/")
        print(f"{'='*60}")

        all_videos = []
        all_thread_ids = []

        # Для JSON API парсим только одну страницу (catalog.json возвращает все треды)
        print(f"\n    [*] Получаем каталог тредов...")

        videos, thread_ids = self.parse_board_page(board, 0)

        if videos or thread_ids:
            all_videos.extend(videos)
            all_thread_ids.extend(thread_ids)
            print(f"        Найдено видео: {len(videos)} | Тредов: {len(thread_ids)}")
        else:
            print(f"        Не удалось получить данные доски")

        # Если нужно, можем добавить fallback на HTML парсинг с пагинацией
        if not all_thread_ids:
            print(f"    [*] Пробуем HTML парсинг с пагинацией...")
            for page in range(min(MAX_PAGES_PER_BOARD, 3)):  # Ограничиваем для тестирования
                print(f"    [*] Страница {page} (HTML)...")

                # Временно меняем URL на HTML для fallback
                original_get_board_url = config.get_board_url
                config.get_board_url = lambda b, p=0: f"{config.BASE_URL}/{b}/" if p == 0 else f"{config.BASE_URL}/{b}/{p}.html"

                videos, thread_ids = self.parse_board_page(board, page)

                # Восстанавливаем JSON URL
                config.get_board_url = original_get_board_url

                if not videos and not thread_ids:
                    print(f"        Пустая страница, останавливаемся")
                    break

                all_videos.extend(videos)
                all_thread_ids.extend(thread_ids)

                print(f"        Найдено видео: {len(videos)} | Тредов: {len(thread_ids)}")

                time.sleep(REQUEST_DELAY)
        
        # Сохраняем видео с главных страниц
        new_count = 0
        for video in all_videos:
            if add_video(video):
                new_count += 1
                self.stats['new_videos'] += 1
        
        self.stats['total_videos_found'] += len(all_videos)
        print(f"\n    [+] Сохранено новых с главных страниц: {new_count}")
        
        # Глубокое сканирование тредов
        if deep_scan and all_thread_ids:
            unique_threads = list(set(all_thread_ids))[:MAX_THREADS_PER_BOARD]
            print(f"\n    [*] Глубокое сканирование {len(unique_threads)} тредов...")
            
            for i, thread_id in enumerate(unique_threads):
                videos = self.parse_thread(board, thread_id)
                
                new_in_thread = 0
                for video in videos:
                    if add_video(video):
                        new_in_thread += 1
                        self.stats['new_videos'] += 1
                
                self.stats['total_videos_found'] += len(videos)
                self.stats['threads_processed'] += 1
                
                if new_in_thread > 0:
                    print(f"        Тред #{thread_id}: +{new_in_thread} видео")
                
                # Прогресс каждые 10 тредов
                if (i + 1) % 10 == 0:
                    print(f"        ... обработано {i + 1}/{len(unique_threads)} тредов")
                
                time.sleep(REQUEST_DELAY)
        
        self.stats['boards_processed'] += 1
        print(f"\n    [OK] Доска /{board}/ завершена")
    
    def run(self, boards: list = None, deep_scan: bool = True):
        """Основной метод запуска"""
        if boards is None:
            boards = get_active_boards()
        
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
        
        print("\n" + "="*60)
        print("   2CH.ORG VIDEO PARSER - STARTED")
        print(f"   Домен: {BASE_URL}")
        print(f"   Досок: {len(boards)}")
        print(f"   Режим: {'Глубокий' if deep_scan else 'Быстрый'}")
        print("="*60)
        
        for i, board in enumerate(boards):
            print(f"\n[{i+1}/{len(boards)}]", end="")
            
            try:
                self.parse_board(board, deep_scan=deep_scan)
            except Exception as e:
                print(f"\n    [!!!] Критическая ошибка на /{board}/: {e}")
                self.stats['errors'] += 1
            
            time.sleep(DELAY_BETWEEN_BOARDS)
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*60)
        print("   ПАРСИНГ ЗАВЕРШЁН!")
        print("="*60)
        print(f"   Статистика:")
        print(f"      • Обработано досок: {self.stats['boards_processed']}")
        print(f"      • Просканировано тредов: {self.stats['threads_processed']}")
        print(f"      • Найдено видео всего: {self.stats['total_videos_found']}")
        print(f"      • Сохранено новых: {self.stats['new_videos']}")
        print(f"      • Ошибок: {self.stats['errors']}")
        print(f"      • Время: {elapsed:.1f} сек ({elapsed/60:.1f} мин)")
        print("="*60 + "\n")
        
        return self.stats['new_videos']

    def _set_age_cookies(self):
        """Устанавливает cookies для подтверждения возраста"""
        self.session.cookies.set('age_confirmed', '1', domain='2ch.org')
        self.session.cookies.set('adult_confirmed', '1', domain='2ch.org')
        self.session.cookies.set('agebox', '1', domain='2ch.org')
        self.session.cookies.set('user_age', '18', domain='2ch.org')
        self.session.cookies.set('age_verified', 'true', domain='2ch.org')
        self.session.cookies.set('over18', '1', domain='2ch.org')

    def _simulate_age_confirmation(self, url):
        """Имитирует подтверждение возраста через POST запрос"""
        try:
            # Пробуем отправить POST запрос на ту же страницу
            post_data = {
                'age_confirmed': '1',
                'adult_confirmed': '1',
                'over18': '1'
            }
            self.session.post(url, data=post_data, timeout=10)
        except:
            pass  # Игнорируем ошибки POST запроса

    def _add_referer_header(self, url):
        """Добавляет referer header"""
        self.session.headers.update({'Referer': url})


# Тест
if __name__ == "__main__":
    from database import init_db
    init_db()
    
    parser = Parser2ch()
    parser.run(boards=["b"], deep_scan=True)