from pathlib import Path

from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA

from encryption.data_handler import DataHandler


class SenderRSAKey:
    def __init__(self, access_key):
        # keys are stored as byte string
        self.private_key = None
        self.public_key = None
        self.encrypted_private_key = None
        self.encrypted_public_key = None

        self.path_private_key = './../test/private/'
        self.private_key_filename = 'private.pem'
        self.full_path_private_key = self.path_private_key + self.private_key_filename

        self.path_public_key = './../test/public/'
        self.public_key_filename = 'public.pem'
        self.full_path_public_key = self.path_public_key + self.public_key_filename

        access_key = access_key.encode()
        self.encrypted_access_key = SHA256.new(data=access_key).digest()

        initial_vector = b'\x92\xc0\xf6$\xa8\xc4\x88b\x07x\xd3DG\xe5\x94\x1a'  # TODO
        self.cipher = AES.new(self.encrypted_access_key, AES.MODE_CBC, iv=initial_vector)

    def __generate_key(self):
        key = RSA.generate(2048)
        # keys are stored as byte string
        self.private_key = key.export_key('PEM')
        self.public_key = key.publickey().export_key('PEM')

    def __encrypt_key(self):
        if self.private_key and self.public_key:
            padded_private_key = DataHandler.add_padding(self.private_key)
            padded_public_key = DataHandler.add_padding(self.public_key)

            self.encrypted_private_key = self.cipher.encrypt(padded_private_key)
            self.encrypted_public_key = self.cipher.encrypt(padded_public_key)

    def __decrypt_key(self):
        if self.encrypted_private_key and self.encrypted_public_key:
            self.private_key = self.cipher.decrypt(self.encrypted_private_key)
            self.public_key = self.cipher.decrypt(self.encrypted_public_key)

            self.private_key = DataHandler.remove_padding(self.private_key)
            self.public_key = DataHandler.remove_padding(self.public_key)

            self.__check_if_correct_access_key()

    def __check_if_correct_access_key(self):
        try:
            # check if keys were decrypted correctly
            RSA.import_key(self.private_key)
            RSA.import_key(self.public_key)
        except ValueError:
            # if access key was incorrect, generate unrelated private and public keys
            self.private_key = RSA.generate(2048).export_key('PEM')
            self.public_key = RSA.generate(2048).publickey().export_key('PEM')

    def __store_key(self):
        if self.encrypted_private_key and self.encrypted_public_key:
            # create path to file if it does not exist
            Path(self.path_private_key).mkdir(parents=True, exist_ok=True)
            with open(self.full_path_private_key, 'wb') as file_out:
                file_out.write(self.encrypted_private_key)

            # create path to file if it does not exist
            Path(self.path_public_key).mkdir(parents=True, exist_ok=True)
            with open(self.full_path_public_key, 'wb') as file_out:
                file_out.write(self.encrypted_public_key)

    def __load_key(self):
        try:
            with open(self.full_path_private_key, 'rb') as file_in:
                self.encrypted_private_key = file_in.read()

            with open(self.full_path_public_key, 'rb') as file_in:
                self.encrypted_public_key = file_in.read()
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
