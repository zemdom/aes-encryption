from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QTabWidget

from app.send_tab.sub_tabs.FileSubTab import FileSubTab
from app.send_tab.sub_tabs.TextSubTab import TextSubTab


class ReceiveTab(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.__createLayout()

    def __createLayout(self):
        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout(self.__initSenderInput())
        vertical_layout.addLayout(self.__initContentTabs())
        self.setLayout(vertical_layout)

    def __initSenderInput(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Sender:"))
        self.sender = QLineEdit()
        self.sender.setDisabled(True)
        layout.addWidget(self.sender)
        return layout

    def __initContentTabs(self):
        layout = QHBoxLayout()
        self.tabs = QTabWidget()
        self.text_sub_tab = TextSubTab(sending=False)
        self.tabs.addTab(self.text_sub_tab, "Text")
        self.file_sub_tab = FileSubTab(sending=False)
        self.tabs.addTab(self.file_sub_tab, "File")
        self.tabs.resize(250, 300)
        layout.addWidget(self.tabs)
        return layout
