from datetime import datetime
from random import Random

from Cryptodome.Cipher import PKCS1_OAEP


class SenderSessionKey:
    def __init__(self, recipient_public_key):
        self.key_size = None
        self.session_key = None
        self.encrypted_session_key = None

        self.public_key = recipient_public_key
        self.cipher = PKCS1_OAEP.new(self.public_key)

    def __generate_key(self):
        # take generator data from environment
        time = datetime.now()
        seed = int(time.strftime('%H%M%S'))

        rand = Random(seed)
        # AES key can be 128, 192 or 256 bits long
        self.key_size = rand.choice([128, 192, 256])
        self.session_key = rand.getrandbits(self.key_size)

    def __encrypt_key(self):
        if self.session_key:
            self.encrypted_session_key = self.cipher.encrypt(self.session_key)

    def create(self):
        self.__generate_key()
        self.__encrypt_key()


# TODO inserting recipient's encrypted session key
class RecipientSessionKey:
    def __init__(self, sender_private_key):
        self.key_size = None
        self.session_key = None
        self.encrypted_session_key = None

        self.private_key = sender_private_key
        self.cipher = PKCS1_OAEP.new(self.private_key)

    def __decrypt_key(self):
        if self.encrypted_session_key:
            self.session_key = self.cipher.decrypt(self.encrypted_session_key)

    def create(self):
        self.__decrypt_key()
