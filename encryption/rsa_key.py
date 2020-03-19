from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA


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

    def create(self):
        loaded = self.__load_key()

        if loaded:
            self.__decrypt_key()
        else:
            self.__generate_key()
            self.__encrypt_key()
            self.__store_key()
