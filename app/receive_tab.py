import asyncio

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QTabWidget

from app.send_tab.sub_tabs.file_subtab import FileSubTab
from app.send_tab.sub_tabs.text_subtab import TextSubTab


class ReceiveTab(QWidget):
    def __init__(self, input_queue, parent=None):
        self.input_queue = input_queue

        super(QWidget, self).__init__(parent)
        self.__create_layout()

        self.thread = ReceiveThread(input_queue, self.text_sub_tab)
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


class ReceiveThread(QThread):
    def __init__(self, input_queue, text_field):
        QThread.__init__(self)
        self.input_queue = input_queue
        self.text_field = text_field

    def run(self):
        asyncio.run(self.__get_messages())

    async def __get_messages(self):
        while True:  # TODO
            message = await self.input_queue.async_get()
            self.text_field.text_message.appendPlainText(message)

    def __update_text_fields(self):
        ...
