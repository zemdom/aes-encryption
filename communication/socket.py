import asyncio

from communication.message_handler import MessageHandler


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


def run_client(outgoing_data, port):
    asyncio.run(create_client(outgoing_data, port))


async def create_client(outgoing_data, port):
    loop = asyncio.get_running_loop()
    sent = False

    while True:  # TODO
        message = MessageHandler.pack_message(*outgoing_data.get())
        while not sent:
            on_con_lost = loop.create_future()
            transport, protocol = await loop.create_connection(lambda: SocketProtocol(message, on_con_lost),
                                                               '127.0.0.1', port)

            # wait until the protocol signals that the connection is lost and close the transport
            try:
                await on_con_lost
                sent = on_con_lost.result()
                print(sent)
            finally:
                transport.close()
