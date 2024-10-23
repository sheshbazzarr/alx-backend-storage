#!/usr/bin/env python3
"""
This module provides a Cache class and functions to replay the history of function calls.
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a function in Redis.
    """
    @wraps(method)
    def wrapper(*args, **kwargs):
        self = args[0]
        redis_client = self._redis

        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        redis_client.rpush(input_key, str(args[1:]))
        output = method(*args, **kwargs)
        redis_client.rpush(output_key, str(output))

        return output

    return wrapper


class Cache:
    """
    Cache class that interacts with Redis and supports history tracking.
    """

    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        return self.get(key, fn=int)


def replay(method: Callable) -> None:
    """
    Function to display the history of calls to a function.
    """
    self = method.__self__
    redis_client = self._redis

    input_key = f"{method.__qualname__}:inputs"
    output_key = f"{method.__qualname__}:outputs"

    inputs = redis_client.lrange(input_key, 0, -1)
    outputs = redis_client.lrange(output_key, 0, -1)

    print(f"{method.__qualname__} was called {len(inputs)} times:")

    for input_val, output_val in zip(inputs, outputs):
        input_str = input_val.decode("utf-8")
        output_str = output_val.decode("utf-8")
        print(f"{method.__qualname__}(*{input_str}) -> {output_str}")

