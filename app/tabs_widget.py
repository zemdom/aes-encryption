from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from app.receive_tab import ReceiveTab
from app.send_tab.send_tab import SendTab


class TabsWidget(QWidget):
    def __init__(self, height, width, input_queue, output_queue, parent=None):
        super(QWidget, self).__init__(parent)
        tabs = self.__create_tabs(height, width, input_queue, output_queue)
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        self.setLayout(layout)

    def __create_tabs(self, height, width, input_queue, output_queue):
        tabs = QTabWidget()
        tabs.addTab(SendTab(output_queue), "Send")
        tabs.addTab(ReceiveTab(input_queue), "Receive")
        tabs.resize(height, width)
        return tabs
