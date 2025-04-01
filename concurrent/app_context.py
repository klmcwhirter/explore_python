'''Arg parsing and context model for perfects.py'''

import argparse
import concurrent.futures
import logging
import os
import sys
import sysconfig
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Generator


class ExecutionMode(StrEnum):
    Single = auto()
    Interpreters = auto()
    Processes = auto()
    Threads = auto()


MODE_2_WORKER_NAME = {
    ExecutionMode.Interpreters: 'Interp',
    ExecutionMode.Processes: 'Worker',
    ExecutionMode.Single: '',
    ExecutionMode.Threads: 'Thread'
}


@dataclass
class AppContext:
    mode: ExecutionMode = field(init=False)

    max_n: int = 1_000_000  # 33_551_000 -> 33_550_336

    # see https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ProcessPoolExecutor
    # see https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
    num_workers: int = min(12, os.process_cpu_count() or 1)

    verbose: bool = False

    def __post_init__(self):
        self.mode = ExecutionMode.Threads if self.gil_disabled else ExecutionMode.Processes

    @property
    def executor_cls(self) -> concurrent.futures.Executor:

        return concurrent.futures.ThreadPoolExecutor if self.mode == ExecutionMode.Threads \
            else concurrent.futures.InterpreterPoolExecutor if self.mode == ExecutionMode.Interpreters \
            else concurrent.futures.ProcessPoolExecutor if self.mode == ExecutionMode.Processes \
            else concurrent.futures.Executor  # fallback to abstract class

    @property
    def gil_config(self) -> int | None:
        return sysconfig.get_config_vars().get('Py_GIL_DISABLED')

    @property
    def gil_disabled(self) -> int:
        return self.gil_config is not None and self.gil_config == 1

    def log_exec_ctx(self) -> None:
        logging.debug(f'{sys.version=}')

        self.log_gil_availability()

        logging.debug(self)

    def log_gil_availability(self) -> None:
        if self.gil_config is None:
            msg = 'GIL cannot be disabled'
        elif self.gil_config == 0:
            msg = 'GIL is active'
        elif self.gil_config == 1:
            msg = 'GIL is disabled'

        logging.debug(msg)

    def set_from_args(self, args: argparse.Namespace) -> None:
        # print(args)
        self.max_n = args.max_n
        self.num_workers = args.num_workers

        self.mode = ExecutionMode.Single if args.single_thread \
            else ExecutionMode.Interpreters if args.interpreters \
            else ExecutionMode.Processes if args.processes \
            else ExecutionMode.Threads if args.threads \
            else self.mode

        self.verbose = args.verbose

    def setup_logging(self) -> None:
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(level=log_level, format='{asctime} - {module} - {funcName} - {levelname} - {message}', style='{')

    def worker_prefix(self) -> str:
        prefix = MODE_2_WORKER_NAME[self.mode]
        return prefix


@contextmanager
def parse_args() -> Generator[AppContext, None, None]:
    '''parses cli args and returns app context'''

    ctx = AppContext()

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--max-n', type=int, default=ctx.max_n,
                        help=f'look for perfect numbers up to and including this value (default: {ctx.max_n:_})')
    parser.add_argument('-w', '--num-workers', type=int, default=ctx.num_workers,
                        help=f'number of worker processes to use (default: {ctx.num_workers})')
    parser.add_argument('-i', '--interpreters', default=False, action='store_true',
                        help=f'force use of interpreters in threads')
    parser.add_argument('-p', '--processes', default=False, action='store_true',
                        help=f'force use of processes instead of threads')
    parser.add_argument('-s', '--single-thread', default=False, action='store_true',
                        help=f'force use of no parallelization')
    parser.add_argument('-t', '--threads', default=False, action='store_true',
                        help=f'force use of threads instead of processes')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='Enable verbose mode')

    args = parser.parse_args()
    ctx.set_from_args(args)

    ctx.setup_logging()
    ctx.log_exec_ctx()

    yield ctx
