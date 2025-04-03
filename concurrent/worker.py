'''Worker function for perfects.py

Note: when using concurrent.futures.InterpreterPoolExecutor functions in the __main__ module
cannot be pickled and so cannot be used.

This is the main purpose of this module being separated.

See https://docs.python.org/3.14/library/concurrent.futures.html#interpreterpoolexecutor

'''

import logging
from dataclasses import dataclass
from functools import reduce


@dataclass
class WorkerContext:
    prefix: str
    idx: int
    rng: tuple[int]

    @property
    def name(self) -> str:
        rc = f'{self.prefix}-{self.idx}' if len(self.prefix) > 0 else ''
        return rc


def find_perfect_numbers_range(ctx: WorkerContext) -> list[int]:
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

    logging.debug(f'{ctx.name} processing ({ctx.rng[0]:_}, {ctx.rng[-1]:_})')

    rc = [i for i in range(ctx.rng[0], ctx.rng[-1]+1) if _is_perfect_number(i)]

    return rc
