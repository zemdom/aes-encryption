import asyncio
from functools import wraps, partial
from queue import SimpleQueue


def asynchronous(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


class AsyncQueue(SimpleQueue):
    @asynchronous
    def async_get(self):
        return self.get()

    def async_put(self, data):
        self.put(data)
