from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from app.receive_tab import ReceiveTab
from app.send_tab.send_tab import SendTab


class TabsWidget(QWidget):
    def __init__(self, height, width, parent=None):
        super(QWidget, self).__init__(parent)
        tabs = self.__create_tabs(height, width)
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        self.setLayout(layout)

    def __create_tabs(self, height, width):
        tabs = QTabWidget()
        tabs.addTab(SendTab(), "Send")
        tabs.addTab(ReceiveTab(), "Receive")
        tabs.resize(height, width)
        return tabs
