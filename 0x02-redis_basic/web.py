#!/usr/bin/env python3
""" A module for fetching and caching web pages. """
import redis
import requests
from functools import wraps
from typing import Callable

# Initialize Redis client
r = redis.Redis()

def count_calls(method: Callable) -> Callable:
    """ Decorator to count how many time a URL is accessed and cache the result."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """ Wrapper that tracks access count and manages caching."""

        cache_html = r.get(url)
        if cache_html:
            r.incr(f"count:{url}")
            return cache_html.decode('utf-8')

        # call the original method to fetch the page cotent
        html = method(url)
        # cache the result with an expiration time of 10 sec
        r.set(url, html, ex=10)
        r.incr(f"count:{url}", 0)
        return html
    return wrapper

@count_calls
def get_page(url: str) -> str:
    """ Fetch the HTML content of a URL. """
    request = requests.get(url)
    request.raise_for_status()
    return request.text

if __name__ == "__main__":
    # Test with a slow URL to demonstrate caching
    test_url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.google.com"
    print(get_page(test_url))  # First call will fetch the page
    print(get_page(test_url))  # Second call will return the cached page
