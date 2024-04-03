
from collections import defaultdict
from typing import Mapping

import pytest


def gen_table(table: list[object]) -> str:
    rc = '\n\nCaptured timings (secs):\n'

    from tabulate import tabulate
    rc += tabulate(
        table,
        headers='keys',
        tablefmt='rounded_grid',
        intfmt=',',
    )

    return rc


def pivot_timings(captured_timings: Mapping[int, list[dict]]) -> list[dict]:
    """ pivot timings by iterations, name"""

    headers: list[str] = sorted(
        event['name']
        for k, grp in captured_timings.items() if k == 2_000_000
        for event in grp
    )

    pivot = [
        {
            'Iterations': iteration,
            **{
                h: event['time_taken'] if event and 'time_taken' in event else ''
                for h in headers
                for event in grp if event['name'] == h
            }
        }
        for iteration, grp in captured_timings.items()
    ]

    return pivot


@pytest.fixture(scope='module')
def timings():
    rc: Mapping[int, list[dict]] = defaultdict[int, list[dict]](list[dict])
    yield rc

    pivot = pivot_timings(rc)
    table = gen_table(pivot)
    print(table)


@pytest.fixture
def capture_timing():
    def wrapper(number: int, time_taken: float, name: str, timings_map: Mapping[int, list[dict]]):
        timings_map[number].append({
            'name': name,
            'number': number,
            'time_taken': time_taken
        })
    return wrapper
