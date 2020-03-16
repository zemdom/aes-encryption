from datetime import datetime
from random import Random

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA


class KeyHandler:
    def __init__(self):
        self.access_key = None
        self.rsa_key = None

        self.recipient_public_key = None
        self.sender_session_key = None

        self.recipient_encrypted_session_key = None
        self.sender_private_key = None
        self.recipient_session_key = None

    def handle_pretransmission(self):
        """access_key needs to be set before calling"""
        if self.access_key:
            self.rsa_key = SenderRSAKey(self.access_key)
            self.rsa_key.create()

    def handle_transmission(self):
        """recipient_public_key needs to be set before calling"""
        if self.recipient_public_key:
            self.sender_session_key = SenderSessionKey(self.recipient_public_key)
            self.sender_session_key.create()

    def handle_posttransmission(self):
        """recipient_encrypted_session_key and sender_private_key need to be set before calling"""
        if self.recipient_encrypted_session_key and self.sender_private_key:
            self.recipient_session_key = RecipientSessionKey(self.sender_private_key)


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


class SenderRSAKey:
    def __init__(self, access_key):
        # keys are stored as byte string
        self.private_key = None
        self.public_key = None
        self.encrypted_private_key = None
        self.encrypted_public_key = None
        self.path_private_key = './test/private/private.pem'
        self.path_public_key = './test/public/public.pem'

        # access_key = None
        self.encrypted_access_key = SHA256.new(data=access_key).digest()

        initial_vector = b'\x92\xc0\xf6$\xa8\xc4\x88b\x07x\xd3DG\xe5\x94\x1a'
        self.cipher = AES.new(self.encrypted_access_key, AES.MODE_CBC, iv=initial_vector)

    def __generate_key(self):
        key = RSA.generate(2048)
        # keys are stored as byte string
        self.private_key = key.export_key()
        self.public_key = key.publickey().export_key()

    def __encrypt_key(self):
        if self.private_key and self.public_key:
            self.encrypted_private_key = self.cipher.encrypt(self.private_key)
            self.encrypted_public_key = self.cipher.encrypt(self.public_key)

    def __decrypt_key(self):
        if self.encrypted_private_key and self.encrypted_public_key:
            self.private_key = self.cipher.decrypt(self.encrypted_private_key)
            self.public_key = self.cipher.decrypt(self.encrypted_public_key)

    def __store_key(self):
        if self.encrypted_private_key and self.encrypted_public_key:
            with open(self.path_private_key, 'wb') as file_out:
                file_out.write(self.encrypted_private_key)

            with open(self.path_public_key, 'wb') as file_out:
                file_out.write(self.encrypted_public_key)

    def create(self):
        loaded = self.__load_key()

        if loaded:
            self.__decrypt_key()
        else:
            self.__generate_key()
            self.__encrypt_key()
            self.__store_key()

    def __load_key(self):
        try:
            with open(self.path_private_key, 'r') as file_in:
                self.encrypted_private_key = RSA.import_key(file_in.read())

            with open(self.path_public_key, 'r') as file_in:
                self.encrypted_public_key = RSA.import_key(file_in.read())
        except IOError:
            return False
        else:
            return True
