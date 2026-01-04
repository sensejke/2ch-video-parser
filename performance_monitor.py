#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Мониторинг производительности приложения
"""

import time
import psutil
import asyncio
from functools import wraps
from flask import g, request
from prometheus_client import Counter, Histogram, Gauge

# Метрики Prometheus
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])
DB_QUERY_COUNT = Counter('db_queries_total', 'Total database queries', ['operation'])
DB_QUERY_LATENCY = Histogram('db_query_duration_seconds', 'Database query latency', ['operation'])
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Current memory usage in bytes')
CPU_USAGE = Gauge('cpu_usage_percent', 'Current CPU usage percentage')

def update_system_metrics():
    """Обновление системных метрик"""
    MEMORY_USAGE.set(psutil.virtual_memory().used)
    CPU_USAGE.set(psutil.cpu_percent(interval=None))

def measure_db_query(operation):
    """Декоратор для измерения времени выполнения запросов к БД"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                DB_QUERY_LATENCY.labels(operation=operation).observe(duration)
                DB_QUERY_COUNT.labels(operation=operation).inc()
                return result
            except Exception as e:
                duration = time.time() - start_time
                DB_QUERY_LATENCY.labels(operation=operation).observe(duration)
                raise e
        return wrapper
    return decorator

def init_performance_monitoring(app):
    """Инициализация мониторинга производительности"""

    @app.before_request
    def before_request():
        g.start_time = time.time()
        update_system_metrics()

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown'
            ).observe(duration)

            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=response.status_code
            ).inc()

        return response

# Экспорт для использования в других модулях
__all__ = ['measure_db_query', 'init_performance_monitoring']
