import asyncio

from communication.message_handler import MessageHandler


class ServerProtocol(asyncio.Protocol):
    def __init__(self, ingoing_data, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.ingoing_data = ingoing_data

    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        print('[SERVER] Connection from {}'.format(self.peername))
        self.transport = transport

    def data_received(self, data):
        message_type, message_length, message_data = MessageHandler.unpack_message(data)
        print('[SERVER] Data received: {!r}'.format(message_data))

        self.ingoing_data.put(message_data)

        self.transport.write('ACK0'.encode())
        self.transport.close()

    def connection_lost(self, exc):
        print('[SERVER] Lost connection of {}'.format(self.peername))
        self.transport.close()


def run_server(ingoing_data, port):
    asyncio.run(create_server(ingoing_data, port))


async def create_server(ingoing_data, port):
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: ServerProtocol(ingoing_data),
        '127.0.0.1', port)

    async with server:
        await server.serve_forever()
