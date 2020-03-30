import asyncio


class ServerProtocol(asyncio.Protocol):
    def __init__(self, ingoing_data, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.ingoing_data = ingoing_data
        self.peername = None
        self.transport = None

    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        print('[SERVER] Connection from {}'.format(self.peername))
        self.transport = transport

    def data_received(self, data):
        print('[SERVER] Data received: {!r}'.format(data))
        self.ingoing_data.put(data)

        self.transport.write('ACK0'.encode())  # TODO
        self.transport.close()

    def connection_lost(self, exc):
        print('[SERVER] Lost connection of {}'.format(self.peername))
        self.transport.close()
