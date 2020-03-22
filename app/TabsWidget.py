from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from app.ReceiveTab import ReceiveTab
from app.SendTab import SendTab


class TabsWidget(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        tabs = self.__createTabs()
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        self.setLayout(layout)

    def __createTabs(self):
        tabs = QTabWidget()
        tabs.addTab(SendTab(), "Send")
        tabs.addTab(ReceiveTab(), "Receive")
        tabs.resize(1000, 600)
        return tabs