import asyncio
import socket

from communication.message_handler import MessageHandler
from communication.socket import Socket


# receives data from a peer
class Server:
    def __init__(self, server_port, server_host=None):
        self.server_port = int(server_port)

        if server_host:
            self.server_host = server_host
        else:
            self.__initialize_server_host()
        self.sock = self.__open()

        self.peer = (None, None)  # (host, port)
        self.shutdown = False
        self.handlers = {'INIT': MessageHandler.init_handler, 'PKEY': MessageHandler.pkey_handler,
                         'PARM': MessageHandler.parm_handler, 'DATA': MessageHandler.data_handler,
                         'QUIT': MessageHandler.quit_handler}  # {message_type : handler_function}
        self.debug = True

    def __initialize_server_host(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect to an Internet host to determine local machine's IP address
        sock.connect(('www.google.com', 80))
        self.server_host = sock.getsockname()[0]
        sock.close()

    def __debug(self, text):
        if self.debug:
            print("[SERVER] - %s" % text)

    def __open(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', self.server_port))
        sock.settimeout(None)

        # TODO?
        # peer to peer connection, server allows only one connection
        sock.listen(1)
        return sock

    async def run(self):
        async for message in self.__mainloop():
            print(message)

    async def __mainloop(self):
        loop = asyncio.get_event_loop()
        self.__debug("Mainloop started.")

        while not self.shutdown:
            peer_sock, _ = await loop.sock_accept(self.sock)
            future = loop.create_future()
            await self.__handle_peer_connection(future, loop, peer_sock)
            yield future.result()

    async def __handle_peer_connection(self, future, loop, sock):
        self.__debug('Peer connected ' + str(sock.getpeername()))

        self.peer = sock.getpeername()
        peer_connection = Socket(*self.peer, sock)
        message_type, message_data = await peer_connection.receive_data(loop)
        peer_connection.close()

        if message_type not in self.handlers:
            self.__debug('Not handled: %s' % message_type)

        # dictionary - get function returns None if key does not exist
        message = self.handlers.get(message_type)(message_data)
        future.set_result(message)

    def close(self):
        self.shutdown = True
        self.sock.close()
