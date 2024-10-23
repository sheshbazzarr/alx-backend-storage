#!/usr/bin/env python3
"""
This module provides a function to fetch web pages while caching the results
in a Redis database with an expiration time. It tracks how many times a URL
is accessed.
"""

import redis
import requests
from functools import wraps
import time


def cache_expiration(expiration: int):
    """
    Decorator to cache the result of the get_page function.

    Args:
        expiration (int): The expiration time in seconds for the cache.

    Returns:
        Callable: The wrapped function with caching functionality.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(url: str) -> str:
            """Wraps the original function to add caching."""
            r = redis.Redis()

            # Increment the access count for the URL
            r.incr(f"count:{url}")

            # Check if the page is already cached
            cached_page = r.get(url)
            if cached_page:
                return cached_page.decode('utf-8')

            # Call the original function to fetch the page
            page_content = func(url)

            # Cache the result with expiration
            r.setex(url, expiration, page_content)

            return page_content

        return wrapper
    return decorator


@cache_expiration(10)
def get_page(url: str) -> str:
    """
    Fetch the HTML content of a URL.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content of the page.
    """
    response = requests.get(url)
    return response.text
