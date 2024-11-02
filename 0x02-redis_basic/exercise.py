#!/usr/bin/env python3
""" A cache class. """
import redis
from uuid import uuid4
from typing import Union, Callable, Optional
from functools import wraps

def count_calls(method: Callable) -> Callable:
    """ Decorator to count how many times a method is called. """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper

def call_history(method: Callable) -> Callable:
    """ Decorator to store the history of inputs and outputs for a particular function."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # Generate Redis keys for storing inputs and outputs
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Convert args to string and push to the inputs list.
        self._redis.rpush(input_key, str(args))

        # Call the original method and get the output
        output = method(self, *args, **kwargs)

        # Store the output in the outputs list
        self._redis.rpush(output_key, output)

        return output

    return wrapper

def replay(method: Callable) -> None:
    r = redis.Redis()
    # Dispaly the history of calls to a particular fucntion.
    input_key = f"{method.__qualname__}:inputs"
    output_key = f"{method.__qualname__}:outputs"

    # Retreive the input and outputs from Redis
    inputs = r.lrange(input_key, 0, -1)
    outputs = r.lrange(output_key, 0, -1)

    # count the number of calls
    call_count = len(inputs)

    print(f"{method.__qualname__} was called {call_count} times:")

    # Loops through inputs and outputs
    for input_data, output_data in zip(inputs, outputs):
        # decode the input and output
        decoded_input = input_data.decode('utf-8')
        decoded_output = output_data.decode('utf-8')
        print(f"{method.__qualname__}(*({decoded_input},)) -> {decoded_output}")


class Cache:
    """ A Cache class. """
    def __init__(self):
        """ Initialize a Redis client and store it as a private variable """
        self._redis = redis.Redis()

        """ Flush the Redis database to clear any existing data."""
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
            Method that stores the cache. """
        key = str(uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None)\
            -> Optional[Union[str, bytes, int, float]]:
        """Retrieve the value from Redis by key and apply the conversion function if provided."""
        value = self._redis.get(key)
        if value is None:
            return None
        if fn:
            return fn(value)
        return value

    def get_str(self, key: str) -> str:
        """ Get a value from Redis and convert it to a string."""
        value = self.get(key)
        if value is None:
            return None
        return value.decode("utf-8")

    def get_int(self, key: str) -> int:
        """ Get a value from Redis and convert it to an integer."""
        return self.get(key, fn=int)
