from PyQt5.QtWidgets import QMainWindow

from app.TabsWidget import TabsWidget


class App(QMainWindow):

    windowHeight = 450
    windowWidth = 300

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.setWindowTitle("Data encryption project")
        self.resize(self.windowHeight, self.windowWidth)
        self.setCentralWidget(TabsWidget(self.windowHeight, self.windowWidth))
        self.show()
