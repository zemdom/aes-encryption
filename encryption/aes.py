from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES

from config import BLOCK_CIPHER_MODE
from utils.bytes_data_handler import BytesDataHandler


class AESEncryption:
    def __init__(self, encode=True):
        self.encode = encode
        self.padding = False
        self.session_key = None
        self.initial_vector = None
        self.cipher = None
        self.cipher_mode_dict = {BLOCK_CIPHER_MODE.ECB: AESEncryption.__set_ecb_mode,
                                 BLOCK_CIPHER_MODE.CBC: AESEncryption.__set_cbc_mode,
                                 BLOCK_CIPHER_MODE.CFB: AESEncryption.__set_cfb_mode,
                                 BLOCK_CIPHER_MODE.OFB: AESEncryption.__set_ofb_mode}

    # data length has to be a multiple of a block size
    def __set_ecb_mode(self):
        self.cipher = AES.new(self.session_key, AES.MODE_ECB)
        self.padding = True

    # data length has to be a multiple of a block size
    def __set_cbc_mode(self):
        self.cipher = AES.new(self.session_key, AES.MODE_CBC, iv=self.initial_vector)
        self.padding = True

    # accepts data of any length
    def __set_cfb_mode(self):
        self.cipher = AES.new(self.session_key, AES.MODE_CFB, iv=self.initial_vector)
        self.padding = False

    # accepts data of any length
    def __set_ofb_mode(self):
        self.cipher = AES.new(self.session_key, AES.MODE_OFB, iv=self.initial_vector)
        self.padding = False

    def create(self, cipher_mode, initial_vector=None):
        if self.encode:
            self.initial_vector = get_random_bytes(16)
        else:
            self.initial_vector = initial_vector

        self.cipher_mode_dict[BLOCK_CIPHER_MODE[cipher_mode]](self)

    def use(self, data):
        if self.encode:
            data = BytesDataHandler.add_padding(data) if self.padding else data
            data = self.__encrypt(data)
            return data
        else:
            data = self.__decrypt(data)
            data = BytesDataHandler.remove_padding(data) if self.padding else data
            return data

    def __encrypt(self, data):
        """

        :param bytes data:
        :return: ciphertext
        :rtype: bytes
        """
        if self.cipher:
            return self.cipher.encrypt(data)

    def __decrypt(self, encrypted_data):
        """

        :param bytes encrypted_data:
        :return: plaintext
        :rtype: bytes
        """
        if self.cipher:
            return self.cipher.decrypt(encrypted_data)
