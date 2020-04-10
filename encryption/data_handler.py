from Cryptodome.Util.Padding import pad, unpad

from config import BLOCK_SIZE


class DataHandler:
    @staticmethod
    def add_padding(data):
        return pad(data, block_size=BLOCK_SIZE)

    @staticmethod
    def remove_padding(data):
        try:
            transformed_data = unpad(data, block_size=BLOCK_SIZE)
        except ValueError:
            # when padding cannot be removed, sender entered incorrect access key and the data is random
            transformed_data = data  # return the random data
        return transformed_data

    def __divide(self, data):
        ...

    def __merge(self, data):
        ...
