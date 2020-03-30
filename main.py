import sys
import threading

from PyQt5.QtWidgets import QApplication

from app.App import App
from threads.async_queue import AsyncQueue
from threads.receiver_thread import create_receiver_thread
from threads.sender_thread import create_sender_thread


def create_gui_thread():
    threading.Thread(target=run_gui).start()


def run_gui():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


def main():
    ingoing_plaindata = AsyncQueue()
    outgoing_plaindata = AsyncQueue()

    outgoing_plaindata.async_put(('INIT', 'Hello World!'))
    outgoing_plaindata.async_put(('QUIT', 'Bye'))

    create_receiver_thread(ingoing_plaindata)
    create_sender_thread(outgoing_plaindata)
    create_gui_thread()


if __name__ == '__main__':
    main()
