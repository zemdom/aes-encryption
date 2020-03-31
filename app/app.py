from PyQt5.QtWidgets import QMainWindow

from app.tabs_widget import TabsWidget


class App(QMainWindow):

    windowHeight = 450
    windowWidth = 300

    def __init__(self, input_queue, output_queue):
        super(QMainWindow, self).__init__()
        self.setWindowTitle("Data encryption project")
        self.resize(self.windowHeight, self.windowWidth)
        self.setCentralWidget(TabsWidget(self.windowHeight, self.windowWidth, input_queue, output_queue))
        self.show()
