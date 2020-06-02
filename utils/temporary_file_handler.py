import os
import shutil

from config import TMP_DIRECTORY_PATH


class TemporaryFileHandler:
    @staticmethod
    def create_temporary_file_directory():
        directory_path = TemporaryFileHandler.get_temporary_file_directory_path()
        try:
            os.makedirs(directory_path)  # creates intermediate directories if needed
        except OSError:
            pass

    @staticmethod
    def remove_temporary_file_directory():
        shutil.rmtree(TMP_DIRECTORY_PATH)

    @staticmethod
    def get_temporary_file_directory_path():
        temporary_directory = os.getcwd()
        temporary_directory = os.path.join(temporary_directory, TMP_DIRECTORY_PATH)
        return temporary_directory

    @staticmethod
    def move_temporary_file(source_path, destination_path):
        shutil.copy2(source_path, destination_path)
