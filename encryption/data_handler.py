from Cryptodome.Util.Padding import pad, unpad

from config import BLOCK_SIZE


class DataHandler:
    @staticmethod
    def add_padding(data):
        return pad(data, block_size=BLOCK_SIZE)

    @staticmethod
    def remove_padding(data):
        return unpad(data, block_size=BLOCK_SIZE)

    def __divide(self, data):
        ...

    def __merge(self, data):
        ...
