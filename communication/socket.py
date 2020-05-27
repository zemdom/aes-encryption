import asyncio
import time


class SocketProtocol(asyncio.Protocol):
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost
        self.ack_received = False
        self.start_time = None

    def connection_made(self, transport):
        transport.write(self.message)
        print(f'[SOCKET] Data sent: {self.message!r}')
        self.start_time = time.time()

    def data_received(self, data):
        message = data.decode()
        print(f'[SOCKET] Data received: {message!r}')

        if message == 'ACK0':
            print(f'[SOCKET] ACK received after %{(time.time() - self.start_time)} seconds')
            self.ack_received = True

    def connection_lost(self, exc):
        print('[SOCKET] The server closed the connection')
        self.on_con_lost.set_result(self.ack_received)
