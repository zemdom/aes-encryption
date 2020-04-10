from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA

from config import SESSION_KEY_SIZES

from secrets import SystemRandom


class SessionKey:
    def __init__(self, rsa_key):
        # keys are stored as byte string
        self.key_size = None
        self.session_key = None  # byte string
        self.encrypted_session_key = None  # byte string

        self.rsa_key = rsa_key  # byte string
        self.cipher = PKCS1_OAEP.new(RSA.import_key(self.rsa_key))

    def _generate_key(self):
        system_rand = SystemRandom()  # generates random numbers from sources provided by the operating system
        self.key_size = system_rand.choice(SESSION_KEY_SIZES)
        session_key = system_rand.getrandbits(self.key_size)
        self.session_key = session_key.to_bytes(self.key_size // 8, byteorder='little')

    def create(self, *args, **kwargs):
        raise NotImplementedError


class SenderSessionKey(SessionKey):
    def __init__(self, recipient_public_key):
        super().__init__(recipient_public_key)

    def __encrypt_key(self):
        if self.session_key:
            self.encrypted_session_key = self.cipher.encrypt(self.session_key)

    def create(self):
        self._generate_key()
        self.__encrypt_key()


class RecipientSessionKey(SessionKey):
    def __init__(self, sender_private_key):
        super().__init__(sender_private_key)

    def __decrypt_key(self, encrypted_session_key):
        try:
            self.session_key = self.cipher.decrypt(encrypted_session_key)
        except ValueError:
            # in case of unauthorised decryption - sender entered incorrect access key - generate random key
            self._generate_key()

    def create(self, key_size):
        self.key_size = key_size
        self.__decrypt_key(self.encrypted_session_key)
