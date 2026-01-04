#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask приложение для PostgreSQL
Использует database_postgres.py вместо database.py
"""

import os
import threading
import re
import asyncio
from datetime import datetime
from flask import Flask, render_template, jsonify, request, make_response

from database_postgres import get_videos, get_video_count, get_boards_stats, close_db_pool
from config import get_active_boards, BASE_URL, ALL_BOARDS
from performance_monitor import init_performance_monitoring

app = Flask(__name__)

# Инициализация мониторинга производительности
init_performance_monitoring(app)

@app.teardown_appcontext
def teardown_db(exception):
    """Закрыть соединения с БД при завершении"""
    asyncio.run(close_db_pool())

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'ok', 'database': 'postgresql'}, 200

# Rate limiting отключен для разработки
# limiter = Limiter(app=app, key_func=get_remote_address)

parser_status = {
    'running': False,
    'last_run': None,
    'last_count': 0
}

@app.template_filter('thumb_url')
def thumb_url_filter(thumbnail):
    """Формирует правильный URL для превью"""
    if not thumbnail:
        return ''
    if '..' in thumbnail:
        return ''
    if thumbnail.startswith('http://') or thumbnail.startswith('https://'):
        return thumbnail
    if thumbnail.startswith('/'):
        return BASE_URL + thumbnail
    return BASE_URL + '/' + thumbnail

@app.route('/')
def index():
    """Главная страница"""
    page = request.args.get('page', 1, type=int)
    board = request.args.get('board', None)
    show_all_unfiltered = request.args.get('all', False, type=lambda x: x.lower() == 'true')
    per_page = 30
    offset = (page - 1) * per_page

    # Валидация board параметра
    if board and not re.match(r'^[a-z0-9]+$', board):
        board = None

    # Асинхронные вызовы к PostgreSQL
    videos = asyncio.run(get_videos(limit=per_page, offset=offset, board=board, show_all=show_all_unfiltered))
    total = asyncio.run(get_video_count(board, show_all=show_all_unfiltered))
    total_pages = max(1, (total + per_page - 1) // per_page)
    boards_stats = asyncio.run(get_boards_stats())

    resp = make_response(render_template('index.html',
                         videos=videos,
                         page=page,
                         total_pages=total_pages,
                         total=total,
                         boards_stats=boards_stats,
                         current_board=board,
                         show_all_unfiltered=show_all_unfiltered,
                         parser_status=parser_status,
                         base_url=BASE_URL))

    # Кэширование
    resp.cache_control.max_age = 60
    resp.cache_control.public = True

    # Заголовки безопасности
    resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
    resp.headers['X-XSS-Protection'] = '1; mode=block'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    resp.headers['Content-Security-Policy'] = "default-src 'self' http: https: data: blob: 'unsafe-inline'"

    return resp

@app.route('/api/videos')
def api_videos():
    """API для получения видео"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)
    board = request.args.get('board', None)
    show_all_unfiltered = request.args.get('all', False, type=lambda x: x.lower() == 'true')
    offset = (page - 1) * per_page

    # Валидация
    if board and not re.match(r'^[a-z0-9]+$', board):
        board = None
    per_page = min(per_page, 100)
    per_page = max(per_page, 1)

    videos = asyncio.run(get_videos(limit=per_page, offset=offset, board=board, show_all=show_all_unfiltered))
    total = asyncio.run(get_video_count(board, show_all=show_all_unfiltered))

    resp = make_response(jsonify({'videos': videos, 'total': total, 'page': page}))
    resp.cache_control.max_age = 30
    resp.cache_control.public = True

    # Заголовки безопасности
    resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
    resp.headers['X-XSS-Protection'] = '1; mode=block'
    resp.headers['X-Content-Type-Options'] = 'nosniff'

    return resp

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """Очистка мертвых видео"""
    from cleanup_videos import cleanup_dead_videos

    try:
        dead_count = asyncio.run(cleanup_dead_videos())
        return jsonify({
            'status': 'completed',
            'dead_videos_removed': dead_count
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/status')
def status():
    """Статус парсера"""
    return jsonify(parser_status)

@app.route('/metrics')
def metrics():
    """Prometheus метрики"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
