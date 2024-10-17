import logging
from functools import partial, wraps
from math import factorial
from typing import Callable, Optional

# logging.basicConfig(level=logging.INFO, format='{asctime} - {module} - {funcName} - {levelname} - {message}', style='{')

config = {
    'CACHE_SIZE': 10,
    'PROGRESS_FREQ': 1_000,
}


def set_cache_size(size: int) -> None:
    config['CACHE_SIZE'] = size


def set_progress_frequency(frequency: int) -> None:
    config['PROGRESS_FREQ'] = frequency


ProgressEmitter = Callable[[str], None]

print_flush = partial(print, flush=True)
progress_logger = logging.info

ProgressFreqProvider = Callable[[], int]


def progress_emitter(*, frequency: ProgressFreqProvider, emitter: ProgressEmitter = progress_logger):
    def decorator(func):
        _counter: int = 0

        def _try_emit_progress() -> None:
            if (_counter % frequency()) == 0:
                emitter(f'progress at {_counter} - {frequency()=}')

        def _reset() -> None:
            nonlocal _counter
            _counter = 0

        func.counter = lambda: _counter
        func.counter_reset = _reset

        @wraps(func)
        def _wrapper(*args, **kwargs):
            nonlocal _counter
            _counter += 1
            _try_emit_progress()
            return func(*args, **kwargs)

        return _wrapper
    return decorator


_CacheInitialCreator = Callable[[], list[Optional[int]]]


def cache(*, initial: _CacheInitialCreator):
    _initial = initial
    _cache = _initial().copy()

    def decorator(func):
        func.cache = _cache
        func.cache_initial = _initial()

        def _reset() -> None:
            _cache.clear()
            _cache.extend(_initial())
            print_flush(f'cache_reset: {len(_cache)=}')
        func.cache_reset = _reset

        @wraps(func)
        def _cache_wrapper(key: int):
            if _cache[key] is not None:
                return _cache[key]

            progress_logger(f'@cache: cache miss at n={key}')  # => {_cache[key]}')

            val = func(key)
            _cache[key] = val

            return val

        return _cache_wrapper

    return decorator


initial_factorial_cache: _CacheInitialCreator = lambda: [1, 1, 2, *[None] * (config['CACHE_SIZE'] - 3 + 1)]


@progress_emitter(frequency=lambda: config['PROGRESS_FREQ'], emitter=progress_logger)
@cache(initial=initial_factorial_cache)
def cached_factorial(n: int) -> int:
    rc = cached_factorial.cache[n]
    if rc is not None:
        return rc

    for i in range(3, n + 1):
        # Note that this should not happen - but be safe
        if cached_factorial.cache[i-1] is not None:
            rc = cached_factorial.cache[i-1]
        else:
            progress_logger(f'cached_factorial: cache miss at n={i-1}')

            rc = factorial(i - 1)
            cached_factorial.cache[i - 1] = rc

        rc *= i
        cached_factorial.cache[i] = rc

    return rc
