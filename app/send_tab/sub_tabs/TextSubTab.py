from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPlainTextEdit


class TextSubTab(QWidget):
    def __init__(self, sending=True):
        super(QWidget, self).__init__()
        layout = QHBoxLayout()
        self.text_message = QPlainTextEdit()
        self.text_message.setDisabled(not sending)
        layout.addWidget(self.text_message)
        self.setLayout(layout)