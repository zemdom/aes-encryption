import asyncio
import sys
import threading

from encryption.message_handler import ReceiverMessageHandler
from communication.server import ServerProtocol
from threads.async_queue import AsyncQueue


def create_receiver_thread(ingoing_plaindata):
    ingoing_data = AsyncQueue()
    threading.Thread(target=run_receiver, args=(ingoing_data, ingoing_plaindata, 55555)).start()


def run_receiver(ingoing_data, ingoing_plaindata, port):
    asyncio.run(run_receiver_mainloops(ingoing_data, ingoing_plaindata, port))
    print('[RECEIVER] Exiting thread')
    # after finishing coroutine, end thread
    sys.exit()


async def run_receiver_mainloops(ingoing_data, ingoing_plaindata, port):
    loop = asyncio.get_running_loop()

    connection_open = [True]  # flag needs to be a mutable object to change its value between classes
    receiver_message_handler = ReceiverMessageHandler(ingoing_data, ingoing_plaindata, connection_open, encrypt=False)
    await asyncio.gather(receiver_message_handler.start_mainloop(),
                         create_server(loop, ingoing_data, port, connection_open), loop=loop)

    # loop.close()


async def create_server(loop, ingoing_data, port, connection_open):
    server = await loop.create_server(lambda: ServerProtocol(ingoing_data, connection_open), '127.0.0.1', port)
    async with server:
        await server.serve_forever()
