import sys
import threading
from queue import SimpleQueue

from PyQt5.QtWidgets import QApplication

from app.App import App
from communication.server import run_server
from communication.socket import run_client


def main():
    # unbounded FIFO queues
    ingoing_data = SimpleQueue()
    outgoing_data = SimpleQueue()

    outgoing_data.put(('INIT', 'Hello World!'))
    threading.Thread(target=run_server, args=(ingoing_data, sys.argv[1])).start()
    threading.Thread(target=run_client, args=(outgoing_data, sys.argv[2])).start()
    # GUI thread
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
