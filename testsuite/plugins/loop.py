import asyncio
import contextlib

import pytest
import uvloop


@pytest.fixture(scope='session')
def event_loop():
    """
    One event loop for all tests.
    """
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    with contextlib.closing(loop):
        yield loop


@pytest.fixture(scope='session')
def loop(event_loop):
    return event_loop
