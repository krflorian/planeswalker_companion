import asyncio
from typing import AsyncGenerator

from .logging import get_logger

logger = get_logger(__name__)


def to_sync_generator(async_gen: AsyncGenerator):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        while True:
            yield loop.run_until_complete(anext(async_gen))
    except StopAsyncIteration:
        logger.info("stop iteration")
    finally:
        loop.close()
