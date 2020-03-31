import asyncio


class SocketProtocol(asyncio.Protocol):
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost
        self.ack_received = False

    def connection_made(self, transport):
        transport.write(self.message)
        # transport.write(self.message.encode())
        print('[SOCKET] Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        message = data.decode()
        print('[SOCKET] Data received: {!r}'.format(data.decode()))

        if message == 'ACK0':
            self.ack_received = True

    def connection_lost(self, exc):
        print('[SOCKET] The server closed the connection')
        self.on_con_lost.set_result(self.ack_received)
