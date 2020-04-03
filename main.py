import os
import sys
from PyQt5.QtWidgets import QApplication
from app.app import App


def run_gui():
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    # sys.exit(app.exec_())
    app.exec_()
    print('[GUI] GUI closed')


def main():
    run_gui()
    os._exit(0)  # TODO


if __name__ == '__main__':
    main()
