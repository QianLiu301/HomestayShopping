"""数据库访问统计 —— 用来确认 Neon 流量到底来自哪里、缓存是否生效。

按接口（路由模板）累计：请求数、缓存命中数、数据库查询数、查询返回行数。
请求之外的查询（定时任务、启动迁移）记在 "(background)" 下。
每小时在日志里打印一次汇总，也可通过 GET /api/admin/db-stats 查看（仅 owner）。
统计保存在内存里，重新部署/重启后从零开始。
"""
import threading
import time
from collections import defaultdict

from flask import has_request_context, request
from sqlalchemy import event

_lock = threading.Lock()
_started_at = time.time()
_last_logged_at = time.time()
_LOG_INTERVAL = 3600
_stats = defaultdict(lambda: {'requests': 0, 'cache_hits': 0, 'queries': 0, 'rows': 0})


def _endpoint_key():
    if not has_request_context():
        return '(background)'
    rule = request.url_rule
    # 用路由模板而不是实际路径，避免 /products/1、/products/2 ... 撑爆统计表
    return f'{request.method} {rule.rule}' if rule else '(unmatched)'


def snapshot():
    with _lock:
        endpoints = {k: dict(v) for k, v in _stats.items()}
    totals = {f: sum(v[f] for v in endpoints.values()) for f in ('requests', 'cache_hits', 'queries', 'rows')}
    top = sorted(endpoints.items(), key=lambda kv: kv[1]['rows'], reverse=True)
    return {
        'since': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(_started_at)),
        'hours': round((time.time() - _started_at) / 3600, 2),
        'totals': totals,
        'endpoints': [{'endpoint': k, **v} for k, v in top],
    }


def _maybe_log(app):
    global _last_logged_at
    now = time.time()
    if now - _last_logged_at < _LOG_INTERVAL:
        return
    _last_logged_at = now
    snap = snapshot()
    t = snap['totals']
    top = ', '.join(f"{e['endpoint']} q={e['queries']} rows={e['rows']} hit={e['cache_hits']}/{e['requests']}"
                    for e in snap['endpoints'][:8])
    app.logger.warning(
        f"[db-stats] since {snap['since']} ({snap['hours']}h): requests={t['requests']} "
        f"cache_hits={t['cache_hits']} queries={t['queries']} rows={t['rows']} | top by rows: {top}"
    )


def init_db_stats(app, db):
    with app.app_context():
        engine = db.engine

    @event.listens_for(engine, 'after_cursor_execute')
    def _count_query(conn, cursor, statement, parameters, context, executemany):
        rows = cursor.rowcount if cursor.rowcount and cursor.rowcount > 0 else 0
        key = _endpoint_key()
        with _lock:
            s = _stats[key]
            s['queries'] += 1
            s['rows'] += rows

    @app.after_request
    def _count_request(resp):
        key = _endpoint_key()
        with _lock:
            s = _stats[key]
            s['requests'] += 1
            if resp.headers.get('X-Cache') == 'HIT':
                s['cache_hits'] += 1
        _maybe_log(app)
        return resp
