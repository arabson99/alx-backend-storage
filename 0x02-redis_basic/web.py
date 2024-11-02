import redis
import requests
from functools import wraps
import time

# Initialize the Redis client
cache = redis.Redis()

def cache_page(func):
    @wraps(func)
    def wrapper(url: str):
        # Check the cache for the URL
        cached_response = cache.get(url)
        if cached_response:
            # Increment the count and return the cached response
            cache.incr(f'count:{url}')
            return cached_response.decode('utf-8')
        
        # Call the original function to get the page
        response = func(url)
        
        # Cache the response with an expiration time of 10 seconds
        cache.set(url, response, ex=10)
        # Increment the count for this URL
        cache.incr(f'count:{url}')
        return response
    return wrapper

@cache_page
def get_page(url: str) -> str:
    """Fetch the HTML content of the URL and return it."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except requests.RequestException as e:
        return f"Error fetching the page: {e}"
