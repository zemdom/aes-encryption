import struct

from config import SOCKET_HEADFORMAT, SOCKET_HEADLEN


class MessageHandler:
    def __init__(self):
        self.handlers = dict(INIT=MessageHandler.init_handler, PKEY=MessageHandler.pkey_handler,
                             PARM=MessageHandler.parm_handler, DATA=MessageHandler.data_handler,
                             QUIT=self.quit_handler)  # {message_type : handler_function}

    def dispatch_message(self, message_type, message):
        self.handlers.get(message_type)(message)

    @staticmethod
    def init_handler(message_data):
        message = message_data
        return message

    @staticmethod
    def pkey_handler(message_data):
        message = message_data
        return message

    @staticmethod
    def parm_handler(message_data):
        message = message_data
        return message

    @staticmethod
    def data_handler(message_data):
        message = message_data
        return message

    @staticmethod
    def quit_handler(message_data):
        message = message_data
        return message

    @staticmethod
    def pack_message(message_type, message_data):
        message_length = len(message_data)
        message_type = message_type.encode()
        message_data = message_data.encode()

        # convert string to bytes, ! - big-endian; 4s - 4 chars (bytes); L - unsigned long, %d s - chars
        message = struct.pack('!{0}{1}s'.format(SOCKET_HEADFORMAT, message_length), message_type, message_length,
                              message_data)
        return message

    @staticmethod
    def unpack_message(message_data):
        message_type, message_length = struct.unpack('!{0}'.format(SOCKET_HEADFORMAT), message_data[:SOCKET_HEADLEN])
        message_data = struct.unpack('!{0}s'.format(message_length), message_data[SOCKET_HEADLEN:])[0]
        return message_type.decode(), str(message_length), message_data.decode()
