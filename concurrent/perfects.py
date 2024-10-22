#!/usr/bin/python3.13
'''
Calculate perfect numbers up to max_n using threads or processes.

Also has support for /usr/bin/python3.13t - NoGIL
'''

import argparse
import concurrent.futures
import logging
import os
import sys
import sysconfig
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import reduce
from typing import Generator


@dataclass
class AppContext:
    threads: bool = False

    max_n: int = 1_000_000  # 34_000_000 -> 33_550_336

    # see https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor
    # see https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
    num_workers: int = min(12, os.process_cpu_count() or 1)

    verbose: bool = False

    def __post_init__(self):
        self.threads = not self.gil_disabled

    @property
    def executor_cls(self) -> concurrent.futures.Executor:
        return concurrent.futures.ThreadPoolExecutor if self.threads else concurrent.futures.ProcessPoolExecutor

    @property
    def gil_config(self) -> int:
        return sysconfig.get_config_vars().get('Py_GIL_DISABLED')

    @property
    def gil_disabled(self) -> int:
        return self.gil_config != 1

    @property
    def worker_prefix(self) -> str:
        return 'Thread' if self.threads else 'Worker'

    def log_exec_ctx(self):
        logging.debug(f'{sys.version=}')

        if self.gil_config is None:
            msg = 'GIL cannot be disabled'
        elif self.gil_config == 0:
            msg = 'GIL is active'
        elif self.gil_config == 1:
            msg = 'GIL is disabled'

        logging.debug(msg)
        logging.debug(self)

    def set_from_args(self, args: argparse.Namespace) -> None:
        # print(args)
        self.max_n = args.max_n
        self.num_workers = args.num_workers
        self.threads = False if args.processes else args.threads
        self.verbose = args.verbose


@contextmanager
def parse_args() -> Generator[AppContext, None, None]:
    ctx = AppContext()

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--max-n', type=int, default=ctx.max_n,
                        help=f'look for perfect numbers up to and including this value (default: {ctx.max_n:_})')
    parser.add_argument('-w', '--num-workers', type=int, default=ctx.num_workers,
                        help=f'number of worker processes to use (default: {ctx.num_workers})')
    parser.add_argument('-p', '--processes', default=False, action='store_true',
                        help=f'force use of processes instead of threads (default: {ctx.gil_disabled})')
    parser.add_argument('-t', '--threads', default=(not ctx.gil_disabled), action='store_true',
                        help=f'force use of threads instead of processes (default: {not ctx.gil_disabled})')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='Enable verbose mode')

    args = parser.parse_args()
    ctx.set_from_args(args)

    log_level = logging.DEBUG if ctx.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='{asctime} - {module} - {funcName} - {levelname} - {message}', style='{')

    ctx.log_exec_ctx()

    yield ctx


def find_perfect_numbers_range(*rng: int, idx: int, worker_prefix: str) -> list[int]:
    def _is_perfect(n: int) -> bool:
        def _factors(n: int) -> set[int]:
            return set(reduce(
                list.__add__,
                ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0),
                []
            ))

        return n == sum([f for f in _factors(n) if n != f])

    logging.debug(f'{worker_prefix}-{idx} processing ({rng[0]:_}, {rng[-1]:_})')

    rc = [i for i in range(rng[0], rng[1]+1) if _is_perfect(i)]

    return rc


def find_perfect_numbers(ctx: AppContext) -> list[int]:
    def _batched_by_work_for_workers(max_n: int, num_workers: int) -> list[tuple[int, int]]:
        '''Distribute work evenly across all workers; returns list of begin/end number ranges'''

        windows = [(0, 0)] * num_workers

        items_per_worker = int(max_n // num_workers) + 1

        last_idx = 1
        for t in range(num_workers):
            next_idx = min(max_n, last_idx + items_per_worker)

            windows[t] = (last_idx, next_idx)

            if next_idx >= max_n:
                break

            last_idx = next_idx + 1

        return windows

    results = set[int]()

    with ctx.executor_cls(max_workers=ctx.num_workers) as executor:
        futures = {
            executor.submit(find_perfect_numbers_range, *rng, idx=idx, worker_prefix=ctx.worker_prefix): idx
            for idx, rng in enumerate(_batched_by_work_for_workers(ctx.max_n, ctx.num_workers))
        }

        for future in concurrent.futures.as_completed(futures):
            idx = futures[future]
            result = future.result()

            if result and len(result) > 0:
                logging.debug(f'Adding result from {ctx.worker_prefix}-{idx}')
                results.update(result)
            else:
                logging.debug(f'Skipping empty result from {ctx.worker_prefix}-{idx}')

    return sorted(list(results))


if __name__ == '__main__':
    with parse_args() as ctx:
        logging.debug('bootstrapping ...')

        start_time = datetime.now()
        result = find_perfect_numbers(ctx)
        elapsed_time: timedelta = datetime.now() - start_time
        logging.info(f'{result} are perfect numbers in {elapsed_time}')

        logging.debug('done.')
