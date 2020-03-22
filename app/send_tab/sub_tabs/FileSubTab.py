from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFileDialog, QPushButton, QMessageBox


class FileSubTab(QWidget):
    def __init__(self, sending=True):
        super(QWidget, self).__init__()
        if sending:
            self.setLayout(self.__initSendLayout())
        else:
            self.setLayout(self.__initReceiveLayout())
        self.file = None

    def __initSendLayout(self):
        layout = QHBoxLayout()
        select_file_button = QPushButton("Select file")
        select_file_button.clicked.connect(self.__selectFileToSend)
        layout.addWidget(select_file_button)
        return layout

    def __selectFileToSend(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)

        if dlg.exec_():
            selected_files = dlg.selectedFiles()
            self.file = open(selected_files[0], 'rb')

    def __initReceiveLayout(self):
        layout = QHBoxLayout()
        download_file_button = QPushButton("Download file")
        download_file_button.clicked.connect(self.__downloadFile)
        layout.addWidget(download_file_button)
        return layout

    def __downloadFile(self):
        if self.file is None:
            QMessageBox.warning(self, "Error", "You didn't receive any file!")
            return
        directory = str(QFileDialog.getExistingDirectory(self, "Select directory"))
        file_name = directory + '/' + self.file.name
        file = open(file_name, 'wb+')
        file.write(self.file.read())
        file.close()
