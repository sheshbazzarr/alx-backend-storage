#!/usr/bin/env python3
"""
This module provides a Cache class that interacts with a Redis database.
The Cache class allows storing data of various types using randomly generated keys.
"""

import redis
import uuid
from typing import Union

class Cache:
    """
    Cache class that provides methods to store data in a Redis database.
    Upon initialization, the Redis database is flushed to ensure a clean state.
    """

    def __init__(self):
        """
        Initialize Redis client and flush the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a randomly generated key.
        
        Args:
            data (Union[str, bytes, int, float]): The data to store.
            
        Returns:
            str: The key under which the data is stored.
        """
        key = str(uuid.uuid4())  # Generate a random key
        self._redis.set(key, data)  # Store the data in Redis
        return key

