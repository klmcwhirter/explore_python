
import pytest


def pytest_addoption(parser):
    parser.addoption("--run-slow", action="store_true", default=False, help="run slow tests"),
    parser.addoption("--run-slowest", action="store_true", default=False, help="run slowest tests"),


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")
    config.addinivalue_line("markers", "slowest: mark test as slowest to run")


def pytest_collection_modifyitems(config, items):
    # order is important here - process slowest before slow
    if config.getoption("--run-slowest"):
        # --run-slowest given in cli: do not skip slowest or slow tests
        return
    skip_slowest = pytest.mark.skip(reason="need --run-slowest option to run")
    for item in items:
        if "slowest" in item.keywords:
            item.add_marker(skip_slowest)

    if config.getoption("--run-slow"):
        # --run-slow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
