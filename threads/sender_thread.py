import asyncio
import sys
import threading

from encryption.message_handler import SenderMessageHandler
from communication.socket import SocketProtocol
from threads.async_queue import AsyncQueue


def create_sender_thread(outgoing_plaindata):
    outgoing_data = AsyncQueue()
    threading.Thread(target=run_sender, args=(outgoing_data, outgoing_plaindata, '127.0.0.1', 55555)).start()


def run_sender(outgoing_data, outgoing_plaindata, host, port):
    asyncio.run(run_sender_mainloops(outgoing_data, outgoing_plaindata, host, port))
    print('[SENDER] Exiting thread')
    sys.exit()  # after finishing coroutine, end thread


async def run_sender_mainloops(outgoing_data, outgoing_plaindata, host, port):
    loop = asyncio.get_running_loop()

    connection_open = [True]  # flag needs to be a mutable object to change its value between classes
    sender_message_handler = SenderMessageHandler(outgoing_plaindata, outgoing_data, connection_open)
    await asyncio.gather(sender_message_handler.start_mainloop(),
                         create_client(loop, outgoing_data, host, port, connection_open), loop=loop)

    # loop.close()


async def create_client(loop, outgoing_data, host, port, connection_open):
    while connection_open[0]:
        message_sent = False
        message = await outgoing_data.async_get()
        while not message_sent:
            on_con_lost = loop.create_future()
            transport, protocol = await loop.create_connection(lambda: SocketProtocol(message, on_con_lost), host, port)

            # wait until the protocol signals that the connection is lost and close the transport
            try:
                await on_con_lost
                message_sent = on_con_lost.result()
                print('Message sent: {}'.format(message_sent))
            finally:
                transport.close()
