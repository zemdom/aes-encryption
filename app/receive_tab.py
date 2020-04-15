from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QTabWidget, QPushButton, QMessageBox

from app.send_tab.sub_tabs.file_subtab import FileSubTab
from app.send_tab.sub_tabs.text_subtab import TextSubTab


class ReceiveTab(QWidget):
    received_connection_request = pyqtSignal(str)

    def __init__(self, input_queue, parent=None):
        super(QWidget, self).__init__(parent)
        self.__create_layout()

        self.input_queue = input_queue
        self.message_dispatchers = dict(INIT=ReceiveTab.__dispatch_init_message,
                                        PKEY=ReceiveTab.__mock,
                                        SKEY=ReceiveTab.__mock,
                                        PARM=ReceiveTab.__mock,
                                        DATA=ReceiveTab.__dispatch_data_message,
                                        QUIT=ReceiveTab.__dispatch_quit_message)

        self.worker = ReceiveWorker(self.input_queue)
        self.thread = QThread(self)
        self.__init_receiving_thread()

    def __init_receiving_thread(self):
        self.worker.message_received.connect(self.__message_received)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def __create_layout(self):
        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout(self.__init_listening_port())
        vertical_layout.addLayout(self.__init_sender_input())
        vertical_layout.addLayout(self.__init_content_tabs())
        self.setLayout(vertical_layout)

    def __init_listening_port(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel('Listening port'))
        self.listening_port = QLineEdit()
        self.listening_port.setValidator(QRegExpValidator(QRegExp('^[0-9]{1,5}$'), self))
        layout.addWidget(self.listening_port)
        self.listening_button = QPushButton('Start listening')
        self.listening_button.clicked.connect(self.__on_listening_button_click)
        layout.addWidget(self.listening_button)
        layout.addStretch(1)
        return layout

    def __on_listening_button_click(self):
        if not self.listening_port.hasAcceptableInput():
            QMessageBox.warning(self, 'Error', 'Port should be number from 0 to 99999')
            return
        self.__change_button_text()
        self.__change_tab_enable_state()
        # todo: start listening on port specified in self.listening_port

    def __change_button_text(self):
        if self.listening_button.text() == 'Start listening':
            self.listening_button.setText('Stop listening')
        else:
            self.listening_button.setText('Start listening')

    def __change_tab_enable_state(self):
        self.tabs.setEnabled(not self.tabs.isEnabled())

    def __init_sender_input(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel('Sender:'))
        self.sender = QLineEdit()
        self.sender.setDisabled(True)
        layout.addWidget(self.sender)
        return layout

    def __init_content_tabs(self):
        layout = QHBoxLayout()
        self.tabs = QTabWidget()
        self.text_sub_tab = TextSubTab(sending=False)
        self.tabs.addTab(self.text_sub_tab, 'Text')
        self.file_sub_tab = FileSubTab(sending=False)
        self.tabs.addTab(self.file_sub_tab, 'File')
        self.tabs.resize(250, 300)
        self.tabs.setDisabled(True)
        layout.addWidget(self.tabs)
        return layout

    @QtCore.pyqtSlot()
    def empty_content_tabs(self):
        self.text_sub_tab.clear_text_message()
        # TODO empty files tab

    @QtCore.pyqtSlot(object)
    def __message_received(self, message):
        self.__dispatch_message(*message)

    def __dispatch_message(self, message_type, message_data):
        self.message_dispatchers.get(message_type)(self, message_data)

    def __dispatch_init_message(self, message):
        host, _ = message.split(':')
        self.sender.setText(host)
        self.received_connection_request.emit(message)

    def __dispatch_data_message(self, message):
        self.text_sub_tab.append_text_message(message)

    def __dispatch_quit_message(self, message):
        self.sender.clear()
        self.empty_content_tabs()
        self.received_connection_request.emit('')

    # TODO
    def __mock(self, message):
        pass


class ReceiveWorker(QObject):
    message_received = pyqtSignal(object)

    def __init__(self, input_queue):
        QObject.__init__(self)
        self.input_queue = input_queue

    @QtCore.pyqtSlot()
    def run(self):
        while True:
            message = self.input_queue.sync_get()
            self.message_received.emit(message)
