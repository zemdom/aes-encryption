from Cryptodome.Util.Padding import pad, unpad

from config import BLOCK_SIZE


class DataHandler:
    def __init__(self):
        self.data = None
        self.padded_data = None
        self.divided_data = []

    def __add_padding(self):
        if self.data:
            self.padded_data = pad(self.data, block_size=BLOCK_SIZE)

    def __remove_padding(self):
        if self.padded_data:
            self.data = unpad(self.padded_data, block_size=BLOCK_SIZE)

    def divide(self):
        ...

    def merge(self):
        ...
