from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QComboBox, QTabWidget, \
    QMessageBox, QProgressBar

from BlockCypherMode import BlockCypherMode
from app.send_tab.sub_tabs.FileSubTab import FileSubTab
from app.send_tab.sub_tabs.TextSubTab import TextSubTab


class SendTab(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.__createLayout()

    def __createLayout(self):
        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout(self.__initReceiverInput())
        vertical_layout.addLayout(self.__initCypherMethodSelect())
        vertical_layout.addLayout(self.__initContentTabs())
        vertical_layout.addStretch(1)
        vertical_layout.addLayout(self.__initSendButton())
        vertical_layout.addLayout(self.__initProgressBar())
        self.setLayout(vertical_layout)

    def __initReceiverInput(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Receiver:"))
        self.receiver = QLineEdit()
        layout.addWidget(self.receiver)
        return layout

    def __initCypherMethodSelect(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Cypher mode:"))
        self.cypher_mode = QComboBox(self)
        self.cypher_mode.addItems([mode.name for mode in BlockCypherMode])
        layout.addWidget(self.cypher_mode)
        return layout

    def __initContentTabs(self):
        layout = QHBoxLayout()
        self.tabs = QTabWidget()
        self.text_sub_tab = TextSubTab()
        self.tabs.addTab(self.text_sub_tab, "Text")
        self.file_sub_tab = FileSubTab()
        self.tabs.addTab(self.file_sub_tab, "File")
        self.tabs.resize(250, 300)
        layout.addWidget(self.tabs)
        return layout

    def __initSendButton(self):
        layout = QHBoxLayout()
        layout.addStretch(1)
        send_button = QPushButton("Send", self)
        send_button.clicked.connect(self.__sendMessage)
        layout.addWidget(send_button)
        return layout

    def __sendMessage(self):
        if self.receiver.text() == '':
            QMessageBox.warning(self, "Error", "Please specify receiver!")
        if self.tabs.currentIndex() == 0:
            print("Send encrypted text")
            self.updateProgressBar(50)
            # encrypt(self.receiver.text(), self.cypher_mode.current_text(),
            # self.text_sub_tab.text_message.toPlainText()
        else:
            print("Send encrypted file")
            # encrypt(self.receiver.text(), self.cypher_mode.currentText(), self.file_sub_tab.file)

    def __initProgressBar(self):
        layout = QHBoxLayout()
        self.progress_bar = QProgressBar(self)
        layout.addWidget(QLabel("Sending progress:"))
        layout.addWidget(self.progress_bar)
        return layout

    def updateProgressBar(self, value):
        self.progress_bar.setValue(value)