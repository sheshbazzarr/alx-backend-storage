#!/usr/bin/env python3
"""
This module provides a Cache class that interacts with a Redis database.
It also includes a decorator to store the history of function inputs and outputs in Redis.
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a particular function in Redis.
    Inputs are stored in a list under the key "<method.__qualname__>:inputs",
    and outputs are stored under the key "<method.__qualname__>:outputs".

    Args:
        method (Callable): The function to be decorated.

    Returns:
        Callable: The wrapped function that stores its input/output history.
    """
    @wraps(method)
    def wrapper(*args, **kwargs):
        """Wrapper function to log inputs and outputs of the method in Redis."""
        self = args[0]  # Cache instance
        inputs_key = f"{method.__qualname__}:inputs"
        outputs_key = f"{method.__qualname__}:outputs"

        # Store input arguments in Redis
        self._redis.rpush(inputs_key, str(args[1:]))  # Ignore self in args

        # Call the original method
        output = method(*args, **kwargs)

        # Store the output in Redis
        self._redis.rpush(outputs_key, str(output))

        return output

    return wrapper


class Cache:
    """
    Cache class that provides methods to store and retrieve data in a Redis database.
    Upon initialization, the Redis database is flushed to ensure a clean state.
    """

    def __init__(self):
        """Initialize Redis client and flush the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a randomly generated key.

        Args:
            data (Union[str, bytes, int, float]): The data to store.

        Returns:
            str: The key under which the data is stored.
        """
        key = str(uuid.uuid4())  # Generate a random key
        self._redis.set(key, data)  # Store data in Redis with the key
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally apply a conversion function.

        Args:
            key (str): The Redis key.
            fn (Optional[Callable]): A callable that converts the Redis data to the desired format.

        Returns:
            Union[str, bytes, int, float, None]: The retrieved data, optionally converted, or None if the key does not exist.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a string from Redis.

        Args:
            key (str): The Redis key.

        Returns:
            Optional[str]: The retrieved string, or None if the key does not exist.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer from Redis.

        Args:
            key (str): The Redis key.

        Returns:
            Optional[int]: The retrieved integer, or None if the key does not exist.
        """
        return self.get(key, fn=int)

