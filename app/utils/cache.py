"""轻量内存 TTL 缓存 —— 给公开只读接口用。

目的：相同的 GET 请求在 TTL 时间内直接返回缓存，不再查数据库，
从而大幅降低 Neon 的网络传输流量（防止爬虫/重复访问把每月 5GB 额度打满）。

说明：
- gunicorn 多 worker 时，每个 worker 各自持有一份缓存，命中率依然很高。
- 按「完整请求路径 + 查询参数」作为缓存键，所以不同语言(lang=xx)、不同分页
  会分别缓存，互不影响。
- 管理端任何写操作成功后会调用 clear_public_cache() 清空缓存，保证内容编辑后立即生效。
"""
import time
from functools import wraps
from flask import request, make_response, Response

# key -> (expire_ts, (body_bytes, status_code, content_type))
_store = {}
_MAX_ENTRIES = 2000


def _purge_expired(now):
    for k in [k for k, v in _store.items() if v[0] <= now]:
        _store.pop(k, None)


def cached(ttl=120):
    """缓存 GET 响应 ttl 秒。仅缓存状态码 200 的响应。

    用法：把 @cached(ttl=秒数) 加在公开只读视图函数上（在 @api_bp.route 下面）。
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if request.method != 'GET':
                return fn(*args, **kwargs)
            key = f"{request.path}?{request.query_string.decode('utf-8', 'ignore')}"
            now = time.time()
            entry = _store.get(key)
            if entry and entry[0] > now:
                body, status, ctype = entry[1]
                resp = Response(body, status=status, content_type=ctype)
                resp.headers['X-Cache'] = 'HIT'
                return resp
            rv = fn(*args, **kwargs)
            try:
                resp = make_response(rv)
                if resp.status_code == 200:
                    if len(_store) >= _MAX_ENTRIES:
                        _purge_expired(now)
                    _store[key] = (now + ttl, (resp.get_data(), resp.status_code, resp.content_type))
                    resp.headers['X-Cache'] = 'MISS'
                return resp
            except Exception:
                return rv
        return wrapper
    return decorator


def clear_public_cache():
    """清空全部公开缓存。管理端写操作成功后调用，让内容改动立即对外生效。"""
    _store.clear()
