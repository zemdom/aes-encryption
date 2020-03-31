import asyncio
import threading

from encryption.message_handler import SenderMessageHandler
from communication.socket import SocketProtocol
from threads.async_queue import AsyncQueue


def create_sender_thread(outgoing_plaindata):
    outgoing_data = AsyncQueue()
    threading.Thread(target=run_sender, args=(outgoing_data, outgoing_plaindata, '127.0.0.1', 55555)).start()


def run_sender(outgoing_data, outgoing_plaindata, host, port):
    asyncio.run(run_sender_mainloops(outgoing_data, outgoing_plaindata, host, port))


async def run_sender_mainloops(outgoing_data, outgoing_plaindata, host, port):
    loop = asyncio.get_running_loop()

    sender_message_handler = SenderMessageHandler('public_key', outgoing_plaindata, outgoing_data)
    await asyncio.gather(sender_message_handler.start_mainloop(), create_client(loop, outgoing_data, host, port),
                         loop=loop)

    loop.close()


async def create_client(loop, outgoing_data, host, port):
    while True:  # TODO
        message_sent = False
        message = await outgoing_data.async_get()
        # message = SenderMessageHandler.pack_message(*message)
        while not message_sent:
            on_con_lost = loop.create_future()
            transport, protocol = await loop.create_connection(lambda: SocketProtocol(message, on_con_lost), host, port)

            # wait until the protocol signals that the connection is lost and close the transport
            try:
                await on_con_lost
                message_sent = on_con_lost.result()
                print(message_sent)
            finally:
                transport.close()
