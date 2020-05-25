from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA

from encryption.keys.session_key import SenderSessionKey, RecipientSessionKey


class KeyHandler:
    def __init__(self, rsa_key):
        self.rsa_key = rsa_key
        self.cipher = PKCS1_OAEP.new(RSA.import_key(self.rsa_key))


class SenderKeyHandler(KeyHandler):
    def __init__(self, public_key):
        super().__init__(public_key)
        self.session_key_handler = None

    def create_session_key(self, recipient_public_key):
        self.session_key_handler = SenderSessionKey(recipient_public_key)
        self.session_key_handler.create()

    def encrypt_using_rsa_key(self, data):
        return self.cipher.encrypt(data)


class ReceiverKeyHandler(KeyHandler):
    def __init__(self, private_key):
        super().__init__(private_key)
        self.sender_session_key_handler = RecipientSessionKey(self.rsa_key)

    def decrypt_using_rsa_key(self, data):
        return self.cipher.decrypt(data)
