import asyncio
import os
import socket
import struct

from config import SOCKET_HEADFORMAT, SOCKET_HEADLEN, BLOCK_SIZE, SESSION_KEY_SIZES, PARM_ALG_TYPE_LEN, \
    PARM_SESS_KEY_SIZE_LEN, PARM_BLOCK_SIZE_LEN, PARM_CIPHER_MODE_LEN, PARM_LEN, BLOCK_CIPHER_MODE, SOCKET_BUFSIZE, \
    FILE_PERCENT_LEN
from encryption.aes import AESEncryption
from encryption.keys.key_handler import ReceiverKeyHandler, SenderKeyHandler
from utils.file_handler import FileHandler


class MessageHandler:
    def __init__(self, input_queue, output_queue, shared_data, connection_open, encrypt=True):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.shared_data = shared_data

        self.connection_open = connection_open

        self.aes = AESEncryption(encrypt)
        self.handlers = dict()
        self.file_handlers = dict()

    async def start_mainloop(self):
        while self.connection_open[0]:  # TODO: connection_open never changes
            input_data = await self.input_queue.async_get()
            async for output_data in self.dispatch_message(input_data):
                self.output_queue.sync_put(output_data)

    def dispatch_message(self, message):
        raise NotImplementedError


class SenderMessageHandler(MessageHandler):
    def __init__(self, public_key, input_queue, output_queue, shared_data, gui_data, port, connection_open,
                 encrypt=True):
        shared_data.create(asyncio.get_running_loop())
        gui_data.create(asyncio.get_running_loop())

        super().__init__(input_queue, output_queue, shared_data, connection_open, encrypt)
        self.gui_data = gui_data

        self.key_handler = SenderKeyHandler(public_key)
        self.handlers = dict(INIT=SenderMessageHandler.__init_handler, PKEY=SenderMessageHandler.__pkey_handler,
                             SKEY=SenderMessageHandler.__skey_handler, PARM=SenderMessageHandler.__parm_handler,
                             TEXT=SenderMessageHandler.__text_handler, FILE=SenderMessageHandler.__file_handler,
                             QUIT=SenderMessageHandler.__quit_handler)  # {message_type : handler_function}
        self.file_handlers = dict(INIT=SenderMessageHandler.__file_init_handler,
                                  PARM=SenderMessageHandler.__file_parm_handler,
                                  DATA=SenderMessageHandler.__file_data_handler,
                                  QUIT=SenderMessageHandler.__file_quit_handler)  # {file_message_type : file_handler_function}
        self.port = port
        self.file_path = None

    async def dispatch_message(self, message):
        """

        :param str message:
        :return: message
        :rtype: bytes
        """
        (message_type, message_data) = message
        async for message_type, message_data in self.handlers.get(message_type)(self, message_type, message_data):
            message = self.__pack_message(message_type, message_data)
            yield message

    async def __init_handler(self, message_type, message_data):
        host_address = socket.gethostbyname(socket.gethostname())
        message_data = f'{host_address}:{self.port}'
        message_data = message_data.encode()
        yield message_type, message_data

    async def __pkey_handler(self, message_type, message_data):
        message_data = self.key_handler.rsa_key
        yield message_type, message_data

    async def __skey_handler(self, message_type, message_data):
        recipient_public_key = await self.shared_data.async_get()
        self.key_handler.create_session_key(recipient_public_key)
        self.aes.session_key = self.key_handler.session_key_handler.session_key
        message_data = self.key_handler.session_key_handler.encrypted_session_key
        yield message_type, message_data

    async def __parm_handler(self, message_type, message_data):
        cipher_mode = message_data
        self.aes.create(cipher_mode)
        message_data = self.__pack_parameters(message_data)
        message_data = self.key_handler.encrypt_using_rsa_key(message_data)
        yield message_type, message_data

    async def __text_handler(self, message_type, message_data):
        message_data = message_data.encode()
        message_data = self.aes.use(message_data)
        yield message_type, message_data

    async def __file_handler(self, message_type, message_data):
        async for message_data in self.__file_dispatch_message(message_data):
            message_data = self.aes.use(message_data)
            yield message_type, message_data

    async def __file_dispatch_message(self, message_data):
        """

        :param str message_data:
        :return: message_data
        :rtype: # bytes
        """
        file_message_type, file_message_data = message_data
        for file_message_type, file_message_data in self.file_handlers.get(file_message_type)(self, file_message_type,
                                                                                              file_message_data):
            file_message = self.__pack_message(file_message_type, file_message_data)
            yield file_message

    def __file_init_handler(self, file_message_type, file_message_data):
        self.file_path = file_message_data
        file_message_data = os.path.basename(file_message_data)
        file_message_data = file_message_data.encode()
        yield file_message_type, file_message_data

    def __file_parm_handler(self, file_message_type, file_message_data):
        file_message_data = os.path.getsize(self.file_path)
        file_message_data = str(file_message_data).encode()
        yield file_message_type, file_message_data

    def __file_data_handler(self, file_message_type, file_message_data):
        for file_message_data, file_message_percent in self.__file_pack_data(self.file_path):
            self.gui_data.sync_put(file_message_percent)
            yield file_message_type, file_message_data

    def __file_quit_handler(self, file_message_type, file_message_data):
        self.file_path = None
        self.gui_data.sync_put(100)
        file_message_data = file_message_data.encode()
        yield file_message_type, file_message_data

    async def __quit_handler(self, message_type, message_data):
        message_data = message_data.encode()
        yield message_type, message_data

    def __pack_parameters(self, cipher_mode):
        """

        :param str cipher_mode:
        :return: parameters
        :rtype: bytes
        """
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

    @staticmethod
    def __file_pack_data(file_path):
        """

        :param str file_path:
        :return: message, message_percent
        ":rtype: (bytes, int)
        """

        file_message_length = SOCKET_BUFSIZE - (FILE_PERCENT_LEN // 8)

        file_size = os.path.getsize(file_path)
        file_size = file_size if file_size > file_message_length else file_message_length

        with open(file_path, 'rb+') as file:
            for i in range(0, file_size, file_message_length):
                percent = int((i + file_message_length) / file_size * 100)
                file_message_header = f'{percent:{FILE_PERCENT_LEN}b}'
                file_message_header = int(file_message_header, 2).to_bytes(FILE_PERCENT_LEN // 8,
                                                                           byteorder='little')
                file_message_data = file.read(file_message_length)
                message = file_message_header + file_message_data

                yield message, percent

    @staticmethod
    def __pack_message(message_type, message_data):
        """

        :param str message_type:
        :param bytes message_data:
        :return: message
        :rtype: bytes
        """
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
                             TEXT=ReceiverMessageHandler.__text_handler, FILE=ReceiverMessageHandler.__file_handler,
                             QUIT=ReceiverMessageHandler.__quit_handler)  # {message_type : handler_function}
        self.file_handlers = dict(INIT=ReceiverMessageHandler.__file_init_handler,
                                  PARM=ReceiverMessageHandler.__file_parm_handler,
                                  DATA=ReceiverMessageHandler.__file_data_handler,
                                  QUIT=ReceiverMessageHandler.__file_quit_handler)  # {file_message_type : file_handler_function}
        self.file_name = None
        self.file = None

    async def dispatch_message(self, message):
        """

        :param bytes message:
        :return: message
        :rtype: str
        """
        message_type, message_length, message_data = self.__unpack_message(message)
        async for message in self.handlers.get(message_type)(self, message_type, message_data):
            yield message

    async def __init_handler(self, message_type, message_data):
        message_data = message_data.decode()
        yield message_type, message_data

    async def __pkey_handler(self, message_type, message_data):
        self.shared_data.sync_put(message_data)
        message_data = ''
        yield message_type, message_data

    async def __skey_handler(self, message_type, message_data):
        encrypted_session_key = message_data
        self.key_handler.sender_session_key_handler.encrypted_session_key = encrypted_session_key
        message_data = ''
        yield message_type, message_data

    async def __parm_handler(self, message_type, message_data):
        message_data = self.key_handler.decrypt_using_rsa_key(message_data)
        parameters = self.__unpack_parameters(message_data)
        algorithm_type, session_key_size, block_size, cipher_mode, initial_vector = parameters
        self.key_handler.sender_session_key_handler.create(session_key_size)
        self.aes.session_key = self.key_handler.sender_session_key_handler.session_key
        self.aes.create(cipher_mode, initial_vector)
        message_data = ''
        yield message_type, message_data

    async def __text_handler(self, message_type, message_data):
        message_data = self.aes.use(message_data)
        message_data = message_data.decode(errors='ignore')  # in case of random data, continue decoding without notice
        yield message_type, message_data

    async def __file_handler(self, message_type, message_data):
        message_data = self.aes.use(message_data)
        async for message_data in self.__file_dispatch_message(message_data):
            yield message_type, message_data

    async def __file_dispatch_message(self, message_data):
        """

        :param bytes message_data:
        :return:  message
        :rtype: # str
        """
        file_message_type, file_message_length, file_message_data = self.__unpack_message(message_data)
        for file_message_type, file_message_data in self.file_handlers.get(file_message_type)(self, file_message_type,
                                                                                              file_message_data):
            yield file_message_type, file_message_data

    def __file_init_handler(self, file_message_type, file_message_data):
        file_message_data = file_message_data.decode()
        self.file_name = file_message_data
        temporary_directory = FileHandler.get_temporary_file_directory_path()
        temporary_path = os.path.join(temporary_directory, self.file_name)
        self.file = open(temporary_path, 'wb+')
        yield file_message_type, file_message_data

    def __file_parm_handler(self, file_message_type, file_message_data):
        file_message_data = file_message_data.decode()
        file_message_data = int(file_message_data)
        yield file_message_type, file_message_data

    def __file_data_handler(self, file_message_type, file_message_data):
        file_message_header, file_message_data = self.__file_unpack_data(file_message_data)
        self.file.write(file_message_data)
        file_message_data = file_message_header
        yield file_message_type, file_message_data

    def __file_quit_handler(self, file_message_type, file_message_data):
        self.file.close()
        yield file_message_type, file_message_data

    async def __quit_handler(self, message_type, message_data):
        message_data = message_data.decode()
        yield message_type, message_data

    @staticmethod
    def __unpack_parameters(message_data):
        """

        :param bytes message_data:
        :return: (algorithm_type, session_key_size, block_size, cipher_mode, initial_vector)
        :rtype: (int, int, int, str, bytes)
        """
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

    @staticmethod
    def __file_unpack_data(message_data):
        """

        :param bytes message_data:
        :return: (message_header, message)
        :rtype: (str, bytes)
        """
        message_header_len = FILE_PERCENT_LEN // 8
        message_header = message_data[:message_header_len]
        message_header = str(int.from_bytes(message_header, byteorder='little'))

        message = message_data[message_header_len:]
        message = message
        return message_header, message

    @staticmethod
    def __unpack_message(message_data):
        """

        :param bytes message_data:
        :return: (message_type, message_length, message_data)
        :rtype: (str, int, bytes)
        """
        message_type, message_length = struct.unpack(f'!{SOCKET_HEADFORMAT}', message_data[:SOCKET_HEADLEN])
        message_data = struct.unpack(f'!{message_length}s', message_data[SOCKET_HEADLEN:])[0]
        message_type = message_type.decode()
        message_length = int(message_length)
        return message_type, message_length, message_data
