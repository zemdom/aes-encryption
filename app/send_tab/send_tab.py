from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QComboBox, QTabWidget, \
    QMessageBox, QProgressBar

from encryption.block_cypher_mode import BlockCypherMode
from app.send_tab.sub_tabs.file_subtab import FileSubTab
from app.send_tab.sub_tabs.text_subtab import TextSubTab


class SendTab(QWidget):
    def __init__(self, output_queue, parent=None):
        self.output_queue = output_queue

        super(QWidget, self).__init__(parent)
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
        layout.addWidget(QLabel('Receiver:'))
        self.receiver = QLineEdit()
        layout.addWidget(self.receiver)
        return layout

    def __init_cypher_method_select(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel('Cypher mode:'))
        self.cypher_mode = QComboBox(self)
        self.cypher_mode.addItems([mode.name for mode in BlockCypherMode])
        layout.addWidget(self.cypher_mode)
        return layout

    def __init_tabs(self):
        layout = QHBoxLayout()
        self.tabs = QTabWidget()
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
        layout.addWidget(QLabel('Sending progress:'))
        layout.addWidget(self.progress_bar)

    def __init_send_button(self, layout):
        send_button = QPushButton('Send', self)
        send_button.clicked.connect(self.__send_message)
        layout.addWidget(send_button)

    def __send_message(self):
        if self.receiver.text() == '':
            QMessageBox.warning(self, 'Error', 'Please specify receiver!')
        if self.tabs.currentIndex() == 0:
            print('[GUI] Selected: send encrypted text')
            self.update_progress_bar(50)

            self.output_queue.async_put(('INIT', self.receiver.text()))
            self.output_queue.async_put(('INIT', self.text_sub_tab.text_message.toPlainText()))
            # encrypt(self.receiver.text(), self.cypher_mode.current_text(),
            # self.text_sub_tab.text_message.toPlainText()
        else:
            print('[GUI] Selected: send encrypted file')
            # encrypt(self.receiver.text(), self.cypher_mode.currentText(), self.file_sub_tab.file)

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)
