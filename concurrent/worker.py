'''Worker function for perfects.py

Note: when using concurrent.futures.InterpreterPoolExecutor functions in the __main__ module
cannot be pickled and so cannot be used.

This is the main purpose of this module being separated.

See https://docs.python.org/3.14/library/concurrent.futures.html#interpreterpoolexecutor

'''

import logging
from functools import reduce


def find_perfect_numbers_range(rng: tuple[int], idx: int, worker_prefix: str) -> list[int]:
    '''worker function that finds perfect numbers within a range of values for n'''

    def _is_perfect_number(n: int) -> bool:
        '''Determines if n is a perfect number.'''

        def _factors(n: int) -> set[int]:
            '''Returns set of unique factors of n'''

            return set(reduce(
                list.__add__,
                ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0),
                []
            ))

        return n == sum(f for f in _factors(n) if n != f)

    logging.debug(f'{worker_name(worker_prefix=worker_prefix, idx=idx)} processing ({rng[0]:_}, {rng[-1]:_})')

    rc = [i for i in range(rng[0], rng[-1]+1) if _is_perfect_number(i)]

    return rc


def worker_name(worker_prefix: str, idx=0) -> str:
    rc = f'{worker_prefix}-{idx}' if len(worker_prefix) > 0 else worker_prefix
    return rc
