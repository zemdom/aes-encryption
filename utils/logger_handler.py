import logging
import os
import time

from config import LOGS_DIRECTORY_PATH, LOGS_FILENAME_PREFIX, LOGS_FILENAME_EXTENSION


class LoggerHandler:
    @staticmethod
    def create():
        """
        Initialize file logger, must be called from main thread before other threads are started.
        :return: logger
        :rtype: LoggerHandler
        """
        LoggerHandler.__prepare_logs_directory()

        time_stamp = time.strftime('%Y-%m-%d_%H%M%S')
        filename = LoggerHandler.__create_logs_filename(time_stamp)
        path = LoggerHandler.__create_logs_relative_path(filename)

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename=path,
                            filemode='w')
        return logging.getLogger()

    @staticmethod
    def __create_logs_filename(time_stamp):
        return f'{LOGS_FILENAME_PREFIX}{time_stamp}{LOGS_FILENAME_EXTENSION}'

    @staticmethod
    def __create_logs_relative_path(filename):
        return f'{LOGS_DIRECTORY_PATH}{os.path.sep}{filename}'

    @staticmethod
    def __prepare_logs_directory():
        current_directory = os.getcwd()
        directory_path = os.path.join(current_directory, LOGS_DIRECTORY_PATH)
        try:
            os.makedirs(directory_path)  # creates intermediate directories if needed
        except OSError:
            pass


logger = LoggerHandler.create()
