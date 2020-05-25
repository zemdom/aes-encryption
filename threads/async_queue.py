import asyncio
import janus
from functools import wraps, partial
from threading import Event


def asynchronous(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_running_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


class AsyncQueue(janus.Queue):
    def __init__(self):
        self.loop = None
        self.created = Event()
        self.created.clear()

    def create(self, loop):
        if not self.created.is_set():
            self.created.set()
            self.loop = loop
            # super().__init__(maxsize=0, loop=self.loop)
            super().__init__(maxsize=0)

    def sync_get(self):
        self.__sync_wait_until_created()
        return self.sync_q.get()

    def __sync_wait_until_created(self):
        self.created.wait()

    async def async_get(self):
        await self.__async_wait_until_created()
        return await self.async_q.get()

    async def __async_wait_until_created(self):
        await asynchronous(self.__sync_wait_until_created)()

    def sync_put(self, data):
        self.__sync_wait_until_created()
        self.sync_q.put(data)

    def close(self):
        self.created.clear()
