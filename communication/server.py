import asyncio


class ServerProtocol(asyncio.Protocol):
    def __init__(self, ingoing_data, connection_open, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.ingoing_data = ingoing_data
        self.connection_open = connection_open
        self.peername = None
        self.transport = None

    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        print(f'[SERVER] Connection from {self.peername}')
        self.transport = transport

    def data_received(self, data):
        print(f'[SERVER] Data received: {data!r}')
        self.ingoing_data.sync_put(data)

        self.transport.write('ACK0'.encode())  # TODO
        self.transport.close()

    def connection_lost(self, exc):
        print(f'[SERVER] Lost connection of {self.peername}')
        self.transport.close()
