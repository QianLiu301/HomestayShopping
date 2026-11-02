import threading
import time
from functools import wraps
from urllib.parse import urlencode

from flask import Response, make_response, request

# 进程内 TTL 缓存：减少公开读接口对 Neon 的查询（gunicorn 每个 worker 各有一份）
_store = {}
_lock = threading.Lock()
_MAX_ENTRIES = 500


def cache_get(key):
    with _lock:
        item = _store.get(key)
        if item is None:
            return None
        expires_at, value = item
        if expires_at < time.monotonic():
            del _store[key]
            return None
        return value


def cache_set(key, value, ttl):
    with _lock:
        if key not in _store and len(_store) >= _MAX_ENTRIES:
            _store.pop(next(iter(_store)))
        _store[key] = (time.monotonic() + ttl, value)


def cache_clear():
    with _lock:
        _store.clear()


def cached_response(ttl=300, browser_ttl=60):
    """缓存 GET 接口的 200 响应，key 为路径 + 排序后的查询参数（含 lang）"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            key = 'resp:' + request.path + '?' + urlencode(sorted(request.args.items(multi=True)))
            hit = cache_get(key)
            if hit is None:
                resp = make_response(f(*args, **kwargs))
                if resp.status_code != 200:
                    return resp
                hit = (resp.get_data(), resp.mimetype)
                cache_set(key, hit, ttl)
            body, mimetype = hit
            resp = Response(body, mimetype=mimetype)
            resp.headers['Cache-Control'] = f'public, max-age={browser_ttl}'
            return resp
        return wrapper
    return decorator
