from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES

from config import BLOCK_SIZE

from encryption.block_cypher_mode import BlockCypherMode


class AESEncryption:
    def __init__(self, input_queue, output_queue, encode=True):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.encode = encode
        self.key_size = ...
        self.session_key = ...  # TODO remove
        self.block_size = BLOCK_SIZE
        self.initial_vector = get_random_bytes(16)
        self.cipher = None
        self.cipher_mode_dict = {BlockCypherMode.ECB: AESEncryption.__set_ecb_mode,
                                 BlockCypherMode.CBC: AESEncryption.__set_cbc_mode,
                                 BlockCypherMode.CFB: AESEncryption.__set_cfb_mode,
                                 BlockCypherMode.OFB: AESEncryption.__set_ofb_mode}

    # data length has to be a multiple of a block size
    def __set_ecb_mode(self):
        self.cipher = AES.new(self.session_key, AES.MODE_ECB)

    # data length has to be a multiple of a block size
    def __set_cbc_mode(self):
        self.cipher = AES.new(self.session_key, AES.MODE_CBC, iv=self.initial_vector)

    # accepts data of any length
    def __set_cfb_mode(self):
        self.cipher = AES.new(self.session_key, AES.MODE_CFB, iv=self.initial_vector)

    # accepts data of any length
    def __set_ofb_mode(self):
        self.cipher = AES.new(self.session_key, AES.MODE_OFB, iv=self.initial_vector)

    def create(self, cipher_mode):
        self.cipher_mode_dict[cipher_mode]()

    def use(self, data):
        if self.encode:
            return self.__encrypt(data)
        else:
            return self.__decrypt(data)

    def __encrypt(self, data):
        if self.cipher:
            return self.cipher.encrypt(data)

        return data  # TODO remove

    def __decrypt(self, encrypted_data):
        if self.cipher:
            return self.cipher.decrypt(encrypted_data)

        return encrypted_data  # TODO remove
