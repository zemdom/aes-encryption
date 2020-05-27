import os
from PyQt5.QtWidgets import QApplication
from app.app import App


def run_gui():
    app = QApplication([])
    ex = App()
    ex.show()
    app.exec_()
    print('[GUI] GUI closed')


def main():
    run_gui()
    os._exit(0)


if __name__ == '__main__':
    main()
