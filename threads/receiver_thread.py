import asyncio
import threading

from encryption.message_handler import ReceiverMessageHandler
from communication.server import ServerProtocol
from threads.async_queue import AsyncQueue


def create_receiver_thread(ingoing_plaindata):
    ingoing_data = AsyncQueue()
    threading.Thread(target=run_receiver, args=(ingoing_data, ingoing_plaindata, 55555)).start()


def run_receiver(ingoing_data, ingoing_plaindata, port):
    asyncio.run(run_receiver_mainloops(ingoing_data, ingoing_plaindata, port))


async def run_receiver_mainloops(ingoing_data, ingoing_plaindata, port):
    loop = asyncio.get_running_loop()

    receiver_message_handler = ReceiverMessageHandler('private_key', ingoing_data, ingoing_plaindata, encrypt=False)
    await asyncio.gather(receiver_message_handler.start_mainloop(), create_server(loop, ingoing_data, port), loop=loop)

    loop.close()


async def create_server(loop, ingoing_data, port):
    server = await loop.create_server(lambda: ServerProtocol(ingoing_data), '127.0.0.1', port)
    async with server:
        await server.serve_forever()
