import struct

from config import SOCKET_HEADFORMAT, SOCKET_HEADLEN, BLOCK_SIZE, SESSION_KEY_SIZES, PARM_ALG_TYPE_LEN, \
    PARM_SESS_KEY_SIZE_LEN, PARM_BLOCK_SIZE_LEN, PARM_CIPHER_MODE_LEN, PARM_LEN, BLOCK_CIPHER_MODE
from encryption.aes import AESEncryption
from encryption.keys.key_handler import ReceiverKeyHandler, SenderKeyHandler


class MessageHandler:
    def __init__(self, input_queue, output_queue, shared_data, connection_open, encrypt=True):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.shared_data = shared_data

        self.connection_open = connection_open

        self.aes = AESEncryption(input_queue, output_queue, encrypt)
        self.handlers = dict()

    async def start_mainloop(self):
        while self.connection_open[0]:  # TODO
            input_data = await self.input_queue.async_get()
            output_data = await self.dispatch_message(input_data)
            self.output_queue.async_put(output_data)

    def dispatch_message(self, message):
        raise NotImplementedError


class SenderMessageHandler(MessageHandler):
    def __init__(self, public_key, input_queue, output_queue, shared_data, connection_open, encrypt=True):
        super().__init__(input_queue, output_queue, shared_data, connection_open, encrypt)

        self.key_handler = SenderKeyHandler(public_key)
        self.handlers = dict(INIT=SenderMessageHandler.__init_handler, PKEY=SenderMessageHandler.__pkey_handler,
                             SKEY=SenderMessageHandler.__skey_handler, PARM=SenderMessageHandler.__parm_handler,
                             DATA=SenderMessageHandler.__data_handler,
                             QUIT=SenderMessageHandler.__quit_handler)  # {message_type : handler_function}

    """params: message: str
        return: message: bytes"""

    async def dispatch_message(self, message):
        (message_type, message_data) = message
        message_type, message_data = await self.handlers.get(message_type)(self, message_type, message_data)
        message = self.__pack_message(message_type, message_data)
        return message

    async def __init_handler(self, message_type, message_data):
        message_data = message_data.split(':')[0].encode()
        return message_type, message_data

    async def __pkey_handler(self, message_type, message_data):
        message_data = self.key_handler.public_key
        return message_type, message_data

    async def __skey_handler(self, message_type, message_data):
        recipient_public_key = await self.shared_data.async_get()
        self.key_handler.create_session_key(recipient_public_key)
        self.aes.session_key = self.key_handler.session_key_handler.session_key
        message_data = self.key_handler.session_key_handler.encrypted_session_key
        return message_type, message_data

    async def __parm_handler(self, message_type, message_data):
        cipher_mode = message_data
        self.aes.create(cipher_mode)
        message_data = self.__pack_parameters(message_data)
        return message_type, message_data

    async def __data_handler(self, message_type, message_data):
        message_data = message_data.encode()
        message_data = self.aes.use(message_data)
        return message_type, message_data

    async def __quit_handler(self, message_type, message_data):
        message_data = message_data.encode()
        return message_type, message_data

    """"params: cipher_mode: str
         return: parameters: bytes"""

    def __pack_parameters(self, cipher_mode):
        algorithm_type = 0  # aes algorithm
        algorithm_type = f'{algorithm_type:0{PARM_ALG_TYPE_LEN}b}'

        session_key_size = SESSION_KEY_SIZES.index(self.key_handler.session_key_handler.key_size)
        session_key_size = f'{session_key_size:0{PARM_SESS_KEY_SIZE_LEN}b}'

        block_size = f'{BLOCK_SIZE:0{PARM_BLOCK_SIZE_LEN}b}'

        cipher_mode = [mode.value for mode in BLOCK_CIPHER_MODE].index(cipher_mode)
        cipher_mode = f'{cipher_mode:0{PARM_CIPHER_MODE_LEN}b}'

        initial_vector = self.aes.initial_vector

        parameters = algorithm_type + session_key_size + block_size + cipher_mode
        parameters = int(parameters, 2).to_bytes(PARM_LEN, byteorder='little')
        parameters = parameters + initial_vector
        return parameters

    """params: message_type: str, message_data: bytes
        return message: bytes"""

    @staticmethod
    def __pack_message(message_type, message_data):
        message_length = len(message_data)
        message_type = message_type.encode()

        # convert string to bytes, ! - big-endian; 4s - 4 chars (bytes); L - unsigned long, %d s - chars
        message = struct.pack(f'!{SOCKET_HEADFORMAT}{message_length}s', message_type, message_length, message_data)

        return message


class ReceiverMessageHandler(MessageHandler):
    def __init__(self, private_key, input_queue, output_queue, shared_data, connection_open, encrypt=True):
        super().__init__(input_queue, output_queue, shared_data, connection_open, encrypt)

        self.key_handler = ReceiverKeyHandler(private_key)
        self.handlers = dict(INIT=ReceiverMessageHandler.__init_handler, PKEY=ReceiverMessageHandler.__pkey_handler,
                             SKEY=ReceiverMessageHandler.__skey_handler, PARM=ReceiverMessageHandler.__parm_handler,
                             DATA=ReceiverMessageHandler.__data_handler,
                             QUIT=ReceiverMessageHandler.__quit_handler)  # {message_type : handler_function}

    """params: message: bytes
        return: message: str"""

    async def dispatch_message(self, message):
        message_type, message_length, message_data = self.__unpack_message(message)
        message = await self.handlers.get(message_type)(self, message_type, message_data)
        return message

    async def __init_handler(self, message_type, message_data):
        message_data = message_data.decode()
        return message_type, message_data

    async def __pkey_handler(self, message_type, message_data):
        self.shared_data.async_put(message_data)
        message_data = ''
        return message_type, message_data

    async def __skey_handler(self, message_type, message_data):
        encrypted_session_key = message_data
        self.key_handler.sender_session_key_handler.encrypted_session_key = encrypted_session_key
        message_data = ''
        return message_type, message_data

    async def __parm_handler(self, message_type, message_data):
        parameters = self.__unpack_parameters(message_data)
        algorithm_type, session_key_size, block_size, cipher_mode, initial_vector = parameters
        self.key_handler.sender_session_key_handler.create(session_key_size)
        self.aes.session_key = self.key_handler.sender_session_key_handler.session_key
        self.aes.create(cipher_mode, initial_vector)
        message_data = ''
        return message_type, message_data

    async def __data_handler(self, message_type, message_data):
        message_data = self.aes.use(message_data)
        message_data = message_data.decode()
        return message_type, message_data

    async def __quit_handler(self, message_type, message_data):
        message_data = ''
        return message_type, message_data

    """params: message_data: bytes
        return: algorithm_type: int, session_key_size: int, block_size: int, cipher_mode: str, initial_vector: bytes"""

    @staticmethod
    def __unpack_parameters(message_data):
        parameters = int.from_bytes(message_data[:PARM_LEN], byteorder='little')
        parameters = f'{parameters:0{PARM_LEN * 8}b}'

        index = 0
        algorithm_type = int(parameters[:index + PARM_ALG_TYPE_LEN], 2)
        index = index + PARM_ALG_TYPE_LEN

        session_key_size_index = int(parameters[index:index + PARM_SESS_KEY_SIZE_LEN], 2)
        session_key_size = SESSION_KEY_SIZES[session_key_size_index]
        index = index + PARM_SESS_KEY_SIZE_LEN

        block_size = int(parameters[index:index + PARM_BLOCK_SIZE_LEN], 2)
        index = index + PARM_BLOCK_SIZE_LEN

        cipher_mode = [mode.value for mode in BLOCK_CIPHER_MODE][int(parameters[index:index + PARM_CIPHER_MODE_LEN], 2)]

        initial_vector = message_data[PARM_LEN:]
        return algorithm_type, session_key_size, block_size, cipher_mode, initial_vector

    """params: message_data: bytes
        return message_type: str, message_length: int, message_data: bytes"""

    @staticmethod
    def __unpack_message(message_data):
        message_type, message_length = struct.unpack(f'!{SOCKET_HEADFORMAT}', message_data[:SOCKET_HEADLEN])
        message_data = struct.unpack(f'!{message_length}s', message_data[SOCKET_HEADLEN:])[0]
        message_type = message_type.decode()
        message_length = int(message_length)
        return message_type, message_length, message_data
