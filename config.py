# ===== НАСТРОЙКИ ДЛЯ 2CH.ORG =====
BASE_URL = "https://2ch.org"

# Полный список досок
ALL_BOARDS = [
    "2d", "8", "a", "aa", "abu", "ai", "alco", "asmr", "asylum", "au",
    "b", "bg", "bi", "biz", "bo", "br", "brg", "by", "c", "cc", "cg", 
    "ch", "char", "crypt", "cul", "cute", "d", "de", "dev", "di", "diy",
    "dom", "dr", "e", "electrach", "em", "es", "ew", "fa", "fag", "fd",
    "fem", "fet", "fi", "fiz", "fl", "fs", "ftb", "fur", "ga", "gabe",
    "gacha", "gb", "gd", "gg", "got", "gsg", "h", "hc", "hh", "hi", "hg",
    "ho", "hry", "hv", "hw", "ind", "ing", "int", "izd", "ja", "jsf",
    "kpop", "kz", "lap", "law", "ld", "m", "ma", "man", "math", "mc",
    "media", "me", "mg", "mlp", "mlpr", "mmo", "mo", "mobi", "mov", "mu",
    "mus", "ne", "news", "nf", "nvr", "o", "obr", "old", "out", "p", "pa",
    "ph", "po", "pok", "pr", "psy", "pvc", "qtr4", "r", "r34", "ra", "re",
    "rf", "rm", "ro", "ruvn", "s", "sad", "sci", "se", "sex", "sf", "sn",
    "soc", "socionics", "smo", "sp", "spc", "srv", "sw", "t", "td", "tes",
    "test", "to", "tr", "trv", "tv", "un", "ussr", "v", "vape", "vg", "vn",
    "vr", "w", "web", "wh", "whn", "wm", "wow", "wrk", "wr", "wwe", "ya", "zog", "hc", "e"
]

# Популярные доски с видео
BOARDS_QUICK = ["b", "mov", "media", "a", "v", "vg", "gg", "sex", "mus", "hc", "e"]

# Режим
USE_QUICK_BOARDS = True

def get_active_boards():
    return BOARDS_QUICK if USE_QUICK_BOARDS else ALL_BOARDS

# URLs
def get_board_url(board, page=0):
    """URL страницы доски"""
    # Используем JSON API с пагинацией для получения всех тредов
    if page == 0:
        return f"{BASE_URL}/{board}/catalog.json"
    else:
        # Для дополнительных страниц используем threads.json с offset
        # 2ch API поддерживает пагинацию через параметр или offset
        return f"{BASE_URL}/{board}/catalog.json?page={page}"

def get_thread_url(board, thread_id):
    """URL треда"""
    return f"{BASE_URL}/{board}/res/{thread_id}.json"

def make_absolute_url(url):
    """Делает URL абсолютным"""
    if not url:
        return None
    if url.startswith('http'):
        return url
    if url.startswith('//'):
        return 'https:' + url
    if url.startswith('/'):
        return BASE_URL + url
    return BASE_URL + '/' + url

# Расширения видео
VIDEO_EXTENSIONS = ('.mp4', '.webm', '.avi', '.mov', '.mkv', '.m4v')

# БД
DATABASE_PATH = "videos.db"

# Обновление
UPDATE_INTERVAL = 60  # минут

# Лимиты
MAX_PAGES_PER_BOARD = 10  # страниц доски
MAX_THREADS_PER_BOARD = 50  # тредов для глубокого сканирования

# Попробуем мобильный User-Agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Sec-Ch-Ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?1',
    'Sec-Ch-Ua-Platform': '"Android"',
}

# Задержки (секунды)
REQUEST_DELAY = 0.3
DELAY_BETWEEN_BOARDS = 1.0