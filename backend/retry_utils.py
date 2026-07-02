"""
Retry utility for handling transient failures in CPU inference operations.
This provides exponential backoff for operations that may fail due to slow CPU inference.
"""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any


def retry_on_failure(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
) -> Callable:
    """
    Decorator to retry a function on failure with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch and retry on
        on_retry: Optional callback function called on each retry (attempt, exception)

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = initial_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        # Final attempt failed, raise the exception
                        raise

                    # Call retry callback if provided
                    if on_retry:
                        on_retry(attempt + 1, e)

                    # Wait before retrying with exponential backoff
                    time.sleep(delay)
                    delay *= backoff_factor

            # This should never be reached, but just in case
            raise last_exception

        return wrapper

    return decorator


def retry_with_logging(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    operation_name: str = "operation",
) -> Callable:
    """
    Decorator to retry with automatic logging of retry attempts.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch and retry on
        operation_name: Name of the operation for logging purposes

    Returns:
        Decorated function with retry logic and logging
    """

    def log_retry(attempt: int, exception: Exception) -> None:
        print(f"Retry {attempt}/{max_retries} for {operation_name}: {exception!s}")

    return retry_on_failure(
        max_retries=max_retries,
        initial_delay=initial_delay,
        backoff_factor=backoff_factor,
        exceptions=exceptions,
        on_retry=log_retry,
    )
