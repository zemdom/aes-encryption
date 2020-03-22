import asyncio
import sys
import threading
from time import sleep

from communication.server import Server
from communication.socket import Socket
from app.App import App
from PyQt5.QtWidgets import QApplication


def main():
    # threading.Thread(target=run_asyncio).start()
    run_asyncio(sys.argv[1], sys.argv[2])
    # GUI main loop
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


def run_asyncio(server_port, peer_port):
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)

    server = Server(server_port=server_port)

    loop.create_task(server.run())

    sleep(5)
    socket = Socket(host='192.168.0.181', port=peer_port)
    loop.create_task(socket.send_data(loop, 'INIT', b'hello'))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    socket.close()
    loop.shutdown_asyncgens()  # close all opened asynchronous generators
    loop.close()


if __name__ == '__main__':
    main()
