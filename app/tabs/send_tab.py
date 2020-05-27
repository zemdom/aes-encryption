from PyQt5 import QtCore
from PyQt5.QtCore import QRegExp, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QComboBox, QTabWidget, \
    QMessageBox, QProgressBar

from config import BLOCK_CIPHER_MODE
from app.tabs.sub_tabs.file_subtab import FileSubTab
from app.tabs.sub_tabs.text_subtab import TextSubTab


class SendTab(QWidget):
    connection_requested = pyqtSignal(str)
    connection_closed = pyqtSignal()
    message_sent = pyqtSignal(object)

    def __init__(self, output_queue, parent=None):
        super(QWidget, self).__init__(parent)
        self.__create_layout()

        self.connected = False
        self.connection_initiator = False

        self.output_queue = output_queue
        self.worker = SendWorker(self.output_queue)
        self.thread = QThread(self)
        self.__init_sending_thread()

    def __init_sending_thread(self):
        self.message_sent.connect(self.worker.message_sent)
        self.worker.moveToThread(self.thread)
        self.thread.start()

    def __create_layout(self):
        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout(self.__init_receiver_input())
        vertical_layout.addLayout(self.__init_cypher_method_select())
        vertical_layout.addLayout(self.__init_tabs())
        vertical_layout.addStretch(1)
        vertical_layout.addLayout(self.__init_footer())
        self.setLayout(vertical_layout)

    def __init_receiver_input(self):
        layout = QHBoxLayout()
        self.receiver_label = QLabel("Receiver")
        layout.addWidget(self.receiver_label)
        layout.addWidget(self.__create_receiver_text_input())
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.__manage_connection_input)
        layout.addWidget(self.connect_button)
        return layout

    def __create_receiver_text_input(self):
        self.receiver = QLineEdit()
        ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        port_regex = "(0|[1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
        ip_regex = QRegExp("^" + ip_range + "\\." + ip_range + "\\." + ip_range + "\\." + ip_range + ":?" + port_regex)
        ip_validator = QRegExpValidator(ip_regex, self)
        self.receiver.setValidator(ip_validator)
        return self.receiver

    def __init_cypher_method_select(self):
        layout = QHBoxLayout()

        self.cypher_mode_label = QLabel("Cypher mode:")
        self.cypher_mode_label.setDisabled(True)
        layout.addWidget(self.cypher_mode_label)
        self.cypher_mode = QComboBox(self)
        self.cypher_mode.setDisabled(True)
        self.cypher_mode.addItems([mode.name for mode in BLOCK_CIPHER_MODE])
        layout.addWidget(self.cypher_mode)
        return layout

    def __init_tabs(self):
        layout = QHBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setDisabled(True)
        self.__init_text_subtab()
        self.__init_file_subtab()
        self.tabs.resize(250, 300)
        layout.addWidget(self.tabs)
        return layout

    def __init_file_subtab(self):
        self.file_sub_tab = FileSubTab(sending=True)
        self.tabs.addTab(self.file_sub_tab, 'File')

    def __init_text_subtab(self):
        self.text_sub_tab = TextSubTab(sending=True)
        self.tabs.addTab(self.text_sub_tab, 'Text')

    def __init_footer(self):
        layout = QHBoxLayout()
        self.__init_send_button(layout)
        self.__init_progress_bar(layout)
        return layout

    def __init_progress_bar(self, layout):
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setDisabled(True)
        self.progress_bar_label = QLabel("File sending progress:")
        self.progress_bar_label.setDisabled(True)
        layout.addWidget(self.progress_bar_label)
        layout.addWidget(self.progress_bar)

    def __init_send_button(self, layout):
        self.send_button = QPushButton("Send", self)
        self.send_button.setDisabled(True)
        self.send_button.clicked.connect(self.__send_message)
        layout.addWidget(self.send_button)

    def __send_message(self):
        if self.receiver.text() == '':
            QMessageBox.warning(self, 'Error', 'Please specify receiver!')

        self.message_sent.emit(('PARM', self.cypher_mode.currentText()))

        if self.tabs.currentIndex() == 0:
            print('[GUI] Selected: send encrypted text')
            self.message_sent.emit(('TEXT', self.text_sub_tab.text_message.toPlainText()))
            self.__empty_text_subtab()
        else:
            print('[GUI] Selected: send encrypted file')
            self.message_sent.emit(('FILE', ('INIT', self.file_sub_tab.filename)))
            self.message_sent.emit(('FILE', ('PARM', 'null')))
            self.message_sent.emit(('FILE', ('DATA', 'null')))
            self.message_sent.emit(('FILE', ('QUIT', 'null')))
            # self.__empty_file_subtab()

    def __empty_text_subtab(self):
        self.text_sub_tab.clear_text_message()

    def __empty_file_subtab(self):
        self.file_sub_tab.clear_file()

    @QtCore.pyqtSlot(int)
    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def __manage_connection_input(self):
        if not self.__is_receiver_filled() or not self.receiver.hasAcceptableInput():
            QMessageBox.warning(self, "Validation error",
                                "Receiver should be specified as IP address and port. For example: 127.0.0.1:2137")
            return
        self.manage_connection()
        self.connection_initiator = not self.connection_initiator

    @QtCore.pyqtSlot(str)
    def manage_connection(self, received_connection_request=None):
        if self.connection_initiator:
            self.connection_initiator = not self.connection_initiator
            return

        self.connected = not self.connected

        if self.connected:
            self.__handle_connect(received_connection_request)
        elif not self.connected:
            self.__handle_disconnect(received_connection_request)

        self.__toggle_connection_view()

    def __handle_connect(self, received_connection_request):
        address = received_connection_request if received_connection_request else self.receiver.text()

        # send signal to app window to open sender thread connecting to given address
        self.connection_requested.emit(address)

        self.message_sent.emit(('INIT', address))
        self.message_sent.emit(('PKEY', 'null'))
        self.message_sent.emit(('SKEY', 'null'))

        if received_connection_request:
            self.receiver.setText(received_connection_request)

    def __handle_disconnect(self, received_connection_request):
        self.message_sent.emit(('QUIT', 'null'))

        if received_connection_request:
            self.receiver.clear()

        # send signal to app window to close sender thread
        self.connection_closed.emit()

    def __toggle_connection_view(self):
        self.cypher_mode.setDisabled(not self.connected)
        self.cypher_mode_label.setDisabled(not self.connected)
        self.tabs.setDisabled(not self.connected)
        self.send_button.setDisabled(not self.connected)
        self.progress_bar.setDisabled(not self.connected)
        self.progress_bar_label.setDisabled(not self.connected)
        self.receiver.setDisabled(self.connected)
        self.receiver_label.setDisabled(self.connected)

        self.connect_button.setText("Disconnect") if self.connected else self.connect_button.setText("Connect")

    def __is_receiver_filled(self):
        return self.receiver.text() is not None and self.receiver.text() != ""


class SendWorker(QObject):
    def __init__(self, output_queue):
        QObject.__init__(self)
        self.output_queue = output_queue

    # @QtCore.pyqtSlot(object) TODO
    def message_sent(self, message):
        self.output_queue.sync_put(message)
