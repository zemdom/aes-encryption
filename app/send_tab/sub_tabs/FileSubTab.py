from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFileDialog, QPushButton


class FileSubTab(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        self.__initLayout()
        self.file = None

    def __initLayout(self):
        layout = QHBoxLayout()
        select_file_button = QPushButton("Select file")
        select_file_button.clicked.connect(self.__getFile)
        layout.addWidget(select_file_button)
        self.setLayout(layout)

    def __getFile(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)

        if dlg.exec_():
            selected_files = dlg.selectedFiles()
            self.file = open(selected_files[0], 'r')
