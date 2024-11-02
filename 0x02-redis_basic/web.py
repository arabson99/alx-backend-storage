#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests
from functools import wraps
from typing import Callable

redis_store = redis.Redis()

def data_cacher(method: Callable) -> Callable:   

    @wraps(method)
    def invoker(url: str) -> str:
        redis_store.incr(f"count:{url}")
        result = redis_store.get(f"result:{url}")
        if result:
            return result.decode("utf-8")
        result = method(url)
        redis_store.setex(f"result:{url}", 10, result)
        return result
    return invoker

@data_cacher
def get_page(url: str) -> str:
    return requests.get(url).text
