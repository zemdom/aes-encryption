import sys
import threading

from PyQt5.QtWidgets import QApplication

from app.app import App
from threads.async_queue import AsyncQueue
from threads.receiver_thread import create_receiver_thread
from threads.sender_thread import create_sender_thread


def create_gui_thread(ingoing_data, outgoing_data):
    threading.Thread(target=run_gui, args=(ingoing_data, outgoing_data)).start()


def run_gui(ingoing_data, outgoing_data):
    app = QApplication(sys.argv)
    ex = App(ingoing_data, outgoing_data)
    sys.exit(app.exec_())


def main():
    ingoing_plaindata = AsyncQueue()
    outgoing_plaindata = AsyncQueue()

    # outgoing_plaindata.async_put(('INIT', 'Hello World!'))
    # outgoing_plaindata.async_put(('QUIT', 'Bye'))

    create_gui_thread(ingoing_plaindata, outgoing_plaindata)
    create_receiver_thread(ingoing_plaindata)
    create_sender_thread(outgoing_plaindata)


if __name__ == '__main__':
    main()
