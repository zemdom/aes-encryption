from PyQt5.QtWidgets import QMainWindow

from app.TabsWidget import TabsWidget


class App(QMainWindow):

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setWindowTitle("Data encryption project")
        self.resize(1000, 600)
        self.setCentralWidget(TabsWidget())
        self.show()
