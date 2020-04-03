from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QTabWidget

from app.send_tab.sub_tabs.file_subtab import FileSubTab
from app.send_tab.sub_tabs.text_subtab import TextSubTab


class ReceiveTab(QWidget):
    def __init__(self, input_queue, parent=None):
        super(QWidget, self).__init__(parent)
        self.__create_layout()

        self.input_queue = input_queue

        self.worker = ReceiveWorker(self.input_queue)
        self.thread = QThread(self)
        self.__init_receiving_thread()

    def __init_receiving_thread(self):
        self.worker.message_received.connect(self.__message_received)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def __create_layout(self):
        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout(self.__init_sender_input())
        vertical_layout.addLayout(self.__init_content_tabs())
        self.setLayout(vertical_layout)

    def __init_sender_input(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel('Sender:'))
        self.sender = QLineEdit()
        self.sender.setDisabled(True)
        layout.addWidget(self.sender)
        return layout

    def __init_content_tabs(self):
        layout = QHBoxLayout()
        self.tabs = QTabWidget()
        self.text_sub_tab = TextSubTab(sending=False)
        self.tabs.addTab(self.text_sub_tab, 'Text')
        self.file_sub_tab = FileSubTab(sending=False)
        self.tabs.addTab(self.file_sub_tab, 'File')
        self.tabs.resize(250, 300)
        layout.addWidget(self.tabs)
        return layout

    @QtCore.pyqtSlot(str)
    def __message_received(self, message):
        self.text_sub_tab.text_message.appendPlainText(message)


class ReceiveWorker(QObject):
    message_received = pyqtSignal(str)

    def __init__(self, input_queue):
        QObject.__init__(self)
        self.input_queue = input_queue
        self.running = True

    @QtCore.pyqtSlot()
    def run(self):
        while self.running:
            message = self.input_queue.get()
            self.message_received.emit(message)

    def close(self):  # TODO never called
        self.running = False
