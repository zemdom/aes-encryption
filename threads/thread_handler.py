import asyncio
import threading

from communication.socket import SocketProtocol
from encryption.message_handler import ReceiverMessageHandler, SenderMessageHandler
from communication.server import ServerProtocol
from threads.async_queue import AsyncQueue


class ThreadHandler:
    def __init__(self):
        self.name = None
        self.connection_open = [True]  # flag needs to be a mutable object to change its value inside other objects
        self.thread = None
        self.task = None

    def create(self, rsa_key, queue_plaindata, address):
        queue_data = AsyncQueue()
        self.thread = threading.Thread(target=self._run_asyncio_task,
                                       args=(rsa_key, queue_data, queue_plaindata, address),
                                       name='{} thread'.format(self.name))
        self.thread.start()

    def _run_asyncio_task(self, key, queue_data, queue_plaindata, address):
        asyncio.run(self._run_mainloops(key, queue_data, queue_plaindata, address))
        print('[{}] Exiting thread'.format(self.name))

    async def _run_mainloops(self, key, queue_data, queue_plaindata, address):
        loop = asyncio.get_running_loop()
        message_handler = self._create_message_handler(key, queue_data, queue_plaindata)

        self.task = asyncio.create_task(self._create_task(loop, message_handler, queue_data, address))

        try:
            await self.task
        except asyncio.CancelledError:
            print('[{0}] Closing {1} thread'.format(self.name, self.name.lower()))

    def _create_message_handler(self, key, queue_data, queue_plaindata):
        pass

    async def _create_task(self, loop, message_handler, queue_data, address):
        await asyncio.gather(message_handler.start_mainloop(),
                             self._create_connection(loop, queue_data, address),
                             self.__wait_for_task_to_close(), loop=loop)

    def _create_connection(self, loop, data, address):
        pass

    async def __wait_for_task_to_close(self):
        await self.__check_connection_open()
        self.task.cancel()

    async def __check_connection_open(self):
        while self.connection_open[0]:
            await asyncio.sleep(5)
            print('[{0}] Connection open'.format(self.name))

    def close(self):
        self.connection_open = [False]


class ReceiverThreadHandler(ThreadHandler):
    def __init__(self):
        super().__init__()
        self.name = 'RECEIVER'

    def _create_message_handler(self, private_key, ingoing_data, ingoing_plaindata):
        return ReceiverMessageHandler(private_key, ingoing_data, ingoing_plaindata, self.connection_open, encrypt=False)

    async def _create_connection(self, loop, ingoing_data, port):
        server = await loop.create_server(lambda: ServerProtocol(ingoing_data, self.connection_open), '127.0.0.1', port)

        async with server:
            await server.serve_forever()


class SenderThreadHandler(ThreadHandler):
    def __init__(self):
        super().__init__()
        self.name = 'SENDER'

    def _create_message_handler(self, public_key, outgoing_data, outgoing_plaindata):
        return SenderMessageHandler(public_key, outgoing_plaindata, outgoing_data, self.connection_open)

    async def _create_connection(self, loop, outgoing_data, address):
        host, port = address[0], address[1]

        while self.connection_open[0]:
            message = await outgoing_data.async_get()

            on_con_lost = loop.create_future()
            transport, protocol = await loop.create_connection(lambda: SocketProtocol(message, on_con_lost),
                                                               host, port)

            # wait until the protocol signals that the connection is lost and close the transport
            try:
                await on_con_lost
                message_sent = on_con_lost.result()
                print('[{0}] Message sent: {1}'.format(self.name, message_sent))
            finally:
                transport.close()
