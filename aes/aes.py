from Cryptodome.Cipher import AES


class AESEncryption:
    def __init__(self):
        # self.recipient_public_key = ...
        self.key_size = ...
        self.session_key = ...  # TODO remove
        self.block_size = ...
        self.cipher_mode = ...
        self.initial_vector = ...
        self.cipher = None

    def set_ecb_mode(self):
        self.cipher = AES.new(self.session_key, AES.MODE_ECB)

    def set_cbc_mode(self):
        self.cipher = AES.new(self.session_key, AES.MODE_CBC, iv=self.initial_vector)

    def set_cfb_mode(self):
        self.cipher = AES.new(self.session_key, AES.MODE_CFB, iv=self.initial_vector)

    def set_ofb_mode(self):
        self.cipher = AES.new(self.session_key, AES.MODE_OFB, iv=self.initial_vector)

    def encrypt_data(self, data):
        return self.cipher.encrypt(data) if self.cipher else None  # TODO
