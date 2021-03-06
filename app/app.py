from PyQt5 import QtCore

from PyQt5.QtWidgets import QMainWindow, QInputDialog, QLineEdit, QMessageBox

from app.tabs.tabs_widget import TabsWidget
from threads.async_queue import AsyncQueue
from threads.thread_handler import SenderThreadHandler, ReceiverThreadHandler

from encryption.keys.rsa_key import SenderRSAKey


class App(QMainWindow):
    windowHeight = 450
    windowWidth = 300

    def __init__(self, receiver_port):
        super(QMainWindow, self).__init__()

        self.input_queue = None
        self.output_queue = None
        self.shared_data = None

        self.rsa_key = None
        self.receiver_port = receiver_port

        self.receiver_thread_handler = None
        self.sender_thread_handler = None

        self.setWindowTitle("Data encryption communicator")
        self.resize(self.windowHeight, self.windowWidth)
        self.__get_password()

        self.central_widget = TabsWidget(self.windowHeight, self.windowWidth, self.input_queue, self.output_queue)
        self.central_widget.send_tab.connection_requested.connect(self.__start_connection)
        self.central_widget.send_tab.connection_closed.connect(self.__close_connection)
        self.setCentralWidget(self.central_widget)

    def __get_password(self):
        password, ok = QInputDialog.getText(self, 'Password', 'Enter your password', QLineEdit.Password)
        if ok:
            self.password = password
            self.__init_application(password)

    def __init_application(self, password):
        self.rsa_key = SenderRSAKey(password)
        self.rsa_key.create()

        self.input_queue = AsyncQueue()
        self.output_queue = AsyncQueue()
        self.shared_data = AsyncQueue()

        self.receiver_thread_handler = ReceiverThreadHandler()
        self.receiver_thread_handler.create(self.rsa_key.private_key, self.input_queue, self.shared_data,
                                            self.receiver_port)

    @QtCore.pyqtSlot(str)
    def __start_connection(self, address):
        host, port = address.split(':')
        self.sender_thread_handler = SenderThreadHandler()
        self.sender_thread_handler.create(self.rsa_key.public_key, self.output_queue, self.shared_data, (host, port),
                                          self.receiver_port)

    @QtCore.pyqtSlot()
    def __close_connection(self):
        self.sender_thread_handler.close()
        self.output_queue.close()
        self.shared_data.close()
        # self.sender_thread_handler.thread.join()  # TODO: handle joining communication threads
        # self.receiver_thread.join()

    def __close_application(self):
        # qt kills all its subthreads when the main loop exits event loop, only TCP connection threads need to be closed
        self.receiver_thread_handler.close()
        if self.sender_thread_handler:
            # if sender is already closed, method does nothing
            self.sender_thread_handler.close()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Close', 'Are you sure you want to close the window?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.__close_application()
            print('[GUI] Closing window')
            event.accept()
        else:
            event.ignore()
