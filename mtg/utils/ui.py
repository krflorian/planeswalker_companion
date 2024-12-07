import asyncio
from typing import AsyncGenerator

from .logging import get_logger

logger = get_logger(__name__)


def to_sync_generator(async_gen: AsyncGenerator):
    logger.info("Started Generating Response")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        while True:
            yield loop.run_until_complete(anext(async_gen))  # noqa F821
    except StopAsyncIteration:
        logger.info("Finished Generating Response")
    finally:
        loop.close()
