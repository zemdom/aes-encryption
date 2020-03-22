from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from app.ReceiveTab import ReceiveTab
from app.send_tab.SendTab import SendTab


class TabsWidget(QWidget):
    def __init__(self, height, width, parent=None):
        super(QWidget, self).__init__(parent)
        tabs = self.__createTabs(height, width)
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        self.setLayout(layout)

    def __createTabs(self, height, width):
        tabs = QTabWidget()
        tabs.addTab(SendTab(), "Send")
        tabs.addTab(ReceiveTab(), "Receive")
        tabs.resize(height, width)
        return tabs
