import os
import sys
from PyQt5.QtWidgets import QApplication
from app.app import App


def run_gui():
    receiver_port = sys.argv[1]
    app = QApplication(sys.argv)
    ex = App(receiver_port)
    ex.show()
    app.exec_()
    print('[GUI] GUI closed')


def main():
    run_gui()
    os._exit(0)


if __name__ == '__main__':
    main()
