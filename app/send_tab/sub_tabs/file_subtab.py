from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFileDialog, QPushButton, QMessageBox, QLabel, QVBoxLayout, QLineEdit


class FileSubTab(QWidget):
    def __init__(self, sending=True):
        super(QWidget, self).__init__()
        self.file = None
        self.download_file_button = QPushButton()
        vertical_layout = QVBoxLayout()
        if sending:
            vertical_layout.addLayout(self.__init_send_layout())
            vertical_layout.addLayout(self.__init_file_name(sending))
        else:
            vertical_layout.addLayout(self.__init_file_name(sending))
            vertical_layout.addLayout(self.__init_receive_layout())
        self.setLayout(vertical_layout)
        self.on_file_change()

    def __init_send_layout(self):
        layout = QHBoxLayout()
        select_file_button = QPushButton("Select file")
        select_file_button.clicked.connect(self.__select_file_to_send)
        layout.addWidget(select_file_button)
        return layout

    def __select_file_to_send(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)

        if dlg.exec_():
            selected_files = dlg.selectedFiles()
            self.file = open(selected_files[0], 'rb')

    def __init_receive_layout(self):
        layout = QHBoxLayout()
        self.download_file_button = QPushButton("Download file")
        self.download_file_button.clicked.connect(self.__download_file)
        layout.addWidget(self.download_file_button)
        return layout

    def __download_file(self):
        if self.file is None:
            QMessageBox.warning(self, "Error", "You didn't receive any file!")
            return
        directory = str(QFileDialog.getExistingDirectory(self, "Select directory"))
        file_name = directory + '/' + self.file.name
        file = open(file_name, 'wb+')
        file.write(self.file.read())
        file.close()

    def __init_file_name(self, sending=True):
        layout = QHBoxLayout()
        if sending:
            layout.addWidget(QLabel("Selected file: "))
        else:
            layout.addWidget(QLabel("Received file: "))
        self.file_name_label = QLineEdit()
        self.file_name_label.setDisabled(True)
        layout.addWidget(self.file_name_label)
        return layout

    def on_file_change(self):
        if self.file is not None:
            self.file_name_label.setText(self.file.name)
            self.download_file_button.setDisabled(False)
        else:
            self.file_name_label.setText("")
            self.download_file_button.setDisabled(True)
