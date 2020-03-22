import socket
import struct
import threading

from config import SOCKET_BUFSIZE, SOCKET_HEADSIZE, SOCKET_HEADFORMAT


# sends data to a peer
class Socket:
    def __init__(self, host, port, sock=None):
        self.host = host
        self.port = int(port)

        if sock:
            self.sock = sock
        else:
            self.__open()

        self.debug = True

    @staticmethod
    def __pack_message(message_type, message_data):
        # convert bytes to string
        message_data = message_data.decode()
        message_length = len(message_data)
        # convert string to bytes, ! - big-endian; 4s - 4 chars; L - unsigned long, %d s - chars
        message = struct.pack("!%s%ds" % (SOCKET_HEADFORMAT, message_length), message_type.encode(), message_length,
                              message_data.encode())
        return message

    def __debug(self, text):
        if self.debug:
            print("<%s>[SOCKET] - %s" % (str(threading.currentThread().getName()), text))

    def __open(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(None)

        # chooses the best address to use for connection, compatible with IPv4 and IPv6
        # self.sock = socket.create_connection((self.host, int(self.port)))

    async def send_data(self, loop, message_type, message_data):
        message = self.__pack_message(message_type, message_data)
        # message_length = len(message)

        # total_sent = 0
        # while total_sent < message_length:
        # socket.send() retries a call if it is interrupted
        # sent = await loop.sock_send(self.sock, message[total_sent:])

        # if sent == 0:
        #     return False
        # total_sent += sent
        # TODO find sock.send() equivalent
        await loop.sock_sendall(self.sock, message)
        return True

    async def receive_data(self, loop):
        message = b''
        total_received = 0
        while total_received < SOCKET_HEADSIZE:
            message += await loop.sock_recv(self.sock, SOCKET_BUFSIZE)
            received = len(message)
            if received == 0:
                return None, None
            total_received += received

        message_type, message_length = struct.unpack('!%s' % SOCKET_HEADFORMAT, message[:8])

        while total_received < message_length:
            message += await loop.sock_recv(self.sock, SOCKET_BUFSIZE)
            received = len(message)
            if received == 0:
                return None, None
            total_received += received

        message = message[8:]
        return message_type.decode(), message.decode()

    def close(self):
        self.sock.close()
        self.sock = None
