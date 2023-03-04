from functools import wraps
from typing import Any, Callable, TypeVar

T = TypeVar('T', bound=Any)


def gameover(game: Callable[..., T]) -> Callable[..., T | None]:

    @wraps(game)
    def wrapper(*args, **kwargs) -> T | None:
        try:
            return game(*args, **kwargs)
        except KeyboardInterrupt:
            return print(
                '\n'
                '\n'
                'Game Over: process terminated by keyboard interruption.'
            )

    return wrapper
