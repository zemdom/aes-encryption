from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES

from config import BLOCK_SIZE


class AESEncryption:
    def __init__(self):
        # self.recipient_public_key = ...
        self.key_size = ...
        self.session_key = ...  # TODO remove
        self.block_size = BLOCK_SIZE
        self.cipher_mode = None
        self.initial_vector = get_random_bytes(16)
        self.cipher = None
        self.cipher_mode_dict = {'ecb': AESEncryption.__set_ecb_mode, 'cbc': AESEncryption.__set_cbc_mode,
                                 'cfb': AESEncryption.__set_cfb_mode, 'ofb': AESEncryption.__set_ofb_mode}

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

    def create(self):
        """cipher_mode needs to be set before calling"""
        if self.cipher_mode:
            self.cipher_mode_dict[self.cipher_mode]()

    def encrypt(self, data):
        if self.cipher:
            return self.cipher.encrypt(data)

    def decrypt(self, encrypted_data):
        if self.cipher:
            return self.cipher.decrypt(encrypted_data)
