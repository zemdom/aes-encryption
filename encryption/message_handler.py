import struct

from config import SOCKET_HEADFORMAT, SOCKET_HEADLEN
from encryption.aes import AESEncryption
from encryption.key_handler import ReceiverKeyHandler, SenderKeyHandler


class MessageHandler:
    def __init__(self, input_queue, output_queue, connection_open, encrypt=True):
        self.input_queue = input_queue
        self.output_queue = output_queue

        self.connection_open = connection_open

        self.aes = AESEncryption(input_queue, output_queue, encrypt)
        self.handlers = dict()

    async def start_mainloop(self):
        while self.connection_open[0]:  # TODO
            input_data = await self.input_queue.async_get()
            output_data = self.dispatch_message(input_data)
            self.output_queue.async_put(output_data)

    def dispatch_message(self, message):
        raise NotImplementedError


class SenderMessageHandler(MessageHandler):
    def __init__(self, public_key, input_queue, output_queue, connection_open, encrypt=True):
        super().__init__(input_queue, output_queue, connection_open, encrypt)

        self.key_handler = SenderKeyHandler(public_key)
        self.handlers = dict(INIT=SenderMessageHandler.__init_handler, PKEY=SenderMessageHandler.__pkey_handler,
                             SKEY=SenderMessageHandler.__skey_handler, PARM=SenderMessageHandler.__parm_handler,
                             DATA=SenderMessageHandler.__data_handler,
                             QUIT=SenderMessageHandler.__quit_handler)  # {message_type : handler_function}

    def dispatch_message(self, message):
        (message_type, message_data) = message
        message_type, message_data = self.handlers.get(message_type)(self, message_type, message_data)
        message = self.__pack_message(message_type, message_data)
        return message

    def __init_handler(self, message_type, message_data):

        return message_type, message_data

    def __pkey_handler(self, message_type, message_data):
        return message_type, message_data

    def __skey_handler(self, message_type, message_data):
        return message_type, message_data

    def __parm_handler(self, message_type, message_data):
        return message_type, message_data

    def __data_handler(self, message_type, message_data):
        message_data = self.aes.use(message_data)
        return message_type, message_data

    def __quit_handler(self, message_type, message_data):
        return message_type, message_data

    @staticmethod
    def __pack_message(message_type, message_data):
        message_length = len(message_data)
        message_type = message_type.encode()
        message_data = message_data.encode()

        # convert string to bytes, ! - big-endian; 4s - 4 chars (bytes); L - unsigned long, %d s - chars
        message = struct.pack('!{0}{1}s'.format(SOCKET_HEADFORMAT, message_length), message_type, message_length,
                              message_data)
        return message


class ReceiverMessageHandler(MessageHandler):
    def __init__(self, private_key, input_queue, output_queue, connection_open, encrypt=True):
        super().__init__(input_queue, output_queue, connection_open, encrypt)

        self.key_handler = ReceiverKeyHandler(private_key)
        self.handlers = dict(INIT=ReceiverMessageHandler.__init_handler, PKEY=ReceiverMessageHandler.__pkey_handler,
                             SKEY=ReceiverMessageHandler.__skey_handler, PARM=ReceiverMessageHandler.__parm_handler,
                             DATA=ReceiverMessageHandler.__data_handler,
                             QUIT=ReceiverMessageHandler.__quit_handler)  # {message_type : handler_function}

    def dispatch_message(self, message):
        message_type, message_length, message_data = self.__unpack_message(message)
        message = self.handlers.get(message_type)(self, message_type, message_data)
        return message

    def __init_handler(self, message_type, message_data):
        return message_type, message_data

    def __pkey_handler(self, message_type, message_data):
        return message_type, message_data

    def __skey_handler(self, message_type, message_data):
        return message_type, message_data

    def __parm_handler(self, message_type, message_data):
        return message_type, message_data

    def __data_handler(self, message_type, message_data):
        return message_type, message_data

    def __quit_handler(self, message_type, message_data):
        return message_type, message_data

    @staticmethod
    def __unpack_message(message_data):
        message_type, message_length = struct.unpack('!{0}'.format(SOCKET_HEADFORMAT), message_data[:SOCKET_HEADLEN])
        message_data = struct.unpack('!{0}s'.format(message_length), message_data[SOCKET_HEADLEN:])[0]
        return message_type.decode(), str(message_length), message_data.decode()
