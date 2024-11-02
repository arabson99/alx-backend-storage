#!/usr/bin/env python3
""" A module for fetching and caching web pages. """
import redis
import requests
from functools import wraps

# Initialize Redis client
r = redis.Redis()

def count_calls(method):
    """ Decorator to count how many times a URL is accessed and cache the result. """
    @wraps(method)
    def wrapper(url: str) -> str:
        """ Wrapper that tracks access count and manages caching. """
        
        # Check if the URL is cached
        cache_html = r.get(url)
        if cache_html:
            # Increment count and return cached result
            r.incr(f"count:{url}")  # Increment the count for this URL
            return cache_html.decode('utf-8')
        # Fetch the content since it's not cached
        html = method(url)
        # Cache the result with an expiration time of 10 seconds
        r.set(url, html, ex=10)

        # Initialize count for this URL
        r.set(f"count:{url}", 1)
        return html

    return wrapper

@count_calls
def get_page(url: str) -> str:
    """ Fetch the HTML content of a URL. """
    response = requests.get(url)
    response.raise_for_status()
    return response.text
