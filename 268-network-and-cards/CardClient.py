import socket
import threading
from time import sleep


class CardClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send(self, message):
        self.sock.sendall(message)

    def listen(self):
        size = 1024
        while True:
            data = self.sock.recv(size)
            if not data:
                break
            print '< %s' % data


if __name__ == "__main__":
    host = 'localhost'
    port = 12916
    myClient = CardClient('localhost', 12916)
    print 'Connected to %s on port %s' % (host, port)
    print 'Type "IDENTIFY <name>" to begin:'
    threading.Thread(target=myClient.listen).start()
    while True:
        message = raw_input("> ")
        myClient.send(message)
        sleep(1)
