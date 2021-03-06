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

    def create(self, rsa_key, queue_plaindata, shared_data, address, port=None):
        queue_data = AsyncQueue()
        self.thread = threading.Thread(target=self._run_asyncio_task,
                                       args=(rsa_key, queue_data, queue_plaindata, shared_data, address, port),
                                       name=f'{self.name} thread')
        self.thread.start()
        print(f'[{self.name}] Thread created')

    def _run_asyncio_task(self, key, queue_data, queue_plaindata, shared_data, address, port):
        asyncio.run(self._run_mainloops(key, queue_data, queue_plaindata, shared_data, address, port))
        print(f'[{self.name}] Exiting thread')

    async def _run_mainloops(self, key, queue_data, queue_plaindata, shared_data, address, port):
        loop = asyncio.get_running_loop()

        queue_data.create(loop)
        queue_plaindata.create(loop)
        # shared_data.create(loop)

        print(f'[{self.name}] Data queues created')

        message_handler = self._create_message_handler(key, queue_data, queue_plaindata, shared_data, port)

        self.task = asyncio.create_task(self._create_task(loop, message_handler, queue_data, address))

        try:
            await self.task
        except asyncio.CancelledError:
            print(f'[{self.name}] Closing {self.name.lower()} thread')

    def _create_message_handler(self, key, queue_data, queue_plaindata, shared_data, port):
        raise NotImplementedError

    async def _create_task(self, loop, message_handler, queue_data, address):
        await asyncio.gather(message_handler.start_mainloop(),
                             self._create_connection(loop, queue_data, address),
                             self.__wait_for_task_to_close(), loop=loop)

    def _create_connection(self, loop, data, address):
        raise NotImplementedError

    async def __wait_for_task_to_close(self):
        await self.__check_connection_open()
        self.task.cancel()

    async def __check_connection_open(self):
        while self.connection_open[0]:
            await asyncio.sleep(5)
            # print(f'[{self.name}] Connection open')

    def close(self):
        self.connection_open = [False]


class ReceiverThreadHandler(ThreadHandler):
    def __init__(self):
        super().__init__()
        self.name = 'RECEIVER'

    def _create_message_handler(self, private_key, ingoing_data, ingoing_plaindata, shared_data, port):
        return ReceiverMessageHandler(private_key, ingoing_data, ingoing_plaindata, shared_data, self.connection_open,
                                      encrypt=False)

    async def _create_connection(self, loop, ingoing_data, port):
        server = await loop.create_server(lambda: ServerProtocol(ingoing_data, self.connection_open), '', port)

        async with server:
            await server.serve_forever()


class SenderThreadHandler(ThreadHandler):
    def __init__(self):
        super().__init__()
        self.name = 'SENDER'

    def _create_message_handler(self, public_key, outgoing_data, outgoing_plaindata, shared_data, port):
        return SenderMessageHandler(public_key, outgoing_plaindata, outgoing_data, shared_data, port,
                                    self.connection_open)

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
                print(f'[{self.name}] Message sent: {message_sent}')
            finally:
                transport.close()
