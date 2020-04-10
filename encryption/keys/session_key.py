from datetime import datetime
from random import Random

from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA

from config import SESSION_KEY_SIZES


class SenderSessionKey:
    def __init__(self, recipient_public_key):
        # keys are stored as byte string
        self.key_size = None
        self.session_key = None  # byte string
        self.encrypted_session_key = None  # byte string

        self.public_key = recipient_public_key  # byte string
        self.cipher = PKCS1_OAEP.new(RSA.import_key(self.public_key))

    def __generate_key(self):
        # take generator data from environment
        time = datetime.now()
        seed = int(time.strftime('%H%M%S'))

        rand = Random(seed)
        self.key_size = rand.choice(SESSION_KEY_SIZES)
        session_key = rand.getrandbits(self.key_size)
        self.session_key = session_key.to_bytes(self.key_size // 8, byteorder='little')

    def __encrypt_key(self):
        if self.session_key:
            self.encrypted_session_key = self.cipher.encrypt(self.session_key)

    def create(self):
        self.__generate_key()
        self.__encrypt_key()


class RecipientSessionKey:
    def __init__(self, sender_private_key):
        # keys are stored as byte string
        self.key_size = None
        self.session_key = None  # byte string
        self.encrypted_session_key = None  # byte string

        self.private_key = sender_private_key  # byte string
        self.cipher = PKCS1_OAEP.new(RSA.import_key(self.private_key))

    def __decrypt_key(self, encrypted_session_key):
        self.session_key = self.cipher.decrypt(encrypted_session_key)

    def create(self, key_size):
        self.key_size = key_size
        self.__decrypt_key(self.encrypted_session_key)
