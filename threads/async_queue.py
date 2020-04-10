import asyncio
from functools import wraps, partial
from queue import _PySimpleQueue


def asynchronous(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


class AsyncQueue(_PySimpleQueue):
    def __init__(self):
        super().__init__()

    @asynchronous
    def async_get(self):
        return self.get()

    def async_put(self, data):
        self.put(data)

    # TODO
    # def async_clear(self):
    #     while not self.empty():
    #         self.get_nowait()
    #     pass

    def async_empty(self):
        while not self.empty():
            continue
