from PyQt5.QtWidgets import QMainWindow, QInputDialog, QLineEdit

from app.tabs_widget import TabsWidget


class App(QMainWindow):

    windowHeight = 450
    windowWidth = 300

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setWindowTitle("Data encryption project")
        self.resize(self.windowHeight, self.windowWidth)
        self.__get_password()
        self.setCentralWidget(TabsWidget(self.windowHeight, self.windowWidth))
        self.show()

    def __get_password(self):
        password, ok = QInputDialog.getText(self, 'Password', 'Enter your password', QLineEdit.Password)
        if ok:
            self.password = password
