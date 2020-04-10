from PyQt5.QtCore import QRegExp, pyqtSignal
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QComboBox, QTabWidget, \
    QMessageBox, QProgressBar

from config import BLOCK_CIPHER_MODE
from app.send_tab.sub_tabs.file_subtab import FileSubTab
from app.send_tab.sub_tabs.text_subtab import TextSubTab


class SendTab(QWidget):
    connection_requested = pyqtSignal(str)
    connection_closed = pyqtSignal()

    def __init__(self, output_queue, parent=None):
        self.output_queue = output_queue

        super(QWidget, self).__init__(parent)
        self.connected = False
        self.__create_layout()

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
        self.connect_button.clicked.connect(self.__manage_connection)
        layout.addWidget(self.connect_button)
        return layout

    def __create_receiver_text_input(self):
        self.receiver = QLineEdit()
        ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ip_regex = QRegExp("^" + ip_range + "\\." + ip_range + "\\." + ip_range + "\\." + ip_range + ":?[0-9]{0,5}$")
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
        self.progress_bar_label = QLabel("Sending progress:")
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
        if self.tabs.currentIndex() == 0:
            print('[GUI] Selected: send encrypted text')
            self.update_progress_bar(50)

            self.output_queue.async_put(('PARM', self.cypher_mode.currentText()))
            self.output_queue.async_put(('DATA', self.text_sub_tab.text_message.toPlainText()))
            self.__empty_text_subtab()
        else:
            print('[GUI] Selected: send encrypted file')
            # encrypt(self.receiver.text(), self.cypher_mode.currentText(), self.file_sub_tab.file)
            self.__empty_file_subtab()

    def __empty_text_subtab(self):
        self.text_sub_tab.clear_text_message()

    def __empty_file_subtab(self):
        ...

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def __manage_connection(self):
        if not self.__is_receiver_filled() or not self.receiver.hasAcceptableInput():
            QMessageBox.warning(self, "Validation error",
                                "Receiver should be specified as IP address and port. For example: 127.0.0.1:2137")
            return
        self.connected = not self.connected
        self.__after_connection_change()

    def __after_connection_change(self):
        self.cypher_mode.setDisabled(not self.connected)
        self.cypher_mode_label.setDisabled(not self.connected)
        self.tabs.setDisabled(not self.connected)
        self.send_button.setDisabled(not self.connected)
        self.progress_bar.setDisabled(not self.connected)
        self.progress_bar_label.setDisabled(not self.connected)
        self.receiver.setDisabled(self.connected)
        self.receiver_label.setDisabled(self.connected)
        if self.connected:
            self.connect_button.setText("Disconnect")
            self.connection_requested.emit(self.receiver.text())
            self.output_queue.async_put(('INIT', self.receiver.text()))
            self.output_queue.async_put(('PKEY', 'null'))
            self.output_queue.async_put(('SKEY', 'null'))
        else:
            self.connect_button.setText("Connect")
            self.output_queue.async_put(('QUIT', self.receiver.text()))
            self.connection_closed.emit()

    def __is_receiver_filled(self):
        return self.receiver.text() is not None and self.receiver.text() != ""
