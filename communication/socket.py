import asyncio


class SocketProtocol(asyncio.Protocol):
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost
        self.ack_received = False

    def connection_made(self, transport):
        transport.write(self.message)
        print(f'[SOCKET] Data sent: {self.message!r}')

    def data_received(self, data):
        message = data.decode()
        print(f'[SOCKET] Data received: {message!r}')

        # TODO
        if message == 'ACK0':
            self.ack_received = True

    def connection_lost(self, exc):
        print('[SOCKET] The server closed the connection')
        self.on_con_lost.set_result(self.ack_received)
