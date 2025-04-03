#!/usr/bin/python3.14
'''
Calculate perfect numbers up to max_n using threads, interpreters or processes.

Also has support for /usr/bin/python3.14t - NoGIL
'''

import concurrent.futures
import logging
import multiprocessing as mp
from datetime import datetime, timedelta

from app_context import AppContext, ExecutionMode, parse_args
from worker import WorkerContext, find_perfect_numbers_range


def find_perfect_numbers(ctx: AppContext) -> list[int]:
    '''Orchestrates the process for finding perfect numbers'''

    if ctx.mode == ExecutionMode.Single:
        worker_ctx = WorkerContext(prefix=ctx.worker_prefix(), idx=0, rng=(1, ctx.max_n))
        return find_perfect_numbers_range(ctx=worker_ctx)

    results = set[int]()

    with ctx.executor_cls(max_workers=ctx.num_workers, initializer=ctx.setup_logging) as executor:
        '''Use executor to parallelize the process of finding perfect numbers'''

        def _number_ranges(max_n: int, num_workers: int) -> list[tuple[int, int]]:
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

        _worker_contexts = [
            WorkerContext(prefix=ctx.worker_prefix(), idx=idx, rng=rng)
            for idx, rng in enumerate(_number_ranges(ctx.max_n, ctx.num_workers))
        ]

        futures = {
            executor.submit(find_perfect_numbers_range, ctx=worker_ctx): worker_ctx
            for worker_ctx in _worker_contexts
        }

        for future in concurrent.futures.as_completed(futures):
            worker_ctx = futures[future]
            result = future.result()

            if result and len(result) > 0:
                logging.debug(f'Adding result from {worker_ctx.name}')
                results.update(result)
            else:
                logging.debug(f'Skipping empty result from {worker_ctx.name}')

    return sorted(list(results))


if __name__ == '__main__':
    mp.set_start_method('spawn')  # in case --processes is requested

    with parse_args() as ctx:
        logging.debug('starting ...')
        start_time = datetime.now()

        result = find_perfect_numbers(ctx)

        elapsed_time: timedelta = datetime.now() - start_time
        logging.info(f'{result} are perfect numbers in {elapsed_time}')

        logging.debug('done.')
