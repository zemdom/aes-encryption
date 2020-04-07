from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from app.receive_tab import ReceiveTab
from app.send_tab.send_tab import SendTab


class TabsWidget(QWidget):
    def __init__(self, height, width, input_queue, output_queue, parent=None):
        super(QWidget, self).__init__(parent)
        self.send_tab = None
        self.receive_tab = None
        tabs = self.__create_tabs(height, width, input_queue, output_queue)
        self.send_tab.connection_closed.connect(self.receive_tab.empty_content_tabs)

        layout = QVBoxLayout(self)
        layout.addWidget(tabs)
        self.setLayout(layout)

    def __create_tabs(self, height, width, input_queue, output_queue):
        tabs = QTabWidget()
        self.send_tab = SendTab(output_queue)
        tabs.addTab(self.send_tab, "Send")
        self.receive_tab = ReceiveTab(input_queue)
        tabs.addTab(self.receive_tab, "Receive")
        tabs.resize(height, width)
        return tabs
