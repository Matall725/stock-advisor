"""缓存管理：避免重复请求 AKShare 数据"""
import os
import diskcache as dc
from config import CACHE_DIR, CACHE_TTL

os.makedirs(CACHE_DIR, exist_ok=True)
_cache = dc.Cache(CACHE_DIR)


def get(key: str):
    return _cache.get(key)


def put(key: str, value, ttl: int = CACHE_TTL):
    _cache.set(key, value, expire=ttl)


def clear():
    _cache.clear()
