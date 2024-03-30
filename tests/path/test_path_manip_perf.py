
import gc
import os
import time
import timeit
from collections import defaultdict
from contextlib import contextmanager
from typing import Callable

import pytest

SOME_IMG_PATH = '/some/path/tiles.png'
MAP_EXT = '.map'

# region unit tests


@pytest.mark.parametrize(
    'image_path',
    [
        # ext removed
        (SOME_IMG_PATH[:SOME_IMG_PATH.rfind('.')]),

        # ext intact
        (SOME_IMG_PATH),
    ]
)
def test_slice_when_no_ext_should_give_root_path(image_path) -> None:
    print(f'\n{image_path=}')
    assert len(image_path) > 0

    # act without Path or os.path involved
    image_path = image_path[:image_path.rfind('.')]

    print(f'after {image_path=}')
    assert len(image_path) > 0

# endregion unit tests

# region perf tests


def slice_with_concat() -> None:
    image = SOME_IMG_PATH
    _ = image[:image.rfind('.')] + MAP_EXT


def slice_with_fstring() -> None:
    image = SOME_IMG_PATH
    _ = f'{image[:image.rfind('.')]}{MAP_EXT}'


def path_with_concat() -> None:
    _ = os.path.splitext(SOME_IMG_PATH)[0] + MAP_EXT


def path_with_fstring() -> None:
    image_root = os.path.splitext(SOME_IMG_PATH)[0]
    _ = f'{image_root}{MAP_EXT}'


@pytest.fixture(scope='module')
def timings():
    rc = defaultdict[str, list[object]](list[object])
    yield rc

    print('\n\ntimings captured:')

    from pprint import pprint
    pprint(rc, sort_dicts=True, width=130, underscore_numbers=True)


def capture_timing(number: int, time_taken: int, name: str, timings: defaultdict[str, list[object]]) -> None:
    timings[name].append({
        'number': number,
        'time_taken_ns': time_taken
    })


@contextmanager
def force_gc():
    yield

    gc.enable()
    gc.collect()
    gc.disable()


@pytest.fixture
def timeit_setup():
    def wrapper(gc_enable: bool) -> str:
        return 'gc.enable()' if gc_enable else ''

    return wrapper


@pytest.mark.parametrize(
    'number,func,gc_enable',
    [
        (2_000_000, path_with_concat, True),
        pytest.param(10_000_000, path_with_concat, True, marks=pytest.mark.slow),
        pytest.param(25_000_000, path_with_concat, True, marks=pytest.mark.slow),
        pytest.param(50_000_000, path_with_concat, True, marks=pytest.mark.slowest),

        (2_000_000, path_with_concat, False),
        pytest.param(10_000_000, path_with_concat, False, marks=pytest.mark.slow),
        pytest.param(25_000_000, path_with_concat, False, marks=pytest.mark.slow),
        pytest.param(50_000_000, path_with_concat, False, marks=pytest.mark.slowest),

        (2_000_000, path_with_fstring, True),
        pytest.param(10_000_000, path_with_fstring, True, marks=pytest.mark.slow),
        pytest.param(25_000_000, path_with_fstring, True, marks=pytest.mark.slow),
        pytest.param(50_000_000, path_with_fstring, True, marks=pytest.mark.slowest),

        (2_000_000, path_with_fstring, False),
        pytest.param(10_000_000, path_with_fstring, False, marks=pytest.mark.slow),
        pytest.param(25_000_000, path_with_fstring, False, marks=pytest.mark.slow),
        pytest.param(50_000_000, path_with_fstring, False, marks=pytest.mark.slowest),

        (2_000_000, slice_with_concat, True),
        (10_000_000, slice_with_concat, True),
        pytest.param(25_000_000, slice_with_concat, True, marks=pytest.mark.slow),
        pytest.param(50_000_000, slice_with_concat, True, marks=pytest.mark.slow),

        (2_000_000, slice_with_concat, False),
        (10_000_000, slice_with_concat, False),
        pytest.param(25_000_000, slice_with_concat, False, marks=pytest.mark.slow),
        pytest.param(50_000_000, slice_with_concat, False, marks=pytest.mark.slow),

        (2_000_000, slice_with_fstring, True),
        (10_000_000, slice_with_fstring, True),
        pytest.param(25_000_000, slice_with_fstring, True, marks=pytest.mark.slow),
        pytest.param(50_000_000, slice_with_fstring, True, marks=pytest.mark.slow),

        (2_000_000, slice_with_fstring, False),
        (10_000_000, slice_with_fstring, False),
        pytest.param(25_000_000, slice_with_fstring, False, marks=pytest.mark.slow),
        pytest.param(50_000_000, slice_with_fstring, False, marks=pytest.mark.slow),
    ]
)
def test_slice_capture_timing(number: int, func: Callable[[], None], gc_enable: bool,
                              timeit_setup, timings) -> None:
    with force_gc():
        timer = timeit.Timer(stmt=func, setup=timeit_setup(gc_enable), timer=time.perf_counter_ns)

        time_taken = timer.timeit(number)

        gc = '_gc' if gc_enable else ''
        capture_timing(number=number, time_taken=time_taken, name=f'{func.__name__}{gc}', timings=timings)

# endregion perf tests
