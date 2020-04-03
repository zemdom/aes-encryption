from PyQt5.QtWidgets import QMainWindow, QInputDialog, QLineEdit, QMessageBox, QApplication

from app.tabs_widget import TabsWidget
from threads.async_queue import AsyncQueue
from threads.thread_handler import SenderThreadHandler, ReceiverThreadHandler

from encryption.rsa_key import SenderRSAKey


class App(QMainWindow):
    windowHeight = 450
    windowWidth = 300

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.input_queue = None
        self.output_queue = None

        # self.receiver_thread = None
        # self.sender_thread = None

        self.setWindowTitle("Data encryption communicator")
        self.resize(self.windowHeight, self.windowWidth)
        self.__get_password()
        self.setCentralWidget(TabsWidget(self.windowHeight, self.windowWidth, self.input_queue, self.output_queue))
        # self.show()

    def __get_password(self):
        password, ok = QInputDialog.getText(self, 'Password', 'Enter your password', QLineEdit.Password)
        if ok:
            self.password = password
            self.__start_application(password)

    def __start_application(self, password):
        rsa_key = SenderRSAKey(password)
        rsa_key.create()

        self.input_queue = AsyncQueue()
        self.output_queue = AsyncQueue()

        self.sender_thread_handler = SenderThreadHandler()
        self.sender_thread_handler.create(rsa_key.public_key, self.output_queue, ('127.0.0.1', 55555))
        # self.sender_thread = self.sender_thread_handler.thread

        self.receiver_thread_handler = ReceiverThreadHandler()
        self.receiver_thread_handler.create(rsa_key.private_key, self.input_queue, 55555)
        # self.receiver_thread = self.receiver_thread_handler.thread

    def __close_application(self):
        # qt kills all subthreads when the main loop exits event loop
        self.sender_thread_handler.close()
        self.receiver_thread_handler.close()
        # self.sender_thread.join()  # TODO
        # self.receiver_thread.join()  # TODO

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Close', 'Are you sure you want to close the window?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.__close_application()
            print('[GUI] Closing window')
            event.accept()
        else:
            event.ignore()
